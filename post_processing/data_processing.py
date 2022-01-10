#%%
import sys
import inspect
import os
import json
import pandas as pd

class DataProcessing:
    def __init__(self):
        self.product_data_path = self.data_path = '../data/product_data'
        self.raw_product_data = DataProcessing._read_data(self.product_data_path)
        self.dictionary_of_category_dataframes = {}
        self._product_data_to_dataframes() # populate dictionary_of_category_dataframes
        self.all_products_df = pd.DataFrame()
        self._all_products_df() # populate dataframe _all_products_df 

    @staticmethod
    def _read_data(path):
        with open(path) as f:
            data = f.read()
            return json.loads(data) 
        
    # populates self.dictionary_of_category_dataframes which is a dictionary of dataframes, one for each category
    # drops any duplicates within the category in case there are any
    def _product_data_to_dataframes(self):
        for key, value in self.raw_product_data.items():
                df_for_category = pd.DataFrame.from_records(value).transpose()
                category = [key] * len(value.items())  # adding a column for the category
                DataProcessing._reformat_column_names(df_for_category)
                df_for_category.index.names = ['sku']
                df_for_category['scraping_category'] = category              
                self.dictionary_of_category_dataframes[key] = (df_for_category
                                .reset_index()
                                .drop_duplicates(subset=['sku'], keep='first')) 
             
    @staticmethod          
    def _reformat_column_names(dataframe):        
        dataframe.columns = dataframe.columns.str.lower()
        dataframe.columns = dataframe.columns.str.replace(' ','_')
                
    # Populates the all_products_df dataframe attribute. 
    # This attribute is a concatenated dataframe where the last column will be different depending on the category the product was scraped in
    # Note this dataframe will have more than one row for a product if the product is in more than one scraping category
    def _all_products_df(self):
        temp_df = pd.concat(self.dictionary_of_category_dataframes.values(), ignore_index=True)
        DataProcessing._reformat_column_names(temp_df)
        self.all_products_df = temp_df
        
######################################################################   
    #PUBLIC functions
    
    # returns a dictionary of dataframes, one for each category
    def get_dictionary_of_dataframes(self):
        return self.dictionary_of_category_dataframes
    
    # returns a dataframe for the specified category
    def get_dataframe_by_category(self, category_name):
        return self.dictionary_of_category_dataframes[category_name]
    
    def get_number_of_unique_products(self):
        return len(self.get_df_all_product_data_excl_list_cols().index)

###################################################################    
# the following functions are used to create dataframes, normalizing the data so we can export to SQL 
    def get_df_all_product_data_excl_list_cols(self):
        return self.all_products_df[self.all_products_df.columns[:-3]].drop_duplicates('sku').reset_index().drop('index', axis=1)
    
    def get_df_of_sku_and_scraping_categories(self):
        return self.all_products_df[['sku', 'scraping_category']].reset_index().drop('index', axis=1)
    
    def get_df_of_sku_and_product_images(self):
        return self.all_products_df[['sku', 'image_links']].drop_duplicates('sku').explode('image_links').sort_values('sku').reset_index().drop('index', axis=1)
    
    def get_df_of_sku_and_all_categories(self):
        return self.all_products_df[['sku', 'categories']].drop_duplicates('sku').explode('categories').sort_values('sku').reset_index().drop('index', axis=1)

    def get_df_of_all_categories(self):
        df =  pd.DataFrame(self.get_df_of_sku_and_all_categories()['categories'].unique())
        return df.rename(columns={df.columns[0]: "categories" })
                
#%%    
process_data = DataProcessing()

# %%