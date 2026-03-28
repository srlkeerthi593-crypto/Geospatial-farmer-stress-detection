# =========================================
# 🎮 AGRISTRESS AVENGERS — GAME VERSION
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time
import os

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 GAME UI STYLE
# ================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #021a02, #000000);
    color:#00ff88;
}
h1 {
    text-align:center;
    font-family:Orbitron;
    text-shadow:0 0 20px #00ff88;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA
# ================================
def load_data():
    if os.path.exists("karnataka_dataset_750_samples.xlsx"):
        return pd.read_excel("karnataka_dataset_750_samples.xlsx")
    return None

df = load_data()

uploaded = st.file_uploader("📂 Upload Dataset", type=["xlsx","csv"])
if uploaded:
    df = pd.read_excel(uploaded)

if df is None:
    st.error("Upload dataset")
    st.stop()

# ================================
# LOAD GEOJSON (BOUNDARY)
# ================================
with open("KARNATAKA_DISTRICTS.geojson") as f:
    geojson = json.load(f)

# ================================
# YEAR
# ================================
if "Year" not in df.columns:
    df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

year = st.slider("🕒 Year", 2020, 2024, 2024)
df = df[df["Year"] == year]

# ================================
# FSI
# ================================
df["FSI"] = (
    (1-df["Rainfall"])*0.25 +
    (1-df["Price"])*0.25 +
    (1-df["Yield"])*0.2 +
    df["Cost"]*0.2 +
    (1-df["Irrigation"])*0.1
)

# ================================
# DISTRICT SUMMARY
# ================================
dist = df.groupby("Region").mean(numeric_only=True).reset_index()

# Dummy coordinates (centered Karnataka grid)
np.random.seed(42)
dist["lat"] = np.random.uniform(11.5, 18, len(dist))
dist["lon"] = np.random.uniform(74, 78.5, len(dist))

# ================================
# HOTSPOTS
# ================================
p66 = dist["FSI"].quantile(0.66)
dist["Hotspot"] = dist["FSI"] >= p66

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

# ================================
# 🎯 HEX TILE GENERATION (FAKE HEX)
# ================================
hex_lat, hex_lon, hex_color = [], [], []

for _, row in dist.iterrows():
    for angle in np.linspace(0, 2*np.pi, 7):
        hex_lat.append(row["lat"] + 0.2*np.sin(angle))
        hex_lon.append(row["lon"] + 0.2*np.cos(angle))
        hex_color.append(row["FSI"])

# ================================
# MAP
# ================================
fig = go.Figure()

# HEX GRID LOOK
fig.add_trace(go.Scattermapbox(
    lat=hex_lat,
    lon=hex_lon,
    mode="markers",
    marker=dict(
        size=8,
        color=hex_color,
        colorscale="RdYlGn_r",
        opacity=0.8
    ),
    hoverinfo="skip"
))

# ================================
# 🔴 BLINKING HOTSPOTS
# ================================
pulse = abs(np.sin(time.time()*2))

fig.add_trace(go.Scattermapbox(
    lat=dist[dist["Hotspot"]]["lat"],
    lon=dist[dist["Hotspot"]]["lon"],
    mode="markers",
    marker=dict(
        size=20 + pulse*15,
        color="red",
        opacity=0.9
    ),
    name="Hotspots"
))

# ================================
# 🟢 RADAR SCAN
# ================================
angle = time.time()

scan_lat = [14.5, 14.5 + np.cos(angle)*3]
scan_lon = [76, 76 + np.sin(angle)*3]

fig.add_trace(go.Scattermapbox(
    lat=scan_lat,
    lon=scan_lon,
    mode="lines",
    line=dict(color="#00ff88", width=3),
    name="Scan"
))

# ================================
# 🟩 KARNATAKA BOUNDARY
# ================================
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson,
    locations=[f["properties"]["district"] for f in geojson["features"]],
    z=[0]*len(geojson["features"]),
    featureidkey="properties.district",
    colorscale=[[0,"rgba(0,0,0,0)"],[1,"rgba(0,0,0,0)"]],
    marker_line_color="#00ff88",
    marker_line_width=1.5,
    showscale=False
))

# ================================
# MAP SETTINGS
# ================================
fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=14.5, lon=76),
        zoom=6
    ),
    margin=dict(l=0,r=0,t=0,b=0),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# 🔥 HOTSPOT PANEL
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")

for _, r in dist[dist["Hotspot"]].iterrows():
    st.error(f"{r['Region']} | FSI={r['FSI']:.3f}")
