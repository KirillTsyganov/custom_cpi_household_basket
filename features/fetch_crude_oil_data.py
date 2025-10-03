# %%
import os
import requests
import argparse
from datetime import datetime, timedelta
import random
import time
# %%
# url="https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23ebf3fb&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=565&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=DCOILWTICO&scale=left&cosd=2024-09-08&coed=2025-09-08&line_color=%230073e6&link_values=false&line_style=solid&mark_type=none&mw=3&lw=3&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2025-09-17&revision_date=2025-09-17&nd=1986-01-02"
# %%

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
# %% 
ids = ["DCOILWTICO", "DCOILBRENTEU"]

# NOTE: API data is about 11 days old
today = datetime.now()
end = today
start = end - timedelta(days=14)   

print(f"MSG: Today -> {today}")
print(f"MSG: Start -> {start}")
print(f"MSG: End -> {end}")

for series_id in ids:

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
    response = requests.get(url)
    filename = f"data/crude_oil/{today.strftime('%Y%m%d')}_{series_id}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.csv"

    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Data for {series_id} saved to {filename}")

    sleep_time = random.randint(0, 120)
    print(f"MSG: Sleeping (seconds) -> {sleep_time}")
    time.sleep(sleep_time)