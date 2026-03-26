import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriStress Avengers",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS – Game HUD Aesthetic ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0f1e;
    color: #c8f0c0;
}

.stApp {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1a0d 50%, #0a0f1e 100%);
}

/* ── Scanline overlay ── */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,255,80,0.02) 2px,
        rgba(0,255,80,0.02) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── Title Block ── */
.game-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.8rem;
    font-weight: 900;
    color: #00ff50;
    text-shadow: 0 0 20px #00ff50, 0 0 40px #00aa30, 0 0 80px #006618;
    letter-spacing: 4px;
    text-align: center;
    padding: 1rem 0 0.2rem;
    animation: flicker 4s infinite;
}
@keyframes flicker {
    0%,95%,100% { opacity:1; }
    96% { opacity:0.85; }
    97% { opacity:1; }
    98% { opacity:0.7; }
}

.game-subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    color: #50aa60;
    text-align: center;
    letter-spacing: 8px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* ── HUD Cards ── */
.hud-card {
    background: linear-gradient(145deg, rgba(0,30,10,0.9), rgba(0,20,5,0.95));
    border: 1px solid #00ff5040;
    border-left: 3px solid #00ff50;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 15px rgba(0,255,80,0.08), inset 0 0 30px rgba(0,255,80,0.03);
    position: relative;
    overflow: hidden;
}
.hud-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 40px; height: 40px;
    border-top: 2px solid #00ff5060;
    border-right: 2px solid #00ff5060;
}

.hud-label {
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem;
    color: #40cc60;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.hud-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #00ff50;
    text-shadow: 0 0 10px #00ff5080;
}

