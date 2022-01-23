#%%
#### Processes the raw data json using pandas to get 
#### dataframes that can be exported directly to Postgres as normalized tables
import sys
import inspect
import os
import json
import pandas as pd

class DataProcessing:
    def __init__(self):
        self.product_data_path = self.data_path = '../data/product_data'
        self.recipes_data_path = '../data/recipes_data'
        self.raw_product_data = DataProcessing._read_data(self.product_data_path)
        self.raw_recipes_data = DataProcessing._read_data(self.recipes_data_path)
        self.dictionary_of_category_dataframes = {}
        self._product_data_to_dataframes() # populate dictionary_of_category_dataframes
        self.all_products_df = pd.DataFrame()
        self._all_products_df() # populate dataframe _all_products_df
        self.all_recipes_df = self.get_df_of_all_recipes()

    @staticmethod
    def _read_data(path):
        '''
        Reads data from file.

        Args:
            path (str): path to the json file to be read

        Returns:
            Python object containing the data at path
        '''
        with open(path) as f:
            data = f.read()
            return json.loads(data) 
        
    # populates self.dictionary_of_category_dataframes which is a dictionary of dataframes, one for each category
    # drops any duplicates within the category in case there are any
    def _product_data_to_dataframes(self):
        '''
        Takes the data from raw_product_data and transforms it into pandas Dataframes.
        The Dataframes are stored in dictionary_of_category_dataframes.

        Returns:
            dict: dictionary of dataframes containing the data in raw_product_data
        '''
        for key, value in self.raw_product_data.items():
                df_for_category = pd.DataFrame.from_records(value).transpose()
                category = [key] * len(value.items())  # adding a column for the category
                DataProcessing._reformat_column_names(df_for_category)
                df_for_category.index.names = ['sku']
                df_for_category['scraping_category'] = category              
                self.dictionary_of_category_dataframes[key] = (df_for_category
                                .reset_index()
                                .drop_duplicates(subset=['sku'], keep='first')) 
        return self.dictionary_of_category_dataframes

    @staticmethod          
    def _reformat_column_names(dataframe):
        '''
        Removes blank spaces and replaces uppercase characters with lowercase characters 
        in the columns names of a pandas dataframe.

        Args:
            DataFrame: pandas dataframe object

        Returns:
            DataFrame: pandas dataframe object with no blank spaces or uppercase characters in column names
        '''
        dataframe.columns = dataframe.columns.str.lower()
        dataframe.columns = dataframe.columns.str.replace(' ','_')
        return dataframe
                
    # Populates the all_products_df dataframe attribute. 
    # This attribute is a concatenated dataframe where the last column will be different depending on the category the product was scraped in
    # Note this dataframe will have more than one row for a product if the product is in more than one scraping category
    def _all_products_df(self):
        '''
        Populates the all_products_df dataframe attribute. 
        This attribute is a concatenated dataframe where the last column will be different depending on the category the product was scraped in
        Note this dataframe will have more than one row for a product if the product is in more than one scraping category
        Only call in the initialiser

        Returns:
            DataFrame: pandas dataframe with product data
        '''
        temp_df = pd.concat(self.dictionary_of_category_dataframes.values(), ignore_index=True)
        DataProcessing._reformat_column_names(temp_df)
        self.all_products_df = temp_df
        return self.all_products_df
        
######################################################################   
    #PUBLIC functions
                 
    def get_raw_product_data(self):
        '''
        returns the dictionary of product_data  - export to S3 bucket
        '''
        return self.raw_product_data   

    
    def get_dictionary_of_dataframes(self):
        '''
        returns a dictionary of dataframes, one for each category
        '''
        return self.dictionary_of_category_dataframes
    
    def get_dataframe_by_category(self, category_name):
        '''
        returns a dataframe for the specified category
        '''
        return self.dictionary_of_category_dataframes[category_name]
    
    def get_number_of_unique_products(self):
        '''
        returns number of unique products
        '''
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
    
    def get_df_of_all_recipes(self):
        recipe_list = [list(a.values())[0] for a in dp.raw_recipes_data]
        return pd.DataFrame(recipe_list)
# #%%    
# process_data = DataProcessing()

# # %%
# process_data.get_df_all_product_data_excl_list_cols()
