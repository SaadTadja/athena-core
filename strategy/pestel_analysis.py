"""
Athena Core — PESTEL Analysis
"""
import pandas as pd


PESTEL_CATEGORIES = ["Politique", "Économique", "Socioculturel", "Technologique", "Environnemental", "Légal"]


def load_pestel(strategic_inputs_df):
    pestel = strategic_inputs_df[strategic_inputs_df["type"] == "PESTEL"].copy()
    pestel["weighted_score"] = pestel["score"] * (pestel["impact"] / 100)
    return pestel


def pestel_radar_data(pestel_df):
    """Aggregate scores by PESTEL dimension for radar chart."""
    radar = pestel_df.groupby("category").agg(
        avg_score=("score", "mean"),
        avg_weighted=("weighted_score", "mean"),
        count=("id", "count"),
    ).reset_index()
    # Ensure all 6 categories are present
    all_cats = pd.DataFrame({"category": PESTEL_CATEGORIES})
    radar = all_cats.merge(radar, on="category", how="left").fillna(0)
    return radar
