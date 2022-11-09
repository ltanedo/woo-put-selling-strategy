import requests
import pandas as pd
import json
from tqdm import tqdm
import time
import numpy as np


from pandas.core.common import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

import config as cf
import sp500

def get_auth_token():
    auth_params = {'grant_type':'refresh_token', 'refresh_token':cf.refresh_token, 'client_id': cf.client_id}
    auth_api_url = 'https://api.tdameritrade.com/v1/oauth2/token'
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    data =  requests.post(auth_api_url, headers = headers, data=auth_params).json()
    #print(data)
    result = "Bearer "+ data['access_token']

    return result

# Following code will get the option chain data using the authorized token
# Parameters: call_or_put: 'CALL'/'PUT'; symbol: string with stock symbol from passed in stock list
def get_raw_option_data(call_or_put, symbol, TOKEN):
    url = 'https://api.tdameritrade.com/v1/marketdata/chains'
    strike_count = '100' #need to figure out how to get ALL or just use an arbitraliy huge num
    strategy = 'SINGLE'
    authorization_header = {'Authorization': TOKEN}
    pay = {'symbol':symbol,'strikeCount':strike_count , 'strategy':strategy}
    if call_or_put == "CALL":
        return [requests.get(url, params = pay, headers = authorization_header).json()['callExpDateMap'], 
                requests.get(url, params = pay, headers = authorization_header).json()['underlyingPrice']]
    elif call_or_put == "PUT":
        return [requests.get(url, params = pay, headers = authorization_header).json()['putExpDateMap'], requests.get(url, params = pay, headers = authorization_header).json()['underlyingPrice']]


def pack_options():
    
    sp500_symbols : list = list(
        pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            header = 0
        )[0]['Symbol']
    ) 

    TOKEN = get_auth_token()

    records = []
    for symbol in tqdm(sp500_symbols):
        
        option = get_raw_option_data('PUT', symbol, TOKEN)
        packed_option = {
            "Symbol" : symbol,
            "Json"   : json.dumps(option)
        }
        records.append(packed_option)

        time.sleep(1)
    
    options_snapshot = pd.DataFrame(records)
    options_snapshot.to_pickle('options_packed.pkl')

def other():
    sp500.options.API_KEY = 'R55GYMLKNWLTKHUS32UZB6N99XNBI5IG' #TODO: Please set key
    sp500.earnings.snapshot().to_pickle('earnings.pkl')
    # sp500.stocks.snapshot().to_pickle('stocks.pkl')
    sp500.options.snapshot().to_pickle('options.pkl')

def inspect():

    STOCKS         : pd = pd.read_pickle("stocks.pkl")
    PACKED_OPTIONS : pd = pd.read_pickle("options_packed.pkl")
    EARNINGS       : pd = pd.read_pickle("earnings.pkl")

    sp500_symbols : list = list(
        pd.read_html(
            'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
            header = 0
        )[0]['Symbol']
    ) 

    for symbol in tqdm(sp500_symbols):

        myData = STOCKS[ STOCKS.Symbol == "AAPL" ]
        myData['20d'] = np.round(myData.Close.rolling(window =20, center = False).mean(),2)
        myData['50d'] = np.round(myData.Close.rolling(window =50, center = False).mean(),2)
        myData['200d'] = np.round(myData.Close.rolling(window =200, center = False).mean(),2)

        option : dict = json.loads( PACKED_OPTIONS[ PACKED_OPTIONS["Symbol"] == symbol ]['Json'].iloc[0] )
        earnings = ( EARNINGS[ EARNINGS.index == symbol].iloc[0] )

        

        # get_all_data(symbol) > annotated df 20, 50, 200
        # get_raw_option_data(symbol) 
        # next_earning_date(symbol) > datetime.date

def next_earnings_date(symbol):
    # Use Yahoo Finance Earnings Calendar https://github.com/wenboyu2/yahoo-earnings-calendar
    from datetime import datetime
    from yahoo_earnings_calendar import YahooEarningsCalendar
    my_custom_delay_s = 0.5
    #try:
    yec = YahooEarningsCalendar(my_custom_delay_s)# Returns the next earnings date of BOX in Unix timestamp
    ts = yec.get_next_earnings_date(symbol)
    time.sleep(2)
    
    return datetime.fromtimestamp(ts)

def earn():
    from datetime import datetime
    from yahoo_earnings_calendar import YahooEarningsCalendar
    my_custom_delay_s = 0.5
    #try:
    yec = YahooEarningsCalendar(my_custom_delay_s)# Returns the next earnings date of BOX in Unix timestamp
    ts = yec.get_next_earnings_date('AAPL')
    print( datetime.fromtimestamp(ts) )

    EARNINGS       : pd = pd.read_pickle("earnings.pkl")
    earnings =  EARNINGS[ EARNINGS.index == "AAPL"].iloc[0]['date'] 
    print(earnings)

# earn()
# other()

# pack_options()
# other()
# inspect()
