"""
Athena Core — Customer Segmentation (RFM + KMeans)
"""
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def compute_rfm(orders_df):
    df = orders_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    max_date = df["order_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (max_date - x.max()).days),
        frequency=("id", "nunique"),
        monetary=("total_amount", "sum"),
    ).reset_index()
    return rfm


def rfm_scoring(rfm_df):
    df = rfm_df.copy()
    if df.empty:
        df["r_score"], df["f_score"], df["m_score"], df["rfm_score"] = 0, 0, 0, 0
        return df
    df["r_score"] = pd.qcut(df["recency"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]
    return df


def kmeans_segmentation(rfm_df, n_clusters=4):
    df = rfm_df.copy()
    features = df[["recency", "frequency", "monetary"]].values
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(scaled)

    # Label clusters based on characteristics
    cluster_stats = df.groupby("cluster").agg(
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        count=("customer_id", "count"),
    ).reset_index()

    # Sort by monetary desc to assign labels
    cluster_stats = cluster_stats.sort_values("avg_monetary", ascending=False)
    labels = ["Champions", "Loyaux", "À Risque", "Perdus"]
    label_map = dict(zip(cluster_stats["cluster"].values, labels[:len(cluster_stats)]))
    df["segment_label"] = df["cluster"].map(label_map)

    return df, cluster_stats, label_map
