# =========================================================
# src/gui/map_view.py
# Plotly Mapbox interactive heatmap for Karnataka FSI.
# =========================================================

import pandas as pd
import plotly.graph_objects as go


def build_map(hex_df: pd.DataFrame, zoom: int = 6) -> go.Figure:
    """
    Build the interactive Karnataka FSI scatter-mapbox heatmap.

    Each district is represented as a circle marker:
      - Colour: FSI value mapped to RdYlGn (red=high, green=low stress)
      - Size:   proportional to FSI (14–28px range)
      - Hover:  full district breakdown on mouse-over

    Parameters
    ----------
    hex_df : pd.DataFrame — aggregated district data with lat/lon/FSI.
    zoom   : int — initial map zoom level (default 6).

    Returns
    -------
    plotly.graph_objects.Figure
    """
    marker_sizes = hex_df["FSI"].apply(lambda x: 14 + x * 14)

    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=hex_df["lat"],
        lon=hex_df["lon"],
        mode="markers",
        marker=dict(
            size=marker_sizes,
            color=hex_df["FSI"],
            colorscale="RdYlGn",
            reversescale=True,
            opacity=0.90,
            colorbar=dict(
                title=dict(text="FSI", font=dict(color="#00ff88", family="Share Tech Mono")),
                tickfont=dict(color="#00ff88", family="Share Tech Mono"),
                bgcolor="rgba(0,13,2,0.85)",
                bordercolor="rgba(0,255,136,0.3)",
                borderwidth=1,
                thickness=14,
                len=0.75,
            )
        ),
        customdata=hex_df[[
            "Region", "Stress", "Reason", "Samples",
            "Rainfall", "Price", "Yield", "Cost", "Irrigation"
        ]].values,
        hovertemplate=(
            "<b>🎯 %{customdata[0]}</b><br>"
            "━━━━━━━━━━━━━━━━━━<br>"
            "⚡ FSI Score: <b>%{marker.color:.3f}</b><br>"
            "🚨 Stress: <b>%{customdata[1]}</b><br>"
            "🧠 Reason: %{customdata[2]}<br>"
            "━━━━━━━━━━━━━━━━━━<br>"
            "🌧 Rainfall: %{customdata[4]:.2f} | 💰 Price: %{customdata[5]:.2f}<br>"
            "🌿 Yield: %{customdata[6]:.2f} | 📦 Cost: %{customdata[7]:.2f}<br>"
            "💧 Irrigation: %{customdata[8]:.2f}<br>"
            "📊 Samples: %{customdata[3]}<extra></extra>"
        )
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=14.5, lon=76.5),
            zoom=zoom,
        ),
        height=560,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Rajdhani", color="#00ff88"),
    )
    return fig
