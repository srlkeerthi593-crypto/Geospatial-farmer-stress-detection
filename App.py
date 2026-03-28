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

# ─── 2. CYBERPUNK GAME UI CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle, #0a1a0a 0%, #050a05 100%);
        color: #00ff88;
        font-family: 'Orbitron', sans-serif;
    }
    .title-text {
        text-align:center;
        font-size:48px;
        font-weight:bold;
        color:#00ff88;
        text-shadow: 0 0 10px #00ff88, 0 0 30px #00ff88;
        padding: 20px;
        border-bottom: 2px solid #00ff88;
        margin-bottom: 25px;
    }
    .status-box {
        background: rgba(0, 255, 136, 0.05);
        border: 1px solid #00ff88;
        padding: 15px;
        border-radius: 10px;
        box-shadow: inset 0 0 10px #00ff88;
        margin-bottom: 20px;
    }
    .stButton>button {
        width: 100%;
        background-color: #00ff88;
        color: #050a05;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00cc6a;
        box-shadow: 0 0 15px #00ff88;
    }
</style>
""", unsafe_allow_html=True)

# ─── 3. SESSION STATE & LOGGING ───
if "xp" not in st.session_state: st.session_state.xp = 0
if "level" not in st.session_state: st.session_state.level = 1
if "log" not in st.session_state: st.session_state.log = ["AVENGER_SYS_READY: Awaiting Intel..."]
if "processed_data" not in st.session_state: st.session_state.processed_data = None

def add_log(msg, xp_gain=25):
    st.session_state.log.insert(0, f"CMD_{len(st.session_state.log)}: {msg}")
    st.session_state.xp += xp_gain
    if st.session_state.xp >= 100:
        st.session_state.level += 1
        st.session_state.xp = 0
        st.session_state.log.insert(0, "🔥 LEVEL UP: Spatial analysis accuracy improved!")

# ─── 4. DATA CORE: FSI MODELLING ENGINE ───
def calculate_fsi(file_upload):
    """Integrates and cleans multiple sheets to generate FSI Score [cite: 31, 32, 34]"""
    try:
        xl = pd.ExcelFile(file_upload)
        
        # Load sheets from your dataset
        df_rain = xl.parse('Rainfall')
        df_yield = xl.parse('Crop_Production')
        df_price = xl.parse('Market_Prices')
        df_cost = xl.parse('Cultivation_Costs')

        # Standardization: District names must match for merging [cite: 32]
        for df in [df_rain, df_yield, df_price, df_cost]:
            df['District'] = df['District'].astype(str).str.upper().str.strip()

        # Merging Logic [cite: 32]
        master = df_rain.merge(df_yield, on=['District', 'Year'], how='inner')
        master = master.merge(df_price, on=['District', 'Year'], how='inner')
        master = master.merge(df_cost, on=['District', 'Year'], how='inner')

        # Stress Normalization (1.0 = High Stress) [cite: 34]
        # Low Rainfall = High Stress
        master['rain_stress'] = 1 - (master['Annual_Rainfall'] - master['Annual_Rainfall'].min()) / (master['Annual_Rainfall'].max() - master['Annual_Rainfall'].min())
        # High Cost = High Stress
        master['cost_stress'] = (master['Cost_of_Cultivation'] - master['Cost_of_Cultivation'].min()) / (master['Cost_of_Cultivation'].max() - master['Cost_of_Cultivation'].min())
        # Low Yield = High Stress
        master['yield_stress'] = 1 - (master['Yield_kg_per_ha'] - master['Yield_kg_per_ha'].min()) / (master['Yield_kg_per_ha'].max() - master['Yield_kg_per_ha'].min())

        # Final Farmer Stress Index (Weighted Average) [cite: 10]
        master['FSI_Score'] = (master['rain_stress'] * 0.4) + (master['cost_stress'] * 0.3) + (master['yield_stress'] * 0.3)

        # Stress Classification [cite: 35]
        master['Stress_Level'] = pd.cut(
            master['FSI_Score'], 
            bins=[0, 0.4, 0.7, 1.0], 
            labels=['LOW', 'MEDIUM', 'HIGH']
        )
        
        return master
    except Exception as e:
        st.error(f"Data Integration Error: {e}")
        return None

# ─── 5. SIDEBAR: AGENT PANEL ───
st.sidebar.markdown("### 🧑‍🚀 AGENT COMMAND")
agent_name = st.sidebar.text_input("Agent ID", "AVENGER_01")

st.sidebar.markdown(f"""
<div class="status-box">
    <b>RANK:</b> SPATIAL ANALYST <br>
    <b>LEVEL:</b> {st.session_state.level} | <b>XP:</b> {st.session_state.xp}/100
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader("📥 Data Intel [cite: 28]")
uploaded_file = st.sidebar.file_uploader("Upload Integrated Excel", type=["xlsx"])
uploaded_geo = st.sidebar.file_uploader("Upload District GeoJSON", type=["geojson"])

