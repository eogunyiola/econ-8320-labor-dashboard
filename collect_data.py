
import requests
import pandas as pd
from datetime import datetime

# Your BLS API key
API_KEY = "ef38c550434d44aea7d504856a674d1a"

# Series to fetch
SERIES_IDS = {
    # Employment
    "Non-Farm Workers": "CES0000000001",
    "Unemployment Rate": "LNS14000000",
    "Civilian Labor Force": "LNS11000000",
    "Civilian Employment": "LNS12000000",
    "Civilian Unemployment": "LNS13000000",

    # Price Indexes
    "CPI-U (Urban Consumers)": "CUUR0000SA0",
    "PPI Final Demand": "WPSFD4",

    # Compensation
    "ECI Private (Unadjusted)": "CIU2010000000000A",
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
    print(f"Response for {series_id}: {response.status_code}")  # Print HTTP status code
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "REQUEST_SUCCEEDED":
            return pd.DataFrame(data["Results"]["series"][0]["data"])
        else:
            print(f"Error for {series_id}: {data['message']}")
    else:
        print(f"HTTP Error for {series_id}: {response.status_code}")
    return None

def convert_quarter_to_date(year, quarter):
    """Convert year and quarter to a valid date."""
    quarter_to_month = {"Q01": "01", "Q02": "04", "Q03": "07", "Q04": "10"}
    month = quarter_to_month.get(quarter, None)
    if month:
        return f"{year}-{month}-01"
    return None

def collect_data():
    """Collect data for all series."""
    current_year = datetime.now().year
    start_year = current_year - 1  # Collect at least one year of previous data
    all_data = {}

    for name, series_id in SERIES_IDS.items():
        print(f"Fetching data for {name}...")
        df = fetch_bls_data(series_id, start_year, current_year)
        if df is not None:
            if not df.empty:
                if set(["year", "period", "value"]).issubset(df.columns):
                    df = df[df["period"].str.startswith("Q")]  # Filter valid quarters
                    df["date"] = df.apply(lambda row: convert_quarter_to_date(row["year"], row["period"]), axis=1)
                    df = df.dropna(subset=["date"])  # Drop rows where date conversion failed
                    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
                    df["series"] = name
                    df = df[["date", "value", "series"]]
                    all_data[name] = df
                else:
                    print(f"Missing required columns for {name}. Skipping...")
            else:
                print(f"No data returned for {name}. Skipping...")
        else:
            print(f"Failed to fetch data for {name}. Skipping...")

    if all_data:
        return pd.concat(all_data.values(), ignore_index=True)
    else:
        print("No data fetched for any series. Check your API key or series IDs.")
        return pd.DataFrame()

if __name__ == "__main__":
    data = collect_data()
    if not data.empty:
        data.to_csv("labor_statistics.csv", index=False)
        print("Data saved to labor_statistics.csv")
    else:
        print("Data collection failed.")

