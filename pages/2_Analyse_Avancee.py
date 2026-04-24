"""
Athena Core — Page 2: Analyse Avancée
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styles import inject_css
from utils.helpers import page_header
from utils.charts import line_chart, scatter_chart, bar_chart, _base_layout
from core.data_loader import load_order_items, load_orders, load_daily_revenue
from analytics.trends import (
    compute_moving_averages, detect_trend_direction,
    seasonal_decomposition, compute_weekly_pattern, compute_monthly_seasonality,
)
from analytics.segmentation import compute_rfm, rfm_scoring, kmeans_segmentation
from analytics.performance import (
    performance_by_category, performance_by_product, monthly_heatmap_data, yoy_comparison,
)

st.set_page_config(page_title="Analyse Avancée — Athena Core", layout="wide")
inject_css()
page_header("Analyse Avancée", "Tendances, segmentation clients et performances détaillées")

tab1, tab2, tab3 = st.tabs(["Tendances", "Segmentation", "Performance"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — TENDANCES
# ═══════════════════════════════════════════════════════════════════
with tab1:
    daily = load_daily_revenue()
    trend = detect_trend_direction(daily, window=90)

    # Trend indicator
    icons = {"up": "▲", "down": "▼", "neutral": "■"}
    colors = {"up": "#00E676", "down": "#FF5252", "neutral": "#FFD600"}
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tendance (90j)", f"{icons[trend['direction']]} {trend['direction'].upper()}",
                  delta=f"{trend['change_pct']}%")
    with col2:
        st.metric("R²", f"{trend['r_squared']:.3f}")
    with col3:
        st.metric("p-value", f"{trend['p_value']:.4f}")

    # Moving averages
    ma_df = compute_moving_averages(daily)
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ma_df["order_date"], y=ma_df["revenue"],
                             mode="lines", name="Revenue", opacity=0.3, line=dict(width=1)))
    fig.add_trace(go.Scatter(x=ma_df["order_date"], y=ma_df["ma_7d"],
                             mode="lines", name="MA 7j", line=dict(width=2, color="#6C63FF")))
    fig.add_trace(go.Scatter(x=ma_df["order_date"], y=ma_df["ma_30d"],
                             mode="lines", name="MA 30j", line=dict(width=2, color="#00D9FF")))
    fig.add_trace(go.Scatter(x=ma_df["order_date"], y=ma_df["ma_90d"],
                             mode="lines", name="MA 90j", line=dict(width=2.5, color="#00E676")))
    st.plotly_chart(_base_layout(fig, "Moyennes Mobiles"), use_container_width=True)

    # Seasonality
    col_a, col_b = st.columns(2)
    with col_a:
        weekly = compute_weekly_pattern(daily)
        st.plotly_chart(bar_chart(weekly, "day_of_week", "avg_revenue", "Pattern Hebdomadaire"),
                        width='stretch')
    with col_b:
        monthly_s = compute_monthly_seasonality(daily)
        st.plotly_chart(bar_chart(monthly_s, "month_name", "avg_revenue", "Saisonnalité Mensuelle"),
                        width='stretch')

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — SEGMENTATION
# ═══════════════════════════════════════════════════════════════════
with tab2:
    orders = load_orders()
    rfm = compute_rfm(orders)
    rfm_scored = rfm_scoring(rfm)
    rfm_clustered, cluster_stats, label_map = kmeans_segmentation(rfm_scored, n_clusters=4)

    # Segment summary
    st.subheader("Segments Clients (RFM + KMeans)")
    cols = st.columns(4)
    for i, (_, row) in enumerate(cluster_stats.iterrows()):
        label = label_map[row["cluster"]]
        with cols[i]:
            st.metric(label, f"{int(row['count'])} clients",
                      delta=f"Moy: {row['avg_monetary']:.0f}€")

    # 3D Scatter
    fig = px.scatter_3d(rfm_clustered, x="recency", y="frequency", z="monetary",
                        color="segment_label", opacity=0.7,
                        title="Segmentation RFM — Vue 3D")
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      scene=dict(xaxis_title="Récence (jours)",
                                 yaxis_title="Fréquence", zaxis_title="Montant (€)"))
    st.plotly_chart(fig, use_container_width=True)

    # Distribution
    fig2 = px.histogram(rfm_clustered, x="rfm_score", color="segment_label",
                        nbins=12, title="Distribution des Scores RFM")
    st.plotly_chart(_base_layout(fig2, "Distribution RFM"), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — PERFORMANCE
# ═══════════════════════════════════════════════════════════════════
with tab3:
    oi = load_order_items()

    # Category performance
    cat_perf = performance_by_category(oi)
    cat_perf["margin_pct"] = (cat_perf["margin"] / cat_perf["revenue"] * 100).round(1)

    col1, col2 = st.columns(2)
    with col1:
        fig = bar_chart(cat_perf, "category_name", "revenue", "Revenue par Catégorie")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = bar_chart(cat_perf, "category_name", "margin_pct", "Marge (%) par Catégorie")
        st.plotly_chart(fig, use_container_width=True)

    # Product performance table
    st.subheader("Top Produits — Performance Détaillée")
    prod_perf = performance_by_product(oi, top_n=15)
    st.dataframe(
        prod_perf[["product_name", "category_name", "revenue", "margin", "margin_pct", "units"]]
        .rename(columns={
            "product_name": "Produit", "category_name": "Catégorie",
            "revenue": "Revenue (€)", "margin": "Marge (€)",
            "margin_pct": "Marge %", "units": "Unités"
        }),
        width='stretch', hide_index=True,
    )

    # Heatmap
    heatmap = monthly_heatmap_data(oi)
    fig = px.imshow(heatmap.values, x=heatmap.columns.tolist(), y=heatmap.index.tolist(),
                    color_continuous_scale="Blues", aspect="auto",
                    title="Heatmap — Revenue Catégorie × Mois")
    st.plotly_chart(_base_layout(fig, ""), use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    import io
    buffer = io.BytesIO()
    if 'rfm_clust' in locals():
        rfm_clust.to_csv(buffer, index=False)
        buffer.seek(0)
        buffer.name = "segments_rfm.csv"
        st.download_button("Exporter Segments (CSV)", data=buffer, file_name="segments_rfm.csv", mime="text/csv")
    else:
        st.button("Exporter Segments (CSV)", disabled=True)
