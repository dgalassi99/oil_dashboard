import streamlit as st
import pandas as pd
import plotly.express as px

#load data
prices = pd.read_csv("data/prices.csv")
prices["period"] = pd.to_datetime(prices["period"], errors="coerce")
prices['value'] = pd.to_numeric(prices['value'], errors='coerce')
prices['change'] = round(prices.groupby('product')['value'].pct_change() * 100, 2)

#
brent = prices[prices['product'] == 'EPCBRENT']
wti = prices[prices['product'] == 'EPCWTI']
spread = brent.set_index('period')['value'] - wti.set_index('period')['value']

st.title("Brent & WTI Spot Prices")
st.markdown(f" Latest Data Available: {prices.period.iloc[-1].date()}")
# --- Layout (3 columns) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.header("WTI Crude Oil")
    st.metric("Price",f"{brent.value.iloc[-1]} $/BBL", f"{brent.change.iloc[-1]}%")

with col2:
    st.header("BRENT Crude Oil")
    st.metric("Price",f"{wti.value.iloc[-1]} $/BBL", f"{wti.change.iloc[-1]}%")
with col3:
    st.header("BRENT-WTI Spread")
    st.metric("Spread",f"{spread.iloc[-1]:.2f} $/BBL", f"{(spread.pct_change().iloc[-1]*100):.2f}%")