/* ── Stress Level Badges ── */
.badge-low    { background:#003300; border:1px solid #00ff50; color:#00ff50; padding:3px 12px; border-radius:2px; font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:2px; }
.badge-medium { background:#332200; border:1px solid #ffaa00; color:#ffaa00; padding:3px 12px; border-radius:2px; font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:2px; }
.badge-high   { background:#330000; border:1px solid #ff3300; color:#ff3300; padding:3px 12px; border-radius:2px; font-family:'Orbitron',monospace; font-size:0.7rem; letter-spacing:2px; }

/* ── Section Headers ── */
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem;
    color: #00ff50;
    letter-spacing: 4px;
    text-transform: uppercase;
    border-bottom: 1px solid #00ff5030;
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem;
}

/* ── Progress Bar ── */
.stress-bar-wrap { margin: 0.3rem 0 0.8rem; }
.stress-bar-bg   { background:#001a00; border-radius:2px; height:8px; border:1px solid #00ff5030; }
.stress-bar-fill { height:6px; border-radius:1px; margin:1px; transition: width 1s ease; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 3px !important;
    background: linear-gradient(135deg, #003300, #001a00) !important;
    color: #00ff50 !important;
    border: 1px solid #00ff5060 !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.5rem !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 15px rgba(0,255,80,0.1) !important;
    transition: all 0.2s !important;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #004400, #002200) !important;
    box-shadow: 0 0 25px rgba(0,255,80,0.3) !important;
    border-color: #00ff50 !important;
    transform: translateY(-1px) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060d06 0%, #0a0f0a 100%) !important;
    border-right: 1px solid #00ff5020 !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.65rem !important;
    color: #40cc60 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* ── Dataframe ── */
.stDataFrame { border: 1px solid #00ff5030 !important; border-radius: 4px; }

/* ── Alerts ── */
.stAlert { border-radius: 2px !important; border-left: 3px solid #00ff50 !important; background: rgba(0,255,80,0.05) !important; }

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(0,30,10,0.8) !important;
    border: 1px solid #00ff5030 !important;
    border-radius: 4px !important;
    padding: 0.8rem !important;
}

/* ── Mission log ── */
.mission-log {
    background: #040d04;
    border: 1px solid #00ff5025;
    border-radius: 3px;
    padding: 0.8rem 1rem;
    font-family: 'Rajdhani', monospace;
    font-size: 0.9rem;
    color: #40bb50;
    line-height: 1.8;
    max-height: 220px;
    overflow-y: auto;
}
.log-line { color: #30aa40; }
.log-line-warn { color: #ffaa00; }
.log-line-alert { color: #ff4422; }
.log-time { color: #005510; margin-right: 0.5rem; }

/* ── Map placeholder ── */
.map-frame {
    background: linear-gradient(145deg, #040d04, #0a1a0a);
    border: 1px solid #00ff5030;
    border-radius: 4px;
    height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.map-grid {
    position: absolute; inset: 0;
    background-image:
        linear-gradient(rgba(0,255,80,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,80,0.04) 1px, transparent 1px);
    background-size: 30px 30px;
}
.map-center-text {
    font-family: 'Orbitron', monospace;
    color: #00ff5060;
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-align: center;
    z-index: 1;
}

/* ── Radar chart colours ── */
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "fsi_data" not in st.session_state:
    st.session_state.fsi_data = None
if "xp" not in st.session_state:
    st.session_state.xp = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "log" not in st.session_state:
    st.session_state.log = []

def add_log(msg, kind="normal"):
    ts = time.strftime("%H:%M:%S")
    st.session_state.log.insert(0, (ts, msg, kind))
    if len(st.session_state.log) > 20:
        st.session_state.log.pop()

def gain_xp(pts):
    st.session_state.xp += pts
    if st.session_state.xp >= st.session_state.level * 100:
        st.session_state.xp -= st.session_state.level * 100
        st.session_state.level += 1
        add_log(f"LEVEL UP → LEVEL {st.session_state.level}  +{pts} XP", "alert")
    else:
        add_log(f"Mission reward: +{pts} XP", "normal")

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">⚡ AGRISTRESS AVENGERS ⚡</div>', unsafe_allow_html=True)
st.markdown('<div class="game-subtitle">Farmer Stress Intelligence System · FSI Command</div>', unsafe_allow_html=True)

# ─── Sidebar – Agent HUD ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-header">🧑‍🚀 Agent Profile</div>', unsafe_allow_html=True)

    agent_name = st.text_input("AGENT ID", value="FIELD_ANALYST_01",
                                help="Your operative codename")

    xp_pct = int((st.session_state.xp / (st.session_state.level * 100)) * 100)
    st.markdown(f"""
    <div class="hud-card">
        <div class="hud-label">Level</div>
        <div class="hud-value">{st.session_state.level:02d}</div>
        <div class="hud-label" style="margin-top:.5rem;">XP Progress — {st.session_state.xp}/{st.session_state.level*100}</div>
        <div class="stress-bar-bg">
            <div class="stress-bar-fill" style="width:{xp_pct}%; background:linear-gradient(90deg,#00aa30,#00ff50);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🗺 Mission Config</div>', unsafe_allow_html=True)

    selected_state = st.selectbox("TARGET STATE", [
        "Andhra Pradesh", "Karnataka", "Maharashtra",
        "Tamil Nadu", "Uttar Pradesh", "Punjab", "Rajasthan"
    ])

    indicators = st.multiselect("STRESS INDICATORS", [
        "Rainfall Deficit", "Crop Yield Loss", "Market Price Swing",
        "Irrigation Scarcity", "Input Cost Burden", "Soil Degradation"
    ], default=["Rainfall Deficit", "Crop Yield Loss", "Market Price Swing"])

    hotspot_threshold = st.slider("HOTSPOT SENSITIVITY", 0.0, 1.0, 0.7, 0.05,
                                   help="Gi* threshold for spatial autocorrelation")

    year = st.selectbox("DATA YEAR", [2024, 2023, 2022, 2021], index=0)

    st.markdown('<div class="section-header">📡 Data Upload</div>', unsafe_allow_html=True)
    uploaded_csv  = st.file_uploader("AGRICULTURE DATASET (CSV/XLSX)", type=["csv","xlsx"])
    uploaded_shp  = st.file_uploader("BOUNDARY SHAPEFILE (ZIP)", type=["zip"])

# ─── Main Layout: 3 columns ──────────────────────────────────────────────────
col_map, col_ctrl = st.columns([3, 2], gap="medium")

# ── Left: Map Area ──
with col_map:
    st.markdown('<div class="section-header">🛰 Geospatial Hotspot Map</div>', unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        st.markdown("""
        <div class="map-frame">
            <div class="map-grid"></div>
            <div class="map-center-text">
                [ AWAITING SCAN INITIATION ]<br><br>
                <span style="font-size:0.65rem; color:#00ff5040;">
                Configure mission parameters →<br>then launch FSI analysis
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = st.session_state.fsi_data
        import plotly.express as px
        # Bubble map substitute using scatter
        fig = px.scatter(
            df, x="Longitude", y="Latitude",
            size="FSI_Score", color="Stress_Level",
            hover_name="District",
            color_discrete_map={"LOW":"#00ff50","MEDIUM":"#ffaa00","HIGH":"#ff3300"},
            size_max=30,
            title=""
        )
        fig.update_layout(
            paper_bgcolor="rgba(4,13,4,0.0)",
            plot_bgcolor="rgba(4,13,4,0.9)",
            font=dict(family="Rajdhani", color="#00ff50"),
            xaxis=dict(showgrid=True, gridcolor="#00ff5015", title="Longitude"),
            yaxis=dict(showgrid=True, gridcolor="#00ff5015", title="Latitude"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#00ff50")),
            margin=dict(l=0,r=0,t=0,b=0),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)

    # FSI Table
    if st.session_state.analysis_done:
        st.markdown('<div class="section-header">📊 FSI District Scorecard</div>', unsafe_allow_html=True)
        df = st.session_state.fsi_data
        def color_stress(val):
            if val == "HIGH":   return "color: #ff3300; font-weight:bold"
            if val == "MEDIUM": return "color: #ffaa00; font-weight:bold"
            return "color: #00ff50; font-weight:bold"

        styled = df[["District","FSI_Score","Stress_Level","Hotspot"]].style\
            .applymap(color_stress, subset=["Stress_Level"])\
            .format({"FSI_Score": "{:.2f}"})\
            .set_properties(**{"background-color":"#040d04","color":"#c8f0c0"})
        st.dataframe(styled, use_container_width=True, height=220)

# ── Right: Control Panel ──
with col_ctrl:
    st.markdown('<div class="section-header">⚙ Mission Control</div>', unsafe_allow_html=True)

    # Stats summary
    if st.session_state.analysis_done:
        df = st.session_state.fsi_data
        n_high   = (df.Stress_Level == "HIGH").sum()
        n_med    = (df.Stress_Level == "MEDIUM").sum()
        n_low    = (df.Stress_Level == "LOW").sum()
        avg_fsi  = df.FSI_Score.mean()
        n_hot    = df.Hotspot.sum()

        c1, c2 = st.columns(2)
        c1.metric("AVG FSI", f"{avg_fsi:.2f}", delta=f"{'⚠ HIGH' if avg_fsi>0.6 else '✓ OK'}")
        c2.metric("HOTSPOTS", int(n_hot), delta=f"{n_high} critical")

        st.markdown(f"""
        <div class="hud-card" style="margin-top:.5rem;">
            <div class="hud-label">Threat Distribution</div>
            <div style="margin-top:.5rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:.3rem;">
                    <span>HIGH STRESS</span><span class="badge-high">■ {n_high} districts</span>
                </div>
                <div class="stress-bar-bg"><div class="stress-bar-fill"
                    style="width:{int(n_high/len(df)*100)}%;background:#ff3300;"></div></div>
                <div style="display:flex; justify-content:space-between; margin:.5rem 0 .3rem;">
                    <span>MEDIUM</span><span class="badge-medium">■ {n_med} districts</span>
                </div>
                <div class="stress-bar-bg"><div class="stress-bar-fill"
                    style="width:{int(n_med/len(df)*100)}%;background:#ffaa00;"></div></div>
                <div style="display:flex; justify-content:space-between; margin:.5rem 0 .3rem;">
                    <span>LOW</span><span class="badge-low">■ {n_low} districts</span>
                </div>
                <div class="stress-bar-bg"><div class="stress-bar-fill"
                    style="width:{int(n_low/len(df)*100)}%;background:#00ff50;"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Buttons ──
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚀 LAUNCH FSI SCAN"):
            if not indicators:
                st.warning("Select at least one indicator.")
            else:
                with st.spinner("Running spatial analysis..."):
                    time.sleep(1.5)   # simulate processing

                # ── Generate synthetic data ──
                np.random.seed(42)
                n = 20
                districts = [f"District-{i+1:02d}" for i in range(n)]
                fsi = np.random.beta(2, 2, n)
                levels = ["LOW" if v < 0.4 else "MEDIUM" if v < 0.7 else "HIGH" for v in fsi]
                hotspots = fsi > hotspot_threshold

                lat_base = {"Andhra Pradesh":15.9,"Karnataka":15.3,"Maharashtra":19.7,
                            "Tamil Nadu":11.1,"Uttar Pradesh":27.1,
                            "Punjab":31.1,"Rajasthan":27.0}[selected_state]
                lon_base = {"Andhra Pradesh":79.7,"Karnataka":75.7,"Maharashtra":75.7,
                            "Tamil Nadu":78.6,"Uttar Pradesh":80.9,
                            "Punjab":75.3,"Rajasthan":74.2}[selected_state]

                df = pd.DataFrame({
                    "District":   districts,
                    "FSI_Score":  np.round(fsi, 3),
                    "Stress_Level": levels,
                    "Hotspot":    hotspots,
                    "Latitude":   lat_base  + np.random.uniform(-3, 3, n),
                    "Longitude":  lon_base  + np.random.uniform(-3, 3, n),
                    **{ind: np.round(np.random.uniform(0,1,n),2) for ind in indicators}
                })

                st.session_state.fsi_data = df
                st.session_state.analysis_done = True
                gain_xp(50)
                add_log(f"FSI Scan complete — {selected_state} · {n} districts · {int(hotspots.sum())} hotspots", "warn")
                st.rerun()

    with b2:
        if st.button("🔄 RESET"):
            st.session_state.analysis_done = False
            st.session_state.fsi_data = None
            add_log("Mission board cleared. Awaiting new scan.", "normal")
            st.rerun()

    # Indicator breakdown radar (bar chart substitute)
    if st.session_state.analysis_done and indicators:
        st.markdown('<div class="section-header">📡 Indicator Breakdown</div>', unsafe_allow_html=True)
        df = st.session_state.fsi_data
        avg_ind = df[indicators].mean().reset_index()
        avg_ind.columns = ["Indicator","Mean Score"]

        import plotly.graph_objects as go
        fig2 = go.Figure(go.Bar(
            x=avg_ind["Mean Score"],
            y=avg_ind["Indicator"],
            orientation="h",
            marker=dict(
                color=avg_ind["Mean Score"],
                colorscale=[[0,"#003300"],[0.5,"#ffaa00"],[1,"#ff3300"]],
                line=dict(color="#00ff5030", width=1)
            ),
            text=[f"{v:.2f}" for v in avg_ind["Mean Score"]],
            textposition="outside",
            textfont=dict(color="#c8f0c0", family="Rajdhani")
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(4,13,4,0.9)",
            font=dict(family="Rajdhani", color="#c8f0c0", size=12),
            xaxis=dict(showgrid=True, gridcolor="#00ff5015", range=[0,1.2]),
            yaxis=dict(showgrid=False),
            margin=dict(l=0,r=40,t=5,b=5),
            height=180
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Download button
    if st.session_state.analysis_done:
        csv = st.session_state.fsi_data.to_csv(index=False)
        st.download_button(
            label="⬇ EXPORT REPORT (CSV)",
            data=csv,
            file_name=f"FSI_{selected_state}_{year}.csv",
            mime="text/csv"
        )
        gain_xp_on_download = False   # prevent re-running XP on rerenders

# ─── Mission Log ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Mission Log</div>', unsafe_allow_html=True)

if not st.session_state.log:
    add_log("System online. Awaiting mission parameters.", "normal")

log_html = "<div class='mission-log'>"
for ts, msg, kind in st.session_state.log:
    cls = {"normal":"log-line","warn":"log-line-warn","alert":"log-line-alert"}[kind]
    icon = {"normal":"›","warn":"⚠","alert":"★"}[kind]
    log_html += f"<div class='{cls}'><span class='log-time'>[{ts}]</span>{icon} {msg}</div>"
log_html += "</div>"
st.markdown(log_html, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:2rem; padding:1rem;
     border-top:1px solid #00ff5015;
     font-family:'Orbitron',monospace; font-size:0.6rem;
     color:#005510; letter-spacing:3px;">
AGRISTRESS AVENGERS · FSI COMMAND v1.0 · SPATIAL INTELLIGENCE DIVISION
</div>
""", unsafe_allow_html=True)
