import numpy as np
import pandas as pd
from src.database.queries import query_to_df


def compute_correlation_matrix(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT a.user_email,
               COUNT(*) as request_count,
               COUNT(DISTINCT a.session_id) as session_count,
               SUM(a.cost_usd) as total_cost,
               AVG(a.cost_usd) as avg_cost,
               SUM(a.input_tokens + a.output_tokens) as total_tokens,
               AVG(a.duration_ms) as avg_duration,
               SUM(a.cache_read_tokens) as cache_reads,
               (SELECT COUNT(*) FROM user_prompts p WHERE p.user_email = a.user_email) as prompt_count,
               (SELECT AVG(p.prompt_length) FROM user_prompts p WHERE p.user_email = a.user_email) as avg_prompt_length,
               (SELECT COUNT(*) FROM tool_results t WHERE t.user_email = a.user_email) as tool_uses
        FROM api_requests a
        GROUP BY a.user_email
    """
    df = query_to_df(sql, db_path=db_path)
    numeric_cols = ["request_count", "session_count", "total_cost", "avg_cost",
                    "total_tokens", "avg_duration", "cache_reads", "prompt_count",
                    "avg_prompt_length", "tool_uses"]
    return df[numeric_cols].corr().round(3)


def user_efficiency_scores(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT a.user_email,
               e.full_name,
               e.practice,
               e.level,
               COUNT(*) as requests,
               SUM(a.output_tokens) as total_output,
               SUM(a.cost_usd) as total_cost,
               SUM(a.cache_read_tokens) as cache_reads,
               SUM(a.input_tokens) as total_input,
               AVG(a.duration_ms) as avg_duration,
               COUNT(DISTINCT a.session_id) as sessions
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY a.user_email
    """
    df = query_to_df(sql, db_path=db_path)

    df["tokens_per_dollar"] = np.where(
        df["total_cost"] > 0,
        (df["total_output"] / df["total_cost"]).round(0),
        0
    )
    df["cache_hit_rate"] = np.where(
        (df["total_input"] + df["cache_reads"]) > 0,
        (df["cache_reads"] / (df["total_input"] + df["cache_reads"]) * 100).round(2),
        0
    )
    df["avg_output_per_request"] = (df["total_output"] / df["requests"]).round(0)

    return df.sort_values("tokens_per_dollar", ascending=False)


def cohort_analysis(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.level,
               COUNT(DISTINCT a.user_email) as users,
               COUNT(*) as total_requests,
               COUNT(*) * 1.0 / COUNT(DISTINCT a.user_email) as requests_per_user,
               COUNT(DISTINCT a.session_id) * 1.0 / COUNT(DISTINCT a.user_email) as sessions_per_user,
               SUM(a.cost_usd) / COUNT(DISTINCT a.user_email) as cost_per_user,
               AVG(a.cost_usd) as avg_cost_per_request,
               AVG(a.output_tokens) as avg_output_tokens,
               AVG(a.duration_ms) as avg_duration_ms,
               SUM(a.cache_read_tokens) * 1.0 / NULLIF(SUM(a.input_tokens + a.cache_read_tokens), 0) * 100 as cache_hit_rate
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY e.level
        ORDER BY e.level
    """
    df = query_to_df(sql, db_path=db_path)
    for col in ["requests_per_user", "sessions_per_user", "cost_per_user",
                 "avg_cost_per_request", "avg_output_tokens", "avg_duration_ms", "cache_hit_rate"]:
        if col in df.columns:
            df[col] = df[col].round(2)
    return df


def practice_comparison(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.practice,
               COUNT(DISTINCT a.user_email) as users,
               COUNT(DISTINCT a.session_id) as total_sessions,
               COUNT(*) as total_requests,
               SUM(a.cost_usd) as total_cost,
               SUM(a.cost_usd) / COUNT(DISTINCT a.user_email) as cost_per_user,
               AVG(a.output_tokens) as avg_output_tokens,
               AVG(a.duration_ms) as avg_duration,
               SUM(a.cache_read_tokens) * 1.0 / NULLIF(SUM(a.input_tokens + a.cache_read_tokens), 0) * 100 as cache_hit_rate,
               (SELECT COUNT(*) FROM tool_results t
                JOIN employees e2 ON t.user_email = e2.email
                WHERE e2.practice = e.practice) * 1.0 / COUNT(*) as tools_per_request
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY e.practice
        ORDER BY total_cost DESC
    """
    df = query_to_df(sql, db_path=db_path)
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].round(2)
    return df


def model_preference_by_practice(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.practice,
               a.model,
               COUNT(*) as request_count,
               SUM(a.cost_usd) as total_cost,
               AVG(a.output_tokens) as avg_output,
               ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY e.practice), 1) as pct_of_practice
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY e.practice, a.model
        ORDER BY e.practice, request_count DESC
    """
    return query_to_df(sql, db_path=db_path)


def prompt_length_analysis(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.practice,
               e.level,
               COUNT(*) as prompt_count,
               AVG(p.prompt_length) as avg_length,
               MIN(p.prompt_length) as min_length,
               MAX(p.prompt_length) as max_length
        FROM user_prompts p
        JOIN employees e ON p.user_email = e.email
        GROUP BY e.practice, e.level
        ORDER BY e.practice, e.level
    """
    df = query_to_df(sql, db_path=db_path)
    df["avg_length"] = df["avg_length"].round(0)
    return df


def session_complexity_distribution(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT a.session_id,
               a.user_email,
               e.practice,
               e.level,
               COUNT(*) as api_calls,
               SUM(a.cost_usd) as session_cost,
               SUM(a.output_tokens) as total_output,
               (SELECT COUNT(*) FROM user_prompts p WHERE p.session_id = a.session_id) as turns,
               (SELECT COUNT(*) FROM tool_results t WHERE t.session_id = a.session_id) as tool_uses
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY a.session_id
    """
    df = query_to_df(sql, db_path=db_path)

    def classify(row):
        if row["turns"] <= 2 and row["tool_uses"] <= 3:
            return "Simple"
        elif row["turns"] <= 5 and row["tool_uses"] <= 10:
            return "Moderate"
        elif row["turns"] <= 15:
            return "Complex"
        else:
            return "Very Complex"

    df["complexity"] = df.apply(classify, axis=1)
    return df


def daily_efficiency_trend(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(event_timestamp) as date,
               SUM(output_tokens) as total_output,
               SUM(cost_usd) as total_cost,
               AVG(duration_ms) as avg_duration,
               SUM(cache_read_tokens) * 1.0 / NULLIF(SUM(input_tokens + cache_read_tokens), 0) * 100 as cache_hit_rate,
               COUNT(DISTINCT user_email) as active_users
        FROM api_requests
        GROUP BY DATE(event_timestamp)
        ORDER BY date
    """
    df = query_to_df(sql, db_path=db_path)
    df["tokens_per_dollar"] = np.where(
        df["total_cost"] > 0,
        (df["total_output"] / df["total_cost"]).round(0),
        0
    )
    return df
