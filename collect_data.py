
import requests
import pandas as pd
from datetime import datetime

# Your BLS API key
API_KEY = "65afab4a256742f183969f74be49fecc."

# Series to fetch
SERIES_IDS = {
    "Non-Farm Workers": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
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
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "REQUEST_SUCCEEDED":
            return pd.DataFrame(data["Results"]["series"][0]["data"])
        else:
            print(f"Error: {data['message']}")
    else:
        print(f"HTTP Error: {response.status_code}")
    return None

def collect_data():
    """Collect data for all series."""
    current_year = datetime.now().year
    start_year = current_year - 1
    all_data = {}

    for name, series_id in SERIES_IDS.items():
        print(f"Fetching data for {name}...")
        df = fetch_bls_data(series_id, start_year, current_year)
        if df is not None:
            df["series"] = name
            df["date"] = pd.to_datetime(df["year"] + "-Q" + df["period"].str[1:])
            df = df[["date", "value", "series"]]
            all_data[name] = df

    return pd.concat(all_data.values(), ignore_index=True)

if __name__ == "__main__":
    data = collect_data()
    data.to_csv("labor_statistics.csv", index=False)
    print("Data saved to labor_statistics.csv")
