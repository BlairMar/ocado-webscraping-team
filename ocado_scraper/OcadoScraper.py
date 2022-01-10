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

# for using webdriver Docker
sys.path.append('/usr/local/bin/')

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
        self.data_path = '../data/'
        self.category_url_path = self.data_path + 'category_urls'
        self.product_data_path = self.data_path + 'product_data'
        self.chrome_options = webdriver.ChromeOptions()
        self.headless = headless
        if self.headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("window-size=1920,1080")
            self.chrome_options.add_argument("--no-sandbox") 
            self.chrome_options.add_argument("--disable-dev-shm-usage") 
            self.chrome_options.add_argument("enable-automation")
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_argument("--dns-prefetch-disable")
            self.chrome_options.add_argument("--disable-gpu")
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
                self.category_urls = OcadoScraper._read_data("../data/category_urls")
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

    def _scrape_product_urls(self, category_url, category_name, threads_number=4, limit=0):
        starting_time = datetime.now()
        number_of_products_on_page = int(category_url.split('=')[-1])
        number_of_scrolls = number_of_products_on_page/35
        threads_number = 1 if (number_of_products_on_page<1500 or limit) \
                            else 3 if number_of_products_on_page>10000 \
                            else threads_number
        scroll_points = [i/threads_number for i in range(threads_number+1)]

        thread_list = [CategoryPageThread(i, category_url, number_of_scrolls, scroll_points[i], scroll_points[i+1], \
                OcadoScraper._scroll_to_get_product_urls, headless=self.headless, limit=limit) for i in range(threads_number)]

        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        data = []
        for thread in thread_list: #bring data together 
            data.extend(thread.product_urls)
        self.product_urls[category_name] = list(set(data))
        
        print(f"It took {datetime.now()-starting_time} seconds to scrape the urls from the {category_name} category page")

    # UTILITY function for the above function to scroll the page and get all the product urls on the page
    @staticmethod
    def _scroll_to_get_product_urls(driver, number_of_scrolls, start_scrolling_at=0, stop_scrolling_at=1, limit=0):
        urls_temp_web_object = []
        for i in range(int(start_scrolling_at*number_of_scrolls), int(stop_scrolling_at*number_of_scrolls)):
            if i == int(start_scrolling_at*number_of_scrolls):
                time.sleep(0.5)
            driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/number_of_scrolls});")
            time.sleep(0.5)
            urls_temp_web_object.extend(driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
            if limit and len(list(set(urls_temp_web_object))) > limit:
                break
        urls_web_object = list(set(urls_temp_web_object))
        urls = [url.get_attribute('href') for url in urls_web_object]
        if limit:
            urls = urls[:limit]
        return urls
    
##############################################################################################################################
# This function is called by the PUBLIC function scrape_products() and scrapes the information and images for 
# all products in the category and puts them in the product_data dictionary 

    def _scrape_product_data_for_category(self, category_name, download_images, threads_number=4, rewrite=False):
        starting_time = datetime.now()
        product_details = {}
        split_urls_lists = OcadoScraper._split_list(self.product_urls[category_name], threads_number)
        thread_list = [ScrapingProductsThread(i, split_urls_lists[i], \
                OcadoScraper._scrape_product_data, download_images, headless=self.headless) for i in range(len(split_urls_lists))]

        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list: #bring the data together
            product_details.update(thread.product_details)
        if rewrite:
            self.product_data[category_name] = product_details
        else:
            self.product_data[category_name].update(product_details)
        print(f"It took {datetime.now()-starting_time} seconds to scrape the products in the {category_name} category")
    
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
            
    @staticmethod
    def _delete_file(path):
        if os.path.exists(path):
            os.remove(path)
        else: 
            print("No stored file")
                        
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
     
    # Gets a list of categories that do not have saved product data. This list can be passed as a parameter to the scrape_products() function to scrape remaining categories                
    # !! check this works if all products have been scraped 
    def get_categories_without_saved_product_data(self):
        all_categories = self.category_urls.keys()
        if os.path.exists(self.product_data_path):
            stored_data = self.get_categories_with_saved_product_data().keys()
            return list(set(all_categories).difference(set(stored_data)))
        else:
            return list(all_categories)
    
    # Beware! - deletes the product_data saved json file if it exists.                     
    def delete_saved_product_data(self):
        self._delete_file(self.product_data_path)
    
    def delete_saved_category_url_data(self):
        self._delete_file(self.category_url_path)
            
    # Delete the saved product data for the specified category name. 
    # Used for example if a scrape of a category has gone wrong and not all the products have been scraped for that category.                     
    def delete_saved_product_data_for_category(self, category_name):
        if os.path.exists(self.product_data_path):            
            product_data = OcadoScraper._read_data(self.product_data_path) 
            if category_name in product_data.keys():
                product_data.pop(category_name)
                self._save_data("product_data", product_data) 
            else:
                print('No stored data for that category')
        else:
            print("No stored data file")
            
    # Beware! - deletes the folder storing all the images.  
    @staticmethod                    
    def delete_downloaded_images():
        path = '../data/images/'
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
        return 0
    
    # returns a dictionary of the number of products in the categories on the ocado website            
    def number_of_products_in_categories(self, categories='ALL'):
        if categories == 'ALL':
            categories = self.category_urls.keys()
        number_of_products = {category_name : int(self.category_urls[category_name].split('=')[-1]) for category_name in categories}
        return number_of_products

    #Print the current status of the scrape
    def current_status_info(self):
        max_number_products = sum(self.number_of_products_in_categories().values())
        print(f'\nTotal number of products to scrape: {max_number_products}') 
        number_products_scraped = sum(self.get_categories_with_saved_product_data().values()) if os.path.exists(self.product_data_path) else 0
        print(f'\nNumber of products scraped already: {number_products_scraped}')
        not_scraped = self.number_of_products_in_categories(self.get_categories_without_saved_product_data())
        number_products_not_scraped = sum(not_scraped.values()) if not_scraped else 0
        print(f'\nNumber of products left to scrape: {number_products_not_scraped}')
        if os.path.exists(self.product_data_path):
            saved = self.get_categories_with_saved_product_data()    
            print(f'\nCategories scraped already and number of products scraped: \n {sorted(saved.items(), key=lambda x: x[1], reverse=True)}')
        print(f'\nCategories left to scrape: \n {sorted(not_scraped.items(), key=lambda x: x[1], reverse=True)}')
        return True
                                          
    # Public function to scrape the products. Pass in a list of categories as a param. If there is saved product data this will be overwritten if we scrape again for the category

    def scrape_products(self, categories="ALL", download_images=False, limit=0, threads_number=4, rewrite=False):
        if categories == "ALL":
            categories = self.category_urls.keys()        
        for category in categories:
            if os.path.exists(self.product_data_path):            
                temp_dict = OcadoScraper._read_data(self.product_data_path) #read the data from the json dict into product_data dict attribute
                self.product_data = temp_dict
            self._scrape_product_urls(self.category_urls[category], category, limit=limit)
            self._scrape_product_data_for_category(category, download_images=download_images, threads_number=threads_number, rewrite=rewrite)

            self._save_data("product_data", self.product_data) #save the product_data dict into a json file after each scrape of a category, overwriting the file if it exists 
            print(f"Product data from the {category} category saved successfully")
    
    # Displays what information is scraped from a sample product page - this data is not saved
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


# %%
