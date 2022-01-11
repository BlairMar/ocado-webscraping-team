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
        cls.chrome_options.add_argument("--headless")
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