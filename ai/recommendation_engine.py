"""
Athena Core — Recommendation Engine
"""
import pandas as pd


def generate_recommendations(bcg_df, rfm_df, anomaly_alerts, prod_perf_df):
    recs = []

    # 1. BCG-based recommendations
    if bcg_df is not None and len(bcg_df) > 0:
        stars = bcg_df[bcg_df["quadrant"] == "Star"]
        for _, p in stars.head(3).iterrows():
            recs.append({
                "priority": "HIGH", "icon": "!", "action": "INVESTIR",
                "target": p["product_name"],
                "reason": f"Star BCG — Croissance {p['market_growth_rate']:.0%}, Part marché {p['relative_market_share']:.1f}x",
                "category": "Croissance",
            })
        dogs = bcg_df[bcg_df["quadrant"] == "Dog"]
        for _, p in dogs.head(2).iterrows():
            recs.append({
                "priority": "MEDIUM", "icon": "-", "action": "RÉDUIRE COÛTS",
                "target": p["product_name"],
                "reason": f"Dog BCG — Faible croissance et faible part de marché",
                "category": "Optimisation",
            })
        questions = bcg_df[bcg_df["quadrant"] == "Question Mark"]
        for _, p in questions.head(2).iterrows():
            recs.append({
                "priority": "MEDIUM", "icon": "?", "action": "ANALYSER",
                "target": p["product_name"],
                "reason": f"Question Mark — Fort potentiel mais position faible",
                "category": "Stratégie",
            })

    # 2. RFM-based recommendations
    if rfm_df is not None and "segment_label" in rfm_df.columns:
        at_risk = rfm_df[rfm_df["segment_label"] == "À Risque"]
        if len(at_risk) > 0:
            recs.append({
                "priority": "HIGH", "icon": "!", "action": "FIDÉLISER",
                "target": f"{len(at_risk)} clients à risque",
                "reason": f"Segment RFM 'À Risque' — Lancer campagne de rétention",
                "category": "Clients",
            })
        lost = rfm_df[rfm_df["segment_label"] == "Perdus"]
        if len(lost) > 0:
            recs.append({
                "priority": "LOW", "icon": "@", "action": "RÉACTIVER",
                "target": f"{len(lost)} clients perdus",
                "reason": "Clients inactifs — Offre de réactivation ciblée",
                "category": "Clients",
            })

    # 3. Anomaly-based recommendations
    for alert in (anomaly_alerts or []):
        if alert.get("type") == "spike_negatif":
            recs.append({
                "priority": "HIGH", "icon": "!", "action": "LANCER PROMOTION",
                "target": "Ventes globales",
                "reason": alert["message"],
                "category": "Urgence",
            })

    # 4. Performance-based recommendations
    if prod_perf_df is not None and len(prod_perf_df) > 0 and "margin_pct" in prod_perf_df.columns:
        low_margin = prod_perf_df[prod_perf_df["margin_pct"] < 20]
        for _, p in low_margin.head(2).iterrows():
            recs.append({
                "priority": "MEDIUM", "icon": "€", "action": "RENÉGOCIER",
                "target": p["product_name"],
                "reason": f"Marge faible ({p['margin_pct']:.1f}%) — Renégocier fournisseur ou augmenter prix",
                "category": "Optimisation",
            })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recs.sort(key=lambda x: priority_order.get(x["priority"], 3))
    return recs
