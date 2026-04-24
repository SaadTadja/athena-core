"""
Athena Core  Page 5: Rapport Final Exécutif
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from utils.styles import inject_css
from utils.helpers import page_header, format_currency
from core.data_loader import load_order_items, load_orders, load_daily_revenue, load_market_data
from analytics.kpis import compute_revenue, compute_gross_margin
from analytics.trends import detect_trend_direction
from strategy.bcg_matrix import compute_bcg, bcg_summary
from ai.anomaly_detector import detect_revenue_anomalies, detect_product_anomalies, get_anomaly_alerts
from ai.recommendation_engine import generate_recommendations
from analytics.segmentation import compute_rfm, rfm_scoring, kmeans_segmentation
from analytics.performance import performance_by_product

st.set_page_config(page_title="Rapport Final  Athena Core", layout="wide")
inject_css()

# Custom CSS specifically for print layout
st.markdown("""
<style>
@media print {
    section[data-testid="stSidebar"] { display: none !important; }
    header { display: none !important; }
    footer { display: none !important; }
    .stApp { background: white !important; }
    .main-header, .metric-value, .stMarkdown p { color: black !important; }
    .metric-card, .rec-card { border: 1px solid #ccc !important; background: white !important; box-shadow: none !important; }
    .stButton { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

col_title, col_btn = st.columns([4, 1])
with col_title:
    page_header("Rapport Exécutif Stratégique", f"Généré automatiquement le {datetime.now().strftime('%d %B %Y')}")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ð¨ï¸ Imprimer / Sauvegarder en PDF", type="primary"):
        st.markdown("<script>window.print()</script>", unsafe_allow_html=True)

st.markdown("---")

# 1. Chargement des données globales
oi = load_order_items()
orders = load_orders()
daily = load_daily_revenue()
market = load_market_data()

rev = compute_revenue(oi)
margin = compute_gross_margin(oi)
trend = detect_trend_direction(daily, window=90)

# 2. Executive Summary
st.markdown("### 1. Résumé Financier")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**Chiffre d'Affaires Global :**<br><span style='font-size:1.5rem; font-weight:bold; color:#1E3A8A;'>{format_currency(rev)}</span>", unsafe_allow_html=True)
with col2:
    st.markdown(f"**Marge Brute Moyenne :**<br><span style='font-size:1.5rem; font-weight:bold; color:#1E3A8A;'>{margin:.1f}%</span>", unsafe_allow_html=True)
with col3:
    direction_map = {"up": "En hausse", "down": "En baisse", "neutral": "Stable"}
    st.markdown(f"**Tendance (90 jours) :**<br><span style='font-size:1.5rem; font-weight:bold; color:#1E3A8A;'>{direction_map.get(trend['direction'], 'Inconnue')}</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Stratégie Produit (BCG)
st.markdown("### 2. Diagnostic du Portefeuille Produits")
try:
    bcg = compute_bcg(oi, market)
    summary = bcg_summary(bcg)
    stars = summary[summary["quadrant"] == "Star"]["count"].sum() if "Star" in summary["quadrant"].values else 0
    dogs = summary[summary["quadrant"] == "Dog"]["count"].sum() if "Dog" in summary["quadrant"].values else 0
    st.markdown(f"""
    L'analyse de la matrice BCG révèle que le portefeuille contient **{int(stars)} produit(s) Star** (fort potentiel de croissance et forte part de marché) 
    qui nécessitent des investissements soutenus pour maintenir leur position dominante. En revanche, **{int(dogs)} produit(s) Dog** ont été identifiés, nécessitant une révision stratégique urgente (optimisation des coûts ou retrait du marché).
    """)
except Exception as e:
    st.warning("Données insuffisantes pour l'analyse stratégique.")

st.markdown("<br>", unsafe_allow_html=True)

# 4. Plan d'Action IA
st.markdown("### 3. Plan d'Action Recommandé (Généré par l'IA)")
try:
    rfm = compute_rfm(orders)
    rfm_scored = rfm_scoring(rfm)
    rfm_clust, _, _ = kmeans_segmentation(rfm_scored)
    prod_perf = performance_by_product(oi)
    rev_anom = detect_revenue_anomalies(daily)
    prod_anom = detect_product_anomalies(oi)
    alerts = get_anomaly_alerts(rev_anom, prod_anom)
    recs = generate_recommendations(bcg, rfm_clust, alerts, prod_perf)
    
    high_priority = [r for r in recs if r["priority"] == "HIGH"]
    
    if high_priority:
        for rec in high_priority:
            st.markdown(f"""
            <div style="border-left: 4px solid #EF4444; padding-left: 15px; margin-bottom: 10px;">
                <strong>PRIORITÉ HAUTE : {rec['action']}</strong>  {rec['target']}<br>
                <em>Justification :</em> {rec['reason']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune recommandation critique immédiate. Le système est stable.")
        
except Exception as e:
    st.error("Erreur lors de la génération des recommandations.")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Export Markdown
st.markdown("### Exportation des Données Brutes")
markdown_report = f"""# Rapport Exécutif Athena Core
Généré le: {datetime.now().strftime('%Y-%m-%d')}

## Finance
- CA: {rev:,.0f} 
- Marge: {margin:.1f}%

## Actions Requises:
"""
for r in (high_priority if 'high_priority' in locals() else []):
    markdown_report += f"- [{r['action']}] {r['target']} : {r['reason']}\n"

import io
buffer = io.BytesIO(markdown_report.encode('utf-8'))
buffer.name = "rapport_executif.txt"

st.download_button(
    label="Télécharger le rapport brut (TXT/Markdown)",
    data=buffer,
    file_name="rapport_executif.txt",
    mime="text/plain"
)

st.caption("Athena Core  Plateforme d'Intelligence Décisionnelle Confidentielle.")
