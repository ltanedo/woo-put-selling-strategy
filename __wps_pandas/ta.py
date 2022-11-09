import numpy as np
import pandas as pd
import math

from . import utils
from . import rate

def macd(data_simple):

        data_simple['26 ema']      = data_simple.Close.ewm(span=26).mean()
        data_simple['12 ema']      = data_simple.Close.ewm(span=12).mean()
        data_simple['MACD']        = data_simple['12 ema'] - data_simple['26 ema']
        data_simple['signal_line'] = data_simple.MACD.ewm(span=9).mean()
        data_simple['hist']        = data_simple['MACD']-data_simple['signal_line']
        data_simple['MACD_Slope']  = data_simple['MACD'] - data_simple['MACD'].shift(periods=1)
        data_simple['MACD_Slope']  = data_simple['MACD_Slope'].apply(lambda x: 1 if x > 0 else -1)
        # data_simple['MACD_Rating'] = data_simple.apply(lambda x: rate.macd(x['MACD'], x['signal_line']), axis=1)

        return data_simple

def rate_macd(data_simple):

        data_simple['MACD_Rating'] = data_simple.apply(lambda x: rate.macd(x['MACD'], x['signal_line']), axis=1)

        return data_simple\
                .drop(
                    columns=['26 ema','12 ema','MACD','signal_line','hist']
                )

def sma(data_simple):

    data_simple['20d'] =data_simple.Close.rolling(window =20, center = False).mean()
    data_simple['50d'] =data_simple.Close.rolling(window =50, center = False).mean()
    data_simple['200d']=data_simple.Close.rolling(window =200, center = False).mean()

    # data_simple['SMA_Rating'] = data_simple.apply(lambda x: rate.sma(x['Close'], x['50d'], x['200d']), axis=1)

    return data_simple

def rate_sma(data_simple):

    data_simple['SMA_Rating'] = data_simple.apply(lambda x: rate.sma(x['Close'], x['50d'], x['200d']), axis=1)

    return data_simple

def rsi(data_simple):

    delta             = data_simple.Close.diff()
    window            = 15
    up_days           = delta.copy()
    up_days[delta<=0] = 0.0
    down_days         = abs(delta.copy())
    down_days[delta>0]=0.0
    RS_up             = up_days.rolling(window).mean()
    RS_down           = down_days.rolling(window).mean()
    rsi               = 100-100/(1+RS_up/RS_down)

    data_simple["RSI"] = rsi
    # data_simple["RSI_Rating"] = data_simple["RSI"].apply(rate.rsi)

    return data_simple


def rsi_old(data_simple):

    n = 14

    rsi = 0
    index = len(data_simple.index)-1
    prices = data_simple['Close']
    
    deltas = np.diff(prices)
    #if index >360:
    #    seed = deltas[index-360 : index-360 + n+1]
    #else:
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n+1, len(prices)):
        delta = deltas[i-1]  # The diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    
    data_simple['RSI'] = rsi

    return data_simple

def rate_rsi(data_simple):

    data_simple["RSI_Rating"] = data_simple["RSI"].apply(rate.rsi)

    return data_simple

def rate_pnf(myData):

    #list1 stores the highest value of each x column by index
    #list2 stores the lowest value of each o column by index
    list1 = []
    list2 = []

    #current_trend stores the value of the most recent trend. we start off with x as default
    current_trend = 'x'

    numberofXBoxes = 1 # to get number of x boxes in all
    numberofOBoxes = 0 # to get number of o boxes in all

    #set box size according to price on day 1
    box_size = utils.updateBoxSize(myData["High"].iloc[0])

    #append price on day 1 to list1 as we stfart with x
    list1.append(math.floor(myData["High"].iloc[0]))

    current_trend = utils.pointAndFigureCreate(box_size, current_trend, list1, list2, myData, numberofXBoxes, numberofOBoxes)
    pattern_map = {
        'ret_val_triple_top'           : utils.continous_triple_top(current_trend,list1),
        'ret_val_triple_bottom'        : utils.continous_triple_bottom(current_trend,list2),
        'ret_val_double_top'           : utils.continous_double_top(current_trend,list1),
        'ret_val_double_bottom'        : utils.continous_double_bottom(current_trend,list2),
        'ret_val_quadruple_top'        : utils.continous_quadruple_top(current_trend,list1),
        'ret_val_quadruple_bottom'     : utils.continous_quadruple_bottom(current_trend,list2),
        'ret_val_spread_triple_top'    : utils.spread_triple_top(current_trend,list1),
        'ret_val_spread_triple_bottom' : utils.spread_triple_bottom(current_trend,list2)
    }

    support1, support2 = utils.get_support_levels(list2)
    resistance1, resistance2 = utils.get_resistance_levels(list1)

    rating = rate.pnf(pattern_map)

    myData["Support1"]    = np.nan
    myData["Support2"]    = np.nan
    myData["Resistance1"] = np.nan
    myData["Resistance2"] = np.nan
    myData["PNF_Rating"]  = np.nan

    myData.loc[myData.index[-1], "Support1"]    = support1
    myData.loc[myData.index[-1], "Support2"]    = support2
    myData.loc[myData.index[-1], "Resistance1"] = resistance1
    myData.loc[myData.index[-1], "Resistance2"] = resistance2
    myData.loc[myData.index[-1], "PNF_Rating"]  = rating

    return myData

def apply_requirements(bars200):

    last_row = bars200.loc[bars200.index[-1]]
    print(last_row)

    if last_row['MACD_Rating'] == 1               \
      and last_row['MACD_Slope'] == 1             \
      and last_row['SMA_Rating'] == 1             \
      and last_row['RSI_Rating'] == 1             :
    #   and last_row['PNF_Rating'] in ['a','b','c']:

        return bars200.tail(1)
    else:
        return pd.DataFrame()
