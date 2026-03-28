import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="AgriStress Avengers — FSI Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #e8f5e9; }
.main { background-color: #f4f9f4; }
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════
@st.cache_data
def load_default():
    return pd.read_excel("agri_dataset_500_samples.xlsx")


def load_uploaded(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)


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
    out["Stress_Category"] = pd.cut(
        out["FSI"], bins=[0, 0.40, 0.65, 1.01],
        labels=["Low", "Medium", "High"], include_lowest=True
    )
    return out


def district_summary(df_fsi):
    grp = df_fsi.groupby("Region", as_index=False).agg(
        FSI        = ("FSI",        "mean"),
        Rainfall   = ("Rainfall",   "mean"),
        Price      = ("Price",      "mean"),
        Cost       = ("Cost",       "mean"),
        Yield      = ("Yield",      "mean"),
        Irrigation = ("Irrigation", "mean"),
        Records    = ("FSI",        "count"),
    )
    grp["FSI"] = grp["FSI"].round(4)
    grp["Stress_Category"] = pd.cut(
        grp["FSI"], bins=[0, 0.40, 0.65, 1.01],
        labels=["Low", "Medium", "High"], include_lowest=True
    )
    return grp.sort_values("FSI", ascending=False).reset_index(drop=True)


CAT_COLORS = {"High": "#d62728", "Medium": "#ff7f0e", "Low": "#2ca02c"}
INDICATORS = ["Rainfall", "Price", "Yield", "Cost", "Irrigation"]


# ════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌾 AgriStress Avengers")
    st.caption("Farmer Stress Index Dashboard\nAP & Karnataka · 2015–2023")
    st.divider()

    uploaded = st.file_uploader("📂 Upload dataset (Excel / CSV)", type=["xlsx", "csv"])
    st.divider()

    st.markdown("### ⚖️ FSI Weights")
    st.caption("Adjust contribution of each stress indicator")
    w_rain  = st.slider("🌧️ Rainfall",        0.0, 1.0, 0.25, 0.05)
    w_price = st.slider("💰 Market Price",     0.0, 1.0, 0.25, 0.05)
    w_yield = st.slider("🌾 Crop Yield",       0.0, 1.0, 0.20, 0.05)
    w_cost  = st.slider("🧾 Cultivation Cost", 0.0, 1.0, 0.20, 0.05)
    w_irr   = st.slider("💧 Irrigation",       0.0, 1.0, 0.10, 0.05)

    total = w_rain + w_price + w_yield + w_cost + w_irr
    if total == 0:
        total = 1.0
    weights = {
        "Rainfall":   w_rain  / total,
        "Price":      w_price / total,
        "Yield":      w_yield / total,
        "Cost":       w_cost  / total,
        "Irrigation": w_irr   / total,
    }
    st.info(f"Weights auto-normalised · Sum = {sum(weights.values()):.2f}")
    st.divider()
    st.caption("Badiya Sunil Kumar · Yashaswini H V\nSRL Keerthi · Sibbala Yoshitha")


# ════════════════════════════════════════
# LOAD DATA
# ════════════════════════════════════════
if uploaded is not None:
    df_raw = load_uploaded(uploaded)
else:
    df_raw = load_default()

required = {"Region", "Crop", "Rainfall", "Price", "Cost", "Yield", "Irrigation"}
missing  = required - set(df_raw.columns)
if missing:
    st.error(f"Dataset is missing columns: {missing}")
    st.stop()

# Sidebar filters (after data is loaded)
with st.sidebar:
    st.markdown("### 🔍 Filters")
    all_crops   = sorted(df_raw["Crop"].dropna().unique().tolist())
    all_regions = sorted(df_raw["Region"].dropna().unique().tolist())
    sel_crops   = st.multiselect("Crop",     all_crops,   default=all_crops)
    sel_regions = st.multiselect("District", all_regions, default=all_regions)

df_f = df_raw[
    df_raw["Crop"].isin(sel_crops) &
    df_raw["Region"].isin(sel_regions)
].copy()

if df_f.empty:
    st.warning("No data for selected filters. Please adjust.")
    st.stop()

df_fsi  = compute_fsi(df_f, weights)
dist_df = district_summary(df_fsi)

n_high  = int((dist_df["Stress_Category"] == "High").sum())
n_med   = int((dist_df["Stress_Category"] == "Medium").sum())
n_low   = int((dist_df["Stress_Category"] == "Low").sum())
avg_fsi = float(df_fsi["FSI"].mean())


# ════════════════════════════════════════
# HEADER + KPIs
# ════════════════════════════════════════
st.markdown("## 🌾 Farmer Stress Index — Spatial Hotspot Dashboard")
st.markdown("**Andhra Pradesh & Karnataka · AgriStress Avengers**")
st.divider()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📊 Avg FSI Score",          f"{avg_fsi:.3f}")
c2.metric("🔴 High Stress Districts",   n_high)
c3.metric("🟠 Medium Stress Districts", n_med)
c4.metric("🟢 Low Stress Districts",    n_low)
c5.metric("📍 Total Districts",         len(dist_df))
st.divider()


# ════════════════════════════════════════
# TABS
# ════════════════════════════════════════
t1, t2, t3, t4, t5 = st.tabs([
    "🗺️ Hotspot Map",
    "📊 FSI Analysis",
    "📈 Indicator Dive",
    "🏆 Rankings",
    "📋 Data & Export",
])


# ── TAB 1 ────────────────────────────
with t1:
    st.subheader("District-wise Farmer Stress Hotspot Map")
    col_map, col_side = st.columns([3, 1])

    with col_map:
        fig_bar = px.bar(
            dist_df.sort_values("FSI"),
            x="FSI", y="Region",
            color="Stress_Category",
            color_discrete_map=CAT_COLORS,
            orientation="h",
            text="FSI",
            labels={"FSI": "FSI Score (0–1)", "Region": "District"},
            title="Farmer Stress Index by District",
            height=620,
        )
        fig_bar.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_bar.update_layout(
            xaxis_range=[0, 1.1],
            plot_bgcolor="#f9fdf9",
            paper_bgcolor="white",
            legend_title="Stress Level",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_side:
        st.markdown("#### Stress Distribution")
        fig_pie = px.pie(
            values=[n_high, n_med, n_low],
            names=["High", "Medium", "Low"],
            color_discrete_sequence=["#d62728", "#ff7f0e", "#2ca02c"],
            hole=0.45,
        )
        fig_pie.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### 🔴 Top 5 Hotspots")
        for _, row in dist_df.head(5).iterrows():
            c = CAT_COLORS.get(str(row["Stress_Category"]), "#888")
            st.markdown(
                f"<div style='border-left:4px solid {c};padding:5px 8px;"
                f"margin:3px 0;background:#fff;border-radius:4px;font-size:13px'>"
                f"<b>{row['Region']}</b><br>FSI: <b>{row['FSI']:.3f}</b></div>",
                unsafe_allow_html=True,
            )

        st.markdown("#### 🟢 Least Stressed")
        for _, row in dist_df.tail(3).iterrows():
            st.markdown(
                f"<div style='border-left:4px solid #2ca02c;padding:5px 8px;"
                f"margin:3px 0;background:#fff;border-radius:4px;font-size:13px'>"
                f"<b>{row['Region']}</b><br>FSI: <b>{row['FSI']:.3f}</b></div>",
                unsafe_allow_html=True,
            )


# ── TAB 2 ────────────────────────────
with t2:
    st.subheader("FSI Distribution & Crop Analysis")

    col_a, col_b = st.columns(2)
    with col_a:
        fig_hist = px.histogram(
            df_fsi, x="FSI", color="Stress_Category",
            color_discrete_map=CAT_COLORS, nbins=30,
            title="FSI Distribution (All Records)",
            labels={"FSI": "FSI Score"},
        )
        fig_hist.update_layout(plot_bgcolor="#f9fdf9", paper_bgcolor="white")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_b:
        fig_box = px.box(
            df_fsi, x="Crop", y="FSI", color="Stress_Category",
            color_discrete_map=CAT_COLORS, points="outliers",
            title="FSI by Crop Type",
        )
        fig_box.update_layout(plot_bgcolor="#f9fdf9", paper_bgcolor="white")
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Radar Profile: Most vs Least Stressed District")
    top_r = dist_df.iloc[0]["Region"]
    bot_r = dist_df.iloc[-1]["Region"]

    scaler2 = MinMaxScaler()
    df_sc   = df_fsi.copy()
    df_sc[INDICATORS] = scaler2.fit_transform(df_fsi[INDICATORS])

    tv = df_sc[df_sc["Region"] == top_r][INDICATORS].mean().tolist()
    bv = df_sc[df_sc["Region"] == bot_r][INDICATORS].mean().tolist()

    fig_rad = go.Figure()
    fig_rad.add_trace(go.Scatterpolar(
        r=tv + [tv[0]], theta=INDICATORS + [INDICATORS[0]],
        fill="toself", name=f"🔴 {top_r}",
        line_color="#d62728", fillcolor="rgba(214,39,40,0.2)",
    ))
    fig_rad.add_trace(go.Scatterpolar(
        r=bv + [bv[0]], theta=INDICATORS + [INDICATORS[0]],
        fill="toself", name=f"🟢 {bot_r}",
        line_color="#2ca02c", fillcolor="rgba(44,160,44,0.2)",
    ))
    fig_rad.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Indicator Profile: Most vs Least Stressed District",
        height=450, paper_bgcolor="white",
    )
    st.plotly_chart(fig_rad, use_container_width=True)


# ── TAB 3 ────────────────────────────
with t3:
    st.subheader("Individual Indicator Deep Dive")

    ind = st.selectbox("Select Indicator", INDICATORS)

    col_c, col_d = st.columns(2)
    with col_c:
        agg   = df_fsi.groupby("Region")[ind].mean().reset_index().sort_values(ind)
        scale = "RdYlGn" if ind != "Cost" else "RdYlGn_r"
        fig_ind = px.bar(
            agg, x=ind, y="Region", orientation="h",
            color=ind, color_continuous_scale=scale,
            title=f"Average {ind} by District", height=500,
        )
        fig_ind.update_layout(plot_bgcolor="#f9fdf9", paper_bgcolor="white")
        st.plotly_chart(fig_ind, use_container_width=True)

    with col_d:
        fig_sc = px.scatter(
            df_fsi, x=ind, y="FSI",
            color="Stress_Category",
            color_discrete_map=CAT_COLORS,
            hover_data=["Region", "Crop"],
            title=f"{ind} vs FSI Score",
            trendline="ols",
        )
        fig_sc.update_layout(plot_bgcolor="#f9fdf9", paper_bgcolor="white")
        st.plotly_chart(fig_sc, use_container_width=True)

    st.subheader("Correlation Matrix")
    corr_cols = INDICATORS + ["FSI"]
    corr = df_fsi[corr_cols].corr().round(3)
    fig_corr = px.imshow(
        corr, text_auto=True, color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Correlation between All Indicators and FSI",
        height=450,
    )
    fig_corr.update_layout(paper_bgcolor="white")
    st.plotly_chart(fig_corr, use_container_width=True)


# ── TAB 4 ────────────────────────────
with t4:
    st.subheader("District Stress Rankings")
    show_cols = ["Region", "FSI", "Rainfall", "Yield", "Cost"]

    col_h, col_m, col_l = st.columns(3)
    fmt = {"FSI": "{:.4f}", "Rainfall": "{:.1f}", "Yield": "{:.1f}", "Cost": "{:.0f}"}

    with col_h:
        st.markdown("### 🔴 High Stress")
        h_df = dist_df[dist_df["Stress_Category"] == "High"][show_cols].reset_index(drop=True)
        h_df.index += 1
        st.dataframe(h_df.style.background_gradient(subset=["FSI"], cmap="Reds").format(fmt),
                     use_container_width=True)

    with col_m:
        st.markdown("### 🟠 Medium Stress")
        m_df = dist_df[dist_df["Stress_Category"] == "Medium"][show_cols].reset_index(drop=True)
        m_df.index += 1
        st.dataframe(m_df.style.background_gradient(subset=["FSI"], cmap="Oranges").format(fmt),
                     use_container_width=True)

    with col_l:
        st.markdown("### 🟢 Low Stress")
        l_df = dist_df[dist_df["Stress_Category"] == "Low"][show_cols].reset_index(drop=True)
        l_df.index += 1
        st.dataframe(l_df.style.background_gradient(subset=["FSI"], cmap="Greens_r").format(fmt),
                     use_container_width=True)

    st.divider()
    col_w, col_crop = st.columns(2)

    with col_w:
        st.subheader("Current FSI Weights")
        fig_w = px.bar(
            x=list(weights.keys()),
            y=[round(v, 3) for v in weights.values()],
            color=list(weights.values()),
            color_continuous_scale="Greens",
            text=[f"{v:.2f}" for v in weights.values()],
            labels={"x": "Indicator", "y": "Weight"},
            title="FSI Indicator Weights",
        )
        fig_w.update_traces(textposition="outside")
        fig_w.update_layout(
            plot_bgcolor="#f9fdf9", paper_bgcolor="white",
            showlegend=False,
            yaxis_range=[0, max(weights.values()) * 1.35],
        )
        st.plotly_chart(fig_w, use_container_width=True)

    with col_crop:
        st.subheader("Stress by Crop")
        crop_agg = df_fsi.groupby("Crop", as_index=False).agg(
            Avg_FSI=("FSI", "mean"),
        ).sort_values("Avg_FSI", ascending=False)
        fig_crop = px.bar(
            crop_agg, x="Crop", y="Avg_FSI",
            color="Avg_FSI", color_continuous_scale="RdYlGn_r",
            text="Avg_FSI", title="Average FSI by Crop",
        )
        fig_crop.update_traces(texttemplate="%{text:.3f}", textposition="outside")
        fig_crop.update_layout(
            plot_bgcolor="#f9fdf9", paper_bgcolor="white",
            showlegend=False, yaxis_range=[0, 1],
        )
        st.plotly_chart(fig_crop, use_container_width=True)


# ── TAB 5 ────────────────────────────
with t5:
    st.subheader("Full Dataset with FSI Scores")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", len(df_fsi))
    m2.metric("Districts",     df_fsi["Region"].nunique())
    m3.metric("Crops",         df_fsi["Crop"].nunique())

    disp_cols = ["Region", "Crop", "Rainfall", "Price", "Cost",
                 "Yield", "Irrigation", "FSI", "Stress_Category"]
    fmt2 = {"FSI": "{:.4f}", "Rainfall": "{:.1f}", "Price": "{:.2f}",
            "Cost": "{:.2f}", "Yield": "{:.2f}", "Irrigation": "{:.2f}"}

    st.dataframe(
        df_fsi[disp_cols]
            .sort_values("FSI", ascending=False)
            .reset_index(drop=True)
            .style.background_gradient(subset=["FSI"], cmap="RdYlGn_r")
                  .format(fmt2),
        use_container_width=True,
        height=480,
    )

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv1 = df_fsi[disp_cols].to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full Results (CSV)", data=csv1,
                           file_name="FSI_Full_Results.csv", mime="text/csv")
    with col_dl2:
        csv2 = dist_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download District Summary (CSV)", data=csv2,
                           file_name="FSI_District_Summary.csv", mime="text/csv")

    st.divider()
    st.subheader("District Summary Table")
    st.dataframe(
        dist_df.style
            .background_gradient(subset=["FSI"], cmap="RdYlGn_r")
            .format(fmt2),
        use_container_width=True,
    )
