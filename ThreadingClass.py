# WIP ThreadingClass
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By

class CategoryPageThread(threading.Thread):
    def __init__(self, threadID, url, number_of_scrolls, start_scrolling_at, stop_scrolling_at, func):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url = url
        self.number_of_scrolls = number_of_scrolls
        self.start_scrolling_at = start_scrolling_at
        self.stop_scrolling_at = stop_scrolling_at
        self.func = func
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.url)
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
        self.product_urls = self.func(self.driver, self.number_of_scrolls, self.start_scrolling_at, self.stop_scrolling_at)
        self.active = False









# class myThread(threading.Thread):
#     def __init__(self, driver, threadID, url_list, function):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.url_list = url_list
#         self.function = function
#         self.chrome_options = webdriver.ChromeOptions()
#         self.chrome_options.add_argument("--start-maximized")
#         self.driver = webdriver.Chrome(options=self.chrome_options)
        
#     def run(self):
#         self.function(self.url_list)