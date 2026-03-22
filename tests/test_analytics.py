import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    session_duration_distribution,
    weekly_engagement,
)
from src.analytics.tool_usage import (
    tool_usage_summary,
    tool_decision_summary,
    tool_usage_by_practice,
    error_analysis,
)
from src.analytics.forecasting import (
    forecast_daily_cost,
    detect_anomalies,
    usage_growth_rate,
)


def test_daily_token_consumption():
    df = daily_token_consumption()
    assert not df.empty, "daily_token_consumption returned empty"
    assert "date" in df.columns
    assert "total_cost" in df.columns
    assert all(df["total_cost"] >= 0)
    print(f"PASS: daily_token_consumption - {len(df)} days")


def test_tokens_by_model():
    df = tokens_by_model()
    assert not df.empty
    assert "model" in df.columns
    assert len(df) >= 3
    print(f"PASS: tokens_by_model - {len(df)} models")


def test_tokens_by_practice():
    df = tokens_by_practice()
    assert not df.empty
    assert "practice" in df.columns
    print(f"PASS: tokens_by_practice - {len(df)} practices")


def test_tokens_by_level():
    df = tokens_by_level()
    assert not df.empty
    assert "level" in df.columns
    print(f"PASS: tokens_by_level - {len(df)} levels")


def test_cost_by_user():
    df = cost_by_user()
    assert not df.empty
    assert "full_name" in df.columns
    assert "total_cost" in df.columns
    print(f"PASS: cost_by_user - {len(df)} users")


def test_hourly_pattern():
    df = hourly_usage_pattern()
    assert not df.empty
    assert len(df) <= 24
    print(f"PASS: hourly_usage_pattern - {len(df)} hours")


def test_sessions_per_user():
    df = sessions_per_user()
    assert not df.empty
    assert "session_count" in df.columns
    print(f"PASS: sessions_per_user - {len(df)} users")


def test_daily_active_users():
    df = daily_active_users()
    assert not df.empty
    assert "active_users" in df.columns
    print(f"PASS: daily_active_users - {len(df)} days")


def test_session_durations():
    df = session_duration_distribution()
    assert not df.empty
    assert "duration_minutes" in df.columns
    print(f"PASS: session_duration_distribution - {len(df)} sessions")


def test_weekly_engagement():
    df = weekly_engagement()
    assert not df.empty
    assert "active_users" in df.columns
    print(f"PASS: weekly_engagement - {len(df)} weeks")


def test_tool_usage_summary():
    df = tool_usage_summary()
    assert not df.empty
    assert "tool_name" in df.columns
    assert "success_rate" in df.columns
    print(f"PASS: tool_usage_summary - {len(df)} tools")


def test_tool_decisions():
    df = tool_decision_summary()
    assert not df.empty
    assert "accept_rate" in df.columns
    print(f"PASS: tool_decision_summary - {len(df)} tools")


def test_tool_by_practice():
    df = tool_usage_by_practice()
    assert not df.empty
    print(f"PASS: tool_usage_by_practice - {len(df)} rows")


def test_error_analysis():
    df = error_analysis()
    assert not df.empty
    assert "error" in df.columns
    print(f"PASS: error_analysis - {len(df)} error types")


def test_forecast_cost():
    df = forecast_daily_cost(days_ahead=7)
    assert not df.empty
    assert "predicted_cost" in df.columns
    forecast_rows = df[df["is_forecast"]].shape[0]
    assert forecast_rows == 7
    print(f"PASS: forecast_daily_cost - {len(df)} rows ({forecast_rows} forecast)")


def test_anomaly_detection():
    df = detect_anomalies()
    assert not df.empty
    assert "is_anomaly" in df.columns
    n_anomalies = df["is_anomaly"].sum()
    print(f"PASS: detect_anomalies - {n_anomalies} anomalies detected")


def test_growth_rate():
    result = usage_growth_rate()
    assert isinstance(result, dict)
    assert "cost_growth_pct" in result
    print(f"PASS: usage_growth_rate - cost growth: {result['cost_growth_pct']}%")


if __name__ == "__main__":
    test_daily_token_consumption()
    test_tokens_by_model()
    test_tokens_by_practice()
    test_tokens_by_level()
    test_cost_by_user()
    test_hourly_pattern()
    test_sessions_per_user()
    test_daily_active_users()
    test_session_durations()
    test_weekly_engagement()
    test_tool_usage_summary()
    test_tool_decisions()
    test_tool_by_practice()
    test_error_analysis()
    test_forecast_cost()
    test_anomaly_detection()
    test_growth_rate()
    print("\nAll analytics tests passed!")
