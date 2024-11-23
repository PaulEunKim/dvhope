import os
import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import random
import matplotlib.pyplot as plt
import plotly.express as px
import string
import webbrowser
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

def return_transformed_name(name):
    add_only_emission_label = [
        'transportation',
        'forest_clearing',
        'petrochemicals',
        'electricity_generation'
        ]
    add_ampersand_label = [
        'residential_commercial',
        'incineration_open_burning'
        ]
    if name in add_only_emission_label:
        return string.capwords(name.replace('_', ' ') + " Emissions")
    elif name == 'coal':
        return string.capwords(name.replace('_', ' ') + " Mining Emissions")
    elif name == 'cropland':
        return string.capwords(name.replace('_', ' ') + " Fires Emissions")
    elif name in add_ampersand_label:
        split_name = name.split('_')
        split_name.insert(1, '&')
        edited_name = ' '.join(split_name)
        return string.capwords(edited_name + " Emissions")

def append_label_emissions(name, x_label):
    if x_label != 'emissions_quantity':
        return string.capwords(name.replace('_', ' '))
    else:
        return return_transformed_name(name)

def define_files():
    files = {
        "air_pollution_death": "data/air_pollution_death.csv",
        "transportation": 'data/road-transportation_country_emissions.csv',
        "coal": 'data/coal-mining_country_emissions.csv',
        "cropland": 'data/cropland-fires_country_emissions.csv',
        "residential_commercial": 'data/residential-and-commercial-onsite-fuel-usage_country_emissions.csv',
        "forest_clearing": 'data/forest-land-clearing_country_emissions.csv',
        "petrochemicals": 'data/petrochemicals_country_emissions.csv',
        "electricity_generation": 'data/electricity-generation_country_emissions.csv',
        "incineration_open_burning": 'data/incineration-and-open-burning-of-waste_country_emissions.csv',
        "health_expenditure": 'data/health-expenditure.csv',
        "urban_population": 'data/urban-population.csv'
    }
    return files

def get_common_country_codes(common_df, envi_files, socio_list):
    common_country_codes = set(common_df['SpatialDimValueCode'])
    for df in envi_files.values():
        common_country_codes &= set(df['iso3_country'])
    for df in socio_list.values():
        common_country_codes &= set(df['Country Code'])
    return list(common_country_codes)

