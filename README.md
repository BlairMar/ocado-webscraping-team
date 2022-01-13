# ocado-webscraping-team

Ocado Web Scraper

We built this commercial scraper to scrape all product and recipe data from Ocado.com, an online supermarket. The website holds thousands of products and hundreds of recipes and we scraped all of this data (+75K product pages).

For each product, we obtained almost all the information contained within the product page. For example price, description, ratings, images and whether the product was out of stock. 

Installation/Running the scraper options:


1) Run ocado_scraper/main.py to scrape all products and get status information, then upload raw data and images to an S3 bucket, process the raw data in pandas and upload tables to AWS RDS. Configure environment variables in .env file. 

2) OcadoScraper.py contains the scraper class needed to launch a new scraper and scrape all the products on the website. 
It is also possible to scrape a subset of categories.
There are several public functions to provide information: 
the categories and products available to scrape on the Ocado website.
about the status of the scrape. 

Example functions: 
1.ocado = OcadoScraper(scrape_categories=True)
2.ocado.categories_available_to_scrape()
3.ocado.scrape_products(download_images=True) OR scrape a subset of categories eg
4.ocado.scrape_products(['Bakery', 'Frozen Food'])
5.ocado.current_status_info() 
6. Scrape one product to view sample data collected and download it's images
url='https://www.ocado.com/products/hovis-best-of-both-medium-sliced-226160'
data = ocado.scrape_product(url, True)
print(data)

3) Package available on PYPI:  <insert link>

4) Image available on Docker hub: <insert link






