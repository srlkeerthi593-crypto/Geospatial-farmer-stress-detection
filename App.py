import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import zipfile
import tempfile
import os
import plotly.express as px

# ─── Page Config ─────────────────────────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("🌾 AgriStress Avengers - Farmer Stress Intelligence System")

# ─── Sidebar ─────────────────────────────────────────────
st.sidebar.header("📂 Upload Data")

uploaded_csv = st.sidebar.file_uploader(
    "Upload Dataset (CSV/XLSX)", type=["csv", "xlsx"]
)

uploaded_shp = st.sidebar.file_uploader(
    "Upload Shapefile ZIP", type=["zip"]
)

# ─── Main App ─────────────────────────────────────────────
if uploaded_csv and uploaded_shp:

    # ---------------- READ DATASET ----------------
    try:
        if uploaded_csv.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_csv)
        else:
            df = pd.read_csv(uploaded_csv)

        st.success("✅ Dataset Loaded Successfully")

    except Exception as e:
        st.error(f"❌ Error reading dataset: {e}")
        st.stop()

    # ---------------- READ SHAPEFILE ----------------
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(uploaded_shp, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            shp_file = None
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(".shp"):
                        shp_file = os.path.join(root, file)

            if shp_file is None:
                st.error("❌ No .shp file found in ZIP")
                st.stop()

            gdf = gpd.read_file(shp_file)

        st.success("✅ Shapefile Loaded Successfully")

    except Exception as e:
        st.error(f"❌ Error reading shapefile: {e}")
        st.stop()

    # ---------------- SHOW COLUMNS ----------------
    st.subheader("🔍 Column Matching")

    col1, col2 = st.columns(2)

    with col1:
        data_col = st.selectbox("Select District column (Dataset)", df.columns)

    with col2:
        shp_col = st.selectbox("Select District column (Shapefile)", gdf.columns)

    # ---------------- CLEAN DATA ----------------
    df[data_col] = df[data_col].astype(str).str.upper().str.strip()
    gdf[shp_col] = gdf[shp_col].astype(str).str.upper().str.strip()

    # ---------------- MERGE ----------------
    try:
        merged = gdf.merge(df, left_on=shp_col, right_on=data_col)

        if merged.empty:
            st.error("❌ Merge failed: No matching district names")
            st.stop()

        st.success("✅ Data Merged Successfully")

    except Exception as e:
        st.error(f"❌ Merge Error: {e}")
        st.stop()

    # ---------------- SELECT FSI COLUMN ----------------
    st.subheader("📊 Select Stress Indicator")

    numeric_cols = merged.select_dtypes(include=np.number).columns

    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns found for analysis")
        st.stop()

    fsi_col = st.selectbox("Select FSI / Stress Column", numeric_cols)

    # ---------------- CREATE STRESS LEVEL ----------------
    merged["Stress_Level"] = pd.cut(
        merged[fsi_col],
        bins=[-np.inf, 0.4, 0.7, np.inf],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    # ---------------- MAP ----------------
    st.subheader("🗺 District Stress Map")

    try:
        merged = merged.to_crs(epsg=4326)

        fig = px.choropleth(
            merged,
            geojson=merged.geometry,
            locations=merged.index,
            color=fsi_col,
            hover_name=data_col,
            color_continuous_scale="RdYlGn_r"
        )

        fig.update_geos(fitbounds="locations", visible=False)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Map Error: {e}")

    # ---------------- STATS ----------------
    st.subheader("📈 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Average Stress", round(merged[fsi_col].mean(), 2))
    col2.metric("Max Stress", round(merged[fsi_col].max(), 2))
    col3.metric("Min Stress", round(merged[fsi_col].min(), 2))

    # ---------------- TABLE ----------------
    st.subheader("📋 Data Table")
    st.dataframe(merged[[data_col, fsi_col, "Stress_Level"]])

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "⬇ Download Results",
        merged.to_csv(index=False),
        "FSI_Result.csv",
        "text/csv"
    )

else:
    st.info("📂 Upload both dataset and shapefile to begin")
