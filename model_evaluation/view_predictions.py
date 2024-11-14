# %%
import h2o
h2o.init()
import pandas as pd

model_path = "../saved_models\GBM_grid_1_AutoML_1_20241110_153230_model_13"
saved_model = h2o.load_model(model_path)

df = pd.read_csv('../exploratory_data_analysis/filtered.csv')
df.columns

input_features = [
    "Pollutant Type_encoded", "Pollutant_encoded", "MeasureId_encoded",
    "CategoryID_encoded", "TotalPopulation_encoded", "TotalPop18plus_encoded",
    "State-County_encoded", "Low_Confidence_Limit", "High_Confidence_Limit", 
    "TotalPopulation", "TotalPop18plus", "Data_Value"
]

output_feature = "Data_Value"

metadata_columns = [
    "State", "State-County", "Pollutant", "Site Name", "EIS Facility ID", 
    "Facility Type", "Street Address", "NAICS", "Lat/Lon", "EPA Region", 
    "FIPS", "StateAbbr_x", "County_x", "StateCountyKey", "Year", 
    "StateAbbr_y", "StateDesc", "LocationName", "DataSource", 
    "Category", "Data_Value_Footnote_Symbol", "Data_Value_Footnote", 
    "Short_Question_Text", "Geolocation", "County_y"
]
h2o_df = h2o.H2OFrame(df)

splits = h2o_df.split_frame(ratios = [0.8], seed = 1)
train = splits[0]
test = splits[1]

predictions = saved_model.predict(test)
print(predictions)
# %%