def start_predict_xgboost():
    print("Start...")

    random_seed = 42
    np.random.seed(random_seed)
    random.seed(random_seed)

    files = define_files()

    exclude_environment_factor_files_list = [
        'air_pollution_death',
        'health_expenditure',
        'urban_population'
    ]
    exclude_socioeconomic_files_list = [
        'health_expenditure',
        'urban_population'
    ]

    environment_factor_files = {k: pd.read_csv(v) for k, v in files.items() if k not in exclude_environment_factor_files_list}
    socioeconomic_factor_files = {k: pd.read_csv(v, skiprows=3) for k, v in files.items() if k in exclude_socioeconomic_files_list}

    air_pollution_df = pd.read_csv(files["air_pollution_death"])

    common_country_codes = get_common_country_codes(air_pollution_df, environment_factor_files, socioeconomic_factor_files)
    common_country_codes = sorted(list(common_country_codes))

    filtered_air_pollution_df = air_pollution_df[
        (air_pollution_df['SpatialDimValueCode'].isin(common_country_codes)) &
        (air_pollution_df['Period'] == 2018) &
        (air_pollution_df['Dim1'] == 'Both sexes')
    ]

    aggregated_air_pollution_df = filtered_air_pollution_df.groupby('SpatialDimValueCode', as_index=False)['FactValueNumeric'].sum()
    aggregated_air_pollution_df = aggregated_air_pollution_df.rename(columns={'SpatialDimValueCode': 'common_country_codes', 'FactValueNumeric': 'air_pollution_death'})


    environment_data = []
    for name, df in environment_factor_files.items():
        filtered_df = df[
            (df['iso3_country'].isin(common_country_codes)) &
            (pd.to_datetime(df['start_time']) == '2018-01-01 00:00:00')
        ]
        aggregated_df = filtered_df.groupby('iso3_country', as_index=False)['emissions_quantity'].sum()
        aggregated_df = aggregated_df.rename(columns={'iso3_country': 'common_country_codes', 'emissions_quantity': name})
        environment_data.append(aggregated_df)

    socioeconomic_data = []
    for name, df in socioeconomic_factor_files.items():
        filtered_df = df[df['Country Code'].isin(common_country_codes)][['Country Code', '2018']]
        filtered_df = filtered_df.rename(columns={'Country Code': 'common_country_codes', '2018': name})
        socioeconomic_data.append(filtered_df)

    merged_df = pd.DataFrame({'common_country_codes': common_country_codes})
    for df in environment_data + socioeconomic_data:
        merged_df = pd.merge(merged_df, df, on='common_country_codes', how='left')

    final_df = pd.merge(merged_df, aggregated_air_pollution_df, on='common_country_codes', how='left')

    final_df = final_df.loc[:, final_df.isnull().mean() < 0.5]

    final_df = final_df.dropna()

    final_df = final_df[~final_df['common_country_codes'].isin(['CHN', 'IND'])]

    X = final_df.drop(columns=['common_country_codes', 'air_pollution_death'])
    y = final_df['air_pollution_death']
    
    capitalize_feature_names = []
    for col_names in X.columns.tolist():
        emissions_only = [
            'transportation',
            'forest_clearing',
            'petrochemicals',
            'electricity_generation',
            'residential_commercial',
            'incineration_open_burning',
            'coal',
            'cropland']
        if col_names in emissions_only:
            capitalize_feature_names.append(return_transformed_name(col_names))
        else:
            capitalize_feature_names.append(string.capwords(col_names.replace('_', ' ')))

    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.2, random_state=random_seed)

    scaler = StandardScaler()
    X_train_val_scaled = scaler.fit_transform(X_train_val)
    X_test_scaled = scaler.transform(X_test)

    print("Creating model...")
    xgb_model = xgb.XGBRegressor(
        max_depth=3,
        learning_rate=0.05,
        n_estimators=50,
        min_child_weight=2,
        subsample=0.7,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=random_seed
    )

    xgb_model.fit(X_train_val_scaled, y_train_val)

    print("Predicting...")
    y_train_pred = xgb_model.predict(X_train_val_scaled)
    train_r2 = r2_score(y_train_val, y_train_pred)
    n_train = len(y_train_val)
    p = X_train_val_scaled.shape[1]
    adjusted_train_r2 = 1 - (1 - train_r2) * ((n_train - 1) / (n_train - p - 1))

    y_test_pred = xgb_model.predict(X_test_scaled)
    test_r2 = r2_score(y_test, y_test_pred)
    n_test = len(y_test)
    adjusted_test_r2 = 1 - (1 - test_r2) * ((n_test - 1) / (n_test - p - 1))

    print(f"Adjusted R² Score (Train data): {adjusted_train_r2:.2f}")
    print(f"Adjusted R² Score (Test data): {adjusted_test_r2:.2f}")

    generate_beeSwarm_plot(xgb_model, X_train_val_scaled, X_test_scaled, capitalize_feature_names)

    return adjusted_test_r2, adjusted_train_r2

