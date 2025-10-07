# %%
import argparse
import os
import requests
import pandas as pd
from datetime import datetime

def download_fx_files(output_dir, historical=False):
    """
    Fetch FX data from the RBA website and save it as a CSV file.

    Args:
        output_dir (str): Directory to save the downloaded files.
        historical (bool): If True, download all historical files; if False, download only the most recent file.
    Returns:
        list of str: List of file paths to the downloaded Excel files.
    """

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

    fx_dir = output_dir
    os.makedirs(fx_dir, exist_ok=True)

    fns = [f"{fx_dir}/{suffix}.xls" for suffix in fn_suffixes]

    # Download files if not present
    if historical:
        for suffix, fn in zip(fn_suffixes, fns):
            if not os.path.exists(fn):
                url = f"{base_url}/{suffix}.xls"
                print(f"Downloading {url} to {fn} ...")
                r = requests.get(url)
                r.raise_for_status()
                with open(fn, "wb") as f:
                    f.write(r.content)
    else:
        suffix = fn_suffixes[-1]
        fn = fns[-1]
        if os.path.exists(fn):
            os.remove(fn)

        url = f"{base_url}/{suffix}.xls"
        print(f"Downloading {url} to {fn} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(fn, "wb") as f:
            f.write(r.content)

    return fns

def read_fx_files(fns):
    """
    Read FX data from the downloaded Excel files and concatenate them into a single DataFrame.

    Args:
        fns (list of str): List of file paths to the downloaded Excel files.
    Returns:
        pd.DataFrame: Concatenated DataFrame containing FX data from all files.
    """

    dfs = []
    for fn in fns:
        xl = pd.ExcelFile(fn)
        sheets = xl.sheet_names
        dfs.append(pd.read_excel(fn, sheet_name=sheets[0], skiprows=10))

    return pd.concat(dfs, ignore_index=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/fx",
        help="Directory to save the downloaded FX files.",
    )
    parser.add_argument(
        "--historical",
        action="store_true",
        help="If set, download all historical FX files; otherwise, download only the most recent file.",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, args.output_dir)

    fns = download_fx_files(output_dir, historical=args.historical)
    dat = read_fx_files(fns)

    # If 'Series ID' is a datetime, this works; otherwise, adjust as needed
    # dat2 = dat.query("`Series ID`.dt.year >= 2000").sort_values("Series ID").reset_index(drop=True)
    dat2 = dat.sort_values("Series ID").reset_index(drop=True)
    
    max_date = dat2["Series ID"].max().strftime("%Y%m%d")
    min_date = dat2["Series ID"].min().strftime("%Y%m%d")

    today = datetime.now().strftime("%Y%m%d")

    output_fn = os.path.join(output_dir, f"{today}_fx_data_{max_date}_{min_date}.csv")
    dat2.to_csv(output_fn, index=False)
# %%
