import pandas as pd 
import numpy as np
import math
import sys

support1 = 0
support2 = 0
resistance1 = 0
resistance2 = 0

#SMA rating
def SMA_rating(data_simple):

    data_simple['20d'] = np.round(data_simple.Close.rolling(window =20, center = False).mean(),2)
    data_simple['50d'] = np.round(data_simple.Close.rolling(window =50, center = False).mean(),2)
    data_simple['200d'] = np.round(data_simple.Close.rolling(window =200, center = False).mean(),2)
    
#     start_date = date(1998,1,2)
#     yesterday = (datetime.now() - timedelta(days=1))
#     end_date = date(yesterday.year,yesterday.month,yesterday.day)
    sma_rating = 0
    index = len(data_simple.index)-1
    if data_simple['Close'][index] > data_simple['50d'][index] > data_simple['200d'][index]:
        sma_rating=1
    elif data_simple['50d'][index] > data_simple['Close'][index]> data_simple['200d'][index]:
        sma_rating=2
    elif data_simple['50d'][index] > data_simple['200d'][index] > data_simple['Close'][index]:
        sma_rating=3
    elif data_simple['200d'][index] > data_simple['50d'][index] > data_simple['Close'][index]:
        sma_rating=4
    elif data_simple['200d'][index]> data_simple['Close'][index] > data_simple['50d'][index]:
        sma_rating=5
    elif data_simple['Close'][index] > data_simple['200d'][index] > data_simple['50d'][index]:
        sma_rating=6
    elif data_simple['Close'][index] > data_simple['50d'][index] > data_simple['200d'][index]:
        sma_rating=7
    return sma_rating

def MACD_rating(data_simple):
        data_simple['26 ema']=data_simple.Close.ewm(span=26).mean()
        data_simple['12 ema']=data_simple.Close.ewm(span=12).mean()
        data_simple['MACD'] = (data_simple['12 ema'] - data_simple['26 ema'])
        data_simple['signal_line']=data_simple.MACD.ewm(span=9).mean()
        data_simple['hist']=(data_simple['MACD']-data_simple['signal_line'])
        
        #MACD rating
        index = len(data_simple)-1
        slope = 0
        macd_rating = 0
        
        #print("Current MACD:",data_simple['MACD'][index])
        #print("Previous day MACD",data_simple['MACD'][index-1])
        
        #Condition for the slope
        if((data_simple['MACD'][index] - data_simple['MACD'][index-1])>0):
            slope = 1
        elif((data_simple['MACD'][index] - data_simple['MACD'][index-1])<0):
            slope = -1
            
        #Condition for the MACD rating
        if data_simple['MACD'][index] > data_simple['signal_line'][index] and data_simple['signal_line'][index] > 0:
            macd_rating=1
        elif data_simple['signal_line'][index] > data_simple['MACD'][index] and data_simple['MACD'][index] > 0:
            macd_rating=2
        elif data_simple['MACD'][index] < 0 and 0 < data_simple['signal_line'][index]:
            macd_rating=3
        elif data_simple['MACD'][index] < data_simple['signal_line'][index] and data_simple['signal_line'][index]< 0:
            macd_rating=4
        elif data_simple['signal_line'][index] < data_simple['MACD'][index] and data_simple['MACD'][index] < 0:
            macd_rating=5
        elif data_simple['MACD'][index] > 0 and 0 > data_simple['signal_line'][index]:
            macd_rating=6
        return macd_rating,slope

def daily_rsi_values(stock, data_simple, n=14):
#     ts = TechIndicators(key='ZSAE2CXUXOLE67NH', output_format='pandas',indexing_type='date')
#     try:
#         data, meta_data = ts.get_rsi(symbol=stock_para, interval='daily') # interval = '1min'
#         print('{}\'s RSI is {}.'.format(stock_para,data['RSI'][-2]))
#     except:
#         return -1
#     if(data.empty):
#         return -1
#     if(data['RSI'][-1]>70 or data['RSI'][-1]<30):
#         ret_val = -1
#     else:
#         ret_val = 1
#     return ret_val
   
    #def RSI(self, prices, n=14):
    
    rsi = 0
    index = len(data_simple.index)-1
    prices = data_simple['Close']
    symbol = stock
    #print(symbol)
    
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
            
    if(rsi[-1] == False):
        print('RSI computing error found.')
        return -1
    elif(rsi[-1]>70 or rsi[-1]<30):
        #print('{}\'s RSI is {}.'.format(symbol,rsi[-1]))
        rsi_rating = -1
    else:
        rsi_rating = 1
        #print('{}\'s RSI is {}.'.format(symbol,rsi[-1]))

    return rsi_rating


