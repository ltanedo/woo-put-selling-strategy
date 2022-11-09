# Upgraded WPS in Complete Pandas
The same strategy from the ipynb, written in pandas.  Aimed to run as AWS Lambdas.

### Update Notes
- Added Calls to sp500.options.snapshot()
- Stock and Option ratings/functions unit tested in branches "testing-stocks" + "testing-options"
- Outliers caught in options with >= vs >
- __wps_pandas.annotate_stocks(...) validated for correct output 

### Usage
> Note: Sample of all caches included, will run automatically w/ sample
0. Make sure to install requirements.txt
1. Run woo_put_sell_2022.py
2. view woo_put_sell_2022.csv

### Reversal for Calls (notes from Professor Liu)
- MACD Rating Completely Reversed
- SMA Rating Completely Reversed
- RSI Rating >= 70 is ideal (looking for RSI to reverse to 30 -> Currently checks between 30,70)
- Skip the PnF Rating
- Options requirement for | percentAnnualPtnlReturn UNECESSARY
- Options requirement for | delta * -2 >= maxProbTouch UNECESSARY

### Thoughts (Lloyd)
- All options basic requirements the same (bid, volume, daysToExpiration)
- All options earnings requirements the same (basically options expire before earnings)
- options.delta and percentOutOfTheMoney requirements will change (more below)

# Below will most likely be changed for calls
```
# __wps_pandas.recommendations.py Line 38
#
options = options[ (-1 * options.percentInTheMoney) >= params['min_percentOutOfTheMoney'] ]   # Lloyd : This was negated


# __wps_pandas.recommendations.py Line 41
#
options["delta"] = 1 + options.delta.astype(float)
options = options[ options.delta >= params['min_probabilityOutOfTheMoney'] ]  


# __wps_pandas.recommendations.py Line 48
#
options = options[ options.putCall == "PUT"]
```
