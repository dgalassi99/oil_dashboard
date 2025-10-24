# Spot Prices.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Load data ---
prices = pd.read_csv("data/prices.csv")
prices["period"] = pd.to_datetime(prices["period"], errors="coerce")
prices["value"] = pd.to_numeric(prices["value"], errors="coerce")

# Compute daily % change
prices["change"] = round(prices.groupby("product")["value"].pct_change() * 100, 2)

# Split products
brent = prices[prices["product"] == "EPCBRENT"].copy()
wti = prices[prices["product"] == "EPCWTI"].copy()

# Create spread DataFrame
spread = brent.set_index('period')['value'] - wti.set_index('period')['value']
spread = pd.DataFrame(spread).reset_index()
spread.columns = ['period', 'value']
spread["change"] = round(spread["value"].pct_change() * 100, 2)


# --- 📅 Time range selection ---
time_filter = st.sidebar.radio(
    "Select Time Range",
    ["1W", "1M", "3M", "6M", "YTD", "1Y", "5Y", "10Y", "Max"],
    index=1
)

def apply_time_filter(df):
    if df.empty:
        return df
    df = df.copy()
    max_date = df["period"].max()
    if time_filter == "1W":
        return df[df["period"] >= max_date - pd.DateOffset(weeks=1)]
    elif time_filter == "1M":
        return df[df["period"] >= max_date - pd.DateOffset(months=1)]
    elif time_filter == "3M":
        return df[df["period"] >= max_date - pd.DateOffset(months=3)]
    elif time_filter == "6M":
        return df[df["period"] >= max_date - pd.DateOffset(months=6)]
    elif time_filter == "YTD":
        return df[df["period"] >= datetime(max_date.year, 1, 1)]
    elif time_filter == "1Y":
        return df[df["period"] >= max_date - pd.DateOffset(years=1)]
    elif time_filter == "5Y":
        return df[df["period"] >= max_date - pd.DateOffset(years=5)]
    elif time_filter == "10Y":
        return df[df["period"] >= max_date - pd.DateOffset(years=10)]
    return df 
    # Apply time filter
brent = apply_time_filter(brent)
wti = apply_time_filter(wti)
spread = apply_time_filter(spread)
# --- Layout ---
st.title("Brent & WTI Spot Prices")
st.markdown(f"Latest Data Available: {prices['period'].max().date()}")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("WTI Crude Oil")
    st.metric(
        "Price",
        f"{wti['value'].iloc[-1]:.2f} $/BBL",
        f"{wti['change'].iloc[-1]:.2f}%"
    )
    fig_wti = px.line(wti, x="period", y="value", markers=False)
    fig_wti.update_layout(
        yaxis_title="Close Price ($/BBL)",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    st.plotly_chart(fig_wti, use_container_width=True)

with col2:
    st.header("Brent Crude Oil")
    st.metric(
        "Price",
        f"{brent['value'].iloc[-1]:.2f} $/BBL",
        f"{brent['change'].iloc[-1]:.2f}%"
    )
    fig_brent = px.line(brent, x="period", y="value", markers=False)
    fig_brent.update_layout(
        yaxis_title="Close Price ($/BBL)",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    st.plotly_chart(fig_brent, use_container_width=True)

with col3:
    st.header("Brent - WTI Spread")
    st.metric(
        "Spread",
        f"{spread['value'].iloc[-1]:.2f} $/BBL",
        f"{spread['change'].iloc[-1]:.2f}%"
    )
    fig_spread = px.line(spread, x="period", y="value", markers=False)
    fig_spread.update_layout(
        yaxis_title="Spread ($/BBL)",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    st.plotly_chart(fig_spread, use_container_width=True)
