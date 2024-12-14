import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import subprocess
import os
import pytest

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

@pytest.fixture(scope="function")
def selenium_driver():
    """Fixture to set up and tear down Selenium WebDriver"""
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

    # Create WebDriver instance
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Yield the driver to the test
    yield driver

    # Tear down - always quit the driver after the test
    driver.quit()

def test_selenium_setup(selenium_driver):
    """Test Selenium setup with Chromium"""
    print("\n=== Starting Selenium Test ===")

    try:
        print("Navigating to example.com...")
        selenium_driver.get('https://example.com')

        # Try to find an element to verify page loading
        title = selenium_driver.title
        h1_element = selenium_driver.find_element(By.TAG_NAME, 'h1')
        h1_text = h1_element.text

        print(f"Page title: {title}")
        print(f"H1 text: {h1_text}")

        # Assertions for pytest
        assert title is not None, "Page title should not be empty"
        assert h1_text is not None, "H1 text should not be empty"
        assert "Example Domain" in title, "Page title should contain 'Example Domain'"

        print("\n✅ Selenium test completed successfully!")

    except Exception as e:
        print(f"\n❌ Selenium test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise to fail the test

# Optional: System info printing can be a separate test or moved to a conftest.py
def test_system_info():
    """Print system information as a separate test"""
    print_system_info()