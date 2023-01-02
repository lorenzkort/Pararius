import time 
 
import pandas as pd 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



def get_driver_info(headless=False):
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome('/Users/lorenzkort/.wdm/drivers/chromedriver/mac64/108.0.5359/chromedriver',
                              options=options)
    driver.implicitly_wait(5)
    url = 'http://whatismybrowser.com/'
    driver.get(url)
    time.sleep(15)
    open(f'browser_{"headless" if headless else "head"}.html', 'w+').write(driver.page_source)
    driver.quit()
    return

def get_pararius(headless=False):
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome('/Users/lorenzkort/.wdm/drivers/chromedriver/mac64/108.0.5359/chromedriver',
                              options=options)
    driver.implicitly_wait(5)
    url = 'https://www.pararius.com/apartments/haarlem/0-1200'
    driver.get(url)
    time.sleep(15)
    open(f'pararius_{"headless" if headless else "head"}.html', 'w+').write(driver.page_source)
    driver.quit()
    return

get_driver_info(headless=True)
get_driver_info(headless=False)
get_pararius(headless=True)
get_pararius(headless=False)




