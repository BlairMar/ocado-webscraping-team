#%%
from threading import ThreadError
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from ThreadingClass import RecipesPageThread, ScrapeRecipesDataThread
import os
import json

class OcadoRecipesScraper:
    def __init__(self, headless=True, data_path = '../data/'):
        self.chrome_options = webdriver.ChromeOptions()
        self.headless = headless
        if self.headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument('window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        if not self.headless:
            self.driver.maximize_window()
        self.ROOT = 'https://www.ocado.com/webshop/recipeSearch.do?categories='
        self.driver.get(self.ROOT)
        WebDriverWait(self.driver, 120).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]'))).click()
        self.number_of_pages = OcadoRecipesScraper._scrape_number_of_pages(self.driver)
        self.data_path = data_path
        self.recipes_urls_path = self.data_path + 'recipes_urls'
        self.recipes_data_path = self.data_path + 'recipes_data'
        self.recipes_urls = []
        self.recipes_data = []
        
    @staticmethod
    def _scrape_number_of_pages(driver):
        """
        Scrapes the number of pages available to scrape.
        Meant to be called in the initialiser.

        Returns:
            int: number of pages available to scrape.
        """
        page_number_objects = driver.find_elements(By.XPATH, '//*[@class="paginationWrapper paginationBottom "]//li/a')
        return max([int(p_n_obj.text) for p_n_obj in page_number_objects if p_n_obj.text.isdigit()])
    
    def get_number_of_pages(self):
        """
        Get the number of pages available to scrape.

        Returns:
            int: number of pages available to scrape.
        """
        return self.number_of_pages

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
    
    def scrape_all_recipe_urls(self, threads_number=2, limit_pages=0):
        """
        Scrape recipe URLs from all the recipe pages if limit_pages=0.
        Otherwise it will scrape all the recipe URLs from the first #limit_pages pages.
        
        Args: 
            limit_pages: int (0 to scrape all the URLs, n to scrape the URL's from the first n pages)
            threads_number: int (number of threads to run the URL scraper on)
        Returns
            list: list of recipe URLs.
        """
        root = 'https://www.ocado.com/webshop/recipeSearch.do?categories=&recipeSearchIndex='
        list_of_urls = [root+str(i) for i in range(self.number_of_pages)]
        if limit_pages:
            list_of_urls = list_of_urls[0:limit_pages]
        split_urls_lists = OcadoRecipesScraper._split_list(list_of_urls, threads_number)
        thread_list = [RecipesPageThread(i, split_urls_lists[i], OcadoRecipesScraper._scrape_recipe_urls_from_page, headless=self.headless) for i in range(threads_number)]
        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list:
            self.recipes_urls.extend(thread.recipes_urls)
        self.recipes_urls = list(set(self.recipes_urls))
        return self.recipes_urls
    
    @staticmethod
    def _scrape_recipe_urls_from_page(driver):
        '''
        Scrape the recipe URLs from a page with a list of recipes.
        Meant to be passed as an argument when initialising RecipesPageThread objects.
        
        Args:
            driver: selenium.webdriver.chrome.webdriver.WebDriver
        Returns:
            list: list of recipe URLs
        '''
        recipe_urls_objcets = driver.find_elements(By.XPATH, '//*[@class="recipeListItem__link"]')
        return [web_object.get_attribute('href') for web_object in recipe_urls_objcets]
    
    @staticmethod
    def _get_xpaths():
        """
        Get a dictionary containing the xpaths for recipe attributes.
        
        Returns: 
            dict: A dictionary of xpaths for each recipe attribute.
        """
        recipes_xpaths = { 'Name' : '//*[@itemprop="name"]',
                           'Description' : '//*[@itemprop="description"]',
                           'Price' : '//*[@itemprop="description"]/span/p[2]/span',
                           'Rating' : '//*[@itemprop="ratingValue"]',
                           'Ingredients' : '//*[@itemprop="recipeIngredient"]',
                           'Image URL' : '//*[@itemprop="image"]',
                           'Time' : '//*[@itemprop="totalTime"]/span',
                           'Instructions' : '//*[@itemprop="recipeInstructions"]',
                           'Serves' : '//*[@itemprop="recipeYield"]'
                         } 
        return recipes_xpaths
    
    @staticmethod
    def _get_web_element_by_xpath_or_none(driver, attribute_name, xpath):
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
            if attribute_name in ['Ingredients', 'Times', 'Instructions']:
                return driver.find_elements(By.XPATH, xpath)
            return driver.find_element(By.XPATH, xpath)
        except:
            return None
    
    @staticmethod
    def _get_recipe_information(key, attribute_web_element):
        """
        Get data from web element.
        
        Args:
            key: selenium.webdriver.chrome.webdriver.WebDriver
            attribute_web_element: selenium.webdriver.remote.webelement.WebElement
        Return: 
            str/list: data retrieved from the web element
        """
        if key in ['Name', 'Description', 'Time', 'Serves', 'Price']:
            return attribute_web_element.text.replace("\u00e0","").replace("\u2019","")
        elif key in ['Rating']:
            return attribute_web_element.get_attribute('style').replace('width: ', '')
        elif key in ['Image URL']:
            return 'https://www.ocado.com' + attribute_web_element.get_attribute('src')
        elif key in ['Ingredients', 'Times', 'Instructions']:
            return [elem.text.replace("\u00bd","").replace("\u00bc","").replace("\u2019","").replace("\u00b0","").replace("\u2103","") for elem in attribute_web_element]
    
    def scrape_all_recipes(self, threads_number=4):
        """
        Scrape all the recipes whose URLs are stored in recipes_urls.

        Args:
            threads_number: int (number of threads to run the scraper on)
        Returns:
            dict: dictionary containing the recipes' data
        
        """
        split_urls_list = OcadoRecipesScraper._split_list(self.recipes_urls, threads_number)
        thread_list = [ScrapeRecipesDataThread(i, split_urls_list[i], OcadoRecipesScraper._scrape_recipe_data, headless=self.headless) for i in range(threads_number)]
        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list:
            self.recipes_data.extend(thread.recipes_data)
        return self.recipes_data
    
    @staticmethod
    def _scrape_recipe_data(driver, url):
        '''
        Scrape a recipe's data given a webdriver and the recipe's URL.
        Meant to be passed as an argument when initialising ScrapeRecipesDataThread objects.

        Args:
            driver: selenium.webdriver.chrome.webdriver.WebDriver
            url: str (URL of the recipe page to be scraped)
        
        Returns:
            dict: A nested dictionary of the recipe's URL, Name and Description and other data.
        '''
        driver.get(url)
        data = {'URL' : url}
        xpaths = OcadoRecipesScraper._get_xpaths()
        for key, value in xpaths.items():
            attribute_web_element = OcadoRecipesScraper._get_web_element_by_xpath_or_none(driver, key, value)
            if attribute_web_element:
                data[key] = OcadoRecipesScraper._get_recipe_information(key, attribute_web_element)
                if key == 'Name':
                    name = data[key]
            else:
                data[key] = None
                if key == 'Name':
                    name = None
        return {name : data}
    
    @staticmethod
    def _create_folder(path):
        '''
        Create a folder at path if the folder doesn't already exist.
        
        Args:
            path: str (the location where the user wants the folder)
        '''
        if not os.path.exists(path):
            os.makedirs(path)
    
    def _save_data(self, filename, data, mode='w', indent=4):
        '''
        Save data in a file named filename.

        Args:
            filename: str (the name of the file to save the data to)
            data: str/dict (data to be saved in the file)
            mode: str (the mode in which the file will be opened)
            indent: int
        '''
        OcadoRecipesScraper._create_folder(self.data_path)
        with open(self.data_path + f'{filename}', mode=mode) as f:
            json.dump(data, f, indent=indent) 
    
    def scrape(self, limit_pages=0):
        '''
        Scrape all recipes URLs and data if limit_pages=0. Otherwise scrape only first #limit_pages recipe pages.
        Store data in recipes_urls and recipes_data files.

        Args:
            limit_pages: int (0 to scrape everything, n to scrape first n pages)
        '''
        self.scrape_all_recipe_urls(limit_pages=limit_pages)
        self._save_data('recipes_urls', self.recipes_urls)
        self.scrape_all_recipes()
        self._save_data('recipes_data', self.recipes_data)

#%%
if __name__ == '__main__':
    start = datetime.now()
    recipe = OcadoRecipesScraper()
    recipe.scrape(limit_pages=5)
    print(datetime.now()-start)
