
import requests
import pandas as pd
from datetime import datetime
import os

# My BLS API key is used to authenticate requests to the API
API_KEY = "ef38c550434d44aea7d504856a674d1a"

# I created a dictionary to store the series IDs I want to collect data for
SERIES_IDS = {
    "Non-Farm Workers": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
    "Civilian Labor Force": "LNS11000000",
    "Civilian Employment": "LNS12000000",
    "Civilian Unemployment": "LNS13000000",
}
# This function sends a request to the BLS API and fetches data for a specific series ID
def fetch_bls_data(series_id, start_year, end_year):
    """Fetch data from the BLS API."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": API_KEY,
    }
     # I use the requests library to send the POST request
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "REQUEST_SUCCEEDED":
            return pd.DataFrame(data["Results"]["series"][0]["data"])
    return pd.DataFrame()
# This function converts the "year" and "period" from the BLS data into a proper date
def convert_period_to_date(year, period):
    """Convert year and period to a valid date."""
    if period.startswith("M"):  # Monthly data
        return f"{year}-{period[1:].zfill(2)}-01"
    elif period.startswith("Q"):  # Quarterly data
        quarter_to_month = {"Q01": "01", "Q02": "04", "Q03": "07", "Q04": "10"}
        return f"{year}-{quarter_to_month[period]}-01"
    return None
# This function loops through all the series IDs, fetches their data, and cleans it
def collect_data():
    """Collect data for all series."""
    current_year = datetime.now().year
    start_year = current_year - 1  # Fetch at least one year of data
    all_data = []
   # I loop through each series in the SERIES_IDS dictionary
    for name, series_id in SERIES_IDS.items():
        print(f"Fetching data for {name} ({series_id})...")
        df = fetch_bls_data(series_id, start_year, current_year)
        if not df.empty and set(["year", "period", "value"]).issubset(df.columns):
            df["date"] = df.apply(lambda row: convert_period_to_date(row["year"], row["period"]), axis=1)
            df = df.dropna(subset=["date"])  # Drop rows where date conversion failed
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
            df["series"] = name  # Add series name as a column
            df = df[["date", "value", "series"]]  # Keep only necessary columns
            all_data.append(df)
        else:
            print(f"No data found for {name}.")
# If I collected data for at least one series, I combine all the DataFrames into one
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()
# This block runs the script to collect data and save it to a CSV file
if __name__ == "__main__":
    data = collect_data()
    if not data.empty:
        data.to_csv("labor_statistics.csv", index=False)
        print("Data saved to labor_statistics.csv")
    else:
        print("No data collected.")

