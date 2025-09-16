# %%
import os
import requests
import pandas as pd

base_url = "https://www.rba.gov.au/statistics/tables/xls-hist/"
fn_suffixes = [
    "1983-1986",
    "1987-1990",
    "1991-1994",
    "1995-1998",
    "1999-2002",
    "2003-2006",
    "2007-2009",
    "2010-2013",
    "2014-2017",
    "2018-2022",
    "2023-current",
]

fx_dir = "data/fx"
os.makedirs(fx_dir, exist_ok=True)

fns = [f"{fx_dir}/{suffix}.xls" for suffix in fn_suffixes]

# Download files if not present
for suffix, fn in zip(fn_suffixes, fns):
    if not os.path.exists(fn):
        url = f"{base_url}/{suffix}.xls"
        print(f"Downloading {url} to {fn} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(fn, "wb") as f:
            f.write(r.content)

# %%
dfs = []

for fn in fns:
    xl = pd.ExcelFile(fn)
    sheets = xl.sheet_names
    dfs.append(pd.read_excel(fn, sheet_name=sheets[0], skiprows=10))

dfs
# %%
dat = pd.concat(dfs, ignore_index=True)
dat

# %%
# If 'Series ID' is a datetime, this works; otherwise, adjust as needed
# dat2 = dat.query("`Series ID`.dt.year >= 2000").sort_values("Series ID").reset_index(drop=True)
dat2 = dat.sort_values("Series ID").reset_index(drop=True)
dat2.to_csv("data/fx/fx_data.csv", index=False)
# %%
