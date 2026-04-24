"""
Athena Core — Performance Analysis (Niveau 2)
"""
import pandas as pd
import numpy as np


def performance_by_category(order_items_df):
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    df["line_cost"] = df["quantity"] * df["cost"]
    df["line_margin"] = df["line_revenue"] - df["line_cost"]
    return df.groupby("category_name").agg(
        revenue=("line_revenue", "sum"),
        cost=("line_cost", "sum"),
        margin=("line_margin", "sum"),
        units=("quantity", "sum"),
        orders=("order_id", "nunique"),
    ).reset_index()


def performance_by_product(order_items_df, top_n=20):
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    df["line_cost"] = df["quantity"] * df["cost"]
    df["line_margin"] = df["line_revenue"] - df["line_cost"]
    result = df.groupby(["product_id", "product_name", "category_name"]).agg(
        revenue=("line_revenue", "sum"),
        margin=("line_margin", "sum"),
        units=("quantity", "sum"),
    ).reset_index()
    result["margin_pct"] = (result["margin"] / result["revenue"] * 100).round(1)
    return result.sort_values("revenue", ascending=False).head(top_n)


def monthly_heatmap_data(order_items_df):
    df = order_items_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.strftime("%Y-%m")
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    pivot = df.pivot_table(
        values="line_revenue", index="category_name",
        columns="month", aggfunc="sum", fill_value=0
    )
    return pivot


def yoy_comparison(order_items_df):
    df = order_items_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    yearly = df.groupby(["year", "month"]).agg(revenue=("line_revenue", "sum")).reset_index()
    return yearly
