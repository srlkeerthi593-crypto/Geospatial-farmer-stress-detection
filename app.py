# =========================================
# 🎮 AGRISTRESS AVENGERS — INTERACTIVE GAME
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import h3

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 UI
# ================================
st.markdown("""
<style>
html, body {background:#020a02;color:#00ff88;}
h1 {text-align:center;text-shadow:0 0 20px #00ff88;}
.game-box {
    border:1px solid #00ff44;
    padding:10px;
    border-radius:10px;
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

uploaded = st.file_uploader("Upload Dataset", type=["xlsx","csv"])
if uploaded:
    df = pd.read_excel(uploaded)

if df is None:
    st.stop()

# ================================
# YEAR
# ================================
if "Year" not in df.columns:
    df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

year = st.slider("Year", 2020, 2024, 2024)
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
# STRESS CATEGORY
# ================================
p33 = df["FSI"].quantile(0.33)
p66 = df["FSI"].quantile(0.66)

def classify(x):
    if x >= p66: return "HIGH"
    elif x >= p33: return "MEDIUM"
    else: return "LOW"

df["Stress"] = df["FSI"].apply(classify)

# ================================
# REASONS
# ================================
def get_reason(row):
    r=[]
    if row["Rainfall"] < 0.4: r.append("Low Rainfall")
    if row["Yield"] < 0.4: r.append("Low Yield")
    if row["Price"] < 0.4: r.append("Low Price")
    if row["Cost"] > 0.6: r.append("High Cost")
    if row["Irrigation"] < 0.4: r.append("Poor Irrigation")
    return ", ".join(r) if r else "Balanced"

df["Reason"] = df.apply(get_reason, axis=1)

# ================================
# COORDS (REALISTIC CLUSTER)
# ================================
np.random.seed(1)
df["lat"] = np.random.uniform(11.5, 18, len(df))
df["lon"] = np.random.uniform(74, 78.5, len(df))

# ================================
# 🔷 H3 GRID
# ================================
hex_bins = {}

for _, row in df.iterrows():
    h = h3.latlng_to_cell(row["lat"], row["lon"], 5)
    if h not in hex_bins:
        hex_bins[h] = []
    hex_bins[h].append(row)

records = []

for h, rows in hex_bins.items():
    lat, lon = h3.cell_to_latlng(h)
    avg_fsi = np.mean([r["FSI"] for r in rows])

    # take first row for metadata
    r = rows[0]

    records.append({
        "lat": lat,
        "lon": lon,
        "FSI": avg_fsi,
        "Region": r["Region"],
        "Stress": r["Stress"],
        "Reason": r["Reason"]
    })

hex_df = pd.DataFrame(records)

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

# ================================
# MAP
# ================================
fig = go.Figure()

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
    customdata=hex_df[["Region","Stress","Reason"]],
    hovertemplate=
    "<b>%{customdata[0]}</b><br>" +
    "FSI: %{marker.color:.3f}<br>" +
    "Stress: %{customdata[1]}<br>" +
    "Reason: %{customdata[2]}<extra></extra>"
))

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
# GAME INFO PANEL
# ================================
st.subheader("🎮 MISSION INTEL PANEL")

st.markdown('<div class="game-box">', unsafe_allow_html=True)
st.write("🟢 Hover over map to scan districts")
st.write("🔴 Red zones indicate high stress")
st.write("🧠 Reasons show contributing factors")
st.markdown('</div>', unsafe_allow_html=True)
