"""
Athena Core — Page 3: Modèles Stratégiques
"""
import streamlit as st
import pandas as pd
from utils.styles import inject_css
from utils.helpers import page_header
from utils.charts import bcg_chart, mckinsey_chart, radar_chart, _base_layout
from core.data_loader import load_order_items, load_orders, load_market_data, load_strategic_inputs
from strategy.bcg_matrix import compute_bcg, bcg_summary
from strategy.mckinsey_matrix import compute_mckinsey
from strategy.swot_analysis import compute_swot_from_data, load_manual_swot, merge_swot
from strategy.pestel_analysis import load_pestel, pestel_radar_data
from strategy.porter_forces import load_porter, porter_radar_data, porter_threat_level

st.set_page_config(page_title="Modèles Stratégiques — Athena Core", layout="wide")
inject_css()
page_header("Modèles Stratégiques", "Matrices BCG, McKinsey, SWOT, PESTEL et Porter data-driven")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["BCG", "McKinsey", "SWOT", "PESTEL", "Porter"])

oi = load_order_items()
orders = load_orders()
market = load_market_data()
strat_inputs = load_strategic_inputs()

# -------------------------------------------------------------------
# TAB 1 — BCG
# -------------------------------------------------------------------
with tab1:
    st.subheader("Matrice BCG — Croissance vs Part de Marché")
    st.caption("Classification automatique basée sur les médianes dynamiques du dataset")

    bcg = compute_bcg(oi, market)
    st.plotly_chart(bcg_chart(bcg), use_container_width=True)

    # Summary cards
    summary = bcg_summary(bcg)
    cols = st.columns(4)
    for i, (_, row) in enumerate(summary.iterrows()):
        with cols[i % 4]:
            st.metric(row["quadrant"],
                      f"{int(row['count'])} produits",
                      delta=f"{row['total_revenue']:,.0f}€")

    with st.expander("Détail par produit"):
        st.dataframe(bcg[["product_name", "category_name", "revenue", "relative_market_share",
                          "market_growth_rate", "quadrant"]]
                     .rename(columns={"product_name": "Produit", "category_name": "Catégorie",
                                      "revenue": "Revenue", "relative_market_share": "Part Marché",
                                      "market_growth_rate": "Croissance", "quadrant": "Quadrant"}),
                     width="stretch", hide_index=True)

# -------------------------------------------------------------------
# TAB 2 — McKINSEY
# -------------------------------------------------------------------
with tab2:
    st.subheader("Matrice McKinsey / GE — Attractivité vs Position")
    mck = compute_mckinsey(oi, market)
    st.plotly_chart(mckinsey_chart(mck), use_container_width=True)

    # Strategy summary
    strat_summary = mck.groupby("strategy").agg(
        count=("product_id", "count"), revenue=("revenue", "sum")
    ).reset_index()
    cols = st.columns(3)
    for i, (_, row) in enumerate(strat_summary.iterrows()):
        with cols[i % 3]:
            st.metric(row["strategy"], f"{int(row['count'])} produits",
                      delta=f"{row['revenue']:,.0f}€")

# -------------------------------------------------------------------
# TAB 3 — SWOT
# -------------------------------------------------------------------
with tab3:
    st.subheader("Analyse SWOT — Forces, Faiblesses, Opportunités, Menaces")

    auto_swot = compute_swot_from_data(oi, orders, market)
    manual_swot = load_manual_swot(strat_inputs)
    swot = merge_swot(auto_swot, manual_swot)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="swot-card swot-force">', unsafe_allow_html=True)
        st.markdown("#### Forces")
        for _, r in swot[swot["category"] == "Force"].iterrows():
            st.markdown(f"- **[{r['score']:.0f}/10]** {r['description']}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="swot-card swot-opportunite">', unsafe_allow_html=True)
        st.markdown("#### Opportunités")
        for _, r in swot[swot["category"] == "Opportunité"].iterrows():
            st.markdown(f"- **[{r['score']:.0f}/10]** {r['description']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="swot-card swot-faiblesse">', unsafe_allow_html=True)
        st.markdown("#### Faiblesses")
        for _, r in swot[swot["category"] == "Faiblesse"].iterrows():
            st.markdown(f"- **[{r['score']:.0f}/10]** {r['description']}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="swot-card swot-menace">', unsafe_allow_html=True)
        st.markdown("#### Menaces")
        for _, r in swot[swot["category"] == "Menace"].iterrows():
            st.markdown(f"- **[{r['score']:.0f}/10]** {r['description']}")
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# TAB 4 — PESTEL
# -------------------------------------------------------------------
with tab4:
    st.subheader("Analyse PESTEL — Facteurs Externes")
    pestel = load_pestel(strat_inputs)
    pestel_radar = pestel_radar_data(pestel)

    st.plotly_chart(
        radar_chart(pestel_radar["category"].tolist(),
                    pestel_radar["avg_score"].abs().tolist(),
                    "Radar PESTEL — Score Moyen par Dimension"),
        width="stretch")

    st.markdown("#### Détail des Facteurs")
    for cat in pestel_radar["category"].tolist():
        items = pestel[pestel["category"] == cat]
        if len(items) > 0:
            with st.expander(f"**{cat}** ({len(items)} facteurs)"):
                for _, r in items.iterrows():
                    icon = "?" if r["score"] > 0 else "?"
                    st.markdown(f"{icon} {r['description']} — Score: **{r['score']}** | "
                                f"Probabilité: **{r['impact']}%** | "
                                f"Pondéré: **{r['weighted_score']:.1f}**")

# -------------------------------------------------------------------
# TAB 5 — PORTER
# -------------------------------------------------------------------
with tab5:
    st.subheader("5 Forces de Porter — Analyse Concurrentielle")
    porter = load_porter(strat_inputs)
    porter_radar = porter_radar_data(porter)

    st.plotly_chart(
        radar_chart(porter_radar["category"].tolist(),
                    porter_radar["score"].tolist(),
                    "Pentagon de Porter — Intensité des Forces"),
        width="stretch")

    st.markdown("#### Détail des Forces")
    for _, row in porter.iterrows():
        level = porter_threat_level(row["score"])
        st.markdown(f"**{row['category']}** — {level} ({row['score']}/5)")
        st.caption(row["description"])

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("Actualiser les Modèles"):
        st.cache_data.clear()
        st.rerun()
