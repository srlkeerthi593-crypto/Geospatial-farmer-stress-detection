import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.graph_objects as go

st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ───────── CSS ─────────
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle, #021402, #000000);
    color: #00ff88;
}
h1,h2,h3 { color:#00ff88; text-align:center; }
.card {
    background:#041a04;
    border:1px solid #00ff88;
    padding:10px;
    border-radius:8px;
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

# ───────── CLEAN DATA (IMPORTANT FIX) ─────────
df = df.dropna()
df.columns = df.columns.str.strip()

required = ["Region","Rainfall","Price","Cost","Yield","Irrigation"]
if not all(col in df.columns for col in required):
    st.error("Dataset missing required columns")
    st.stop()

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
dist = df.groupby("Region", as_index=False).mean(numeric_only=True)

# ───────── CATEGORY ─────────
dist["Category"] = pd.cut(
    dist["FSI"],
    bins=[-1,0.4,0.7,1],
    labels=["Low","Medium","High"]
)

# ───────── COORDINATES (AUTO FIX) ─────────
coords = {
    'ANANTAPUR':(14.68,77.60),
    'GUNTUR':(16.30,80.43),
    'KURNOOL':(15.82,78.03),
    'NELLORE':(14.44,79.98),
    'MYSURU':(12.29,76.63),
    'BENGALURU URBAN':(12.97,77.59),
}

dist["lat"] = dist["Region"].map(lambda x: coords.get(x,(None,None))[0])
dist["lon"] = dist["Region"].map(lambda x: coords.get(x,(None,None))[1])

# 🔥 IMPORTANT FIX (don’t drop missing → show all data)
dist_map = dist.dropna(subset=["lat","lon"])

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

# ───────── MAIN LAYOUT ─────────
left, center, right = st.columns([1,2,1])

# ───────── LEFT PANEL ─────────
with left:
    st.markdown("### 🧑‍🚀 AGENT PANEL")
    st.markdown('<div class="card">AGENT: FARMER_AI<br>LEVEL: 5<br>XP: ██████░░ 70%</div>', unsafe_allow_html=True)

    if len(dist)>0:
        d = dist.iloc[0]
        st.markdown(f'''
        <div class="card">
        STATE: {d["Region"]}<br>
        RAINFALL: {d["Rainfall"]:.0f}<br>
        YIELD: {d["Yield"]:.1f}<br>
        PRICE: ₹{d["Price"]:.0f}
        </div>
        ''', unsafe_allow_html=True)

# ───────── CENTER MAP ─────────
with center:
    st.markdown("### 🗺️ MISSION MAP")

    fig = go.Figure()

    colors = {"High":"red","Medium":"yellow","Low":"green"}

    for cat,color in colors.items():
        d = dist_map[dist_map["Category"]==cat]

        fig.add_trace(go.Scattermapbox(
            lat=d["lat"],
            lon=d["lon"],
            mode="markers",
            marker=dict(size=d["FSI"]*60+10,color=color),
            text=d["Region"] + "<br>FSI:" + d["FSI"].round(2).astype(str),
            name=cat
        ))

    fig.update_layout(
        mapbox=dict(style="open-street-map",center=dict(lat=15,lon=78),zoom=5),
        margin=dict(l=0,r=0,t=0,b=0),
        height=550
    )

    st.plotly_chart(fig, use_container_width=True)

# ───────── RIGHT PANEL ─────────
with right:
    st.markdown("### 🎛️ CONTROL PANEL")

    if st.button("🚀 Launch Scan"):
        st.success("Scan Complete")

    if st.button("🔄 Reset"):
        st.warning("Reset Done")

    st.download_button("📥 Export", dist.to_csv(index=False), "FSI.csv")

    st.metric("AVG", round(avg,2))
    st.metric("HOTSPOTS", high)

    fig_bar = go.Figure(go.Bar(
        x=["Low","Medium","High"],
        y=[low,med,high],
        marker=dict(color=["green","yellow","red"])
    ))
    fig_bar.update_layout(height=200)
    st.plotly_chart(fig_bar, use_container_width=True)

# ───────── LOG ─────────
st.markdown("### 📜 MISSION LOG")

for _,row in dist.head(5).iterrows():
    st.write(f"⚠ {row['Region']} → {row['Category']} (FSI {row['FSI']:.2f})")
