"""
Athena Core — Page 6: Assistant IA (Chatbot)
"""
import streamlit as st
from utils.styles import inject_css
from utils.helpers import page_header
from ai.chatbot_engine import LocalChatbot
from core.data_loader import load_order_items, load_orders, load_daily_revenue, load_market_data
from analytics.kpis import compute_revenue
from strategy.bcg_matrix import compute_bcg
from ai.anomaly_detector import detect_revenue_anomalies, detect_product_anomalies, get_anomaly_alerts
from ai.recommendation_engine import generate_recommendations
from analytics.segmentation import compute_rfm, rfm_scoring, kmeans_segmentation
from analytics.performance import performance_by_product

st.set_page_config(page_title="Assistant IA — Athena Core", layout="wide")
inject_css()
page_header("Assistant IA Décisionnel", "Posez vos questions sur la stratégie, les anomalies ou les recommandations")

# Initialize chatbot in session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = LocalChatbot()
    
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis l'assistant IA local de votre plateforme. Demandez-moi quelles sont les recommandations urgentes, s'il y a des anomalies, ou quel est l'état de notre matrice BCG."}
    ]

# Load Context (Cached automatically by data_loader)
@st.cache_data(ttl=3600)
def load_chatbot_context():
    oi = load_order_items()
    orders = load_orders()
    daily = load_daily_revenue()
    market = load_market_data()
    
    rev = compute_revenue(oi)
    bcg = compute_bcg(oi, market)
    
    rfm = compute_rfm(orders)
    rfm_scored = rfm_scoring(rfm)
    rfm_clust, _, _ = kmeans_segmentation(rfm_scored)
    prod_perf = performance_by_product(oi)
    rev_anom = detect_revenue_anomalies(daily)
    prod_anom = detect_product_anomalies(oi)
    alerts = get_anomaly_alerts(rev_anom, prod_anom)
    recs = generate_recommendations(bcg, rfm_clust, alerts, prod_perf)
    
    return {
        "rev": rev,
        "bcg": bcg,
        "alerts": alerts,
        "recs": recs
    }

context = load_chatbot_context()

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Que voulez-vous savoir sur votre stratégie ?"):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate bot response
    with st.chat_message("assistant"):
        with st.spinner("Analyse de la demande..."):
            bot = st.session_state.chatbot
            response = bot.get_response(prompt, context)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
