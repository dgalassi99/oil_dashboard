# utils.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import streamlit as st
import os
import toml

# --- Colors ---
CONFIG_PATH = os.path.join(os.path.dirname(__file__), ".streamlit", "config.toml")
config = toml.load(CONFIG_PATH)
theme = config.get("theme", {})
text_color = theme.get("textColor", "#e2e8f0")
primary_color = theme.get("primaryColor", "#615fff")
bg_color = theme.get("backgroundColor", "#1d293d")
sidebar_bg = theme.get("secondaryBackgroundColor", "#0f172b")
accent_color1 = theme.get("accentColor1", "#F4F754" )
accent_color2 = theme.get("accentColor2", "#CD2C58")

# SPOT ANALYSIS HELPER FUNCTIONS

# --- load spot prices data ---
def load_spot_data():
    prices = pd.read_csv("data/prices.csv")
    prices["period"] = pd.to_datetime(prices["period"], errors="coerce")
    prices["value"] = pd.to_numeric(prices["value"], errors="coerce")
    prices["change"] = round(prices.groupby("product")["value"].pct_change() * 100, 2)

    brent = prices[prices["product"] == "EPCBRENT"].copy()
    wti = prices[prices["product"] == "EPCWTI"].copy()

    spread = brent.set_index("period")["value"] - wti.set_index("period")["value"]
    spread = pd.DataFrame(spread).reset_index()
    spread["value"] = spread["value"].ffill()
    spread.columns = ["period", "value"]
    spread["change"] = round(spread["value"].pct_change() * 100, 2)

    return brent, wti, spread, prices

# --- Time filter ---
def apply_time_filter(df, time_filter):
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

# --- Price chart ---
def plot_price_chart(df, product_name, title, yaxis_title, show_ma=True):
    """
    Plot price chart with optional moving averages.
    
    df: DataFrame with ['period', 'value']
    product_name: str, name of the product for labeling
    title: chart title
    yaxis_title: y-axis label
    show_ma: bool, whether to show moving averages
    fast_ma: int, period of fast MA
    slow_ma: int, period of slow MA
    """
    df = df.copy()
    fig = go.Figure()
    # fast and slow moving averages
    col_fast, col_slow = st.columns([1,1])
    with col_slow:
        slow_k = st.number_input(
            f"Rolling window for {product_name} slow MA",
            min_value=1, max_value=250, value=20, step=1,
            key=f"slow_rolling_{product_name}")
    with col_fast:
        fast_k = st.number_input(
            f"Rolling window for {product_name} fast MA",
            min_value=1, max_value=250, value=20, step=1,
            key=f"fast_rolling_{product_name}")
        # Main price line
    fig.add_trace(go.Scatter(
        x=df['period'],
        y=df['value'],
        mode='lines',
        name='Price',
        line=dict(color=primary_color)
    ))

    if show_ma:
        if fast_k > 0:
            df[f'MA{fast_k}'] = df['value'].rolling(fast_k).mean()
            fig.add_trace(go.Scatter(
                x=df['period'],
                y=df[f'MA{fast_k}'],
                mode='lines',
                name=f'MA{fast_k} (Fast)',
                line=dict(color=accent_color1, dash='dot')
            ))
        if slow_k > 0:
            df[f'MA{slow_k}'] = df['value'].rolling(slow_k).mean()
            fig.add_trace(go.Scatter(
                x=df['period'],
                y=df[f'MA{slow_k}'],
                mode='lines',
                name=f'MA{slow_k} (Slow)',
                line=dict(color=accent_color2, dash='dash')
            ))

    fig.update_layout(
        title=title,
        yaxis_title=yaxis_title,
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    return fig

'''def plot_price_chart(df, title, yaxis_title):
    fig = px.line(df, x="period", y="value", markers=False, title=title)
    fig.update_layout(
        yaxis_title=yaxis_title,
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    return fig
'''
# --- Returns + volatility chart ---
def plot_returns_with_vol(df, product_name):
    df = df.copy()
    df["returns"] = df["value"].pct_change() * 100

    # --- Rolling window input above chart ---
    k = st.number_input(
        f"Rolling window for {product_name} volatility",
        min_value=1, max_value=250, value=20, step=1,
        key=f"rolling_{product_name}"
    )

    df["rolling_std"] = df["returns"].rolling(k).std()
    df["upper"] = df["returns"] + df["rolling_std"]
    df["lower"] = df["returns"] - df["rolling_std"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["period"], y=df["returns"], mode="lines", name="Returns"))
    fig.add_trace(go.Scatter(x=df["period"], y=df["upper"],
                             line=dict(color=accent_color1, dash='dot'), name="+1σ", fill=None,))
    fig.add_trace(go.Scatter(x=df["period"], y=df["lower"],
                             line=dict(color=accent_color2, dash='dot',), name="-1σ", fill=None,))

    fig.update_layout(
        title=f"{product_name} Daily Returns with {k}-period Rolling Volatility",
        yaxis_title="Daily Returns (%)",
        xaxis_title=None,
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="x unified"
    )
    return fig

