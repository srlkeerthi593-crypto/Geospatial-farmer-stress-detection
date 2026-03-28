# ================================
# ⚡ AGRISTRESS AVENGERS — FINAL UI
# ================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import time
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ================================
# 🎮 NEON GAME UI (UNCHANGED STYLE)
# ================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top, #021a02, #000000);
    color:#00ff88;
}
h1,h2,h3 {color:#00ff88; font-family:Orbitron; text-shadow:0 0 15px #00ff88;}
.block-container {padding:1rem;}
</style>
""", unsafe_allow_html=True)

# ================================
# LOAD FILES
# ================================
@st.cache_data
def load_data():
    return pd.read_excel("karnataka_dataset_750_samples.xlsx")

@st.cache_data
def load_geo():
    with open("KARNATAKA_DISTRICTS.geojson") as f:
        return json.load(f)

df = load_data()
geojson = load_geo()

INDICATORS = ["Rainfall","Price","Yield","Cost","Irrigation"]

# ================================
# 🎬 ANIMATION CONTROLS
# ================================
colA,colB = st.columns([3,1])

with colA:
    year = st.slider("🕒 Select Year", 2020, 2024, 2024)

with colB:
    autoplay = st.button("▶ AUTO PLAY")

if "Year" not in df.columns:
    df["Year"] = np.random.choice([2020,2021,2022,2023,2024], len(df))

# ================================
# HEADER
# ================================
st.markdown("<h1>⚡ AGRISTRESS AVENGERS ⚡</h1>", unsafe_allow_html=True)

# ================================
# FUNCTION TO RUN MODEL + MAP
# ================================
def run_dashboard(df_year):

    # FSI
    df_year["FSI"] = (
        (1-df_year["Rainfall"])*0.25 +
        (1-df_year["Price"])*0.25 +
        (1-df_year["Yield"])*0.2 +
        (df_year["Cost"])*0.2 +
        (1-df_year["Irrigation"])*0.1
    )

    # NDVI
    df_year["NDVI"] = (df_year["Yield"] + df_year["Irrigation"]) / 2

    # AI MODEL
    model = RandomForestRegressor()
    model.fit(df_year[INDICATORS], df_year["FSI"])
    df_year["Predicted_FSI"] = model.predict(df_year[INDICATORS])

    # DISTRICT SUMMARY
    dist = df_year.groupby("Region").mean(numeric_only=True).reset_index()
    dist["Region"] = dist["Region"].str.upper().str.strip()

    # FIX GEOJSON
    for f in geojson["features"]:
        name = f["properties"].get("district") or f["properties"].get("name")
        f["properties"]["district_fixed"] = str(name).upper().strip()

    # CLASSIFY
    p33 = dist["FSI"].quantile(0.33)
    p66 = dist["FSI"].quantile(0.66)

    dist["Stress"] = dist["FSI"].apply(
        lambda x: "High" if x>=p66 else ("Medium" if x>=p33 else "Low")
    )

    # REASONS
    def reason(r):
        res=[]
        if r["Rainfall"]<0.4: res.append("Low Rainfall")
        if r["Yield"]<0.4: res.append("Low Yield")
        if r["Price"]<0.4: res.append("Low Price")
        if r["Cost"]>0.6: res.append("High Cost")
        if r["Irrigation"]<0.4: res.append("Poor Irrigation")
        return ", ".join(res) if res else "Balanced"

    dist["Reason"] = dist.apply(reason, axis=1)

    # KPIs
    c1,c2,c3 = st.columns(3)
    c1.metric("Avg FSI", round(dist["FSI"].mean(),3))
    c2.metric("Hotspots", (dist["Stress"]=="High").sum())
    c3.metric("Districts", len(dist))

    # ================= MAP =================
    st.subheader(f"🔥 Karnataka Heatmap — {int(df_year['Year'].iloc[0])}")

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

    # ================= HOTSPOTS =================
    st.subheader("🔥 High Stress Districts")
    hot = dist[dist["Stress"]=="High"].sort_values("FSI", ascending=False)

    for _,r in hot.iterrows():
        st.error(f"{r['Region']} | FSI={r['FSI']:.3f} | {r['Reason']}")

    # ================= AI =================
    st.subheader("🤖 AI Prediction")
    st.bar_chart(dist.set_index("Region")["Predicted_FSI"])

    # ================= NDVI =================
    st.subheader("📡 NDVI (Vegetation Health)")
    st.bar_chart(dist.set_index("Region")["NDVI"])


# ================================
# RUN NORMAL OR AUTOPLAY
# ================================
if autoplay:
    for y in range(2020,2025):
        st.empty()
        st.write(f"### ▶ Year: {y}")
        run_dashboard(df[df["Year"]==y])
        time.sleep(1.2)
else:
    run_dashboard(df[df["Year"]==year])
