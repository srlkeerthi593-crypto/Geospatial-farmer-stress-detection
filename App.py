import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

st.title("🌾 AgriStress Avengers - FSI Dashboard")

# ─── Upload Section ─────────────────────────────
st.sidebar.header("📂 Upload Files")

uploaded_csv = st.sidebar.file_uploader("Upload Dataset (CSV/XLSX)", type=["csv", "xlsx"])
uploaded_geojson = st.sidebar.file_uploader("Upload GeoJSON (District Boundaries)", type=["geojson"])

# ─── Main Logic ─────────────────────────────
if uploaded_csv and uploaded_geojson:

    # ---- Read Dataset ----
    try:
        if uploaded_csv.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_csv)
        else:
            df = pd.read_csv(uploaded_csv)

        st.success("✅ Dataset Loaded")

    except Exception as e:
        st.error(f"❌ Dataset Error: {e}")
        st.stop()

    # ---- Read GeoJSON ----
    try:
        geojson = json.load(uploaded_geojson)
        st.success("✅ GeoJSON Loaded")

    except Exception as e:
        st.error(f"❌ GeoJSON Error: {e}")
        st.stop()

    # ---- Show columns ----
    st.subheader("🔗 Column Matching")

    col1, col2 = st.columns(2)

    data_col = col1.selectbox("Dataset District Column", df.columns)

    # Try auto-detect geojson property keys
    geo_props = geojson["features"][0]["properties"].keys()
    geo_col = col2.selectbox("GeoJSON District Column", geo_props)

    # ---- Clean Data ----
    df[data_col] = df[data_col].astype(str).str.upper().str.strip()

    # ---- Create mapping ----
    geo_df = pd.json_normalize(geojson["features"])

    geo_df[geo_col] = geo_df[f"properties.{geo_col}"].astype(str).str.upper().str.strip()

    # ---- Merge ----
    merged = geo_df.merge(df, left_on=geo_col, right_on=data_col)

    if merged.empty:
        st.error("❌ No matching districts found. Check names.")
        st.stop()

    st.success("✅ Data Merged Successfully")

    # ---- Select FSI Column ----
    numeric_cols = df.select_dtypes(include="number").columns

    fsi_col = st.selectbox("Select Stress Column", numeric_cols)

    # ---- Map ----
    st.subheader("🗺 District Stress Map")

    fig = px.choropleth(
        merged,
        geojson=geojson,
        locations=merged.index,
        featureidkey=f"properties.{geo_col}",
        color=fsi_col,
        hover_name=data_col,
        color_continuous_scale="RdYlGn_r"
    )

    fig.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig, use_container_width=True)

    # ---- Stats ----
    st.subheader("📊 Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average", round(merged[fsi_col].mean(), 2))
    col2.metric("Max", round(merged[fsi_col].max(), 2))
    col3.metric("Min", round(merged[fsi_col].min(), 2))

    # ---- Table ----
    st.dataframe(merged[[data_col, fsi_col]])

    # ---- Download ----
    st.download_button(
        "⬇ Download Results",
        merged.to_csv(index=False),
        "FSI_Result.csv",
        "text/csv"
    )

else:
    st.info("📂 Upload both dataset and GeoJSON file")
