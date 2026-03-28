# =========================================
# 🎮 AGRISTRESS AVENGERS — STABLE GAME
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 UI
# ================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #021a02, #000000);
    color:#00ff88;
}
h1 {
    text-align:center;
    text-shadow:0 0 20px #00ff88;
}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD DATA (SAFE)
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

# Karnataka center coords (lightweight)
np.random.seed(1)
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

# KPIs
c1,c2 = st.columns(2)
c1.metric("AVG FSI", round(dist["FSI"].mean(),3))
c2.metric("HOTSPOTS", dist["Hotspot"].sum())

# ================================
# 🔥 GAME HEATMAP (SAFE VERSION)
# ================================
st.subheader("🗺️ MISSION MAP")

fig = go.Figure()

# Density Heatmap (FAST)
fig.add_trace(go.Densitymapbox(
    lat=dist["lat"],
    lon=dist["lon"],
    z=dist["FSI"],
    radius=25,
    colorscale=[
        [0,"#00ff88"],
        [0.5,"#ffcc00"],
        [1,"#ff0000"]
    ],
    opacity=0.85
))

# Hotspots (pulse look without animation)
fig.add_trace(go.Scattermapbox(
    lat=dist[dist["Hotspot"]]["lat"],
    lon=dist[dist["Hotspot"]]["lon"],
    mode="markers",
    marker=dict(
        size=18,
        color="red",
        opacity=0.9
    ),
    name="Hotspots"
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
    height=550
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# HOTSPOT LIST
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")

for _, r in dist[dist["Hotspot"]].iterrows():
    st.error(f"{r['Region']} | FSI={r['FSI']:.3f}")
