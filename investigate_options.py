# %%
import pandas as pd
import json
from tqdm import tqdm
import numpy as np
import pandas as pd
import json
import datetime as dt

import options_orig
import __wps_pandas.rules as rules


old = pd.read_pickle("old_options.pkl")
new = pd.read_pickle("new_options.pkl")
EARNINGS = pd.read_pickle("earnings.pkl")


# Set selection parameters
safe_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                       'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.95, 'annual_ptnl_ret_lim': 0.01, \
                       'prob_touch_lim': 0.9, 'label': 'safe'}
mod_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                      'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.90, 'annual_ptnl_ret_lim': 0.01, \
                      'prob_touch_lim': 0.9, 'label': 'moderate'}
risky_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                        'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.80, 'annual_ptnl_ret_lim': 0.01, \
                        'prob_touch_lim': 0.9, 'label': 'risky'}

def test_earnings(options_class):
    valid = []
    for i, row in options_class.iterrows():

        try:
            ed = options_orig.next_earnings_date(row.underlying).date()
            delta = ed - dt.datetime.today().date() #compute dates from today to earnings date

            #if delta.days>0: # Yahoo may report earning dates that just passed.
            d_days = delta.days - row.daysToExpiration                

            if ( not (d_days <= 0) ):
                valid.append(row.underlying)
        except:
            continue
    
    return valid

def test_option_params(old_options_frame, params):
    data = {}
    for i, row in old_options_frame.iterrows():
        item = row['Symbol']
        data_entry = json.loads(row['Json'])
        data.update({item: data_entry})
        
    Option_Data = pd.DataFrame(data)

    output = []
    for Symbol in list(Option_Data.columns):
        result = options_orig.processing(
            Symbol,
            Option_Data,
            params,
            "PUT"
        )

        if not result.empty:
            output.append(result)
    
    return pd.concat(output)




def annotate_options(options, earnings, risk):

    '''
    load safe params
    '''
    if   risk == "safe"    : params = rules.safe_put_map
    elif risk == "moderate": params = rules.moderate_put_map
    else                   : params = rules.risky_put_map

    '''
    ANNOTATE ["moneyness", "percentAnnualPtnlReturn"]
    '''
    options['moneyness'] = options.strikePrice - options.underlyingPrice                        # Lloyd: correct name is intrinsic_value
    options['moneyness'] = options.moneyness.apply(lambda cell : cell if cell > 0 else 0)
    options['percentAnnualPtnlReturn'] = (options.bid - options.moneyness)        \
                                            / (options.strikePrice - options.bid) \
                                            * 365 / options.daysToExpiration      \
                                            * 100

    '''
    GENERIC REQUIREMENTS
    '''
    options = options[ options.daysToExpiration > params['min_daysToExpiration'] ]
    options = options[ options.daysToExpiration < params['max_daysToExpiration'] ]
    options = options[ options.bid >= params['min_bid'] ]
    # options = options[ options.bid < params['max_bid'] ]
    options = options[ options.totalVolume >= params['min_totalVolume'] ]

    # options["percentOutOfTheMoney"] = (options["underlyingPrice"] - options["strikePrice"]) / options["underlyingPrice"]
    options = options[ (-1 * options.percentInTheMoney) >= params['min_percentOutOfTheMoney'] ]   # Lloyd : This was negated


    options["delta"] = 1 + options.delta.astype(float)
    options = options[ options.delta >= params['min_probabilityOutOfTheMoney'] ]  # MOST IMPORTANT

    '''
    PUT REQUIREMENETS
    # no -2 for perc_annual_return
    '''
    options = options[ options.putCall == "PUT"]
    options = options[ options.percentAnnualPtnlReturn > params['max_percentAnnualPtnlReturn'] ]    # ProfLiu: Discarded as redundant
    options = options[ options.delta.astype(float) * -2 <= params['max_probabilityTouch'] ]          # ProfLiu: Discarded as redundant

    # '''
    # ANNOTATE EARNINGS
    # '''
    # erng_frame = pd.read_pickle("earnings.pkl")
    # erng_frame['date'] = pd.to_datetime(erng_frame['date'], format='%Y%m%d %H:%M:%S')
    # erng_frame['date'] = erng_frame['date'].dt.date
    # erng_frame['today'] = dt.date.today()
    # erng_frame['daysToEarnings']      = (erng_frame['date'] - erng_frame['today']).dt.days        # delta


    # '''
    # EARNINGS + EXPIRATION REQUIREMENETS
    # '''
    # erngs_map = dict( erng_frame['daysToEarnings'] )
    # options['daysToEarnings'] = options.underlying.apply(lambda symbol: erngs_map[symbol])
    # options['daysBtwnExprErngs'] = options['daysToEarnings'] - options['daysToExpiration'] # d_days
    # options = options[ options.daysBtwnExprErngs > 0 ]

    """
    ANNOTATE RISK
    """
    if   risk == "safe"    : options['Risk'] = "safe"
    elif risk == "moderate": options['Risk'] = "moderate"
    else                   : options['Risk'] = "risky"

    return options


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
print("\n[+] Rating Options ...")
safe_options = annotate_options(new, EARNINGS, "safe")
moderate_options = annotate_options(new, EARNINGS, "moderate")
risky_options = annotate_options(new, EARNINGS, "risky")

