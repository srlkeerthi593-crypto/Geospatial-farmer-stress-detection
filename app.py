import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="AgriStress Avengers",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GAMING CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #020f02 !important;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at top, #0a1f0a 0%, #020f02 70%) !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #041404 0%, #021002 100%) !important;
    border-right: 1px solid #00ff4130 !important;
}
[data-testid="stSidebar"] * { color: #00ff88 !important; }
[data-testid="stSidebar"] label { color: #00cc66 !important; font-family: 'Share Tech Mono', monospace !important; }

h1, h2, h3, h4 { font-family: 'Orbitron', monospace !important; color: #00ff88 !important; }
p, span, div { color: #44ff88; }

.block-container { padding: 0.5rem 1rem 1rem 1rem !important; }

.game-header {
    background: linear-gradient(135deg, #041a04 0%, #0a2a0a 50%, #041a04 100%);
    border: 2px solid #00ff44;
    border-radius: 4px;
    padding: 12px 20px;
    text-align: center;
    margin-bottom: 10px;
    box-shadow: 0 0 30px #00ff4440, inset 0 0 30px #00ff4410;
    font-family: 'Orbitron', monospace;
}
.game-header h1 {
    color: #00ff88 !important;
    font-size: 2rem !important;
    letter-spacing: 6px;
    text-shadow: 0 0 20px #00ff88, 0 0 40px #00ff4480;
    margin: 0 !important;
}
.game-header p {
    color: #44ff88 !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 3px;
    margin: 4px 0 0 0;
}

/* Agent card styling (left panel like in image) */
.agent-card {
    background: linear-gradient(135deg, #041a04, #0a2a0a);
    border: 2px solid #00ff4460;
    border-radius: 6px;
    padding: 16px 12px;
    text-align: center;
    box-shadow: 0 0 20px #00ff4420, inset 0 0 15px #00ff4408;
    margin-bottom: 12px;
}
.agent-avatar {
    font-size: 3rem;
    display: block;
    margin-bottom: 8px;
    filter: drop-shadow(0 0 10px #00ff88);
}
.agent-name {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    color: #00ff88 !important;
    letter-spacing: 2px;
    font-weight: 700;
}
.agent-level {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #44cc66 !important;
    margin: 4px 0;
}
.xp-bar-container {
    background: #021002;
    border: 1px solid #00ff4430;
    border-radius: 10px;
    height: 10px;
    margin: 6px 0;
    overflow: hidden;
}
.xp-bar {
    height: 100%;
    background: linear-gradient(90deg, #ff2200, #ffaa00, #00ff44);
    border-radius: 10px;
    width: 72%;
}
.agent-stat {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #44cc66 !important;
    text-align: left;
    margin: 3px 0;
}
.agent-stat-val {
    color: #00ff88 !important;
    font-weight: bold;
}

.kpi-card {
    background: linear-gradient(135deg, #041a04, #0a2a0a);
    border: 1px solid #00ff4440;
    border-radius: 4px;
    padding: 14px 10px;
    text-align: center;
    box-shadow: 0 0 15px #00ff4420;
    margin-bottom: 8px;
}
.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #44cc66;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.kpi-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem;
    font-weight: 900;
    color: #00ff88;
    text-shadow: 0 0 10px #00ff88;
}
.kpi-high  { border-color: #ff3333 !important; box-shadow: 0 0 15px #ff333340 !important; }
.kpi-high .kpi-value { color: #ff4444 !important; text-shadow: 0 0 10px #ff4444 !important; }
.kpi-med   { border-color: #ffaa00 !important; box-shadow: 0 0 15px #ffaa0040 !important; }
.kpi-med .kpi-value  { color: #ffcc00 !important; text-shadow: 0 0 10px #ffcc00 !important; }
.kpi-low   { border-color: #00ff44 !important; box-shadow: 0 0 15px #00ff4440 !important; }
.kpi-low .kpi-value  { color: #00ff88 !important; }

.mission-log {
    background: #020f02;
    border: 1px solid #00ff4430;
    border-radius: 4px;
    padding: 10px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    color: #44ff88;
    margin-top: 8px;
    max-height: 280px;
    overflow-y: auto;
}
.log-high   { color: #ff4444; }
.log-med    { color: #ffcc00; }
.log-normal { color: #00ff88; }
.log-info   { color: #44aaff; }
.log-xp     { color: #ffaa00; }

.district-card {
    background: linear-gradient(135deg, #041a04, #081808);
    border: 1px solid #00ff4430;
    border-radius: 4px;
    padding: 8px 12px;
    margin: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
}
.district-high { border-left: 4px solid #ff4444 !important; }
.district-med  { border-left: 4px solid #ffcc00 !important; }
.district-low  { border-left: 4px solid #00ff88 !important; }

div[data-testid="stMetric"] {
    background: #041a04;
    border: 1px solid #00ff4430;
    border-radius: 4px;
    padding: 8px;
}
div[data-testid="stMetric"] label { color: #44cc66 !important; font-family: 'Share Tech Mono', monospace !important; }
div[data-testid="stMetric"] div   { color: #00ff88 !important; font-family: 'Orbitron', monospace !important; }

.stTabs [data-baseweb="tab-list"] { background: #041404; border-bottom: 1px solid #00ff4430; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: #44cc66 !important;
    background: transparent !important;
    border: none !important;
    letter-spacing: 2px;
    font-size: 0.75rem;
}
.stTabs [aria-selected="true"] {
    color: #00ff88 !important;
    border-bottom: 2px solid #00ff88 !important;
    background: #00ff8810 !important;
}

/* Control panel style buttons */
.ctrl-btn {
    display: block;
    background: linear-gradient(135deg, #041a04, #0d300d);
    border: 1px solid #00ff4460;
    border-radius: 4px;
    padding: 8px 12px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    color: #00ff88;
    letter-spacing: 1px;
    margin: 5px 0;
    text-align: left;
    box-shadow: 0 0 8px #00ff4420;
}
.ctrl-btn:hover { border-color: #00ff88; box-shadow: 0 0 15px #00ff4440; }

.scan-complete {
    background: linear-gradient(135deg, #0a1f0a, #041a04);
    border: 1px solid #00ff4440;
    border-radius: 4px;
    padding: 10px;
    text-align: center;
    font-family: 'Orbitron', monospace;
    font-size: 0.9rem;
    color: #00ff88;
    box-shadow: 0 0 20px #00ff4430;
    margin: 8px 0;
    text-shadow: 0 0 10px #00ff88;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { box-shadow: 0 0 20px #00ff4430; }
    50% { box-shadow: 0 0 35px #00ff4460; }
}

section[data-testid="stSidebar"] .stSlider [data-testid="stSliderThumb"] { background: #00ff88 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #020f02; }
::-webkit-scrollbar-thumb { background: #00ff4440; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── CONSTANTS ───────────────────────────────────────────────────
DISTRICT_INFO = {
    'ANANTAPUR':      {'state': 'Andhra Pradesh', 'lat': 14.6819, 'lon': 77.6006},
    'CHITTOOR':       {'state': 'Andhra Pradesh', 'lat': 13.2172, 'lon': 79.1003},
    'EAST GODAVARI':  {'state': 'Andhra Pradesh', 'lat': 17.0005, 'lon': 81.8040},
    'GUNTUR':         {'state': 'Andhra Pradesh', 'lat': 16.3067, 'lon': 80.4365},
    'KRISHNA':        {'state': 'Andhra Pradesh', 'lat': 16.6100, 'lon': 80.7214},
    'KURNOOL':        {'state': 'Andhra Pradesh', 'lat': 15.8281, 'lon': 78.0373},
    'NELLORE':        {'state': 'Andhra Pradesh', 'lat': 14.4426, 'lon': 79.9865},
    'PRAKASAM':       {'state': 'Andhra Pradesh', 'lat': 15.3408, 'lon': 79.5748},
    'SRIKAKULAM':     {'state': 'Andhra Pradesh', 'lat': 18.2949, 'lon': 83.8938},
    'VISAKHAPATNAM':  {'state': 'Andhra Pradesh', 'lat': 17.6868, 'lon': 83.2185},
    'VIZIANAGARAM':   {'state': 'Andhra Pradesh', 'lat': 18.1066, 'lon': 83.3956},
    'WEST GODAVARI':  {'state': 'Andhra Pradesh', 'lat': 16.9174, 'lon': 81.3318},
    'YSR KADAPA':     {'state': 'Andhra Pradesh', 'lat': 14.4674, 'lon': 78.8241},
    'BELAGAVI':       {'state': 'Karnataka',       'lat': 15.8497, 'lon': 74.4977},
    'BENGALURU RURAL':{'state': 'Karnataka',       'lat': 13.2257, 'lon': 77.5946},
    'BENGALURU URBAN':{'state': 'Karnataka',       'lat': 12.9716, 'lon': 77.5946},
    'BIDAR':          {'state': 'Karnataka',       'lat': 17.9104, 'lon': 77.5199},
    'DAVANAGERE':     {'state': 'Karnataka',       'lat': 14.4644, 'lon': 75.9218},
    'HASSAN':         {'state': 'Karnataka',       'lat': 13.0072, 'lon': 76.1004},
    'KALABURAGI':     {'state': 'Karnataka',       'lat': 17.3297, 'lon': 76.8343},
    'KODAGU':         {'state': 'Karnataka',       'lat': 12.3375, 'lon': 75.8069},
    'MYSURU':         {'state': 'Karnataka',       'lat': 12.2958, 'lon': 76.6394},
    'RAICHUR':        {'state': 'Karnataka',       'lat': 16.2120, 'lon': 77.3439},
    'SHIVAMOGGA':     {'state': 'Karnataka',       'lat': 13.9299, 'lon': 75.5681},
    'TUMKUR':         {'state': 'Karnataka',       'lat': 13.3379, 'lon': 77.1173},
}

PLOTLY_DARK = dict(
    plot_bgcolor='#020f02',
    paper_bgcolor='#041404',
    font=dict(family='Share Tech Mono, monospace', color='#44ff88'),
    xaxis=dict(gridcolor='#00ff4415', zerolinecolor='#00ff4430', color='#44ff88'),
    yaxis=dict(gridcolor='#00ff4415', zerolinecolor='#00ff4430', color='#44ff88'),
)


# ── FSI LOGIC ───────────────────────────────────────────────────
@st.cache_data
def load_default():
    # Try multiple possible paths
    for path in ["agri_dataset_500_samples.xlsx", "/mnt/user-data/uploads/agri_dataset_500_samples.xlsx"]:
        if os.path.exists(path):
            return pd.read_excel(path)
    raise FileNotFoundError("Dataset not found. Please upload via sidebar.")


def compute_fsi(df, weights):
    scaler = MinMaxScaler()
    out = df.copy()
    out["norm_rainfall"]   = 1 - scaler.fit_transform(df[["Rainfall"]])
    out["norm_price"]      = 1 - scaler.fit_transform(df[["Price"]])
    out["norm_yield"]      = 1 - scaler.fit_transform(df[["Yield"]])
    out["norm_cost"]       =     scaler.fit_transform(df[["Cost"]])
    out["norm_irrigation"] = 1 - scaler.fit_transform(df[["Irrigation"]])
    out["FSI"] = (
        weights["Rainfall"]   * out["norm_rainfall"]   +
        weights["Price"]      * out["norm_price"]       +
        weights["Yield"]      * out["norm_yield"]       +
        weights["Cost"]       * out["norm_cost"]        +
        weights["Irrigation"] * out["norm_irrigation"]
    ).round(4)
    return out


def district_summary(df_fsi):
    grp = df_fsi.groupby("Region", as_index=False).agg(
        FSI=("FSI", "mean"),
        Rainfall=("Rainfall", "mean"),
        Price=("Price", "mean"),
        Cost=("Cost", "mean"),
        Yield=("Yield", "mean"),
        Irrigation=("Irrigation", "mean"),
        Records=("FSI", "count"),
    )
    grp["FSI"] = grp["FSI"].round(4)
    p33 = grp["FSI"].quantile(0.33)
    p66 = grp["FSI"].quantile(0.66)
    def cat(v):
        if v >= p66: return "High"
        elif v >= p33: return "Medium"
        else: return "Low"
    grp["Stress_Category"] = grp["FSI"].apply(cat)
    grp["State"] = grp["Region"].map(lambda r: DISTRICT_INFO.get(r, {}).get("state", "Unknown"))
    grp["lat"]   = grp["Region"].map(lambda r: DISTRICT_INFO.get(r, {}).get("lat", None))
    grp["lon"]   = grp["Region"].map(lambda r: DISTRICT_INFO.get(r, {}).get("lon", None))
    return grp.sort_values("FSI", ascending=False).reset_index(drop=True)


# ── SIDEBAR ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:8px 0;'>
      <div style='font-family:Orbitron,monospace;font-size:1rem;color:#00ff88;letter-spacing:3px;text-shadow:0 0 10px #00ff88'>🌾 AGRISTRESS</div>
      <div style='font-family:Orbitron,monospace;font-size:1.2rem;color:#00ff44;letter-spacing:4px;font-weight:900;text-shadow:0 0 15px #00ff44'>AVENGERS</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66;letter-spacing:2px;margin-top:4px'>FSI MISSION CONTROL · AP & KA</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Agent Panel
    st.markdown("""
    <div class="agent-card">
      <span class="agent-avatar">🥷</span>
      <div class="agent-name">◈ AGENT: FARMER_AI ◈</div>
      <div class="agent-level">LEVEL: 5 &nbsp;|&nbsp; CLASS: ANALYST</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66;margin:4px 0'>XP</div>
      <div class="xp-bar-container"><div class="xp-bar"></div></div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#44cc66;margin:6px 0 2px 0'>◆ ACTIVE MISSION ◆</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#00ff88'>STRESS HOTSPOT SCAN</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader("📂 UPLOAD DATASET", type=["xlsx", "csv"])
    st.divider()

    st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.8rem;color:#00ff88;letter-spacing:2px'>⚖️ FSI WEIGHT CONFIG</div>", unsafe_allow_html=True)
    w_rain  = st.slider("🌧️ RAINFALL",        0.0, 1.0, 0.25, 0.05)
    w_price = st.slider("💰 MARKET PRICE",     0.0, 1.0, 0.25, 0.05)
    w_yield = st.slider("🌾 CROP YIELD",       0.0, 1.0, 0.20, 0.05)
    w_cost  = st.slider("🧾 CULTIVATION COST", 0.0, 1.0, 0.20, 0.05)
    w_irr   = st.slider("💧 IRRIGATION",       0.0, 1.0, 0.10, 0.05)

    total = w_rain + w_price + w_yield + w_cost + w_irr or 1.0
    weights = {
        "Rainfall":   w_rain  / total,
        "Price":      w_price / total,
        "Yield":      w_yield / total,
        "Cost":       w_cost  / total,
        "Irrigation": w_irr   / total,
    }
    st.divider()

    st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.8rem;color:#00ff88;letter-spacing:2px'>🗺️ STATE FILTER</div>", unsafe_allow_html=True)
    state_filter = st.multiselect(
        "Select States",
        ["Andhra Pradesh", "Karnataka"],
        default=["Andhra Pradesh", "Karnataka"]
    )
    st.divider()

    st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66'>TEAM: BADIYA SUNIL KUMAR<br>YASHASWINI H V · SRL KEERTHI<br>SIBBALA YOSHITHA</div>", unsafe_allow_html=True)


# ── LOAD DATA ───────────────────────────────────────────────────
if uploaded:
    df_raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
else:
    try:
        df_raw = load_default()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

required = {"Region", "Crop", "Rainfall", "Price", "Cost", "Yield", "Irrigation"}
if not required.issubset(df_raw.columns):
    st.error(f"Missing columns: {required - set(df_raw.columns)}")
    st.stop()

with st.sidebar:
    all_crops = sorted(df_raw["Crop"].dropna().unique().tolist())
    sel_crops = st.multiselect("🌱 CROP FILTER", all_crops, default=all_crops)

df_f = df_raw[df_raw["Crop"].isin(sel_crops)].copy()
if df_f.empty:
    st.warning("No data. Adjust filters.")
    st.stop()

df_fsi  = compute_fsi(df_f, weights)
dist_df = district_summary(df_fsi)

dist_filtered = dist_df[dist_df["State"].isin(state_filter)] if state_filter else dist_df

n_high  = int((dist_filtered["Stress_Category"] == "High").sum())
n_med   = int((dist_filtered["Stress_Category"] == "Medium").sum())
n_low   = int((dist_filtered["Stress_Category"] == "Low").sum())
avg_fsi = float(dist_filtered["FSI"].mean()) if len(dist_filtered) else 0.0
n_hotspots = n_high

# Top hotspot for agent panel display
top_hotspot = dist_filtered.iloc[0] if len(dist_filtered) > 0 else None

# Update sidebar agent stats after data load
with st.sidebar:
    if top_hotspot is not None:
        st.markdown(f"""
        <div style='background:#041a04;border:1px solid #00ff4430;border-radius:4px;padding:8px 10px;margin-top:8px'>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66;letter-spacing:1px'>◈ LIVE INTEL</div>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#00ff88;margin-top:4px'>
            STATE: <span style='color:#44aaff'>{top_hotspot['State'][:15].upper()}</span><br>
            RAINFALL: <span style='color:#00ff88'>{top_hotspot['Rainfall']:.0f} mm</span><br>
            YIELD: <span style='color:#00ff88'>{top_hotspot['Yield']:.1f} kg/ha</span><br>
            MARKET: <span style='color:#00ff88'>₹{top_hotspot['Price']:.0f}/qtl</span><br>
            HOTSPOT: <span style='color:#ff4444'>{top_hotspot['Region']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── HEADER ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="game-header">
  <h1>⚡ AGRISTRESS AVENGERS ⚡</h1>
  <p>◈ SPATIAL HOTSPOT DETECTION · FARMER STRESS INDEX · MISSION CONTROL ◈</p>
  <p style='font-size:0.7rem;color:#44cc66;margin-top:2px'>ANDHRA PRADESH & KARNATAKA · 500 RECORDS LOADED · SCAN ACTIVE</p>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ─────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">AVG FSI SCORE</div>
        <div class="kpi-value">{avg_fsi:.3f}</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="kpi-card kpi-high">
        <div class="kpi-label">🔴 HIGH STRESS</div>
        <div class="kpi-value">{n_high}</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="kpi-card kpi-med">
        <div class="kpi-label">🟡 MEDIUM STRESS</div>
        <div class="kpi-value">{n_med}</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="kpi-card kpi-low">
        <div class="kpi-label">🟢 LOW STRESS</div>
        <div class="kpi-value">{n_low}</div>
    </div>""", unsafe_allow_html=True)
with k5:
    st.markdown(f"""<div class="kpi-card kpi-high">
        <div class="kpi-label">🔥 HOTSPOTS</div>
        <div class="kpi-value">{n_hotspots}</div>
    </div>""", unsafe_allow_html=True)
with k6:
    st.markdown(f"""<div class="kpi-card">
        <div class="kpi-label">DISTRICTS SCANNED</div>
        <div class="kpi-value">{len(dist_filtered)}</div>
    </div>""", unsafe_allow_html=True)


# ── TABS ────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "🗺️  MISSION MAP",
    "📊  FSI ANALYSIS",
    "📈  INDICATOR SCAN",
    "🏆  RANKINGS",
    "📋  DATA EXPORT",
])


# ══ TAB 1: MISSION MAP ══════════════════════════════════════════
with t1:
    # 3-column layout: Agent Panel | Map | Control Panel
    left_col, map_col, right_col = st.columns([1, 3.5, 1])

    with left_col:
        st.markdown("#### 🥷 AGENT PANEL")

        if top_hotspot is not None:
            # Dynamic district info
            st.markdown(f"""
            <div class="agent-card" style='margin-bottom:10px'>
              <span class="agent-avatar">🥷</span>
              <div class="agent-name">FARMER_AI</div>
              <div class="agent-level">LEVEL: 5</div>
              <div class='xp-bar-container'><div class='xp-bar'></div></div>
              <hr style='border-color:#00ff4420;margin:8px 0'>
              <div class='agent-stat'>● <span style='color:#44cc66'>STATE:</span> <span class='agent-stat-val'>{top_hotspot['State'][:13]}</span></div>
              <div class='agent-stat'>● <span style='color:#44cc66'>RAIN:</span> <span class='agent-stat-val'>{top_hotspot['Rainfall']:.0f} mm</span></div>
              <div class='agent-stat'>● <span style='color:#44cc66'>YIELD:</span> <span class='agent-stat-val'>{top_hotspot['Yield']:.1f} kg/ha</span></div>
              <div class='agent-stat'>● <span style='color:#44cc66'>PRICE:</span> <span class='agent-stat-val'>₹{top_hotspot['Price']:.0f}</span></div>
            </div>
            """, unsafe_allow_html=True)

        # Year display (decorative)
        st.markdown("""
        <div style='background:#041a04;border:1px solid #00ff4440;border-radius:4px;padding:8px;text-align:center;font-family:Share Tech Mono,monospace'>
          <div style='color:#44cc66;font-size:0.65rem'>◄ MISSION YEAR ►</div>
          <div style='color:#00ff88;font-size:1.4rem;font-family:Orbitron,monospace;font-weight:900;text-shadow:0 0 10px #00ff88'>2015-23</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Mini bar chart for stress distribution
        st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#44cc66;letter-spacing:1px;margin-bottom:4px'>◈ STRESS BREAKDOWN</div>", unsafe_allow_html=True)
        fig_mini = go.Figure(go.Bar(
            x=["LOW", "MEDIUM", "HIGH"],
            y=[n_low, n_med, n_high],
            marker=dict(color=["#00ff88", "#ffcc00", "#ff2222"]),
            text=[n_low, n_med, n_high],
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=10),
        ))
        fig_mini.update_layout(
            **PLOTLY_DARK,
            height=200,
            margin=dict(t=10, b=5, l=5, r=5),
            showlegend=False,
            yaxis=dict(showticklabels=False, gridcolor='#00ff4415'),
            xaxis=dict(color='#44cc66'),
        )
        st.plotly_chart(fig_mini, use_container_width=True)

    with map_col:
        st.markdown("#### 🗺️ MISSION MAP — DISTRICT STRESS HEATMAP")
        map_data = dist_filtered.dropna(subset=["lat", "lon"]).copy()

        if len(map_data) == 0:
            st.warning("No geo data for selected states.")
        else:
            cat_color = {"High": "#ff2222", "Medium": "#ffcc00", "Low": "#00ff88"}
            fig_map = go.Figure()

            for cat_name, color in cat_color.items():
                sub = map_data[map_data["Stress_Category"] == cat_name]
                if len(sub) == 0:
                    continue
                fig_map.add_trace(go.Scattermapbox(
                    lat=sub["lat"],
                    lon=sub["lon"],
                    mode="markers",
                    marker=dict(
                        size=sub["FSI"] * 60 + 14,
                        color=color,
                        opacity=0.88,
                        sizemode="diameter",
                    ),
                    text=sub.apply(lambda r:
                        f"<b>{r['Region']}</b><br>"
                        f"State: {r['State']}<br>"
                        f"FSI Score: {r['FSI']:.4f}<br>"
                        f"Stress: <b>{r['Stress_Category']}</b><br>"
                        f"Rainfall: {r['Rainfall']:.1f} mm<br>"
                        f"Yield: {r['Yield']:.1f} kg/ha<br>"
                        f"Price: ₹{r['Price']:.0f}/qtl<br>"
                        f"Cost: ₹{r['Cost']:.0f}/ha<br>"
                        f"Irrigation: {r['Irrigation']:.1f}%",
                        axis=1
                    ),
                    hoverinfo="text",
                    name=f"{cat_name} Stress",
                ))

            center_lat = map_data["lat"].mean()
            center_lon = map_data["lon"].mean()

            fig_map.update_layout(
                mapbox=dict(
                    style="carto-darkmatter",
                    center=dict(lat=center_lat, lon=center_lon),
                    zoom=5.5,
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=520,
                paper_bgcolor="#020f02",
                legend=dict(
                    bgcolor="#041404",
                    bordercolor="#00ff4440",
                    borderwidth=1,
                    font=dict(color="#00ff88", family="Share Tech Mono"),
                    x=0.01, y=0.01,
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption("🟢 Low Stress   🟡 Medium Stress   🔴 High Stress · Circle size = FSI intensity · Hover for details")

        # Mission Log below map
        logs = []
        logs.append('<span class="log-xp">★ SCAN COMPLETE! +50 XP</span>')
        for _, row in dist_filtered[dist_filtered["Stress_Category"] == "High"].head(3).iterrows():
            logs.append(f'<span class="log-high">● ALERT: {row["Region"]} is under high stress. FSI={row["FSI"]:.3f}</span>')
        for _, row in dist_filtered[dist_filtered["Stress_Category"] == "Medium"].head(2).iterrows():
            logs.append(f'<span class="log-med">◈ WATCH: {row["Region"]} FSI={row["FSI"]:.3f}</span>')
        logs.append(f'<span class="log-info">✦ Data analysis initiated...</span>')
        logs.append(f'<span class="log-normal">★ Welcome, Agent FARMER_AI</span>')
        st.markdown(f"""<div class="mission-log">
            <b style='color:#00ff88;letter-spacing:2px'>◈ MISSION LOG ◈</b><br><br>
            {"<br>".join(logs)}
        </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### ⚡ CONTROL PANEL")

        # Control buttons styled
        st.markdown("""
        <div class="ctrl-btn">🚀 LAUNCH SCAN</div>
        <div class="ctrl-btn">🔄 RESET MISSION</div>
        <div class="ctrl-btn">📥 EXPORT REPORT</div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # KPI Display
        st.markdown(f"""
        <div class='kpi-card' style='margin-bottom:8px'>
          <div class='kpi-label'>AVG SCORE</div>
          <div class='kpi-value' style='font-size:1.4rem'>{avg_fsi:.2f}</div>
        </div>
        <div class='kpi-card kpi-high' style='margin-bottom:8px'>
          <div class='kpi-label'>HOTSPOTS</div>
          <div class='kpi-value' style='font-size:1.4rem'>{n_hotspots}</div>
        </div>
        """, unsafe_allow_html=True)

        # Pie chart
        st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#44cc66;margin:8px 0 4px'>◈ DISTRIBUTION</div>", unsafe_allow_html=True)
        if len(dist_filtered) > 0:
            fig_pie = go.Figure(go.Pie(
                values=[n_high, n_med, n_low],
                labels=["HIGH", "MED", "LOW"],
                marker=dict(colors=["#ff2222", "#ffcc00", "#00ff88"]),
                hole=0.55,
                textfont=dict(family="Share Tech Mono", size=9),
            ))
            fig_pie.update_layout(
                height=180, margin=dict(t=5, b=5, l=5, r=5),
                paper_bgcolor="#041404",
                legend=dict(font=dict(color="#00ff88", family="Share Tech Mono", size=9), orientation="h", x=0, y=-0.1),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Top hotspot highlight
        if top_hotspot is not None:
            cat_c = "#ff4444" if top_hotspot["Stress_Category"]=="High" else "#ffcc00"
            st.markdown(f"""
            <div style='background:#041a04;border:1px solid #ff444460;border-radius:4px;padding:8px;margin-top:6px'>
              <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#ff4444;letter-spacing:1px'>🔴 TOP HOTSPOT</div>
              <div style='font-family:Orbitron,monospace;font-size:0.8rem;color:{cat_c};margin-top:4px'>{top_hotspot['Region']}</div>
              <div style='font-family:Share Tech Mono,monospace;font-size:0.7rem;color:#44cc66'>FSI: <span style='color:{cat_c}'>{top_hotspot['FSI']:.4f}</span></div>
              <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66'>STRESS: <span style='color:{cat_c};font-weight:bold'>{top_hotspot['Stress_Category'].upper()}</span></div>
            </div>
            """, unsafe_allow_html=True)


# ══ TAB 2: FSI ANALYSIS ════════════════════════════════════════
with t2:
    st.markdown("#### 📊 FSI SCORE BY DISTRICT")
    col_a, col_b = st.columns([2, 1])

    with col_a:
        sorted_dist = dist_filtered.sort_values("FSI")
        colors_list = sorted_dist["Stress_Category"].map(
            {"High": "#ff2222", "Medium": "#ffcc00", "Low": "#00ff88"}
        ).tolist()
        fig_bar = go.Figure(go.Bar(
            x=sorted_dist["FSI"],
            y=sorted_dist["Region"],
            orientation="h",
            marker=dict(color=colors_list, line=dict(color="#00ff4430", width=0.5)),
            text=sorted_dist["FSI"].apply(lambda x: f"{x:.4f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=10),
            hovertemplate="<b>%{y}</b><br>FSI: %{x:.4f}<extra></extra>",
        ))
        fig_bar.update_layout(
            **PLOTLY_DARK,
            height=620,
            xaxis_range=[0, 0.7],
            title=dict(text="FARMER STRESS INDEX · DISTRICT RANKING", font=dict(family="Orbitron", color="#00ff88", size=13)),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.markdown("#### 📈 STATE COMPARISON")
        state_agg = dist_df.groupby("State", as_index=False)["FSI"].mean()
        fig_state = go.Figure(go.Bar(
            x=state_agg["State"],
            y=state_agg["FSI"],
            marker=dict(color=["#00aaff", "#ffaa00"]),
            text=state_agg["FSI"].apply(lambda x: f"{x:.4f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono"),
        ))
        fig_state.update_layout(
            **PLOTLY_DARK, height=280,
            title=dict(text="AVG FSI BY STATE", font=dict(family="Orbitron", color="#00ff88", size=11)),
        )
        st.plotly_chart(fig_state, use_container_width=True)

        st.markdown("#### 🌾 CROP STRESS")
        crop_agg = df_fsi.groupby("Crop", as_index=False)["FSI"].mean().sort_values("FSI", ascending=False)
        fig_crop = go.Figure(go.Bar(
            x=crop_agg["Crop"], y=crop_agg["FSI"],
            marker=dict(color=crop_agg["FSI"], colorscale=[[0,"#00ff88"],[0.5,"#ffcc00"],[1,"#ff2222"]]),
            text=crop_agg["FSI"].apply(lambda x: f"{x:.3f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=9),
        ))
        fig_crop.update_layout(
            **PLOTLY_DARK, height=270,
            title=dict(text="FSI BY CROP TYPE", font=dict(family="Orbitron", color="#00ff88", size=11)),
        )
        st.plotly_chart(fig_crop, use_container_width=True)

    # Radar
    st.markdown("#### 🕸️ INDICATOR RADAR — MOST vs LEAST STRESSED")
    INDICATORS = ["Rainfall", "Price", "Yield", "Cost", "Irrigation"]
    if len(dist_filtered) >= 2:
        top_r = dist_filtered.iloc[0]["Region"]
        bot_r = dist_filtered.iloc[-1]["Region"]
        scaler2 = MinMaxScaler()
        df_sc = df_fsi.copy()
        df_sc[INDICATORS] = scaler2.fit_transform(df_fsi[INDICATORS])
        tv = df_sc[df_sc["Region"] == top_r][INDICATORS].mean().tolist()
        bv = df_sc[df_sc["Region"] == bot_r][INDICATORS].mean().tolist()
        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(r=tv+[tv[0]], theta=INDICATORS+[INDICATORS[0]],
            fill="toself", name=f"🔴 {top_r}", line_color="#ff2222", fillcolor="rgba(255,34,34,0.15)"))
        fig_rad.add_trace(go.Scatterpolar(r=bv+[bv[0]], theta=INDICATORS+[INDICATORS[0]],
            fill="toself", name=f"🟢 {bot_r}", line_color="#00ff88", fillcolor="rgba(0,255,136,0.15)"))
        fig_rad.update_layout(
            polar=dict(bgcolor="#041404",
                radialaxis=dict(visible=True, range=[0,1], gridcolor="#00ff4420", color="#44cc66"),
                angularaxis=dict(gridcolor="#00ff4420", color="#44cc66")),
            paper_bgcolor="#041404", height=420,
            legend=dict(font=dict(color="#00ff88", family="Share Tech Mono")),
            title=dict(text="INDICATOR PROFILE COMPARISON", font=dict(family="Orbitron", color="#00ff88", size=12)),
        )
        st.plotly_chart(fig_rad, use_container_width=True)


# ══ TAB 3: INDICATOR SCAN ══════════════════════════════════════
with t3:
    st.markdown("#### 📈 INDICATOR DEEP SCAN")
    INDICATORS = ["Rainfall", "Price", "Yield", "Cost", "Irrigation"]
    ind = st.selectbox("SELECT INDICATOR", INDICATORS)

    col_c, col_d = st.columns(2)
    with col_c:
        agg = df_fsi.groupby("Region")[ind].mean().reset_index().sort_values(ind)
        scale = [[0,"#ff2222"],[0.5,"#ffcc00"],[1,"#00ff88"]] if ind != "Cost" else [[0,"#00ff88"],[0.5,"#ffcc00"],[1,"#ff2222"]]
        fig_ind = go.Figure(go.Bar(
            x=agg[ind], y=agg["Region"], orientation="h",
            marker=dict(color=agg[ind], colorscale=scale),
            text=agg[ind].apply(lambda x: f"{x:.1f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=9),
        ))
        fig_ind.update_layout(**PLOTLY_DARK, height=540,
            title=dict(text=f"AVG {ind.upper()} BY DISTRICT", font=dict(family="Orbitron", color="#00ff88", size=12)))
        st.plotly_chart(fig_ind, use_container_width=True)

    with col_d:
        p33_val = dist_filtered["FSI"].quantile(0.33) if len(dist_filtered) > 0 else 0.33
        p66_val = dist_filtered["FSI"].quantile(0.66) if len(dist_filtered) > 0 else 0.66
        cat_color_map = {"High": "#ff2222", "Medium": "#ffcc00", "Low": "#00ff88"}
        fig_sc = go.Figure()
        for cat_name, color in cat_color_map.items():
            sub = df_fsi[df_fsi["FSI"].apply(lambda v:
                "High" if v >= p66_val else "Medium" if v >= p33_val else "Low") == cat_name]
            if len(sub) == 0:
                continue
            fig_sc.add_trace(go.Scatter(
                x=sub[ind], y=sub["FSI"], mode="markers",
                marker=dict(color=color, size=7, opacity=0.8, line=dict(color="#020f02", width=0.5)),
                name=cat_name,
                hovertemplate=f"<b>%{{customdata}}</b><br>{ind}: %{{x:.2f}}<br>FSI: %{{y:.4f}}<extra></extra>",
                customdata=sub["Region"],
            ))
        fig_sc.update_layout(**PLOTLY_DARK, height=540,
            title=dict(text=f"{ind.upper()} vs FSI SCORE", font=dict(family="Orbitron", color="#00ff88", size=12)),
            legend=dict(font=dict(color="#00ff88", family="Share Tech Mono")))
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("#### 🔗 CORRELATION MATRIX")
    corr_cols = INDICATORS + ["FSI"]
    corr = df_fsi[corr_cols].corr().round(3)
    fig_corr = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
        colorscale=[[0,"#ff2222"],[0.5,"#020f02"],[1,"#00ff88"]],
        zmin=-1, zmax=1,
        text=corr.values.round(2),
        texttemplate="%{text}",
        textfont=dict(color="#00ff88", family="Share Tech Mono", size=11),
    ))
    fig_corr.update_layout(**PLOTLY_DARK, height=420,
        title=dict(text="INDICATOR CORRELATION MATRIX", font=dict(family="Orbitron", color="#00ff88", size=12)))
    st.plotly_chart(fig_corr, use_container_width=True)


# ══ TAB 4: RANKINGS ════════════════════════════════════════════
with t4:
    st.markdown("#### 🏆 DISTRICT STRESS RANKINGS")
    col_h, col_m, col_l = st.columns(3)

    def render_ranking(df_sub, title, color):
        st.markdown(f"<p style='color:{color};font-family:Orbitron;font-size:0.85rem;letter-spacing:2px'>{title}</p>", unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_sub.iterrows(), 1):
            st.markdown(f"""<div class="district-card" style="border-left:3px solid {color}">
                <span style="color:{color};font-size:0.7rem">#{i}</span>
                <span style="color:#00ff88;font-weight:bold;margin-left:8px">{row['Region']}</span>
                <span style="color:#44cc66;font-size:0.7rem;margin-left:4px">({row['State']})</span><br>
                <span style="color:{color};font-size:0.75rem">FSI: {row['FSI']:.4f}</span>
                <span style="color:#44cc66;font-size:0.65rem;margin-left:8px">
                Rain:{row['Rainfall']:.0f}mm Yield:{row['Yield']:.0f}</span>
            </div>""", unsafe_allow_html=True)

    with col_h:
        render_ranking(dist_filtered[dist_filtered["Stress_Category"]=="High"].reset_index(drop=True), "🔴 HIGH STRESS ZONES", "#ff4444")
    with col_m:
        render_ranking(dist_filtered[dist_filtered["Stress_Category"]=="Medium"].reset_index(drop=True), "🟡 MEDIUM STRESS ZONES", "#ffcc00")
    with col_l:
        render_ranking(dist_filtered[dist_filtered["Stress_Category"]=="Low"].reset_index(drop=True), "🟢 LOW STRESS ZONES", "#00ff88")

    st.divider()
    st.markdown("#### ⚖️ CURRENT WEIGHT CONFIGURATION")
    fig_w = go.Figure(go.Bar(
        x=list(weights.keys()),
        y=[round(v, 3) for v in weights.values()],
        marker=dict(color=["#00aaff","#ffaa00","#00ff88","#ff4444","#aa44ff"],
            line=dict(color="#00ff4430", width=1)),
        text=[f"{v:.2f}" for v in weights.values()],
        textposition="outside",
        textfont=dict(color="#00ff88", family="Share Tech Mono"),
    ))
    fig_w.update_layout(**PLOTLY_DARK, height=300,
        title=dict(text="FSI INDICATOR WEIGHTS", font=dict(family="Orbitron", color="#00ff88", size=12)),
        yaxis_range=[0, max(weights.values())*1.4])
    st.plotly_chart(fig_w, use_container_width=True)


# ══ TAB 5: DATA EXPORT ════════════════════════════════════════
with t5:
    st.markdown("#### 📋 FULL DATASET WITH FSI SCORES")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL RECORDS", len(df_fsi))
    m2.metric("DISTRICTS", df_fsi["Region"].nunique())
    m3.metric("CROPS", df_fsi["Crop"].nunique())
    m4.metric("STATES", dist_df["State"].nunique())

    disp_cols = ["Region", "Crop", "Rainfall", "Price", "Cost", "Yield", "Irrigation", "FSI"]
    show_df = df_fsi[disp_cols].sort_values("FSI", ascending=False).reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True, height=420)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv1 = df_fsi[disp_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ DOWNLOAD FULL RESULTS (CSV)", data=csv1,
            file_name="FSI_Full_Results.csv", mime="text/csv")
    with col_d2:
        dist_export = dist_df[["Region","State","FSI","Stress_Category","Rainfall","Yield","Cost","Irrigation","Records"]]
        csv2 = dist_export.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ DOWNLOAD DISTRICT SUMMARY (CSV)", data=csv2,
            file_name="FSI_District_Summary.csv", mime="text/csv")

    st.divider()
    st.markdown("#### 🗺️ DISTRICT SUMMARY TABLE")
    st.dataframe(
        dist_filtered[["Region","State","FSI","Stress_Category","Rainfall","Yield","Cost","Irrigation","Records"]],
        use_container_width=True
    )
