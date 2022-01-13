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
from dotenv import load_dotenv
        
def main():
    load_dotenv()
    ocado = OcadoScraper(scrape_categories=True, headless=True) 
    print(ocado.current_status_info())
    if len(sys.argv)>1: # If categories are specified as arguments to docker run scrape those categories otherwise scrape all categorie
         ocado.scrape_products(sys.argv[1:])
    else:
        ocado.scrape_products()
    print(ocado.current_status_info())
       
    s3 = Data_and_Images_to_S3(bucket_name=os.getenv('BUCKET_NAME'), region_name=os.getenv('REGION_NAME'))
    s3.upload_product_data()
    s3.upload_images('../data/images')
    
    export = Export_to_AWS_RDS(endpoint=os.getenv('ENDPOINT'), password=os.getenv('PASSWORD'), database=os.getenv('DATABASE'))
    export.export_all_normalized_tables()
   
if __name__ == '__main__':
    main()

# %%
