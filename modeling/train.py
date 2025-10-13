# %%
import json
import pandas as pd
import statsmodels.api as sm
import pickle

# %%
fn_quarter = "../features/data/processed/features_quarter_on_quarter.csv"

dat_quarter = pd.read_csv(fn_quarter).assign(
    cal_quarter=lambda x: x["cal_quarter"].str.replace("-", "")
)

dat_quarter
# %%
fn_year = "../features/data/processed/features_year_on_year.csv"

dat_year = pd.read_csv(fn_year).assign(
    cal_quarter=lambda x: x["cal_quarter"].str.replace("-", "")
)
dat_year
# %%
fn = "../features/data/cpi/cpi_11_main_groups.json"

groups = []

with open(fn, "r") as f:
    for group in json.load(f)["nodes"]:
        groups.append((group["id"], group["name"]))

groups
# %%
# basket = groups[0][1]
# basket
# %%
tmp = []
for _, basket in groups:
    basket_qoq = basket + "_qoq"
    basket_yoy = basket + "_yoy"
    # Merge qoq and yoy data on cal_quarter
    merged = pd.merge(
        dat_quarter,
        dat_year,
        on="cal_quarter",
        suffixes=("_qoq", "_yoy"),
    )
    df = (
        merged[
            [
                "cal_quarter",
                basket_qoq,
                basket_yoy,
                "FXRUSD_pct_change_qoq",
                "FXRTWI_pct_change_qoq",
                "oil_price_pct_change_qoq",
                "FXRUSD_pct_change_yoy",
                "FXRTWI_pct_change_yoy",
                "oil_price_pct_change_yoy",
            ]
        ]
        .dropna()
        .sort_values("cal_quarter")
    )
    df.set_index("cal_quarter", inplace=True)

    # Convert index to quarterly PeriodIndex
    df.index = pd.PeriodIndex(df.index, freq="Q")

    tmp.append((basket, df))
    # Generic: forecast basket_qoq using all other columns as exogenous features
    y = df[basket_qoq]
    # exog = df.drop(columns=[basket_qoq])
    # model = sm.tsa.ARIMA(y, order=(1, 1, 1), exog=exog)
    model = sm.tsa.ARIMA(y, order=(1, 1, 1))
    results = model.fit()

    # Save model artifact as pkl file
    with open(f"artifacts/{basket}_arima_model.pkl", "wb") as f:
        pickle.dump(results, f)
# %%
tmp[0][1].columns.tolist()
# # Forecast next quarter
# forecast = results.forecast(steps=1)
# print(f"Forecasted CPI for {basket} next quarter:", forecast.iloc[0])

# %%
