"""
Athena Core — Page 1: KPIs Classiques
"""
import streamlit as st
import pandas as pd
from utils.styles import inject_css
from utils.helpers import page_header, render_metric_card, format_currency, format_number
from utils.charts import line_chart, bar_chart, pie_chart
from core.data_loader import load_order_items, load_orders, load_daily_revenue
from analytics.kpis import (
    compute_revenue, compute_total_orders, compute_avg_basket,
    compute_gross_margin, compute_top_products, compute_top_categories,
    compute_growth_rate, compute_monthly_revenue, compute_channel_breakdown,
    compute_period_comparison,
)

st.set_page_config(page_title="KPIs — Athena Core", layout="wide")
inject_css()
page_header("KPIs Classiques", "Vue d'ensemble des indicateurs clés de performance")

# Load data
order_items = load_order_items()
orders = load_orders()
daily_rev = load_daily_revenue()

# ─── Period filter ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filtres")
    period_days = st.selectbox("Période", [30, 60, 90, 180, 365, 730],
                               format_func=lambda x: f"Derniers {x} jours", index=4)

oi = order_items.copy()
oi["order_date"] = pd.to_datetime(oi["order_date"])
max_date = oi["order_date"].max()
oi = oi[oi["order_date"] >= max_date - pd.Timedelta(days=period_days)]
orders_f = orders.copy()
orders_f["order_date"] = pd.to_datetime(orders_f["order_date"])
orders_f = orders_f[orders_f["order_date"] >= max_date - pd.Timedelta(days=period_days)]

# ─── Main KPIs ───────────────────────────────────────────────────
comparison = compute_period_comparison(order_items, days=period_days)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Chiffre d'Affaires", format_currency(comparison["current_revenue"]),
                       delta=comparison["revenue_delta"])
with col2:
    render_metric_card("Commandes", format_number(comparison["current_orders"]),
                       delta=comparison["orders_delta"])
with col3:
    avg = compute_avg_basket(orders_f)
    render_metric_card("Panier Moyen", f"{avg:.0f}€")
with col4:
    margin = compute_gross_margin(oi)
    render_metric_card("Marge Brute", f"{margin:.1f}", suffix="%")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ─── Revenue chart ───────────────────────────────────────────────
monthly = compute_monthly_revenue(daily_rev)
st.plotly_chart(line_chart(monthly, "month", "revenue", "Évolution du Chiffre d'Affaires Mensuel"),
                width='stretch')

# ─── Top Products & Categories ───────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    top_prods = compute_top_products(oi, top_n=10)
    fig = bar_chart(top_prods, y="product_name", x="revenue", title="Top 10 Produits",
                    orientation="h")
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    top_cats = compute_top_categories(oi)
    st.plotly_chart(pie_chart(top_cats, "category_name", "revenue", "Répartition par Catégorie"),
                    width='stretch')

# ─── Growth & Channels ──────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    growth = compute_growth_rate(daily_rev, period="ME")
    fig = bar_chart(growth.dropna(), "order_date", "growth_rate", "Croissance Mensuelle (%)")
    fig.update_traces(marker_color=[
        "#00E676" if v >= 0 else "#FF5252" for v in growth.dropna()["growth_rate"]
    ])
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    channels = compute_channel_breakdown(oi)
    st.plotly_chart(pie_chart(channels, "channel", "revenue", "Répartition par Canal"),
                    width='stretch')

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
with col_btn1:
    import io
    buffer = io.BytesIO()
    top_prods.to_csv(buffer, index=False)
    buffer.seek(0)
    buffer.name = "top_produits.csv"
    
    st.download_button(
        label="Télécharger Top Produits",
        data=buffer,
        file_name='top_produits.csv',
        mime='text/csv',
        type="primary"
    )
with col_btn2:
    if st.button("Actualiser les données"):
        st.cache_data.clear()
        st.rerun()
