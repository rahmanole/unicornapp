import requests
import datetime
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys

def scrape_quotes(url):
# Set up the Selenium WebDriver
  driver = webdriver.Chrome() # Make sure you have chromedriver installed and in your PATH
  driver.get(url)

def web_content_div(web_content,class_path):
    web_content_div = web_content.find_all("div",{"class":class_path})

def real_time_top_gainers():
    url = "https://www.webull.com/quote/us/gainers"
    try:
        r = requests.get(url)
        web_content = bs(r.text,"lxml")
        texts = web_content_div()
    except Exception as e:
        print(e)
        raise Exception(e)
    
if __name__=="__main__":
    # url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo'
    # r = requests.get(url)
    # data = r.json()

    # print(data)
    # real_time_top_gainers()
    driver = webdriver.Chrome() # Make sure you have chromedriver installed and in your PATH
    driver.get("https://www.webull.com/quote/us/gainers/1d")
    last_height = driver.execute_script("return document.body.scrollHeight")

    for scroll_count in range(4):  # Assuming there are 5 scroll events in total
        # Scroll down using JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        # Wait for the dynamically loaded content to appear
        initial_html = driver.page_source
        initial_soup = bs(initial_html, 'html.parser')
        initial_stocks = initial_soup.find_all('div', class_='table-row')
        for stock in initial_stocks:
            name_ticker = stock.find_all('div','table-cell')[1].find_all("p")
            name = name_ticker[1].text
            ticker = name_ticker[2].text
            other_info = stock.find_all('span')
            _,cng,last_price,volume,mkt_cap=[i.text for i in other_info]
            print(f"{ticker:<6} {cng:<8} {last_price:<4} {volume:<4} {mkt_cap:<6} {name:<30} ")
        print("")
        print(f"***************{scroll_count}***************")