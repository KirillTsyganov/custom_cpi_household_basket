# %%
import json
import pandas as pd
import statsmodels.api as sm
import pickle
# %%
fn = '../features/data/processed/features.csv'

dat1 = pd \
        .read_csv(fn) \
        .assign(cal_quarter=lambda x: x['cal_quarter'].str.replace('-', ''))

dat1
# %%
fn = '../features/data/cpi/cpi_11_main_groups.json'

groups = []

with open(fn, 'r') as f:
    for group in  json.load(f)['nodes']:
        groups.append((group['id'], group['name']))

groups
# %%
# basket = groups[0][1]
# basket
# %%
for _, basket in groups:

    df = dat1[['cal_quarter', basket, 'FXRUSD_pct_change', 'FXRTWI_pct_change', 'oil_price_pct_change']].dropna().sort_values('cal_quarter')
    df.set_index('cal_quarter', inplace=True)

    # Convert index to quarterly PeriodIndex
    df.index = pd.PeriodIndex(df.index, freq='Q')

    # Train ARIMA on basket CPI
    model = sm.tsa.ARIMA(df[basket], order=(1, 1, 1))
    results = model.fit()

    # Save model artifact as pkl file
    with open(f'artifacts/{basket}_arima_model.pkl', 'wb') as f:
        pickle.dump(results, f)
# %%
# # Forecast next quarter
# forecast = results.forecast(steps=1)
# print(f"Forecasted CPI for {basket} next quarter:", forecast.iloc[0])