new_safe     = list( safe_options['symbol'] )
new_moderate = list( moderate_options['symbol'] )
new_risky    = list( risky_options['symbol'] )

old_safe     = list( test_option_params(old, safe_put_parameters).index )
old_moderate = list( test_option_params(old, mod_put_parameters).index )
old_risky    = list( test_option_params(old, risky_put_parameters).index )



if len(new_safe) == len(old_safe):
    print(f'\u2713 {len(new_safe)} = {len(old_safe)} [Safe]')
else: 
    print(f'\u274c {len(new_safe) - len(old_safe)} missing... [Safe]')

if len(old_moderate) == len(new_moderate):
    print(f'\u2713 {len(old_moderate)} = {len(new_moderate)} [Moderate]')
else: 
    print(f'\u274c {len(old_moderate) - len(new_moderate)} missing... [Moderate]')

if len(old_risky) == len(new_risky):
    print(f'\u2713 {len(old_risky)} = {len(new_risky)} [Risky]')
else: 
    print(f'\u274c {len(old_risky) - len(new_risky)} missing... [Risky]')


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
print("\n[+] Matching Earnings ... ")
#TEST older function
options = annotate_options(new, EARNINGS, "risky")
#ANNOTATE EARNINGS
erng_frame = pd.read_pickle("earnings.pkl")
erng_frame['date'] = pd.to_datetime(erng_frame['date'], format='%Y%m%d %H:%M:%S')
erng_frame['date'] = erng_frame['date'].dt.date
erng_frame['today'] = dt.date.today()
erng_frame['daysToEarnings']      = (erng_frame['date'] - erng_frame['today']).dt.days        # delta
#EARNINGS + EXPIRATION REQUIREMENETS
erngs_map = dict( erng_frame['daysToEarnings'] )
options['daysToEarnings'] = options.underlying.apply(lambda symbol: erngs_map[symbol])
options['daysBtwnExprErngs'] = options['daysToEarnings'] - options['daysToExpiration'] # d_days
options = options[ options.daysBtwnExprErngs > 0 ]

#TEST earnings same
new_earn_symbols = list( options.symbol )
old_earn_symbols = test_earnings(risky_options)

if len(new_earn_symbols) == len(options):
    print(f'\u2713 {len(new_earn_symbols)} = {len(old_earn_symbols)} [Earnings]\n')
else: 
    print(f'\u274c {len(new_earn_symbols) - len(old_earn_symbols)} missing... [Earnings]\n')

