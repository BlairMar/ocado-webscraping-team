#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from pprint import pprint
import os
import requests
from uuid import uuid4

#%% 
### once we have a class make url_dictionary and driver attributes instead of params:
def get_url_list_by_category(category_name, category_url, url_dictionary, driver): 
    url_list = []    
    driver.get(category_url)   
    number_of_products_in_category = driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/div[1]/div[2]/div/span').text.split(' ')[0]
    driver.get(category_url + "?display=" + number_of_products_in_category)  
    ## Scroll to get 30 product url's at a time:
    urls_tmp_web_object = []
    n = int(int(number_of_products_in_category)/30)
    for i in range(n):
        driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight*{(i+1)/n});")
        urls_tmp_web_object.extend(driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a'))
        time.sleep(0.5)
    urls_web_object = list(set(urls_tmp_web_object))
    urls_web_object = driver.find_elements(By.XPATH, '//*[@id="main-content"]/div[2]/div[2]/ul/li/div[2]/div[1]/a')
    urls = [url.get_attribute('href') for url in urls_web_object]
    # for url in urls:
    #     url_list.append(url) # use a list as we need to scroll to find all the products
    url_dictionary[category_name] = urls


def get_product_xpaths(key):
        product_xpaths = { 'Name' : '//*[@id="overview"]/section[1]/header/h2',
                           'Description' : '//*[@id="productInformation"]/div[2]/div[1]/div[2]/div/div[1]/div',
                           'Price' : '//*[@id="overview"]/section[2]/div[1]/div/h2',
                        #  'Price per' : '//*[@id="overview"]/section[2]/div[1]/div/span', # doesn't exist for all items
                           'Rating' : '//*[@id="overview"]/section[1]/header/div/a[1]/div/span[1]/span'    
                         } 
        return product_xpaths[key]


def get_product_data_by_category(category_name, all_products_dict):
    category_links = url_data[category_name]
    product_details_dict = {} 
    for i, url in enumerate(category_links): ## remove enumerate - just for testing
        driver.get(url)
        name = driver.find_element(By.XPATH, get_product_xpaths('Name')).text
        description = driver.find_element(By.XPATH, get_product_xpaths('Description')).text
        price = driver.find_element(By.XPATH, get_product_xpaths('Price')).text
        # price_per = driver.find_element(By.XPATH, get_product_xpaths('Price per')).text # doesn't exist for all items
        rating = driver.find_element(By.XPATH, get_product_xpaths('Rating')).get_attribute('title').split(' ')[1]        
        product_details_dict[name] = { 'Description' : description,
                                       'Price' : price,
                                    #    'Price per' : price_per,
                                       'Rating' : rating 
                                    }  
        if i == 1:  ### remove - just for testing
            break
    all_products_dict[category_name] = product_details_dict
#%%

## put into function
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
driver.maximize_window()
URL = "https://www.ocado.com/browse"
driver.get(URL)

## put into function
cookie_button = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
cookie_button.click()

## create new function to get all the category url's 
# fruits_url = 'https://www.ocado.com/browse/fresh-chilled-food-20002/fruit-44490'
bakery_url = 'https://www.ocado.com/browse/bakery-25189'
# fresh_and_chilled_url = 'https://www.ocado.com/browse/fresh-chilled-food-20002'
url_data = {} ## make this an attribute
## create function to get all the top level category urls:
# get_url_list_by_category("Fruits", fruits_url, url_data, driver)
get_url_list_by_category("Bakery", bakery_url, url_data, driver)
# get_url_list_by_category("Fresh & Chilled Food", fresh_and_chilled_url, url_data, driver)
# print(len(url_data['Fruits'])) 
print(len(url_data['Bakery'])) 
# print(len(url_data['Fresh & Chilled Food'])) 
all_products_dict = {} ##make this attribute
## iterate over all the categories once we have them
# get_product_data_by_category('Fruits',all_products_dict) ## make all_products_dict an attribute
get_product_data_by_category('Bakery',all_products_dict) ## make all_products_dict an attribute
#%%
# len(all_products_dict['Fruits'])
len(all_products_dict['Bakery'])
#%%
for key, value in all_products_dict['Bakery'].items():
    print(key)
    print(value)

# %%
pprint(all_products_dict['Bakery'])
# %%

# %%
