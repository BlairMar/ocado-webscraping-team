#%%
### export all the dataframes to AWS RDS ###
import sys
import inspect
import os
import pandas as pd

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from data_processing import Data_Processing
from sqlalchemy import create_engine

DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = 'ocadodb.cughg1zxgq0r.eu-west-2.rds.amazonaws.com' # AWS endpoint
USER = 'postgres'
PASSWORD = '' #### Add password in here ###
PORT = 5432
DATABASE = 'ocado'

class Export_to_AWS_RDS:
    def __init__(self):
        self.engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        self.engine.connect()
        self.process_data = Data_Processing()
        
    def export_all_product_information(self):
        self.process_data.get_df_all_product_data_excl_list_cols().to_sql('all_products_information', engine, if_exists='replace', index=False)   
        
    def export_product_images(self):
       self.process_data.get_df_of_sku_and_product_images().to_sql('product_images', engine, if_exists='replace', index=False)

    def export_product_scraping_categories(self):
        self.process_data.get_df_of_sku_and_scraping_categories().to_sql('product_scraping_categories', engine, if_exists='replace', index=False)

    def export_product_all_categories(self):
        self.process_data.get_df_of_sku_and_all_categories().to_sql('product_all_categories', engine, if_exists='replace', index=False)

    def export_all_categories(self):
        self.process_data.get_df_of_all_categories().to_sql('all_categories', engine, if_exists='replace', index=False)

    def export_product_data_by_category(self):
        for category, df in self.process_data.get_dictionary_of_dataframes().items():
            table_name = category.lower() 
            table_name = table_name.replace(' ','_') 
            df.to_sql(f'{table_name}', engine, if_exists='replace', index=False)
            
#%%
export = Export_to_AWS_RDS()
export.export_product_data_by_category()