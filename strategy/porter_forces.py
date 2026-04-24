"""
Athena Core — Porter's 5 Forces Analysis
"""
import pandas as pd

PORTER_FORCES = [
    "Pouvoir Fournisseurs", "Pouvoir Clients",
    "Menace Nouveaux Entrants", "Menace Substituts",
    "Rivalité Concurrentielle",
]


def load_porter(strategic_inputs_df):
    porter = strategic_inputs_df[strategic_inputs_df["type"] == "PORTER"].copy()
    return porter


def porter_radar_data(porter_df):
    radar = porter_df.groupby("category").agg(
        score=("score", "mean"),
        count=("id", "count"),
    ).reset_index()
    all_forces = pd.DataFrame({"category": PORTER_FORCES})
    radar = all_forces.merge(radar, on="category", how="left").fillna(0)
    return radar


def porter_threat_level(score):
    if score >= 4:
        return "🔴 Élevé"
    elif score >= 2.5:
        return "🟡 Moyen"
    else:
        return "🟢 Faible"
