#%%
### Imports:
from types import DynamicClassAttribute
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
import shutil
from pprint import pprint
from ThreadingClass import CategoryPageThread
from ThreadingClass import ScrapingProductsThread
import inspect
import sys
from datetime import datetime

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from product import Product
from images import Product_Images

### Class Template:
class OcadoScraper:
    def __init__(self, scrape_categories=False, headless=True):
        """
        Access Ocado front page using chromedriver
        """
        self.ROOT = 'https://www.ocado.com/'
        self.data_path = './data/'
        self.category_url_path = self.data_path + 'category_urls'
        self.product_data_path = self.data_path + 'product_data'
        self.chrome_options = webdriver.ChromeOptions()
        self.headless = headless
        if self.headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument('window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        if not self.headless:
            self.driver.maximize_window()
        self.driver.get(self.ROOT)
        OcadoScraper._accept_cookies(self.driver)
        self.category_urls = {}
        self.product_urls = {}
        self.product_data = {}
        self._get_categories(scrape_categories) # populate category_urls attribute

    @staticmethod
    def _accept_cookies(driver):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
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
            try:
                self.category_urls = OcadoScraper._read_data("./data/category_urls")
            except Exception as e:
                print("Error: No stored data for category urls, re-run the scraper with scrape_categories=True")
                return

    # UTILITY function for above function
    # only used by the function _get_categories() to scrape the category urls (and then save to a file)
    def _scrape_category_urls(self):
        self.driver.get(self.ROOT + "browse")
        OcadoScraper._accept_cookies(self.driver)
        categories_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/div/div/div[1]/div/div[1]/div/ul/li/a')
        self.category_urls = {category.text : category.get_attribute('href').replace("?hideOOS=true", "") for category in categories_web_object}
        for category_name, category_url in self.category_urls.items():
            number_of_products = self._get_number_of_products(category_url)
            self.category_urls[category_name] += '?display=' + number_of_products
        self._save_data("category_urls", self.category_urls)
        return self.category_urls

    # UTILITY function for above function
    # only used in the function _scrape_category_urls() - gets the number of products in a category
    def _get_number_of_products(self, category_url, close_window=False):
        self.driver.get(category_url)
        number_of_products = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]//div/div[2]/div/span').text.split(' ')[0]
        if close_window:
            self.driver.close()
        return number_of_products
    
