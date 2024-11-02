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
import requests


def thousands_to_mln_bln(val):
    val = float(val)
    return str(round(val/(1000*1000),2))+"M" if val<999998888 else str(round(val/(1000*1000*1000),2))+"B"

def convert_to_pct(val):
    val = float(val)*100
    return round(val,2)

def get_from_webull(rankType:str="1d"):
    end_point = f"https://quotes-gw.webullfintech.com/api/wlas/ranking/topGainers?regionId=6&rankType={rankType}&pageIndex=1&pageSize=500"
    response = requests.get(end_point)
    data =  response.json()
    all_data = []
    for i in range(500):
        all_data.append(data["data"][i]["ticker"])
    return all_data

def get_sector_name(tickerId:int):
    end_point = f"https://quotes-gw.webullfintech.com/api/information/stock/brief?tickerId={tickerId}"
    response = requests.get(end_point)
    data =  response.json()
    return data["sectors"][0]["name"]

def filter_stocks(price:float=5.0,vol:float=1,mkt_cap:int=200):
    vol = vol*1000000
    mkt_cap = mkt_cap*1000000
    stocks = get_from_webull()
    df = pd.DataFrame(stocks)

    # columns
    # ['tickerId', 'exchangeId', 'type', 'secType', 'regionId', 'currencyId',
    #    'currencyCode', 'name', 'symbol', 'disSymbol', 'disExchangeCode',
    #    'exchangeCode', 'listStatus', 'template', 'derivativeSupport', 'isPTP',
    #    'isAdr', 'issuerRegionId', 'shariahFlag', 'overnightTradeFlag',
    #    'secType2', 'tradeTime', 'faTradeTime', 'status', 'close', 'change',
    #    'changeRatio', 'marketValue', 'volume', 'turnoverRate', 'regionName',
    #    'regionIsoCode', 'peTtm', 'timeZone', 'preClose', 'open', 'high', 'low',
    #    'vibrateRatio', 'change', 'pchRatio', 'pprice', 'amount']
    tmp_df = df.copy()
    tmp_df = tmp_df[["tickerId","disSymbol","changeRatio","pprice","volume","marketValue"]]
    tmp_df = tmp_df.dropna().reset_index()
    # tmp_df['pprice'].astype(float)
    # tmp_df['volume'].astype(float)
    # tmp_df['marketValue'].astype(float)
    filter_arg = (tmp_df["pprice"].values.astype(float)>price) * (tmp_df["volume"].values.astype(float)>vol) * (tmp_df["marketValue"].values.astype(float)>mkt_cap)
    tmp_df = tmp_df.loc[filter_arg].reset_index(drop=True)
    tmp_df["volume"] = tmp_df["volume"].map(lambda x: thousands_to_mln_bln(x))
    tmp_df["marketValue"] = tmp_df["marketValue"].map(lambda x: thousands_to_mln_bln(x))
    tmp_df["changeRatio"] = tmp_df["changeRatio"].map(lambda x: convert_to_pct(x))
    tmp_df["sector"] = tmp_df["tickerId"].map(lambda x: get_sector_name(x))
    tmp_df.drop(["tickerId"],axis=1,inplace=True)
    return tmp_df

if __name__ == "__main__":
    data = filter_stocks()
    data = get_from_webull()
    df = pd.DataFrame(data)
    print("")