# 3/5/2020 Charlie suggests this label was wrong. He recommends RSI>40 for 1, and others for -1.

## Global Declarations

reversal = 3 #reversal amount set to 3 as default

# (price range, box size)
#function will provide box sizes according to traditional method
box_ranges = [(.25,.0625),
              (1,.125), 
              (5,.25),
              (20,.5),
              (100,1),
              (200,2),
              (500,4),
              (1000,5),
              (25000,50),
              (sys.maxsize,500)]

#to check and update box size according to current value of stock
def updateBoxSize(price):
    for i in range (len(box_ranges)):
        if price < box_ranges[i][0]: #Zhen: Does it return multiple values?
            return box_ranges[i][1] 
    return None


#using alpha_vantage because quandl gives only data till March 2018

#if current trend is x update x column appropriately or move to o column if needed
def updateX(item, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes):
    box_size = updateBoxSize(list1[-1])
   # print(math.floor(item["High"]))
    if ( math.floor(item["High"]) >= list1[-1]+box_size ):
        list1[-1] = math.floor(item["High"])
    #   print("Updated the x value to:"+str(list1[-1]))
        numberofXBoxes += 1
    elif ( math.ceil(item["Low"]) <= list1[-1]-reversal*box_size):
        list2.append(math.ceil(item["Low"]))
    #   print("Updated the o value to:"+str(list2[-1]))
        current_trend = 'o'
        numberofOBoxes += 1
    return current_trend

#if current trend is o update o column appropriately or move to x column if needed
def updateO(item, list1, list2, box_size, reversal, current_trend,  numberofXBoxes, numberofOBoxes):
    box_size = updateBoxSize(list2[-1])
    if ( math.ceil(item["Low"]) <= list2[-1]-box_size ):
        list2[-1] = math.ceil(item["Low"])
#        print("Updated the o value to:"+str(list2[-1]))
        numberofOBoxes += 1
    elif ( math.floor(item["High"]) >= list2[-1]+reversal*box_size):
        list1.append(math.floor(item["High"]))
 #       print("Updated the x value to:"+str(list1[-1]))
        current_trend = 'x'
        numberofXBoxes += 1
    return current_trend

#create the point and figure from scratch

def pointAndFigureCreate(box_size,current_trend, list1, list2, stockhilowdata, numberofXBoxes, numberofOBoxes):
    #iterate over each date for the stock and create x or o columns
    for index,row in stockhilowdata.iloc[0:].iterrows():
        if current_trend == 'x':
        #   print("The price is:"+str(row["High"]))
            current_trend = updateX(row, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes)
        elif current_trend=='o':
            current_trend = updateO(row, list1, list2, box_size, reversal, current_trend, numberofXBoxes, numberofOBoxes)
          #  print("The price is:"+str(row["Low"]))
    return current_trend