st.sidebar.markdown("---")
gi_threshold = st.sidebar.slider("🔥 Hotspot Sensitivity", 0.0, 1.0, 0.65)

# ─── 6. MAIN DASHBOARD ───
st.markdown('<div class="title-text">⚡ AGRISTRESS AVENGERS ⚡</div>', unsafe_allow_html=True)

col_map, col_ctrl = st.columns([3, 2])

with col_ctrl:
    st.markdown("### 🎮 MISSION CONTROL")
    
    if uploaded_file:
        if st.button("🚀 INITIATE SPATIAL SCAN"):
            processed_df = calculate_fsi(uploaded_file)
            if processed_df is not None:
                st.session_state.processed_data = processed_df
                add_log(f"FSI Calculation complete for {len(processed_df)} sectors.")
                st.success("Analysis Complete!")
    else:
        st.warning("Awaiting Dataset Upload...")

    # Statistics Output [cite: 38]
    if st.session_state.processed_data is not None:
        df = st.session_state.processed_data
        st.markdown("---")
        st.subheader("📊 SECTOR ANALYSIS")
        
        c1, c2 = st.columns(2)
        avg_fsi = df['FSI_Score'].mean()
        hotspots = len(df[df['FSI_Score'] > gi_threshold])
        
        c1.metric("AVG STRESS", f"{avg_fsi:.2f}")
        c2.metric("HOTSPOTS", hotspots)
        
        # Primary Stress Driver Detection [cite: 37]
        st.markdown("**Dominant Stress Factors:**")
        drivers = {"Rainfall": df['rain_stress'].mean(), "Cost": df['cost_stress'].mean(), "Yield": df['yield_stress'].mean()}
        st.write(f"Primary Threat: {max(drivers, key=drivers.get)}")

with col_map:
    st.markdown("### 🗺️ BATTLE MAP (HOTSPOTS) [cite: 47]")
    
    if st.session_state.processed_data is not None:
        df = st.session_state.processed_data
        
        if uploaded_geo:
            # Full Geospatial Hotspot Map [cite: 48]
            geo_data = json.load(uploaded_geo)
            fig = px.choropleth(
                df,
                geojson=geo_data,
                locations="District",
                featureidkey="properties.District",
                color="FSI_Score",
                color_continuous_scale="RdYlGn_r",
                range_color=[0, 1],
                hover_data=["Stress_Level", "Annual_Rainfall"],
                template="plotly_dark"
            )
            fig.update_geos(fitbounds="locations", visible=False)
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback Visualization [cite: 38]
            st.info("Upload GeoJSON for district mapping. Showing indicator chart:")
            fig = px.bar(df.sort_values("FSI_Score", ascending=False).head(10), 
                         x="District", y="FSI_Score", color="Stress_Level",
                         template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("System Standby. Please initiate scan to generate mission map.")

# ─── 7. MISSION LOG (TERMINAL STYLE) [cite: 41] ───
st.markdown("---")
st.subheader("📋 MISSION LOG")
log_content = "\n".join(st.session_state.log[:8])
st.code(log_content, language="bash")

# ─── 8. EXPORT REPORT [cite: 38] ───
if st.session_state.processed_data is not None:
    csv = st.session_state.processed_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Analytical Summary Report",
        data=csv,
        file_name='agristress_hotspot_report.csv',
        mime='text/csv',
    )
