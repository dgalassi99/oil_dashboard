import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import prepare_sankey_nodes, plot_barchart, plot_sankey

# --- Load your data ---
usimp = pd.read_csv("data/us_crude_imports.csv")

# --- Sidebar filters ---
chart_type = st.sidebar.radio("Select chart type", ["Sankey", "Bar Chart"])
year_filter = st.sidebar.selectbox("Select Year", sorted(usimp['period'].str[:4].unique(), reverse=True))
country_filter = st.sidebar.multiselect("Select countries", usimp['originName'].unique(), default=usimp['originName'].unique())

# Apply filters
df_filtered = usimp[usimp['period'].str[:4] == year_filter]
df_filtered = df_filtered[df_filtered['originName'].isin(country_filter)]


# --- Render charts ---
st.title("US Crude Oil Import Flows")
st.markdown(f"You can filter the data by selecting different chart types, years and countries from the sidebar.")

current_max_importer = df_filtered.groupby('originName')['quantity'].sum().idxmax()
max_import_value = df_filtered.groupby('originName')['quantity'].sum().max()
second_max_importer = df_filtered.groupby('originName')['quantity'].sum().nlargest(2).idxmin()
second_import_value = df_filtered.groupby('originName')['quantity'].sum().nlargest(2).min()

col1, col2 = st.columns(2)
with col1:
    st.metric(f"Top Importing Country {current_max_importer}", f"{max_import_value/1000:.0f} Million Barrels")
with col2:
    st.metric(f"Second Top Importing Country {second_max_importer}", f"{second_import_value/1000:.0f} Million Barrels")


if chart_type == "Sankey":
    nodes, src, tgt, vals = prepare_sankey_nodes(df_filtered)
    st.plotly_chart(plot_sankey(nodes, src, tgt, vals, title="US Crude Oil International Imports"), use_container_width=True)
    st.markdown("Each main flow line represents the yearly volume of crude oil imported from a specific country to the USA. Each single subline is a montly flow")
else:
    st.plotly_chart(plot_barchart(df_filtered, year_filter, title="US Crude Oil International Imports"), use_container_width=True)
    st.markdown("Each column represents the total volume of crude oil imported from a specific country to the USA in the selected year.")