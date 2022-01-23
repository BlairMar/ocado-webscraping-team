#%%
#### Upload the raw data json and all saved images to AWS S3 bucket 

import boto3 
import os
import requests

BUCKET_NAME = 'ocado-scraper-bucket'
REGION_NAME = 'us-east-1'

class Data_and_Images_to_S3:
    def __init__(self, bucket_name=BUCKET_NAME, region_name=REGION_NAME):
        self.s3_client = boto3.client('s3', region_name)
        self.s3_resource = boto3.resource('s3',region_name)
        self.bucket_name = bucket_name
        
    def upload_product_data(self):
        product_path = '../data/product_data'
        product_name = 'product_data.json'
        self._upload_data_to_s3(product_path, product_name)
    
    def upload_recipe_data(self):
        recipe_path = '../data/recipes_data'
        recipe_name = 'recipes_data'
        self._upload_data_to_s3(recipe_path, recipe_name)
        
    def _upload_data_to_s3(self, path, name):
        self.s3_client.upload_file(path, self.bucket_name, name)

    def upload_images(self, path):
        bucket = self.s3_resource.Bucket(self.bucket_name)
        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    bucket.put_object(Key=full_path[len(path)+1:], Body=data)

    # prints all the files we have stored in the S3 bucket
    def print_all_file_keys(self):
        bucket = self.s3_resource.Bucket(self.bucket_name)
        for file in bucket.objects.all():
            print(file.key)

    # use a file key from the above function to pass into this function
    def download_file_from_s3(self, file_key, name ):
        self.s3_client.download_file(self.bucket_name, file_key, name)
  

#%%           
# s3 = Data_and_Images_to_S3()
# #%%
# s3.upload_product_data()
# s3.upload_images('../data/images')
# #%%
# s3.print_all_file_keys()
# s3.download_file_from_s3('91430011/0.jpg', 'image.jpg')
#%%

