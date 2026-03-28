import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.express as px

# ─── PAGE CONFIG ─────────────────────────
st.set_page_config(page_title="AgriStress Avengers", layout="wide")

# ─── CUSTOM GAME UI CSS ─────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050a05, #0a1a0a);
    color: #00ff88;
    font-family: 'Orbitron', sans-serif;
}
.title {
    text-align:center;
    font-size:40px;
    color:#00ff88;
    text-shadow:0 0 20px #00ff88;
}
.panel {
    background:#001a00;
    border:1px solid #00ff88;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────
if "data" not in st.session_state:
    st.session_state.data = None
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "log" not in st.session_state:
    st.session_state.log = []

# ─── FUNCTIONS ─────────────────────────
def add_log(msg):
    st.session_state.log.insert(0, msg)

def gain_xp():
    st.session_state.xp += 50
    if st.session_state.xp >= 100:
        st.session_state.level += 1
        st.session_state.xp = 0
        add_log("🔥 LEVEL UP!")

# ─── HEADER ─────────────────────────
st.markdown('<div class="title">⚡ AGRISTRESS AVENGERS ⚡</div>', unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────
st.sidebar.header("🧑‍🚀 Agent Panel")

agent = st.sidebar.text_input("Agent Name", "FARMER_AI")

st.sidebar.markdown(f"""
<div class="panel">
LEVEL: {st.session_state.level} <br>
XP: {st.session_state.xp}/100
</div>
""", unsafe_allow_html=True)

uploaded_csv = st.sidebar.file_uploader("Upload Dataset", type=["csv","xlsx"])
uploaded_geojson = st.sidebar.file_uploader("Upload GeoJSON", type=["geojson"])

threshold = st.sidebar.slider("Hotspot Threshold", 0.0, 1.0, 0.7)

# ─── LAYOUT ─────────────────────────
col_map, col_ctrl = st.columns([3,2])

# ─── MAP PANEL ─────────────────────────
with col_map:
    st.subheader("🗺 Mission Map")

    if st.session_state.data is not None and uploaded_geojson:
        geojson = json.load(uploaded_geojson)
        df = st.session_state.data

        fig = px.choropleth(
            df,
            geojson=geojson,
            locations="District",
            featureidkey="properties.District",
            color="FSI_Score",
            color_continuous_scale="RdYlGn_r"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload files and start scan")

# ─── CONTROL PANEL ─────────────────────────
with col_ctrl:
    st.subheader("🎮 Control Panel")

    if st.button("🚀 LAUNCH SCAN"):

        if uploaded_csv is None:
            st.warning("Upload dataset first")
        else:
            try:
                # Load data
                if uploaded_csv.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded_csv)
                else:
                    df = pd.read_csv(uploaded_csv)

                st.write("Columns:", df.columns)

                # Dynamic selection
                district_col = st.selectbox("District Column", df.columns)
                value_col = st.selectbox("FSI Column", df.select_dtypes(include=np.number).columns)

                # Clean
                df[district_col] = df[district_col].astype(str).str.upper().str.strip()

                df = df.rename(columns={
                    district_col: "District",
                    value_col: "FSI_Score"
                })

                # Stress levels
                df["Stress"] = pd.cut(
                    df["FSI_Score"],
                    bins=[-1,0.4,0.7,1],
                    labels=["LOW","MEDIUM","HIGH"]
                )

                df["Hotspot"] = df["FSI_Score"] > threshold

                st.session_state.data = df

                gain_xp()
                add_log("Scan completed successfully")

                st.success("✅ Scan Completed")

            except Exception as e:
                st.error(e)

    # ─── STATS ─────────────────────────
    if st.session_state.data is not None:
        df = st.session_state.data

        st.subheader("📊 Stats")

        col1, col2, col3 = st.columns(3)
        col1.metric("AVG", round(df["FSI_Score"].mean(),2))
        col2.metric("MAX", round(df["FSI_Score"].max(),2))
        col3.metric("MIN", round(df["FSI_Score"].min(),2))

# ─── MISSION LOG ─────────────────────────
st.subheader("📋 Mission Log")

for log in st.session_state.log[:8]:
    st.write(f"➡ {log}")
