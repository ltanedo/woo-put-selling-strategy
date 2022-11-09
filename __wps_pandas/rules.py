safe_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                       'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.95, 'annual_ptnl_ret_lim': 0.01, \
                       'prob_touch_lim': 0.9, 'label': 'safe'}

safe_put_map = {
    'min_daysToExpiration'        : 1,
    'max_daysToExpiration'        : 60,
    'min_bid'                     : 0.25,
    'max_bid'                     : 10000000,
    'min_totalVolume'             : 5,
    'max_totalVolume'             : 1000000000,
    'min_percentOutOfTheMoney'    : 0.0,       # Percent distance    outOfTheMoney
    'min_probabilityOutOfTheMoney': 0.95,      # Percent probability outOfTheMoney   95
    'max_percentAnnualPtnlReturn' : 0.01,
    'max_probabilityTouch'        : 0.9,
}


mod_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                      'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.90, 'annual_ptnl_ret_lim': 0.01, \
                      'prob_touch_lim': 0.9, 'label': 'moderate'}
moderate_put_map = {
    'min_daysToExpiration'        : 1,
    'max_daysToExpiration'        : 60,
    'min_bid'                     : 0.25,
    'max_bid'                     : 10000000,
    'min_totalVolume'             : 5,
    'max_totalVolume'             : 1000000000,
    'min_percentOutOfTheMoney'    : 0.0,      # Percent distance    outOfTheMoney
    'min_probabilityOutOfTheMoney': 0.90,     # Percent probability outOfTheMoney  90
    'max_percentAnnualPtnlReturn' : 0.01,
    'max_probabilityTouch'        : 0.9,
}

risky_put_parameters = {'days_min': 1, 'days_max': 60, 'bid_min':0.25, 'bid_max': 10000000, 'min_vol': 5, \
                        'max_vol': 1000000000, '%OTM_lim': 0.0, 'prob_OTM_lim': 0.80, 'annual_ptnl_ret_lim': 0.01, \
                        'prob_touch_lim': 0.9, 'label': 'risky'}

risky_put_map = {
    'min_daysToExpiration'        : 1,
    'max_daysToExpiration'        : 60,
    'min_bid'                     : 0.25,
    'max_bid'                     : 10000000,
    'min_totalVolume'             : 5,
    'max_totalVolume'             : 1000000000,
    'min_percentOutOfTheMoney'    : 0.0,     # Percent distance    outOfTheMoney
    'min_probabilityOutOfTheMoney': 0.80,    # Percent probability outOfTheMoney   80
    'max_percentAnnualPtnlReturn' : 0.01,
    'max_probabilityTouch'        : 0.9,
}

