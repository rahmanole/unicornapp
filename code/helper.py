from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import undetected_chromedriver as uc
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import os
import json 
import shutil
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
from selenium.webdriver.chrome.options import Options as ChromeOptions
import yfinance as yf

def realtime_data(ticker):
    return yf.download(ticker, period="1d")

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
    time.sleep(0.1)

def save_html(driver, scroll_count):
    # Create a directory for saving HTML files if it doesn't exist
    if not os.path.exists('./saved_pages'):
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

def thousands_to_mln(val):
    unit = val[-1]
    val = float(val[:-1])
    return round(val/1000,3)if unit=="K" else val

def billion_to_mln(val):
    unit = val[-1]
    val = float(val[:-1])
    return val*1000 if "B"==unit else val

def get_stock_data(driver, scroll_count, filename='stock_data.csv'):
    top_300 = []
    soup = bs(driver.page_source, 'html.parser')
    stocks = soup.find_all('div', class_='table-row')
    # Write headers only if it's the first scroll
    if scroll_count == 1:
        headers = ['Ticker', 'Change', 'Price', 'Volume', 'Market Cap', 'Name', 'Scroll Count']    
    # Process each stock row
    for stock in stocks:
        name_ticker = stock.find_all('div', 'table-cell')[1].find_all("p")
        name = name_ticker[1].text if len(name_ticker) > 1 else "N/A"
        ticker = name_ticker[2].text if len(name_ticker) > 2 else "N/A"
        
        other_info = stock.find_all('span')
        if len(other_info) >= 4:
            tmp_dic = {}
            *_, cng, last_price, volume, mkt_cap = [i.text for i in other_info]
            # print(f"{ticker:<6} {cng:<8} {last_price:<8} {volume:<8} {mkt_cap:<8} {name:<30}")
            # Write the row to CSV
            tmp_dic["ticker"]=ticker,
            tmp_dic["cng"]=cng,
            tmp_dic["last_price"]=last_price,
            tmp_dic["volume"]=volume,
            tmp_dic["mkt_cap"]=mkt_cap,
            tmp_dic["name"]=name,
            top_300.append(tmp_dic)
    
    stocks = []
    for i in top_300:
        tmp = {}
        for k in i:
            if k=="volume":
                tmp[k] = str(thousands_to_mln(i[k][0]))+"M"
                continue
            tmp[k] = i[k][0]
        stocks.append(tmp)
    driver.quit()
    return stocks

def main():
    driver = chromeDriver()    
    driver.get("https://www.webull.com/quote/us/gainers")
    # driver.get("https://www.webull.com/quote/us/dropers")
    time.sleep(0.1)
    
    scroll_count = 0
    t1 = time.time()
    for i in range(10, 70, 10):
        scroll_count += 1
        
        xpath = f"(//div[@class='table-row table-row-hover'])[{i}]"
        scroll_to_element(driver, xpath)
        time.sleep(0.1)

        xpath_terms = "(//p[@aria-label='Terms Conditions'])[1]"
        scroll_to_element(driver, xpath_terms)
    print(f"Time taken for scrolling webpage: {time.time()-t1}")
    # save_html(driver, scroll_count)
    # driver.quit()
    return get_stock_data(driver, scroll_count)

def filter_stocks(price:float=5.0,vol:float=1,mkt_cap:int=200):
    stocks = main()
    df = pd.DataFrame(stocks)
    tmp_df = df.copy()
    tmp_df["last_price"] = tmp_df["last_price"].map(lambda x: float(x.replace(",","")))
    tmp_df["volume"] = tmp_df["volume"].map(lambda x: thousands_to_mln(x))
    tmp_df["mkt_cap"] = tmp_df["mkt_cap"].map(lambda x: billion_to_mln(x))
    filter_arg = (tmp_df["last_price"].values>price) * (tmp_df["volume"].values>vol) * (tmp_df["mkt_cap"].values>mkt_cap)
    df = df.loc[filter_arg].reset_index(drop=True)
    df.to_json('./results.json', orient='table')

def get_data(price:float=5.0,vol:float=1,mkt_cap:int=200,**kwargs):
    t1 = time.time()
    print("api call received")
    print(f"recevied values{price,vol,mkt_cap}")

    filter_stocks(price,vol,mkt_cap)
    print(f"Time taken to process whole api call: {time.time()-t1}")
    with open('./results.json', 'r') as f:
        data = json.load(f)
    return data["data"]

if __name__ == "__main__":
    data = get_data()
    df = pd.DataFrame(data)
    print("")
    realtime_data()