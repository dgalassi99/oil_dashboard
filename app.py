# app.py
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Oil Stocks Dashboard", layout="wide")
st.title("Oil Stocks Dashboard")

# Load local CSV
DATA_PATH = "data/stocks.csv"
df_stocks = pd.read_csv(DATA_PATH, parse_dates=["period"])

# Sidebar filter: country only
countries = sorted(df_stocks["countryRegionName"].unique())
selected_country = st.sidebar.selectbox("Select Country", countries)

# Filter data
df_plot = df_stocks[
    df_stocks["countryRegionName"] == selected_country
].sort_values("period")

# Time series chart
chart = alt.Chart(df_plot).mark_line().encode(
    x="period:T",
    y="value:Q",
    tooltip=["period:T", "value:Q"]
).properties(title=f"Stocks in {selected_country}")

st.altair_chart(chart, use_container_width=True)

# Optional: show raw data
if st.checkbox("Show raw data"):
    st.dataframe(df_plot)
