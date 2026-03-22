import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from src.database.queries import get_summary_stats, query_to_df
from src.analytics.token_usage import (
    daily_token_consumption,
    tokens_by_model,
    tokens_by_practice,
    tokens_by_level,
    cost_by_user,
    hourly_usage_pattern,
)
from src.analytics.session_patterns import (
    sessions_per_user,
    daily_active_users,
    weekly_engagement,
)
from src.analytics.tool_usage import (
    tool_usage_summary,
    tool_decision_summary,
    error_analysis,
)
from src.analytics.forecasting import (
    forecast_daily_cost,
    detect_anomalies,
    usage_growth_rate,
)

app = FastAPI(
    title="Claude Code Analytics API",
    description="Programmatic access to Claude Code usage analytics",
    version="1.0.0",
)


def df_to_response(df):
    return df.fillna("").to_dict(orient="records")


@app.get("/")
def root():
    return {"message": "Claude Code Analytics API", "version": "1.0.0"}


@app.get("/api/summary")
def summary():
    return get_summary_stats()


@app.get("/api/tokens/daily")
def tokens_daily():
    return df_to_response(daily_token_consumption())


@app.get("/api/tokens/by-model")
def tokens_model():
    return df_to_response(tokens_by_model())


@app.get("/api/tokens/by-practice")
def tokens_practice():
    return df_to_response(tokens_by_practice())


@app.get("/api/tokens/by-level")
def tokens_level():
    return df_to_response(tokens_by_level())


@app.get("/api/tokens/hourly-pattern")
def tokens_hourly():
    return df_to_response(hourly_usage_pattern())


@app.get("/api/users/cost")
def users_cost():
    return df_to_response(cost_by_user())


@app.get("/api/users/sessions")
def users_sessions():
    return df_to_response(sessions_per_user())


@app.get("/api/users/daily-active")
def users_dau():
    return df_to_response(daily_active_users())


@app.get("/api/users/weekly-engagement")
def users_weekly():
    return df_to_response(weekly_engagement())


@app.get("/api/tools/usage")
def tools_usage():
    return df_to_response(tool_usage_summary())


@app.get("/api/tools/decisions")
def tools_decisions():
    return df_to_response(tool_decision_summary())


@app.get("/api/errors")
def errors():
    return df_to_response(error_analysis())


@app.get("/api/forecast/cost")
def forecast_cost(days: int = Query(14, ge=1, le=60)):
    df = forecast_daily_cost(days_ahead=days)
    return df_to_response(df)


@app.get("/api/anomalies")
def anomalies(sensitivity: float = Query(0.05, ge=0.01, le=0.2)):
    df = detect_anomalies(contamination=sensitivity)
    return df_to_response(df)


@app.get("/api/growth")
def growth():
    return usage_growth_rate()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