###########################################################################################################################
    #The following 2 functions are used to populate the product urls dictionary for the specified category
    
    # This function is called by the PUBLIC function scrape_products() and populates the product_urls dictionary for the specified category

    #TO TIDY UP THIS
    def _scrape_product_urls(self, category_url, category_name, threads_number=4):
        s = datetime.now()
        number_of_products_on_page = int(category_url.split('=')[-1])
        if number_of_products_on_page < 1500: #if pages are too small only use one thread
            threads_number = 1
        if threads_number == 4 and number_of_products_on_page > 10000: #if pages are too big reduces number of threads from 4 to 3
            threads_number = 3
        number_of_scrolls = number_of_products_on_page/35
        if threads_number-1: #if more than one thread is being used
            scroll_points = []
            for i in range(threads_number+1): #compute scrolling boundaries
                scroll_points.append(i/threads_number)
            thread_list = []
            for i in range(len(scroll_points)-1): #add threads to a list
                thread_list.append(CategoryPageThread(i, category_url, number_of_scrolls, scroll_points[i], scroll_points[i+1], OcadoScraper._scroll_to_get_product_urls, headless=self.headless))
            for thread in thread_list:
                thread.start() #start s crolling and scraping in each thread's browser
            while True: #wait for threads to finish running
                threads_activity = [thread.active for thread in thread_list]
                if True not in threads_activity:
                    break
            data = []
            for thread in thread_list: #bring data together 
                data.extend(thread.product_urls)
            self.product_urls[category_name] = list(set(data))
        else: #if we only use one thread
            self.driver.get(category_url)
            OcadoScraper._accept_cookies(self.driver)
            self.product_urls[category_name] = OcadoScraper._scroll_to_get_product_urls(self.driver, number_of_scrolls)
        print(datetime.now()-s)

    # UTILITY function for the above function to scroll the page and get all the product urls on the page
    @staticmethod
    def _scroll_to_get_product_urls(driver, number_of_scrolls, start_scrolling_at=0, stop_scrolling_at=1):
        urls_temp_web_object = []
        for i in range(int(start_scrolling_at*number_of_scrolls), int(stop_scrolling_at*number_of_scrolls)):
            if i == int(start_scrolling_at*number_of_scrolls):
                time.sleep(0.5)
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/number_of_scrolls});")
            time.sleep(0.5)
            urls_temp_web_object.extend(driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
        urls_web_object = list(set(urls_temp_web_object))
        # urls_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
        urls = [url.get_attribute('href') for url in urls_web_object]
        return urls
    
##############################################################################################################################
# This function is called by the PUBLIC function scrape_products() and scrapes the information and images for 
# all products in the category and puts them in the product_data dictionary 
    def _scrape_product_data_for_category(self, category_name, download_images):
        product_details = {}
        split_urls_lists = OcadoScraper._split_list(self.product_urls[category_name], 4)
        thread_list = []
        for i in range(len(split_urls_lists)): #add threads to a list
            thread_list.append(ScrapingProductsThread(i, split_urls_lists[i], OcadoScraper._scrape_product_data, download_images, headless=self.headless))
        for thread in thread_list:
            thread.start() #start scraping the urls allocated to each thread
        while True: #wait for threads to finish running
            threads_activity = [thread.active for thread in thread_list]
            if True not in threads_activity:
                break
        for thread in thread_list: #bring the data together
            product_details.update(thread.product_details)
        self.product_data[category_name] = product_details
    
    @staticmethod
    def _scrape_product_data(driver, url, download_images):
        product = Product(url)
        return product.scrape_product_data(driver, download_images)
    
    @staticmethod
    def _split_list(lst, n):
        divided_list = []
        for i in range(n):
            divided_list.append(lst[i::n])
        return divided_list
                    
##################################################################################################################  

    # Function to read data from a json file
    @staticmethod
    def _read_data(path):
        with open(path) as f:
            data = f.read()
            return json.loads(data) 

    # Function to dump the data to a json file. Used to save the category_urls, product_links and product_data dictionarys to file
    def _save_data(self, filename, data, mode='w', indent=4):
        OcadoScraper._create_folder(self.data_path)
        with open(self.data_path + f'{filename}', mode=mode) as f:
            json.dump(data, f, indent=indent) 
            
    @staticmethod
    def _create_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
                        
###################################################################################################################
    # PUBLIC FUNCTIONS
    
    # returns a list of categories available to scrape on the ocado website
    # if from_file=True returns a list of saved categories from a previous scrape else gets the categories from the website
    def categories_available_to_scrape(self, from_file=True):
        if from_file == True:
            if os.path.exists(self.category_url_path):
                temp_dict = OcadoScraper._read_data(self.category_url_path)
                return list(temp_dict.keys())
            else: 
                print("Error: No stored data for category urls, re-run this function with from_file=False")
                return                 
        else:
            self._get_categories(True)
            return list(self.category_urls.keys())
        
    # Gets a dictionary showing which categories have scraped data saved in the product_data json file. Also shows how many items from that category have been scraped.     
    def get_categories_with_saved_product_data(self):
        if os.path.exists(self.product_data_path):
            temp_dict = OcadoScraper._read_data(self.product_data_path)
            return {category : int(self.number_of_products_saved_from_category(category)) for category in temp_dict.keys()}
        else:
            print('No categories with saved product data')
            return 
     
    # Gets a list of categories that do not have saved product data. This list can be passed as a parameter to the scrape_products() function to scrape remaining categories                
    def get_categories_without_saved_product_data(self):
        all_categories = {}
        if os.path.exists(self.category_url_path):
            all_categories = OcadoScraper._read_data(self.category_url_path).keys()
        else: 
            self._scrape_category_urls()
            all_categories = self.category_urls.keys()
        if os.path.exists(self.product_data_path):
            stored_data = self.get_categories_with_saved_product_data().keys()
            return list(set(all_categories).difference(set(stored_data)))
        else:
            return list(all_categories)
    
    # Beware! - deletes the product_data saved json file if it exists.                     
    def delete_saved_product_data(self):
        if os.path.exists(self.product_data_path):
            os.remove(self.product_data_path)
        else: 
            print("Can not delete the file as it doesn't exist")
            
    # Delete the saved product data for the specified category name. 
    # Used for example if a scrape of a category has gone wrong and not all the products have been scraped for that category.                     
    def delete_saved_product_data_for_category(self, category_name):
        if os.path.exists(self.product_data_path):            
            product_data = OcadoScraper._read_data(self.product_data_path) 
            product_data.pop(category_name, "No stored data for that category")
            self._save_data("product_data", product_data) 
        else:
            print("No stored data file")
            
    # Beware! - deletes the folder storing all the images.  
    @staticmethod                    
    def delete_downloaded_images():
        path = './data/images/'
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))                    
            
    # Get the number of products saved to the product_data json file for the specified category name.
    def number_of_products_saved_from_category(self, category_name):
        if os.path.exists(self.product_data_path):
            temp_dict = OcadoScraper._read_data(self.product_data_path)
            if category_name in temp_dict.keys():
                return len(temp_dict[category_name])
        print("No products saved for this category")
    
    # The number of products in the categories on the ocado website            
    def number_of_products_in_categories(self, categories='ALL'):
        if categories == 'ALL':
            categories = self.category_urls.keys()
        number_of_products = {category_name : int(self.category_urls[category_name].split('=')[-1]) for category_name in categories}
        return number_of_products

    #Print the current status of the scrape
    def current_status_info(self):
        max_number_products = sum(self.number_of_products_in_categories().values())
        print(f'\nTotal number of products to scrape: {max_number_products}') 
        number_products_scraped = sum(self.get_categories_with_saved_product_data().values()) 
        print(f'\nNumber of products scraped already: {number_products_scraped}')
        print(f'\nNumber of products left to scrape: {max_number_products - number_products_scraped}')
        saved = self.get_categories_with_saved_product_data()    
        print(f'\nCategories scraped already and number of products scraped: \n {sorted(saved.items(), key=lambda x: x[1], reverse=True)}')
        not_scraped = self.number_of_products_in_categories(self.get_categories_without_saved_product_data())
        print(f'\nCategories left to scrape: \n {sorted(not_scraped.items(), key=lambda x: x[1], reverse=True)}')
                                          
    # Public function to scrape the products. Pass in a list of categories as a param. If there is saved product data this will be overwritten if we scrape again for the category
    def scrape_products(self, categories="ALL", download_images=False):
        if categories == "ALL":
            categories = self.category_urls.keys()        
        for category in categories:
            if os.path.exists(self.product_data_path):            
                temp_dict = OcadoScraper._read_data(self.product_data_path) #read the data from the json dict into product_data dict attribute
                self.product_data = temp_dict
            self._scrape_product_urls(self.category_urls[category], category)
            self._scrape_product_data_for_category(category, download_images)
            self._save_data("product_data", self.product_data) #save the product_data dict into a json file after each scrape of a category, overwriting the file if it exists 
            print(f"Product data from the {category} category saved successfully")

    def scrape_product(self, url, download_images=False):
        self.driver.get(url)
        OcadoScraper._accept_cookies(self.driver)
        return OcadoScraper._scrape_product_data(self.driver, url, download_images)
    
    # Download all images for the specified LIST of categories using the stored image links in the json product data file. 
    def download_images(self, categories='ALL'):
        if categories == 'ALL':
            categories = self.category_urls.keys()
        if os.path.exists(self.product_data_path):            
            products = OcadoScraper._read_data(self.product_data_path) 
        else:
            print('No stored product data')
            return
        for category in categories:
            if category in products.keys():
                for key, value in products[category].items():
                    image_src_list = products[category][key]['Image links']
                    image_list = Product_Images(key, image_src_list)
                    image_list.download_all_images()
            else:
                print(f'No stored data for {category} category')
 
