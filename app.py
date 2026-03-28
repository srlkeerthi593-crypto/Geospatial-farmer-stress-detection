import streamlit as st
import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ───────── UI STYLE ─────────
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle, #021402, #000000);
    color: #00ff88;
}
h1,h2,h3 { color:#00ff88; text-align:center; }
.panel {
    background:#041a04;
    border:1px solid #00ff88;
    padding:12px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

st.title("⚡ AGRISTRESS AVENGERS ⚡")

# ───────── LOAD DATA ─────────
@st.cache_data
def load_data(file):
    if file:
        return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    else:
        return pd.read_excel("agri_dataset_500_samples.xlsx")

uploaded = st.sidebar.file_uploader("Upload Dataset", type=["csv","xlsx"])
df = load_data(uploaded)

# ───────── LOAD GEOJSON ─────────
with open("india_districts.geojson") as f:
    geojson = json.load(f)

# ───────── CLEAN ─────────
df.columns = df.columns.str.strip()
df = df.dropna()

# ───────── STATE FILTER ─────────
def get_state(region):
    ap = ["ANANTAPUR","GUNTUR","KURNOOL","NELLORE"]
    ka = ["MYSURU","BENGALURU URBAN"]
    if region in ap: return "Andhra Pradesh"
    elif region in ka: return "Karnataka"
    return "Other"

df["State"] = df["Region"].apply(get_state)

state = st.sidebar.selectbox("🌍 Select State", ["All","Andhra Pradesh","Karnataka"])

if state != "All":
    df = df[df["State"] == state]

# ───────── NORMALIZE ─────────
scaler = MinMaxScaler()
for col in ["Rainfall","Price","Cost","Yield","Irrigation"]:
    df[col+"_norm"] = scaler.fit_transform(df[[col]])

# ───────── FSI ─────────
df["FSI"] = (
    0.3 * df["Cost_norm"] +
    0.25 * (1 - df["Yield_norm"]) +
    0.2 * (1 - df["Rainfall_norm"]) +
    0.15 * (1 - df["Irrigation_norm"]) +
    0.1 * (1 - df["Price_norm"])
)

# ───────── GROUP ─────────
dist = df.groupby("Region", as_index=False)["FSI"].mean()

# 🔥 IMPORTANT: MATCH GEOJSON NAMES
dist["Region"] = dist["Region"].str.upper().str.strip()

# ───────── CATEGORY ─────────
dist["Category"] = pd.cut(
    dist["FSI"],
    bins=[-1,0.4,0.7,1],
    labels=["Low","Medium","High"]
)

# ───────── KPIs ─────────
avg = dist["FSI"].mean()
high = (dist["Category"]=="High").sum()
med = (dist["Category"]=="Medium").sum()
low = (dist["Category"]=="Low").sum()

k1,k2,k3,k4 = st.columns(4)
k1.metric("AVG SCORE", round(avg,2))
k2.metric("HIGH", high)
k3.metric("MEDIUM", med)
k4.metric("LOW", low)

# ───────── LAYOUT ─────────
left, center, right = st.columns([1,2,1])

# ───────── LEFT PANEL ─────────
with left:
    st.markdown("### 🧑‍🚀 AGENT PANEL")
    st.markdown('<div class="panel">AGENT: FARMER_AI<br>LEVEL: 5<br>XP: ██████░░</div>', unsafe_allow_html=True)

# ───────── MAP (REAL HEATMAP) ─────────
with center:
    st.markdown("### 🗺️ MISSION MAP")

    fig = px.choropleth(
        dist,
        geojson=geojson,
        locations="Region",
        featureidkey="properties.DISTRICT",  # ⚠️ must match geojson
        color="FSI",
        color_continuous_scale="RdYlGn_r"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin=dict(l=0,r=0,t=0,b=0))

    st.plotly_chart(fig, use_container_width=True)

# ───────── RIGHT PANEL ─────────
with right:
    st.markdown("### 🎛️ CONTROL PANEL")

    st.button("🚀 Launch Scan")
    st.button("🔄 Reset")

    st.download_button("📥 Export", dist.to_csv(index=False), "FSI.csv")

    st.metric("AVG", round(avg,2))
    st.metric("HOTSPOTS", high)

    fig_bar = px.bar(
        x=["Low","Medium","High"],
        y=[low,med,high],
        color=["Low","Medium","High"],
        color_discrete_map={
            "Low":"green",
            "Medium":"yellow",
            "High":"red"
        }
    )
    fig_bar.update_layout(height=200)
    st.plotly_chart(fig_bar, use_container_width=True)

# ───────── LOG ─────────
st.markdown("### 📜 MISSION LOG")

for _,row in dist.head(5).iterrows():
    st.write(f"⚠ {row['Region']} → {row['Category']} (FSI {row['FSI']:.2f})")
