from selenium import webdriver
from utils import URL_MARKETPLACE
d = webdriver.Firefox()
d.get(URL_MARKETPLACE % 1)

print(d.page_source)
