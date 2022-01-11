# %%
#OcadoScraper OFFICIAL TEST!
import sys
sys.path.insert(0, '..//ocado_scraper')

from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import json
import os

class OcadoScraperTestCase(unittest.TestCase):

    def setUp(self):
        self.scraper = OcadoScraper(data_path='./data/')
        self.LIMIT = 5
        self.category_for_testing = 'Bakery'
        self.path_pwd = os.path.abspath(os.getcwd())
        self.url_for_testing = 'https://www.ocado.com/products/clearwipe-microfibre-lens-wipes-544774011'

    def test_scrape_category_urls(self):
        '''
        Testing _scrape_category_urls for blank keys in dictionary and if urls are showing the display figure.
        '''
        scrape_category_urls = self.scraper._scrape_category_urls()
        list_of_ints = [str(i) for i in range(10)]
        for category, url in scrape_category_urls.items():
            self.assertNotEqual(category, '')
            self.assertIn(url[-1], list_of_ints)

    def test_get_number_of_products(self):
        '''
        Testing _get_number_of_products to see if number of products is greater than 1
        '''
        get_number_of_products_str = self.scraper._get_number_of_products('https://www.ocado.com/browse/food-cupboard-20424?filters=vegetarian-19996')
        get_number_of_products = int(get_number_of_products_str)
        self.assertGreaterEqual(get_number_of_products, 1)

    def test_categories_available_to_scrape(self):
        '''
        Testing _categories_available_to_scrape. Tests category is not an empty string and list_of_categories list is greater than or equal to 13.
        '''
        list_of_categories = self.scraper.categories_available_to_scrape()
        for category in list_of_categories:
            self.assertNotEqual(category, '')
        self.assertGreaterEqual(len(list_of_categories), 13)
    
    def test_number_of_products_in_categories(self):
        '''
        Testing _number_of_products_in_categories. Tests there is more than one product in each category.
        '''
        number_of_products_in_categories = self.scraper.number_of_products_in_categories()
        for number_of_products in number_of_products_in_categories.values():
            self.assertGreaterEqual(number_of_products, 1)
    
    def test08_scrape_product(self):
        '''
        Testing scrape_product. Tests there are no missing keys in the dictionary returned.
        '''
        product_info = self.scraper.scrape_product(self.url_for_testing, download_images=True)
        key_dict = ['URL', 'Name', 'Description', 'Price', 'Price per', 'Offers', 'Rating', 'Ingredients', 'Usage', 'Nutrition', 'Brand details', 'Out of Stock', 'Image links', 'Categories']
        for key in product_info.keys():
            self.assertIn(key, key_dict)
    
    def test01_scrape_products(self):
        '''
        Testing scrape_products. Tests the product_data file exists and that the correct number of products have been scraped.
        '''
        self.scraper.scrape_products(categories=[self.category_for_testing], threads_number=1, limit=self.LIMIT)
        products_path_bool = os.path.isfile(f'{self.path_pwd}/data/product_data')
        self.assertTrue(products_path_bool)
        with open(f'{self.path_pwd}/data/product_data') as json_file:
            data = json.load(json_file) 
            product_dict = data[self.category_for_testing]
            sku_list = [sku for sku in product_dict.keys()]
            self.assertEquals(len(sku_list), self.LIMIT)

    def test05_get_number_products_saved_from_category(self):
        '''
        Testing get_number_of_products_saved_from_category. Tests that the correct number of products have been scraped.
        '''
        number_of_products = self.scraper.number_of_products_saved_from_category('Bakery')
        self.assertEquals(number_of_products, self.LIMIT)

    def test03_get_categories_with_saved_product_data(self):
        '''
        Testing get_categories_with_saved_product_data. Tests that we have the correct category and the correct number of products from that category.
        '''
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        for category, number in self.categories_with_saved_product_data.items():
            self.category = category
            self.assertEquals(category, self.category_for_testing)
            self.assertEquals(number, self.LIMIT)

    def test04_get_categories_without_saved_product_data(self):
        '''
        Testing get_categories_without_saved_product_data. Tests the categories that are not saved are difference form those that are.
        '''
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        self.categories_without_saved_product_data = self.scraper.get_categories_without_saved_product_data()
        for category_name in self.categories_without_saved_product_data:
            self.assertNotEqual(category_name, self.categories_with_saved_product_data.keys())
    
    def test06_delete_saved_product_data_for_category(self):
        '''
        Testing delete_saved_product_data_for_category. Tests the information saved is deleted.
        '''
        self.scraper.delete_saved_product_data_for_category(self.category_for_testing)
        with open(f'{self.path_pwd}/data/product_data') as json_file:
            data = json.load(json_file) 
        self.assertEquals(len(data), 0)
    
    def test07_delete_saved_product_data(self):
        '''
        Testing delete saved_product_data. Tests the file created to dump data is deleted.
        '''
        self.scraper.delete_saved_product_data()
        products_path_bool = os.path.isfile(f'{self.path_pwd}/data/product_data')
        self.assertFalse(products_path_bool)

    def test09_download_images(self):
        '''
        Testing download_images. Tests that each image has been donwloaded.
        '''
        url_sku = self.url_for_testing.split('-')[-1]
        images_path_sku_bool = os.path.isdir(f'{self.path_pwd}/data/images/{url_sku}')
        self.assertTrue(images_path_sku_bool)
    
    def test10_delete_downloaded_images(self):
        '''
        Testing delete_downloaded_images. Tests that each image from the products has been deleted.
        '''
        self.scraper.delete_downloaded_images(data_path='./data/')
        images_path_bool = os.path.isdir(f'{self.path_pwd}/data/images/')
        self.assertFalse(images_path_bool)
    
    def test02_current_status_info(self):
        '''
        Testing current_status_info. Tests the method has correctly been called.
        '''
        self.assertTrue(self.scraper.current_status_info())

    def tearDown(self):
        del self.scraper

unittest.main(argv=[''], verbosity=2, exit=False)

#%%

