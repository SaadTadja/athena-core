"""
Athena Core — BCG Matrix (Data-Driven)
"""
import pandas as pd
import numpy as np


def compute_bcg(order_items_df, market_data_df):
    oi = order_items_df.copy()
    oi["line_revenue"] = oi["quantity"] * oi["unit_price"] * (1 - oi["discount"])

    product_revenue = oi.groupby(["product_id", "product_name", "category_name"]).agg(
        revenue=("line_revenue", "sum")
    ).reset_index()

    md = market_data_df[["product_id", "market_growth_rate", "relative_market_share"]].copy()
    bcg = product_revenue.merge(md, on="product_id", how="left")
    bcg = bcg.dropna(subset=["market_growth_rate", "relative_market_share"])

    median_share = bcg["relative_market_share"].median()
    median_growth = bcg["market_growth_rate"].median()

    conditions = [
        (bcg["relative_market_share"] >= median_share) & (bcg["market_growth_rate"] >= median_growth),
        (bcg["relative_market_share"] >= median_share) & (bcg["market_growth_rate"] < median_growth),
        (bcg["relative_market_share"] < median_share) & (bcg["market_growth_rate"] >= median_growth),
        (bcg["relative_market_share"] < median_share) & (bcg["market_growth_rate"] < median_growth),
    ]
    labels = ["Star", "Cash Cow", "Question Mark", "Dog"]
    bcg["quadrant"] = np.select(conditions, labels, default="Unknown")
    bcg["median_share"] = median_share
    bcg["median_growth"] = median_growth
    return bcg


def bcg_summary(bcg_df):
    summary = bcg_df.groupby("quadrant").agg(
        count=("product_id", "count"),
        total_revenue=("revenue", "sum"),
        avg_growth=("market_growth_rate", "mean"),
        avg_share=("relative_market_share", "mean"),
    ).reset_index()
    return summary
