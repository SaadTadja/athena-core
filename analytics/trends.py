"""
Athena Core — Trend Detection (Niveau 2)
"""
import pandas as pd
import numpy as np
from scipy import stats


def compute_moving_averages(daily_df, windows=[7, 30, 90]):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date")
    for w in windows:
        df[f"ma_{w}d"] = df["revenue"].rolling(window=w, min_periods=1).mean()
    return df


def detect_trend_direction(daily_df, window=90):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").tail(window)
    if len(df) < 10:
        return {"direction": "neutral", "slope": 0, "r_squared": 0, "change_pct": 0, "p_value": 1.0}
    x = np.arange(len(df))
    y = df["revenue"].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    predicted_start = intercept
    predicted_end = intercept + slope * len(x)
    change_pct = ((predicted_end - predicted_start) / predicted_start * 100) if predicted_start != 0 else 0
    if slope > 0 and p_value < 0.05:
        direction = "up"
    elif slope < 0 and p_value < 0.05:
        direction = "down"
    else:
        direction = "neutral"
    return {
        "direction": direction,
        "slope": round(slope, 2),
        "r_squared": round(r_value ** 2, 4),
        "change_pct": round(change_pct, 2),
        "p_value": round(p_value, 4),
    }


def seasonal_decomposition(daily_df, period=30):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").set_index("order_date")
    df["trend"] = df["revenue"].rolling(window=period, center=True, min_periods=1).mean()
    df["detrended"] = df["revenue"] - df["trend"]
    df["day_of_month"] = df.index.day
    seasonal_pattern = df.groupby("day_of_month")["detrended"].mean()
    df["seasonal"] = df["day_of_month"].map(seasonal_pattern)
    df["residual"] = df["revenue"] - df["trend"] - df["seasonal"]
    return df.reset_index()


def compute_weekly_pattern(daily_df):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["day_of_week"] = df["order_date"].dt.day_name()
    df["day_num"] = df["order_date"].dt.dayofweek
    return (
        df.groupby(["day_num", "day_of_week"])
        .agg(avg_revenue=("revenue", "mean"), avg_orders=("num_orders", "mean"))
        .reset_index().sort_values("day_num")
    )


def compute_monthly_seasonality(daily_df):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.month
    df["month_name"] = df["order_date"].dt.strftime("%b")
    return (
        df.groupby(["month", "month_name"])
        .agg(avg_revenue=("revenue", "mean"), total_revenue=("revenue", "sum"))
        .reset_index().sort_values("month")
    )
