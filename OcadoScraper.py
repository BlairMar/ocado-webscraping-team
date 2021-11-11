#%%
### Imports:
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import json
import os
from pprint import pprint
import threading
###
#%%
### Class Template:
class OcadoScraper:
    def __init__(self, scrape_categories=False):
        """
        Access Ocado front page using chromedriver
        """
        self.ROOT = 'https://www.ocado.com/' 
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver.get(self.ROOT)
        self._accept_cookies()
        self.category_urls = {}
        self.product_links = {}
        self.product_data = {}
        self._get_categories(scrape_categories) # populate category_links attribute

    def _accept_cookies(self):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            _accept_cookies.click()
        except:
            print("No Cookies buttons found on page")

    def _get_categories(self, scrape_categories=True):
        if scrape_categories:
            self._scrape_category_urls()
        else:
            with open("./data/category_urls") as f:
                data = f.read()
                self.category_urls = json.loads(data)

    def _scrape_category_urls(self):
        self.driver.get(self.ROOT + "browse")
        self._accept_cookies()
        categories_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[1]/div/div/div[1]/div/div[1]/div/ul/li/a')
        self.category_urls = {category.text : category.get_attribute('href').replace("?hideOOS=true", "") for category in categories_web_object}
        for category_name, category_url in self.category_urls.items():
            number_of_products = self._get_number_of_products(category_url)
            self.category_urls[category_name] += '?display=' + number_of_products
        self._save_data("category_urls", self.category_urls, 'w')

    def _get_product_links(self, category_name):
        number_of_products_in_category = self.category_urls[category_name].split('=')[-1]
        self.driver.get(self.category_urls[category_name] + '0')
        self.product_links[category_name] = self._scroll_to_get_all_product_links(number_of_products_in_category, 30)

    def _get_number_of_products(self, category_url):
        self.driver.get(category_url)
        number_of_products = self.driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]//div/div[2]/div/span').text.split(' ')[0]
        return number_of_products

    def _scroll_to_get_all_product_links(self, number_of_products, number_of_items_in_each_scroll):
        urls_tmp_web_object = []
        n = int(int(number_of_products)/number_of_items_in_each_scroll)
        for i in range(n):
            self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/n});")
            urls_tmp_web_object.extend(self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
            time.sleep(0.5)
        urls_web_object = list(set(urls_tmp_web_object))
        urls_web_object = self.driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
        links = [url.get_attribute('href') for url in urls_web_object]
        return links

    def _get_product_data(self, category_name, download_images):
        product_details = {} 
        for i, url in enumerate(self.product_links[category_name]): ## remove enumerate 
            self.driver.get(url)
            product_sku = OcadoScraper._get_sku_from_url(url)
            product_attributes = {'URL':url}
            for key, value in OcadoScraper._get_attribute_xpaths().items():
                attribute_web_element = self._get_attribute_by_xpath_or_none(key, value)
                if attribute_web_element:
                    if key in ['Name', 'Product Information', 'Price', 'Price per', 'Offers', 'Ingredients', 'Nutrition']:
                        product_attributes[key] = attribute_web_element.text
                    if key in ['Usage', 'Brand details']:
                        product_attributes[key] = OcadoScraper._scrape_hidden_attributes(attribute_web_element)
                    if key == 'Rating':
                        product_attributes[key] = attribute_web_element.get_attribute('title').split(' ')[1]
                    if key == 'Out of Stock':
                       product_attributes[key] = True 
                    if key == 'Image links':
                       product_attributes[key] = OcadoScraper._scrape_image_links(attribute_web_element, category_name, product_sku, download_images)  
                else:
                    product_attributes[key] = False if key == 'Out of Stock' else None                                                              
            product_details[product_sku] = product_attributes
            if i == 20:  ### get the first i+1 products - just for testing
                break
        self.product_data[category_name] = product_details


    def _get_product_data_for_multithreading(self, category_name, url_list):
        product_details = {}
        for i in range(len(url_list)): ## remove enumerate 
            self.driver.get(url_list[i])
            product_attributes = {'URL':url_list[i]}
            for key, value in OcadoScraper._get_attribute_xpaths().items():
                attribute_web_element = self._get_attribute_by_xpath_or_none(key, value)
                if attribute_web_element:
                    if key in ['Name', 'Product Information', 'Price', 'Price per', 'Offers', 'Ingredients', 'Nutrition']:
                        product_attributes[key] = attribute_web_element.text
                    if key in ['Usage', 'Brand details']:
                        product_attributes[key] = OcadoScraper._scrape_hidden_attributes(attribute_web_element)
                    if key == 'Rating':
                        product_attributes[key] = attribute_web_element.get_attribute('title').split(' ')[1]
                    if key == 'Out of Stock':
                       product_attributes[key] = True 
                    if key == 'Image links':
                       product_attributes[key] = OcadoScraper._scrape_image_links(attribute_web_element)  
                else:
                    product_attributes[key] = False if key == 'Out of Stock' else None
            product_details[OcadoScraper._get_sku_from_url(url_list[i])] = product_attributes
        return product_details

    def _get_product_links_from_file(self):
        with open("./data/product_urls") as f:
            data = f.read()
            self.product_links = json.loads(data)
    
    @staticmethod
    def split_list(lst, n):
        divided_list = []
        for i in range(n):
            divided_list.append(lst[i::n])
        return divided_list


    @staticmethod
    def _scrape_image_links(web_elements, category_name, product_sku, download_images):
        image_set = set() # use a set as if we have more than one image the large image will be counted twice

        for image in web_elements:
            image_src = image.get_attribute('src')
            if "640x640" in image_src:
                image_set.add(image_src.replace("640x640", "1280x1280"))
            else: 
                image_set.add(image_src.replace("75x75", "1280x1280"))
        image_list = list(image_set)
        if download_images:
            OcadoScraper._download_all_images(image_list, category_name, product_sku)
        return image_list 
    
    @staticmethod
    def _download_all_images(image_list, category_name, product_sku):
        path = f'./data/images/{category_name}/{product_sku}'
        OcadoScraper._create_image_folder_if_not_exist(path)
        for image_url in image_list:
            image_number = image_url.split("_")[1] # image number 0 is main picture
            OcadoScraper._download_img(image_url, path + f'/{image_number}.jpg')
        
    @staticmethod
    def _create_image_folder_if_not_exist(path):
        if not os.path.exists(path):
            os.makedirs(path)
                
    @staticmethod
    def _download_img(url, path):
        img_data = requests.get(url).content
        with open(path, 'wb') as handler:
            handler.write(img_data)
    
    @staticmethod
    def _scrape_hidden_attributes(web_elements):
        text_in_hidden_elements = [element.get_attribute('textContent') for element in web_elements]
        return (' '.join(str(text) for text in text_in_hidden_elements))        

    def _get_attribute_by_xpath_or_none(self, attribute_name, xpath):
        """
        Get a web element of the product attribute xpath.

        params : 
                attribute_name: name of the product attribute
                xpath: xpath of the product attribute, eg xpath of the product name, price, description etc
        return: 
                The web element or None if nothing found.
        """
        try:
            if attribute_name in ['Usage', 'Brand details', 'Image links']:
                return self.driver.find_elements(By.XPATH, xpath)
            return self.driver.find_element(By.XPATH, xpath)
        except:
            return None

    @staticmethod
    def _get_attribute_xpaths():
        """
        Gets a dictionary containing the xpath for a product attribute.

        return: 
                A dictionary of xpaths for each product attribute

        """
        product_xpaths = { 'Name' : '//*[@id="overview"]/section[1]/header/h2',
                           'Product Information' : '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div',
                           'Price' : '//*[@id="overview"]/section[2]/div[1]/div/h2',
                           'Price per' : '//*[@id="overview"]/section[2]/div[1]/div/span[2]',
                           'Offers' : '//*[@id="overview"]/section[2]/div[2]/div/a/p',
                           'Rating' : '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span',
                           'Ingredients' : '//*[@id="productInformation"]/div[3]/div/div[2]/div[2]/div/div[1]/div',
                           'Usage' : '/html/body/div[1]/div[1]/div[3]/article/section[5]/div[2]/div[2]/div[2]//div/div',
                           'Nutrition' : '//*[@id="productInformation"]/div[3]/div/div/div[2]/div/div/div/div/table/tbody',
                           'Brand details' : '//html/body/div[1]/div[1]/div[3]/article/section[5]/div[2]/div[3]/div[2]//div/div',
                           'Out of Stock' : '//*[@id="overview"]/section[2]/div[2]/h1',
                           'Image links' : '//*[@class="bop-gallery__miniatures"]//img | /html/body/div[1]/div[1]/div[3]/article/section[1]/div/div/div[1]/img'   
                         } 
        return product_xpaths    
    
    @staticmethod
    def _get_sku_from_url(url):
        return url.split("-")[-1]

    def scrape_products(self, categories="ALL", download_images=False):
        if categories == "ALL":
            categories = self.category_urls.keys()        
        for category in categories:
            self._get_product_links(category)
            self._get_product_data(category, download_images)
        self._save_data("product_links", self.product_links)
        self._save_data("product_data", self.product_data)
        print(f"Product links and product data from the {categories} categories saved successfully")
 
    # def scrape_all_products(self):
    #     for category in self.category_urls.keys():
    #         scrape_sub_categorys(category)

    def _save_data(self, filename, data, mode='a'):
        with open(f'./data/{filename}', mode=mode) as f:
            json.dump(data, f, indent=4) 
        
    def zoom_page(self, zoom_percentage=100):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")

#%%
#Class for multithreading
class myThread(threading.Thread):
    def __init__(self, threadID, url_list, category_name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.category_name = category_name
        self.url_list = url_list
        self.ocado_scraper = OcadoScraper()
        
    def run(self):
        self.data = self.ocado_scraper._get_product_data_for_multithreading(self.category_name, self.url_list)
#%%
#test multithreading
#This takes between 90 and 120 minutes to run
# scraper_0 = OcadoScraper()
# scraper_0._get_product_links_from_file()
# list_of_url_lists = OcadoScraper().split_list(scraper_0.product_links["Fresh & Chilled Food"], 4)
# scraper_0.driver.close()

# threads = []

# for i in range(len(list_of_url_lists)):
#     threads.append(myThread(i, list_of_url_lists[i], "Fresh & Chilled Food"))

# for thread in threads:
#     thread.start()
# print("done")

#%%
#continue test multithreading

# print(threads[0].data)

# total = {}

# for thread in threads:
#     total.update(thread.data)
# print(len(total.items()))

# total_2 = {"Fresh & Chilled Food": total}
# with open('./data/product_data', 'w') as f:
#     json.dump(total_2, f, indent=4)

#%%
if __name__ == '__main__':
    pass
    # ocado = OcadoScraper() 
    # ocado.scrape_products()
#%%

# ocado = OcadoScraper()
# categories_to_scrape = ["Bakery"]
# ocado.scrape_products(categories_to_scrape, True)
# print(len(ocado.product_links["Bakery"]))


#%%
# ocado = OcadoScraper(scrape_categories=True)
# categories_to_scrape = "Fresh & Chilled Food"
# ocado._get_product_links(categories_to_scrape)
# print(len(ocado.product_links["Fresh & Chilled Food"]))
# ocado._save_data('product_urls', ocado.product_links, mode='r')

#%%
# ocado = OcadoScraper(True)
# categories_to_scrape = ["Baby, Parent & Kids"]
# ocado.scrape_products(categories_to_scrape)
# print(len(ocado.product_links["Baby, Parent & Kids"]))
        
# ocado = OcadoScraper(True)
# categories_to_scrape = ["Baby, Parent & Kids"]
# ocado.scrape_products(categories_to_scrape)
# print(len(ocado.product_links["Baby, Parent & Kids"]))

#%%
# ocado = OcadoScraper()
# ocado.scrape_all_products()
    
# %%