####################################################################### 
# Other functions 
    def zoom_page(self, zoom_percentage=100):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")
#######################################################################

if __name__ == '__main__':
    pass
    # ocado = OcadoScraper() 
    # ocado.scrape_products()



# ocado = OcadoScraper(True)
# categories_to_scrape = ['Fresh & Chilled Food']
# ocado.scrape_products(categories_to_scrape)
#%%
# ocado = OcadoScraper()
# url = 'https://www.ocado.com/products/hovis-best-of-both-medium-sliced-22616011'
# data = ocado.scrape_product(url, True)
# pprint(data)
#%%
ocado = OcadoScraper()
ocado.categories_available_to_scrape()
#%%
ocado.get_categories_without_saved_product_data()
#%%
ocado = OcadoScraper()
ocado.number_of_products_in_categories()
ocado.categories_available_to_scrape()
ocado.current_status_info()
#%%
# ocado.scrape_products(ocado.get_categories_without_saved_product_data())
# ocado = OcadoScraper()
# categories_to_scrape = [Toys, Games & Books, Baby, Parent & Kids]
# ocado.scrape_products(categories_to_scrape)
# print(len(ocado.product_urls["Clothing & Accessories"]))
    #%%
# ocado = OcadoScraper()
# url = 'https://www.ocado.com/products/shatterproof-silver-multi-finish-baubles-pack-of-4-558717011'
# data = ocado.scrape_product(url, False)
# pprint(data)
#%%
# ocado = OcadoScraper()
# ocado.categories_available_to_scrape()
# ocado.get_categories_with_saved_product_data()
# ocado.get_categories_without_saved_product_data()
# ocado.scrape_products(ocado.get_categories_without_saved_product_data())

