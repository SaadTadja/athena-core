"""
Athena Core — SWOT Analysis (Data-Driven)
"""
import pandas as pd


def compute_swot_from_data(order_items_df, orders_df, market_data_df):
    """Auto-generate SWOT items from actual data."""
    auto_swot = []
    oi = order_items_df.copy()
    oi["line_revenue"] = oi["quantity"] * oi["unit_price"] * (1 - oi["discount"])
    oi["line_margin"] = oi["line_revenue"] - (oi["quantity"] * oi["cost"])

    # FORCES — high-margin categories
    cat_margin = oi.groupby("category_name").agg(
        margin_pct=("line_margin", lambda x: (x.sum() / oi.loc[x.index, "line_revenue"].sum()) * 100)
    ).reset_index()
    avg_margin = cat_margin["margin_pct"].mean()
    for _, r in cat_margin[cat_margin["margin_pct"] > avg_margin].iterrows():
        auto_swot.append({
            "category": "Force",
            "description": f"Marge élevée: {r['category_name']} ({r['margin_pct']:.1f}%)",
            "score": min(round(r["margin_pct"] / 10, 1), 10),
        })

    # FAIBLESSES — low performing products
    prod_perf = oi.groupby("product_name").agg(revenue=("line_revenue", "sum")).reset_index()
    bottom = prod_perf.nsmallest(3, "revenue")
    for _, r in bottom.iterrows():
        auto_swot.append({
            "category": "Faiblesse",
            "description": f"Produit sous-performant: {r['product_name']} ({r['revenue']:.0f}€)",
            "score": 5,
        })

    # OPPORTUNITES — growing market segments
    md = market_data_df.copy()
    growing = md[md["market_growth_rate"] > 0.15]
    if len(growing) > 0:
        auto_swot.append({
            "category": "Opportunité",
            "description": f"{len(growing)} produits dans des marchés en forte croissance (>15%)",
            "score": 8,
        })

    # MENACES — declining products
    declining = md[md["market_growth_rate"] < -0.05]
    if len(declining) > 0:
        auto_swot.append({
            "category": "Menace",
            "description": f"{len(declining)} produits dans des marchés en déclin",
            "score": 7,
        })

    return pd.DataFrame(auto_swot)


def load_manual_swot(strategic_inputs_df):
    """Load manually entered SWOT items."""
    swot = strategic_inputs_df[strategic_inputs_df["type"] == "SWOT"].copy()
    return swot[["category", "description", "score"]]


def merge_swot(auto_df, manual_df):
    """Combine auto-generated and manual SWOT items."""
    return pd.concat([auto_df, manual_df], ignore_index=True)
