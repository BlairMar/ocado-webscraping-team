#%%
### Imports:
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
from pprint import pprint

import inspect
import sys

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from product import Product
from images import Product_Images

### Class Template:
class OcadoScraper:
    def __init__(self, scrape_categories=False):
        """
        Access Ocado front page using chromedriver
        """
        self.ROOT = 'https://www.ocado.com/' 
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver.get(self.ROOT)
        self._accept_cookies()
        self.category_urls = {}
        self.product_urls = {}
        self.product_data = {}
        self._get_categories(scrape_categories) # populate category_urls attribute

    def _accept_cookies(self):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            _accept_cookies.click()
            print("Cookies button clicked")
        except:
            print("No Cookies buttons found on page")

############################################################################################
# The following 3 functions are used to populate category_urls in the initialiser

    # only used in the initialiser to get all the category urls (from a file if the file exists and scrape_categories=False)
    def _get_categories(self, scrape_categories=True):
        if scrape_categories:
            self._scrape_category_urls()
        else:
            self.category_urls = OcadoScraper.read_data("./data/category_urls")

    # UTILITY function for above function
    # only used by the function _get_categories() to scrape the category urls (and then save to a file)
    def _scrape_category_urls(self):
        self.driver.get(self.ROOT + "browse")
        self._accept_cookies()
        categories_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/div/div/div[1]/div/div[1]/div/ul/li/a')
        self.category_urls = {category.text : category.get_attribute('href').replace("?hideOOS=true", "") for category in categories_web_object}
        for category_name, category_url in self.category_urls.items():
            number_of_products = self._get_number_of_products(category_url)
            self.category_urls[category_name] += '?display=' + number_of_products
        OcadoScraper._save_data("category_urls", self.category_urls, 'w')

    # UTILITY function for above function
    # only used in the function _scrape_category_urls() - gets the number of products in a category
    def _get_number_of_products(self, category_url):
        self.driver.get(category_url)
        number_of_products = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]//div/div[2]/div/span').text.split(' ')[0]
        return number_of_products
    
###########################################################################################################################
    #The following 2 functions are used to populate the product urls dictionary for the specified category
    
    # This function is called by the PUBLIC function scrape_products() and populates the product_urls dictionary for the specified category
    def _scrape_product_urls(self, category_name):
        number_of_products_in_category = self.category_urls[category_name].split('=')[-1]
        self.driver.get(self.category_urls[category_name])
        # self.product_urls[category_name] = self._scroll_to_get_all_product_urls(number_of_products_in_category, 30)
        self.product_urls[category_name] = self._scroll_to_get_all_product_urls(30, 30)

    # UTILITY function for the above function to scroll the page and get all the product urls on the page
    def _scroll_to_get_all_product_urls(self, number_of_products, number_of_items_in_each_scroll):
        urls_temp_web_object = []
        number_of_times_to_scroll = int(int(number_of_products)/number_of_items_in_each_scroll)
        for i in range(number_of_times_to_scroll):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/number_of_times_to_scroll});")
            urls_temp_web_object.extend(self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
            time.sleep(0.5)
        urls_web_object = list(set(urls_temp_web_object))
        urls_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
        urls = [url.get_attribute('href') for url in urls_web_object]
        return urls
    
##############################################################################################################################
# This function is called by the PUBLIC function scrape_products() and scrapes the information and images for 
# all products in the category and puts them in the product_data dictionary
 
    def _scrape_product_data_for_category(self, category_name, download_images):
        for i, url in enumerate(self.product_urls[category_name]): ## remove enumerate 
            self._scrape_product_data(url, download_images)
            if i == 10:  ### get the first i+1 products - just for testing
                break
        self.product_data[category_name] = product_details
      
    def _scrape_product_data(self, url, download_images):
        product_details = {} 
        product = Product(url)
        sku = product.get_sku()
        product_details[sku] = product.scrape_product_data(self.driver) 
        if download_images:
            product.download_images()
        return product_details    
                    
##################################################################################################################  
    # function to read data from a json file
    @staticmethod
    def read_data(path):
        with open(path) as f:
            data = f.read()
            return json.loads(data) 
  
    # function to dump the data to a json file. Used to save the category_urls, product_links and product_data dictionarys to file
    @staticmethod
    def _save_data(filename, data, mode='a'):
        path = f'./data/{filename}'
        with open(path, mode=mode) as f:
            json.dump(data, f) 

###################################################################################################################
    # PUBLIC FUNCTIONS
    
    # returns a list of categories available to scrape on the ocado website
    # if from_file=True returns a list of saved categories from a previous scrape else gets the categories from the website
    def categories_available_to_scrape(self, from_file=True):
        if from_file == True:
            temp_dict = OcadoScraper.read_data("./data/category_urls")
            return list(temp_dict.keys())
        else:
            self._get_categories(True)
            return list(self.category_urls.keys())
               
    def get_categories_with_saved_product_data():
        pass
    # read the json dict 
    
    def get_categories_without_saved_product_data():
        pass
    
    # public function to scrape the products. Pass in a list of categories as a param. If there is saved product data this will be overwritten if we scrape again for the category
    def scrape_products(self, categories="ALL", download_images=False):
        if categories == "ALL":
            categories = self.category_urls.keys()        
        for category in categories:
            #### now read the data from the json dict into product_data attribute, clear the data from the json 
            self._scrape_product_urls(category)
            self._scrape_product_data_for_category(category, download_images)
            OcadoScraper._save_data("product_data", self.product_data) #save data into the file after each scrape of a category
        # save each time we scrape - put inside for loop
        OcadoScraper._save_data("product_urls", self.product_urls)     
        print(f"Product urls and product data from the {categories} categories saved successfully")

    def scrape_product(self, url, download_images):
        self.driver.get(url)
        self._accept_cookies()
        return self._scrape_product_data(url, download_images)
         
        
####################################################################### 
# This is not being used right now       
    def zoom_page(self, zoom_percentage=100):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")
#######################################################################


if __name__ == '__main__':
    pass
    # ocado = OcadoScraper() 
    # ocado.scrape_products()

#%%
ocado = OcadoScraper()
# categories_to_scrape = ["Clothing & Accessories", "Bakery"]
categories_to_scrape = ["Clothing & Accessories", 'Bakery']
# ocado.scrape_products(categories_to_scrape, True)
ocado.scrape_products(categories_to_scrape)
# print(len(ocado.product_urls["Clothing & Accessories"]))
#%%
ocado = OcadoScraper()
url = 'https://www.ocado.com/products/gail-s-seeded-sourdough-540647011'
data = ocado.scrape_product(url, False)
pprint(data)

#%%
ocado.categories_available_to_scrape()

# %%

