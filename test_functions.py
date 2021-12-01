#%%
# from product import Product
# from selenium import webdriver
# from selenium.webdriver.common.by import By

# with open('product_urls_for_testing', 'r') as f:
#     lines = f.readlines()

# urls_list = []
# for line in lines:
#     urls_list.append(line)

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--start-maximized")
# driver = webdriver.Chrome(options=chrome_options)
# driver.maximize_window()

# info_list = []
# for url in urls_list:
#     product = Product(url)
#     info = product.scrape_product_data(driver)
#     info_list.append(info)

# for dict in info_list:
#     for key, value in dict.items():
#         if value == None:
#             print(f'{dict["Name"]} has a missing value at {key}')




#%%
from product import Product
from selenium import webdriver
from selenium.webdriver.common.by import By

with open('product_urls_for_testing', 'r') as f:
    lines = f.readlines()
urls_list = []
for line in lines:
    urls_list.append(line)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
info_list = []
for i, url in enumerate(urls_list):
    print(f'{i/70*100}% done')
    product = Product(url)
    product.download_images
    info = product.scrape_product_data(driver, product.download_images)
    info_list.append(info)

missing_keys = {key : 0 for key in info_list[0].keys()}
for dict in info_list:
    counter = 0
    print(dict)
    for key, value in dict.items():
        if value == None:
            missing_keys[key] += 1
            print(dict['URL'])
            print(f'{dict["Name"]} has a missing value at {key}/n')
        elif value != None:
            counter += 1
print(missing_keys)
print(counter)



# %%
# # For importing files in the repo
# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)


# %%
# from product import Product
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import unittest

# class ProductTestCase(unittest.TestCase):
#     def setUp(self):
#         self.chrome_options = webdriver.ChromeOptions()
#         self.chrome_options.add_argument("--start-maximized")
#         self.driver = webdriver.Chrome(options=self.chrome_options)
#         self.driver.maximize_window()

#     def test_scrape_product_data(self):
#         '''
#         Tests scrape_product_data to find any missing information and counts the number of missing information
#         '''
#         with open('product_urls_for_testing', 'r') as f:
#             lines = f.readlines()
#         urls_list = []
#         for line in lines:
#             urls_list.append(line)

#         info_list = []
#         for i, url in enumerate(urls_list):
#             print(f'{i/70*100}% done')
#             self.product = Product(url)
#             self.product.download_images
#             info = self.product.scrape_product_data(self.driver, self.product.download_images)
#             info_list.append(info)

#         missing_keys = {key : 0 for key in info_list[0].keys()}
#         for dict in info_list:
#             counter = 0
#             for key, value in dict.items():
#                 if value == None:
#                     missing_keys[key] += 1
#                     print(dict['URL'])
#                     print(f'{dict["Name"]} has a missing value at {key}/n')
#                 elif value != None:
#                     counter += 1
#             self.assertGreaterEqual(counter, 1)
#         print(missing_keys)

# unittest.main(argv=[''], verbosity=2, exit=False)



# %%
# from product import Product
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# import unittest

# class ProductTestCase(unittest.TestCase):
#     def setUp(self):
#         with open('product_urls_for_testing', 'r') as f:
#             lines = f.readlines()
#         urls_list = []
#         for line in lines:
#             urls_list.append(line)

#         for url in urls_list:
#             self.scrape = Product(url)
#             self.get_sku = self.scrape.get_sku()

#     def test_get_sku(self):
#         '''
#         Tests get_sku to see if sku is bigger than 1 and if they are a string of numbers.
#         '''
#         self.assertGreaterEqual(len(self.get_sku), 1)
#         self.get_sku_int = int(self.get_sku)
#         self.assertIsInstance(self.get_sku, str)
#         self.assertIsInstance(self.get_sku_int, int)

#     def tearDown(self):
#         del self.scrape

# unittest.main(argv=[''], verbosity=2, exit=False)



# %%
# This cell is the unit test for Product. OFFICIAL!
# # For importing files in the repo
# current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)

from product import Product
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
from OcadoScraper import OcadoScraper


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
# This cell is to test out functions from OcadoScraper.
from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import json

scraper = OcadoScraper()
scraper._scrape_category_urls()




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
        list_of_ints = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
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
    
    def test07_scrape_product(self):
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

    def test04_get_number_products_saved_from_category(self):
        number_of_products = self.scraper.number_of_products_saved_from_category('Bakery')
        self.assertEquals(number_of_products, self.LIMIT)

    def test02_get_categories_with_saved_product_data(self):
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        for category, number in self.categories_with_saved_product_data.items():
            self.category = category
            self.assertEquals(category, self.category_for_testing)
            self.assertEquals(number, self.LIMIT)

    def test03_get_categories_without_saved_product_data(self):
        self.categories_with_saved_product_data = self.scraper.get_categories_with_saved_product_data()
        self.categories_without_saved_product_data = self.scraper.get_categories_without_saved_product_data()
        for category_name in self.categories_without_saved_product_data:
            self.assertNotEqual(category_name, self.categories_with_saved_product_data.keys())
    
    def test05_delete_saved_product_data_for_category(self):
        self.scraper.delete_saved_product_data_for_category(self.category_for_testing)
        with open(f'{self.path_pwd}/data/product_data') as json_file:
            data = json.load(json_file) 
        self.assertEquals(len(data), 0)
    
    def test06_delete_saved_product_data(self):
        self.scraper.delete_saved_product_data()
        products_path_bool = os.path.isfile(f'{self.path_pwd}/data/product_data')
        self.assertFalse(products_path_bool)

    def test08_download_images(self):
        url_sku = self.url_for_testing.split('-')[-1]
        images_path_sku_bool = os.path.isdir(f'{self.path_pwd}/data/images/{url_sku}')
        self.assertTrue(images_path_sku_bool)
    
    def test09_delete_downloaded_images(self):
        self.scraper.delete_downloaded_images()
        images_path_bool = os.path.isdir(f'{self.path_pwd}/data/images/')
        self.assertFalse(images_path_bool)
    
    def tearDown(self):
        del self.scraper

unittest.main(argv=[''], verbosity=2, exit=False)
# %%
# This cell is to test functions for Product.
from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

product = Product('https://www.ocado.com/products/clearwipe-microfibre-lens-wipes-544774011')
product.download_images
product.scrape_product_data(driver, product.download_images)



# %%
# This cell is to test out new tests on Product.
from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import os.path

class ProductTestCase(unittest.TestCase):
    def test_download_images(self):
        '''
        Tests to see if path to image file exists.
        '''
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()

        product = Product('https://www.ocado.com/products/clearwipe-microfibre-lens-wipes-544774011')
        product.download_images
        product.scrape_product_data(driver, product.download_images)
        path_pwd = os.path.abspath(os.getcwd())
        image_path = os.path.isfile(f'{path_pwd}/data/images/544774011/0.jpg')
        self.assertTrue(image_path)

unittest.main(argv=[''], verbosity=2, exit=False)

# %%
# This cell is to test functions for Product_Images.
from product import Product
from OcadoScraper import OcadoScraper
from images import Product_Images
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import os.path

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

images = Product_Images()
images.scrape_images()

# %%
