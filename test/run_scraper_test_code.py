#%%
import sys
sys.path.insert(0, '..//ocado_scraper')

from OcadoScraper import OcadoScraper

# create a new instance of the scraper class
ocado = OcadoScraper()
#%% 
# get the categories available to scrape on the ocado website. Either from file or from the website - this will update the category urls data 
ocado.categories_available_to_scrape(True)
#%%
# get the current status of the scrape - which categories have been saved already
ocado.current_status_info()
#%%
# get the number of products in each category - note this may be from saved data so if this 
# is the case and we want to get the latest data run categories_available_to_scrape(True)
ocado.number_of_products_in_categories()
#%%
#scrape all products on the ocado website
ocado.scrape_products()
#%%
# scrape only the categories specified
ocado.scrape_products(['Bakery', 'Frozen Food'])
#%% 
# scrape all categories we don't have saved product data for 
ocado.scrape_products(ocado.get_categories_without_saved_product_data())
#%%
ocado = OcadoScraper(True) #pass True in to scrape category URLs if either 1) these have changed eg after Christmas or 2) the number of products in the category has changed significantly
categories_to_scrape = ['Fresh & Chilled Food', 'Frozen Food']
ocado.scrape_products(categories_to_scrape)
#%%
# scrape one product to view sample data collected and download it's images 
url = 'https://www.ocado.com/products/hovis-best-of-both-medium-sliced-22616011'
data = ocado.scrape_product(url, True) 
print(data)
#%%
ocado = OcadoScraper(False, False) # don't scrape in headless mode
#%%
# download images for the saved categories specified - these categories must be scraped first
ocado.download_images(['Frozen Food', 'Bakery' ])
#%%
# print(len(ocado.product_urls["Clothing & Accessories"]))
#%%
# Test multithreading for scrape product urls
# ocado = OcadoScraper()
# category1 = 'Clothing & Accessories'
# category3 = 'Food Cupboard'
# url1 = 'https://www.ocado.com/browse/clothing-accessories-148232?display=943'
# url2 = 'https://www.ocado.com/browse/christmas-317740?display=4958'
# url3 ='https://www.ocado.com/browse/food-cupboard-20424?display=13989'
# ocado._scrape_product_urls(url3, category3, threads_number=3)
#%%
# Test multithreading for _scrape_product_data_for_category
# ocado = OcadoScraper()
# category1 = 'Clothing & Accessories'
# category3 = 'Food Cupboard'
# url1 = 'https://www.ocado.com/browse/clothing-accessories-148232?display=943'
# url2 = 'https://www.ocado.com/browse/christmas-317740?display=4958'
# url3 ='https://www.ocado.com/browse/food-cupboard-20424?display=13989'
# ocado._scrape_product_urls(url3, category3, threads_number=3)
# print('available',ocado.categories_available_to_scrape(),'\n')
# print('saved',ocado.get_categories_with_saved_product_data(),'\n')
# print('not saved',ocado.get_categories_without_saved_product_data(),'\n')
#%%
# Test headless
# ocado = OcadoScraper()
# a = ocado._scrape_category_urls()
# ocado.driver.save_screenshot('screenie.png')
# print(a)
# ocado.driver.close()

#%%
# For _scrape_category_urls()
# 1. there are more than 2 items
# 2. keys are not empty strings
# 3. urls(dictionary values) end in a number
# _get_number_of_products()
# https://www.ocado.com/browse?filters=vegetarian-19996
# check that the number is bigger than 1

#%%


# %%
