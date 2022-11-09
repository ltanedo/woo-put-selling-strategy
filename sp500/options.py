import requests
import pandas as pd
import time

from tqdm import tqdm

API_KEY = None

def chain_condenser(data):

    l_records = []

    for expiration in data["putExpDateMap"].keys():
        for strike in data["putExpDateMap"][expiration]:

            keys = [
                "putCall","symbol","exchangeName","bid","ask","last","bidSize",
                "askSize", "lastSize","highPrice","lowPrice","openPrice","closePrice",
                "totalVolume","tradeTimeInLong","quoteTimeInLong",
                "volatility","delta","gamma","theta","vega","rho","openInterest",
                "strikePrice","expirationDate","daysToExpiration","expirationType",
                "percentChange","intrinsicValue","inTheMoney", "pennyPilot"
            ]

            record = data["putExpDateMap"][expiration][strike][0]
            record = { key: record[key] for key in keys }

            record["isDelayed"]       = data["isDelayed"]
            record["interestRate"]    = data["interestRate"]
            record["underlying"]      = data["symbol"]
            record["underlyingPrice"] = data["underlyingPrice"]

            percentInTheMoney = (record["strikePrice"] - data["underlyingPrice"]) / data["underlyingPrice"] * 100
            record["percentInTheMoney"] = percentInTheMoney if record["putCall"] == "PUT" else (-1 * percentInTheMoney)
            record["collateral"] = record['last'] * 100

            l_records.append(record)

            # TESTIT: view first iteration
            # print(record)
            # quit()
    
    for expiration in data["callExpDateMap"].keys():
        for strike in data["callExpDateMap"][expiration]:

            keys = [
                "putCall","symbol","exchangeName","bid","ask","last","bidSize",
                "askSize", "lastSize","highPrice","lowPrice","openPrice","closePrice",
                "totalVolume","tradeTimeInLong","quoteTimeInLong",
                "volatility","delta","gamma","theta","vega","rho","openInterest",
                "strikePrice","expirationDate","daysToExpiration","expirationType",
                "percentChange","intrinsicValue","inTheMoney", "pennyPilot"
            ]

            

            record = data["callExpDateMap"][expiration][strike][0]
            record = { key: record[key] for key in keys }

            record["isDelayed"]       = data["isDelayed"]
            record["interestRate"]    = data["interestRate"]
            record["underlying"]      = data["symbol"]
            record["underlyingPrice"] = data["underlyingPrice"]

            percentInTheMoney = (record["strikePrice"] - data["underlyingPrice"]) / data["underlyingPrice"] * 100
            record["percentInTheMoney"] = percentInTheMoney if record["putCall"] == "PUT" else (-1 * percentInTheMoney)
            record["collateral"] = record['last'] * 100

            l_records.append(record)

            # TESTIT: view first iteration
            # print(record)
            # quit()

    return l_records

def get_option_chain(symbol):
    resp = requests.get(
        url = "https://api.tdameritrade.com/v1/marketdata/chains",
        params = {
            "apikey": API_KEY,
            "symbol": symbol
        },
    )

    return chain_condenser(resp.json())

def snapshot():
    symbols = list(pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', header = 0)[0]['Symbol'])

    chains = []
    for symbol in tqdm(symbols):
        try:
            chain = get_option_chain(symbol)
            chains += (chain)
            time.sleep(1)

        except Exception as e:
            print(e)
            None

    return pd.DataFrame(chains)