#check for a continous triple top pattern
def continous_triple_top(current_trend, list1):
    if(len(list1)<3):
        return -1
    ret_val = 0
    if current_trend == 'x':
        if((list1[-1]> list1[-2]) and (list1[-2] == list1[-3])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val
        
#check for a continous triple bottom pattern
def continous_triple_bottom(current_trend, list2):
    if(len(list2)<3):
        return -1
    ret_val = 0
    if current_trend == 'o':
        if((list2[-1] < list2[-2]) and (list2[-2] == list2[-3])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

#check for a continous double top pattern
def continous_double_top(current_trend, list1):
    if(len(list1)<2):
        return -1
    ret_val = 0
    if current_trend=='x':
        if(list1[-1]> list1[-2]):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

#check for a continous double bottom pattern
def continous_double_bottom(current_trend, list2):
    if(len(list2)<2):
        return -1
    ret_val = 0
    if current_trend == 'o':
        if(list2[-1]< list2[-2]):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def continous_quadruple_top(current_trend, list1):
    if(len(list1)<4):
        return -1
    ret_val = 0
    if current_trend == 'x' and len(list1)>3:
        if((list1[-1] > list1[-2]) and (list1[-2] == list1[-3] == list1[-4])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def continous_quadruple_bottom(current_trend, list2):
    if(len(list2)<4):
        return -1
    ret_val = 0
    if current_trend == 'o' and len(list2)>3:
        if((list2[-1] < list2[-2]) and (list2[-2] == list2[-3] == list2[-4])):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

import itertools
def spread_triple_top(current_trend, list1):
    ret_val = -1
    if current_trend == 'x' and len(list1)>7:
        iterprev = 0
        resistance = 0
        notstt = True
        for iter in list1[-2:-7:1]:
            if iterprev == iter:
                resistance = iter
                notstt = False
            if resistance!=0 and iter > resistance:
                notstt = True
                break
            iterprev = iter
        if(notstt == False):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def spread_triple_bottom(current_trend, list2):

    # # Added : global resistance
    # global resistance

    ret_val = -1
    if current_trend == 'o' and len(list2)>7:
        iterprev = 0
        support = 0
        notstb = True
        for iter in list2[-2:-7:1]:
            if iterprev == iter:
                support = iter
                notstb = False
            if support!=0 and iter<resistance:
                notstb = True
                break
            iterprev = iter
        if(notstb == False):
            ret_val = 1
        else:
            ret_val = -1
    return ret_val

def get_support_levels(list2):
    if(len(list2)>=2):
        return list2[-1],list2[-2]
    elif (len(list2)==1):
        return list2[-1],0
    else:
        return 0,0

def get_resistance_levels(list1):
    if(len(list1)>=2):
        return list1[-1],list1[-2]
    elif (len(list1)==1):
        return list1[-1],0
    else:
        return 0,0
    
    
def PnFMain(myData):
    #list1 stores the highest value of each x column by index
    #list2 stores the lowest value of each o column by index
    list1 = []
    list2 = []

    #current_trend stores the value of the most recent trend. we start off with x as default
    current_trend = 'x'

    numberofXBoxes = 1 # to get number of x boxes in all
    numberofOBoxes = 0 # to get number of o boxes in all

    #set box size according to price on day 1
    box_size = updateBoxSize(myData["High"].iloc[0])
    #append price on day 1 to list1 as we stfart with x
    list1.append(math.floor(myData["High"].iloc[0]))
    current_trend = pointAndFigureCreate(box_size, current_trend, list1, list2, myData, numberofXBoxes, numberofOBoxes)
    ret_val_triple_top = continous_triple_top(current_trend,list1)
    ret_val_triple_bottom = continous_triple_bottom(current_trend,list2)
    ret_val_double_top = continous_double_top(current_trend,list1)
    ret_val_double_bottom = continous_double_bottom(current_trend,list2)
    ret_val_quadruple_top = continous_quadruple_top(current_trend,list1)
    ret_val_quadruple_bottom = continous_quadruple_bottom(current_trend,list2)
    ret_val_spread_triple_top = spread_triple_top(current_trend,list1)
    ret_val_spread_triple_bottom = spread_triple_bottom(current_trend,list2)
    
    # global support1
    # global support2
    # global resistance1
    # global resistance2
    
    # support1,support2 = get_support_levels(list2)
    # resistance1,resistance2 = get_resistance_levels(list1)
    
    if ret_val_quadruple_top == 1:
        return 'a'
    elif ret_val_triple_top == 1:
        return 'b'
    elif ret_val_double_top == 1:
        return 'c'
    elif ret_val_quadruple_bottom == 1:
        return 'd'
    elif ret_val_triple_bottom == 1:
        return 'e'
    elif ret_val_double_bottom == 1:
        return 'f'
    else:
        return np.nan
    