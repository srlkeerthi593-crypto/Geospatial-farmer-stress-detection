# =========================================
# 🎮 AGRISTRESS AVENGERS — ELITE VERSION
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 NEON UI
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
# LOAD GEOJSON
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
dist["Region"] = dist["Region"].str.upper().str.strip()

# ================================
# MATCH GEOJSON
# ================================
for f in geojson["features"]:
    name = f["properties"].get("district") or f["properties"].get("name")
    f["properties"]["district_fixed"] = str(name).upper().strip()

# ================================
# HOTSPOTS
# ================================
p66 = dist["FSI"].quantile(0.66)
dist["Hotspot"] = dist["FSI"] >= p66

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

c1,c2 = st.columns(2)
c1.metric("AVG FSI", round(dist["FSI"].mean(),3))
c2.metric("HOTSPOTS", dist["Hotspot"].sum())

# ================================
# 🗺️ MAIN GAME MAP
# ================================
st.subheader("🗺️ MISSION MAP")

fig = go.Figure()

# HEATMAP INSIDE KARNATAKA
fig.add_trace(go.Choroplethmapbox(
    geojson=geojson,
    locations=dist["Region"],
    featureidkey="properties.district_fixed",
    z=dist["FSI"],
    colorscale=[
        [0,"#00ff88"],
        [0.5,"#ffcc00"],
        [1,"#ff0000"]
    ],
    marker_line_color="#00ff88",
    marker_line_width=1,
    colorbar_title="FSI"
))

# HOTSPOT GLOW (MULTI LAYER)
hot = dist[dist["Hotspot"]]

fig.add_trace(go.Scattermapbox(
    lat=[np.random.uniform(12,17) for _ in range(len(hot))],
    lon=[np.random.uniform(74,78) for _ in range(len(hot))],
    mode="markers",
    marker=dict(size=25, color="red", opacity=0.4),
    name="Glow"
))

fig.add_trace(go.Scattermapbox(
    lat=[np.random.uniform(12,17) for _ in range(len(hot))],
    lon=[np.random.uniform(74,78) for _ in range(len(hot))],
    mode="markers",
    marker=dict(size=12, color="red", opacity=1),
    name="Hotspot"
))

# SCAN BUTTON
fig.update_layout(
    mapbox=dict(
        style="carto-darkmatter",
        center=dict(lat=14.5, lon=76),
        zoom=6
    ),
    height=600,
    margin=dict(l=0,r=0,t=0,b=0),
    updatemenus=[{
        "type": "buttons",
        "buttons": [{
            "label": "▶ SCAN",
            "method": "animate",
            "args": [None, {"frame": {"duration": 400}}]
        }]
    }]
)

st.plotly_chart(fig, use_container_width=True)

# ================================
# HOTSPOT PANEL
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")

for _, r in hot.iterrows():
    st.error(f"{r['Region']} | FSI={r['FSI']:.3f}")
