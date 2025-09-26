from datetime import datetime
import time
import pandas as pd
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo  # Python 3.9+

def thousands_to_mln_bln(val):
    val = float(val)
    return str(round(val/(1000*1000),2))+"M" if val<999998888 else str(round(val/(1000*1000*1000),2))+"B"

def convert_to_pct(val):
    val = float(val)*100
    return round(val,2)

def get_from_webull(rankType):
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

def filter_stocks(ranktype="1d",price:float=5.0,vol:float=1,mkt_cap:int=200):
    vol = vol*1000000
    mkt_cap = mkt_cap*1000000
    stocks = get_from_webull(ranktype)
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
    # tmp_df["sector"] = tmp_df["tickerId"].map(lambda x: get_sector_name(x))
    tmp_df.drop(["tickerId"],axis=1,inplace=True)
    return tmp_df

# Function to create acronyms
def create_acronym(name):
    words = name.split()
    if len(words) == 1:  # single word → take first 4 chars
        return name[:4].upper()
    else:  # multi-word → take first letter of each word
        return ''.join(word[0].upper() for word in words if word[0].isalpha())

def get_rank_type(tz: str = "America/Chicago") -> str:
    now = datetime.now()
    """
    Returns one of: "preMarket", "1d", "afterMarket" based on local time in America/Chicago.
    
    Windows (inclusive of endpoints unless noted):
      - 03:00 – 08:29  => "preMarket"
      - 08:30 – 14:59  => "1d"
      - 15:00 – 02:59  => "afterMarket" (spans midnight)
    """
    tzinfo = ZoneInfo(tz)
    local_now = (now.astimezone(tzinfo) if now else datetime.now(tzinfo))
    t = local_now.time()

    pre_start, pre_end = time(3, 0), time(8, 29, 59)
    reg_start, reg_end = time(8, 30), time(14, 59, 59)
    # afterMarket is everything else (15:00–23:59:59 and 00:00–02:59:59)

    if pre_start <= t <= pre_end:
        return ["Pre Market","Day","After Market"]
    if reg_start <= t <= reg_end:
        return ["Day","Pre Market","After Market"]
    return ["After Market","Day","Pre Market"]

if __name__ == "__main__":
    data = filter_stocks()
    data = get_from_webull()
    df = pd.DataFrame(data)
    print("")