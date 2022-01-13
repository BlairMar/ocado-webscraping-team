#%%
import sys
sys.path.insert(0, '..//ocado_scraper')

from OcadoRecipesScraper import OcadoRecipesScraper
from selenium import webdriver
import unittest
import os

class OcadoRecipesScraperTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pwd = os.path.abspath(os.getcwd())

    def setUp(self):
        self.scraper = OcadoRecipesScraper(data_path='./data/')
        self.key_list = ['URL', 'Name', 'Description', 'Price', 'Rating', 'Ingredients', 'Image URL', 'Time', 'Instructions', 'Serves']

    def test_scrape_number_of_pages(self):
        '''
        Testing _scrape_number_of_pages. Tests there are at least 2 pages.
        '''
        self.assertGreaterEqual(self.scraper.number_of_pages, 2)

    def test_scrape_all_recipe_urls(self):
        '''
        Testing scrape_all_recipe_urls. Tests the URLs end in an integer and the word "Categories" is in them, thus ensuring they are in fact URLs.
        '''
        recipe_urls = self.scraper.scrape_all_recipe_urls(limit_pages=2)
        self.assertGreaterEqual(len(recipe_urls), 1)
        split_url_list = [url.split('/') for url in recipe_urls]
        url_end_list = [url for lists in split_url_list for i, url in enumerate(lists) if i == 6]
        for url_end in url_end_list:
            self.assertIsInstance(int(url_end[1]), int)
            self.assertEqual(url_end[::-1][0:10][::-1], 'Categories')

    def test_scrape_recipe_urls_from_page(self):
        '''
        Testing _scrape_recipe_urls_from_page. Tests the URLs end in an integer and the word "Categories" is in them, thus ensuring they are in fact URLs.
        '''
        page_urls = self.scraper._scrape_recipe_urls_from_page(self.scraper.driver)
        self.assertGreaterEqual(len(page_urls), 1)
        split_url_list = [url.split('/') for url in page_urls]
        url_end_list = [url for lists in split_url_list for i, url in enumerate(lists) if i == 6]
        for url_end in url_end_list:
            self.assertIsInstance(int(url_end[1]), int)
            self.assertEqual(url_end[::-1][0:10][::-1], 'Categories')
    
    def test_scrape_recipe_data(self):
        '''
        Testing _scrape_recipe_data. Tests the dictionary has the correct keys and there are no missing keys.
        '''
        url_for_testing = 'https://www.ocado.com/webshop/recipe/Tuna-Mayo-Sub-Club/202568?selectedCategories'
        product_name = ' '.join(url_for_testing.split('/')[5].split('-'))
        recipe_dict = self.scraper._scrape_recipe_data(self.scraper.driver, url_for_testing)
        for dict in recipe_dict.values():
            self.assertEqual(dict['Name'], product_name)
            self.assertEqual(dict['URL'], url_for_testing)
            for key in dict.keys():
                self.assertIn(key, self.key_list)
    
    def test_scrape(self):
        '''
        Testing scrape. Tests that the files recipes_data and recipe_urls exist.
        '''
        self.scraper.scrape(limit_pages=1)
        recipe_data_path_bool = os.path.isfile(f'{self.pwd}/data/recipes_data')
        self.assertTrue(recipe_data_path_bool)
        recipe_urls_path_bool = os.path.isfile(f'{self.pwd}/data/recipes_urls')
        self.assertTrue(recipe_urls_path_bool)
    
    def test_scrape_all_recipes(self):
        '''
        Testing scrape_all_recipes. Tests there are no missing items, the "Ingredients" value is a list and the "Name" value is correct.
        '''

        self.scraper.scrape_all_recipe_urls(limit_pages=1)
        all_recipes = self.scraper.scrape_all_recipes()
        for dict in all_recipes:
            for name, dicts_info in dict.items():
                for description_title in dicts_info.keys():
                    self.assertIn(description_title, self.key_list)
                    self.assertIsInstance(dicts_info['Ingredients'], list)
                    self.assertEqual(name, dicts_info['Name'])

    def tearDown(self):
        self.scraper.driver.close()
        del self.scraper
    
    @classmethod
    def tearDownClass(cls):
        os.remove(f'{cls.pwd}/data/recipes_urls')
        os.remove(f'{cls.pwd}/data/recipes_data')

unittest.main(argv=[''], verbosity=2, exit=False)
