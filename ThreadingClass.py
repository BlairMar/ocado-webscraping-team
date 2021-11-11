# WIP ThreadingClass
# import threading
# from selenium import webdriver

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