import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("🌾 AgriStress Avengers - FSI Dashboard")

# ─── CACHE ─────────────────────────────
@st.cache_data
def load_data(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return pd.read_csv(file)

@st.cache_data
def load_geo(file):
    return json.load(file)

# ─── SIDEBAR ─────────────────────────────
st.sidebar.header("📂 Upload Files")

data_file = st.sidebar.file_uploader("Dataset", type=["csv", "xlsx"])
geo_file = st.sidebar.file_uploader("GeoJSON", type=["geojson"])

# ─── MAIN ─────────────────────────────
if data_file and geo_file:

    df = load_data(data_file)
    geojson = load_geo(geo_file)

    st.subheader("🔗 Column Matching")

    col1, col2 = st.columns(2)

    data_col = col1.selectbox("Dataset District Column", df.columns)
    geo_cols = geojson["features"][0]["properties"].keys()
    geo_col = col2.selectbox("GeoJSON District Column", geo_cols)

    # Clean data
    df[data_col] = df[data_col].astype(str).str.upper().str.strip()

    # Get GeoJSON district names
    geo_names = [
        str(f["properties"][geo_col]).upper().strip()
        for f in geojson["features"]
    ]

    # Filter dataset
    df = df[df[data_col].isin(geo_names)]

    if df.empty:
        st.error("❌ District names not matching")
        st.stop()

    # Select numeric column
    num_cols = df.select_dtypes(include="number").columns
    fsi_col = st.selectbox("Select Stress Column", num_cols)

    # Map
    st.subheader("🗺 District Stress Map")

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations=data_col,
        featureidkey=f"properties.{geo_col}",
        color=fsi_col,
        color_continuous_scale="RdYlGn_r"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig, use_container_width=True)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg", round(df[fsi_col].mean(), 2))
    col2.metric("Max", round(df[fsi_col].max(), 2))
    col3.metric("Min", round(df[fsi_col].min(), 2))

    # Table
    st.dataframe(df[[data_col, fsi_col]].head(50))

else:
    st.info("📂 Upload dataset + GeoJSON")
