"""
Athena Core — KPI Calculations (Niveau 1)
"""
import pandas as pd
import numpy as np


def compute_revenue(order_items_df):
    """Total revenue from order items."""
    return (order_items_df["quantity"] * order_items_df["unit_price"] * (1 - order_items_df["discount"])).sum()


def compute_total_orders(orders_df):
    """Total number of distinct orders."""
    return orders_df["id"].nunique()


def compute_avg_basket(orders_df):
    """Average order value."""
    return orders_df["total_amount"].mean()


def compute_gross_margin(order_items_df):
    """Gross margin percentage."""
    revenue = (order_items_df["quantity"] * order_items_df["unit_price"] * (1 - order_items_df["discount"])).sum()
    cost = (order_items_df["quantity"] * order_items_df["cost"]).sum()
    if revenue == 0:
        return 0
    return ((revenue - cost) / revenue) * 100


def compute_top_products(order_items_df, top_n=10):
    """Top N products by revenue."""
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    top = (
        df.groupby(["product_id", "product_name"])
        .agg(revenue=("line_revenue", "sum"), units=("quantity", "sum"))
        .reset_index()
        .sort_values("revenue", ascending=False)
        .head(top_n)
    )
    return top


def compute_top_categories(order_items_df):
    """Revenue by category."""
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    return (
        df.groupby("category_name")
        .agg(revenue=("line_revenue", "sum"), units=("quantity", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def compute_growth_rate(daily_revenue_df, period="ME"):
    """Growth rate by period (M=monthly, Q=quarterly)."""
    df = daily_revenue_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.set_index("order_date").resample(period)["revenue"].sum().reset_index()
    df["growth_rate"] = df["revenue"].pct_change() * 100
    return df


def compute_monthly_revenue(daily_revenue_df):
    """Monthly revenue aggregation."""
    df = daily_revenue_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.strftime("%Y-%m")
    monthly = df.groupby("month").agg(
        revenue=("revenue", "sum"),
        orders=("num_orders", "sum"),
        units=("units_sold", "sum"),
    ).reset_index()
    return monthly


def compute_channel_breakdown(order_items_df):
    """Revenue breakdown by sales channel."""
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    return (
        df.groupby("channel")
        .agg(revenue=("line_revenue", "sum"), orders=("order_id", "nunique"))
        .reset_index()
        .sort_values("revenue", ascending=False)
    )


def compute_period_comparison(order_items_df, days=30):
    """Compare current period vs previous period."""
    df = order_items_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    max_date = df["order_date"].max()
    current_start = max_date - pd.Timedelta(days=days)
    prev_start = current_start - pd.Timedelta(days=days)

    current = df[df["order_date"] > current_start]
    previous = df[(df["order_date"] > prev_start) & (df["order_date"] <= current_start)]

    current_rev = (current["quantity"] * current["unit_price"] * (1 - current["discount"])).sum()
    prev_rev = (previous["quantity"] * previous["unit_price"] * (1 - previous["discount"])).sum()

    current_orders = current["order_id"].nunique()
    prev_orders = previous["order_id"].nunique()

    return {
        "current_revenue": current_rev,
        "previous_revenue": prev_rev,
        "revenue_delta": ((current_rev - prev_rev) / prev_rev * 100) if prev_rev > 0 else 0,
        "current_orders": current_orders,
        "previous_orders": prev_orders,
        "orders_delta": ((current_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0,
    }
