from selenium import webdriver

d = webdriver.Firefox()
d.get('https://www.google.com/')

print(d.page_source)
