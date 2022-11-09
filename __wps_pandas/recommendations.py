import pandas   as pd
import datetime as dt
from tqdm import tqdm

from . import ta
from . import rate
from . import rules

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

    '''
    ANNOTATE EARNINGS
    '''
    erng_frame = pd.read_pickle("earnings.pkl")
    erng_frame['date'] = pd.to_datetime(erng_frame['date'], format='%Y%m%d %H:%M:%S')
    erng_frame['date'] = erng_frame['date'].dt.date
    erng_frame['today'] = dt.date.today()
    erng_frame['daysToEarnings']      = (erng_frame['date'] - erng_frame['today']).dt.days        # delta


    '''
    EARNINGS + EXPIRATION REQUIREMENETS
    '''
    erngs_map = dict( erng_frame['daysToEarnings'] )
    options['daysToEarnings'] = options.underlying.apply(lambda symbol: erngs_map[symbol])
    options['daysBtwnExprErngs'] = options['daysToEarnings'] - options['daysToExpiration'] # d_days
    options = options[ options.daysBtwnExprErngs > 0 ]

    """
    ANNOTATE RISK
    """
    if   risk == "safe"    : options['Risk'] = "safe"
    elif risk == "moderate": options['Risk'] = "moderate"
    else                   : options['Risk'] = "risky"

    return options


def annotate_stocks(stocks, underlyings = []):

    if not underlyings:
        underlyings = list( stocks.Symbol )

    '''
    Rate and parse "ticker" in "underlyings"
    '''
    stock_rcmndts = pd.DataFrame()
    for symbol in tqdm(underlyings, desc="[1] Rating Stocks"):

        bars = stocks[ stocks.Symbol == symbol ].tail(200)
        if len(bars) != 200: continue

        bars = ta.macd(bars)
        bars = ta.sma(bars)
        bars = ta.rsi_old(bars)
        bars = ta.rate_pnf(bars)

        bars = ta.rate_sma(bars)
        bars = ta.rate_rsi(bars)
        bars['MACD_Rating'] = bars.apply(
            lambda x: rate.macd(x['MACD'], x['signal_line']), 
            axis=1
        )

        MACD_Rating = bars['MACD_Rating'].tail(1)[0]
        MACD_Slope  = bars['MACD_Slope'].tail(1)[0]
        SMA_Rating = bars['SMA_Rating'].tail(1)[0]
        RSI_Rating = bars['RSI_Rating'].tail(1)[0]
        PNF_Rating = bars['PNF_Rating'].tail(1)[0]

        if MACD_Rating == 1 \
            and MACD_Slope == 1 \
                and SMA_Rating == 1 \
                    and RSI_Rating == 1\
                        and PNF_Rating in ['a','b','c']:
                            stock_rcmndts = pd.concat([stock_rcmndts, bars.tail(1)])

    return stock_rcmndts

def snapshot(stocks, options, earnings, sectors, DEBUG=True):

    '''
    Annotate options and select using requirements
    '''
    print("[0] annotating options (safe, moderate, risky)")
    safe_options     = annotate_options(options, earnings, "safe")      # from annotate_options() above
    moderate_options = annotate_options(options, earnings, "moderate")
    risky_options    = annotate_options(options, earnings, "risky")

    '''
    # remove moderate from risky
    # remove safe from moderate
    # concat all options
    '''
    risky_options = risky_options[ ~risky_options.symbol.isin( list(moderate_options.symbol) ) ]
    moderate_options = moderate_options[ ~moderate_options.symbol.isin( list(safe_options.symbol) ) ]
    annotated_options = pd.concat(
        [ safe_options, moderate_options, risky_options ]
    )

    '''
    # get stock ratings (for all underlyings)
    '''
    # import sp500
    # underlyings = sp500.stocks.symbols()
    underlyings = list( annotated_options.underlying.unique() )
    annotated_stocks  = annotate_stocks(stocks, underlyings)            # from annotate_stocks() above


    if (DEBUG):
        print(annotated_options)
        print(annotated_stocks)

    if not len(annotated_stocks):
        return pd.DataFrame()

    '''
    # syncronize options and stocs indexes
    '''
    subset_annotated_options = annotated_options[ annotated_options.underlying.isin( list(annotated_stocks.Symbol) ) ]
    subset_annotated_options = subset_annotated_options.set_index('underlying')

    stocks_data = pd.DataFrame()
    for symbol in list(subset_annotated_options.index):
        stocks_data = pd.concat(
            [
                stocks_data, annotated_stocks[ annotated_stocks.Symbol == symbol]
            ]
        )
    

    '''
    # concat and drop cols
    '''
    stocks_data = stocks_data.set_index('Symbol')
    rcmdnts = pd.concat(
                    objs = [ subset_annotated_options, stocks_data ],
                    axis = 1
                ).reset_index()

    '''
    # return subset of columns
    '''
    return rcmdnts[
       [
            'symbol', 'quoteTimeInLong', 'isDelayed', 'exchangeName', 'last', 'lastSize',
            'delta', 'volatility', 'openInterest', 'totalVolume',
            'strikePrice', 'underlyingPrice', 'moneyness', 'percentInTheMoney',
            'collateral',  'percentAnnualPtnlReturn', 'daysToEarnings', 'daysBtwnExprErngs', 'expirationDate', 'daysToExpiration',
            'Risk', 'MACD_Rating','SMA_Rating', 'RSI_Rating', 
            'Support1', 'Support2', 'Resistance1', 'Resistance2', 'PNF_Rating'
        ]
    ]

    # TODO: adding "strikeBtwnSprts"
