# =========================================
# 🎮 AGRISTRESS AVENGERS — FINAL GAME APP
# =========================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import h3

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 NEON UI (UNCHANGED STYLE)
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
.game-box {
    border:1px solid #00ff44;
    padding:12px;
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
# COORDS (LIGHTWEIGHT)
# ================================
np.random.seed(1)
df["lat"] = np.random.uniform(11.5, 18, len(df))
df["lon"] = np.random.uniform(74, 78.5, len(df))

# ================================
# 🔷 H3 HEX GRID (FIXED)
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
# STRESS LABEL (GAME STYLE)
# ================================
def badge(s):
    if s == "HIGH": return "🔴 HIGH"
    elif s == "MEDIUM": return "🟡 MEDIUM"
    else: return "🟢 LOW"

hex_df["Stress_Label"] = hex_df["Stress"].apply(badge)

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
    customdata=hex_df[["Region","Stress_Label","Reason"]],
    hovertemplate=
    "<b>🎯 %{customdata[0]}</b><br>" +
    "⚡ FSI: %{marker.color:.3f}<br>" +
    "🚨 %{customdata[1]}<br>" +
    "🧠 %{customdata[2]}<extra></extra>"
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
# 🎮 MISSION CONTROL PANEL
# ================================
st.subheader("🎮 MISSION CONTROL")

col1, col2 = st.columns([2,1])

with col1:
    selected = st.selectbox("🔍 Select District", hex_df["Region"].unique())
    sel = hex_df[hex_df["Region"] == selected].iloc[0]

    st.markdown('<div class="game-box">', unsafe_allow_html=True)
    st.markdown(f"""
    **📍 Region:** {sel['Region']}  
    **⚡ FSI Score:** {sel['FSI']:.3f}  
    **🚨 Stress Level:** {sel['Stress_Label']}  
    **🧠 Reason:** {sel['Reason']}  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 🏆 TOP HOTSPOTS")
    top = hex_df.sort_values("FSI", ascending=False).head(5)
    for _, r in top.iterrows():
        st.error(f"{r['Region']} ({r['FSI']:.2f})")

# ================================
# 📊 ANALYTICS
# ================================
st.subheader("📊 STRESS DISTRIBUTION")
st.bar_chart(hex_df["Stress"].value_counts())

# ================================
# 🔥 ALERT PANEL
# ================================
st.subheader("🔥 HIGH STRESS ALERTS")
for _, r in hex_df[hex_df["Stress"]=="HIGH"].iterrows():
    st.error(f"{r['Region']} | FSI = {r['FSI']:.3f}")
