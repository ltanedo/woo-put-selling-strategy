# %%
import ta_orig 
import __wps_pandas.ta as ta
import __wps_pandas.rate as rate

import sp500

import pandas as pd
import numpy as np

from tqdm import tqdm

NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)


# %%
#
# MACD
# 
NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)
for symbol in sp500.stocks.symbols()[:]:

    bars = STOCKS[ STOCKS.Symbol == symbol ].tail(200)
    if len(bars) != 200: continue

    new_bars_macd = ta.macd(bars)
    new_bars_macd['MACD_Rating'] = bars.apply(lambda x: rate.macd(x['MACD'], x['signal_line']), axis=1)
    
    new_output = (
        new_bars_macd['MACD_Rating'].tail(1)[0],
        new_bars_macd['MACD_Slope'].tail(1)[0]
    )

    old_output = ta_orig.MACD_rating(bars)

    if (new_output == old_output):
        print('\u2713' + f' {symbol} [MACD]')
    else:
        print('\u274c' + f' {symbol} [MACD]')
        raise Exception("Not Equivalent")

    


# %%
#
# SMA
#  
NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)
for symbol in sp500.stocks.symbols()[:]:

    bars = STOCKS[ STOCKS.Symbol == symbol ].tail(200)
    if len(bars) != 200: continue

    new_output = ta.sma(bars)
    new_output = ta.rate_sma(bars)['SMA_Rating'].tail(1)[0]
    old_output = ta_orig.SMA_rating(bars)

    if (new_output == old_output):
        print('\u2713' + f' {symbol} [SMA]')
    else:
        print('\u274c' + f' {symbol} [SMA]')
        raise Exception("Not Equivalent")



# %%
#
# RSI
#  
import ta_orig 
import __wps_pandas.ta as ta
import __wps_pandas.rate as rate

NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)

for symbol in sp500.stocks.symbols()[:]:

    bars = STOCKS[ STOCKS.Symbol == symbol ].tail(200)
    if len(bars) != 200: continue

    new_output = ta.rsi_old(bars)
    new_output = ta.rate_rsi(bars)['RSI_Rating'].tail(1)[0]
    old_output = ta_orig.daily_rsi_values(symbol, bars)

    if (new_output == old_output):
        print('\u2713' + f' {symbol} [RSI]')
    else:
        print('\u274c' + f' {symbol} [RSI]')
        raise Exception("Not Equivalent")


# %%
#
# PnF
#
import ta_orig 
import __wps_pandas.ta as ta
import __wps_pandas.rate as rate

NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)

for symbol in sp500.stocks.symbols()[:]:

    bars = STOCKS[ STOCKS.Symbol == symbol ].tail(200)
    if len(bars) != 200: continue

    bars = ta.rate_pnf(bars)
    new_output = bars['PNF_Rating'].tail(1)[0]
    old_output = ta_orig.PnFMain(bars)
    
    if (new_output == old_output):
        print('\u2713' + f' {symbol} [PnF]')
    else:
        if ( np.isnan(new_output) and np.isnan(old_output) ):
            print('\u2713' + f' {symbol} [PnF]')
            continue

        print('\u274c' + f' {symbol} [PnF]')
        raise Exception("Not Equivalent")



# %%
#
# Stock Recommendations
# 
NAME   = "stocks_norgate.pkl"
STOCKS = pd.read_pickle(NAME)

valid = pd.DataFrame()
for symbol in tqdm(sp500.stocks.symbols()[:], desc = "[+] tesing annotations"):

    bars = STOCKS[ STOCKS.Symbol == symbol ].tail(200)
    if len(bars) != 200: continue

    bars = ta.macd(bars)
    bars['MACD_Rating'] = bars.apply(lambda x: rate.macd(x['MACD'], x['signal_line']), axis=1)
    MACD_Rating = bars['MACD_Rating'].tail(1)[0]
    MACD_Slope  = bars['MACD_Slope'].tail(1)[0]

    bars = ta.sma(bars)
    SMA_Rating = ta.rate_sma(bars)['SMA_Rating'].tail(1)[0]

    bars = ta.rsi_old(bars)
    RSI_Rating = ta.rate_rsi(bars)['RSI_Rating'].tail(1)[0]

    if MACD_Rating == 1 \
        and MACD_Slope == 1 \
            and SMA_Rating == 1 \
                and RSI_Rating == 1:
                    valid = pd.concat([valid, bars.tail(1)])

GOLD_OUTPUT = [
    'AMP','AJG','WRB','CBOE','NDAQ','COP','MRO','MPC','OXY','FTV','IEX','PWR','SNA','GWW','APD','MCK','GPC','MSI','PTC','CAG','MNST'
]

if set(GOLD_OUTPUT).issubset(set(valid['Symbol'])):
    print('\u2713' + f' {len(GOLD_OUTPUT)} match | {len(valid) - len(GOLD_OUTPUT)} unique')
else: 
    print('\u274c' + f' {len(valid) - len(GOLD_OUTPUT)} missing...')


