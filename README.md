# ocado-webscraping-team

Ocado Web Scraper

We built this commercial scraper to scrape all product and recipe data from Ocado.com, an online supermarket. The website holds thousands of products and thousands of recipes and we scraped all of this data (+75K product pages and +2k recipe pages).

For each product, we obtained almost all the information contained within the product page. For example price, description, ratings, images and whether the product was out of stock.
Similarly for each recipe, we obtained information like description, rating, cooking time, ingredients and instructions.

Installation/Running the scraper options:


1) Run ocado_scraper/main.py to scrape all products and get status information, then upload raw data and images to an S3 bucket, process the raw data in pandas and upload tables to AWS RDS. Configure environment variables in .env file. 

2) OcadoScraper.py contains the scraper class needed to launch a new scraper and scrape all the products on the website. 
 - It is also possible to scrape a subset of categories.
 - There are several public functions to provide information about the categories and products available to scrape and the status of the scrape.


Example usage: 
	•	create a new instance of the scraper class: 
     	``` ocado = OcadoScraper(scrape_categories=True) ```
	•	Check which categories are available to scrape on the ocado website: 
     	```ocado.categories_available_to_scrape() ```
	•	Scrape all products and recipes on the ocado website: 
     	```ocado.scrape(recipes=True) ```
	•	Scrape all products on the ocado website and their images: 
     	```ocado.scrape_products(download_images=True)```
	•	OR scrape a subset of categories: 
     	```ocado.scrape_products(['Bakery', 'Frozen Food'])```

Information functions:
Public function to get information about the data scraped before, during and after the scrape
	•	Show status information about the scrape - eg which categories have been scraped already and number of products scraped, also which categories are left to scrape etc : ```ocado.current_status_info()```
	•	Scrape one product to view sample data collected and download it's images
		```url='https://www.ocado.com/products/hovis-best-of-both-medium-sliced-226160'
		   data = ocado.scrape_product(url, True)
		   print(data)```
	•	Display a list of categories without saved product data: ```ocado.get_categories_without_saved_product_data() ```
	•	Display the number of products in each category: ```ocado.number_of_products_in_categories() ``` Note this may be from saved data so if this is the  		     case and we want to get the latest data run categories_available_to_scrape(from_file=False)
	•	Download images for the categories specified after the scrape has been run. Default parameter is all categories: 
	        ```ocado.download_images(['Frozen Food', 'Bakery' ]) ``` (Note images can also be downloaded during the scrape by setting download_images=False in 		   scrape_products())
	•	There are also public functions to delete the saved product data file, downloaded images and to delete the product data for a specific category:
	•	```delete_saved_product_data()```
	•	```delete_saved_category_url_data```
	•	```delete_saved_product_data_for_category(“Bakery”):```
	•	```delete_downloaded_images()```

3) An UML diagram of the classes and methods used to scrape the data can be found at /docs/diagram.jpg

4) Testing files for each class used for scraping can be found at /test/

5) Package available on PYPI:  <insert link>

6) Image available on Docker hub: <insert link






