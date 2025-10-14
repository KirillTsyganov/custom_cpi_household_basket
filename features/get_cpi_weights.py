# %%
import json
import pandas as pd

from abs_api import ABSData

# %%
fn = "data/cpi/cpi_11_main_groups.json"

groups = []

with open(fn, "r") as f:
    for group in json.load(f)["nodes"]:
        groups.append((group["id"], group["name"]))

groups
# %%
# %%
measure_type = [
    (1, "Percentage contribution to the All groups CPI", "total_contribution"),
    # (
    #     2,
    #     "Capital city percentage contribution to the weighted average of eight capital cities",
    #     "year_on_year",
    # ),
    # (4, "Contribution to Total CPI"),
    # (5, "Change in Contribution to Total CPI"),
]
# %%

for idx, measure, measure_name in measure_type:
    print(f"MSG: Processing -> {measure}")

    dfs = []

    for key, group in groups:
        # percentage_changes.category.original_values.melbourne.quarterly
        data_key = f"{idx}.{key}.2.Q"
        print(f"MSG: Processing -> {group}")
        print(f"MSG: Data Key -> {data_key}")

        abs_data = ABSData("CPI_WEIGHTS", debug=True)
        abs_data.call_api_data(data_key)
        dat = abs_data.make_table()

        dat2 = (
            dat.assign(
                start=lambda x: pd.to_datetime(x["start"]),
                end=lambda x: pd.to_datetime(x["end"]),
                measurement=measure,
            )
            .sort_values("start")
            .reset_index(drop=True)
        )

        dfs.append(dat2)

    dat = (
        pd.concat(dfs, axis=0)
        .reset_index(drop=True)
        .rename(
            columns={"Index": "group", "Region": "region", "Frequency": "frequency", "cpi_value": "cpi_weights"}
        )
        .sort_values(["group", "measurement", "start"])
        .drop(columns=["frequency"])
        .reset_index(drop=True)
    )

    fn_out = f"data/cpi/cpi_weights_{measure_name}.csv"
    dat.to_csv(fn_out, index=False)
