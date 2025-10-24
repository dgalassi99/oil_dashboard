import streamlit as st

st.set_page_config(page_title="Oil Dashboard", layout="wide")

st.title("Global Oil Dashboard")

# Create 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Production (OPEC)", "32.5M bbl/day", "+0.8%")
 
with col2:
    st.metric("Consumption (OECD)", "45.2M bbl/day", "-0.3%")

with col3:
    st.metric("Global Stocks", "3.1B bbl", "+1.5%")

st.markdown("---")
st.subheader("Welcome")
st.write(
    "Use the sidebar or the navigation menu above to explore detailed country-level charts "
    "and time-series comparisons."
)
