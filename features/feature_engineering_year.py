# %%
import pandas as pd

# %%
year_on_year = (
    pd.read_csv(
        "data/cpi/cpi_quarterly_year_on_year.csv", parse_dates=["start", "end"]
    )
    .sort_values(["group", "start"])
    .drop(["frequency", "measurement", "region"], axis=1)
)
year_on_year

# %%
dat1 = (
    year_on_year.set_index(["start", "end", "cal_quarter", "group"])
    .unstack(["group"])
    .reset_index()
)

dat1.columns = [col[1] if col[1] else col[0] for col in dat1.columns.values]

dat1
# %%
quarters = (
    year_on_year[["start", "end", "cal_quarter"]]
    .drop_duplicates()
    .sort_values("start")
)
quarters
# %%
fx_data = (
    pd.read_csv("data/fx/fx_data.csv", parse_dates=["Series ID"])
    .loc[:, ["Series ID", "FXRUSD", "FXRTWI"]]
    .query("FXRUSD != 'CLOSED'")
    .query("FXRUSD != 'Closed'")
    .sort_values("Series ID")
    .assign(
        FXRUSD=lambda df: pd.to_numeric(df["FXRUSD"]),
        FXRTWI=lambda df: pd.to_numeric(df["FXRTWI"]),
    )
)
fx_data
# %%
# Assign each FX row to its quarter
fx_data_with_quarter = pd.merge_asof(
    fx_data, quarters, left_on="Series ID", right_on="start", direction="backward"
)

fx_data_with_quarter
# %%
# Find last trading day for each quarter
last_fx_per_quarter = (
    fx_data_with_quarter.groupby("cal_quarter")
    .apply(lambda df: df.loc[df["Series ID"].idxmax()])
    .reset_index(drop=True)
    .sort_values("cal_quarter")
)

last_fx_per_quarter
# %%
# Calculate percentage change for FXRUSD and FXRTWI
for col in ["FXRUSD", "FXRTWI"]:
    last_fx_per_quarter[f"{col}_pct_change"] = (
        last_fx_per_quarter[col].diff() / last_fx_per_quarter[col].shift(4) * 100
    )

last_fx_per_quarter.drop(["Series ID", "FXRUSD", "FXRTWI"], axis=1, inplace=True)
last_fx_per_quarter
# %%
crude_oil_price = pd.read_csv(
    "data/crude_oil/DCOILBRENTEU.csv", parse_dates=["observation_date"]
).rename(columns={"DCOILBRENTEU": "oil_price"})
crude_oil_price
# %%
# Assign each crude_oil row to its quarter
crude_oil_price_with_quarter = pd.merge_asof(
    crude_oil_price,
    quarters,
    left_on="observation_date",
    right_on="start",
    direction="backward",
)

crude_oil_price_with_quarter
# %%
# Find last trading day for each quarter
last_crude_oil_price_per_quarter = (
    crude_oil_price_with_quarter.groupby("cal_quarter")
    .apply(lambda df: df.loc[df["observation_date"].idxmax()])
    .reset_index(drop=True)
    .sort_values("cal_quarter")
)

last_crude_oil_price_per_quarter
# %%
# Calculate percentage change for crude oil price
col = "oil_price"
last_crude_oil_price_per_quarter[f"{col}_pct_change"] = (
    last_crude_oil_price_per_quarter[col].diff()
    / last_crude_oil_price_per_quarter[col].shift(4)
    * 100
)

last_crude_oil_price_per_quarter.drop(
    ["observation_date", "oil_price"], axis=1, inplace=True
)
last_crude_oil_price_per_quarter
# %%
dat2 = pd.merge(
    dat1, last_fx_per_quarter, on=["start", "end", "cal_quarter"], how="left"
).merge(
    last_crude_oil_price_per_quarter, on=["start", "end", "cal_quarter"], how="left"
)

# dat2 = dat2.rename(columns=lambda x: f"{x}_yoy")

dat2.to_csv("data/processed/features_year_on_year.csv", index=False)

# %%
