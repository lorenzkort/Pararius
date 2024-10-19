import time
from bs4 import BeautifulSoup as bs
import requests as r
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a session object
session = r.Session()

def get_html_content(url):
    response = session.get(url)
    return response.text

# Returns the URL's that are currently on the site
def get_pararius_objects(url='https://www.pararius.com/apartments/haarlem/0-1300'):
    print(f"Fetching URL: {url}")
    
    html = get_html_content(url)
    print(f"HTML content length: {len(html)} characters")
    
    print("First 1000 characters of HTML:")
    print(html[:1000])
    
    soup = bs(html, 'html.parser')
    
    # Print all unique tag names in the HTML
    unique_tags = set([tag.name for tag in soup.find_all()])
    print("\nUnique HTML tags found:")
    print(", ".join(sorted(unique_tags)))
    
    # Print all unique class names in the HTML
    unique_classes = set([cls for tag in soup.find_all() for cls in tag.get('class', [])])
    print("\nUnique class names found:")
    print(", ".join(sorted(unique_classes)))
    
    # Print the structure of the first few levels of the HTML
    print("\nHTML structure (first 3 levels):")
    def print_structure(element, level=0, max_level=3):
        if level >= max_level:
            return
        print("  " * level + f"<{element.name}>")
        for child in element.children:
            if child.name:
                print_structure(child, level + 1, max_level)
    
    print_structure(soup.html)
    
    # Check for any error messages or captcha
    error_message = soup.find('div', class_='error-message')
    if error_message:
        print(f"Error message found: {error_message.text.strip()}")
    
    captcha = soup.find('div', id='captcha-container')
    if captcha:
        print("Captcha detected on the page")
    
    # Look for the main content container
    main_content = soup.find('main', id='main')
    if main_content:
        print("Main content container found")
    else:
        print("Main content container not found")
    
    # Search for apartment listings
    items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)
    print(f"Number of apartment listings found: {len(items)}")
    
    # Check for other common elements
    print("\nChecking for other common elements:")
    common_elements = [
        ('header', soup.find('header')),
        ('footer', soup.find('footer')),
        ('search form', soup.find('form', class_='search-form')),
        ('pagination', soup.find('nav', class_='pagination'))
    ]
    for name, element in common_elements:
        if element:
            print(f"- {name.capitalize()} found")
        else:
            print(f"- {name.capitalize()} not found")
    
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
        details['price'] = soup.find("div", "listing-detail-summary__price").text.replace(price_postfix, '').strip().replace("€", '').replace(',','')
    
    if soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms"):
        details['bedrooms'] = soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms").text.strip()
    
    if soup.find("dd","listing-features__description listing-features__description--service_costs"):
        details['service_costs'] = soup.find("dd","listing-features__description listing-features__description--service_costs").text.replace("€","").strip()
    
    if soup.find("ul", "listing-features__sub-description"):
        details['rental_price_services'] = soup.find("ul", "listing-features__sub-description").text.strip()
        
    if soup.find("li", "illustrated-features__item illustrated-features__item--surface-area"):
        details['surface_area'] = soup.find("li", "illustrated-features__item illustrated-features__item--surface-area").text.replace("m²","")
    
    return details

def enrich_details(details):
    if type(details['price']) == int and type(details['bedrooms']) == int:
        details['price_per_bedroom'] = ( details['price'] + details['service_costs'] ) / details['bedrooms']
        
    if type(details['price']) == int and type(details['surface_area']) == int:
        details['price_per_m2'] = details['price'] / details['surface_area']
        
    return details

# print(enrich_details(get_object_details()))

def get_pararius_objects(url='https://www.pararius.com/apartments/amsterdam'):
    print(f"Starting get_pararius_objects with URL: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows and Linux
    chrome_options.add_argument("--disable-software-rasterizer")  # Prevent software rasterizer from being used
    chrome_options.add_argument("--window-size=1920x1080")  # Set a default window size
        
    print("Initialising Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(10)
    
    try:
        print(f"Navigating to URL: {url}")
        driver.get(url)
        
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-search-item__link--title"))
        )
        
        print("Page loaded. Parsing HTML...")
        html = driver.page_source
        soup = bs(html, 'html.parser')
        
        items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)
        parsed_items = ['https://pararius.com' + a['href'] for a in items]
        
        print(f"Found {len(parsed_items)} items.")
        return parsed_items
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []
    finally:
        print("Closing Chrome driver...")
        try:
            driver.quit()
        except Exception as e:
            print(f"Error closing driver: {str(e)}")

# Test the function
if __name__ == "__main__":
    print("Starting main execution...")
    results = get_pararius_objects()
    print(f"Total results: {len(results)}")
    if results:
        print("First few results:")
        for url in results[:5]:
            print(url)
    else:
        print("No results found.")

# Add this function at the end of the file
def cleanup():
    session.close()
