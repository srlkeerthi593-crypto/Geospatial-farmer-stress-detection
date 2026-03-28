# ================================
# ⚡ AGRISTRESS AVENGERS FINAL
# ================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import os

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
h1,h2,h3 {
    color:#00ff88;
    font-family:Orbitron;
    text-shadow:0 0 15px #00ff88;
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

uploaded = st.file_uploader("📂 Upload Dataset", type=["xlsx","csv"])

if uploaded:
    df = pd.read_excel(uploaded)

if df is None:
    st.error("Dataset not found")
    st.stop()

# ================================
# DISTRICT COORDS (KARNATAKA)
# ================================
DISTRICT_INFO = {
    'BAGALKOT': (16.1691,75.6965),'BALLARI': (15.1394,76.9214),
    'BELAGAVI': (15.8497,74.4977),'BENGALURU URBAN': (12.9716,77.5946),
    'BIDAR': (17.9104,77.5199),'CHIKKAMAGALURU': (13.3161,75.7720),
    'DAVANAGERE': (14.4644,75.9218),'DHARWAD': (15.4589,75.0078),
    'HASSAN': (13.0072,76.1004),'KOLAR': (13.1360,78.1294),
    'MANDYA': (12.5218,76.8951),'MYSURU': (12.2958,76.6394),
    'RAICHUR': (16.2120,77.3439),'SHIVAMOGGA': (13.9299,75.5681),
    'TUMAKURU': (13.3379,77.1173),'UDUPI': (13.3409,74.7421),
    'VIJAYAPURA': (16.8302,75.7100),'YADGIR': (16.7712,77.1382),
}

# ================================
# YEAR SLIDER
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
dist["Region"] = dist["Region"].str.upper().str.strip()

# ADD COORDS
dist["lat"] = dist["Region"].map(lambda x: DISTRICT_INFO.get(x,(None,None))[0])
dist["lon"] = dist["Region"].map(lambda x: DISTRICT_INFO.get(x,(None,None))[1])

dist = dist.dropna()

# ================================
# HOTSPOTS
# ================================
p66 = dist["FSI"].quantile(0.66)
dist["Hotspot"] = dist["FSI"] >= p66

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

# KPIs
c1,c2 = st.columns(2)
c1.metric("AVG FSI", round(dist["FSI"].mean(),3))
c2.metric("HOTSPOTS", dist["Hotspot"].sum())

# ================================
# 🔥 HEX GRID STYLE MAP
# ================================
st.subheader("🗺️ MISSION MAP")

# Create grid points (HEX-like)
grid_lat, grid_lon, grid_val = [], [], []

for _, row in dist.iterrows():
    for i in range(15):  # density
        grid_lat.append(row["lat"] + np.random.uniform(-0.08,0.08))
        grid_lon.append(row["lon"] + np.random.uniform(-0.08,0.08))
        grid_val.append(row["FSI"])

# MAIN HEAT LAYER
fig = go.Figure()

fig.add_trace(go.Densitymapbox(
    lat=grid_lat,
    lon=grid_lon,
    z=grid_val,
    radius=18,
    colorscale=[
        [0, "#00ff88"],
        [0.4, "#ccff00"],
        [0.6, "#ffcc00"],
        [0.8, "#ff6600"],
        [1, "#ff0000"]
    ],
    opacity=0.9,
))

# ================================
# 🔴 BLINKING HOTSPOTS
# ================================
fig.add_trace(go.Scattermapbox(
    lat=dist[dist["Hotspot"]]["lat"],
    lon=dist[dist["Hotspot"]]["lon"],
    mode="markers",
    marker=dict(
        size=20,
        color="red",
        opacity=0.9
    ),
    name="Hotspots"
))

# ================================
# 🟢 SCAN EFFECT (RADAR LINE)
# ================================
angle = time.time() % 6

scan_lat = [14.5, 14.5 + np.cos(angle)*2]
scan_lon = [76, 76 + np.sin(angle)*2]

fig.add_trace(go.Scattermapbox(
    lat=scan_lat,
    lon=scan_lon,
    mode="lines",
    line=dict(color="#00ff88", width=3),
    name="Scan"
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
    height=550,
    margin=dict(l=0,r=0,t=0,b=0)
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# HOTSPOT LIST
# ================================
st.subheader("🔥 HIGH STRESS DISTRICTS")

for _, r in dist[dist["Hotspot"]].iterrows():
    st.error(f"{r['Region']} | FSI={r['FSI']:.3f}")
