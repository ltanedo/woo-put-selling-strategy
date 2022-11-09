# Options Tests
> Note: old_options.pkl is too big missing (get here : https://drive.google.com/file/d/1MKXCj9aFdffZXUC1IqZvC_q-1M-KoPp2/view?usp=share_link)
- Verified Options pandas queries select the same exact symbols as the ipynb.processing(...) function
- Verified Earnings section in options queries same as ipynb.report(...) function
- Fixed edge case comming from '>' cs '>=' during negations of "continue" conditionals in .ipnb
- Fixed edge-case mistake in ipynb using any query with delta (ex below)

```
# if delta = np.nan or None
# statement evaluates to False, continuing the function 
# even if requirement doesn't pass
if 1 - agg_data[date_keys[i][0]][date_keys[i][1][j]][0]['delta'] < params['prob_OTM_lim']: # Prob OTM Requirement!
                    continue
```
