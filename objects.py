import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
 
# Returns the URL's that are currently on the site
def get_pararius_objects(url='', headless=False):
    # Call as: get_pararius_objects('https://www.pararius.com/apartments/haarlem/0-1300')

    # Create driver
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    # Get HTML from site and quit driver
    driver.get(url)
    time.sleep(30)
    html = driver.page_source
    driver.quit()

    # search for all HTML list-items with class search-list__item search-list__item--listing
    soup = bs(html, 'html.parser')
    items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)
    parsed_items = ['https://pararius.com' + a['href'] for a in items]
    return parsed_items # Returns the URL's that are currently on the site