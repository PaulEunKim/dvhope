import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load Dataset 1
pollution_df = pd.read_csv("../data/NEI_pollution_source_2020.csv",
                           encoding="ISO-8859-1")

# Load Dataset 2
health_df = pd.read_csv(
    "../data/PLACES__Local_Data_for_Better_Health__County_Data_2024_release_20241023.csv",
    encoding="ISO-8859-1")
health_df.columns
health_df[[
    'Category', 'Measure', 'Data_Value_Type', 'Data_Value_Footnote_Symbol',
    'Data_Value_Unit', 'Data_Value'
]]

# Prepare Dataset 1
pollution_df[['StateAbbr',
              'County']] = pollution_df['State-County'].str.split(' - ',
                                                                  expand=True)

# Prepare Dataset 2
health_df['County'] = health_df['LocationName']

# Create Composite Key in Both DataFrames
pollution_df['StateCountyKey'] = pollution_df[
    'StateAbbr'] + '-' + pollution_df['County']
health_df[
    'StateCountyKey'] = health_df['StateAbbr'] + '-' + health_df['County']
joined_df = pollution_df.merge(health_df, on="StateCountyKey", how="inner")

joined_df.to_csv("../exploratory_data_analysis/test.csv")
joined_df.columns

label_encoder = LabelEncoder()

categorical_cols = [
    "Pollutant Type", "Pollutant", "MeasureId", "CategoryID",
    "TotalPopulation", "TotalPop18plus", "State-County"
]

# Apply LabelEncoder to each column in categorical_cols
for col in categorical_cols:
    joined_df[col + '_encoded'] = label_encoder.fit_transform(joined_df[col])

joined_df.to_csv("../exploratory_data_analysis/encoded.csv")
joined_df = pd.read_csv("../exploratory_data_analysis/encoded.csv")

filtered_data = joined_df[(joined_df["MeasureId"] == "CANCER")
                          & (joined_df["DataValueTypeID"] == "AgeAdjPrv")]

filtered_data = pd.read_csv("../exploratory_data_analysis/filtered.csv")

# Count the number of unique states per pollutant
pollutants_per_state = filtered_data.groupby('Pollutant')['State'].nunique()

# Get pollutants that appear in all states
shared_pollutants = pollutants_per_state[pollutants_per_state == filtered_data['State'].nunique()].index

# Filter the original DataFrame to only include these shared pollutants
df_shared_pollutants = filtered_data[filtered_data['Pollutant'].isin(shared_pollutants)]
df_shared_pollutants.groupby('State')['Pollutant'].nunique()
# Convert 'Emissions (Tons)' to numeric, forcing errors to NaN
df_shared_pollutants['Emissions (Tons)'] = pd.to_numeric(df_shared_pollutants['Emissions (Tons)'], errors='coerce')

# Replace NaN values with 0
df_shared_pollutants['Emissions (Tons)'] = df_shared_pollutants['Emissions (Tons)'].fillna(0)

df_shared_pollutants.groupby('Pollutant')['Emissions (Tons)'].sum().sort_values(ascending=False)

# # Include 'State' and 'Data_Value' columns from the original DataFrame
# merged_df = df_shared_pollutants[['State', 'Data_Value']].drop_duplicates().merge(pivot_df, on='State', how='left')

# print(merged_df)
pivot_df = df_shared_pollutants.pivot_table(
    index='State-County',
    columns='Pollutant',
    values='Emissions (Tons)',
    aggfunc='sum').fillna(0).reset_index()

merged_df = df_shared_pollutants[['State', 'State-County', 'Data_Value'
                                  ]].drop_duplicates().merge(pivot_df,
                                                             on='State-County',
                                                             how='left')

moved_df = merged_df.copy()  # Optional: Copy to avoid modifying the original
moved_column = moved_df.pop('Data_Value')  # Remove 'Data_Value' from the DataFrame
moved_df['Data_Value'] = moved_column      # Add 'Data_Value' back as the last column

moved_df.to_csv('../data/pivoted_cancer.csv', index=False)