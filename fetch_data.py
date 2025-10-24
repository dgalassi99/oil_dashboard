''' Retrieve data from EIA and save to CSV'''

# fetch_data.py
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
EIA_API_KEY = os.getenv("EIA_API_KEY")

DATA_PATH = "data/stocks.csv"

# Top countries
COUNTRIES = [
    "AGO","ARE","BRA","CAN","CHN","DEU","FRA","GBR","IDN","IND",
    "IRN","IRQ","JPN","KAZ","KOR","KWT","MEX","NGA","NOR","RUS","SAU","USA","VEN","ITA"
]

# Products to include
PRODUCT_IDS = ['5','53','54','57']  # EIA product IDs for oil stocks

# Units
UNITS = ["MBBL"]  # million barrels

def fetch_stocks():
    """Fetch stocks data from EIA, filter locally, save CSV"""
    url = "https://api.eia.gov/v2/international/data/"
    all_data = []
    offset = 0
    length = 5000

    while True:
        params = {
            "api_key": EIA_API_KEY,
            "frequency": "monthly",
            "data[0]": "value",
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "offset": offset,
            "length": length,
        }

        # Facets
        for i, cid in enumerate(COUNTRIES):
            params[f"facets[countryRegionId][{i}]"] = cid
        for i, pid in enumerate(PRODUCT_IDS):
            params[f"facets[productId][{i}]"] = pid
        for i, unit in enumerate(UNITS):
            params[f"facets[unit][{i}]"] = unit

        # Request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["response"]["data"]

        if not data:
            break

        all_data.extend(data)
        offset += length

    # Create DataFrame
    df = pd.DataFrame(all_data)
    if not df.empty:
        # Convert types
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["period"] = pd.to_datetime(df["period"], errors="coerce")
        df.drop(columns=['productId', 'activityId', 'activityName','countryRegionTypeId',
       'countryRegionTypeName', 'dataFlagId', 'dataFlagDescription','unitName'], inplace=True)
        

    # Save CSV
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"Stocks data saved to {DATA_PATH}, total rows: {len(df)}")
    return df

if __name__ == "__main__":
    fetch_stocks()
