import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AgriStress Avengers — FSI Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS
st.markdown("""
<style>
    .main { background-color: #f0f4f0; }
    .stMetric { background-color: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); }
    .block-container { padding-top: 1.5rem; }
    h1 { color: #1a4a1a; }
    h2, h3 { color: #2d6a2d; }
    .stress-high { color: #d62728; font-weight: bold; }
    .stress-med  { color: #ff7f0e; font-weight: bold; }
    .stress-low  { color: #2ca02c; font-weight: bold; }
    .sidebar .sidebar-content { background-color: #e8f5e9; }
    div[data-testid="stSidebar"] { background-color: #e8f5e9; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════
# FSI COMPUTATION
# ══════════════════════════════════════
def compute_fsi(df, weights):
    """Compute Farmer Stress Index (0-1, higher = more stress)"""
    scaler = MinMaxScaler()
    result = df.copy()

    # Normalize indicators (stress direction)
    result['norm_rainfall']   = 1 - scaler.fit_transform(df[['Rainfall']])       # less rain = more stress
    result['norm_price']      = 1 - scaler.fit_transform(df[['Price']])           # lower price = more stress
    result['norm_yield']      = 1 - scaler.fit_transform(df[['Yield']])           # lower yield = more stress
    result['norm_cost']       = scaler.fit_transform(df[['Cost']])                 # higher cost = more stress
    result['norm_irrigation'] = 1 - scaler.fit_transform(df[['Irrigation']])      # less irrigation = more stress

    w = weights
    result['FSI'] = (
        w['Rainfall']   * result['norm_rainfall']   +
        w['Price']      * result['norm_price']       +
        w['Yield']      * result['norm_yield']       +
        w['Cost']       * result['norm_cost']        +
        w['Irrigation'] * result['norm_irrigation']
    )

    result['FSI'] = result['FSI'].round(4)
    result['Stress_Category'] = pd.cut(
        result['FSI'],
        bins=[0, 0.4, 0.65, 1.0],
        labels=['Low', 'Medium', 'High'],
        include_lowest=True
    )
    return result


def district_summary(df_fsi):
    grp = df_fsi.groupby('Region').agg(
        FSI=('FSI', 'mean'),
        Rainfall=('Rainfall', 'mean'),
        Price=('Price', 'mean'),
        Cost=('Cost', 'mean'),
        Yield=('Yield', 'mean'),
        Irrigation=('Irrigation', 'mean'),
        Sample_Count=('FSI', 'count')
    ).reset_index()
    grp['FSI'] = grp['FSI'].round(4)
    grp['Stress_Category'] = pd.cut(
        grp['FSI'], bins=[0, 0.4, 0.65, 1.0],
        labels=['Low', 'Medium', 'High'], include_lowest=True
    )
    grp = grp.sort_values('FSI', ascending=False)
    return grp


# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2165/2165694.png", width=60)
    st.title("🌾 AgriStress Avengers")
    st.caption("Spatial Hotspot Detection of Farmer Stress")
    st.divider()

    st.subheader("📂 Data Source")
    upload = st.file_uploader("Upload dataset (Excel/CSV)", type=['xlsx','csv'])

    st.divider()
    st.subheader("⚖️ FSI Indicator Weights")
    st.caption("Adjust how much each factor contributes to stress")

    w_rain = st.slider("🌧️ Rainfall",   0.0, 1.0, 0.25, 0.05)
    w_price= st.slider("💰 Market Price",0.0, 1.0, 0.25, 0.05)
    w_yield= st.slider("🌾 Crop Yield",  0.0, 1.0, 0.20, 0.05)
    w_cost = st.slider("🧾 Cultivation Cost", 0.0, 1.0, 0.20, 0.05)
    w_irr  = st.slider("💧 Irrigation",  0.0, 1.0, 0.10, 0.05)

    total_w = w_rain + w_price + w_yield + w_cost + w_irr
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum = {total_w:.2f} (should be 1.0). Auto-normalizing.")
        if total_w > 0:
            w_rain /= total_w; w_price /= total_w
            w_yield /= total_w; w_cost /= total_w; w_irr /= total_w

    weights = {'Rainfall': w_rain, 'Price': w_price,
               'Yield': w_yield, 'Cost': w_cost, 'Irrigation': w_irr}

    st.divider()
    st.subheader("🔍 Filters")
    crop_filter = st.multiselect("Filter by Crop", options=[], default=[])
    region_filter = st.multiselect("Filter by District", options=[], default=[])

    st.divider()
    st.caption("Group: AGRISTRESS AVENGERS\nBadiya Sunil Kumar | Yashaswini H V\nSRL Keerthi | Sibbala Yoshitha")


# ══════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════
@st.cache_data
def load_default():
    return pd.read_excel("data/agri_dataset_500_samples.xlsx")

if upload:
    try:
        if upload.name.endswith('.csv'):
            df_raw = pd.read_csv(upload)
        else:
            df_raw = pd.read_excel(upload)
        st.sidebar.success(f"✅ Loaded: {upload.name}")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        df_raw = load_default()
else:
    df_raw = load_default()

# Update sidebar filters
all_crops   = sorted(df_raw['Crop'].unique().tolist())
all_regions = sorted(df_raw['Region'].unique().tolist())

with st.sidebar:
    crop_filter   = st.multiselect("Filter by Crop",     all_crops,   default=all_crops,   key="crop_f")
    region_filter = st.multiselect("Filter by District", all_regions, default=all_regions, key="reg_f")

df_filtered = df_raw[
    df_raw['Crop'].isin(crop_filter) &
    df_raw['Region'].isin(region_filter)
].copy()

if df_filtered.empty:
    st.error("No data matches the selected filters. Please adjust.")
    st.stop()

df_fsi     = compute_fsi(df_filtered, weights)
dist_df    = district_summary(df_fsi)
high_count = (dist_df['Stress_Category'] == 'High').sum()
med_count  = (dist_df['Stress_Category'] == 'Medium').sum()
low_count  = (dist_df['Stress_Category'] == 'Low').sum()
avg_fsi    = df_fsi['FSI'].mean()


# ══════════════════════════════════════
# HEADER
# ══════════════════════════════════════
st.markdown("## 🌾 Farmer Stress Index — Spatial Hotspot Dashboard")
st.markdown("**AP & Karnataka | 2015–2023 | AgriStress Avengers**")
st.divider()

# ══════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📊 Avg FSI Score",    f"{avg_fsi:.3f}",  help="0=No stress, 1=Max stress")
k2.metric("🔴 High Stress Districts", high_count,   help="FSI > 0.65")
k3.metric("🟠 Medium Stress",    med_count,          help="FSI 0.40–0.65")
k4.metric("🟢 Low Stress",       low_count,          help="FSI < 0.40")
k5.metric("📍 Total Districts",  dist_df.shape[0])


# ══════════════════════════════════════
# TABS
# ══════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Hotspot Map", "📊 FSI Analysis", "📈 Indicator Deep Dive",
    "🏆 District Rankings", "📋 Raw Data"
])


# ── TAB 1: HOTSPOT MAP
with tab1:
    st.subheader("🗺️ District-wise Farmer Stress Hotspot Map")

    col1, col2 = st.columns([2, 1])

    with col1:
        color_map = {'High': '#d62728', 'Medium': '#ff7f0e', 'Low': '#2ca02c'}
        fig_map = px.bar(
            dist_df.sort_values('FSI', ascending=True),
            x='FSI', y='Region',
            color='Stress_Category',
            color_discrete_map=color_map,
            orientation='h',
            title='Farmer Stress Index by District',
            labels={'FSI': 'FSI Score (0–1)', 'Region': 'District'},
            height=600,
            text='FSI'
        )
        fig_map.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_map.update_layout(
            plot_bgcolor='#f9fdf9',
            paper_bgcolor='white',
            font=dict(size=12),
            legend_title='Stress Level',
            xaxis=dict(range=[0, 1.1])
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.markdown("#### 🎯 Stress Distribution")
        fig_pie = px.pie(
            values=[high_count, med_count, low_count],
            names=['High Stress', 'Medium Stress', 'Low Stress'],
            color_discrete_sequence=['#d62728', '#ff7f0e', '#2ca02c'],
            hole=0.45
        )
        fig_pie.update_layout(height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### 🔴 Top 5 Hotspots")
        top5 = dist_df.head(5)[['Region', 'FSI', 'Stress_Category']]
        for _, row in top5.iterrows():
            cat = row['Stress_Category']
            color = color_map.get(str(cat), '#888')
            st.markdown(
                f"<div style='padding:6px;margin:3px 0;border-left:4px solid {color};"
                f"background:#fff;border-radius:4px'>"
                f"<b>{row['Region']}</b> — FSI: <b>{row['FSI']:.3f}</b></div>",
                unsafe_allow_html=True
            )

        st.markdown("#### 🟢 Least Stressed (Bottom 3)")
        bot3 = dist_df.tail(3)[['Region', 'FSI']]
        for _, row in bot3.iterrows():
            st.markdown(
                f"<div style='padding:6px;margin:3px 0;border-left:4px solid #2ca02c;"
                f"background:#fff;border-radius:4px'>"
                f"<b>{row['Region']}</b> — FSI: <b>{row['FSI']:.3f}</b></div>",
                unsafe_allow_html=True
            )


# ── TAB 2: FSI ANALYSIS
with tab2:
    st.subheader("📊 FSI Score Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_hist = px.histogram(
            df_fsi, x='FSI', color='Stress_Category',
            color_discrete_map={'High':'#d62728','Medium':'#ff7f0e','Low':'#2ca02c'},
            nbins=30, title='FSI Distribution across All Records',
            labels={'FSI': 'FSI Score', 'count': 'Number of Records'}
        )
        fig_hist.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white')
        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        fig_box = px.box(
            df_fsi, x='Crop', y='FSI', color='Stress_Category',
            color_discrete_map={'High':'#d62728','Medium':'#ff7f0e','Low':'#2ca02c'},
            title='FSI Distribution by Crop',
            points='outliers'
        )
        fig_box.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white')
        st.plotly_chart(fig_box, use_container_width=True)

    # Radar chart for top stressed district
    st.subheader("🕸️ Indicator Profile — Top vs Bottom District")
    top_dist    = dist_df.iloc[0]['Region']
    bottom_dist = dist_df.iloc[-1]['Region']

    indicators = ['Rainfall', 'Price', 'Yield', 'Cost', 'Irrigation']
    scaler2 = MinMaxScaler()
    df_scaled = df_fsi.copy()
    df_scaled[indicators] = scaler2.fit_transform(df_fsi[indicators])

    top_vals    = df_scaled[df_scaled['Region']==top_dist][indicators].mean().tolist()
    bottom_vals = df_scaled[df_scaled['Region']==bottom_dist][indicators].mean().tolist()

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=top_vals + [top_vals[0]], theta=indicators + [indicators[0]],
        fill='toself', name=f'🔴 {top_dist}',
        line_color='#d62728', fillcolor='rgba(214,39,40,0.2)'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=bottom_vals + [bottom_vals[0]], theta=indicators + [indicators[0]],
        fill='toself', name=f'🟢 {bottom_dist}',
        line_color='#2ca02c', fillcolor='rgba(44,160,44,0.2)'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        title='Indicator Comparison: Most vs Least Stressed District',
        height=450, paper_bgcolor='white'
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ── TAB 3: INDICATOR DEEP DIVE
with tab3:
    st.subheader("📈 Individual Indicator Analysis")

    indicator = st.selectbox("Select Indicator", ['Rainfall','Price','Yield','Cost','Irrigation'])

    col1, col2 = st.columns(2)

    with col1:
        fig_ind = px.bar(
            df_fsi.groupby('Region')[indicator].mean().reset_index().sort_values(indicator),
            x=indicator, y='Region', orientation='h',
            title=f'Average {indicator} by District',
            color=indicator, color_continuous_scale='RdYlGn' if indicator!='Cost' else 'RdYlGn_r',
            height=500
        )
        fig_ind.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white')
        st.plotly_chart(fig_ind, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            df_fsi, x=indicator, y='FSI',
            color='Stress_Category', size_max=8,
            color_discrete_map={'High':'#d62728','Medium':'#ff7f0e','Low':'#2ca02c'},
            title=f'{indicator} vs FSI Score',
            trendline='ols', hover_data=['Region','Crop']
        )
        fig_scatter.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white')
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Correlation heatmap
    st.subheader("🔗 Indicator Correlation Matrix")
    corr_cols = ['Rainfall','Price','Yield','Cost','Irrigation','FSI']
    corr = df_fsi[corr_cols].corr().round(3)
    fig_corr = px.imshow(
        corr, text_auto=True, color_continuous_scale='RdBu_r',
        title='Correlation between Indicators and FSI',
        zmin=-1, zmax=1, height=450
    )
    fig_corr.update_layout(paper_bgcolor='white')
    st.plotly_chart(fig_corr, use_container_width=True)


# ── TAB 4: DISTRICT RANKINGS
with tab4:
    st.subheader("🏆 District Stress Rankings")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔴 High Stress Districts")
        high_df = dist_df[dist_df['Stress_Category']=='High'][['Region','FSI','Rainfall','Yield','Cost']].reset_index(drop=True)
        high_df.index += 1
        st.dataframe(high_df.style.background_gradient(subset=['FSI'], cmap='Reds'), use_container_width=True)

    with col2:
        st.markdown("### 🟠 Medium Stress Districts")
        med_df = dist_df[dist_df['Stress_Category']=='Medium'][['Region','FSI','Rainfall','Yield','Cost']].reset_index(drop=True)
        med_df.index += 1
        st.dataframe(med_df.style.background_gradient(subset=['FSI'], cmap='Oranges'), use_container_width=True)

    with col3:
        st.markdown("### 🟢 Low Stress Districts")
        low_df = dist_df[dist_df['Stress_Category']=='Low'][['Region','FSI','Rainfall','Yield','Cost']].reset_index(drop=True)
        low_df.index += 1
        st.dataframe(low_df.style.background_gradient(subset=['FSI'], cmap='Greens_r'), use_container_width=True)

    st.divider()
    st.subheader("📊 Weight Contribution to FSI")
    fig_weights = px.bar(
        x=list(weights.keys()), y=list(weights.values()),
        labels={'x':'Indicator','y':'Weight'},
        title='Current FSI Indicator Weights',
        color=list(weights.values()),
        color_continuous_scale='Greens'
    )
    fig_weights.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white', showlegend=False)
    st.plotly_chart(fig_weights, use_container_width=True)

    # Crop-wise stress
    st.subheader("🌾 Stress by Crop Type")
    crop_stress = df_fsi.groupby('Crop').agg(
        Avg_FSI=('FSI','mean'),
        High_Count=('Stress_Category', lambda x: (x=='High').sum()),
        Total=('FSI','count')
    ).reset_index()
    crop_stress['High_Pct'] = (crop_stress['High_Count']/crop_stress['Total']*100).round(1)
    crop_stress = crop_stress.sort_values('Avg_FSI', ascending=False)
    fig_crop = px.bar(
        crop_stress, x='Crop', y='Avg_FSI',
        color='Avg_FSI', color_continuous_scale='RdYlGn_r',
        title='Average FSI by Crop', text='Avg_FSI'
    )
    fig_crop.update_traces(texttemplate='%{text:.3f}')
    fig_crop.update_layout(plot_bgcolor='#f9fdf9', paper_bgcolor='white')
    st.plotly_chart(fig_crop, use_container_width=True)


# ── TAB 5: RAW DATA
with tab5:
    st.subheader("📋 FSI Dataset with Computed Scores")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records",    len(df_fsi))
    col2.metric("Districts",        df_fsi['Region'].nunique())
    col3.metric("Crops",            df_fsi['Crop'].nunique())

    show_cols = ['Region','Crop','Rainfall','Price','Cost','Yield','Irrigation','FSI','Stress_Category']
    st.dataframe(
        df_fsi[show_cols].sort_values('FSI', ascending=False).reset_index(drop=True)
        .style.background_gradient(subset=['FSI'], cmap='RdYlGn_r')
        .format({'FSI':'{:.4f}','Rainfall':'{:.1f}','Price':'{:.2f}',
                 'Cost':'{:.2f}','Yield':'{:.2f}','Irrigation':'{:.2f}'}),
        use_container_width=True, height=500
    )

    csv = df_fsi[show_cols].to_csv(index=False)
    st.download_button(
        "⬇️ Download FSI Results as CSV",
        data=csv, file_name="FSI_Results_AP_Karnataka.csv",
        mime="text/csv"
    )

    st.divider()
    st.subheader("📊 District Summary Table")
    st.dataframe(
        dist_df.style.background_gradient(subset=['FSI'], cmap='RdYlGn_r')
        .format({'FSI':'{:.4f}','Rainfall':'{:.1f}','Price':'{:.2f}',
                 'Cost':'{:.2f}','Yield':'{:.2f}','Irrigation':'{:.2f}'}),
        use_container_width=True
    )
    csv2 = dist_df.to_csv(index=False)
    st.download_button(
        "⬇️ Download District Summary CSV",
        data=csv2, file_name="FSI_District_Summary.csv",
        mime="text/csv"
    )
