#%%
### Imports:
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time

from pprint import pprint
###
#%%
### Class Template:
class OcadoScraper:
    def __init__(self):
        """
        Initialiser: to decide what functions are called here and what attributes and arguments are defined
        """
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver.get('https://www.ocado.com/')
        try:
            self._accept_cookies()
        except:
            pass
        self.category_links = {}
        self.product_links = {}
        self.product_data = {}

    def _accept_cookies(self):
        """
        Clicks Cookies button
        Locate and Click Cookies Button
        """
        _accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
        _accept_cookies.click()

    def _get_category_links(self):
        if not self.category_links: # remove this probably
            self.driver.get("https://www.ocado.com/browse")
            categories_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/div/div/div[1]/div/div[1]/div/ul/li/a')
            self.category_links = {category.text : category.get_attribute('href') for category in categories_web_object}

    def _get_product_links(self, category_name): 
        category_url = self.category_links[category_name]  
        self.driver.get(category_url)  
        number_of_products_in_category = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/div[2]/div[2]/div/span').text.split(' ')[0]
        self.driver.get(category_url + "?display=" + number_of_products_in_category)  
        urls_tmp_web_object = []
        n = int(int(number_of_products_in_category)/30) ## Scroll to get 30 product url's at a time:
        for i in range(n):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/n});")
            urls_tmp_web_object.extend(self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
            time.sleep(0.5)
        urls_web_object = list(set(urls_tmp_web_object))
        urls_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
        links = [url.get_attribute('href') for url in urls_web_object]
        self.product_links[category_name] = links

    def _get_product_data(self, category_name):
        product_details = {} 
        for i, url in enumerate(self.product_links[category_name]): ## remove enumerate - just for testing
            self.driver.get(url)
            name = self.driver.find_element(By.XPATH, self._get_product_xpaths('Name')).text
            description = self.driver.find_element(By.XPATH, self._get_product_xpaths('Description')).text
            price = self.driver.find_element(By.XPATH, self._get_product_xpaths('Price')).text
            # price_per = self.driver.find_element(By.XPATH, self._get_product_xpaths('Price per')).text # doesn't exist for all items
            rating = self.driver.find_element(By.XPATH, self._get_product_xpaths('Rating')).get_attribute('title').split(' ')[1]        
            product_details[name] = { 'Description' : description,
                                        'Price' : price,
                                        #    'Price per' : price_per,
                                        'Rating' : rating 
                                        }  
            if i == 1:  ### remove - just for testing
                break
        self.product_data[category_name] = product_details

    @staticmethod
    def _get_product_xpaths(key):
        product_xpaths = { 'Name' : '//*[@id="overview"]/section[1]/header/h2',
                           'Description' : '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div/div[1]/div',
                           'Price' : '//*[@id="overview"]/section[2]/div[1]/div/h2',
                        #  'Price per' : '//*[@id="overview"]/section[2]/div[1]/div/span', # doesn't exist for all items
                           'Rating' : '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span'    
                         } 
        return product_xpaths[key]

    def scrape_products(self, categories="ALL"):
        self._get_category_links()
        if categories == "ALL":
            categories = self.category_links.keys()
        for i, category in enumerate(categories):
            self._get_product_links(category)
            self._get_product_data(category)
            if i == 0:
                break

 
    def func2(self):
        """
        Gets Browse shop category URLs
        """
    
    def func3(self):
        """
        Gets inner category urls from each Browse shop category
        """
    
    def func4(self):
        """
        Opens URL in new tab
        """

    def func5(self):
        """
        Closes current tab (This function might be redundant)
        """

    def func6_0(self):
        """
        Gets number of items that can be displayed on page
        """

    def func6(self):
        """
        Displays all items on page
        """

    def func7(self):
        """
        Collects all the item URLs on a page
        """
    
    def func8(self):
        """
        Gets images from item page
        """
    
    def func9_0(self):
        """
        Gets price, description, SKU, reviews from item page
        """
    def func9(self):
        """
        Scrapes an item's page
        """

    def func10(self):
        """
        Creates folder in which to store data dictionaries if the folder doesn't already exist
        """
    
    def func11(self):
        """
        Saves data into dictionary
        """
    
    def func12(self):
        """
        Saves dictionary in a file
        """
    

if __name__ == '__main__':
    pass
#%%
ocado = OcadoScraper() 
ocado.scrape_products()
print(len(ocado.product_links["Christmas"]))
print(ocado.category_links)


# %%
