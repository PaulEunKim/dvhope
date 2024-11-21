import pandas as pd
df = pd.read_csv("../exploratory_data_analysis/filtered.csv")

# Count the number of unique states per pollutant
pollutants_per_state = df.groupby('Pollutant')['State'].nunique()

# Get pollutants that appear in all states
shared_pollutants = pollutants_per_state[pollutants_per_state == df['State'].nunique()].index

# Filter the original DataFrame to only include these shared pollutants
df_shared_pollutants = df[df['Pollutant'].isin(shared_pollutants)]
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

moved_df.to_csv('pivoted_cancer.csv', index=False)