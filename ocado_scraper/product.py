#%%
import inspect
import sys
import os
from selenium.webdriver.common.by import By

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from images import Product_Images

#%%
class Product:
    def __init__(self, url):
        self.url = url
        self.sku = self._get_sku_from_url()
        self.product_information = {'URL' : url} # a dictionary to store all the information we scrape from the product page
        self.image_list = Product_Images(self.sku)
        
    def _get_sku_from_url(self):
        '''
        Return sku obtained from the url.
        
        Returns:
            str: sku
        '''
        return self.url.split("-")[-1] 
 
    @staticmethod
    def _get_xpaths():
        """
        Get a dictionary containing the xpaths for recipe attributes.
        
        Returns: 
            dict: A dictionary of xpaths for each recipe attribute.
        """
        product_xpaths = { 'Name' : '//*[@id="overview"]/section[1]/header/h2',
                           'Description' : '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div',
                           'Price' : '//*[@id="overview"]/section[2]/div[1]/div/h2',
                           'Price per' : '//*[@id="overview"]/section[2]/div[1]/div/span',
                           'Offers' : '//*[@id="overview"]/section[2]/div[2]/div/a/p',
                           'Rating' : '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span',
                           'Ingredients' : '//*[@id="productInformation"]/div[3]/div/div[2]/div[2]/div/div[1]/div',
                           'Usage' : '/html/body/div[1]/div[1]/div[3]/article/section[5]/div[2]/div[2]/div[2]//div/div',
                           'Nutrition' : '//*[@id="productInformation"]/div[3]/div/div/div[2]/div/div/div/div/table/tbody',
                           'Brand details' : '//html/body/div[1]/div[1]/div[3]/article/section/div[2]/div[3]/div[2]//div/div',
                           'Out of Stock' : '//*[@id="overview"]/section[2]/div[2]/h1',
                           'Image links' : '//*[@class="bop-gallery__miniatures"]//img | /html/body/div[1]/div[1]/div[3]/article/section[1]/div/div/div[1]/img',
                           'Categories' : '//html/body/div[1]/div[1]/div[3]/article/section/div[2]/ul/li//a'   
                         } 
        return product_xpaths        
                                                                              
    def _get_web_element_by_xpath_or_none(self, driver, attribute_name, xpath):
        """
        Search for web element by xpath. Return web element if found, otherwise return None.
        
        Args:
            driver: selenium.webdriver.chrome.webdriver.WebDriver
            attribute_name: str
            xpath: str
        Return: 
            dict/None: A dictionary of xpaths for each recipe attribute/None
        """
        try:
            if attribute_name in ['Usage', 'Brand details', 'Image links', 'Categories']:
                return driver.find_elements(By.XPATH, xpath)
            return driver.find_element(By.XPATH, xpath)
        except:
            return None     

    # scrape all the information and images of the product 
    def _get_product_information(self, key, attribute_web_element):
        """
        Get data from web element.
        
        Args:
            key: selenium.webdriver.chrome.webdriver.WebDriver
            attribute_web_element: selenium.webdriver.remote.webelement.WebElement
        Return: 
            str/list: data retrieved from the web element
        """
        if key in ['Name', 'Description', 'Price', 'Price per', 'Offers', 'Ingredients', 'Nutrition']:
            return attribute_web_element.text
        if key in ['Usage', 'Brand details']:
            return Product._scrape_hidden_information(attribute_web_element)
        if key == 'Rating':
            return attribute_web_element.get_attribute('title').split(' ')[1]
        if key == 'Out of Stock':
            return True 
        if key == 'Image links':
            return self.image_list.scrape_images(attribute_web_element)
        if key == 'Categories':
            return Product._scrape_category_info(attribute_web_element)
                 
    @staticmethod
    def _scrape_hidden_information(web_elements):
        '''
        Get hidden information from web elements.

        Args:
            list of selenium.webdriver.remote.webelement.WebElement
        Returns:
            list: list of str
        '''
        text_in_hidden_elements = [element.get_attribute('textContent') for element in web_elements]
        return (' '.join(str(text) for text in text_in_hidden_elements))     
    
    @staticmethod
    def _scrape_category_info(web_elements):
        '''
        Get information from web elements.

        Args:
            list of selenium.webdriver.remote.webelement.WebElement
        Returns:
            list: list of str
        '''
        return [element.get_attribute('textContent') for element in web_elements]
    
 ##############################################################################
 # PUBLIC functions
    
    # returns the sku (unique product ID) of a product
    def get_sku(self):
        '''
        Return the sku (unique product ID) of a product
        
        Returns:
            str: str (sku (unique product ID))
        '''
        return self.sku
    
    # returns a dictionary of product information eg {Name: , Price :  ,Description : , ...., Image links : ... }            
    def scrape_product_data(self, driver, download_images, data_path='../data/'):
        '''
        Return a dictionary of product information 
        eg {Name: , Price :  ,Description : , ...., Image links : ... }.

        Args:
            driver: selenium.webdriver.chrome.webdriver.WebDriver
            download_images: bool (if True download images, otherwise images are not downloaded)
            data_path: str (path to the data folder)
        Returns:
            dict: dictionary of product information.
        '''
        driver.get(self.url)
        for key, value in Product._get_xpaths().items():
            attribute_web_element = self._get_web_element_by_xpath_or_none(driver, key, value)
            if attribute_web_element:
                self.product_information[key] = self._get_product_information(key, attribute_web_element)
            else:
                self.product_information[key] = False if key == 'Out of Stock' else None
        if download_images: 
            self.download_images(data_path)
        return self.product_information 

    # downloads all the product images. Note: The function above must be called first to get the image list
    def download_images(self, data_path='../data/'):
        '''
        Download all the product images.

        Args:
            data_path: str (path to data folder
        Returns:
            str: path to where the images have been saved
        '''
        return self.image_list.download_all_images(data_path)             
                

# %%

