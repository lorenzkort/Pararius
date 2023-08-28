import time
from bs4 import BeautifulSoup as bs
import requests as r


 
# Returns the URL's that are currently on the site
def get_pararius_objects(url='https://www.pararius.com/apartments/haarlem/0-1300'):
    
    # Call as: get_pararius_objects('https://www.pararius.com/apartments/haarlem/0-1300')
    html = r.get(url).text

    # search for all HTML list-items with class search-list__item search-list__item--listing
    soup = bs(html, 'html.parser')
    items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)
    parsed_items = ['https://pararius.com' + a['href'] for a in items]
    
    return parsed_items # Returns the URL's that are currently on the site

def get_object_details(url='https://www.pararius.com/apartment-for-rent/haarlem/26f1726d/tempeliersstraat'):
    # get HTML
    html = r.get(url).text
    soup = bs(html, 'html.parser')
    details = {
        "price": '',
        "bedrooms": 0,
        "service_costs": 0,
        "rental_price_services": '',
        "surface_area": 0
    }
    
    # Get data points
    price_postfix = ''
    if soup.find("span", "listing-detail-summary__price-postfix"):
        price_postfix = soup.find("span", "listing-detail-summary__price-postfix").text
    
    if soup.find("div", "listing-detail-summary__price"):
        details['price'] = int(soup.find("div", "listing-detail-summary__price").text.replace(price_postfix, '').strip().replace("€", '').replace(',',''))
    
    if soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms"):
        details['bedrooms'] = int(soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms").text.strip())
    
    if soup.find("dd","listing-features__description listing-features__description--service_costs"):
        details['service_costs'] = int(soup.find("dd","listing-features__description listing-features__description--service_costs").text.replace("€","").strip())
    
    if soup.find("ul", "listing-features__sub-description"):
        details['rental_price_services'] = soup.find("ul", "listing-features__sub-description").text.strip()
        
    if soup.find("li", "illustrated-features__item illustrated-features__item--surface-area"):
        details['surface_area'] = int(soup.find("li", "illustrated-features__item illustrated-features__item--surface-area").text.replace("m²",""))
    
    return details

def enrich_details(details):
    if details['price'] and details['bedrooms']:
        details['price_per_bedroom'] = int(( details['price'] + details['service_costs'] ) / details['bedrooms'])
        
    if details['price'] and details['surface_area']:
        details['price_per_m2'] = int(details['price'] / details['surface_area'])
        
    return details

# print(enrich_details(get_object_details()))