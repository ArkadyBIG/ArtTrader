from selenium import webdriver
from utils import URL_MARKETPLACE
d = webdriver.Firefox()
d.get('https://github.com/seleniumhq/selenium-google-code-issue-archive')

print(d.page_source)