# --- Sub-metrics (High / Low) ---
def sub_metrics(df, label_high="High", label_low="Low", time_filter_name="Timeframe", unit="$/BBL"):
    if df.empty:
        return
    col_low, col_high = st.columns(2)
    col_high.markdown(f"<p style='font-size:18px; margin:0'>{label_high} ({time_filter_name}): "
                      f"<b>{df['value'].max():.2f} {unit}</b></p>", unsafe_allow_html=True)
    col_low.markdown(f"<p style='font-size:18px; margin:0'>{label_low} ({time_filter_name}): "
                     f"<b>{df['value'].min():.2f} {unit}</b></p>", unsafe_allow_html=True)

# --- Aggregate prices ---
def aggregate_prices(df, freq="Daily"):
    """
    Aggregate single-product daily data to Weekly or Monthly frequency.
    freq: "Daily", "Weekly", or "Monthly"
    """
    df = df.copy()
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df = df.set_index("period")

    if freq == "Weekly":
        df_agg = df.resample("W-FRI").last().reset_index()
    elif freq == "Monthly":
        df_agg = df.resample("M").last().reset_index()
    else:  # Daily
        df_agg = df.reset_index()

    return df_agg


# SUPPLY & DEMAND ANALYSIS HELPERS

# utils.py (Supply & Demand section)

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# --- Apply time filter for monthly S&D data ---
def apply_time_filter_snd(df, time_filter):
    """Filter monthly S&D data based on sidebar selection."""
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

# --- Load and clean CSV data ---
def load_and_clean(path, filter_crude=False):
    df = pd.read_csv(path)
    if filter_crude and "productName" in df.columns:
        df = df[df["productName"] == "Crude oil including lease condensate"]
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[df["value"].notna() & (df["value"] > 0)]
    return df

# --- Plot line + bar section ---
def plot_section(df, title, selected_countries, global_countries):
    """Plot monthly line and last 12-month bar chart for selected countries."""
    if df.empty:
        st.warning(f"No data available for {title}.")
        return

    selected = selected_countries if selected_countries else global_countries
    df = df[df["countryRegionId"].isin(selected)]

    if df.empty:
        st.warning(f"No data available for {title} with the selected countries.")
        return

    # Line chart
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

    # Bar chart: average last 12 months
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


# US IMPORT FLOWS HELPERS

def prepare_sankey_nodes(df, target_name="USA"):
    """
    Prepare Sankey nodes and link indices for Plotly.

    Parameters
    ----------
    df : pd.DataFrame
        Must have columns ['originName', 'quantity'].
    target_name : str
        Name of the target node (default "USA").

    Returns
    -------
    nodes : list
        List of node labels
    source_indices : list
        Source node indices
    target_indices : list
        Target node indices
    values : list
        Link values
    """
    # Nodes
    nodes = list(df['originName'].unique())
    if target_name not in nodes:
        nodes.append(target_name)
    
    # Links
    source_indices = [nodes.index(origin) for origin in df['originName']]
    target_indices = [nodes.index(target_name) for _ in range(len(df))]
    values = df['quantity'].tolist()
    
    return nodes, source_indices, target_indices, values


def plot_sankey(nodes, source_indices, target_indices, values, title="Sankey Diagram"):
    """
    Plot a Sankey diagram with Plotly in Streamlit.

    Parameters
    ----------
    nodes : list
        Node labels
    source_indices : list
        Source node indices
    target_indices : list
        Target node indices
    values : list
        Link values
    title : str
        Chart title
    """
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=nodes, color=primary_color),
        link=dict(source=source_indices, target=target_indices, value=values)
    )])
    fig.update_layout(yaxis_title="Thousand Barrels",
        xaxis_title=None,
        legend_title="Country/Region",
        template="plotly_white",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode=None,
        title={"text": f"{title} Monthly Data", "x": 0.5, "xanchor": "center"},
    )
    return fig

def plot_barchart(df, year_filter, title="Bar Chart"):
    df_sum = df.groupby("originName")["quantity"].sum().sort_values(ascending=False).reset_index()
    fig = go.Figure(go.Bar(
        x=df_sum['originName'],
        y=df_sum['quantity'],
        text=df_sum['quantity'],
        textposition='auto'
    ))
    fig.update_layout(title={"text": f"{title} - {year_filter}", "x": 0.5, "xanchor": "center"},
                      yaxis_title="Thousand Barrels",
                      template="plotly_white",
                      height=500,
        margin=dict(l=20, r=20, t=30, b=20),)
    return fig

