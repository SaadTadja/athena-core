"""
Athena Core — McKinsey / GE Matrix (Data-Driven)
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def compute_mckinsey(order_items_df, market_data_df):
    oi = order_items_df.copy()
    oi["line_revenue"] = oi["quantity"] * oi["unit_price"] * (1 - oi["discount"])
    oi["line_margin"] = oi["line_revenue"] - (oi["quantity"] * oi["cost"])

    prod_stats = oi.groupby(["product_id", "product_name", "category_name"]).agg(
        revenue=("line_revenue", "sum"),
        margin=("line_margin", "sum"),
        units=("quantity", "sum"),
    ).reset_index()
    prod_stats["margin_pct"] = (prod_stats["margin"] / prod_stats["revenue"] * 100)

    md = market_data_df[["product_id", "market_attractiveness", "competitive_position"]].copy()
    mckinsey = prod_stats.merge(md, on="product_id", how="left").dropna()

    if mckinsey.empty:
        mckinsey["attractiveness_score"] = pd.Series(dtype=float)
        mckinsey["position_score"] = pd.Series(dtype=float)
        mckinsey["strategy"] = pd.Series(dtype=str)
        return mckinsey

    scaler = MinMaxScaler(feature_range=(1, 9))
    mckinsey["attractiveness_score"] = scaler.fit_transform(mckinsey[["market_attractiveness"]])
    mckinsey["position_score"] = scaler.fit_transform(mckinsey[["competitive_position"]])

    def classify(row):
        a, p = row["attractiveness_score"], row["position_score"]
        if a >= 6 and p >= 6:
            return "Investir"
        elif a >= 6 and p < 6:
            return "Sélectif"
        elif a < 6 and p >= 6:
            return "Sélectif"
        elif a >= 3 and p >= 3:
            return "Sélectif"
        else:
            return "Récolter"

    mckinsey["strategy"] = mckinsey.apply(classify, axis=1)
    return mckinsey
