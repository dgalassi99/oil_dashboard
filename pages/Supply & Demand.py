import streamlit as st
import pandas as pd
import plotly.express as px
from utils import apply_time_filter_snd, load_and_clean, plot_section

st.title("International Crude Market Overview")
st.subheader("Production, Consumption, and Stocks Monthly Time Series")

# Sidebar: time range
time_filter = st.sidebar.radio(
    "Select Time Range",["All", "Last 1 Year", "Last 5 Years", "Last 10 Years"],index=1)

# Load datasets
prod = load_and_clean("data/production.csv", filter_crude=True)
cons = load_and_clean("data/consumption.csv")
stocks = load_and_clean("data/stocks.csv")

# Apply time filter
prod = apply_time_filter_snd(prod, time_filter)
cons = apply_time_filter_snd(cons, time_filter)
stocks = apply_time_filter_snd(stocks, time_filter)

# Global sidebar countries
available_countries = sorted(set(prod["countryRegionId"]) | set(cons["countryRegionId"]) | set(stocks["countryRegionId"]))
global_countries = st.sidebar.multiselect("Select countries (global)",available_countries,["USA", "OPEC"])

# Layout: 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    prod_countries = st.multiselect("Countries for Production", available_countries, global_countries, key="prod_select")
    plot_section(prod, "Production", prod_countries, global_countries)

with col2:
    cons_countries = st.multiselect("Countries for Consumption", available_countries, global_countries, key="cons_select")
    plot_section(cons, "Consumption", cons_countries, global_countries)

with col3:
    stocks_countries = st.multiselect("Countries for Stocks", available_countries, global_countries, key="stocks_select")
    plot_section(stocks, "Stocks", stocks_countries, global_countries)


# --- Footer ---
st.divider()
st.subheader("Additional Improvements Coming Soon :)")

st.markdown("---")
st.markdown(
    """
    **Source:** [U.S. Energy Information Administration (EIA) International Data API](https://www.eia.gov/opendata/browser/international)
    """,
    unsafe_allow_html=True,
)
