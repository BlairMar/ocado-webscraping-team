#%%
### Export all the dataframes to AWS RDS as normalized SQL tables ###

import sys
import inspect
import os
import pandas as pd

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from data_processing import DataProcessing
from sqlalchemy import create_engine

DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
ENDPOINT = 'ocadodb.cughg1zxgq0r.eu-west-2.rds.amazonaws.com' # AWS endpoint
USER = 'postgres'
PASSWORD = '' #### Add password in here ###
PORT = 5432
DATABASE = 'ocado' 

class Export_to_AWS_RDS:
    def __init__(self, database_type=DATABASE_TYPE, dbapi=DBAPI, user=USER, port=PORT, endpoint=ENDPOINT, password=PASSWORD, database=DATABASE):
        self.engine = create_engine(f"{database_type}+{dbapi}://{user}:{password}@{endpoint}:{port}/{database}")
        self.engine.connect()
        self.process_data = DataProcessing()
        
  ########################################################
  # Normalized data  
  
    # Creates a table 'all_products_information' in SQL of all products on the ocado website and all information that was not scraped in list form
    def export_all_products_information(self):
        self.process_data.get_df_all_product_data_excl_list_cols().to_sql('all_products_information', self.engine, if_exists='replace', index=False)   
        
    # Creates a table 'product_images' where the list of image links for each product are extracted into a separate table to satisfy the first normal form
    def export_product_images(self):
       self.process_data.get_df_of_sku_and_product_images().to_sql('product_images', self.engine, if_exists='replace', index=False)

    # Creates a table 'product_scraping_categories' where the list of scraping categories each product is in is extracted into a separate table to satisfy the first normal form
    def export_product_scraping_categories(self):
        self.process_data.get_df_of_sku_and_scraping_categories().to_sql('product_scraping_categories', self.engine, if_exists='replace', index=False)

    # Creates a table 'product_all_categories' where the list of categories for each product are extracted into a separate table to satisfy the first normal form
    def export_product_all_categories(self):
        self.process_data.get_df_of_sku_and_all_categories().to_sql('product_all_categories', self.engine, if_exists='replace', index=False)

    # Creates a table of all the unique categories on the ocado website
    def export_all_categories(self):
        self.process_data.get_df_of_all_categories().to_sql('all_categories', self.engine, if_exists='replace', index=False)
        
    # Just calls the 5 functions above to get all the tables
    def export_all_normalized_tables(self):
        self.export_all_products_information()
        self.export_product_images()
        self.export_product_scraping_categories()
        self.export_product_all_categories()
        self.export_all_categories()
        
###########################################################

    # Creates a separate table for each category including all the scraped information
    # Note: the list entries are not transformed in these tables and are still in list format
    def export_product_data_by_category(self):
        for category, df in self.process_data.get_dictionary_of_dataframes().items():      
            table_name = Export_to_AWS_RDS._reformat_string(category)   
            df.to_sql(f'{table_name}', self.engine, if_exists='replace', index=False)
          
    @staticmethod          
    def _reformat_string(string):   
        return string.lower().replace(' ', '_').replace('&', '').replace(',', '').replace('__', '_')
                  
#%%
# export = Export_to_AWS_RDS()

# # Fill in your details below
# # Note: create server with endpoint details in pgAdmin and a database inside the server to view the tables 
# # export = Export_to_AWS_RDS(endpoint='', password='', database='')
# #%%
# export.export_all_normalized_tables()
# %%

