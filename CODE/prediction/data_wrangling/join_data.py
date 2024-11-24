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
filtered_data.to_csv('../exploratory_data_analysis/filtered.csv')
