# pages/US Import Flows.py
import streamlit as st
import pandas as pd
import pydeck as pdk

# --- LOAD DATA --- #
usimpgeo = pd.read_csv("data/geo_us_crude_imports.csv")
us_lat, us_lon = 37.0902, -95.7129  # USA center coordinates

# --- STREAMLIT PAGE --- #
st.set_page_config(layout="wide")
st.title("US Crude Oil Imports Flows")

# Sidebar filters
years = sorted(usimpgeo['period'].str[:4].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", years)
countries = sorted(usimpgeo['originName'].unique())
selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries[:10])

# Filter data
df = usimpgeo[
    (usimpgeo['period'].str.startswith(selected_year)) &
    (usimpgeo['originName'].isin(selected_countries))
]

# Prepare pydeck arcs
df['start'] = df.apply(lambda x: [x['originLon'], x['originLat']], axis=1)
df['end'] = [[us_lon, us_lat]] * len(df)
df['flow_value'] = df['quantity']

# --- PYDECK MAP --- #
arc_layer = pdk.Layer(
    "ArcLayer",
    data=df,
    get_source_position='start',
    get_target_position='end',
    get_source_color=[255, 0, 0, 160],
    get_target_color=[0, 128, 255, 160],
    get_width='flow_value',
    auto_highlight=True,
    pickable=True,
)

view_state = pdk.ViewState(
    longitude=us_lon,
    latitude=us_lat,
    zoom=2,
    pitch=0
)

r = pdk.Deck(
    layers=[arc_layer],
    initial_view_state=view_state,
    tooltip={"text": "{originName}\nQuantity: {quantity}"}
)

st.pydeck_chart(r)
