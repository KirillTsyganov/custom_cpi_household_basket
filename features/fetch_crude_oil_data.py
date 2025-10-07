"""Fetches crude oil data, 14 days snapshot or historical data, from FRED and saves it to CSV files. """
# %%
import os
import argparse
import random
import time
from datetime import datetime, timedelta
import requests

# url="https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23ebf3fb&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=565&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DCOILWTICO&scale=left&cosd=2024-09-08&coed=2025-09-08&line_color=%230073e6&link_values=false&line_style=solid&mark_type=none&mw=3&lw=3&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2025-09-17&revision_date=2025-09-17&nd=1986-01-02"

# - id (series_id): The unique identifier for the economic data series (e.g., DCOILWTICO for Crude Oil Prices).
# - cosd (observation_start): The start date of the data series you want to retrieve. Stands for Commencement of Series Date.
# - coed (observation_end): The end date of the data series you want to retrieve. Stands for Conclusion of End Date.
# - fq (frequency): The frequency of the data, such as Daily or Monthly.
# - fml (formula): The formula used for transformations, such as a for the primary series.
# - fam (aggregation_method): The method used to aggregate data (e.g., avg for average).
# - vintage_date (vintage_date): The date on which the data was first published or last revised.
# - revision_date (revision_date): The date of the most recent revision for the data.
# - nd (observation_date_of_first_observation): The date of the first observation in the dataset.

# DCOILBRENTEU  Crude Oil Prices: Brent - Europe
# DCOILWTICO    Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma


# POILBREUSDM   Global Price Brent Crude
# POILWTIUSDM   Global price of WTI Crude

def main(series_id, start, end, today, output_dir):
    """
    Fetches crude oil data from FRED and saves it to a CSV file.
    Args:
        series_id (str): The FRED series ID for the crude oil data.
        start (datetime): The start date for the data retrieval.
        end (datetime): The end date for the data retrieval.
        today (datetime): The current date for versioning the file and data revision.
        output_dir (str): The directory to save the fetched data.

    Returns:
    """
    # NOTE: API data is about 11 days old

    url = (
        "https://fred.stlouisfed.org/graph/fredgraph.csv?"
        f"id={series_id}&"
        f"cosd={start.strftime('%Y-%m-%d')}&"
        f"coed={end.strftime('%Y-%m-%d')}&"
        "fq=Daily&"
        "fml=a&"
        "fam=avg&"
        f"vintage_date={today.strftime('%Y-%m-%d')}&"
        f"revision_date={today.strftime('%Y-%m-%d')}&"
        "nd=1986-01-02"
    )
    response = requests.get(url, timeout=30)
    filename = f"{output_dir}/{today.strftime('%Y%m%d')}_{series_id}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"
    print(f"INFO: Output path -> {filename}")

    with open(filename, "wb") as file:
        file.write(response.content)
    print(f"Data for {series_id} saved to {filename}")

    sleep_time = random.randint(0, 120)
    print(f"INFO: Sleeping (seconds) -> {sleep_time}")
    time.sleep(sleep_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch crude oil data from FRED")
    parser.add_argument(
        "--series_ids",
        type=str,
        nargs="+",
        default=["DCOILWTICO", "DCOILBRENTEU"],
        help="FRED series IDs to fetch",
    )
    parser.add_argument(
        "--start_days_ago",
        type=str,
        help="Number of days ago to start fetching data from, format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--end_days_ago",
        type=str,
        help="Number of days ago to end fetching data, format: YYYY-MM-DD",
    )
    parser.add_argument(
        "--snapshot_window",
        type=int,
        default=21,
        help="Number of days for snapshot data extraction if start_days_ago and end_days_ago are not provided",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/crude_oil",
        help="Directory to save the fetched data",
    )

    args = parser.parse_args()
    # how to get origin of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, args.output_dir)
    print(f"INFO: Output directory -> {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    today_date = datetime.now()

    for s_id in args.series_ids:
        if args.start_days_ago is not None and args.end_days_ago is not None:
            # convert args.end_days_ago into date type
            end_date = datetime.strptime(args.end_days_ago, "%Y-%m-%d")
            start_date = datetime.strptime(args.start_days_ago, "%Y-%m-%d")
            print(
                f"INFO: Performing data extraction from {start_date} to {end_date} days ago."
            )
        else:
            print(
                f"INFO: Performing {args.snapshot_window} days snapshot data extraction."
            )
            end_date = today_date
            start_date = end_date - timedelta(days=args.snapshot_window)

        print(f"INFO: Today -> {today_date}")
        print(f"INFO: Start -> {start_date}")
        print(f"INFO: End -> {end_date}")

        main(s_id, start_date, end_date, today_date, output_dir)

        # NOTE: API data is about 11 days old
