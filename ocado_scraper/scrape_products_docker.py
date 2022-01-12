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

# If categories are specified as arguments to docker run scrape those categories 
# otherwise scrape all categories 
if sys.argv[1]:
    ocado.scrape_products(sys.argv[1:])
else:
    ocado.scrape_products()

######## docker example commands ########
# docker build -t ocado:1 .
# docker run --rm 90ae05b3e30e "Bakery"

# docker volume create data-volume 

# docker run --rm -v data-volume:/data 90ae05b3e30e
# OR to just scrape a specific category eg bakery
# docker run --rm -v data-volume:/data 90ae05b3e30e "Bakery" 
# %%
