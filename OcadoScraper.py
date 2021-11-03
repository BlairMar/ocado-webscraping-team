#%%
### Imports: 
from selenium import webdriver
from selenium.webdriver.common.by import By
from pprint import pprint
###

### Class Template:
class OcadoScraper:
    def __init__(self):
        """
        Access Ocado front page using chromedriver
        """
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.maximize_window()
        self.driver.get('https://www.ocado.com/')
        try:
            self._accept_cookies()
        except:
            pass

    def _accept_cookies(self):
        """
        Locate and Click Cookies Button
        """
        _accept_cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
        _accept_cookies.click()

    def func2(self):
        """
        Gets Browse shop category URLs
        """
    
    def func3(self):
        """
        Gets inner category urls from each Browse shop category
        """
    
    def func4(self):
        """
        Opens URL in new tab
        """

    def func5(self):
        """
        Closes current tab (This function might be redundant)
        """

    def func6_0(self):
        """
        Gets number of items that can be displayed on page
        """

    def func6(self):
        """
        Displays all items on page
        """

    def func7(self):
        """
        Collects all the item URLs on a page
        """
    
    def func8(self):
        """
        Gets images from item page
        """
    
    def func9_0(self):
        """
        Gets price, description, SKU, reviews from item page
        """
    def func9(self):
        """
        Scrapes an item's page
        """

    def func10(self):
        """
        Creates folder in which to store data dictionaries if the folder doesn't already exist
        """
    
    def func11(self):
        """
        Saves data into dictionary
        """
    
    def func12(self):
        """
        Saves dictionary in a file
        """

if __name__ == '__main__':
    ocado = OcadoScraper()