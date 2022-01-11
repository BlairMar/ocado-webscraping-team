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
    def __init__(self, headless=True):
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
        self.number_of_pages = OcadoRecipesScraper.get_number_of_pages(self.driver)
        # self.driver.close()
        self.data_path = '../data/'
        self.recipes_urls_path = self.data_path + 'recipes_urls'
        self.recipes_data_path = self.data_path + 'recipes_data'
        self.recipes_urls = []
        self.recipes_data = []
        
    @staticmethod
    def get_number_of_pages(driver):
        """
        Gets the number of pages available to scrape.

        Returns:
            int: number of pages available to scrape.
        """

        page_number_objects = driver.find_elements(By.XPATH, '//*[@class="paginationWrapper paginationBottom "]//li/a')
        return max([int(p_n_obj.text) for p_n_obj in page_number_objects if p_n_obj.text.isdigit()])
    
    @staticmethod
    def _split_list(lst, n):
        divided_list = []
        for i in range(n):
            divided_list.append(lst[i::n])
        return divided_list
    
    def scrape_all_recipe_urls(self, threads_number=2, limit_pages=0):
        """
        This function scrapes all URLs of the products.
        
        Args: 
            limit_pages: Allows user to choose how many pages to scrape.
            threads_number:
        Returns
            list: URLs scraped.
        """
        root = 'https://www.ocado.com/webshop/recipeSearch.do?categories=&recipeSearchIndex='
        list_of_urls = [root+str(i) for i in range(self.number_of_pages)]
        if limit_pages:
            list_of_urls = list_of_urls[0:limit_pages]
        split_urls_lists = OcadoRecipesScraper._split_list(list_of_urls, threads_number)
        thread_list = [RecipesPageThread(i, split_urls_lists[i], OcadoRecipesScraper.scrape_recipe_urls_from_page, headless=self.headless) for i in range(threads_number)]
        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list:
            self.recipes_urls.extend(thread.recipes_urls)
        self.recipes_urls = list(set(self.recipes_urls))
        return self.recipes_urls
    
    @staticmethod
    def scrape_recipe_urls_from_page(driver):
        '''
        This function scrapes the product URLs of the products on the page for which the XPATH is given.
        
        Args:
            driver: 
        Returns:
            list: A list of the product URLs.
        '''
        recipe_urls_objcets = driver.find_elements(By.XPATH, '//*[@class="recipeListItem__link"]')
        return [web_object.get_attribute('href') for web_object in recipe_urls_objcets]
    
    @staticmethod
    def _get_xpaths():
        """
        Gets a dictionary containing the xpath for a recipe attribute.
        
        Return: 
            Dictionary: A dictionary of xpaths for each recipe attribute.
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
        try:
            if attribute_name in ['Ingredients', 'Times', 'Instructions']:
                return driver.find_elements(By.XPATH, xpath)
            return driver.find_element(By.XPATH, xpath)
        except:
            return None
    
    @staticmethod
    def _get_recipe_information(key, attribute_web_element):
        if key in ['Name', 'Description', 'Time', 'Serves', 'Price']:
            return attribute_web_element.text.replace("\u00e0","").replace("\u2019","")
        elif key in ['Rating']:
            return attribute_web_element.get_attribute('style').replace('width: ', '')
        elif key in ['Image URL']:
            return 'https://www.ocado.com' + attribute_web_element.get_attribute('src')
        elif key in ['Ingredients', 'Times', 'Instructions']:
            return [elem.text.replace("\u00bd","").replace("\u00bc","").replace("\u2019","").replace("\u00b0","").replace("\u2103","") for elem in attribute_web_element]
    
    def scrape_all_recipes(self, threads_number=4):
        split_urls_list = OcadoRecipesScraper._split_list(self.recipes_urls, threads_number)
        thread_list = [ScrapeRecipesDataThread(i, split_urls_list[i], OcadoRecipesScraper.scrape_recipe_data, headless=self.headless) for i in range(threads_number)]
        [thread.start() for thread in thread_list] #start scraping on each thread
        [thread.join() for thread in thread_list] #wait for threads to finish runnning
        for thread in thread_list:
            self.recipes_data.extend(thread.recipes_data)
        return self.recipes_data
    
    @staticmethod
    def scrape_recipe_data(driver, url):
        '''
        This function scrapes the recipe for a particular URL.
        
        Args:
            driver:
            url: The URL of the recipe to scrape.
        
        Returns:
            Dictionary: A nested dictionary of the recipes URL, Name and Description.
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
    
    # @staticmethod
    # def scrape_recipes_data(driver, url_list):
    #     data = []
    #     start = datetime.now()
    #     for i, url in url_list:
    #         if i%20 == 0 and i != 0:
    #             print(f"{i/len(url_list)}% done. Estimated time left: {(datetime.now()-start)*(len(url_list)/i-1)}")
    #         data.append(OcadoRecipesScraper.scrape_recipe_data(driver, url))
    #     return data
    
    @staticmethod
    def _create_folder(path):
        '''
        This function will create a folder.
        
        Args:
            path: The location where the user wants the folder.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
    
    def _save_data(self, filename, data, mode='w', indent=4):
        '''
        This functions saves the data in the files created when _create_folder is called.

        Args:
            filename: The name of the file to save the data to.
            data: The data to be saved in the file.
            mode: the mode in which the data will be saved.
            indent:
        '''
        OcadoRecipesScraper._create_folder(self.data_path)
        with open(self.data_path + f'{filename}', mode=mode) as f:
            json.dump(data, f, indent=indent) 
    
    def scrape(self, limit_pages=0):
        '''
        This function scrapes the recipes and urls and saves them into folders recipes_data and recipes_urls respectively.
        
        Args:
            limit_pages: Allows the user to choose the number of pages to scrape.
        '''
        self.scrape_all_recipe_urls(limit_pages=limit_pages)
        self._save_data('recipes_urls', self.recipes_urls)
        self.scrape_all_recipes()
        self._save_data('recipes_data', self.recipes_data)

#%%
# start = datetime.now()
# recipe = OcadoRecipesScraper(headless=False)
# recipe.scrape()
# print(datetime.now()-start)
