#%%
### Imports:
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
from pprint import pprint
###
#%%
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
        self.product_links = {}
        self.product_data = {}
        self._get_categories(scrape_categories) # populate category_links attribute

    def _accept_cookies(self):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            _accept_cookies.click()
        except:
            print("No Cookies buttons found on page")

    def _get_categories(self, scrape_categories=True):
        if scrape_categories:
            self._scrape_category_urls()
        else:
            with open("./data/category_urls") as f:
                data = f.read()
                self.category_urls = json.loads(data)

    def _scrape_category_urls(self):
        self.driver.get(self.ROOT + "browse")
        self._accept_cookies()
        categories_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/div/div/div[1]/div/div[1]/div/ul/li/a')
        self.category_urls = {category.text : category.get_attribute('href').replace("?hideOOS=true", "") for category in categories_web_object}
        for category_name, category_url in self.category_urls.items():
            number_of_products = self._get_number_of_products(category_url)
            self.category_urls[category_name] += '?display=' + number_of_products
        self.save_category_urls()

    def _get_product_links(self, category_name):
        number_of_products_in_category = self.category_urls[category_name].split('=')[-1]
        self.driver.get(self.category_urls[category_name])
        self.product_links[category_name] = self._scroll_to_get_all_product_links(number_of_products_in_category, 30)

    def _get_number_of_products(self, category_url):
        self.driver.get(category_url)
        number_of_products = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]//div/div[2]/div/span').text.split(' ')[0]
        return number_of_products

    def _scroll_to_get_all_product_links(self, number_of_products, number_of_items_in_each_scroll):
        urls_tmp_web_object = []
        n = int(int(number_of_products)/number_of_items_in_each_scroll)
        for i in range(n):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/n});")
            urls_tmp_web_object.extend(self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
            time.sleep(0.5)
        urls_web_object = list(set(urls_tmp_web_object))
        urls_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
        links = [url.get_attribute('href') for url in urls_web_object]
        return links

    def _get_product_data(self, category_name):
        product_details = {} 
        for i, url in enumerate(self.product_links[category_name]): ## remove enumerate 
            self.driver.get(url)
            product_attributes = {}
            for key, value in OcadoScraper._get_attribute_xpaths().items():
                attribute_web_element = self._get_attribute_by_xpath_or_none(key, value)
                if attribute_web_element:
                    if key in ['Name', 'Product Information', 'Price', 'Price per', 'Offers', 'Ingredients', 'Nutrition']:
                        product_attributes[key] = attribute_web_element.text
                    if key in ['Usage', 'Brand details']:
                        product_attributes[key] = self._scrape_hidden_attributes(value)
                    if key == 'Rating':
                        product_attributes[key] = attribute_web_element.get_attribute('title').split(' ')[1]
                    if key == 'Out of Stock':
                       product_attributes[key] = True  
                else:
                    product_attributes[key] = False if key == 'Out of Stock' else None                                                              
            product_details[OcadoScraper._get_sku_from_url(url)] = product_attributes
            # if i == 10:  ### get the first i products - just for testing
            #     break
        self.product_data[category_name] = product_details

    def _scrape_hidden_attributes(self, xpath):
        hidden_html_elements = self.driver.find_elements(By.XPATH, xpath)
        text_in_hidden_elements = [element.get_attribute('textContent') for element in hidden_html_elements]
        return (' '.join(str(text) for text in text_in_hidden_elements))        

    def _get_attribute_by_xpath_or_none(self, attribute_name, xpath):
        """
        Get a web element of the product attribute xpath.

        params : 
                attribute_name: name of the product attribute
                xpath: xpath of the product attribute, eg xpath of the product name, price, description etc
        return: 
                The web element or None if nothing found.
        """
        try:
            if attribute_name in ['Usage', 'Brand details']:
                return self.driver.find_elements(By.XPATH, xpath)
            return self.driver.find_element(By.XPATH, xpath)
        except:
            return None

    @staticmethod
    def _get_attribute_xpaths():
        """
        Gets a dictionary containing the xpath for a product attribute.

        return: 
                A dictionary of xpaths for each product attribute

        """
        product_xpaths = { 'Name' : '//*[@id="overview"]/section[1]/header/h2',
                           'Product Information' : '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div',
                           'Price' : '//*[@id="overview"]/section[2]/div[1]/div/h2',
                           'Price per' : '//*[@id="overview"]/section[2]/div[1]/div/span[2]',
                           'Offers' : '//*[@id="overview"]/section[2]/div[2]/div/a/p',
                           'Rating' : '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span',
                           'Ingredients' : '//*[@id="productInformation"]/div[3]/div/div[2]/div[2]/div/div[1]/div',
                           'Usage' : '/html/body/div[1]/div[1]/div[3]/article/section[5]/div[2]/div[2]/div[2]//div/div',
                           'Nutrition' : '//*[@id="productInformation"]/div[3]/div/div/div[2]/div/div/div/div/table/tbody',
                           'Brand details' : '//html/body/div[1]/div[1]/div[3]/article/section[5]/div[2]/div[3]/div[2]//div/div',
                           'Out of Stock' : '//*[@id="overview"]/section[2]/div[2]/h1'   
                         } 
        return product_xpaths
    
    @staticmethod
    def _get_sku_from_url(url):
        return url.split("-")[-1]

    def scrape_products(self, categories="ALL"):
        if categories == "ALL":
            categories = self.category_links.keys()        
        for i, category in enumerate(categories):
            self._get_product_links(category)
            self._get_product_data(category)
            if i == 3:
                break
        self.save_product_links()

    def save_product_links(self, mode='a'):
        with open('./data/product_links', mode=mode) as f:
            json.dump(self.product_links, f)
    
    def save_category_urls(self, mode='w'):
        with open('./data/category_urls', mode=mode) as f:
            json.dump(self.category_urls, f)
        
    def zoom_page(self, zoom_percentage=100):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")

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

    ocado = OcadoScraper()


    pass
    # ocado = OcadoScraper() 
    # ocado.scrape_products()

#%%
ocado = OcadoScraper()
categories_to_scrape = ["Bakery"]
ocado.scrape_products(categories_to_scrape)
print(len(ocado.product_links["Bakery"]))
#%%
ocado._get_product_links("Health, Beauty & Personal Care")  
#%%
ocado = OcadoScraper()
categories_to_scrape = ["Baby, Parent & Kids"]
ocado.scrape_products(categories_to_scrape)
print(len(ocado.product_links["Baby, Parent & Kids"]))



# %%
