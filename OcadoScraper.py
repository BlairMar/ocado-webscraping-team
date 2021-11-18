#%%
### Imports:
from types import DynamicClassAttribute
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
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
        OcadoScraper._save_data("category_urls", self.category_urls)

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

    def _scrape_product_urls(self, category_url, category_name, threads_number=4):
        s = datetime.now()
        number_of_products_on_page = int(category_url.split('=')[-1])
        if number_of_products_on_page < 1500: #if pages are too small only use one thread
            threads_number = 1
        if threads_number == 4 and number_of_products_on_page > 10000: #if pages are too big reduces number of threads from 4 to 3
            threads_number = 3
        number_of_scrolls = number_of_products_on_page/35
        if threads_number-1: #if more than one thread is beign used
            scroll_points = []
            for i in range(threads_number+1): #compute scrolling boundaries
                scroll_points.append(i/threads_number)
            thread_list = []
            for i in range(len(scroll_points)-1): #add threads to a list
                thread_list.append(CategoryPageThread(i, category_url, number_of_scrolls, scroll_points[i], scroll_points[i+1], OcadoScraper._scroll_to_get_product_urls))
            for thread in thread_list:
                thread.start() #start scrolling and scraping in each thread's browser
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
        split_urls_lists = OcadoScraper.split_list(self.product_urls[category_name], 4)
        thread_list = []
        for i in range(len(split_urls_lists)): #add threads to a list
            thread_list.append(ScrapingProductsThread(i, split_urls_lists[i], OcadoScraper._scrape_product_data, download_images))
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
        if download_images:
            product.download_images()
        return product.scrape_product_data(driver)
                    
##################################################################################################################  
    # function to read data from a json file
    @staticmethod
    def _read_data(path):
        with open(path) as f:
            data = f.read()
            return json.loads(data) 
  
    # function to dump the data to a json file. Used to save the category_urls, product_links and product_data dictionarys to file
    @staticmethod
    def _save_data(filename, data, mode='w', indent=4):
        path = './data/'
        OcadoScraper._create_folder(path)
        with open(path + f'{filename}', mode=mode) as f:
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
        path = "./data/category_urls"
        if from_file == True:
            if os.path.exists(path):
                temp_dict = OcadoScraper._read_data(path)
                return list(temp_dict.keys())
            else: 
                print("Error: No stored data for category urls, re-run this function with from_file=False")
                return                 
        else:
            self._get_categories(True)
            return list(self.category_urls.keys())
     
    @staticmethod           
    def get_categories_with_saved_product_data():
        path = "./data/product_data"
        if os.path.exists(path):
            temp_dict = OcadoScraper._read_data(path)
            return list(temp_dict.keys())
        else:
            print('No categories with saved product data')
            return
                    
    def get_categories_without_saved_product_data(self):
        all_categories = {}
        path = "./data/category_urls"
        if os.path.exists(path):
            all_categories = OcadoScraper._read_data(path).keys()
        else: 
            self._scrape_category_urls()
            all_categories = self.category_urls.keys()
        stored_data = OcadoScraper.get_categories_with_saved_product_data()
        if stored_data:
            return list(set(all_categories).difference(set(stored_data)))
        else:
            return list(all_categories)
                        
    @staticmethod
    def delete_saved_product_data():
        path = "./data/product_data"
        if os.path.exists(path):
            os.remove(path)
        else: 
            print("Can not delete the file as it doesn't exist")
    
    @staticmethod
    def number_of_products_saved_from_category(category_name):
        path = "./data/product_data"
        if os.path.exists(path):
            temp_dict = OcadoScraper._read_data(path)
            if category_name in temp_dict.keys():
                return len(temp_dict[category_name])
        print("No products saved for this category")
                               
    # public function to scrape the products. Pass in a list of categories as a param. If there is saved product data this will be overwritten if we scrape again for the category
    def scrape_products(self, categories="ALL", download_images=False):
        if categories == "ALL":
            categories = self.category_urls.keys()        
        for category in categories:
            path = "./data/product_data"
            if os.path.exists(path):            
                temp_dict = OcadoScraper._read_data(path) #read the data from the json dict into product_data dict attribute
                self.product_data = temp_dict
            self._scrape_product_urls(self.category_urls[category], category)
            self._scrape_product_data_for_category(category, download_images)
            OcadoScraper._save_data("product_data", self.product_data) #save the product_data dict into a json file after each scrape of a category, overwriting the file if it exists 
            print(f"Product data from the {category} category saved successfully")

    def scrape_product(self, url, download_images=False):
        self.driver.get(url)
        OcadoScraper._accept_cookies(self.driver)
        return OcadoScraper._scrape_product_data(self.driver, url, download_images)

        
####################################################################### 
# Other functions
    @staticmethod
    def split_list(lst, n):
        divided_list = []
        for i in range(n):
            divided_list.append(lst[i::n])
        return divided_list

    def zoom_page(self, zoom_percentage=100):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")
#######################################################################

if __name__ == '__main__':
    pass
    # ocado = OcadoScraper() 
    # ocado.scrape_products()

#%%
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

#%% 
# saved_categories = ocado.get_categories_with_saved_product_data()
# for category in saved_categories:
#     print(f"{category} : {ocado.number_of_products_saved(category)}")

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
ocado = OcadoScraper()
print('available',ocado.categories_available_to_scrape(),'\n')
print('saved',ocado.get_categories_with_saved_product_data(),'\n')
print('not saved',ocado.get_categories_without_saved_product_data(),'\n')
#%%
# ocado = OcadoScraper(scrape_categories=False)
# ocado.scrape_products(categories=['Baby, Parent & Kids'])


#%%
