# %%
import pandas as pd

# fn = "data/fx/1999-2002.xls"
fns = [
    "data/fx/1999-2002.xls",
    "data/fx/2003-2006.xls",
    "data/fx/2007-2009.xls",
    "data/fx/2010-2013.xls",
    "data/fx/2014-2017.xls",
    "data/fx/2018-2022.xls",
    "data/fx/2023-current.xls"
]
# %%
dfs = []

for fn in fns:
    xl = pd.ExcelFile(fn)
    sheets = xl.sheet_names
    dfs.append(pd.read_excel(fn, sheet_name=sheets[0], skiprows=10))
# %%
dat = pd.concat(dfs, ignore_index=True)
dat
# %%
dat2 = dat.query("`Series ID`.dt.year >= 2000").sort_values("Series ID").reset_index(drop=True)
dat2.to_csv("data/fx/fx_data.csv", index=False)

# %%
