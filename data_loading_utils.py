import pandas as pd
import os
import glob

class DataLoader():
    def __init__(self, path, file_pattern = '*.csv') -> None:
        self.path = path
        self.file_pattern = file_pattern

        self.file_paths = glob.glob(os.path.join(self.path, self.file_pattern))

    def get_dfs(self) -> pd.DataFrame():
        """Returns a pandas df from all the csv files specified in the directory"""
        if not os.path.exists(self.path):
            print('Path Not Found!')
        else:
            dfs = [pd.read_csv(file, dtype={'FIPS':str, 'EPA Region':str}, index_col = 0) for file in self.file_paths]

            return pd.concat(dfs).sort_index()
        
if __name__ == '__main__':
    path = os.path.join('data', 'nei_pollution')
    dl = DataLoader(path)

    pollution_df = dl.get_dfs()
    print(pollution_df.describe())
    print(pollution_df.head())
    print(pollution_df.dtypes)