import pandas as pd
import datetime as dt
import time
import requests

from tqdm import tqdm

from . import yfinance as yf

def snapshot():

    all_bars : list = []

    sp500_symbols : list = list(
        pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            header = 0
        )[0]['Symbol']
    )

    for symbol in tqdm(sp500_symbols):

        try:
            bars = yf.Ticker(symbol)\
                    .history(
                        end      = (dt.datetime.now().strftime("%Y-%m-%d")),
                        start    = (dt.datetime.now() - dt.timedelta(days=365)).strftime("%Y-%m-%d"),
                        interval = "1d"
                    )

            bars["Symbol"] = symbol
            bars = bars[:200]

        except:
            continue

        all_bars.append(bars)
        time.sleep(1)

    return pd.concat(all_bars)

def snapshot_norgate():

    import norgatedata
    priceadjust = norgatedata.StockPriceAdjustmentType.TOTALRETURN 
    padding_setting = norgatedata.PaddingType.NONE   
    timeseriesformat = 'pandas-dataframe'

    sp500_symbols : list = list(
        pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            header = 0
        )[0]['Symbol']
    ) 

    frames = []
    for symbol in tqdm(sp500_symbols):
        start_date = '2015-01-01' #ts = TimeSeries(key='ZSAE2CXUXOLE67NH', output_format='pandas',indexing_type='date')
        try:
            pricedata_dataframe = norgatedata.price_timeseries(
                        symbol,
                        stock_price_adjustment_setting = priceadjust,
                        padding_setting = padding_setting,
                        start_date = start_date,
                        format=timeseriesformat)
            # company_name = norgatedata.security_name(symbol)[:-7]

            pricedata_dataframe["Symbol"] = symbol
            frames.append(pricedata_dataframe)
        except:
            pd.DataFrame()

    dff = pd.concat(frames)

    return dff

def snapshot_nasdaq():
    sp500_symbols : list = list(
    pd.read_html(
        'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        header = 0
    )[0]['Symbol']
) 

    records = []
    for symbol in tqdm(sp500_symbols):

        today      = dt.datetime.now().date()
        last_year  = dt.date(today.year-1, today.month, today.day)

        resp = requests.get(
            url = f'https://api.nasdaq.com/api/quote/{symbol}/historical',
            params={
                'assetclass' : 'stocks',
                'fromdate' : str(last_year),
                'todate' : str(today),
                'limit' : '200'
            },
            headers={
                "accept"         : "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "origin"         : "https://www.nasdaq.com",
                "referer"        : "https://www.nasdaq.com/",
                "user-agent"     : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            },
            timeout=10
        )

        # print(resp.json()['data']['tradesTable']['rows'].keys())
        # quit()

        try:
            rows = resp.json()['data']['tradesTable']['rows']
            for row in reversed(rows):
                new_row = row 
                new_row["Symbol"] = symbol
                
                records.append(new_row)

        except Exception as e: 
            print(f"{symbol} : {e}")
            continue
            
        time.sleep(1)
    
    bars = pd.DataFrame(records)
    bars = bars.rename(
        columns={"date":"Date","close":"Close","volume":"Volume","open":"Open","high":"High","low":"Low"}
    )

    bars.Open  = bars['Open'].str.replace("$","").astype(float)
    bars.High  = bars['High'].str.replace("$","").astype(float)
    bars.Low   = bars['Low'].str.replace("$","").astype(float)
    bars.Close = bars['Close'].str.replace("$","").astype(float)

    bars = bars.set_index("Date")

    return bars