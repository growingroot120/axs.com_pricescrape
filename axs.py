import undetected_chromedriver as uc
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Generate a random user agent
ua = UserAgent()
fake_user_agent = ua.random

# Selenium Wire options
seleniumwire_options = {
    'proxy': {
        'http': 'http://xbbxciqu-rotate:5wr5qae1jymj@p.webshare.io:80',
        'https': 'http://xbbxciqu-rotate:5wr5qae1jymj@p.webshare.io:80',
        'no_proxy': 'localhost,127.0.0.1'  # Bypass the proxy for these addresses
    },
    'ca_cert': 'ca.crt'
}

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-fullscreen")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument(f'user-agent={fake_user_agent}')

# Initialize the WebDriver using undetected-chromedriver
driver = uc.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)

try:
    # Navigate to the AXS browse page
    driver.get("https://www.axs.com/browse")

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "events_link")))

    events_data = []
    seen_urls = set()

    # Scroll down 500 pixels, repeating 200 times
    for _ in range(200):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.4)  # Pause slightly between scrolls to simulate human scrolling
        
        # Find elements with class 'events_link' and extract data
        events = driver.find_elements(By.CLASS_NAME, "events_link")
        for event in events:
            try:
                href = event.get_attribute("href")
                title = event.get_attribute("title")
                
                # Ensure the event is unique
                if href in seen_urls:
                    continue
                seen_urls.add(href)
                
                # Extract date and time details
                date_elements = event.find_elements(By.CSS_SELECTOR, ".results-table__col--event .date-block__starting, .results-table__col--event .h-uppercase, .results-table__col--event .boldest, .results-table__col--event span")
                date_text = ' '.join([el.text for el in date_elements]).strip()
                
                # Extract venue details
                venue_element = event.find_element(By.CLASS_NAME, "venue-info-container")
                venue_text = venue_element.text.strip()

                if href and title:
                    events_data.append({
                        "URL": href,
                        "Title": title,
                        "Date": date_text,
                        "Venue": venue_text
                    })
            except Exception as e:
                print(f"Error retrieving event data: {e}")

        # Save the event data to a CSV file
        with open('events_data.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["URL", "Title", "Date", "Venue"])
            writer.writeheader()
            for event_data in events_data:
                writer.writerow(event_data)

    print("sleep")
    time.sleep(20)

finally:
    # Close the WebDriver properly
    try:
        driver.quit()
    except Exception as e:
        print(f"Error while closing the driver: {e}")
