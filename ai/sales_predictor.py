"""
Athena Core — Sales Prediction (ML)
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error


def prepare_features(daily_df):
    df = daily_df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.sort_values("order_date").reset_index(drop=True)
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["month"] = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["day_of_month"] = df["order_date"].dt.day
    for lag in [1, 7, 14, 30]:
        df[f"lag_{lag}"] = df["revenue"].shift(lag)
    for w in [7, 14, 30]:
        df[f"rolling_mean_{w}"] = df["revenue"].rolling(window=w, min_periods=1).mean()
        df[f"rolling_std_{w}"] = df["revenue"].rolling(window=w, min_periods=1).std()
    df = df.dropna().reset_index(drop=True)
    return df


def train_model(daily_df):
    df = prepare_features(daily_df)
    feature_cols = [c for c in df.columns if c not in ["order_date", "revenue", "num_orders", "units_sold"]]
    
    if df.empty or len(df) < 5:
        return None, feature_cols, {
            "mae": 0, "rmse": 0, "test_dates": [], "y_test": [], "y_pred": [],
            "importance": pd.DataFrame(columns=["feature", "importance"])
        }

    X = df[feature_cols].values
    y = df["revenue"].values

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Feature importance
    importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    test_dates = df["order_date"].iloc[split_idx:].values
    return model, feature_cols, {
        "mae": round(mae, 2), "rmse": round(rmse, 2),
        "test_dates": test_dates, "y_test": y_test, "y_pred": y_pred,
        "importance": importance,
    }


def forecast_future(model, daily_df, feature_cols, days=30):
    if model is None:
        return pd.DataFrame(columns=["date", "predicted_revenue"])
    df = prepare_features(daily_df)
    last_row = df.iloc[-1].copy()
    last_date = pd.to_datetime(df["order_date"].iloc[-1])
    forecasts = []
    revenue_history = df["revenue"].tolist()

    for i in range(1, days + 1):
        future_date = last_date + pd.Timedelta(days=i)
        row = {}
        row["day_of_week"] = future_date.dayofweek
        row["month"] = future_date.month
        row["quarter"] = future_date.quarter
        row["is_weekend"] = 1 if future_date.dayofweek >= 5 else 0
        row["day_of_month"] = future_date.day

        hist = revenue_history
        row["lag_1"] = hist[-1] if len(hist) >= 1 else 0
        row["lag_7"] = hist[-7] if len(hist) >= 7 else hist[-1]
        row["lag_14"] = hist[-14] if len(hist) >= 14 else hist[-1]
        row["lag_30"] = hist[-30] if len(hist) >= 30 else hist[-1]

        for w in [7, 14, 30]:
            window = hist[-w:] if len(hist) >= w else hist
            row[f"rolling_mean_{w}"] = np.mean(window)
            row[f"rolling_std_{w}"] = np.std(window) if len(window) > 1 else 0

        X_future = np.array([[row.get(f, 0) for f in feature_cols]])
        pred = model.predict(X_future)[0]
        revenue_history.append(pred)
        forecasts.append({"date": future_date, "predicted_revenue": round(pred, 2)})

    return pd.DataFrame(forecasts)
