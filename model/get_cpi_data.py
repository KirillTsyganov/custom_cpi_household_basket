# %%
import json
import pandas as pd

from abs_api import ABSData
# %%
# fn = 'data/top_level_categories.json'

# categories = []

# with open(fn, 'r') as f:
#     for category in  json.load(f)['nodes']:
#         categories.append((category['id'], category['name']))

# categories
# %%
categories = [
    ('115922', 'All groups CPI excluding Alcohol and tobacco'),
    ('128058', 'All groups CPI excluding Insurance and financial services'),
    # ('104100', 'Goods and services series'),
    ('131197', 'All groups CPI excluding food and energy'),
    ('115941', 'All groups CPI excluding Clothing and footwear'),
    ('104122', "All groups CPI excluding 'volatile items'"),
    # ('132300', 'Non-discretionary and discretionary series'),
    ('117101',
     'All groups CPI excluding Furnishings, household equipment and services'),
    ('117121', 'All groups CPI excluding Communication'),
    ('115902', 'All groups CPI excluding Food and non-alcoholic beverages'),
    ('117124', 'All groups CPI excluding Recreation and culture'),
    ('117104', 'All groups CPI excluding Health'),
    # ('102674', 'International trade exposure series'),
    ('128061',
     'All groups CPI excluding Housing and Insurance and financial services'),
    # ('999900', 'Underlying trend series'),
    ('115961', 'All groups CPI excluding Housing'),
    ('117107', 'All groups CPI excluding Transport'),
    # ('131198', 'All groups CPI including'),
    ('10001', 'All groups CPI'),
    ('117127', 'All groups CPI excluding Education'),
    # ('104099', "Market goods and services excluding 'volatile items'"),
    ('117144', 'All groups CPI excluding Medical and hospital services')
]
# %%
measure_type = [
    (2, "Percentage Change from Previous Period"),
    (3, "Percentage Change from Corresponding Quarter of the Previous Year"),
    (4, "Contribution to Total CPI"),
    (5, "Change in Contribution to Total CPI"),
]
# %%
dfs = []

for idx, measure in measure_type:

    print(f"MSG: Processing -> {measure}")

    for key, category in categories:
        # percentage_changes.category.original_values.melbourne.quarterly
        data_key = f"{idx}.{key}.10.2.Q"
        print(f"MSG: Processing -> {category}")
        print(f"MSG: Data Key -> {data_key}")

        abs_data = ABSData('CPI', debug=True)
        abs_data.call_api_data(data_key, start='2000')
        dat = abs_data.make_table()

        dat2 = dat.assign(start = lambda x: pd.to_datetime(x['start']), 
                          end = lambda x: pd.to_datetime(x['end']),
                          measurement = measure) \
                    .sort_values('start') \
                    .reset_index(drop=True) 

        dfs.append(dat2)
# %%
dat = pd \
        .concat(dfs, axis=0) \
        .reset_index(drop=True) \
        .rename(columns={'Index': 'category', 'Region': 'region', 'Frequency': 'frequency'}) \
        .sort_values(['category', 'measurement', 'start']) \
        .reset_index(drop=True)
dat
# %%
dat.to_csv('data/cpi_quarterly.csv', index=False)
# %%
