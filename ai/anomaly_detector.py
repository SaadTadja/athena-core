"""
Athena Core — Anomaly Detection
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_revenue_anomalies(daily_df, contamination=0.05):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").reset_index(drop=True)

    if df.empty or len(df) < 2:
        df["anomaly"] = 1
        df["anomaly_score"] = 0.0
        df["is_anomaly"] = False
        df["anomaly_type"] = "normal"
        return df

    features = df[["revenue", "num_orders", "units_sold"]].values
    iso = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
    df["anomaly"] = iso.fit_predict(features)
    df["anomaly_score"] = iso.decision_function(features)
    df["is_anomaly"] = df["anomaly"] == -1

    # Classify anomaly type
    rolling_mean = df["revenue"].rolling(window=30, min_periods=1).mean()
    df["anomaly_type"] = "normal"
    df.loc[df["is_anomaly"] & (df["revenue"] > rolling_mean), "anomaly_type"] = "spike_positif"
    df.loc[df["is_anomaly"] & (df["revenue"] <= rolling_mean), "anomaly_type"] = "spike_negatif"

    return df


def detect_product_anomalies(order_items_df):
    df = order_items_df.copy()
    df["line_revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount"])
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.strftime("%Y-%m")

    monthly = df.groupby(["product_name", "month"]).agg(
        revenue=("line_revenue", "sum"), units=("quantity", "sum")
    ).reset_index()

    anomalies = []
    for prod in monthly["product_name"].unique():
        prod_data = monthly[monthly["product_name"] == prod].sort_values("month")
        if len(prod_data) < 3:
            continue
        mean_rev = prod_data["revenue"].mean()
        std_rev = prod_data["revenue"].std()
        if std_rev == 0:
            continue
        last = prod_data.iloc[-1]
        z_score = (last["revenue"] - mean_rev) / std_rev
        if abs(z_score) > 2:
            anomalies.append({
                "product": prod,
                "month": last["month"],
                "revenue": last["revenue"],
                "avg_revenue": round(mean_rev, 2),
                "z_score": round(z_score, 2),
                "type": "📈 Pic" if z_score > 0 else "📉 Chute",
            })

    return pd.DataFrame(anomalies) if anomalies else pd.DataFrame(
        columns=["product", "month", "revenue", "avg_revenue", "z_score", "type"]
    )


def get_anomaly_alerts(rev_anomalies_df, prod_anomalies_df):
    alerts = []
    recent = rev_anomalies_df[rev_anomalies_df["is_anomaly"]].tail(5)
    for _, r in recent.iterrows():
        icon = "🔺" if r["anomaly_type"] == "spike_positif" else "🔻"
        alerts.append({
            "icon": icon,
            "message": f"Anomalie détectée le {r['order_date'].strftime('%Y-%m-%d') if hasattr(r['order_date'], 'strftime') else r['order_date']}: CA = {r['revenue']:.0f}€",
            "type": r["anomaly_type"],
        })
    for _, r in prod_anomalies_df.head(5).iterrows():
        alerts.append({
            "icon": "⚠️",
            "message": f"{r['type']} sur {r['product']}: {r['revenue']:.0f}€ vs moy {r['avg_revenue']:.0f}€",
            "type": "product",
        })
    return alerts
