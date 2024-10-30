from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver import ActionChains
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import os

def chromeDriver():
    options = ChromeOptions()
    options.headless = False
    options.add_argument("--disable-notifications")
    options.add_argument("--incognito")
    options.headless = True
    driver = uc.Chrome(options=options)
    return driver

def scroll_to_element(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    time.sleep(2)

def save_html(driver, scroll_count):
    # Create a directory for saving HTML files if it doesn't exist
    if not os.path.exists('saved_pages'):
        os.makedirs('saved_pages')
    
    # Save the page source to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'saved_pages/webull_scroll_{scroll_count}_{timestamp}.html'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print(f"Saved HTML to: {filename}")

# def print_stock_data(html_content, scroll_count):
#     soup = bs(html_content, 'html.parser')
#     stocks = soup.find_all('div', class_='table-row')
    
#     print("\nStock Data after scroll {scroll_count}:")
#     print(f"{'Ticker':<6} {'Change':<8} {'Price':<8} {'Volume':<8} {'Mkt Cap':<8} {'Name':<30}")
#     print("-" * 70)
    
#     for stock in stocks:
#         name_ticker = stock.find_all('div', 'table-cell')[1].find_all("p")
#         name = name_ticker[1].text if len(name_ticker) > 1 else "N/A"
#         ticker = name_ticker[2].text if len(name_ticker) > 2 else "N/A"
        
#         other_info = stock.find_all('span')
#         if len(other_info) >= 4:
#             *_, cng, last_price, volume, mkt_cap = [i.text for i in other_info]
#             print(f"{ticker:<6} {cng:<8} {last_price:<8} {volume:<8} {mkt_cap:<8} {name:<30}")
    
#     print(f"\n{'*' * 20} Scroll {scroll_count} {'*' * 20}\n")

def print_stock_data(html_content, scroll_count, filename='stock_data.csv'):
    import csv
    from bs4 import BeautifulSoup as bs
    
    soup = bs(html_content, 'html.parser')
    stocks = soup.find_all('div', class_='table-row')
    
    # Open the CSV file in append mode if it exists, otherwise create it
    file_mode = 'a' if scroll_count > 1 else 'w'
    
    with open(filename, file_mode, newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write headers only if it's the first scroll
        if scroll_count == 1:
            headers = ['Ticker', 'Change', 'Price', 'Volume', 'Market Cap', 'Name', 'Scroll Count']
            csvwriter.writerow(headers)
        
        # Process each stock row
        for stock in stocks:
            name_ticker = stock.find_all('div', 'table-cell')[1].find_all("p")
            name = name_ticker[1].text if len(name_ticker) > 1 else "N/A"
            ticker = name_ticker[2].text if len(name_ticker) > 2 else "N/A"
            
            other_info = stock.find_all('span')
            if len(other_info) >= 4:
                *_, cng, last_price, volume, mkt_cap = [i.text for i in other_info]
                print(f"{ticker:<6} {cng:<8} {last_price:<8} {volume:<8} {mkt_cap:<8} {name:<30}")
                # Write the row to CSV
                csvwriter.writerow([
                    ticker,
                    cng,
                    last_price,
                    volume,
                    mkt_cap,
                    name,
                    scroll_count
                ])

def main():
    driver = chromeDriver()
    driver.get("https://www.webull.com/quote/us/gainers")
    time.sleep(2)
    
    scroll_count = 0
    for i in range(10, 70, 10):
        scroll_count += 1
        
        xpath = f"(//div[@class='table-row table-row-hover'])[{i}]"
        scroll_to_element(driver, xpath)
        time.sleep(5)

        xpath_terms = "(//p[@aria-label='Terms Conditions'])[1]"
        scroll_to_element(driver, xpath_terms)
    save_html(driver, scroll_count)
    print_stock_data(driver.page_source, scroll_count)
    

    
    input("Testing complete. Press Enter to exit.")
    driver.quit()

if __name__ == "__main__":

    main()
