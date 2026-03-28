import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px

# ─── PAGE CONFIG ─────────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("🌾 AgriStress Avengers - Farmer Stress Intelligence System")

# ─── SIDEBAR ─────────────────────────────
st.sidebar.header("📂 Upload Files")

uploaded_csv = st.sidebar.file_uploader("Upload Dataset (CSV/XLSX)", type=["csv", "xlsx"])
uploaded_geojson = st.sidebar.file_uploader("Upload GeoJSON (District Boundaries)", type=["geojson"])

hotspot_threshold = st.sidebar.slider("Hotspot Threshold", 0.0, 1.0, 0.7)

# ─── MAIN ─────────────────────────────
if uploaded_csv and uploaded_geojson:

    try:
        # ---- Load dataset ----
        if uploaded_csv.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_csv)
        else:
            df = pd.read_csv(uploaded_csv)

        st.success("✅ Dataset Loaded")

    except Exception as e:
        st.error(f"❌ Dataset Error: {e}")
        st.stop()

    try:
        # ---- Load GeoJSON ----
        geojson = json.load(uploaded_geojson)
        st.success("✅ GeoJSON Loaded")

    except Exception as e:
        st.error(f"❌ GeoJSON Error: {e}")
        st.stop()

    # ─── SHOW COLUMNS ─────────────────────────
    st.subheader("🔗 Match Columns")

    col1, col2 = st.columns(2)

    district_col = col1.selectbox("Select District Column", df.columns)

    numeric_cols = df.select_dtypes(include=np.number).columns
    if len(numeric_cols) == 0:
        st.error("❌ No numeric columns found")
        st.stop()

    fsi_col = col2.selectbox("Select FSI / Stress Column", numeric_cols)

    # ─── CLEAN DATA ─────────────────────────
    df[district_col] = df[district_col].astype(str).str.upper().str.strip()

    # Rename for consistency
    df = df.rename(columns={
        district_col: "District",
        fsi_col: "FSI_Score"
    })

    # ─── OPTIONAL FILTERS ─────────────────────────
    if "State" in df.columns:
        state = st.selectbox("Select State", df["State"].unique())
        df = df[df["State"] == state]

    if "Year" in df.columns:
        year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
        df = df[df["Year"] == year]

    # ─── STRESS CLASSIFICATION ─────────────────────────
    df["Stress_Level"] = pd.cut(
        df["FSI_Score"],
        bins=[-np.inf, 0.4, 0.7, np.inf],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    df["Hotspot"] = df["FSI_Score"] > hotspot_threshold

    # ─── MAP ─────────────────────────
    st.subheader("🗺 District Stress Map")

    try:
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations="District",
            featureidkey="properties.District",
            color="FSI_Score",
            color_continuous_scale="RdYlGn_r",
            hover_name="District"
        )

        fig.update_geos(fitbounds="locations", visible=False)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Map Error: {e}")

    # ─── SUMMARY ─────────────────────────
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Stress", round(df["FSI_Score"].mean(), 2))
    col2.metric("Max Stress", round(df["FSI_Score"].max(), 2))
    col3.metric("Min Stress", round(df["FSI_Score"].min(), 2))

    # ─── TABLE ─────────────────────────
    st.subheader("📋 Data Preview")
    st.dataframe(df[["District", "FSI_Score", "Stress_Level"]].head(50))

    # ─── DOWNLOAD ─────────────────────────
    st.download_button(
        "⬇ Download Results",
        df.to_csv(index=False),
        "FSI_Result.csv",
        "text/csv"
    )

else:
    st.info("📂 Upload BOTH dataset and GeoJSON file to start")
