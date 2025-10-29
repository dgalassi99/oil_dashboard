# pages/Spot Prices.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import apply_time_filter, plot_price_chart, plot_returns_with_vol, sub_metrics, aggregate_prices, load_spot_data

# --- DATA --- #
# load prices data
brent, wti, spread, prices = load_spot_data()

# --- GLOBAL USER INPUTS --- #

# timeframe filter input 
time_filter = st.sidebar.radio(
    "Timeframe",["1W", "1M", "3M", "6M", "YTD", "1Y", "5Y", "10Y", "Max"], index=1)

# aggregation frequency input
freq = st.sidebar.radio('Price Aggregation', ['Daily', 'Weekly', 'Monthly'], index=1)
# --- DASHBOARD PAGE --- #

st.set_page_config(layout="wide")
st.title("Brent & WTI Spot Prices")
st.markdown(f"Latest Data Available: {prices['period'].max().date()}")

# Aplly aggregation
brent = aggregate_prices(brent, freq)
wti = aggregate_prices(wti, freq)
spread = aggregate_prices(spread, freq)

# Apply time filter
brent = apply_time_filter(brent, time_filter)
wti = apply_time_filter(wti, time_filter)
spread = apply_time_filter(spread, time_filter)

# 3 columns
col1, col2, col3 = st.columns(3)

# --- WTI ---
with col1:
    st.header("WTI Crude Oil")
    last_val, last_change = wti["value"].iloc[-1], wti["change"].iloc[-1]
    st.metric("Last Close Price", f"{last_val:.2f} $/BBL", f"{last_change:.2f}%")
    sub_metrics(wti, "High", "Low", time_filter, "$/BBL")
    st.markdown("---")
    st.plotly_chart(plot_price_chart(wti,"WTI", "WTI Crude Spot Price", "Close Price ($/BBL)"), use_container_width=True)
    st.markdown("---")
    st.plotly_chart(plot_returns_with_vol(wti, "WTI"), use_container_width=True)

# --- Brent ---
with col2:
    st.header("Brent Crude Oil")
    last_val, last_chg = brent["value"].iloc[-1], brent["change"].iloc[-1]
    st.metric("Last Price", f"{last_val:.2f} $/BBL", f"{last_chg:.2f}%")
    sub_metrics(brent, "High", "Low", time_filter, "$/BBL")
    st.markdown("---")
    st.plotly_chart(plot_price_chart(brent, "Brent","Brent Crude Spot Price", "Close Price ($/BBL)"), use_container_width=True)
    st.markdown("---")
    st.plotly_chart(plot_returns_with_vol(brent, "Brent"), use_container_width=True)

# --- Spread ---
with col3:
    st.header("Brent - WTI Spread")
    last_val, last_chg = spread["value"].iloc[-1], spread["change"].iloc[-1]
    st.metric("Current Spread", f"{last_val:.2f} $/BBL", f"{last_chg:.2f}%")
    sub_metrics(spread, "High", "Low", time_filter, "$/BBL")
    st.markdown("---")
    st.plotly_chart(plot_price_chart(spread, "Spread","Brent-WTI Spread", "Spread ($/BBL)"), use_container_width=True)
    st.markdown("---")
    st.plotly_chart(plot_returns_with_vol(spread, "Spread"), use_container_width=True)


st.markdown("---")
st.markdown(
    """
    **Source:** [U.S. Energy Information Administration (EIA) International Data API](https://www.eia.gov/opendata/browser/petroleum/pri/spt)
    """,
    unsafe_allow_html=True,
)