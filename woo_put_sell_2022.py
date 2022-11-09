'''
Install required packages (Mac/Linux)
import subprocess
subprocess.run(["pip install -r requirements.txt"])
'''

#%% Import libraries ("data" is custom from me)
import sp500 as data
import pandas as pd
import os

data.options.API_KEY = '' #TODO: Please set key

#%% Check if pickle exists, else build data

stocks_file = "stocks_norgate.pkl"

stocks = pd.read_pickle(stocks_file) \
            if os.path.exists(stocks_file) \
                else data.stocks.snapshot()

options = pd.read_pickle("options.pkl") \
            if os.path.exists("options.pkl") \
                else data.options.snapshot()

earnings = pd.read_pickle("earnings.pkl") \
            if os.path.exists("earnings.pkl") \
                else data.earnings.snapshot()

sectors = pd.read_pickle("sectors.pkl") \
            if os.path.exists("sectors.pkl") \
                else data.sectors.snapshot()

#%% Cache data for future runs
stocks.to_pickle("stocks.pkl")
options.to_pickle("options.pkl")
earnings.to_pickle("earnings.pkl")
sectors.to_pickle("sectors.pkl")

#%% Run WPS_Strategy -> return recommendations df
import __wps_pandas as wps

rcmndts = wps.recommendations.snapshot(stocks, options, earnings, sectors,DEBUG=False)
rcmndts.to_csv("woo_put_sell_2022.csv")

# %%
res1 = pd.read_csv("woo_put_sell_2022.csv")
res2 = pd.read_csv("norgate_result.csv")

intersection = res2['contract'].isin(res1['symbol'])
print (f'[+] {len(rcmndts)} vs {len(res2[intersection])} [new vs old]')
print (f'[+] {len(res2[~intersection])} missing symbols...')

