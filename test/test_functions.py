# %%
# This cell is the unit test for Product. OFFICIAL!

#### For importing files in the repo
import sys
sys.path.insert(0, '..//ocado_scraper')

from product import Product
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
from OcadoScraper import OcadoScraper
import os


class ProductTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chrome_options = webdriver.ChromeOptions()
        cls.chrome_options.add_argument("--start-maximized")
        cls.driver = webdriver.Chrome(options=cls.chrome_options)
        cls.driver.maximize_window()

        with open('product_urls_for_testing', 'r') as f:
            lines = f.readlines()
        urls_list = []
        for line in lines:
            urls_list.append(line)
        
        cls.info_list = []
        cls.sku_list = []
        for i, url in enumerate(urls_list):
            print(f'{i/70*100}% done')
            product = Product(url)
            product.download_images
            info = product.scrape_product_data(cls.driver, product.download_images)
            cls.info_list.append(info)
            cls.sku_list.append(product.get_sku())

            if i == 5:
                break
    
    def setUp(self):
        pass

    def test_scrape_product_data(self):
        '''
        Tests scrape_product_data to find any missing information and counts the number of missing information
        '''
        print('test_scrape_product_data')
        missing_keys = {key : 0 for key in self.info_list[0].keys()}
        for dict in self.info_list:
            counter = 0
            for key, value in dict.items():
                if value == None:
                    missing_keys[key] += 1
                    print(dict['URL'])
                    print(f'{dict["Name"]} has a missing value at {key}/n')
                elif value != None:
                    counter += 1
            self.assertGreaterEqual(counter, 1)
        print(missing_keys)

    def test_get_sku(self):
        '''
        Tests get_sku to see if sku is bigger than 1 and if they are a string of numbers.
        '''
        for sku in self.sku_list:
            print('test_get_sku')
            self.assertGreaterEqual(len(sku), 1)
            get_sku_int = int(sku)
            self.assertIsInstance(sku, str)
            self.assertIsInstance(get_sku_int, int)

    def test_download_images(self):
        '''
        Tests to see if path to image file exists.
        '''
        product = Product('https://www.ocado.com/products/clearwipe-microfibre-lens-wipes-544774011')
        product.download_images
        product.scrape_product_data(self.driver, product.download_images)
        path_pwd = os.path.abspath(os.getcwd())
        # image_sku = url.split('-')[-1]
        image_path = os.path.isdir(f'{path_pwd}/data/images/544774011')
        self.assertTrue(image_path)
    
    def tearDown(self):
        pass
    #     print('tearDown')
    #     del self.product
    #     OcadoScraper.delete_downloaded_images()

    @classmethod
    def tearDownClass(cls):
        print('tearDown')
        # del cls.product
        OcadoScraper.delete_downloaded_images()


unittest.main(argv=[''], verbosity=2, exit=False)


# %%


# %%
#OcadoScraper OFFICIAL TEST!
from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import json
import os

