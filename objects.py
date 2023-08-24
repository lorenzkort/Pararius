import time
from bs4 import BeautifulSoup as bs
import requests as r


 
# Returns the URL's that are currently on the site
def get_pararius_objects(url='https://www.pararius.com/apartments/haarlem/0-1300', headless=False):
    
    # Call as: get_pararius_objects('https://www.pararius.com/apartments/haarlem/0-1300')
    html = r.get(url).text

    # search for all HTML list-items with class search-list__item search-list__item--listing
    soup = bs(html, 'html.parser')
    items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)
    parsed_items = ['https://pararius.com' + a['href'] for a in items]
    
    return parsed_items # Returns the URL's that are currently on the site