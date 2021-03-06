#%%
### Imports:
from types import DynamicClassAttribute
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import json
import os
import shutil
from pprint import pprint
from ThreadingClass import CategoryPageThread
from ThreadingClass import ScrapingProductsThread
from OcadoRecipesScraper import OcadoRecipesScraper
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
    def __init__(self, scrape_categories=True, headless=True, data_path='../data/'):
        self.ROOT = 'https://www.ocado.com/'
        self.data_path = data_path
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
        Wait for up 120 seconds to locate cookies button and click it if found.
        """
        try:
            WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]'))).click()
            # _accept_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            # _accept_cookies.click()
            print("Cookies button clicked")
        except:
            print("No Cookies buttons found on page")

############################################################################################
# The following 3 functions are used to populate category_urls in the initialiser

    # only used in the initialiser to get all the category urls (from a file if the file exists and scrape_categories=False)
    def _get_categories(self, scrape_categories=True):
        '''
        If scrape_categories=True call _scrape_category_urls to scrape category URLs.
        Otherwise load them from file.
        Meant to be called in the initialiser.

        Args:
            scrape_categories: bool
        '''
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
        '''
        Scrape category URLs from ocado browsing page. Edit the URLs to display all products available for each category.
        
        Returns:
            dict: dictionary containg the category URLs
        '''
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
        '''
        Scrape the number of products in a category from the category's page.

        Args:
            category_url: str (URL of the category)
            close_window: bool
        Returns:
            str: number of products in category in string format
        ''' 
        self.driver.get(category_url)
        number_of_products = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]//div/div[2]/div/span').text.split(' ')[0]
        if close_window:
            self.driver.close()
        return number_of_products
    
###########################################################################################################################
    #The following 2 functions are used to populate the product urls dictionary for the specified category
    
    # This function is called by the PUBLIC function scrape_products() and populates the product_urls dictionary for the specified category

    def _scrape_product_urls(self, category_url, category_name, threads_number=4, limit=0):
        '''
        Scrape all the URLs of all the products in a given category.
        If limit is set to a different number than 0, the function will stop scrolling after the number of
        product URLs that have been collected is higher than #limit.

        Args:
            category_url: str (URL of the category)
            category_name: str (name of the category)
            threads_number: int (how many threads to use)
            limit: int
        '''
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
        return self.product_urls[category_name]

    # UTILITY function for the above function to scroll the page and get all the product urls on the page
    @staticmethod
    def _scroll_to_get_product_urls(driver, number_of_scrolls, start_scrolling_at=0, stop_scrolling_at=1, limit=0):
        '''
        Scroll through a product category page between two points and scrape the product URLs inbetween.
        If limit is set to a different number than 0, the function will stop scrolling after the number of
        product URLs that have been collected is higher than #limit.
        Meant to be passed as an argument when initialising CategoryPageThread objects.

        Args:
            driver: selenium.webdriver.chrome.webdriver.WebDriver
            number_of_scrolls: int (how many times to scroll)
            start_scrolling_at: int (fraction of the page's height at which to start scrolling)
            stop_scrolling_at: int (fraction of the page's height at which to stop scrolling)
            limit: int
        Returns:
            list: list of product URLs
        '''
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
        '''
        Scrape data for all the product in a given category.
        
        Args:
            category_name: str (the name of the category to scrape)
            download_images: bool (if True, downloads the images of the product; otherwise it does not download the images)
            threads_number: int (number of threads to use)
            rewrite: bool (if False update existing data; otherwise rewrite existing files)
        Returns:
            dict: dictionary contains the data of the products in the given category
        '''
        starting_time = datetime.now()
        product_details = {}
        split_urls_lists = OcadoScraper._split_list(self.product_urls[category_name], threads_number)
        thread_list = [ScrapingProductsThread(i, split_urls_lists[i], \
                OcadoScraper._scrape_product_data, download_images, headless=self.headless, data_path=self.data_path) for i in range(len(split_urls_lists))]

        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list: #bring the data together
            product_details.update(thread.product_details)
        if category_name not in self.product_data:
            self.product_data[category_name] = {}
        if rewrite:
            self.product_data[category_name] = product_details
        else:
            if category_name not in self.product_data:
                self.product_data[category_name] = {}
            self.product_data[category_name].update(product_details)
        print(f"It took {datetime.now()-starting_time} seconds to scrape the products in the {category_name} category")
        return self.product_data[category_name]
    
    @staticmethod
    def _scrape_product_data(driver, url, download_images, data_path='../data/'):
        '''
        Scrape a product's data from its page.
        Meant to be passed as an argument when initialising ScrapingProductsThread objects.

        Args:
            url: str (the URL of the product to scrape)
            download_images: bool (if True, downloads the images of the product; otherwise it does not download the images)
            data_path: str (path to where the data should be stored)
        
        Returns:
            dict: dictionary of all the product information.
        '''
        product = Product(url)
        return product.scrape_product_data(driver, download_images, data_path=data_path)
    
    @staticmethod
    def _split_list(lst, n):
        """
        Splits a list into n lists of similiar size.

        Args:
            lst: list
            n: int 
        Returns:
            list: list of lists
        """
        divided_list = []
        for i in range(n):
            divided_list.append(lst[i::n])
        return divided_list
                    
##################################################################################################################  

    # Function to read data from a json file
    @staticmethod
    def _read_data(path):
        '''
        Read data from a json file.

        Args:
            path: str
        Returns:
            dict/list: data from file
        '''
        with open(path) as f:
            data = f.read()
            return json.loads(data) 

    # Function to dump the data to a json file. Used to save the category_urls, product_links and product_data dictionarys to file
    def _save_data(self, filename, data, mode='w', indent=4):
        '''
        Save data in a file named filename.

        Args:
            filename: str (the name of the file to save the data to)
            data: str/dict (data to be saved in the file)
            mode: str (the mode in which the file will be opened)
            indent: int
        '''
        OcadoScraper._create_folder(self.data_path)
        with open(self.data_path + f'{filename}', mode=mode) as f:
            json.dump(data, f, indent=indent) 
            
    @staticmethod
    def _create_folder(path):
        '''
        Create a folder at path if the folder doesn't already exist.
        
        Args:
            path: str (the location where the user wants the folder)
        '''
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def _delete_file(path):
        '''
        Delete file at path if the file exists.
        
        Args:
            path: str (the location where to look for the file)
        '''
        if os.path.exists(path):
            os.remove(path)
        else: 
            print("No stored file")
                        
###################################################################################################################
    # PUBLIC FUNCTIONS
    
    # returns a list of categories available to scrape on the ocado website
    # if from_file=True returns a list of saved categories from a previous scrape else gets the categories from the website
    def categories_available_to_scrape(self, from_file=True):
        '''
        Return a list of the categories available to scrape on the ocado website.
        The list is scraped from the website if from_file=False, otherwise it is looked for in stored data.

        Args:
            from_file: bool
        
        Returns:
            list: a list of the categories that can be scraped.
        '''
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
        '''
        Return a dictionary showing which categories have scraped data saved in the product_data json file.
        Also show how many items from that category have been scraped.
        
        Returns:
            dict: dictionary of the categories with saved data.
        '''
        if os.path.exists(self.product_data_path):
            temp_dict = OcadoScraper._read_data(self.product_data_path)
            return {category : int(self.number_of_products_saved_from_category(category)) for category in temp_dict.keys()}
        else:
            print('No categories with saved product data')
     
    # Gets a list of categories that do not have saved product data. This list can be passed as a parameter to the scrape_products() function to scrape remaining categories                
    def get_categories_without_saved_product_data(self):
        '''
        Return a list of categories that do not have saved product data. 
        This list can be passed as a parameter to the scrape_products() function to scrape remaining categories.

        Returns:
            dict: dictionary of the categories without saved data.
        '''
        all_categories = self.category_urls.keys()
        if os.path.exists(self.product_data_path):
            stored_data = self.get_categories_with_saved_product_data().keys()
            return list(set(all_categories).difference(set(stored_data)))
        else:
            return list(all_categories)
    
    # Beware! - deletes the product_data saved json file if it exists.                     
    def delete_saved_product_data(self):
        '''
        Delete the product_data saved json if it exists.
        '''
        if os.path.exists(self.product_data_path):
            os.remove(self.product_data_path)
        else: 
            print("No stored data file")
        self._delete_file(self.product_data_path)
    
    def delete_saved_category_url_data(self):
        '''
        Delete the category_url saved json if it exists.
        '''
        self._delete_file(self.category_url_path)

            
    # Delete the saved product data for the specified category name. 
    # Used for example if a scrape of a category has gone wrong and not all the products have been scraped for that category.                     
    def delete_saved_product_data_for_category(self, category_name):
        '''
        Delete the saved product data for the specified category name.

        Args:
            category_name: str (name of the category to be deleted)
        '''
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
    def delete_downloaded_images(data_path='../data/'):
        '''
        Delete the folder storing all the images.
        Args:
            data_path: str (path to where the images folder can be located)
        '''
        path = data_path + 'images/'
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s : %s" % (path, e.strerror))                    
            
    # Get the number of products saved to the product_data json file for the specified category name.
    def number_of_products_saved_from_category(self, category_name):
        '''
        Return the number of products saved to the product_data json file for the specified category name.
        
        Args:
            category_name: str (name of the category for which to get the number of products saved)
        Returns:
            int: number of products saved for the given category
        '''
        if os.path.exists(self.product_data_path):
            temp_dict = OcadoScraper._read_data(self.product_data_path)
            if category_name in temp_dict.keys():
                return len(temp_dict[category_name])
        print("No products saved for this category")
        return 0
    
    # The number of products in the categories on the ocado website            
    def number_of_products_in_categories(self, categories='ALL'):
        '''
        Return upper bound on the number of products in the categories on the ocado website.
        
        Args:
            categories: 'ALL'/list of str (the categories for which to get the number of products)
        Returns:
            dict: dictionary with upper bound on the number of products in the categories on the ocado website
        '''
        if categories == 'ALL':
            categories = self.category_urls.keys()
        number_of_products = {category_name : int(self.category_urls[category_name].split('=')[-1]) for category_name in categories}
        return number_of_products

    #Print the current status of the scrape
    def current_status_info(self):
        '''
        Print useful information about what has been scraped and what hasn't

        Returns:
            bool : True
        '''
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
        '''
        Scrape product URLs and data for all the products on the website if categories="ALL".
        If categories is a list of category names, scrape product URLs and data for the products in those categories.
        
        Args:
            categories: 'ALL'/ list (categories whose products' data to scrape)
            download_images: bool (if True, download the images of the products; otherwise images are not downloaded)
            limit: int (if different than 0 limit the number of products to be scraped to #limit)
            thread_number: int (number of threads to use)
            rewrite: bool (if True scraped data overwrites existing files, otherwise update existing files)
        '''
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
        '''
        Scrape a single product given its URL.

        Args:
            url: str (URL of the product to scrape)
            download_images: bool (if False, images will not be downloaded)
        
        Returns:
            dict: dictionary containing information about to product
        '''
        self.driver.get(url)
        OcadoScraper._accept_cookies(self.driver)
        return OcadoScraper._scrape_product_data(self.driver, url, download_images, data_path=self.data_path)
    
    # Download all images for the specified LIST of categories using the stored image links in the json product data file. 
    def download_images(self, categories='ALL'):
        '''
        Downloads all images on the website if categories="ALL".
        If categories is a list of category names, download all the images of the products in those categories.

        Args:
            categories: bool (the list of categories from which to download the images)
        '''
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
                    image_list.download_all_images(data_path=self.data_path)
            else:
                print(f'No stored data for {category} category')
    
    def scrape(self, categories="ALL", download_images=False, limit=0, threads_number=4, rewrite=False, recipes=False):
        '''
        Scrape product URLs and data for all the products on the website if categories="ALL".
        If categories is a list of category names, scrape product URLs and data for the products in those categories.
        If recipes=True also scrape all the recipes on the website.

        Args:
            categories: 'ALL'/ list (categories whose products' data to scrape)
            download_images: bool (if True, download the images of the products; otherwise images are not downloaded)
            limit: int (if different than 0 limit the number of products to be scraped to #limit)
            thread_number: int (number of threads to use)
            rewrite: bool (if True scraped data overwrites existing files, otherwise update existing files)
            recipes: bool (if True also scrape all recipes on the website)
        '''
        self.scrape_products(categories="ALL", download_images=False, limit=0, threads_number=4, rewrite=False)
        try:
            if recipes:
                recipe_scraper = OcadoRecipesScraper()
                recipe_scraper.scrape()
        except:
            print("Recipies could not be scraped")


#%%
if __name__ == '__main__':
    ocado = OcadoScraper()
    ocado.scrape(categories=["Bakery"], limit=200, recipes=False)
