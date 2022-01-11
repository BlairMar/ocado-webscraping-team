#%%
import os
import requests

# Product Images class used by the Scraper class 
# represents a list of the image urls associated with a product
class Product_Images:
    def __init__(self, product_sku, image_src_list=[]):
        self.product_sku = product_sku        
        self.image_src_list = image_src_list
        
    @staticmethod
    def _create_folder(path):
        '''
        This function creates a file where the images will be dumped.

        Args:
            path: The path to the file.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
                
    @staticmethod
    def _download_img(url, path):
        '''
        Downloads the image of a specfic image.
        
        Args:
            url: The URL of the product for which the image is to be downloaded.
            path: The path to the file where the image will be dumped.
            '''
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)   
            
####################################################################
# Public functions
            
    def scrape_images(self, web_elements):
        '''
        This function scrapes all image links for particular product and stores them in the image_src_list attribute '''
        image_set = set() # use a set as if we have more than one image the large image will be counted twice
        for image in web_elements:
            image_src = image.get_attribute('src')
            if "640x640" in image_src:
                image_set.add(image_src.replace("640x640", "1280x1280"))
            else: 
                image_set.add(image_src.replace("75x75", "1280x1280"))
        self.image_src_list = list(image_set)
        return self.image_src_list
        
    def download_all_images(self, data_path='../data/'):
        '''
        This function downloads all the images
        '''
        path = data_path + f'images/{self.product_sku}'

        self._create_folder(path)
        for image_url in self.image_src_list:
            image_number = image_url.split("_")[1] # image number 0 is main picture
            self._download_img(image_url, path + f'/{image_number}.jpg')
        return path
         
# %%
