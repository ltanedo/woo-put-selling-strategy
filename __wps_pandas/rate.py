import numpy as np

def macd(macd, signal):

    macd_rating = np.nan

    if macd > signal\
      and signal > 0:
        macd_rating=1

    elif signal > macd\
      and macd > 0:
        macd_rating=2

    elif macd < 0\
      and signal > 0:
        macd_rating=3

    elif macd < signal\
      and signal< 0:
        macd_rating=4

    elif signal < macd\
      and macd < 0:
        macd_rating=5

    elif macd > 0\
      and 0 > signal:
        macd_rating=6

    return macd_rating

def sma(close, sma50, sma200):

    sma_rating = np.nan

    if close > sma50 > sma200:
        sma_rating=1

    elif sma50 > close > sma200:
        sma_rating=2

    elif sma50 > sma200 > close:
        sma_rating=3

    elif sma200 > sma50 > close:
        sma_rating=4

    elif sma200 > close > sma50:
        sma_rating=5

    elif close > sma200 > sma50:
        sma_rating=6

    elif close > sma50 > sma200:
        sma_rating=7

    return sma_rating

def rsi(value):
    return 1 if (value > 30 and value < 70) else -1

def pnf(pattern_map):

        if   pattern_map['ret_val_quadruple_top'] == 1:
            return 'a'
        elif pattern_map['ret_val_triple_top'] == 1:
            return 'b'
        elif pattern_map['ret_val_double_top'] == 1:
            return 'c'
        elif pattern_map['ret_val_quadruple_bottom'] == 1:
            return 'd'
        elif pattern_map['ret_val_triple_bottom'] == 1:
            return 'e'
        elif pattern_map['ret_val_double_bottom'] == 1:
            return 'f'
        else:
            return np.nan
