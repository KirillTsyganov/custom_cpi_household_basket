# %%
import pandas as pd

# %%
cpi_data = pd.read_csv(
    "data/cpi/cpi_quarterly.csv", parse_dates=["start", "end"]
).sort_values(["category", "region", "start"])

cpi_data
# %%
cpi_data["measurement"].unique()
# %%
quarter_on_quarter = cpi_data.query(
    "measurement == 'Percentage Change from Previous Period'"
)
quarter_on_quarter
# %%
year_on_year = cpi_data.query(
    "measurement == 'Percentage Change from Corresponding Quarter of the Previous Year'"
)
year_on_year
# %%
cpi_data2 = pd.merge(
    quarter_on_quarter,
    year_on_year,
    on=["start", "end", "cal_quarter", "category", "region", "frequency"],
    how="inner",
    suffixes=("_qoq", "_yoy"),
)
cpi_data2
# %%
quarters = (
    cpi_data2[["start", "end", "cal_quarter"]].drop_duplicates().sort_values("start")
)
quarters
# %%
fx_data = (
    pd.read_csv("data/fx/fx_data.csv", parse_dates=["Series ID"])
    .loc[:, ["Series ID", "FXRUSD", "FXRTWI"]] \
    .query("FXRUSD != 'CLOSED'") \
    .query("FXRUSD != 'Closed'") \
    .sort_values("Series ID") \
    .assign(FXRUSD=lambda df: pd.to_numeric(df["FXRUSD"]),
            FXRTWI=lambda df: pd.to_numeric(df["FXRTWI"]))
)
fx_data
# %%
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
        last_fx_per_quarter[col].diff() / last_fx_per_quarter[col].shift(1) * 100
    )

last_fx_per_quarter
# %%
