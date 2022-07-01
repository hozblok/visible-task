from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

options = Options()
options.add_argument('--headless')

driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options=options)
driver.get("https://www.google.com")
print('Done')
driver.quit()