class OcadoScraperTestCase(unittest.TestCase):

    def setUp(self):
        self.scraper = OcadoScraper()
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
        list_of_categories = self.scraper.categories_available_to_scrape()
        for category in list_of_categories:
            self.assertNotEqual(category, '')
        self.assertGreaterEqual(len(list_of_categories), 13)
    
    def test_number_of_products_in_categories(self):
        number_of_products_in_categories = self.scraper.number_of_products_in_categories()
        for number_of_products in number_of_products_in_categories.values():
            self.assertGreaterEqual(number_of_products, 1)
    
    def test08_scrape_product(self):
        product_info = self.scraper.scrape_product(self.url_for_testing, download_images=True)
        key_dict = ['URL', 'Name', 'Description', 'Price', 'Price per', 'Offers', 'Rating', 'Ingredients', 'Usage', 'Nutrition', 'Brand details', 'Out of Stock', 'Image links', 'Categories']
        for key in product_info.keys():
            self.assertIn(key, key_dict)
    
    def test01_scrape_products(self):
        self.scraper.scrape_products(categories=[self.category_for_testing], threads_number=1, limit=self.LIMIT)
        products_path_bool = os.path.isfile(f'{self.path_pwd}/data/product_data')
        self.assertTrue(products_path_bool)
        with open(f'{self.path_pwd}/data/product_data') as json_file:
            data = json.load(json_file) 
            product_dict = data[self.category_for_testing]
            sku_list = [sku for sku in product_dict.keys()]
            self.assertEquals(len(sku_list), self.LIMIT)

    def test05_get_number_products_saved_from_category(self):
        number_of_products = self.scraper.number_of_products_saved_from_category('Bakery')
        self.assertEquals(number_of_products, self.LIMIT)

    def test03_get_categories_with_saved_product_data(self):
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        for category, number in self.categories_with_saved_product_data.items():
            self.category = category
            self.assertEquals(category, self.category_for_testing)
            self.assertEquals(number, self.LIMIT)

    def test04_get_categories_without_saved_product_data(self):
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        self.categories_without_saved_product_data = self.scraper.get_categories_without_saved_product_data()
        for category_name in self.categories_without_saved_product_data:
            self.assertNotEqual(category_name, self.categories_with_saved_product_data.keys())
    
    def test06_delete_saved_product_data_for_category(self):
        self.scraper.delete_saved_product_data_for_category(self.category_for_testing)
        with open(f'{self.path_pwd}/data/product_data') as json_file:
            data = json.load(json_file) 
        self.assertEquals(len(data), 0)
    
    def test07_delete_saved_product_data(self):
        self.scraper.delete_saved_product_data()
        products_path_bool = os.path.isfile(f'{self.path_pwd}/data/product_data')
        self.assertFalse(products_path_bool)

    def test09_download_images(self):
        url_sku = self.url_for_testing.split('-')[-1]
        images_path_sku_bool = os.path.isdir(f'{self.path_pwd}/data/images/{url_sku}')
        self.assertTrue(images_path_sku_bool)
    
    def test10_delete_downloaded_images(self):
        self.scraper.delete_downloaded_images()
        images_path_bool = os.path.isdir(f'{self.path_pwd}/data/images/')
        self.assertFalse(images_path_bool)
    
    def test02_current_status_info(self):
        self.assertTrue(self.scraper.current_status_info())

    def tearDown(self):
        del self.scraper

unittest.main(argv=[''], verbosity=2, exit=False)

# %%
# This cell is to test functions for Product_Images.

from product import Product
from selenium import webdriver
from images import Product_Images
from OcadoScraper import OcadoScraper

potato_url = 'https://www.ocado.com/products/ocado-sweet-potatoes-544565011'

potato_product = Product(potato_url)

potato_sku = potato_product.get_sku()

driver = webdriver.Chrome() # you need a driver to call _get_web_element_by_xapth_or_none
# you probably already have a driver in your testing class
driver.get(potato_url)

image_xpath = potato_product._get_xpaths()['Image links']
potato_image_web_objects = potato_product._get_web_element_by_xpath_or_none(driver, 'Image links', image_xpath)
print(potato_image_web_objects)
#ASSERT HERE THAT potato_image_web_objects is not an empty list

potato_product_images = Product_Images(potato_sku)
potato_product_images.scrape_images(potato_image_web_objects)
potato_product_images.download_all_images()
#NOW CHECK THERE ARE IMAGES IN THE IMAGES FOLDER

# %%
from product import Product
from selenium import webdriver
from images import Product_Images
from OcadoScraper import OcadoScraper
import unittest
import os

class Product_ImagesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        potato_url = 'https://www.ocado.com/products/ocado-sweet-potatoes-544565011'
        cls.potato_product = Product(potato_url)
        cls.potato_sku = cls.potato_product.get_sku()
        cls.driver = webdriver.Chrome() # you need a driver to call _get_web_element_by_xapth_or_none
        # you probably already have a driver in your testing class
        cls.driver.get(potato_url)
        cls.potato_product_images = Product_Images(cls.potato_sku)

    def test_scrape_images(self):
        image_xpath = self.potato_product._get_xpaths()['Image links']
        potato_image_web_objects = self.potato_product._get_web_element_by_xpath_or_none(self.driver, 'Image links', image_xpath)
        print(potato_image_web_objects)
        #ASSERT HERE THAT potato_image_web_objects is not an empty list
        self.assertGreaterEqual(len(potato_image_web_objects), 0)
        self.potato_product_images.scrape_images(potato_image_web_objects)

    def test_download_all_images(self):
        self.potato_product_images.download_all_images()
        path_pwd = os.path.abspath(os.getcwd())
        images_path_bool = os.path.isfile(f'{path_pwd}/data/images/544565011/0.jpg')
        self.assertTrue(images_path_bool)
        #NOW CHECK THERE ARE IMAGES IN THE IMAGES FOLDER
    
    @classmethod
    def tearDownClas(cls):
        del cls.driver

