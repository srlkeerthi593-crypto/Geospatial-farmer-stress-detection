import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("⚡ AgriStress Avengers - Ultra Fast Dashboard")

# ─── CACHE EVERYTHING ─────────────────────────────

@st.cache_data
def load_dataset(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    return pd.read_csv(file)

@st.cache_data
def load_geojson(file):
    return json.load(file)

@st.cache_data
def prepare_geo_keys(geojson, geo_col):
    keys = []
    for f in geojson["features"]:
        val = str(f["properties"][geo_col]).upper().strip()
        keys.append(val)
    return keys

# ─── SIDEBAR ─────────────────────────────

st.sidebar.header("📂 Upload Files")

data_file = st.sidebar.file_uploader("Dataset", type=["csv", "xlsx"])
geo_file = st.sidebar.file_uploader("GeoJSON", type=["geojson"])

# ─── MAIN ─────────────────────────────

if data_file and geo_file:

    df = load_dataset(data_file)
    geojson = load_geojson(geo_file)

    # ─── COLUMN MATCHING ─────────────────────
    st.subheader("🔗 Column Matching")

    col1, col2 = st.columns(2)

    data_col = col1.selectbox("Dataset District Column", df.columns)
    geo_cols = geojson["features"][0]["properties"].keys()
    geo_col = col2.selectbox("GeoJSON District Column", geo_cols)

    # ─── CLEAN DATA ─────────────────────────
    df[data_col] = df[data_col].astype(str).str.upper().str.strip()

    # ─── CREATE FAST LOOKUP ─────────────────
    geo_keys = prepare_geo_keys(geojson, geo_col)

    df = df[df[data_col].isin(geo_keys)]

    if df.empty:
        st.error("❌ No matching districts")
        st.stop()

    # ─── SELECT NUMERIC COLUMN ──────────────
    num_cols = df.select_dtypes(include="number").columns
    fsi_col = st.selectbox("Select Stress Column", num_cols)

    # ─── ULTRA FAST MAP ─────────────────────
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

    # ─── KPIs ───────────────────────────────
    col1, col2, col3 = st.columns(3)

    col1.metric("Avg Stress", round(df[fsi_col].mean(), 2))
    col2.metric("Max Stress", round(df[fsi_col].max(), 2))
    col3.metric("Min Stress", round(df[fsi_col].min(), 2))

    # ─── TABLE (LIMITED) ────────────────────
    st.subheader("📊 Preview")
    st.dataframe(df[[data_col, fsi_col]].head(30))

else:
    st.info("📂 Upload dataset + geojson to start")
