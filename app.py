# ================================
# 🚀 AGRISTRESS AVENGERS — FINAL
# ================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

# Try ML (safe fallback)
try:
    from sklearn.ensemble import RandomForestRegressor
    ML_AVAILABLE = True
except:
    ML_AVAILABLE = False

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 NASA STYLE UI
# ================================
st.markdown("""
<style>
html, body {
    background: radial-gradient(circle at top, #021a02, #000000);
}
h1 {
    color:#00ff88;
    text-align:center;
    font-family:Orbitron;
    text-shadow:0 0 25px #00ff88;
}
.stMetric {
    background:#021a02;
    border:1px solid #00ff44;
    border-radius:10px;
    padding:10px;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 📂 LOAD DATA (FIXED)
# ================================
def load_data():
    if os.path.exists("karnataka_dataset_750_samples.xlsx"):
        return pd.read_excel("karnataka_dataset_750_samples.xlsx")
    return None

df = load_data()

uploaded = st.file_uploader("📂 Upload Dataset (Excel/CSV)", type=["xlsx","csv"])

if uploaded:
    df = pd.read_excel(uploaded)

if df is None:
    st.error("❌ Dataset not found. Upload file or add to repo.")
    st.stop()

# ================================
# LOAD GEOJSON
# ================================
@st.cache_data
def load_geo():
    with open("KARNATAKA_DISTRICTS.geojson") as f:
        return json.load(f)

geojson = load_geo()

# ================================
# YEAR SIMULATION
# ================================
if "Year" not in df.columns:
    df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

year = st.slider("🕒 Select Year", 2020, 2024, 2024)
df = df[df["Year"] == year]

# ================================
# FSI CALCULATION
# ================================
df["FSI"] = (
    (1-df["Rainfall"])*0.25 +
    (1-df["Price"])*0.25 +
    (1-df["Yield"])*0.2 +
    (df["Cost"])*0.2 +
    (1-df["Irrigation"])*0.1
)

# ================================
# NDVI (PROXY)
# ================================
df["NDVI"] = (df["Yield"] + df["Irrigation"]) / 2

# ================================
# AI MODEL (SAFE)
# ================================
if ML_AVAILABLE:
    try:
        model = RandomForestRegressor()
        model.fit(df[["Rainfall","Price","Yield","Cost","Irrigation"]], df["FSI"])
        df["Predicted_FSI"] = model.predict(df[["Rainfall","Price","Yield","Cost","Irrigation"]])
    except:
        df["Predicted_FSI"] = df["FSI"]
else:
    df["Predicted_FSI"] = df["FSI"]

# ================================
# DISTRICT SUMMARY
# ================================
dist = df.groupby("Region").mean(numeric_only=True).reset_index()
dist["Region"] = dist["Region"].str.upper().str.strip()

# FIX GEOJSON NAMES
for f in geojson["features"]:
    name = f["properties"].get("district") or f["properties"].get("name")
    f["properties"]["district_fixed"] = str(name).upper().strip()

# ================================
# CLASSIFICATION
# ================================
p33 = dist["FSI"].quantile(0.33)
p66 = dist["FSI"].quantile(0.66)

dist["Stress"] = dist["FSI"].apply(
    lambda x: "High" if x>=p66 else ("Medium" if x>=p33 else "Low")
)

# ================================
# REASONS
# ================================
def get_reason(r):
    reasons=[]
    if r["Rainfall"]<0.4: reasons.append("Low Rainfall")
    if r["Yield"]<0.4: reasons.append("Low Yield")
    if r["Price"]<0.4: reasons.append("Low Price")
    if r["Cost"]>0.6: reasons.append("High Cost")
    if r["Irrigation"]<0.4: reasons.append("Poor Irrigation")
    return ", ".join(reasons) if reasons else "Balanced"

dist["Reason"] = dist.apply(get_reason, axis=1)

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

# KPIs
c1,c2,c3 = st.columns(3)
c1.metric("Avg FSI", round(dist["FSI"].mean(),3))
c2.metric("Hotspots", (dist["Stress"]=="High").sum())
c3.metric("Districts", len(dist))

# ================================
# 🗺️ HEATMAP
# ================================
st.subheader("🗺️ Karnataka Stress Heatmap")

fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson,
    locations=dist["Region"],
    featureidkey="properties.district_fixed",
    z=dist["FSI"],
    colorscale=[[0,"#00ff88"],[0.5,"#ffcc00"],[1,"#ff2222"]],
    marker_line_width=0.5,
    customdata=dist[["Stress","Reason"]],
    hovertemplate="<b>%{location}</b><br>FSI:%{z:.3f}<br>%{customdata[0]}<br>%{customdata[1]}"
))

fig.update_layout(
    mapbox_style="carto-darkmatter",
    mapbox_center={"lat":14.5,"lon":76},
    mapbox_zoom=5.8,
    height=550
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# HOTSPOTS
# ================================
st.subheader("🔥 High Stress Districts")

hot = dist[dist["Stress"]=="High"].sort_values("FSI", ascending=False)

for _,r in hot.iterrows():
    st.error(f"{r['Region']} | FSI={r['FSI']:.3f} | {r['Reason']}")

# ================================
# AI VISUAL
# ================================
st.subheader("🤖 AI Predicted Stress")

st.bar_chart(dist.set_index("Region")["Predicted_FSI"])

# ================================
# NDVI VISUAL
# ================================
st.subheader("📡 NDVI (Vegetation Health Proxy)")

st.bar_chart(dist.set_index("Region")["NDVI"])

# ================================
# DATA TABLE
# ================================
st.subheader("📊 Full Data")

st.dataframe(dist)
