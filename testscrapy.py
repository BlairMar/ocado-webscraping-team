#%%
import scrapy

with open('product_urls_for_testing', 'r') as f:
    lines = f.readlines()

class MySpider(scrapy.Spider):
    name = 'test_spider'
    allowed_domains = ['ocado.com/']
    start_urls = lines

    def parse(self, response):
        item = {}
        item['name'] = response.xpath('//*[@id="overview"]/section[1]/header/h2').get()
        item['price'] = response.xpath('//*[@id="overview"]/section[2]/div[1]/div/h2').get()
        return item

a = MySpider()
help(a)
#%%
print(lines[0])