#%%
import sys
import inspect
import os

sys.path.insert(0, '../post_processing')
#### For importing files in the repo
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from OcadoScraper import OcadoScraper
from AWS_RDS import Export_to_AWS_RDS
from s3 import Data_and_Images_to_S3
        
def main():
    ocado = OcadoScraper(scrape_categories=True, headless=True) 
    # if len(sys.argv)>1: # If categories are specified as arguments to docker run scrape those categories otherwise scrape all categories
    #     ocado.scrape_products(sys.argv[1:]) # this approach doesn't work when using docker compose
    # else: 
    ocado.scrape_products()
       
    s3 = Data_and_Images_to_S3(bucket_name=os.getenv('BUCKET_NAME'), region_name=os.getenv('REGION_NAME'))
    s3.upload_product_data()
    s3.upload_images('../data/images')
    
    export = Export_to_AWS_RDS(endpoint=os.getenv('ENDPOINT'), password=os.getenv('PASSWORD'), database=os.getenv('DATABASE'))
    export.export_all_normalized_tables()
   
if __name__ == '__main__':
    main()

# %%
