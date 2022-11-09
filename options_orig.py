import json
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime  
from datetime import timedelta
from datetime import datetime, timedelta, date


from tqdm import tqdm

import numpy as np


# Following code does the filtering of the options data based on our chosen parameters
def processing(symbol, Option_Data, params, call_or_put):
    data = Option_Data[symbol]
    agg_data = {}
    date_keys = []
    for (k,v) in data[0].items():
        date_keys.append([k,list(v.keys())])
        agg_data[k] = v
        
    #If there is no data regarding some symbol in API then just return an empty dataframe
    if not date_keys:
        return pd.DataFrame()
        
    target_list = []
    stock_price = data[1]
    
    if call_or_put == "CALL":
        for i in range(0,len(date_keys)):
            for j in range(0, len(date_keys[i][1])):
                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'] < params['days_min'] or agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'] > params['days_max']: # Days to Expiration Requirement!
                    continue
                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'] < params['bid_min']: # Min/Max Bid requirement!
                    continue
                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['totalVolume'] < params['min_vol']: # Min/Max Volume Requirement!
                    continue
                if (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - stock_price) / stock_price < params['%OTM_lim']: # Percent OTM Requirement!
                    continue
                if 1 - agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta'] < params['prob_OTM_lim']: # Prob OTM Requirement!
                    continue
                support = 0
                
                # construct a dictionary object characteristics we want and append to list
                target = {'stock': symbol,
                         'contract': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['symbol'],
                         'strike_price':agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'],
                         'stock_price':stock_price,
                         'days_to_exp':agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'],
                         'bid': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'],
                         'ask': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['ask'],
                         'last': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['last'],
                         'prob_OTM': 1 - agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta'],
                         '% OTM': (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - stock_price) / stock_price,
                         'cov_ret': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['mark']-((stock_price - agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'])/stock_price)*(365/agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration']),
                         'max_cov_ret': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['mark']+((agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - stock_price)/stock_price)*(365/agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration']),
                         'prob_touch': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta']*2,
                         'annual_return': (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['ask'] * 365 * 100)/((agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']) * (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'])),
                         'btwn_supports':support}
                target_list.append(target)
    elif call_or_put == "PUT":
        for i in range(0,len(date_keys)):
            for j in range(0, len(date_keys[i][1])):

                import math
                if math.isnan( float(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta']) ):
                    continue


                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'] < params['days_min'] or \
                agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'] > params['days_max']: # Days to Expiration Requirement!
                    continue

                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'] < params['bid_min']: # Min/Max Bid requirement!
                    continue

                if agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['totalVolume'] < params['min_vol']: # Min/Max Volume Requirement!
                    continue

                if (stock_price - agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']) / \
                stock_price < params['%OTM_lim']: 
                    # Percent OTM Requirement!
                    continue

                prob_otm = 1 + float(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta'])
                #print("The prob of OTM is", round(prob_otm, 2))
                #print("The otm limit is", params['prob_OTM_lim'])
                if prob_otm < params['prob_OTM_lim']: # Prob OTM Requirement!      + or -???
                    #print("The prob of OTM", round(prob_otm, 2))
                    continue
                
                if (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'] - \
                          max(0, (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - \
                            stock_price)))/(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']- \
                                           agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid']) * 365 * 100/\
                           agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'] < \
                            params['annual_ptnl_ret_lim']: # Covered return Requirement! 
                    continue
                
                if float(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta'])*(-2) > \
                  params['prob_touch_lim']: # Probability of touching parameter      + or - ???
                    continue
                



                support = 0

#Commented code checks for 24% annual return. If required in future
#                 value = (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid']*365*100)/(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']*agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'])
#                 if value<15:
#                     continue
    
                # Construct a dictionary object characteristics we want and append to list
                target = {'stock':symbol,
                         'contract':agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['symbol'],
                         'strike_price':agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'],
                         'stock_price':stock_price,
                         'days_to_exp':agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'],
                         'bid': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'],
                         'ask': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['ask'],
                         'last': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['last'],
                         'prob_OTM': 1 + float(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta']), # + or - ???
                         '% OTM': 1-agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']/stock_price,
                         'ptnl_ret': (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'] - \
                          max(0, (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - \
                            stock_price)))/(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']- \
                                           agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid']),
                         'annual_ptnl_ret': (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid'] - \
                          max(0, (agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice'] - \
                            stock_price)))/(agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['strikePrice']- \
                                           agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['bid']) * 365 * 100/\
                           agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['daysToExpiration'],

                         'prob_touch': agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta']*(-2),
                         'btwn_supports': support}# + or - ???
                
#                 print("The value of accepted delta",target['prob_OTM'])
                target_list.append(target)
    df = pd.DataFrame(target_list)
    if(df.empty):
        # print('Got empty')
        return df
    df = df.set_index('contract', drop = True)
    return df



# Following function returns price data for a stock which can be used to construct a P&F chart
# def return_candle_data(symbol):
#     candle_url = 'https://api.tdameritrade.com/v1/marketdata/'+symbol+'/pricehistory'
#     candle_header = {'Authorization': get_auth_token()}
#     # Vary the properties below depending on how often you want the data
#     # Ideally, we want to set up a web socket to continuously stream this data?
#     period_type = 'day'
#     period = 2
#     freq_type = 'minute'
#     freq = 1
#     candle_payload = {'periodType': period_type, 'period': period, 'frequencyType': freq_type, 'frequency': freq}
#     raw_candle_data = requests.get(candle_url, params = candle_payload, headers = candle_header).json()
#     df = pd.DataFrame(raw_candle_data['candles'])
#     return df

def next_earnings_date(symbol):
    # Use Yahoo Finance Earnings Calendar https://github.com/wenboyu2/yahoo-earnings-calendar
    return  EARNINGS[ EARNINGS.index == symbol].iloc[0]['date'] 

def report(stock_list, Option_Data, put_parameters):
    # Select by WOO ratings and earnings dates criteria
    
    df_top_five_all =  pd.DataFrame()
    
    d0 = date.today()
    
    for row in tqdm(stock_list.iterrows()):
        item = row[1]['Symbol']
        # supp1 = row[1]['Support1']
        # supp2 = row[1]['Support2']
        name = row[1]['Company Name']
        print(item, end=" ")
        df = processing(item, Option_Data, put_parameters, "PUT")
        if(not df.empty):
            df_top_five = df.sort_values(by=['annual_ptnl_ret'], ascending=False)
            df_top_five = df_top_five.head(5)
            df_top_five['company name'] = name
            if df_top_five_all.empty:
                df_top_five_all = df_top_five
            else:
                df_top_five_all = df_top_five_all.append(df_top_five)
        #time.sleep(5)
                
    if(not df_top_five_all.empty):
        df_top_five_all = df_top_five_all.sort_values(by=['btwn_supports','stock','annual_ptnl_ret'], ascending=[False,True,False])
        
        df_top_five_all['Days to Earnings'] = '!' # In case earnings date data is not avaialbe, avoid reporting the contracts.
        
        df_top_five_all['Risk level'] = put_parameters['label']
        
        for index, row in df_top_five_all.iterrows():
            
            try:
                ed = next_earnings_date(row['stock']).date()
                delta = ed - d0 #compute dates from today to earnings date
                #print(delta.days)
                print('The next earnings date of {} is {}.'.format(row['stock'],ed))
           
                #if delta.days>0: # Yahoo may report earning dates that just passed.
                d_days = delta.days - row['days_to_exp']                

                if (d_days <= 0):
                    df_top_five_all = df_top_five_all.drop(index, axis=0)
                else:
                    df_top_five_all.at[index, 'Days to Earnings']= delta.days
            except:
                print(f"{row['stock']}: Error happens in finding the next earnings data.")
                df_top_five_all = df_top_five_all.drop(index, axis=0)
                pass

    else:
        print("No contracts available in the {} criteria.".format(put_parameters['label']))
    
    return df_top_five_all    
               
        
    
        