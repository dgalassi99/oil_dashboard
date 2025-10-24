''' Retrieve data from EIA and save to CSV'''

# fetch_data.py
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
EIA_API_KEY = os.getenv("EIA_API_KEY")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# PARAMETERS
COUNTRY_IDS = [
    # Individual countries (top producers / consumers)
    "AGO",  # Angola
    "ARE",  # UAE
    "BRA",  # Brazil
    "CAN",  # Canada
    "CHN",  # China
    "DEU",  # Germany
    "FRA",  # France
    "GBR",  # UK
    "IDN",  # Indonesia
    "IND",  # India
    "IRN",  # Iran
    "IRQ",  # Iraq
    'ITA',  # Italy
    "JPN",  # Japan
    "KAZ",  # Kazakhstan
    "KOR",  # South Korea
    "KWT",  # Kuwait
    "MEX",  # Mexico
    "NGA",  # Nigeria
    "NOR",  # Norway
    "RUS",  # Russia
    "SAU",  # Saudi Arabia
    "USA",  # United States
    "VEN",  # Venezuela

    # Additional countries
    "GAB",  # Gabon
    "COG",  # Congo
    "LBY",  # Libya
    "DZA",  # Algeria
    "OMN",  # Oman
    "AZE",  # Azerbaijan
    "MYS",  # Malaysia
    "BHR",  # Bahrain
    "SSD",  # South Sudan
    "SDN",  # Sudan
    "BRN",  # Brunei

    # Regional OPEC aggregates
    "OPNO",  # Non-OPEC
    "OPEC",  # Core Middle East OPEC
    "OPSA",  # South America OPEC
    "OPAF"   # African OPEC
]

# Activity mapping: name -> activityId
ACTIVITIES = {
    "Production": "1",
    "Consumption": "2",
    "Stocks": "5"
}

URL = "https://api.eia.gov/v2/international/data/"
START_DATE = "2020-01"
LENGTH = 5000  # max rows per call

def fetch_activity(activity_name: str, activity_id: str) -> pd.DataFrame:
    """Fetch data for a single activity across all countries with pagination."""
    all_data = []

    for country_id in COUNTRY_IDS:
        offset = 0
        while True:
            params = {
                "api_key": EIA_API_KEY,
                "frequency": "monthly",
                "data[0]": "value",
                "sort[0][column]": "period",
                "sort[0][direction]": "desc",
                "offset": offset,
                "length": LENGTH,
                "facets[countryRegionId][0]": country_id,
                "facets[activityId][0]": activity_id,
                "start": START_DATE,
                "end": None
            }

            response = requests.get(URL, params=params)
            response.raise_for_status()
            data = response.json()["response"]["data"]

            if not data:
                break

            all_data.extend(data)
            if len(data) < LENGTH:
                break
            offset += LENGTH

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    if not df.empty:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        #df["value"] = df["value"].fillna(0)
        df["period"] = pd.to_datetime(df["period"], errors="coerce")
        # Drop unnecessary columns
        drop_cols = [
            "productId", "countryRegionTypeId",
            "countryRegionTypeName", "dataFlagId", "dataFlagDescription", "unitName"
        ]
        df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

    # Save CSV using readable activity name
    csv_path = os.path.join(DATA_DIR, f"{activity_name.lower()}.csv")
    df.to_csv(csv_path, index=False)
    print(f"{activity_name} data saved to {csv_path}, total rows: {len(df)}")

    return df

if __name__ == "__main__":
    for name, aid in ACTIVITIES.items():
        fetch_activity(name, aid)

