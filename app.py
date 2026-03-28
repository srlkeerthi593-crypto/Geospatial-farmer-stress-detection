# =========================================
# 🎮 AGRISTRESS AVENGERS — GOD MODE
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os
import h3

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 ADVANCED GAME UI
# ================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #021a02, #000000);
    color:#00ff88;
}
h1 {
    text-align:center;
    text-shadow:0 0 25px #00ff88;
    font-family:Orbitron;
}
.control-box {
    border:1px solid #00ff44;
    padding:10px;
    border-radius:8px;
    background:#021a02;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA
# ================================
@st.cache_data
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
# YEAR CONTROL PANEL
# ================================
col1, col2 = st.columns([3,1])

with col1:
    if "Year" not in df.columns:
        df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

    year = st.slider("🕒 YEAR SELECTOR", 2020, 2024, 2024)

with col2:
    st.markdown('<div class="control-box">🚀 CONTROL PANEL<br>▶ Scan Active</div>', unsafe_allow_html=True)

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
# ADD APPROX COORDS (FAST)
# ================================
np.random.seed(42)
df["lat"] = np.random.uniform(11.5, 18, len(df))
df["lon"] = np.random.uniform(74, 78.5, len(df))

# ================================
# 🔷 H3 HEX GRID
# ================================
hex_bins = {}

for _, row in df.iterrows():
    h = h3.geo_to_h3(row["lat"], row["lon"], 5)
    if h not in hex_bins:
        hex_bins[h] = []
    hex_bins[h].append(row["FSI"])

hex_ids = []
hex_vals = []
hex_lats = []
hex_lons = []

for h, vals in hex_bins.items():
    lat, lon = h3.h3_to_geo(h)
    hex_ids.append(h)
    hex_vals.append(np.mean(vals))
    hex_lats.append(lat)
    hex_lons.append(lon)

hex_df = pd.DataFrame({
    "lat": hex_lats,
    "lon": hex_lons,
    "FSI": hex_vals
})

# ================================
# HOTSPOTS
# ================================
p66 = hex_df["FSI"].quantile(0.66)
hex_df["Hotspot"] = hex_df["FSI"] >= p66

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

c1,c2 = st.columns(2)
c1.metric("AVG FSI", round(hex_df["FSI"].mean(),3))
c2.metric("HOTSPOTS", hex_df["Hotspot"].sum())

# ================================
# 🗺️ HEX MAP (GAME STYLE)
# ================================
st.subheader("🗺️ MISSION MAP")

fig = go.Figure()

# HEX LAYER
fig.add_trace(go.Scattermapbox(
    lat=hex_df["lat"],
    lon=hex_df["lon"],
    mode="markers",
    marker=dict(
        size=14,
        color=hex_df["FSI"],
        colorscale="RdYlGn_r",
        opacity=0.85
    )
))

# ================================
# 🔴 HOTSPOT GLOW
# ================================
hot = hex_df[hex_df["Hotspot"]]

fig.add_trace(go.Scattermapbox(
    lat=hot["lat"],
    lon=hot["lon"],
    mode="markers",
    marker=dict(
        size=22,
        color="red",
        opacity=0.6
    )
))

# ================================
# 🟢 RADAR SWEEP (STATIC STYLE)
# ================================
fig.add_trace(go.Scattermapbox(
    lat=[14.5, 16],
    lon=[76, 78],
    mode="lines",
    line=dict(color="#00ff88", width=2)
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
    height=600,
    margin=dict(l=0,r=0,t=0,b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# 🔥 ALERT PANEL
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")

for _, r in hot.iterrows():
    st.error(f"HEX ZONE | FSI={r['FSI']:.3f}")