# %%
ocado = OcadoScraper()
ocado.scrape_products(['Bakery'])
ocado.download_images(['Frozen Food', 'Bakery']) #default value is ALL categories
# %%

#test multithreading for scrape product urls
# ocado = OcadoScraper()
# category1 = 'Clothing & Accessories'
# category3 = 'Food Cupboard'
# url1 = 'https://www.ocado.com/browse/clothing-accessories-148232?display=943'
# url2 = 'https://www.ocado.com/browse/christmas-317740?display=4958'
# url3 ='https://www.ocado.com/browse/food-cupboard-20424?display=13989'
# ocado._scrape_product_urls(url3, category3, threads_number=3)
#%%
#test multithreading for _scrape_product_data_for_category
# ocado = OcadoScraper()

# category1 = 'Clothing & Accessories'
# category3 = 'Food Cupboard'
# url1 = 'https://www.ocado.com/browse/clothing-accessories-148232?display=943'
# url2 = 'https://www.ocado.com/browse/christmas-317740?display=4958'
# url3 ='https://www.ocado.com/browse/food-cupboard-20424?display=13989'
# ocado._scrape_product_urls(url3, category3, threads_number=3)
# print('available',ocado.categories_available_to_scrape(),'\n')
# print('saved',ocado.get_categories_with_saved_product_data(),'\n')
# print('not saved',ocado.get_categories_without_saved_product_data(),'\n')
#%%
# ocado = OcadoScraper(scrape_categories=False)
# ocado.scrape_products(categories=["Clothing & Accessories"])




#%%

#test headless
# ocado = OcadoScraper()
# a = ocado._scrape_category_urls()
# ocado.driver.save_screenshot('screenie.png')
# print(a)
# ocado.driver.close()

#%%
# For _scrape_category_urls()
# 1. there are more than 2 items
# 2. keys are not empty strings
# 3. urls(dictionary values) end in a number


# _get_number_of_products()
# https://www.ocado.com/browse?filters=vegetarian-19996
# check that the number is bigger than 1
#%%
ocado = OcadoScraper()

# %%
# ocado.delete_saved_product_data_for_category('Fresh & Chilled Food')
# %%
ocado = OcadoScraper()
ocado.current_status_info()



# %%
ocado.delete_saved_product_data_for_category('Fresh & Chilled Food')
# %%

# %%
