import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

class CategoryPageThread(threading.Thread):
    def __init__(self, threadID, url, number_of_scrolls, start_scrolling_at, stop_scrolling_at, func, headless=True, limit=0):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url = url
        self.number_of_scrolls = number_of_scrolls
        self.start_scrolling_at = start_scrolling_at
        self.stop_scrolling_at = stop_scrolling_at
        self.func = func # OcadoScraper._scroll_to_get_product_urls()
        self.headless = headless
        self.limit = limit
        self.chrome_options = webdriver.ChromeOptions()
        if self.headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument('window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.url)
        if not self.headless:
            self.driver.maximize_window()
        CategoryPageThread._accept_cookies(self.driver)

        self.active = True

    @staticmethod
    def _accept_cookies(driver):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            _accept_cookies.click()
            print("Cookies button clicked")
        except:
            print("No Cookies buttons found on page")
    
    def run(self):
        """
        Using the _scroll_to_get_product_urls() function from OcadoScraper
        the urls of the products appearing on the page whose url is self.url
        between self.start_scrolling_at and self.stop scrolling_at fractions of the page length
        are collected in self.product_urls
        """
        self.product_urls = self.func(self.driver, self.number_of_scrolls, self.start_scrolling_at, self.stop_scrolling_at, limit=self.limit)
        self.active = False



class ScrapingProductsThread(threading.Thread):
    def __init__(self, threadID, url_list, func, download_images=False, headless=True):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url_list = url_list
        self.func = func # OcadoScraper._scrape_product_data()
        self.download_images = download_images
        self.headless = headless
        self.chrome_options = webdriver.ChromeOptions()
        if self.headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument('window-size=1920,1080')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        if not self.headless:
            self.driver.maximize_window()
        CategoryPageThread._accept_cookies(self.driver)

        self.product_details = {}
        self.active = True
    
    @staticmethod
    def _accept_cookies(driver):
        """
        Locate and Click Cookies Button
        """
        try:
            _accept_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
            _accept_cookies.click()
            print("Cookies button clicked")
        except:
            print("No Cookies buttons found on page")

    def run(self):
        """
        Using the _scrape_product_data() function from OcadoScraper
        the products whose urls are in self.url_list are scraped and
        the results are stored in self.product_details
        """
        start = datetime.now()
        l = len(self.url_list)
        for i, url in enumerate(self.url_list):
            self.product_details[url.split("-")[-1]] = self.func(self.driver, url, self.download_images)
            time_passed = datetime.now() - start
            if i%50 == 0:
                print(f'Thread {self.threadID} is {int(i/l*100)}% done')
                if i != 0:
                    print(f'Estimated time left for thread {self.threadID}: {time_passed*(l/i-1)}')
        print(f'Thread {self.threadID} is 100% done')
        self.active = False
