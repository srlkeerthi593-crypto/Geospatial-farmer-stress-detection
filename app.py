# =========================================
# 🎮 AGRISTRESS AVENGERS — FINAL STABLE GAME
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import h3

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 NEON GAME UI
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
}
.stMetric {
    background:#021a02;
    border:1px solid #00ff44;
    padding:10px;
    border-radius:10px;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA (FAST)
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
    st.error("❌ Upload dataset")
    st.stop()

# ================================
# YEAR FILTER
# ================================
if "Year" not in df.columns:
    df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

year = st.slider("🕒 Year", 2020, 2024, 2024)
df = df[df["Year"] == year]

# ================================
# FSI CALCULATION
# ================================
df["FSI"] = (
    (1 - df["Rainfall"]) * 0.25 +
    (1 - df["Price"]) * 0.25 +
    (1 - df["Yield"]) * 0.20 +
    df["Cost"] * 0.20 +
    (1 - df["Irrigation"]) * 0.10
)

# ================================
# ADD LIGHT COORDS (FAST)
# ================================
np.random.seed(42)
df["lat"] = np.random.uniform(11.5, 18, len(df))
df["lon"] = np.random.uniform(74, 78.5, len(df))

# ================================
# 🔷 H3 HEX GRID (FIXED VERSION)
# ================================
hex_bins = {}

for _, row in df.iterrows():
    h = h3.latlng_to_cell(row["lat"], row["lon"], 5)
    if h not in hex_bins:
        hex_bins[h] = []
    hex_bins[h].append(row["FSI"])

hex_lats, hex_lons, hex_vals = [], [], []

for h, vals in hex_bins.items():
    lat, lon = h3.cell_to_latlng(h)
    hex_lats.append(lat)
    hex_lons.append(lon)
    hex_vals.append(np.mean(vals))

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

c1, c2 = st.columns(2)
c1.metric("AVG FSI", round(hex_df["FSI"].mean(), 3))
c2.metric("HOTSPOTS", int(hex_df["Hotspot"].sum()))

# ================================
# 🗺️ GAME MAP (FAST HEX)
# ================================
st.subheader("🗺️ MISSION MAP")

fig = go.Figure()

# HEX GRID VISUAL
fig.add_trace(go.Scattermapbox(
    lat=hex_df["lat"],
    lon=hex_df["lon"],
    mode="markers",
    marker=dict(
        size=14,
        color=hex_df["FSI"],
        colorscale="RdYlGn_r",
        opacity=0.85
    ),
    name="Hex Grid"
))

# 🔴 HOTSPOTS
hot = hex_df[hex_df["Hotspot"]]

fig.add_trace(go.Scattermapbox(
    lat=hot["lat"],
    lon=hot["lon"],
    mode="markers",
    marker=dict(
        size=22,
        color="red",
        opacity=0.7
    ),
    name="Hotspots"
))

# 🟢 RADAR LINE (STATIC EFFECT)
fig.add_trace(go.Scattermapbox(
    lat=[14.5, 16],
    lon=[76, 78],
    mode="lines",
    line=dict(color="#00ff88", width=2),
    name="Scan"
))

# MAP SETTINGS
fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=14.5, lon=76),
        zoom=6
    ),
    height=600,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# 🔥 ALERT PANEL
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")

for _, r in hot.iterrows():
    st.error(f"HEX ZONE | FSI = {r['FSI']:.3f}")
