from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time

URL = 'https://niftygateway.com/marketplace?page=1&search=&order=asc&orderType=price&onSale=true'

HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'accept': '*/*' }

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def parse():
    driver = webdriver.Firefox(executable_path=r'/home/arkady/Desktop/geckodriver')
    driver.get(URL)
    a = driver.find_elements_by_id('root')
    print(a)
        
    

if __name__ == "__main__":
    parse()
