import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import plotly.express as px

# ─── PAGE CONFIG ─────────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ─── SESSION STATE ─────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "fsi_data" not in st.session_state:
    st.session_state.fsi_data = None

# ─── HEADER ─────────────────────────────
st.title("⚡ AGRISTRESS AVENGERS ⚡")
st.caption("Farmer Stress Intelligence System")

# ─── SIDEBAR ─────────────────────────────
st.sidebar.header("⚙ Mission Config")

uploaded_csv = st.sidebar.file_uploader("Upload Dataset (CSV/XLSX)", type=["csv", "xlsx"])
uploaded_geojson = st.sidebar.file_uploader("Upload GeoJSON", type=["geojson"])

hotspot_threshold = st.sidebar.slider("Hotspot Threshold", 0.0, 1.0, 0.7)

# ─── MAIN LAYOUT ─────────────────────────────
col1, col2 = st.columns([3, 2])

# ─── MAP AREA ─────────────────────────────
with col1:
    st.subheader("🗺 Geospatial Map")

    if not st.session_state.analysis_done:
        st.info("Upload data and click 'Launch FSI Scan'")
    else:
        if uploaded_geojson is not None:
            geojson = json.load(uploaded_geojson)
            df = st.session_state.fsi_data

            fig = px.choropleth(
                df,
                geojson=geojson,
                locations="District",
                featureidkey="properties.District",
                color="FSI_Score",
                color_continuous_scale="RdYlGn_r",
            )

            fig.update_geos(fitbounds="locations", visible=False)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Upload GeoJSON to display map")

# ─── CONTROL PANEL ─────────────────────────────
with col2:
    st.subheader("⚙ Controls")

    if st.button("🚀 LAUNCH FSI SCAN"):

        if uploaded_csv is None:
            st.warning("Upload dataset first")
        else:
            try:
                # ---- Load dataset ----
                if uploaded_csv.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_csv)
                else:
                    df = pd.read_csv(uploaded_csv)

                # ---- Clean ----
                df["District"] = df["District"].astype(str).str.upper().str.strip()

                # ---- Check column ----
                if "FSI_Score" not in df.columns:
                    st.error("Dataset must contain 'FSI_Score'")
                    st.stop()

                # ---- Stress classification ----
                df["Stress_Level"] = [
                    "LOW" if v < 0.4 else "MEDIUM" if v < 0.7 else "HIGH"
                    for v in df["FSI_Score"]
                ]

                df["Hotspot"] = df["FSI_Score"] > hotspot_threshold

                # ---- Save ----
                st.session_state.fsi_data = df
                st.session_state.analysis_done = True

                st.success("✅ Analysis Complete")

                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    # ─── RESULTS ─────────────────────────────
    if st.session_state.analysis_done:
        df = st.session_state.fsi_data

        st.subheader("📊 Summary")

        colA, colB, colC = st.columns(3)
        colA.metric("Average", round(df["FSI_Score"].mean(), 2))
        colB.metric("Max", round(df["FSI_Score"].max(), 2))
        colC.metric("Min", round(df["FSI_Score"].min(), 2))

        st.subheader("📋 Data")
        st.dataframe(df[["District", "FSI_Score", "Stress_Level"]])

        st.download_button(
            "⬇ Download CSV",
            df.to_csv(index=False),
            "FSI_Result.csv",
            "text/csv"
        )
