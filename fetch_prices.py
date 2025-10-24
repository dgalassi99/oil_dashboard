# fetch_prices.py
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load API key from .env
load_dotenv()
EIA_API_KEY = os.getenv("EIA_API_KEY")

# Output folder
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
CSV_PATH = os.path.join(DATA_DIR, "prices.csv")

# Parameters
PRODUCT_NAMES = {
    "WTI Crude Oil": "RWTC",   # WTI Cushing
    "UK Brent Crude Oil": "RBRTE"  # Europe Brent
}
FREQUENCY = "daily"  # daily prices
START_DATE = "2015-01-01"  # adjust as needed
LENGTH = 5000  # max rows per call

EIA_URL = "https://api.eia.gov/v2/petroleum/pri/spt/data/"

def fetch_prices():
    all_data = []
    offset = 0

    while True:
        params = {
            "api_key": EIA_API_KEY,
            "frequency": FREQUENCY,
            "data[0]": "value",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": offset,
            "length": LENGTH,
        }

        # Add facets for products
        for i, p in enumerate(PRODUCT_NAMES):
            params[f"facets[product][{i}]"] = p

        # Start date
        params["start"] = START_DATE

        response = requests.get(EIA_URL, params=params)
        response.raise_for_status()
        data = response.json()["response"]["data"]

        if not data:
            break

        for row in data:
            row["product-name"] = PRODUCT_NAMES.get(row["product"], row["product"])
        all_data.extend(data)

        if len(data) < LENGTH:
            break
        offset += LENGTH

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    if df.empty:
        print("No data retrieved!")
        return df

    # Keep relevant columns
    df = df[["period", "product","product-name","process-name","series-description", "value", "units"]]

    # Clean types
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Sort by period
    df = df.sort_values(["period","product"]).reset_index(drop=True)

    # Save CSV
    df.to_csv(CSV_PATH, index=False)
    print(f"Prices data saved to {CSV_PATH}, total rows: {len(df)}")
    return df

if __name__ == "__main__":
    fetch_prices()
