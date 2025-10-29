import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# Example U.S. coords (center of map / destination)
US_COORDS = (39.8283, -98.5795)

# Load your enriched data
usimpgeo = pd.read_csv("data/geo_us_crude_imports.csv")

# Sidebar filters
year_sel = st.sidebar.selectbox("Select Year", sorted(usimpgeo["period"].str[:4].unique()), index=0)
countries_sel = st.sidebar.multiselect(
    "Select origin countries",
    sorted(usimpgeo["originName"].unique()),
    default=[]
)

# Filter data
df = usimpgeo.copy()
df["year"] = df["period"].astype(str).str[:4]
df = df[df["year"] == year_sel]
if countries_sel:
    df = df[df["originName"].isin(countries_sel)]

# Create folium map
m = folium.Map(location=US_COORDS, zoom_start=2)

# Add arrows (as PolyLines) from origins → US
for _, row in df.iterrows():
    lat0, lon0 = row["originLat"], row["originLon"]
    if pd.notna(lat0) and pd.notna(lon0):
        folium.PolyLine(
            locations=[(lat0, lon0), US_COORDS],
            color="blue",
            weight=2 + row["quantity"] * 0.001,  # scale width by quantity
            opacity=0.7,
            dash_array="5,5"
        ).add_to(m)
        # optionally add a marker or popup at origin
        folium.CircleMarker(
            (lat0, lon0),
            radius=3,
            color="red",
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['originName']} → {row['quantity']}"
        ).add_to(m)

# Render in Streamlit
st_data = st_folium(m, width=700, height=500)



