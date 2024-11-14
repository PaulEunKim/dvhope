#%%
!echo %JAVA_HOME%
#%%
# import os
# os.environ['JAVA_HOME'] = "C:\Program Files (x86)\Java\jre1.8.0_202"  # Adjust path as needed
# os.environ['PATH'] = os.environ['JAVA_HOME'] + "bin;" + os.environ['PATH']

from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("CSVImport").getOrCreate()

#%%
# Path to your CSV file
# file_path = "/path/to/your/file.csv"
files = [
    # "../data/air_pollution_death.csv",
    # "../data/cropland-fires_country_emissions.csv",
    # "../data/coal-mining_country_emissions.csv",
    # "../data/electricity-generation_country_emissions.csv",
    # "../data/forest-land-clearing_country_emissions.csv",
    # "../data/health-expenditure.csv",
    # "../data/incineration-and-open-burning-of-waste_country_emissions.csv",
    "../data/NEI_pollution_source_2020.csv",
    # "../data/petrochemicals_country_emissions.csv",
    "../data/PLACES__Local_Data_for_Better_Health__County_Data_2024_release_20241023.csv",
    # "../data/residential-and-commercial-onsite-fuel-usage_country_emissions.csv",
    # "../data/road-transportation_country_emissions.csv",
    # "../data/urban-population.csv"
]

dataframes = {}

for file in files:
    # Read each file
    df = spark.read.csv(file, header=True, inferSchema=True)
    
    # Print the file name
    print(f"Inspecting file: {file}")
    
    # Show the schema to understand the structure
    df.printSchema()
    
    # Show a sample of the data
    df.show(5)
    
    # Add DataFrame to the dictionary using the file name as the key
    dataframes[file] = df

# # Load the CSV file
# df = spark.read.csv('../data/NEI_pollution_source_2020.csv',
#                     header=True,
#                     inferSchema=True)

# Display the schema to verify the data types
df.printSchema()

# Show the first few rows
df.show(1000)


# %%