def start_create_html():
    adjusted_test_r2, adjusted_train_r2 = start_predict_xgboost()
    files = define_files()
    air_pollution_df = pd.read_csv(files["air_pollution_death"])
    environment_factor_files_list = [
        'transportation',
        'coal',
        'cropland',
        'residential_commercial',
        'forest_clearing',
        'petrochemicals',
        'electricity_generation',
        'incineration_open_burning'
    ]
    socioeconomic_files_list = [
        'health_expenditure',
        'urban_population'
    ]

    air_pollution_df = pd.read_csv(files["air_pollution_death"])
    environment_factor_files = {k: v for k, v in files.items() if k in environment_factor_files_list}
    socioeconomic_files = {k: v for k, v in files.items() if k in socioeconomic_files_list}

    common_country_codes = set(air_pollution_df['SpatialDimValueCode'])
    for path in environment_factor_files.values():
        df = pd.read_csv(path)
        common_country_codes &= set(df['iso3_country'])
    for path in socioeconomic_files.values():
        df = pd.read_csv(path, skiprows=3)
        common_country_codes &= set(df['Country Code'])
    common_country_codes_list = list(common_country_codes)


    filtered_air_pollution_df = air_pollution_df[
        (air_pollution_df['SpatialDimValueCode'].isin(common_country_codes_list)) &
        (air_pollution_df['Period'] == 2018) &
        (air_pollution_df['Dim1'] == 'Both sexes')
    ]
    aggregated_air_pollution_df = filtered_air_pollution_df.groupby('SpatialDimValueCode', as_index=False)['FactValueNumeric'].sum()

    environment_dfs = {name: pd.read_csv(path) for name, path in environment_factor_files.items()}
    for name, df in environment_dfs.items():
        df['start_time'] = pd.to_datetime(df['start_time'])
        environment_dfs[name] = df[
            (df['iso3_country'].isin(common_country_codes_list)) &
            (df['start_time'] == '2018-01-01 00:00:00')
        ].groupby('iso3_country', as_index=False)['emissions_quantity'].sum()

    socioeconomic_dfs = {}
    for name, path in socioeconomic_files.items():
        df = pd.read_csv(path, skiprows=3)
        socioeconomic_dfs[name] = df[df['Country Code'].isin(common_country_codes_list)][['Country Code', '2018']].rename(columns={'Country Code': 'iso3_country', '2018': name.capitalize().replace('_', ' ')})

    air_pollution_no_china_india = aggregated_air_pollution_df[~aggregated_air_pollution_df['SpatialDimValueCode'].isin(['CHN', 'IND'])]
    environment_dfs_no_china_india = {name: df[~df['iso3_country'].isin(['CHN', 'IND'])] for name, df in environment_dfs.items()}
    socioeconomic_dfs_no_china_india = {name: df[~df['iso3_country'].isin(['CHN', 'IND'])] for name, df in socioeconomic_dfs.items()}

    choropleth_map = px.choropleth(
        aggregated_air_pollution_df,
        locations='SpatialDimValueCode',
        color='FactValueNumeric',
        color_continuous_scale='OrRd',
        projection='natural earth',
        labels={'FactValueNumeric': 'Air Pollution Deaths', 'SpatialDimValueCode': 'Country Code'}
    )
    choropleth_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        coloraxis_colorbar=dict(title="Air Pollution Deaths")
    )

    scatter_html_blocks = []
    radio_input_info = {}
    for name, df in {**environment_dfs, **socioeconomic_dfs}.items():
        if name in socioeconomic_dfs:
            x_label = socioeconomic_dfs[name].columns[-1]
            scatter_data = pd.merge(df, aggregated_air_pollution_df, left_on='iso3_country', right_on='SpatialDimValueCode')
            scatter_data_no_china_india = pd.merge(socioeconomic_dfs_no_china_india[name], air_pollution_no_china_india, left_on='iso3_country', right_on='SpatialDimValueCode')
        else:
            x_label = 'emissions_quantity'
            scatter_data = pd.merge(df, aggregated_air_pollution_df, left_on='iso3_country', right_on='SpatialDimValueCode')
            scatter_data_no_china_india = pd.merge(environment_dfs_no_china_india[name], air_pollution_no_china_india, left_on='iso3_country', right_on='SpatialDimValueCode')

        scatter_data = scatter_data.dropna(subset=[x_label, 'FactValueNumeric'])
        scatter_data_no_china_india = scatter_data_no_china_india.dropna(subset=[x_label, 'FactValueNumeric'])

        correlation = scatter_data['FactValueNumeric'].corr(scatter_data[x_label])
        correlation_no_china_india = scatter_data_no_china_india['FactValueNumeric'].corr(scatter_data_no_china_india[x_label])

        radio_input_info[name] = append_label_emissions(name, x_label)

        scatter_fig = px.scatter(
            scatter_data,
            x=x_label,
            y='FactValueNumeric',
            text='iso3_country',
            labels={x_label: append_label_emissions(name, x_label), 'FactValueNumeric': 'Air Pollution Deaths', 'iso3_country': 'Country Code'},
            title=f"{append_label_emissions(name, x_label)} vs. Air Pollution Deaths (Correlation: {correlation:.2f})"
        )
        scatter_fig.update_layout(width=1000, height=600, title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

        scatter_fig_no_china_india = px.scatter(
            scatter_data_no_china_india,
            x=x_label,
            y='FactValueNumeric',
            text='iso3_country',
            labels={x_label: append_label_emissions(name, x_label), 'FactValueNumeric': 'Air Pollution Deaths', 'iso3_country': 'Country Code'},
            title=f"{append_label_emissions(name, x_label)} vs. Air Pollution Deaths (Excl. CHN & IND) (Correlation: {correlation_no_china_india:.2f})"
        )
        scatter_fig_no_china_india.update_layout(width=1000, height=600, title={'y': 0.9, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

        scatter_html_blocks.append({
            'name': name,
            'with_china_india': scatter_fig.to_html(full_html=False, include_plotlyjs=False),
            'without_china_india': scatter_fig_no_china_india.to_html(full_html=False, include_plotlyjs=False)
        })

    choropleth_html = choropleth_map.to_html(full_html=False, include_plotlyjs='cdn')
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""
        <html>
            <head>
                <title>Air Pollution and Emissions Analysis</title>
                <link rel="stylesheet" href="styles.css" />
                <script>
                    function showScatterPlot() {{
                        let selectedDataSource = document.querySelector('input[name="data-source"]:checked').value;
                        let excludeOption = document.getElementById('filter-select').value;
                        document.querySelectorAll('.scatter-plot').forEach(plot => plot.style.display = 'none');
                        document.getElementById(`scatter-${{selectedDataSource}}-${{excludeOption}}`).style.display = 'block';
                    }}
                    window.onload = function() {{
                        showScatterPlot();
                    }}
                </script>
            </head>
            <body>
                <h1>Air Pollution Deaths by Country</h1>
                <div class="plot-container">{choropleth_html}</div>
                <hr />
                <div class="scatter-form-container">
                    <h2 class="scatter-form-title">Scatter Plot</h2>
                    <div class="form-container">
                        <div class="radio-container">""" + ''.join(f'\n<label><input type="radio" name="data-source" value="{key}" onclick="showScatterPlot()" checked> {radio_input_info[key]}</label>\n' for key in radio_input_info.keys())
                        + """\n
                            <div class="option-container">
                                <br />
                                <label for="filter-select">Outlier Removal Option:</label>
                                <select id="filter-select" onchange="showScatterPlot()">
                                    <option value="with_china_india" selected>Include CHN & IND</option>
                                    <option value="without_china_india">Exclude CHN & IND</option>
                                </select>
                            </div>
                        </div>
                    </div>
        """)

        for scatter_html in scatter_html_blocks:
            display_style = 'block' if scatter_html['name'] == 'transportation' and 'with_china_india' == 'with_china_india' else 'none'
            f.write(f"""
                    <div id="scatter-{scatter_html['name']}-with_china_india" class="scatter-container scatter-plot" style="display: {display_style};">
                        {scatter_html['with_china_india']}
                    </div>
                    <div id="scatter-{scatter_html['name']}-without_china_india" class="scatter-container scatter-plot" style="display: none;">
                        {scatter_html['without_china_india']}
                    </div>
            """)

        f.write(f"""
                </div>
                <hr />
                <div class="adjusted-score">
                    <h2>Adjusted R&sup2; Score</h2>
                    <p>
                        Train data:<strong> {adjusted_train_r2:.2f}</strong>
                    <br />
                        Test data:<strong> {adjusted_test_r2:.2f}</strong>
                    </p>
                </div>
                <hr />
                <div style="text-align: center; margin-bottom: 50px">
                    <h2>SHAP Beeswarm Plot</h2>
                    <img src="beeswarm_plot.png" alt="SHAP Beeswarm Plot" style="width:80%; height:auto;">
                </div>
            </body>
        </html>
        """)

    print("Saved as HTML: index.html")
    current_cwd = os.getcwd()
    file_uri = 'file:///' + current_cwd + '/index.html'
    webbrowser.open_new(file_uri)

def generate_beeSwarm_plot(xgb_model, X_train_val_scaled, X_test_scaled, feature_names):
    explainer = shap.Explainer(xgb_model, X_train_val_scaled, feature_names=feature_names)
    shap_values = explainer(X_test_scaled)

    shap_fig = plt.figure()
    shap.plots.beeswarm(shap_values, show=False)
    shap_fig.savefig("beeswarm_plot.png", bbox_inches='tight')
    plt.close(shap_fig)
    print("Image has been saved as beeswarm_plot.png")

def main():
    start_create_html()

if __name__ == "__main__":
    main()
