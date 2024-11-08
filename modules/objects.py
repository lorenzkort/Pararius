from bs4 import BeautifulSoup as bs
import requests as r
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from contextlib import contextmanager
import gc
import logging
import time
from threading import Lock
from queue import Queue
import os

class ParariusDriver:
    _instance = None
    _lock = Lock()
    _driver = None
    _task_queue = Queue()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self):
        if ParariusDriver._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ParariusDriver._instance = self
            self._setup_driver()

    def _setup_driver(self):
        chrome_options = Options()
        chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--dns-prefetch-disable')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Set up ChromeDriver service
        service = Service(
            executable_path=os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        )

        self._driver = webdriver.Chrome(service=service, options=chrome_options)
        self._driver.set_page_load_timeout(10)

    def get_driver(self):
        if self._driver is None:
            self._setup_driver()
        return self._driver

    def add_task(self, task):
        """Add a scraping task to the queue"""
        self._task_queue.put(task)

    def process_queue(self):
        """Process tasks from the queue with rate limiting"""
        while not self._task_queue.empty():
            task = self._task_queue.get()
            try:
                result = self._process_task(task)
                # Add delay between tasks for rate limiting
                time.sleep(2)  # Adjust this value based on your needs
                self._task_queue.task_done()
                yield result
            except Exception as e:
                logging.error(f"Error processing task: {e}")
                self._task_queue.task_done()

    def _process_task(self, task):
        """Process a single scraping task"""
        with self._lock:
            driver = self.get_driver()
            try:
                driver.get(task['url'])
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "listing-search-item__link--title"))
                )
                return driver.page_source
            except Exception as e:
                logging.error(f"Error in task processing: {e}")
                return None

    def quit(self):
        if self._driver:
            try:
                self._driver.quit()
            except Exception as e:
                logging.error(f"Error closing driver: {str(e)}")
            finally:
                self._driver = None

@contextmanager
def create_session():
    session = r.Session()
    try:
        yield session
    finally:
        session.close()

def get_pararius_objects(url='https://www.pararius.com/apartments/amsterdam', batch_size=10):
    """
    Thread-safe implementation of Pararius apartment listings fetcher using queue.
    """
    logging.info(f"Starting get_pararius_objects with URL: {url}")
    all_listings = []

    try:
        # Get the singleton driver instance
        driver_manager = ParariusDriver.get_instance()

        # Add scraping task to queue
        driver_manager.add_task({'url': url, 'batch_size': batch_size})

        # Process the queue and get results
        for html in driver_manager.process_queue():
            if html:
                # Process HTML outside the lock
                soup = bs(html, 'html.parser')
                items = soup.find_all("a", "listing-search-item__link listing-search-item__link--title", href=True)

                # Process items in batches
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    batch_urls = ['https://pararius.com' + a['href'] for a in batch]
                    all_listings.extend(batch_urls)

                    # Add delay between batches
                    time.sleep(0.5)

                    logging.info(f"Processed batch of {len(batch_urls)} items")

                # Clean up
                del soup
                gc.collect()

        logging.info(f"Found {len(all_listings)} items total.")
        return all_listings

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return []

def get_object_details(url):
    """Thread-safe implementation of object details fetcher with rate limiting"""
    time.sleep(1)  # Rate limiting for API calls

    with create_session() as session:
        try:
            response = session.get(url)
            soup = bs(response.text, 'html.parser')
            details = {
                "price": '',
                "bedrooms": 0,
                "service_costs": 0,
                "rental_price_services": '',
                "surface_area": 0
            }

            # Extract price postfix
            if soup.find("span", "listing-detail-summary__price-postfix"):
                price_postfix = soup.find("span", "listing-detail-summary__price-postfix").text

            # Extract price
            if soup.find("div", "listing-detail-summary__price"):
                price_element = soup.find("div", "listing-detail-summary__price")
                details['price'] = price_element.text.replace(price_postfix, '').strip().replace("€", '').replace(',','')

            # Extract bedrooms
            if soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms"):
                bedroom_element = soup.find("dd", "listing-features__description listing-features__description--number_of_bedrooms")
                details['bedrooms'] = bedroom_element.text.strip()

            # Extract service costs
            if soup.find("dd","listing-features__description listing-features__description--service_costs"):
                service_cost_element = soup.find("dd","listing-features__description listing-features__description--service_costs")
                details['service_costs'] = service_cost_element.text.replace("€","").strip()

            # Extract rental price services
            if soup.find("ul", "listing-features__sub-description"):
                rental_price_services_element = soup.find("ul", "listing-features__sub-description")
                details['rental_price_services'] = rental_price_services_element.text.strip()

            # Extract surface area
            if soup.find("li", "illustrated-features__item illustrated-features__item--surface-area"):
                surface_area_element = soup.find("li", "illustrated-features__item illustrated-features__item--surface-area")
                details['surface_area'] = surface_area_element.text.replace("m²","")

            return details

        except Exception as e:
            logging.error(f"Error fetching details for {url}: {str(e)}")
            return None
        finally:
            del soup
            gc.collect()

def enrich_details(details):
    # Calculate price per bedroom
    if isinstance(details['price'], int) and isinstance(details['bedrooms'], int):
        details['price_per_bedroom'] = (details['price'] + details['service_costs']) / details['bedrooms']

    # Calculate price per square meter
    if isinstance(details['price'], int) and isinstance(details['surface_area'], int):
        details['price_per_m2'] = details['price'] / details['surface_area']

    return details

def cleanup():
    try:
        driver_manager = ParariusDriver.get_instance()
        driver_manager.quit()
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    print("Starting main execution...")
    try:
        results = get_pararius_objects()
        print(f"Total results: {len(results)}")
        if results:
            print("First few results:")
            for url in results[:5]:
                print(url)
        else:
            print("No results found.")
    finally:
        cleanup()
