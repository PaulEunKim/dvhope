"""
Run this code if you need to break up the 1M row NEI pollution data set into seperate, smaller csv files. 

Needs access to the 'NEI_pollution_source_2020.csv' dataset that won't fit onto the git repo all on its own.
"""
# %%
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geodatasets
import os
import ast
import math

from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
# %%
df = pd.read_csv(os.path.join('data', 'NEI_pollution_source_2020.csv'), dtype={'FIPS':str}, index_col=0)
df.head()

# %%
df['Lat/Lon'] = df['Lat/Lon'].apply(ast.literal_eval)
df.head()

# %%
file_size = os.path.getsize(os.path.join('data', 'NEI_pollution_source_2020.csv')) / 1e6
# github filesize limit is 50 Mb. Need to split this file into several files to upload them
n_files = math.ceil(file_size / 50)
n_rows = df.shape[0]
row_limit = n_rows // n_files

splits = range(0, n_rows + 1, row_limit)

save_data_dir = os.path.join('data', 'nei_pollution')

if not os.path.exists(save_data_dir):
    os.makedirs(save_data_dir)

for i, start_end in enumerate(zip(splits[:-1], splits[1:])):
    start = start_end[0]
    end = start_end[1]

    file_name = f'NEI_point_source_pollution_{i}.csv'
    df.iloc[start:end, :].to_csv(os.path.join(save_data_dir, file_name))

print('All done!')



