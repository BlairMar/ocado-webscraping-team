# %%
import sys
sys.path.insert(0, '..//ocado_scraper')

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
        cls.chrome_options = webdriver.ChromeOptions()
        cls.chrome_options.add_argument("--start-maximized")
        cls.chrome_options.add_argument("--headless")
        cls.potato_product = Product(potato_url)
        cls.potato_sku = cls.potato_product.get_sku()
        cls.driver = webdriver.Chrome(options=cls.chrome_options) # you need a driver to call _get_web_element_by_xapth_or_none
        # you probably already have a driver in your testing class
        cls.driver.get(potato_url)
        cls.potato_product_images = Product_Images(cls.potato_sku)

    def test_scrape_images(self):
        '''
        Tests scrape_images.
        '''
        image_xpath = self.potato_product._get_xpaths()['Image links']
        potato_image_web_objects = self.potato_product._get_web_element_by_xpath_or_none(self.driver, 'Image links', image_xpath)
        print(potato_image_web_objects)
        #ASSERT HERE THAT potato_image_web_objects is not an empty list
        self.assertGreaterEqual(len(potato_image_web_objects), 0)
        image_src_list = self.potato_product_images.scrape_images(potato_image_web_objects)
        self.assertNotEqual(image_src_list, [])

    def test_download_all_images(self):
        '''
        Testing download_all_images. Tests the image files exist.
        '''
        self.test_scrape_images()
        self.potato_product_images.download_all_images(data_path='./data/')
        path_pwd = os.path.abspath(os.getcwd())
        images_path_bool = os.path.isfile(f'{path_pwd}/data/images/544565011/0.jpg')
        self.assertTrue(images_path_bool)
        #NOW CHECK THERE ARE IMAGES IN THE IMAGES FOLDER
    
    @classmethod
    def tearDownClas(cls):
        del cls.driver

unittest.main(argv=[''], verbosity=2, exit=False)