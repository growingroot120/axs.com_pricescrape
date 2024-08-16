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

# Disable logging
logging.getLogger('seleniumwire').setLevel(logging.CRITICAL)
logging.getLogger('WDM').setLevel(logging.CRITICAL)

def initialize_driver():
    ua = UserAgent()
    fake_user_agent = ua.random
    seleniumwire_options = {
        'proxy': {
            'http': 'http://ba13396172373555b0b863c3af19140ff78c3c78f7948ccf411c5406f3a876a76ef6202bb1c21b1bb63089312f289e5a:sier7c6x0xjw@proxy.oculus-proxy.com:31111',
            'https': 'http://ba13396172373555b0b863c3af19140ff78c3c78f7948ccf411c5406f3a876a76ef6202bb1c21b1bb63089312f289e5a:sier7c6x0xjw@proxy.oculus-proxy.com:31111',
            'no_proxy': 'localhost,127.0.0.1'
        },
        'ca_cert': 'ca.crt'
    }
    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximize")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument(f'user-agent={fake_user_agent}')
    chrome_options.add_argument('--log-level=3')
    return webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)

urls_df = pd.read_csv('links.csv')
urls = urls_df['URL'].tolist()

ticket_links, dates, titles, locations, check_status = [], [], [], [], []

for url in urls:
    driver = initialize_driver()
    try:
        driver.get(url)
        # time.sleep(25)
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
        location_text = f"{venue_name}, {venue_city} "
        check_status.append("Yes")
        print("Succeed:")
    except Exception as e:
        ticket_link, date_text, title_text, location_text = None, None, None, None
        check_status.append("Fail")
        # Print the current result
        print("Failed:")
    finally:
        ticket_links.append(ticket_link)
        dates.append(date_text)
        titles.append(title_text)
        locations.append(location_text)
        driver.close()  # Ensure the driver is closed properly
        time.sleep(1)

        # Update DataFrame after each URL is processed to monitor progress and catch issues early
        current_df = pd.DataFrame({'URL': urls[:len(ticket_links)], 'Ticket URL': ticket_links, 'Date': dates, 'Title': titles, 'Location': locations})
        current_df.to_csv('links_with_tickets.csv', index=False)
        check_df = pd.DataFrame({'URL': urls[:len(ticket_links)], 'Check' : check_status})
        check_df.to_csv('links_checked.csv', index=False)
        # Print the current result
        print(current_df.tail(1))
# # Final save of the updated DataFrame to the CSV file
# urls_df['Ticket URL'] = ticket_links
# urls_df['Date'] = dates
# urls_df['Title'] = titles
# urls_df['Location'] = locations
# urls_df.to_csv('links_with_tickets.csv', index=False)
