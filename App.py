import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json

# ─── 1. PAGE CONFIGURATION ───
st.set_page_config(
    page_title="AgriStress Avengers",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. CYBERPUNK GAME UI CSS [Source: 17, 18] ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle, #050a05 0%, #000000 100%);
        color: #00ff88;
        font-family: 'Orbitron', sans-serif;
    }
    .title-text {
        text-align:center;
        font-size:42px;
        font-weight:bold;
        color:#00ff88;
        text-shadow: 0 0 15px #00ff88;
        padding: 20px;
    }
    .status-panel {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid #00ff88;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    /* Style metrics for better visibility */
    [data-testid="stMetricValue"] { color: #00ff88 !important; }
</style>
""", unsafe_allow_html=True)

# ─── 3. SESSION STATE FOR GAME MECHANICS ───
if "xp" not in st.session_state: st.session_state.xp = 0
if "level" not in st.session_state: st.session_state.level = 1
if "log" not in st.session_state: st.session_state.log = ["SYSTEM_READY: Awaiting Intel..."]
if "master_data" not in st.session_state: st.session_state.master_data = None

def add_mission_log(msg, xp_boost=30):
    st.session_state.log.insert(0, f"LOG_{len(st.session_state.log)}: {msg}")
    st.session_state.xp += xp_boost
    if st.session_state.xp >= 100:
        st.session_state.level += 1
        st.session_state.xp = 0
        st.session_state.log.insert(0, "⭐ LEVEL UP: Spatial analysis precision increased!")

# ─── 4. DATA PROCESSING ENGINE [Source: 32, 34, 35] ───
def process_fsi_data(file):
    try:
        xl = pd.ExcelFile(file)
        # Load sheets from your specific dataset [Source: 24, 25]
        df_rain = xl.parse('Rainfall')
        df_yield = xl.parse('Crop_Production')
        df_price = xl.parse('Market_Prices')
        df_cost = xl.parse('Cultivation_Costs')

        # Clean District Names
        for df in [df_rain, df_yield, df_price, df_cost]:
            df['District'] = df['District'].astype(str).str.upper().str.strip()

        # Merge datasets [Source: 32]
        merged = df_rain.merge(df_yield, on=['District', 'Year'], how='inner')
        merged = merged.merge(df_price, on=['District', 'Year'], how='inner')
        merged = merged.merge(df_cost, on=['District', 'Year'], how='inner')

        # Calculate FSI (Farmer Stress Index) [Source: 34]
        # Normalization (0 to 1, where 1 is maximum stress)
        merged['rain_s'] = 1 - (merged['Annual_Rainfall'] / merged['Annual_Rainfall'].max())
        merged['cost_s'] = merged['Cost_of_Cultivation'] / merged['Cost_of_Cultivation'].max()
        merged['yield_s'] = 1 - (merged['Yield_kg_per_ha'] / merged['Yield_kg_per_ha'].max())
        
        # Weighted Index Calculation [Source: 10]
        merged['FSI_Score'] = (merged['rain_s'] * 0.4) + (merged['cost_s'] * 0.3) + (merged['yield_s'] * 0.3)
        
        # Classify Stress Levels [Source: 35]
        merged['Stress_Level'] = pd.cut(merged['FSI_Score'], 
                                        bins=[0, 0.4, 0.7, 1.0], 
                                        labels=['LOW', 'MEDIUM', 'HIGH'])
        return merged
    except Exception as e:
        st.error(f"Scan Failed: {e}")
        return None

# ─── 5. SIDEBAR: AGENT COMMAND CENTER [Source: 27] ───
st.sidebar.markdown("### 🧑‍🚀 AGENT COMMAND")
agent_id = st.sidebar.text_input("Agent Name", "AVENGER_LEAD")

st.sidebar.markdown(f"""
<div class="status-panel">
    <b>RANK:</b> SPATIAL ANALYST<br>
    <b>LEVEL:</b> {st.session_state.level} | <b>XP:</b> {st.session_state.xp}/100
</div>
""", unsafe_allow_html=True)

st.sidebar.header("📥 Intel Upload")
uploaded_data = st.sidebar.file_uploader("Upload Farmer Stress Dataset (.xlsx)", type=["xlsx"])
uploaded_geo = st.sidebar.file_uploader("Upload District GeoJSON", type=["geojson"])

st.sidebar.markdown("---")
threshold = st.sidebar.slider("🔥 Hotspot Threshold", 0.0, 1.0, 0.7)

# ─── 6. MAIN DASHBOARD LAYOUT ───
st.markdown('<div class="title-text">⚡ AGRISTRESS AVENGERS ⚡</div>', unsafe_allow_html=True)

col_map, col_stats = st.columns([3, 2])

with col_stats:
    st.subheader("🎮 Mission Control")
    if uploaded_data:
        if st.button("🚀 LAUNCH SPATIAL SCAN"):
            with st.spinner("Analyzing agricultural stressors..."):
                result = process_fsi_data(uploaded_data)
                if result is not None:
                    st.session_state.master_data = result
                    add_mission_log(f"FSI Scan complete for {len(result)} records.")
    
    if st.session_state.master_data is not None:
        data = st.session_state.master_data
        st.markdown("---")
        st.write("### 📊 Sector Intel")
        m1, m2 = st.columns(2)
        m1.metric("AVG STRESS", f"{data['FSI_Score'].mean():.2f}")
        m2.metric("CRITICAL ZONES", len(data[data['Stress_Level'] == 'HIGH']))
        
        # Stress Drivers Chart [Source: 37, 38]
        st.write("**Primary Driver Analysis**")
        avg_drivers = data[['rain_s', 'cost_s', 'yield_s']].mean()
        st.bar_chart(avg_drivers)

with col_map:
    st.subheader("🗺️ Mission Map: Hotspot Detection")
    if st.session_state.master_data is not None:
        df = st.session_state.master_data
        
        if uploaded_geo:
            geojson_data = json.load(uploaded_geo)
            fig = px.choropleth(
                df,
                geojson=geojson_data,
                locations="District",
                featureidkey="properties.District",
                color="FSI_Score",
                color_continuous_scale="RdYlGn_r",
                range_color=[0, 1],
                template="plotly_dark",
                hover_data=["Stress_Level"]
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please upload GeoJSON to enable Geospatial Mapping.")
            # Fallback bar chart
            fig_bar = px.bar(df.sort_values("FSI_Score", ascending=False).head(10), 
                             x="District", y="FSI_Score", color="Stress_Level",
                             template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("System Idle. Upload files to begin analysis.")

# ─── 7. MISSION LOG (TERMINAL) ───
st.subheader("📋 Mission Log")
terminal_text = "\n".join(st.session_state.log[:6])
st.code(terminal_text, language="bash")

# ─── 8. EXPORT Intel [Source: 38] ───
if st.session_state.master_data is not None:
    csv = st.session_state.master_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Analytical Report", data=csv, file_name="fsi_report.csv", mime="text/csv")
