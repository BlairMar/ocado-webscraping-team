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

# scrape the category passed as an argument to docker run
ocado.scrape_products([sys.argv[1]])

# scrape all categories     
# ocado.scrape_products()



# %%
