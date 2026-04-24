"""
Athena Core — Page 4: Intelligence Artificielle
"""
import streamlit as st
import pandas as pd
from utils.styles import inject_css
from utils.helpers import page_header
from utils.charts import anomaly_chart, forecast_chart, bar_chart, _base_layout
from core.data_loader import load_order_items, load_orders, load_daily_revenue, load_market_data
from ai.sales_predictor import train_model, forecast_future
from ai.anomaly_detector import detect_revenue_anomalies, detect_product_anomalies, get_anomaly_alerts
from ai.recommendation_engine import generate_recommendations
from analytics.segmentation import compute_rfm, rfm_scoring, kmeans_segmentation
from analytics.performance import performance_by_product
from strategy.bcg_matrix import compute_bcg

st.set_page_config(page_title="Intelligence IA — Athena Core", layout="wide")
inject_css()
page_header("Intelligence Artificielle", "Prédictions, détection d'anomalies et recommandations automatiques")

tab1, tab2, tab3 = st.tabs(["Prédictions", "Anomalies", "Recommandations"])

daily = load_daily_revenue()
oi = load_order_items()
orders = load_orders()

# -------------------------------------------------------------------
# TAB 1 — PREDICTIONS
# -------------------------------------------------------------------
with tab1:
    st.subheader("Prédiction des Ventes — Machine Learning")

    with st.spinner("Entraînement du modèle RandomForest..."):
        model, feature_cols, metrics = train_model(daily)
        forecast = forecast_future(model, daily, feature_cols, days=30)

    # Model metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("MAE (Erreur Absolue Moyenne)", f"{metrics['mae']:,.0f}€")
    with col2:
        st.metric("RMSE", f"{metrics['rmse']:,.0f}€")
    with col3:
        total_forecast = forecast["predicted_revenue"].sum()
        st.metric("CA Prévu (30j)", f"{total_forecast:,.0f}€")

    # Forecast chart
    st.plotly_chart(forecast_chart(daily, forecast, metrics), use_container_width=True)

    # Feature importance
    with st.expander("Importance des Features"):
        imp = metrics["importance"].head(10)
        fig = bar_chart(imp, y="feature", x="importance",
                        title="Top 10 Features", orientation="h")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    # Forecast table
    with st.expander("Tableau des Prévisions (30 jours)"):
        st.dataframe(forecast.rename(columns={
            "date": "Date", "predicted_revenue": "CA Prévu (€)"
        }), use_container_width=True, hide_index=True)

# -------------------------------------------------------------------
# TAB 2 — ANOMALIES
# -------------------------------------------------------------------
with tab2:
    st.subheader("Détection d'Anomalies — IsolationForest")

    with st.spinner("Analyse des anomalies..."):
        rev_anomalies = detect_revenue_anomalies(daily)
        prod_anomalies = detect_product_anomalies(oi)

    num_anomalies = rev_anomalies["is_anomaly"].sum()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Anomalies Revenue", f"{num_anomalies} jours")
    with col2:
        pos = len(rev_anomalies[rev_anomalies["anomaly_type"] == "spike_positif"])
        st.metric("Pics Positifs", pos)
    with col3:
        neg = len(rev_anomalies[rev_anomalies["anomaly_type"] == "spike_negatif"])
        st.metric("Pics Négatifs", neg)

    st.plotly_chart(anomaly_chart(rev_anomalies), use_container_width=True)

    # Product anomalies
    if len(prod_anomalies) > 0:
        st.markdown("#### Anomalies Produits (dernier mois)")
        st.dataframe(prod_anomalies.rename(columns={
            "product": "Produit", "month": "Mois", "revenue": "Revenue",
            "avg_revenue": "Moy. Revenue", "z_score": "Z-Score", "type": "Type"
        }), use_container_width=True, hide_index=True)

    # Alert list
    alerts = get_anomaly_alerts(rev_anomalies, prod_anomalies)
    if alerts:
        st.markdown("#### Alertes Récentes")
        for a in alerts:
            st.warning(f"{a['icon']} {a['message']}")

# -------------------------------------------------------------------
# TAB 3 — RECOMMANDATIONS
# -------------------------------------------------------------------
with tab3:
    st.subheader("Recommandations Automatiques")
    st.caption("Générées à partir de l'analyse BCG, RFM, anomalies et performance")

    with st.spinner("Génération des recommandations..."):
        market = load_market_data()
        bcg = compute_bcg(oi, market)
        rfm = compute_rfm(orders)
        rfm_scored = rfm_scoring(rfm)
        rfm_clust, _, _ = kmeans_segmentation(rfm_scored)
        prod_perf = performance_by_product(oi)
        rev_anom = detect_revenue_anomalies(daily)
        prod_anom = detect_product_anomalies(oi)
        alerts = get_anomaly_alerts(rev_anom, prod_anom)
        recs = generate_recommendations(bcg, rfm_clust, alerts, prod_perf)

    if not recs:
        st.info("Aucune recommandation urgente — tout semble nominal.")
    else:
        # Summary
        high = sum(1 for r in recs if r["priority"] == "HIGH")
        med = sum(1 for r in recs if r["priority"] == "MEDIUM")
        low = sum(1 for r in recs if r["priority"] == "LOW")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Priorité Haute", high)
        with col2:
            st.metric("Priorité Moyenne", med)
        with col3:
            st.metric("Priorité Basse", low)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        # Render recommendation cards
        for rec in recs:
            css_class = {"HIGH": "rec-high", "MEDIUM": "rec-medium", "LOW": "rec-low"}
            priority_label = {"HIGH": "HAUTE", "MEDIUM": "MOYENNE", "LOW": "BASSE"}
            
            col_rec, col_act = st.columns([4, 1])
            with col_rec:
                st.markdown(f"""
                <div class="rec-card {css_class.get(rec['priority'], '')}">
                    <strong>[{rec['icon']}] {rec['action']}</strong> — {rec['target']}<br>
                    <span style="color: #94A3B8; font-size: 0.9rem;">{rec['reason']}</span><br>
                    <span style="font-size: 0.75rem; font-weight: bold;">Priorité: {priority_label.get(rec['priority'], '')}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_act:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Appliquer", key=f"apply_{rec['target']}"):
                    st.toast(f"Action '{rec['action']}' programmée pour {rec['target']}.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
if st.button("Relancer l'Analyse IA", type="primary"):
    st.cache_data.clear()
    st.rerun()
