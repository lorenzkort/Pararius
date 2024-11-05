from bs4 import BeautifulSoup as bs
import requests as r
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from contextlib import contextmanager
import gc

@contextmanager
def create_session():
    session = r.Session()
    try:
        yield session
    finally:
        session.close()

def get_html_content(url):
    with create_session() as session:
        response = session.get(url)
        return response.text

# Returns the URL's that are currently on the site
def get_pararius_objects(url='https://www.pararius.com/apartments/amsterdam', batch_size=10):
    """
    Fetch Pararius apartment listings using batch processing to minimize memory usage.

    Args:
        url (str): The URL to scrape
        batch_size (int): Number of items to process in each batch

    Returns:
        list: List of apartment URLs
    """
    print(f"Starting get_pararius_objects with URL: {url}")

    # Initialize Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = None
    all_listings = []

    try:
        print("Initializing Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(20)

        print(f"Navigating to URL: {url}")
        driver.get(url)

        # Wait for the first listing to appear
        print("Waiting for listings to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-search-item__link--title"))
        )

        # Get all listing elements
        listing_elements = driver.find_elements(By.CLASS_NAME, "listing-search-item__link--title")
        total_listings = len(listing_elements)
        print(f"Found {total_listings} total listings")

        # Process listings in batches
        for batch_start in range(0, total_listings, batch_size):
            batch_end = min(batch_start + batch_size, total_listings)
            print(f"Processing batch {batch_start//batch_size + 1} "
                  f"(items {batch_start + 1} to {batch_end})")

            # Process current batch
            current_batch = listing_elements[batch_start:batch_end]
            batch_urls = []

            for element in current_batch:
                try:
                    # Get href attribute directly without loading full element
                    href = element.get_attribute('href')
                    if href:
                        full_url = ('https://pararius.com' + href) if not href.startswith('http') else href
                        batch_urls.append(full_url)
                except Exception as e:
                    print(f"Error processing element: {str(e)}")
                    continue

            # Add processed batch to results
            all_listings.extend(batch_urls)

            # Print progress
            print(f"Processed {len(batch_urls)} listings in current batch")
            print(f"Total listings processed so far: {len(all_listings)}")

            # Optional: Add a small delay between batches to prevent overloading
            # time.sleep(0.5)

        return all_listings

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return []

    finally:
        if driver:
            print("Closing Chrome driver...")
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver: {str(e)}")

def get_object_details(url='https://www.pararius.com/apartment-for-rent/haarlem/26f1726d/tempeliersstraat'):
    # get HTML
    with create_session() as session:
        response = session.get(url)
        soup = bs(response.text, 'html.parser')
        details = {
            "price": '',
            "bedrooms": 0,
            "service_costs": 0,
            "rental_price_services": '',
            "surface_area": 0
        }

        # Extract and process various details from the parsed HTML

        # Get the price postfix (e.g., "per month")
        price_postfix = ''
        if soup.find("span", "listing-detail-summary__price-postfix"):
            price_postfix = soup.find("span", "listing-detail-summary__price-postfix").text

        # Extract the price, removing the postfix, euro sign, and commas
        if soup.find("div", "listing-detail-summary__price"):
            price_element = soup.find("div", "listing-detail-summary__price")
            details['price'] = price_element.text.replace(price_postfix, '').strip().replace("€", '').replace(',','')

        # Extract the number of bedrooms
        if soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms"):
            bedroom_element = soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms")
            details['bedrooms'] = bedroom_element.text.strip()

        # Extract the service costs, removing the euro sign
        if soup.find("dd","listing-features__description listing-features__description--service_costs"):
            service_cost_element = soup.find("dd","listing-features__description listing-features__description--service_costs")
            details['service_costs'] = service_cost_element.text.replace("€","").strip()

        # Extract additional rental price services information
        if soup.find("ul", "listing-features__sub-description"):
            rental_price_services_element = soup.find("ul", "listing-features__sub-description")
            details['rental_price_services'] = rental_price_services_element.text.strip()

        # Extract the surface area, removing the "m²" unit
        if soup.find("li", "illustrated-features__item illustrated-features__item--surface-area"):
            surface_area_element = soup.find("li", "illustrated-features__item illustrated-features__item--surface-area")
            details['surface_area'] = surface_area_element.text.replace("m²","")

        # Note: Consider adding error handling and type conversion for numeric fields
        # For example, converting 'price', 'bedrooms', 'service_costs', and 'surface_area' to appropriate numeric types

        del soup
        gc.collect()  # Force garbage collection

        return details

def enrich_details(details):
    # Calculate price per bedroom
    if isinstance(details['price'], int) and isinstance(details['bedrooms'], int):
        details['price_per_bedroom'] = (details['price'] + details['service_costs']) / details['bedrooms']

    # Calculate price per square meter
    if isinstance(details['price'], int) and isinstance(details['surface_area'], int):
        details['price_per_m2'] = details['price'] / details['surface_area']

    return details

def get_pararius_objects(url='https://www.pararius.com/apartments/amsterdam'):
    print(f"Starting get_pararius_objects with URL: {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Applicable to Windows and Linux
    chrome_options.add_argument("--disable-software-rasterizer")  # Prevent software rasterizer from being used
    chrome_options.add_argument("--window-size=1920x1080")  # Set a default window size

    driver = None

    try:
        print("Initialising Chrome driver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(10)

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
