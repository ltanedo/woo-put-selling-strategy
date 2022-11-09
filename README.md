# The Orignal .ipynb
- WPS_092321.ipnb is the original notebook (needs some fixing to run on new machine)
- WPS_norgate.ipynb is the original notebook slightly cleaned
- WPS_yfin.ipynb is the same as WPS_norgate, but modified to run cached dataframes

## Usage
> Note: Obtain cached data from here https://drive.google.com/drive/folders/1zZ253u4wzNA3DFAdk7Xr9YzGsWTjgWaR?usp=share_link
0. Make sure norgate data updater is running (.exe)
0. Add config.py file to directory
```
#
# in config.py
#
refresh_token = "refresh_token_from_account_authentication"
client_id     = "the_api_key_from_the_td_api_dash_confusing_i_know"
```
1. Run WPS_norgate.ipynb
2. View "norgate_stock_list.csv"
3. View "norgate_result.csv"

## Usage with TD Refresh Token
> Note WPS_yfin doesn't actually use yfinance
0. Aim to run WPS_yfin.ipynb
1. Make sure pickles from directory (get here -> https://drive.google.com/drive/folders/1zZ253u4wzNA3DFAdk7Xr9YzGsWTjgWaR?usp=share_link
```
STOCKS         : pd = pd.read_pickle("stocks_norate.pkl")
PACKED_OPTIONS : pd = pd.read_pickle("options_packed.pkl")
EARNINGS       : pd = pd.read_pickle("earnings.pkl")
```
2. View "yfin_stock_list.csv"
3. View "yfin_result.csv"
