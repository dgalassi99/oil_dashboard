import streamlit as st
import pandas as pd
import plotly.graph_objects as go
#from utils import prepare_sankey_nodes, plot_barchart, plot_sankey

# --- Load your data ---
usimp = pd.read_csv("data/us_crude_imports.csv")

# --- Sidebar filters ---
chart_type = st.sidebar.radio("Select chart type", ["Sankey", "Bar Chart"])
year_filter = st.sidebar.selectbox("Select Year", sorted(usimp['period'].str[:4].unique(), reverse=True))
country_filter = st.sidebar.multiselect("Select countries", usimp['originName'].unique(), default=usimp['originName'].unique())

# Apply filters
df_filtered = usimp[usimp['period'].str[:4] == year_filter]
df_filtered = df_filtered[df_filtered['originName'].isin(country_filter)]

# FUNCTION TO BE REMOVED LATER IDK WHY IT DOES NOT READ UTILS.PY MAYBE BUG IN GITHUB
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
        node=dict(label=nodes, color='firebrick'),
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

#####################################

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