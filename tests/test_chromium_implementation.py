import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
import os

def print_system_info():
    """Print relevant system information for debugging"""
    print("\n=== System Information ===")
    print(f"Python version: {sys.version}")

    # Check Chromium version
    try:
        chromium_version = subprocess.check_output(['chromium', '--version']).decode().strip()
        print(f"Chromium version: {chromium_version}")
    except Exception as e:
        print(f"Error getting Chromium version: {e}")

    # Check ChromeDriver version
    try:
        chromedriver_version = subprocess.check_output(['chromedriver', '--version']).decode().strip()
        print(f"ChromeDriver version: {chromedriver_version}")
    except Exception as e:
        print(f"Error getting ChromeDriver version: {e}")

    # Print environment variables
    print("\n=== Environment Variables ===")
    print(f"CHROME_BIN: {os.environ.get('CHROME_BIN', 'Not set')}")
    print(f"CHROMEDRIVER_PATH: {os.environ.get('CHROMEDRIVER_PATH', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")

def test_selenium_setup():
    """Test Selenium setup with Chromium"""
    print("\n=== Starting Selenium Test ===")

    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.binary_location = os.environ.get('CHROME_BIN', '/usr/bin/chromium')

        # Set up ChromeDriver service
        service = Service(
            executable_path=os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        )

        print("Creating WebDriver instance...")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        print("Navigating to example.com...")
        driver.get('https://example.com')

        # Try to find an element to verify page loading
        title = driver.title
        h1_text = driver.find_element(By.TAG_NAME, 'h1').text

        print(f"Page title: {title}")
        print(f"H1 text: {h1_text}")

        driver.quit()
        print("\n✅ Selenium test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Selenium test failed: {str(e)}")
        print("\nStack trace:")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print_system_info()
    success = test_selenium_setup()
    sys.exit(0 if success else 1)
