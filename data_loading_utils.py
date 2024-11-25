import pandas as pd
import pyspark.pandas as ps
import os
import glob

from xlsx2csv import Xlsx2csv
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.functions import lpad
from functools import reduce

class DataLoader():
    def __init__(self, path, reader = pd.read_csv, file_pattern = '*.csv') -> None:
        self.path = path
        self.file_pattern = file_pattern
        self.reader = reader

        self.file_paths = glob.glob(os.path.join(self.path, self.file_pattern))

    def get_dfs(self, read_kwargs = {'dtype':{'FIPS':str, 'EPA Region':str}}) -> pd.DataFrame:
        """Returns a pandas df from all the csv files specified in the directory"""
        if not os.path.exists(self.path):
            print('Path Not Found!')
        elif os.path.isdir(self.path):
            dfs = [self.reader(file, **read_kwargs) for file in self.file_paths]

            return pd.concat(dfs).sort_index()
        else:
            return self.reader(path, **read_kwargs)
        
    def get_spark_dfs(self, spark_kwargs = {'header':True, 'inferSchema':True}):

        spark = SparkSession.builder.appName('CsvReader').getOrCreate()

        spark_dfs = [spark.read.csv(file, **spark_kwargs) for file in self.file_paths]

        # union all spark dfs into one
        spark_df = reduce(lambda l, r: l.unionByName(r), spark_dfs)
        # fill leading zeroes on fips columns
        spark_df = spark_df.withColumn('FIPS', lpad(spark_df['FIPS'].cast(StringType()), 5, '0'))


        return spark_df
            
    def xlsx_to_csv(self, new_dir = None, overwrite_existing = False) -> None:
        """Converts all xlsx files in a directory to csv. By default, saves the new files to the same directory as the old files"""
        save_dir = self.path if new_dir is None else save_dir

        excel_files = glob.glob(os.path.join(self.path, '*.xlsx'))

        for file in excel_files:
            base_name = os.path.splitext(os.path.basename(file))[0]

            print(f'Converting {base_name}')

            new_file_name = base_name + '.csv'

            if not os.path.exists(os.path.join(save_dir, new_file_name)) or overwrite_existing:
                Xlsx2csv(file).convert(os.path.join(save_dir, new_file_name))

            else: 
                print(f'{new_file_name} already exists in {save_dir}')

            print('All Done!')
        
if __name__ == '__main__':
    path = os.path.join('data', 'nei_pollution')
    dl = DataLoader(path)

    pollution_df = dl.get_dfs()
    print(pollution_df.describe())
    print(pollution_df.head())
    print(pollution_df.dtypes)