unittest.main(argv=[''], verbosity=2, exit=False)

# %%
from OcadoRecipesScraper import OcadoRecipesScraper
from selenium import webdriver
import unittest
import os

class OcadoRecipesScraperTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pwd = os.path.abspath(os.getcwd())

    def setUp(self):
        self.scraper = OcadoRecipesScraper()
        self.key_list = ['URL', 'Name', 'Description', 'Price', 'Rating', 'Ingredients', 'Image URL', 'Time', 'Instructions', 'Serves']

    def test_get_number_of_pages(self):
        number_of_pages = self.scraper.get_number_of_pages(self.scraper.driver)
        self.assertGreaterEqual(number_of_pages, 1)

    def test_scrape_all_recipe_urls(self):
        recipe_urls = self.scraper.scrape_all_recipe_urls(limit_pages=1)
        self.assertGreaterEqual(len(recipe_urls), 1)
        split_url_list = [url.split('/') for url in recipe_urls]
        url_end_list = [url for lists in split_url_list for i, url in enumerate(lists) if i == 6]
        for url_end in url_end_list:
            self.assertIsInstance(int(url_end[1]), int)
            self.assertEqual(url_end[::-1][0:10][::-1], 'Categories')

    def test_scrape_recipe_urls_from_page(self):
        page_urls = self.scraper.scrape_recipe_urls_from_page(self.scraper.driver)
        self.assertGreaterEqual(len(page_urls), 1)
        split_url_list = [url.split('/') for url in page_urls]
        url_end_list = [url for lists in split_url_list for i, url in enumerate(lists) if i == 6]
        for url_end in url_end_list:
            self.assertIsInstance(int(url_end[1]), int)
            self.assertEqual(url_end[::-1][0:10][::-1], 'Categories')
    
    def test_scrape_recipe_data(self):
        url_for_testing = 'https://www.ocado.com/webshop/recipe/Tuna-Mayo-Sub-Club/202568?selectedCategories'
        product_name = ' '.join(url_for_testing.split('/')[5].split('-'))
        recipe_dict = self.scraper.scrape_recipe_data(self.scraper.driver, url_for_testing)
        for dict in recipe_dict.values():
            self.assertEqual(dict['Name'], product_name)
            self.assertEqual(dict['URL'], url_for_testing)
            for key in dict.keys():
                self.assertIn(key, self.key_list)
    
    def test_scrape(self):
        self.scraper.scrape(limit_pages=1)
        recipe_data_path_bool = os.path.isfile(f'{self.pwd}/data/recipes_data')
        self.assertTrue(recipe_data_path_bool)
        recipe_urls_path_bool = os.path.isfile(f'{self.pwd}/data/recipes_urls')
        self.assertTrue(recipe_urls_path_bool)
    
    def test_scrape_all_recipes(self):
        self.scraper.scrape_all_recipe_urls(limit_pages=1)
        all_recipes = self.scraper.scrape_all_recipes()
        for dict in all_recipes:
            for name, dicts_info in dict.items():
                for description_title in dicts_info.keys():
                    self.assertIn(description_title, self.key_list)
                    self.assertIsInstance(dicts_info['Ingredients'], list)
                    self.assertEqual(name, dicts_info['Name'])

    def tearDown(self):
        del self.scraper
    
    @classmethod
    def tearDownClass(cls):
        os.remove(f'{cls.pwd}/data/recipes_urls')
        os.remove(f'{cls.pwd}/data/recipes_data')

unittest.main(argv=[''], verbosity=2, exit=False)

# %%
