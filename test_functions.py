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
# for i, url in enumerate(urls_list):
#     print(f'{i/70*100}% done')
#     product = Product(url)
#     product.download_images
#     info = product.scrape_product_data(driver, product.download_images)
#     info_list.append(info)

# missing_keys = {key : 0 for key in info_list[0].keys()}
# for dict in info_list:
#     counter = 0
#     print(dict)
#     for key, value in dict.items():
#         if value == None:
#             missing_keys[key] += 1
#             print(dict['URL'])
#             print(f'{dict["Name"]} has a missing value at {key}/n')
#         elif value != None:
#             counter += 1
# print(missing_keys)
# print(counter)



# %%
from product import Product
from OcadoScraper import OcadoScraper
from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest

class OcadoScraperTestCase(unittest.TestCase):

    def setUp(self):
        self.scraper = OcadoScraper()

    def test_scrape_category_urls(self):
        '''
        Testing _scrape_category_urls for blank keys in dictionary and if urls are showing the display figure.
        '''
        scrape_category_urls = self.scraper._scrape_category_urls()
        list_of_ints = ['0', '1,', '2', '3', '4', '5', '6', '7', '8', '9']
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
    
    def tearDown(self):
        del self.scraper

unittest.main(argv=[''], verbosity=2, exit=False)




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
