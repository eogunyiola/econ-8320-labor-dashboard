import requests
import pandas as pd
from datetime import datetime

# Your BLS API key
API_KEY = "ef38c550434d44aea7d504856a674d1a"

# Series to fetch
SERIES_IDS = {
    "Non-Farm Workers": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
    "Civilian Labor Force": "LNS11000000",
}

def fetch_bls_data(series_id, start_year, end_year):
    """Fetch data from the BLS API."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    payload = {
        "seriesid": [series_id],
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": API_KEY,
    }
    response = requests.post(url, json=payload)
    print(f"Response for {series_id}: {response.status_code}")  # Debug HTTP status
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "REQUEST_SUCCEEDED":
            if data["Results"]["series"][0]["data"]:
                print(f"Data fetched for {series_id}: {len(data['Results']['series'][0]['data'])} records.")
                return pd.DataFrame(data["Results"]["series"][0]["data"])
            else:
                print(f"No records found for {series_id}. Skipping...")
        else:
            print(f"Error for {series_id}: {data.get('message', 'No message provided')}")
    else:
        print(f"HTTP Error for {series_id}: {response.status_code}")
    return None

def convert_date(row):
    """Convert BLS period and year to datetime."""
    try:
        return pd.to_datetime(f"{row['year']}-{row['period'][1:]}-01", format="%Y-%m-%d")
    except Exception:
        return None

def collect_data():
    """Collect data for all series."""
    current_year = datetime.now().year
    start_year = current_year - 1  # Fetch at least one year of data
    all_data = {}

    for name, series_id in SERIES_IDS.items():
        print(f"Fetching data for {name}...")
        df = fetch_bls_data(series_id, start_year, current_year)
        if df is not None and not df.empty:
            df["date"] = df.apply(convert_date, axis=1)
            df = df.dropna(subset=["date"])  # Drop invalid dates
            df["series"] = name
            df = df[["date", "value", "series"]]
            all_data[name] = df
            print(f"Fetched {len(df)} records for {name}.")
        else:
            print(f"No data returned for {name}. Skipping...")

    if all_data:
        combined_data = pd.concat(all_data.values(), ignore_index=True)
        print(f"Total records fetched: {len(combined_data)}")
        return combined_data
    else:
        print("No data fetched for any series.")
        return pd.DataFrame()

if __name__ == "__main__":
    data = collect_data()
    if not data.empty:
        data.to_csv("labor_statistics.csv", index=False)
        print("Data saved to labor_statistics.csv")
    else:
        print("No data collected. CSV file not updated.")


