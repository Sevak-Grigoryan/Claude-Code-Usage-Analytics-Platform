import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
from src.analytics.token_usage import daily_token_consumption


def forecast_daily_cost(days_ahead: int = 14, db_path: str = None) -> pd.DataFrame:
    df = daily_token_consumption(db_path=db_path)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["day_num"] = (df["date"] - df["date"].min()).dt.days

    X = df[["day_num"]].values
    y = df["total_cost"].values

    model = LinearRegression()
    model.fit(X, y)
    df["predicted_cost"] = model.predict(X)
    df["is_forecast"] = False

    last_date = df["date"].max()
    last_day_num = df["day_num"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days_ahead)
    future_day_nums = np.arange(last_day_num + 1, last_day_num + 1 + days_ahead).reshape(-1, 1)
    future_costs = model.predict(future_day_nums)

    future_df = pd.DataFrame({
        "date": future_dates,
        "day_num": future_day_nums.flatten(),
        "total_cost": np.nan,
        "predicted_cost": future_costs,
        "is_forecast": True,
    })

    result = pd.concat([df, future_df], ignore_index=True)
    result["trend_slope"] = model.coef_[0]
    result["r_squared"] = model.score(X, y)
    return result


def forecast_token_usage(days_ahead: int = 14, db_path: str = None) -> pd.DataFrame:
    df = daily_token_consumption(db_path=db_path)
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["day_num"] = (df["date"] - df["date"].min()).dt.days

    X = df[["day_num"]].values
    y = df["total_tokens"].values

    model = LinearRegression()
    model.fit(X, y)
    df["predicted_tokens"] = model.predict(X)
    df["is_forecast"] = False

    last_date = df["date"].max()
    last_day_num = df["day_num"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=days_ahead)
    future_day_nums = np.arange(last_day_num + 1, last_day_num + 1 + days_ahead).reshape(-1, 1)
    future_tokens = model.predict(future_day_nums)

    future_df = pd.DataFrame({
        "date": future_dates,
        "day_num": future_day_nums.flatten(),
        "total_tokens": np.nan,
        "predicted_tokens": future_tokens,
        "is_forecast": True,
    })

    return pd.concat([df, future_df], ignore_index=True)


def detect_anomalies(db_path: str = None, contamination: float = 0.05) -> pd.DataFrame:
    df = daily_token_consumption(db_path=db_path)
    if df.empty or len(df) < 10:
        return df

    features = df[["total_tokens", "total_cost", "request_count", "avg_duration_ms"]].copy()
    features = features.fillna(0)

    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )
    df["anomaly"] = iso_forest.fit_predict(features)
    df["anomaly_score"] = iso_forest.score_samples(features)
    df["is_anomaly"] = df["anomaly"] == -1

    return df


def usage_growth_rate(db_path: str = None) -> dict:
    df = daily_token_consumption(db_path=db_path)
    if df.empty:
        return {}

    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["year"] = df["date"].dt.year

    weekly = df.groupby(["year", "week"]).agg({
        "total_cost": "sum",
        "total_tokens": "sum",
        "request_count": "sum",
    }).reset_index()

    if len(weekly) < 2:
        return {"cost_growth": 0, "token_growth": 0, "request_growth": 0}

    recent = weekly.iloc[-1]
    previous = weekly.iloc[-2]

    def growth(current, prev):
        if prev == 0:
            return 0
        return round(((current - prev) / prev) * 100, 2)

    return {
        "cost_growth_pct": growth(recent["total_cost"], previous["total_cost"]),
        "token_growth_pct": growth(recent["total_tokens"], previous["total_tokens"]),
        "request_growth_pct": growth(recent["request_count"], previous["request_count"]),
        "current_week_cost": round(recent["total_cost"], 2),
        "previous_week_cost": round(previous["total_cost"], 2),
    }
