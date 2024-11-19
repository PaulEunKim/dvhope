import pandas as pd
import numpy as np
import os
import json

from data_loading_utils import DataLoader
from pprint import pprint

pollution_path = os.path.join('data', 'nei_pollution')
dl = DataLoader(pollution_path)
df = dl.get_dfs()

emissions_col = 'Emissions (Tons)'
print(df.columns)

sums_df = df.groupby(['State', 'NAICS', 'Pollutant'], as_index=False).sum()

# get national sums and label them
national_sums = df.groupby(['NAICS', 'Pollutant'], as_index=False).sum()
national_sums['State'] = 'USA'

sums_df = pd.concat([national_sums, sums_df])
print(sums_df.describe())

cancer_causing = ['Acetaldehyde', 
                  'Acrolein', 
                  'Formaldehyde' 
                  '2,2,4-Trimethylpentane', 
                  'Benzene', 
                  '1,3-Butadiene', 
                  'Polycyclic Organic Matter', 
                  'Nitrogen Oxides',
                  'Hexane', 
                  'Methanol']

sparse_list = []
dense_list = []

def update_dict(df: pd.DataFrame, sparse_list: list = sparse_list, dense_list: list = dense_list, n: int = 10, filter_co2=True) -> None:
    """
    Creates a list of nested dicts in various formats.
    
    Dense list can be used to create chord diagrams per state
    """
    d_sparse = {'state': df.name}
    d_dense = {'state': df.name}

    sparse_df = df[['NAICS', 'Pollutant', emissions_col]].dropna(subset=emissions_col)

    if filter_co2:
        df = df.loc[df['Pollutant'] != 'Carbon Dioxide', :]

    df_cancer = df.loc[df['Pollutant'].isin(cancer_causing), :]

    dense_df = make_dense_pollution_matrix(df)
    dense_cancer_df = make_dense_pollution_matrix(df_cancer)

    d_sparse['data'] = sparse_df.to_dict('list')
    d_dense['All Pollutants'] = dense_df.to_dict('split')
    d_dense['Cancer Causing Pollutants'] = dense_cancer_df.to_dict('split')

    sparse_list.append(d_sparse)
    dense_list.append(d_dense)

def make_dense_pollution_matrix(df: pd.DataFrame, n: int= 10) -> pd.DataFrame:
    # get top n industries and pollutants in state to make square matrix
    top_naics = df.groupby('NAICS').sum().sort_values(emissions_col, ascending=False).index[:n]
    top_pollutants = df.groupby('Pollutant').sum().sort_values(emissions_col, ascending=False).index[:n]

    dense_df = df[['NAICS', 'Pollutant', emissions_col]].set_index(['NAICS', 'Pollutant']).unstack()
    dense_df = dense_df.droplevel(level=0, axis=1)

    # filter df now to preserve ordering
    dense_df = dense_df.loc[top_naics, top_pollutants]

    # need to make dense df a square
    zeroes_df = dense_df.copy().T
    # assign the reverse values to 0
    zeroes_df.loc[:,:] = 0

    # Need to ensure indices line up to columns
    col_order = list(dense_df.index) + list(dense_df.columns)

    dense_df = pd.concat([dense_df, zeroes_df])
    dense_df = dense_df.reindex(col_order)
    dense_df = dense_df[col_order]

    return dense_df[col_order].fillna(0)

sums_df[['State', 'NAICS', 'Pollutant', emissions_col]].groupby('State', group_keys=False).apply(lambda x: update_dict(x, filter_co2=False))

pprint(dense_list[0])

with open(os.path.join('data', 'states_pollution_sparse.json'), 'w') as f:
    json.dump(sparse_list, f, indent=4)

with open(os.path.join('data', 'states_pollution_dense.json'), 'w') as f:
    json.dump(dense_list, f, indent=4, allow_nan=False)

# pprint(d['California'])
# print(sums_df[emissions_col].unstack())

# sums_df[emissions_col].groupby(level=0).apply(lambda x: update_d(x.name, x.to_dict()))

# sums_df[emissions_col].unstack().to_json(os.path.join('data', 'state_pollutants.json'), orient='split')

# sums_df[emissions_col].to_csv(os.path.join('data', 'state_pollutants.csv'))