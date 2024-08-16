import undetected_chromedriver as uc
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import logging

def initialize_driver():
    # Generate a random user agent
    ua = UserAgent()
    fake_user_agent = ua.random

    # Selenium Wire options
    seleniumwire_options = {
        'proxy': {
            'http': 'http://xbbxciqu-rotate:5wr5qae1jymj@p.webshare.io:80',
            'https': 'http://xbbxciqu-rotate:5wr5qae1jymj@p.webshare.io:80',
            'no_proxy': 'localhost,127.0.0.1'
        },
        'ca_cert': 'ca.crt',
        'disable_encoding': True  # Disable request encoding to improve performance
    }

    # Set Chrome options for headless execution
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument(f'user-agent={fake_user_agent}')

    # Initialize the WebDriver using undetected-chromedriver
    return uc.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)

def scrape_prices(driver, url):
    driver.get(url)
    time.sleep(5)  # Allow dynamic content to load

    # Handle the "OK" modal button if present
    try:
        ok_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button.sc-imWZod.bqiFXe.c-axs-button.btn--single.btn.btn-default.fanSight-btn')))
        ok_button.click()
        time.sleep(3)
    except Exception:
        pass  # Ignore if the modal is not present

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="main"]')))
    time.sleep(3)

    # Attempt to locate the price in three different locations
    try:
        # Primary price location
        main_div = driver.find_element(By.CSS_SELECTOR, 'div[role="main"]')
        price_div = main_div.find_element(By.CSS_SELECTOR, "div.sc-dIMiFF.jogrwx > div.sc-hfYwrA.QleGC > p.sc-dCrkxH.khAhjN")
        price_text = price_div.text.strip()
        if price_text:
            return price_text
    except Exception:
        pass  # Move to secondary location if primary fails

    try:
        # Secondary price location
        price_div_secondary = main_div.find_element(By.CSS_SELECTOR, "div.sc-aYaIB.dOxdYv.c-axs-block.sc-ebXHZa.hSytnQ.c-axs-button-filter")
        price_text = price_div_secondary.text.strip()
        if price_text:
            return price_text
    except Exception:
        pass  # Move to tertiary location if secondary fails

    try:
        # Tertiary price location
        price_level_containers = main_div.find_elements(By.CSS_SELECTOR, "div.price-level__range span.price-range span span")
        if price_level_containers:
            price_text = price_level_containers[0].text.strip()
            return price_text
    except Exception:
        pass

    return "Price not available"  # If all locations fail


def main():
    logging.getLogger('seleniumwire').setLevel(logging.ERROR)  # Suppress verbose logs
    driver = initialize_driver()

    try:
        urls_df = pd.read_csv('links_with_tickets.csv')
        urls = urls_df['Ticket URL'].tolist()
        prices = []  # List to store prices

        for i, url in enumerate(urls):
            price = scrape_prices(driver, url)
            prices.append(price)
            # Update the DataFrame and save to CSV after processing each URL
            urls_df.loc[i, 'Price'] = price
            urls_df.to_csv('links_with_prices.csv', index=False)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
