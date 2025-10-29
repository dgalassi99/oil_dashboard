# Main.py
import streamlit as st
from utils import load_and_clean, load_spot_data

st.set_page_config(page_title="Global Oil Dashboard", layout="wide")
st.title("Global Oil Dashboard")
st.markdown("---")
st.markdown("KPIs: oil production, consumption, and stocks.")


# --- Load datasets ---
prod = load_and_clean("data/production.csv", filter_crude=True)
cons = load_and_clean("data/consumption.csv")
stocks = load_and_clean("data/stocks.csv")

brent, wti, spread, prices = load_spot_data()

# --- Sidebar: select one country per KPI ---
available_countries = sorted(set(prod["countryRegionId"]) | set(cons["countryRegionId"]) | set(stocks["countryRegionId"]))

prod_country = st.sidebar.selectbox("Select Production Country", available_countries, index=available_countries.index("USA") if "USA" in available_countries else 0)
cons_country = st.sidebar.selectbox("Select Consumption Country", available_countries, index=available_countries.index("USA") if "USA" in available_countries else 0)
stocks_country = st.sidebar.selectbox("Select Stocks Country", available_countries, index=available_countries.index("USA") if "USA" in available_countries else 0)

# --- 3 Columns: KPIs ---
col1, col2, col3 = st.columns(3)

# Production KPI
with col1:
    df = prod[prod["countryRegionId"] == prod_country]
    last_val = df["value"].iloc[-1] if not df.empty else 0
    last_chg = df["value"].pct_change().iloc[-1] * 100 if len(df) > 1 else 0
    st.metric(f"Last Month Production ({prod_country})", f"{last_val:.1f} TBPD", f"{last_chg:+.1f}%")

# Consumption KPI
with col2:
    df = cons[cons["countryRegionId"] == cons_country]
    last_val = df["value"].iloc[-1] if not df.empty else 0
    last_chg = df["value"].pct_change().iloc[-1] * 100 if len(df) > 1 else 0
    st.metric(f"Last Month Consumption ({cons_country})", f"{last_val:.1f} TBPD", f"{last_chg:+.1f}%")

# Stocks KPI
with col3:
    df = stocks[stocks["countryRegionId"] == stocks_country]
    last_val = df["value"].iloc[-1] if not df.empty else 0
    last_chg = df["value"].pct_change().iloc[-1] * 100 if len(df) > 1 else 0
    st.metric(f"Last Month Stocks ({stocks_country})", f"{last_val:.1f} MBBL", f"{last_chg:+.1f}%")

st.markdown("---")
st.markdown("KPIs: Brent, WTI and their Spread.")
wti_last = wti.iloc[-1]
brent_last = brent.iloc[-1]
spread_last = spread.iloc[-1]

# --- 3 Columns: KPIs for Spot Prices ---

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("WTI Price", f"{wti_last['value']:.2f} $/BBL", f"{wti_last['change']:.2f}%")
with col2:
    st.metric("Brent Price", f"{brent_last['value']:.2f} $/BBL", f"{brent_last['change']:.2f}%")
with col3:
    st.metric("Spread (Brent - WTI)", f"{spread_last['value']:.2f} $/BBL", f"{spread_last['change']:.2f}%")

st.markdown("---")
st.markdown(
    """
    **Source:** [U.S. Energy Information Administration (EIA) International Data API](https://www.eia.gov/opendata/browser)
    """,
    unsafe_allow_html=True,
)