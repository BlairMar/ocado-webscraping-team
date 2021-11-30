#%%
import sys
import inspect
import os
import pandas as pd
from sqlalchemy import create_engine
import boto3

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from OcadoScraper import OcadoScraper

class Data_Processing:
    def __init__(self):
        self.product_data_path = self.data_path = './data/product_data'
        self.scraper = OcadoScraper() 
        self.raw_product_data = self.scraper._read_data(self.product_data_path)
        self.dictionary_of_category_dataframes = {}
        self._product_data_to_dataframes() # populate dictionary_of_category_dataframes
        self.all_products_df = pd.DataFrame()
        self._all_products_df() # populate dataframe _all_products_df 
        
    # populates self.dictionary_of_category_dataframes which is a dictionary of dataframes, one for each category
    # drops any duplicates within the category in case there are any
    def _product_data_to_dataframes(self):
        for key, value in self.raw_product_data.items():
                df_for_category = pd.DataFrame.from_records(value).transpose()
                df_for_category.index.names = ['Sku']
                category = [key] * len(value.items())  # adding a column for the category
                df_for_category['scraping_category'] = category              
                self.dictionary_of_category_dataframes[key] = (df_for_category
                                .reset_index()
                                .drop_duplicates(subset=['Sku'], keep='first')) # method chaining 

    # Populates the all_products_df dataframe attribute. 
    # This attribute is a concatenated dataframe where the last column will be different depending on the category the product was scraped in
    # Note this dataframe will have more than one row for a product if the product is in more than one scraping category
    def _all_products_df(self):
        temp_df = pd.concat(self.dictionary_of_category_dataframes.values(), ignore_index=True)
        temp_df.columns= temp_df.columns.str.lower()
        temp_df.columns = temp_df.columns.str.replace(' ','_')
        self.all_products_df = temp_df
                
    # returns the dictionary of product_data  - export to S3 bucket
    def get_raw_product_data(self):
        return self.raw_product_data   
    
    # returns a dictionary of dataframes, one for each category
    def get_dictionary_of_dataframes(self):
        return self.dictionary_of_category_dataframes
    
    # returns a dataframe for the specified category
    def get_dataframe_by_category(self, category_name):
        return self.dictionary_of_category_dataframes[category_name]
    
    def get_number_of_unique_products(self):
        return len(self.get_dataframe_all_product_data_excl_list_cols().index)

###################################################################    
# the following functions are used to create dataframes, normalizing the data so we can export to SQL 
    def get_dataframe_all_product_data_excl_list_cols(self):
        return self.all_products_df[self.all_products_df.columns[:-3]].drop_duplicates('sku')
    
    def get_dataframe_of_sku_and_scraping_categories(self):
        return self.all_products_df[['sku', 'scraping_category']] 
    
    def get_dataframe_of_sku_and_product_images(self):
        return self.all_products_df[['sku', 'image_links']].drop_duplicates('sku').explode('image_links').sort_values('sku')
    
    def get_dataframe_of_sku_and_all_categories(self):
        return self.all_products_df[['sku', 'categories']].drop_duplicates('sku').explode('categories').sort_values('sku')

    def get_dataframe_of_all_categories(self):
        return pd.DataFrame(self.get_dataframe_of_sku_and_all_categories()['categories'].unique())
                
#%%    
process_data = Data_Processing()
#%%


        

