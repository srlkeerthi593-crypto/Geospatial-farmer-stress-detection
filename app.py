import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="AgriStress Avengers – Karnataka",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GAMING CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

html, body, [data-testid="stAppViewContainer"] { background-color: #020f02 !important; }
[data-testid="stAppViewContainer"] { background: radial-gradient(ellipse at top, #0a1f0a 0%, #020f02 70%) !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #041404 0%, #021002 100%) !important; border-right: 1px solid #00ff4130 !important; }
[data-testid="stSidebar"] * { color: #00ff88 !important; }
[data-testid="stSidebar"] label { color: #00cc66 !important; font-family: 'Share Tech Mono', monospace !important; }
h1,h2,h3,h4 { font-family: 'Orbitron', monospace !important; color: #00ff88 !important; }
.block-container { padding: 0.5rem 1rem 1rem 1rem !important; }

.game-header {
    background: linear-gradient(135deg, #041a04 0%, #0a2a0a 50%, #041a04 100%);
    border: 2px solid #00ff44; border-radius: 6px; padding: 14px 20px;
    text-align: center; margin-bottom: 12px;
    box-shadow: 0 0 40px #00ff4450, inset 0 0 30px #00ff4410;
    font-family: 'Orbitron', monospace; position: relative; overflow: hidden;
}
.game-header::before {
    content: ''; position: absolute; inset: 0;
    background: repeating-linear-gradient(0deg, transparent, transparent 2px, #00ff4405 2px, #00ff4405 4px);
    pointer-events: none;
}
.game-header h1 { color: #00ff88 !important; font-size: 2.2rem !important; letter-spacing: 6px; text-shadow: 0 0 20px #00ff88, 0 0 50px #00ff4480; margin: 0 !important; }
.game-header .sub { color: #44ff88; font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; letter-spacing: 3px; margin: 5px 0 0 0; }
.state-badge { display: inline-block; background: #00ff4420; border: 1px solid #00ff44; border-radius: 3px; padding: 2px 12px; font-family: 'Orbitron', monospace; font-size: 0.7rem; color: #00ff88; letter-spacing: 4px; margin-top: 6px; }

.kpi-card { background: linear-gradient(135deg, #041a04, #0a2a0a); border: 1px solid #00ff4440; border-radius: 5px; padding: 14px 8px; text-align: center; box-shadow: 0 0 15px #00ff4420; margin-bottom: 8px; }
.kpi-label { font-family: 'Share Tech Mono', monospace; font-size: 0.62rem; color: #44cc66; letter-spacing: 2px; text-transform: uppercase; }
.kpi-value { font-family: 'Orbitron', monospace; font-size: 1.6rem; font-weight: 900; color: #00ff88; text-shadow: 0 0 10px #00ff88; }
.kpi-high  { border-color: #ff3333 !important; box-shadow: 0 0 18px #ff333345 !important; }
.kpi-high .kpi-value { color: #ff4444 !important; text-shadow: 0 0 12px #ff4444 !important; }
.kpi-med   { border-color: #ffaa00 !important; box-shadow: 0 0 18px #ffaa0045 !important; }
.kpi-med .kpi-value  { color: #ffcc00 !important; text-shadow: 0 0 12px #ffcc00 !important; }
.kpi-low   { border-color: #00ff44 !important; box-shadow: 0 0 18px #00ff4445 !important; }

.agent-card { background: linear-gradient(135deg, #041a04, #0a2a0a); border: 2px solid #00ff4460; border-radius: 6px; padding: 14px 10px; text-align: center; box-shadow: 0 0 25px #00ff4425, inset 0 0 15px #00ff4408; margin-bottom: 10px; }
.agent-avatar { font-size: 2.8rem; display: block; margin-bottom: 6px; filter: drop-shadow(0 0 10px #00ff88); }
.agent-name   { font-family: 'Orbitron', monospace; font-size: 0.82rem; color: #00ff88; letter-spacing: 2px; font-weight: 700; }
.agent-level  { font-family: 'Share Tech Mono', monospace; font-size: 0.72rem; color: #44cc66; margin: 3px 0; }
.xp-bar-container { background: #021002; border: 1px solid #00ff4430; border-radius: 10px; height: 9px; margin: 6px 0; overflow: hidden; }
.xp-bar { height: 100%; background: linear-gradient(90deg, #ff2200, #ffaa00, #00ff44); border-radius: 10px; width: 68%; }
.agent-stat { font-family: 'Share Tech Mono', monospace; font-size: 0.68rem; color: #44cc66; text-align: left; margin: 3px 0; }

.district-card { background: linear-gradient(135deg, #041a04, #081808); border: 1px solid #00ff4430; border-radius: 4px; padding: 7px 11px; margin: 3px 0; font-family: 'Share Tech Mono', monospace; font-size: 0.78rem; }
.district-high { border-left: 4px solid #ff4444 !important; }
.district-med  { border-left: 4px solid #ffcc00 !important; }
.district-low  { border-left: 4px solid #00ff88 !important; }

.mission-log { background: #020f02; border: 1px solid #00ff4430; border-radius: 4px; padding: 10px 14px; font-family: 'Share Tech Mono', monospace; font-size: 0.76rem; color: #44ff88; margin-top: 8px; max-height: 260px; overflow-y: auto; line-height: 1.7; }
.log-high { color: #ff4444; } .log-med { color: #ffcc00; } .log-norm { color: #00ff88; } .log-info { color: #44aaff; } .log-xp { color: #ffaa00; }

.ctrl-btn { display: block; background: linear-gradient(135deg, #041a04, #0d300d); border: 1px solid #00ff4460; border-radius: 4px; padding: 9px 12px; font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: #00ff88; letter-spacing: 1px; margin: 5px 0; box-shadow: 0 0 8px #00ff4420; }

.stTabs [data-baseweb="tab-list"] { background: #041404; border-bottom: 1px solid #00ff4430; }
.stTabs [data-baseweb="tab"] { font-family: 'Share Tech Mono', monospace !important; color: #44cc66 !important; background: transparent !important; border: none !important; letter-spacing: 2px; font-size: 0.75rem; }
.stTabs [aria-selected="true"] { color: #00ff88 !important; border-bottom: 2px solid #00ff88 !important; background: #00ff8810 !important; }

div[data-testid="stMetric"] { background: #041a04; border: 1px solid #00ff4430; border-radius: 4px; padding: 8px; }
div[data-testid="stMetric"] label { color: #44cc66 !important; font-family: 'Share Tech Mono', monospace !important; }
div[data-testid="stMetric"] div   { color: #00ff88 !important; font-family: 'Orbitron', monospace !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #020f02; }
::-webkit-scrollbar-thumb { background: #00ff4440; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── DISTRICT GEO-COORDS (Karnataka, 30 districts) ────────────────
DISTRICT_INFO = {
    'BAGALKOT':         {'lat': 16.1691, 'lon': 75.6965},
    'BALLARI':          {'lat': 15.1394, 'lon': 76.9214},
    'BELAGAVI':         {'lat': 15.8497, 'lon': 74.4977},
    'BENGALURU RURAL':  {'lat': 13.2257, 'lon': 77.5946},
    'BENGALURU URBAN':  {'lat': 12.9716, 'lon': 77.5946},
    'BIDAR':            {'lat': 17.9104, 'lon': 77.5199},
    'CHAMARAJANAGAR':   {'lat': 11.9261, 'lon': 76.9437},
    'CHIKKABALLAPUR':   {'lat': 13.4355, 'lon': 77.7315},
    'CHIKKAMAGALURU':   {'lat': 13.3161, 'lon': 75.7720},
    'CHITRADURGA':      {'lat': 14.2251, 'lon': 76.3980},
    'DAKSHINA KANNADA': {'lat': 12.8438, 'lon': 75.2479},
    'DAVANAGERE':       {'lat': 14.4644, 'lon': 75.9218},
    'DHARWAD':          {'lat': 15.4589, 'lon': 75.0078},
    'GADAG':            {'lat': 15.4166, 'lon': 75.6180},
    'HASSAN':           {'lat': 13.0072, 'lon': 76.1004},
    'HAVERI':           {'lat': 14.7957, 'lon': 75.4001},
    'KALABURAGI':       {'lat': 17.3297, 'lon': 76.8343},
    'KODAGU':           {'lat': 12.3375, 'lon': 75.8069},
    'KOLAR':            {'lat': 13.1360, 'lon': 78.1294},
    'KOPPAL':           {'lat': 15.3547, 'lon': 76.1547},
    'MANDYA':           {'lat': 12.5218, 'lon': 76.8951},
    'MYSURU':           {'lat': 12.2958, 'lon': 76.6394},
    'RAICHUR':          {'lat': 16.2120, 'lon': 77.3439},
    'RAMANAGARA':       {'lat': 12.7157, 'lon': 77.2820},
    'SHIVAMOGGA':       {'lat': 13.9299, 'lon': 75.5681},
    'TUMAKURU':         {'lat': 13.3379, 'lon': 77.1173},
    'UDUPI':            {'lat': 13.3409, 'lon': 74.7421},
    'UTTARA KANNADA':   {'lat': 14.7907, 'lon': 74.6940},
    'VIJAYAPURA':       {'lat': 16.8302, 'lon': 75.7100},
    'YADGIR':           {'lat': 16.7712, 'lon': 77.1382},
}

PLOTLY_DARK = dict(
    plot_bgcolor='#020f02', paper_bgcolor='#041404',
    font=dict(family='Share Tech Mono, monospace', color='#44ff88'),
    xaxis=dict(gridcolor='#00ff4415', zerolinecolor='#00ff4430', color='#44ff88'),
    yaxis=dict(gridcolor='#00ff4415', zerolinecolor='#00ff4430', color='#44ff88'),
)

INDICATORS = ["Rainfall","Price","Yield","Cost","Irrigation"]

# ── DATA LOAD ────────────────────────────────────────────────────
@st.cache_data
def load_default():
    for path in ["karnataka_dataset_750_samples.xlsx",
                 "/mnt/user-data/uploads/karnataka_dataset_750_samples.xlsx"]:
        if os.path.exists(path):
            return pd.read_excel(path)
    raise FileNotFoundError("Dataset not found. Please upload via sidebar.")

# ── FSI COMPUTE (data already 0-1 normalised) ───────────────────
def compute_fsi(df, weights):
    out = df.copy()
    out["s_rainfall"]   = 1 - df["Rainfall"]
    out["s_price"]      = 1 - df["Price"]
    out["s_yield"]      = 1 - df["Yield"]
    out["s_cost"]       =     df["Cost"]
    out["s_irrigation"] = 1 - df["Irrigation"]
    out["FSI"] = (
        weights["Rainfall"]   * out["s_rainfall"]   +
        weights["Price"]      * out["s_price"]       +
        weights["Yield"]      * out["s_yield"]       +
        weights["Cost"]       * out["s_cost"]        +
        weights["Irrigation"] * out["s_irrigation"]
    ).round(4)
    return out

def district_summary(df_fsi):
    grp = df_fsi.groupby("Region", as_index=False).agg(
        FSI=("FSI","mean"), Rainfall=("Rainfall","mean"),
        Price=("Price","mean"), Cost=("Cost","mean"),
        Yield=("Yield","mean"), Irrigation=("Irrigation","mean"),
        Records=("FSI","count"),
    )
    grp["FSI"] = grp["FSI"].round(4)
    p33 = grp["FSI"].quantile(0.33)
    p66 = grp["FSI"].quantile(0.66)
    grp["Stress_Category"] = grp["FSI"].apply(
        lambda v: "High" if v>=p66 else ("Medium" if v>=p33 else "Low"))
    grp["lat"] = grp["Region"].map(lambda r: DISTRICT_INFO.get(r,{}).get("lat"))
    grp["lon"] = grp["Region"].map(lambda r: DISTRICT_INFO.get(r,{}).get("lon"))
    return grp.sort_values("FSI", ascending=False).reset_index(drop=True)

# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:8px 0'>
      <div style='font-family:Orbitron,monospace;font-size:0.95rem;color:#00ff88;letter-spacing:3px;text-shadow:0 0 10px #00ff88'>🌾 AGRISTRESS</div>
      <div style='font-family:Orbitron,monospace;font-size:1.15rem;color:#00ff44;letter-spacing:4px;font-weight:900;text-shadow:0 0 15px #00ff44'>AVENGERS</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.6rem;color:#44cc66;letter-spacing:2px;margin-top:3px'>KARNATAKA · FSI MISSION CONTROL</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class="agent-card">
      <span class="agent-avatar">🥷</span>
      <div class="agent-name">◈ AGENT: FARMER_AI ◈</div>
      <div class="agent-level">LEVEL: 5 | CLASS: ANALYST</div>
      <div class="xp-bar-container"><div class="xp-bar"></div></div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#44cc66;margin:5px 0 2px'>◆ ACTIVE MISSION ◆</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#00ff88'>KARNATAKA STRESS SCAN</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    uploaded = st.file_uploader("📂 UPLOAD DATASET", type=["xlsx","csv"])
    st.divider()

    st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.78rem;color:#00ff88;letter-spacing:2px'>⚖️ FSI WEIGHT CONFIG</div>", unsafe_allow_html=True)
    w_rain  = st.slider("🌧️ RAINFALL",        0.0, 1.0, 0.25, 0.05)
    w_price = st.slider("💰 MARKET PRICE",     0.0, 1.0, 0.25, 0.05)
    w_yield = st.slider("🌾 CROP YIELD",       0.0, 1.0, 0.20, 0.05)
    w_cost  = st.slider("🧾 CULTIVATION COST", 0.0, 1.0, 0.20, 0.05)
    w_irr   = st.slider("💧 IRRIGATION",       0.0, 1.0, 0.10, 0.05)

    total = (w_rain+w_price+w_yield+w_cost+w_irr) or 1.0
    weights = {
        "Rainfall": w_rain/total, "Price": w_price/total,
        "Yield": w_yield/total,   "Cost": w_cost/total,
        "Irrigation": w_irr/total,
    }
    st.divider()
    st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#44cc66'>TEAM: BADIYA SUNIL KUMAR<br>YASHASWINI H V · SRL KEERTHI<br>SIBBALA YOSHITHA</div>", unsafe_allow_html=True)

# ── LOAD DATA ───────────────────────────────────────────────────
if uploaded:
    df_raw = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
else:
    try:
        df_raw = load_default()
    except FileNotFoundError as e:
        st.error(str(e)); st.stop()

required = {"Region","Crop","Rainfall","Price","Cost","Yield","Irrigation"}
if not required.issubset(df_raw.columns):
    st.error(f"Missing columns: {required - set(df_raw.columns)}"); st.stop()

with st.sidebar:
    all_crops = sorted(df_raw["Crop"].dropna().unique().tolist())
    sel_crops = st.multiselect("🌱 CROP FILTER", all_crops, default=all_crops)

df_f = df_raw[df_raw["Crop"].isin(sel_crops)].copy()
if df_f.empty:
    st.warning("No data. Adjust filters."); st.stop()

df_fsi  = compute_fsi(df_f, weights)
dist_df = district_summary(df_fsi)

n_high  = int((dist_df["Stress_Category"]=="High").sum())
n_med   = int((dist_df["Stress_Category"]=="Medium").sum())
n_low   = int((dist_df["Stress_Category"]=="Low").sum())
avg_fsi = float(dist_df["FSI"].mean())
top_row = dist_df.iloc[0]
safe_row= dist_df.iloc[-1]

with st.sidebar:
    st.markdown(f"""
    <div style='background:#041a04;border:1px solid #00ff4430;border-radius:4px;padding:9px 11px;margin-top:4px'>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#44cc66;letter-spacing:1px'>◈ LIVE INTEL</div>
      <div style='font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#00ff88;margin-top:5px;line-height:1.8'>
        STATE: <span style='color:#44aaff'>KARNATAKA</span><br>
        TOP HOTSPOT: <span style='color:#ff4444'>{top_row['Region']}</span><br>
        FSI: <span style='color:#ff4444'>{top_row['FSI']:.4f}</span><br>
        DISTRICTS: <span style='color:#00ff88'>{len(dist_df)}</span><br>
        RECORDS: <span style='color:#00ff88'>{len(df_fsi)}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="game-header">
  <h1>⚡ AGRISTRESS AVENGERS ⚡</h1>
  <p class="sub">◈ SPATIAL HOTSPOT DETECTION · FARMER STRESS INDEX · MISSION CONTROL ◈</p>
  <div class="state-badge">🏛️ KARNATAKA STATE COMMAND · {len(dist_df)} DISTRICTS · {len(df_fsi)} RECORDS</div>
</div>
""", unsafe_allow_html=True)

# ── KPI ROW ─────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-label">AVG FSI SCORE</div><div class="kpi-value">{avg_fsi:.3f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="kpi-card kpi-high"><div class="kpi-label">🔴 HIGH STRESS</div><div class="kpi-value">{n_high}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="kpi-card kpi-med"><div class="kpi-label">🟡 MEDIUM STRESS</div><div class="kpi-value">{n_med}</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="kpi-card kpi-low"><div class="kpi-label">🟢 LOW STRESS</div><div class="kpi-value">{n_low}</div></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="kpi-card kpi-high"><div class="kpi-label">🔥 HOTSPOTS</div><div class="kpi-value">{n_high}</div></div>', unsafe_allow_html=True)
with c6: st.markdown(f'<div class="kpi-card"><div class="kpi-label">DISTRICTS SCANNED</div><div class="kpi-value">{len(dist_df)}</div></div>', unsafe_allow_html=True)

# ── TABS ────────────────────────────────────────────────────────
t1,t2,t3,t4,t5 = st.tabs([
    "🗺️  MISSION MAP", "📊  FSI ANALYSIS",
    "📈  INDICATOR SCAN", "🏆  RANKINGS", "📋  DATA EXPORT",
])

# ══ TAB 1 ══════════════════════════════════════════════════════
with t1:
    left_col, map_col, right_col = st.columns([1, 3.5, 1])

    with left_col:
        st.markdown("#### 🥷 AGENT PANEL")
        st.markdown(f"""
        <div class="agent-card">
          <span class="agent-avatar">🥷</span>
          <div class="agent-name">FARMER_AI</div>
          <div class="agent-level">LEVEL: 5 · ANALYST</div>
          <div class='xp-bar-container'><div class='xp-bar'></div></div>
          <hr style='border-color:#00ff4420;margin:8px 0'>
          <div class='agent-stat'>● <span style='color:#44cc66'>STATE:</span> <span style='color:#44aaff'>KARNATAKA</span></div>
          <div class='agent-stat'>● <span style='color:#44cc66'>RAIN:</span> <span style='color:#00ff88'>{top_row['Rainfall']:.2f}</span></div>
          <div class='agent-stat'>● <span style='color:#44cc66'>YIELD:</span> <span style='color:#00ff88'>{top_row['Yield']:.2f}</span></div>
          <div class='agent-stat'>● <span style='color:#44cc66'>PRICE:</span> <span style='color:#00ff88'>{top_row['Price']:.2f}</span></div>
          <div class='agent-stat'>● <span style='color:#44cc66'>IRRIG:</span> <span style='color:#00ff88'>{top_row['Irrigation']:.2f}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#041a04;border:1px solid #00ff4440;border-radius:4px;padding:9px;text-align:center'>
          <div style='color:#44cc66;font-size:0.62rem;font-family:Share Tech Mono,monospace'>◄ MISSION YEAR ►</div>
          <div style='color:#00ff88;font-size:1.3rem;font-family:Orbitron,monospace;font-weight:900;text-shadow:0 0 10px #00ff88'>2020-24</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div style='font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#44cc66;margin-bottom:2px'>◈ STRESS BREAKDOWN</div>", unsafe_allow_html=True)
        fig_mini = go.Figure(go.Bar(
            x=["LOW","MED","HIGH"], y=[n_low,n_med,n_high],
            marker=dict(color=["#00ff88","#ffcc00","#ff2222"]),
            text=[n_low,n_med,n_high], textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=10),
        ))
        fig_mini.update_layout(**PLOTLY_DARK, height=190,
            margin=dict(t=5,b=5,l=3,r=3), showlegend=False,
            yaxis=dict(showticklabels=False, gridcolor="#00ff4415"),
            xaxis=dict(color="#44cc66"))
        st.plotly_chart(fig_mini, use_container_width=True)

    with map_col:
        st.markdown("#### 🗺️ MISSION MAP — KARNATAKA DISTRICT STRESS HEATMAP")
        map_data = dist_df.dropna(subset=["lat","lon"]).copy()

        fig_map = go.Figure()
        for cat_name, color in {"High":"#ff2222","Medium":"#ffcc00","Low":"#00ff88"}.items():
            sub = map_data[map_data["Stress_Category"]==cat_name]
            if sub.empty: continue
            fig_map.add_trace(go.Scattermapbox(
                lat=sub["lat"], lon=sub["lon"],
                mode="markers+text",
                marker=dict(size=sub["FSI"]*90+20, color=color, opacity=0.88, sizemode="diameter"),
                text=sub["Region"],
                textfont=dict(color="white", size=7, family="Share Tech Mono"),
                textposition="top center",
                customdata=sub[["FSI","Stress_Category","Rainfall","Yield","Price","Cost","Irrigation","Records"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "FSI Score: <b>%{customdata[0]:.4f}</b><br>"
                    "Stress: <b>%{customdata[1]}</b><br>"
                    "Rainfall: %{customdata[2]:.2f}<br>"
                    "Yield: %{customdata[3]:.2f}<br>"
                    "Price: %{customdata[4]:.2f}<br>"
                    "Cost: %{customdata[5]:.2f}<br>"
                    "Irrigation: %{customdata[6]:.2f}<br>"
                    "Records: %{customdata[7]}<extra></extra>"
                ),
                name=f"{cat_name} Stress",
            ))

        fig_map.update_layout(
            mapbox=dict(style="carto-darkmatter", center=dict(lat=14.5, lon=76.0), zoom=6.2),
            margin=dict(l=0,r=0,t=0,b=0), height=530, paper_bgcolor="#020f02",
            legend=dict(bgcolor="#041404", bordercolor="#00ff4440", borderwidth=1,
                font=dict(color="#00ff88", family="Share Tech Mono"), x=0.01, y=0.01),
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("🟢 Low Stress  🟡 Medium Stress  🔴 High Stress · Circle size = FSI intensity · Hover for details")

        logs = ['<span class="log-xp">★ SCAN COMPLETE! +50 XP · KARNATAKA LOADED</span>']
        for _, row in dist_df[dist_df["Stress_Category"]=="High"].head(3).iterrows():
            logs.append(f'<span class="log-high">● ALERT: {row["Region"]} is under HIGH stress. FSI={row["FSI"]:.4f}</span>')
        for _, row in dist_df[dist_df["Stress_Category"]=="Medium"].head(2).iterrows():
            logs.append(f'<span class="log-med">◈ WATCH: {row["Region"]} FSI={row["FSI"]:.4f}</span>')
        logs.append('<span class="log-info">✦ Data analysis initiated for Karnataka...</span>')
        logs.append('<span class="log-norm">★ Welcome, Agent FARMER_AI</span>')
        st.markdown(f"""<div class="mission-log">
            <b style='color:#00ff88;letter-spacing:2px'>◈ MISSION LOG ◈</b><br><br>{"<br>".join(logs)}
        </div>""", unsafe_allow_html=True)

    with right_col:
        st.markdown("#### ⚡ CONTROL PANEL")
        st.markdown("""
        <div class="ctrl-btn">🚀 LAUNCH SCAN</div>
        <div class="ctrl-btn">🔄 RESET MISSION</div>
        <div class="ctrl-btn">📥 EXPORT REPORT</div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='kpi-card' style='margin-bottom:8px'>
          <div class='kpi-label'>AVG SCORE</div>
          <div class='kpi-value' style='font-size:1.35rem'>{avg_fsi:.3f}</div>
        </div>
        <div class='kpi-card kpi-high' style='margin-bottom:8px'>
          <div class='kpi-label'>HOTSPOTS</div>
          <div class='kpi-value' style='font-size:1.35rem'>{n_high}</div>
        </div>
        """, unsafe_allow_html=True)

        fig_pie = go.Figure(go.Pie(
            values=[n_high,n_med,n_low], labels=["HIGH","MED","LOW"],
            marker=dict(colors=["#ff2222","#ffcc00","#00ff88"]),
            hole=0.55, textfont=dict(family="Share Tech Mono", size=9),
        ))
        fig_pie.update_layout(
            height=175, margin=dict(t=5,b=5,l=5,r=5),
            paper_bgcolor="#041404",
            legend=dict(font=dict(color="#00ff88", family="Share Tech Mono", size=9), orientation="h", x=0, y=-0.12),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        cat_c = "#ff4444" if top_row["Stress_Category"]=="High" else "#ffcc00"
        st.markdown(f"""
        <div style='background:#041a04;border:1px solid #ff444450;border-radius:4px;padding:9px;margin-top:5px'>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#ff4444'>🔴 TOP HOTSPOT</div>
          <div style='font-family:Orbitron,monospace;font-size:0.78rem;color:{cat_c};margin-top:4px'>{top_row['Region']}</div>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#44cc66'>FSI: <span style='color:{cat_c}'>{top_row['FSI']:.4f}</span></div>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.65rem;color:#44cc66'>STRESS: <span style='color:{cat_c};font-weight:bold'>{top_row['Stress_Category'].upper()}</span></div>
        </div>
        <div style='background:#041a04;border:1px solid #00ff4450;border-radius:4px;padding:9px;margin-top:6px'>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.62rem;color:#00ff88'>🟢 SAFE ZONE</div>
          <div style='font-family:Orbitron,monospace;font-size:0.78rem;color:#00ff88;margin-top:4px'>{safe_row['Region']}</div>
          <div style='font-family:Share Tech Mono,monospace;font-size:0.68rem;color:#44cc66'>FSI: <span style='color:#00ff88'>{safe_row['FSI']:.4f}</span></div>
        </div>
        """, unsafe_allow_html=True)

# ══ TAB 2 ══════════════════════════════════════════════════════
with t2:
    st.markdown("#### 📊 FSI SCORE BY DISTRICT — KARNATAKA")
    col_a, col_b = st.columns([2,1])

    with col_a:
        s = dist_df.sort_values("FSI")
        cols_list = s["Stress_Category"].map({"High":"#ff2222","Medium":"#ffcc00","Low":"#00ff88"}).tolist()
        fig_bar = go.Figure(go.Bar(
            x=s["FSI"], y=s["Region"], orientation="h",
            marker=dict(color=cols_list, line=dict(color="#00ff4430", width=0.5)),
            text=s["FSI"].apply(lambda x: f"{x:.4f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=9),
            hovertemplate="<b>%{y}</b><br>FSI: %{x:.4f}<extra></extra>",
        ))
        fig_bar.update_layout(**PLOTLY_DARK, height=720,
            xaxis_range=[0, 0.65],
            title=dict(text="FARMER STRESS INDEX · KARNATAKA DISTRICT RANKING",
                       font=dict(family="Orbitron", color="#00ff88", size=12)))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.markdown("#### 🌾 CROP STRESS")
        crop_agg = df_fsi.groupby("Crop", as_index=False)["FSI"].mean().sort_values("FSI", ascending=False)
        fig_crop = go.Figure(go.Bar(
            x=crop_agg["Crop"], y=crop_agg["FSI"],
            marker=dict(color=crop_agg["FSI"],
                colorscale=[[0,"#00ff88"],[0.5,"#ffcc00"],[1,"#ff2222"]]),
            text=crop_agg["FSI"].apply(lambda x: f"{x:.4f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=9),
        ))
        fig_crop.update_layout(**PLOTLY_DARK, height=300,
            title=dict(text="FSI BY CROP TYPE", font=dict(family="Orbitron", color="#00ff88", size=11)))
        st.plotly_chart(fig_crop, use_container_width=True)

        st.markdown("#### 🕸️ INDICATOR RADAR")
        tv = df_fsi[df_fsi["Region"]==top_row["Region"]][INDICATORS].mean().tolist()
        bv = df_fsi[df_fsi["Region"]==safe_row["Region"]][INDICATORS].mean().tolist()
        fig_rad = go.Figure()
        fig_rad.add_trace(go.Scatterpolar(
            r=tv+[tv[0]], theta=INDICATORS+[INDICATORS[0]], fill="toself",
            name=f"🔴 {top_row['Region']}", line_color="#ff2222", fillcolor="rgba(255,34,34,0.12)"))
        fig_rad.add_trace(go.Scatterpolar(
            r=bv+[bv[0]], theta=INDICATORS+[INDICATORS[0]], fill="toself",
            name=f"🟢 {safe_row['Region']}", line_color="#00ff88", fillcolor="rgba(0,255,136,0.12)"))
        fig_rad.update_layout(
            polar=dict(bgcolor="#041404",
                radialaxis=dict(visible=True, range=[0,1], gridcolor="#00ff4420", color="#44cc66"),
                angularaxis=dict(gridcolor="#00ff4420", color="#44cc66")),
            paper_bgcolor="#041404", height=400,
            legend=dict(font=dict(color="#00ff88", family="Share Tech Mono", size=9)),
            title=dict(text="HIGH vs LOW STRESS PROFILE",
                       font=dict(family="Orbitron", color="#00ff88", size=10)),
            margin=dict(t=40,b=20,l=20,r=20),
        )
        st.plotly_chart(fig_rad, use_container_width=True)

# ══ TAB 3 ══════════════════════════════════════════════════════
with t3:
    st.markdown("#### 📈 INDICATOR DEEP SCAN — KARNATAKA")
    ind = st.selectbox("SELECT INDICATOR", INDICATORS)
    col_c, col_d = st.columns(2)

    with col_c:
        agg = df_fsi.groupby("Region")[ind].mean().reset_index().sort_values(ind)
        scale = [[0,"#ff2222"],[0.5,"#ffcc00"],[1,"#00ff88"]] if ind!="Cost" else [[0,"#00ff88"],[0.5,"#ffcc00"],[1,"#ff2222"]]
        fig_ind = go.Figure(go.Bar(
            x=agg[ind], y=agg["Region"], orientation="h",
            marker=dict(color=agg[ind], colorscale=scale),
            text=agg[ind].apply(lambda x: f"{x:.3f}"),
            textposition="outside",
            textfont=dict(color="#00ff88", family="Share Tech Mono", size=9),
        ))
        fig_ind.update_layout(**PLOTLY_DARK, height=650,
            title=dict(text=f"AVG {ind.upper()} BY DISTRICT",
                       font=dict(family="Orbitron", color="#00ff88", size=12)))
        st.plotly_chart(fig_ind, use_container_width=True)

    with col_d:
        p33v = dist_df["FSI"].quantile(0.33)
        p66v = dist_df["FSI"].quantile(0.66)
        fig_sc = go.Figure()
        for cat_name, color in {"High":"#ff2222","Medium":"#ffcc00","Low":"#00ff88"}.items():
            sub = df_fsi[df_fsi["FSI"].apply(
                lambda v: "High" if v>=p66v else "Medium" if v>=p33v else "Low")==cat_name]
            if sub.empty: continue
            fig_sc.add_trace(go.Scatter(
                x=sub[ind], y=sub["FSI"], mode="markers",
                marker=dict(color=color, size=7, opacity=0.8, line=dict(color="#020f02", width=0.5)),
                name=cat_name,
                hovertemplate=f"<b>%{{customdata}}</b><br>{ind}: %{{x:.3f}}<br>FSI: %{{y:.4f}}<extra></extra>",
                customdata=sub["Region"],
            ))
        fig_sc.update_layout(**PLOTLY_DARK, height=650,
            title=dict(text=f"{ind.upper()} vs FSI SCORE",
                       font=dict(family="Orbitron", color="#00ff88", size=12)),
            legend=dict(font=dict(color="#00ff88", family="Share Tech Mono")))
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("#### 🔗 CORRELATION MATRIX")
    corr = df_fsi[INDICATORS+["FSI"]].corr().round(3)
    fig_corr = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
        colorscale=[[0,"#ff2222"],[0.5,"#020f02"],[1,"#00ff88"]],
        zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(color="#00ff88", family="Share Tech Mono", size=11),
    ))
    fig_corr.update_layout(**PLOTLY_DARK, height=420,
        title=dict(text="INDICATOR CORRELATION MATRIX",
                   font=dict(family="Orbitron", color="#00ff88", size=12)))
    st.plotly_chart(fig_corr, use_container_width=True)

# ══ TAB 4 ══════════════════════════════════════════════════════
with t4:
    st.markdown("#### 🏆 KARNATAKA DISTRICT STRESS RANKINGS")
    col_h, col_m, col_l = st.columns(3)

    def render_ranking(df_sub, title, color):
        st.markdown(f"<p style='color:{color};font-family:Orbitron;font-size:0.82rem;letter-spacing:2px'>{title}</p>",
                    unsafe_allow_html=True)
        for i, (_, row) in enumerate(df_sub.iterrows(), 1):
            st.markdown(f"""<div class="district-card" style="border-left:3px solid {color}">
                <span style="color:{color};font-size:0.68rem">#{i}</span>
                <span style="color:#00ff88;font-weight:bold;margin-left:7px">{row['Region']}</span><br>
                <span style="color:{color};font-size:0.72rem">FSI: {row['FSI']:.4f}</span>
                <span style="color:#44cc66;font-size:0.62rem;margin-left:8px">Rain:{row['Rainfall']:.2f} Yield:{row['Yield']:.2f}</span>
            </div>""", unsafe_allow_html=True)

    with col_h: render_ranking(dist_df[dist_df["Stress_Category"]=="High"].reset_index(drop=True),  "🔴 HIGH STRESS ZONES",   "#ff4444")
    with col_m: render_ranking(dist_df[dist_df["Stress_Category"]=="Medium"].reset_index(drop=True),"🟡 MEDIUM STRESS ZONES", "#ffcc00")
    with col_l: render_ranking(dist_df[dist_df["Stress_Category"]=="Low"].reset_index(drop=True),   "🟢 LOW STRESS ZONES",    "#00ff88")

    st.divider()
    st.markdown("#### ⚖️ CURRENT WEIGHT CONFIGURATION")
    fig_w = go.Figure(go.Bar(
        x=list(weights.keys()), y=[round(v,3) for v in weights.values()],
        marker=dict(color=["#00aaff","#ffaa00","#00ff88","#ff4444","#aa44ff"],
            line=dict(color="#00ff4430", width=1)),
        text=[f"{v:.2f}" for v in weights.values()], textposition="outside",
        textfont=dict(color="#00ff88", family="Share Tech Mono"),
    ))
    fig_w.update_layout(**PLOTLY_DARK, height=280,
        title=dict(text="FSI INDICATOR WEIGHTS", font=dict(family="Orbitron", color="#00ff88", size=12)),
        yaxis_range=[0, max(weights.values())*1.45])
    st.plotly_chart(fig_w, use_container_width=True)

# ══ TAB 5 ══════════════════════════════════════════════════════
with t5:
    st.markdown("#### 📋 FULL DATASET WITH FSI SCORES")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("TOTAL RECORDS", len(df_fsi))
    m2.metric("DISTRICTS",     df_fsi["Region"].nunique())
    m3.metric("CROPS",         df_fsi["Crop"].nunique())
    m4.metric("STATE",         "Karnataka")

    disp_cols = ["Region","Crop","Rainfall","Price","Cost","Yield","Irrigation","FSI"]
    show_df   = df_fsi[disp_cols].sort_values("FSI", ascending=False).reset_index(drop=True)
    st.dataframe(show_df, use_container_width=True, height=420)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv1 = df_fsi[disp_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ DOWNLOAD FULL RESULTS (CSV)", data=csv1,
            file_name="KA_FSI_Full_Results.csv", mime="text/csv")
    with col_d2:
        dist_exp = dist_df[["Region","FSI","Stress_Category","Rainfall","Yield","Cost","Irrigation","Records"]]
        csv2 = dist_exp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ DOWNLOAD DISTRICT SUMMARY (CSV)", data=csv2,
            file_name="KA_FSI_District_Summary.csv", mime="text/csv")

    st.divider()
    st.markdown("#### 🗺️ DISTRICT SUMMARY TABLE")
    st.dataframe(dist_df[["Region","FSI","Stress_Category","Rainfall","Yield","Cost","Irrigation","Records"]],
        use_container_width=True)
