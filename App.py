import streamlit as st
import pandas as pd
import json
import plotly.express as px

# ─── PAGE CONFIG ─────────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("🌾 AgriStress Avengers - Farmer Stress Intelligence System")

# ─── SIDEBAR ─────────────────────────────
st.sidebar.header("📂 Upload Files")

uploaded_csv = st.sidebar.file_uploader(
    "Upload Dataset (CSV / XLSX)", type=["csv", "xlsx"]
)

uploaded_geojson = st.sidebar.file_uploader(
    "Upload GeoJSON (District Boundaries)", type=["geojson"]
)

# ─── MAIN LOGIC ─────────────────────────────
if uploaded_csv and uploaded_geojson:

    # ---- READ DATASET ----
    try:
        if uploaded_csv.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_csv)
        else:
            df = pd.read_csv(uploaded_csv)

        st.success("✅ Dataset Loaded Successfully")

    except Exception as e:
        st.error(f"❌ Error reading dataset: {e}")
        st.stop()

    # ---- READ GEOJSON ----
    try:
        geojson = json.load(uploaded_geojson)
        st.success("✅ GeoJSON Loaded Successfully")

    except Exception as e:
        st.error(f"❌ Error reading GeoJSON: {e}")
        st.stop()

    # ---- COLUMN SELECTION ----
    st.subheader("🔗 Match District Columns")

    col1, col2 = st.columns(2)

    data_col = col1.selectbox("Dataset District Column", df.columns)

    geo_props = geojson["features"][0]["properties"].keys()
    geo_col = col2.selectbox("GeoJSON District Column", geo_props)

    # ---- CLEAN DATA ----
    df[data_col] = df[data_col].astype(str).str.upper().str.strip()

    # ---- CONVERT GEOJSON TO DATAFRAME ----
    geo_df = pd.json_normalize(geojson["features"])
    geo_df[geo_col] = geo_df[f"properties.{geo_col}"].astype(str).str.upper().str.strip()

    # ---- MERGE ----
    merged = geo_df.merge(df, left_on=geo_col, right_on=data_col)

    if merged.empty:
        st.error("❌ Merge failed: District names do not match")
        st.stop()

    st.success("✅ Data Merged Successfully")

    # ---- SELECT NUMERIC COLUMN ----
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns found in dataset")
        st.stop()

    fsi_col = st.selectbox("Select Stress / FSI Column", numeric_cols)

    # ---- MAP ----
    st.subheader("🗺 District Stress Map")

    fig = px.choropleth(
        merged,
        geojson=geojson,
        locations=geo_col,
        featureidkey=f"properties.{geo_col}",
        color=fsi_col,
        hover_name=data_col,
        color_continuous_scale="RdYlGn_r"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig, use_container_width=True)

    # ---- SUMMARY ----
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average", round(merged[fsi_col].mean(), 2))
    col2.metric("Maximum", round(merged[fsi_col].max(), 2))
    col3.metric("Minimum", round(merged[fsi_col].min(), 2))

    # ---- TABLE ----
    st.subheader("📋 Data Table")
    st.dataframe(merged[[data_col, fsi_col]])

    # ---- DOWNLOAD ----
    st.download_button(
        "⬇ Download Results",
        merged.to_csv(index=False),
        "FSI_Result.csv",
        "text/csv"
    )

else:
    st.info("📂 Please upload BOTH dataset and GeoJSON file to continue")
