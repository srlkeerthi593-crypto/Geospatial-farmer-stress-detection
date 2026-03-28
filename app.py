import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

# ─── PAGE CONFIG ─────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ─── SIMPLE GAME UI STYLE ─────────────────────────
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle, #061b06, #020f02);
    color: #00ff88;
}
h1 { text-align: center; color: #00ff88; }
</style>
""", unsafe_allow_html=True)

# ─── DISTRICT GEO INFO ─────────────────────────
DISTRICT_INFO = {
    'ANANTAPUR': {'lat': 14.68, 'lon': 77.60},
    'GUNTUR': {'lat': 16.30, 'lon': 80.43},
    'KURNOOL': {'lat': 15.82, 'lon': 78.03},
    'NELLORE': {'lat': 14.44, 'lon': 79.98},
    'MYSURU': {'lat': 12.29, 'lon': 76.63},
    'BENGALURU URBAN': {'lat': 12.97, 'lon': 77.59},
}

# ─── LOAD DATA ─────────────────────────
@st.cache_data
def load_data(file):
    if file is not None:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    else:
        return pd.read_excel("agri_dataset_500_samples.xlsx")

uploaded = st.sidebar.file_uploader("📂 Upload Dataset", type=["csv", "xlsx"])
df = load_data(uploaded)

# ─── REQUIRED COLUMNS CHECK ─────────────────────────
required = ["Region", "Rainfall", "Price", "Cost", "Yield", "Irrigation"]
if not all(col in df.columns for col in required):
    st.error("Dataset must contain: " + ", ".join(required))
    st.stop()

# ─── NORMALIZATION ─────────────────────────
scaler = MinMaxScaler()

df["Rainfall_norm"] = scaler.fit_transform(df[["Rainfall"]])
df["Price_norm"] = scaler.fit_transform(df[["Price"]])
df["Cost_norm"] = scaler.fit_transform(df[["Cost"]])
df["Yield_norm"] = scaler.fit_transform(df[["Yield"]])
df["Irrigation_norm"] = scaler.fit_transform(df[["Irrigation"]])

# ─── FSI CALCULATION (REALISTIC) ─────────────────────────
df["FSI"] = (
    0.3 * df["Cost_norm"] +
    0.25 * (1 - df["Yield_norm"]) +
    0.2 * (1 - df["Rainfall_norm"]) +
    0.15 * (1 - df["Irrigation_norm"]) +
    0.1 * (1 - df["Price_norm"])
)

# ─── DISTRICT LEVEL ─────────────────────────
dist = df.groupby("Region", as_index=False)["FSI"].mean()

# Add coordinates
dist["lat"] = dist["Region"].map(lambda x: DISTRICT_INFO.get(x, {}).get("lat"))
dist["lon"] = dist["Region"].map(lambda x: DISTRICT_INFO.get(x, {}).get("lon"))
dist = dist.dropna()

# ─── CATEGORY ─────────────────────────
dist["Category"] = pd.cut(
    dist["FSI"],
    bins=[-1, 0.4, 0.7, 1],
    labels=["Low", "Medium", "High"]
)

# ─── KPIs ─────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Average FSI", round(dist["FSI"].mean(), 3))
col2.metric("High Stress", (dist["Category"] == "High").sum())
col3.metric("Districts", len(dist))

# ─── MAP ─────────────────────────
st.title("⚡ AGRISTRESS AVENGERS ⚡")

fig = go.Figure()

colors = {"High": "red", "Medium": "yellow", "Low": "green"}

for cat in ["High", "Medium", "Low"]:
    d = dist[dist["Category"] == cat]
    fig.add_trace(go.Scattermapbox(
        lat=d["lat"],
        lon=d["lon"],
        mode="markers",
        marker=dict(
            size=d["FSI"] * 60 + 10,
            color=colors[cat],
            opacity=0.8
        ),
        text=d["Region"],
        name=cat
    ))

fig.update_layout(
    mapbox=dict(
        style="open-street-map",  # ✅ FIXED
        center=dict(lat=15.5, lon=78),
        zoom=5
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ─── TABLE ─────────────────────────
st.subheader("📊 District Stress Data")
st.dataframe(dist.sort_values("FSI", ascending=False))

# ─── DOWNLOAD ─────────────────────────
st.download_button(
    "⬇ Download Results",
    dist.to_csv(index=False),
    "FSI_results.csv"
)
