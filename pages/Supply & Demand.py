import streamlit as st
import pandas as pd
import plotly.express as px

st.title("International Crude Market Overview")
st.subheader("Production, Consumption, and Stocks Monthly Time Series")

# --- 📅 Time range selection ---
time_filter = st.sidebar.radio(
    "Select Time Range",
    ["All", "Last 1 Year", "Last 5 Years", "Last 10 Years"],
    index=1
)

def apply_time_filter(df):
    if df.empty:
        return df
    max_date = df["period"].max()
    if time_filter == "Last 1 Year":
        return df[df["period"] >= max_date - pd.DateOffset(years=1)]
    elif time_filter == "Last 5 Years":
        return df[df["period"] >= max_date - pd.DateOffset(years=5)]
    elif time_filter == "Last 10 Years":
        return df[df["period"] >= max_date - pd.DateOffset(years=10)]
    return df


def load_and_clean(path, filter_crude=False):
    df = pd.read_csv(path)
    if filter_crude and "productName" in df.columns:
        df = df[df["productName"] == "Crude oil including lease condensate"]
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[df["value"].notna() & (df["value"] > 0)]
    return df


# --- Load datasets ---
prod = load_and_clean("data/production.csv", filter_crude=True)
cons = load_and_clean("data/consumption.csv")
stocks = load_and_clean("data/stocks.csv")

# --- Apply time filter ---
prod = apply_time_filter(prod)
cons = apply_time_filter(cons)
stocks = apply_time_filter(stocks)

# --- Global sidebar country selection ---
available_countries = sorted(set(prod["countryRegionId"]) | set(cons["countryRegionId"]) | set(stocks["countryRegionId"]))
global_countries = st.sidebar.multiselect(
    "Select countries (global)",
    available_countries,
    ["USA", "OPEC"]
)

def plot_section(df, title, override_selection=None):
    if df.empty:
        st.warning(f"No data available for {title}.")
        return

    selected = override_selection if override_selection else global_countries
    df = df[df["countryRegionId"].isin(selected)]

    if df.empty:
        st.warning(f"No data available for {title} with the selected countries.")
        return

    fig_line = px.line(df, x="period", y="value", color="countryRegionId", markers=True)
    fig_line.update_layout(
        yaxis_title="Thousand Barrels per Day" if title != "Stocks" else "Million Barrels",
        xaxis_title=None,
        legend_title="Country/Region",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified",
        title={"text": f"{title} Monthly Time Series", "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig_line, use_container_width=True)

    last_12m = df["period"].max() - pd.DateOffset(months=12)
    latest = df[df["period"] > last_12m].groupby("countryRegionId")["value"].mean().sort_values(ascending=False)
    fig_bar = px.bar(latest, x=latest.index, y="value")
    fig_bar.update_layout(
        yaxis_title="Thousand Barrels per Day" if title != "Stocks" else "Million Barrels",
        template="plotly_white",
        xaxis_title=None,
        height=250,
        margin=dict(l=20, r=20, t=30, b=20),
        title={"text": f"{title} - Average Last 12 Months", "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# --- Layout (3 columns) ---
col1, col2, col3 = st.columns(3)

with col1:
    prod_countries = st.multiselect("Countries for Production", available_countries, global_countries, key="prod_select")
    plot_section(prod, "Production", prod_countries)

with col2:
    cons_countries = st.multiselect("Countries for Consumption", available_countries, global_countries, key="cons_select")
    plot_section(cons, "Consumption", cons_countries)

with col3:
    stocks_countries = st.multiselect("Countries for Stocks", available_countries, global_countries, key="stocks_select")
    plot_section(stocks, "Stocks", stocks_countries)

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
