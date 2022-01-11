#%%
import sys
import inspect
import os

#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from OcadoScraper import OcadoScraper

# create a new instance of the scraper class
ocado = OcadoScraper(True, True)

# scrape all categories     
ocado.scrape_products()

# scrape the category passed as an argument to docker run
# ocado.scrape_products([sys.argv[1]])



######## docker example commands ########
# docker build -t allproducts:ver1 .
# docker volume create data-volume 
# docker run --rm -v data-volume:/data 93ee1c6b830d

# OR to just scrape a specific category eg bakery
# docker build -t bakery:ver1 .
# docker run --rm -v data-volume:/data 93ee1c6b830d "Bakery" 
# %%
