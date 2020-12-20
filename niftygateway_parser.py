from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
from functools import cached_property
from utils import URL_MARKETPLACE, URL_BASE_OFFER

def parse_price_from_description(description):
    try:
        return float(description.rsplit('$')[-1])
    except ValueError:
        return -1

class Offer:
    def __init__(self, element=None, token_id=None, contract_address=None, price=None, description=None):
        if element:
            self._element = element
            self.text = element.text
            self.price = parse_price_from_description(element.text)
            self.token_id = None
            self.contract_address = None
            self.description = self.text.split('#')[0]
        else:
            self.text = None
            self.price = price
            self.token_id = token_id
            self.contract_address = contract_address
            self.description = description
        
    def set_url(self, url):
        url = url.rsplit('/', 2)
        self.token_id = int(url[-1])
        self.contract_address = url[-2]
    
    @property
    def url(self):
        return '%s%s/%s' % (URL_BASE_OFFER, self.contract_address, self.token_id)
    
class NiftygatewayParser:
    def __init__(self, url=URL_MARKETPLACE):
        self._url_marketplace = url
        
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2, 
                 'profile.default_content_settings.images': 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome('/home/ubuntu/chromedriver', options=chrome_options)
    
    def get_offers(self, max_price=None, on_pool=None):
        if max_price is None:
           max_price = float('inf')
        
        if on_pool is None:
            on_pool = lambda *_: None
        
        self._load_marketplace_page(1)
        page_count = self._get_marketplace_page_count()
        offers = self._get_offers_on_page(max_price)
        on_pool(1, page_count, offers, max_price)
        
        empty_pages_in_row = 0
        for page_number in range(2, page_count + 1):
            self._load_marketplace_page(page_number)
            time.sleep(2)
            new_offers = self._get_offers_on_page(max_price)

            offers += new_offers
            on_pool(page_number, page_count, offers, max_price)

            empty_pages_in_row += not new_offers
            if empty_pages_in_row >= 1:
                break
        return offers
    
    def close(self):
        self.driver.close()
    
    def _get_offer_page_url(self, offer):
        offer._element.click()
        url = self.driver.current_url
        return url
    
    def _get_raw_offers_on_page(self):
        for _ in range(20):
            offers = self.driver.find_elements_by_class_name('MuiGrid-grid-lg-3')
            if len(offers) == 20:
                break
            time.sleep(0.1)
        else:
            print('error')
            return None
        return [Offer(i) for i in offers]
    
    def _get_offers_on_page(self, max_price):
        offers = []
        processed_texts = set()
        current_url = self.driver.current_url
        for _ in range(20):
            raw_offers = self._get_raw_offers_on_page()
            offer_element = (i for i in raw_offers if 
                     i.price <= max_price and 
                     i.text not in processed_texts)

            if offer := next(offer_element, None):
                processed_texts.add(offer.text)
                offers.append(offer)
                
                offer.set_url(self._get_offer_page_url(offer))
                self.driver.get(current_url)
                
                time.sleep(0.5)
                print(offer.url, offer.price)
            else:
                break
        return offers
    
    def _get_marketplace_page_count(self):
        for _ in range(20):
            pages = self.driver.find_elements_by_class_name('MuiPaginationItem-rounded')
            if pages:
                break
            time.sleep(0.1)
        else:
            print('error')
            return 0
        return max((int(p.text) for p in pages if p.text))
    
    def _load_marketplace_page(self, page_number: int):
        self.driver.get(self._url_marketplace % page_number)


if __name__ == "__main__":
    NiftygatewayParser()
