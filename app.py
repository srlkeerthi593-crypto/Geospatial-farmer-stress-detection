import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go
import time

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ─── 🔥 GAMING UI CSS ─────────────────────────
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at center, #021402, #000000);
    color: #00ff88;
}
h1 {
    text-align: center;
    font-size: 42px;
    text-shadow: 0 0 20px #00ff88;
}
.metric-card {
    background: #001a00;
    border: 1px solid #00ff88;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ─────────────────────────
st.markdown("## ⚡ AGRISTRESS AVENGERS ⚡")

# ─── FILE UPLOAD ─────────────────────────
uploaded = st.sidebar.file_uploader("📂 Upload Dataset", type=["csv", "xlsx"])

@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    else:
        return pd.read_excel("agri_dataset_500_samples.xlsx")

df = load_data(uploaded)

# ─── CHECK ─────────────────────────
required = ["Region", "Rainfall", "Price", "Cost", "Yield", "Irrigation"]
if not all(col in df.columns for col in required):
    st.error("Dataset must contain required columns")
    st.stop()

# ─── NORMALIZE ─────────────────────────
scaler = MinMaxScaler()
for col in ["Rainfall", "Price", "Cost", "Yield", "Irrigation"]:
    df[col+"_norm"] = scaler.fit_transform(df[[col]])

# ─── FSI ─────────────────────────
df["FSI"] = (
    0.3 * df["Cost_norm"] +
    0.25 * (1 - df["Yield_norm"]) +
    0.2 * (1 - df["Rainfall_norm"]) +
    0.15 * (1 - df["Irrigation_norm"]) +
    0.1 * (1 - df["Price_norm"])
)

dist = df.groupby("Region", as_index=False)["FSI"].mean()

# ─── CATEGORY ─────────────────────────
dist["Category"] = pd.cut(dist["FSI"],
                         bins=[-1, 0.4, 0.7, 1],
                         labels=["Low", "Medium", "High"])

# ─── KPIs ─────────────────────────
col1, col2, col3 = st.columns(3)

col1.markdown(f'<div class="metric-card">Average FSI<br><h2>{round(dist["FSI"].mean(),3)}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="metric-card">🔥 High Stress<br><h2>{(dist["Category"]=="High").sum()}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="metric-card">📍 Districts<br><h2>{len(dist)}</h2></div>', unsafe_allow_html=True)

# ─── DISTRICT COORDINATES ─────────────────────────
coords = {
    'ANANTAPUR': (14.68,77.60),
    'GUNTUR': (16.30,80.43),
    'KURNOOL': (15.82,78.03),
    'NELLORE': (14.44,79.98),
    'MYSURU': (12.29,76.63),
    'BENGALURU URBAN': (12.97,77.59),
}

dist["lat"] = dist["Region"].map(lambda x: coords.get(x,(None,None))[0])
dist["lon"] = dist["Region"].map(lambda x: coords.get(x,(None,None))[1])
dist = dist.dropna()

# ─── 🚀 RADAR SCAN ANIMATION ─────────────────────────
progress = st.progress(0)

for i in range(100):
    time.sleep(0.01)
    progress.progress(i+1)

st.success("Scan Complete 🔥")

# ─── MAP ─────────────────────────
fig = go.Figure()

colors = {"High":"red","Medium":"yellow","Low":"green"}

for cat in ["High","Medium","Low"]:
    d = dist[dist["Category"]==cat]

    fig.add_trace(go.Scattermapbox(
        lat=d["lat"],
        lon=d["lon"],
        mode="markers",
        marker=dict(
            size=d["FSI"]*80 + 10,
            color=colors[cat],
            opacity=0.8
        ),
        text=d["Region"] + "<br>FSI: " + d["FSI"].round(2).astype(str),
        name=cat
    ))

fig.update_layout(
    mapbox=dict(
        style="open-street-map",
        center=dict(lat=15.5, lon=78),
        zoom=5
    ),
    margin=dict(l=0,r=0,t=0,b=0),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ─── HOTSPOT TABLE ─────────────────────────
st.subheader("🔥 High Stress Zones")
st.dataframe(dist[dist["Category"]=="High"])

# ─── DOWNLOAD ─────────────────────────
st.download_button(
    "⬇ Download Results",
    dist.to_csv(index=False),
    "FSI_results.csv"
)
