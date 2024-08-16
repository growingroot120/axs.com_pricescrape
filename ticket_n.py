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
import multiprocessing as mp

# Disable logging
logging.getLogger('seleniumwire').setLevel(logging.CRITICAL)
logging.getLogger('WDM').setLevel(logging.CRITICAL)

def initialize_driver():
    ua = UserAgent()
    fake_user_agent = ua.random
    seleniumwire_options = {
        'proxy': {
            'http': 'http://Visabot1-rotate:Visa1234@p.webshare.io:80',
            'https': 'http://Visabot1-rotate:Visa1234@p.webshare.io:80',
            'no_proxy': 'localhost,127.0.0.1'
        },
        'ca_cert': 'ca.crt'
    }
    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument(f'user-agent={fake_user_agent}')
    chrome_options.add_argument('--log-level=3')
    return webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)

def process_urls(url_chunk):
    ticket_links, dates, titles, locations = [], [], [], []

    for url in url_chunk:
        driver = initialize_driver()
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "c-card__column2")))
            card_columns = driver.find_elements(By.CLASS_NAME, "c-card__column2")
            ticket_link = card_columns[0].find_element(By.TAG_NAME, "a").get_attribute("href") if card_columns else None
            event_info_table = driver.find_element(By.CLASS_NAME, "c-event-info__table")
            date_span = event_info_table.find_element(By.CLASS_NAME, "c-event-info__table-date")
            date_text = date_span.text.strip()
            title_div = event_info_table.find_element(By.CLASS_NAME, "c-marquee__headliner")
            title_text = title_div.text.strip()
            venue_div = event_info_table.find_element(By.CLASS_NAME, "c-event-info__venue")
            venue_name = venue_div.find_element(By.CLASS_NAME, "c-event-info__venue-name").text.strip()
            venue_city = venue_div.find_element(By.CLASS_NAME, "c-event-info__venue-city").text.strip()
            location_text = f"{venue_name}, {venue_city}"
        except Exception as e:
            print(f"Error extracting data: {e}")
            ticket_link, date_text, title_text, location_text = None, None, None, None
        finally:
            ticket_links.append(ticket_link)
            dates.append(date_text)
            titles.append(title_text)
            locations.append(location_text)
            driver.close()  # Ensure the driver is closed properly
            time.sleep(1)
        
    # Return results as a DataFrame
    return pd.DataFrame({'URL': url_chunk, 'Ticket URL': ticket_links, 'Date': dates, 'Title': titles, 'Location': locations})

def main():
    urls_df = pd.read_csv('links.csv')
    urls = urls_df['URL'].tolist()

    # Define number of processes (e.g., number of CPU cores)
    num_processes = mp.cpu_count()

    # Split URLs into chunks for each process
    url_chunks = [urls[i::num_processes] for i in range(num_processes)]

    # Create a pool of processes
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(process_urls, url_chunks)

    # Combine results from all processes
    final_df = pd.concat(results, ignore_index=True)

    # Save the final DataFrame to CSV
    final_df.to_csv('links_with_tickets.csv', index=False)
    print(final_df)

if __name__ == '__main__':
    main()
