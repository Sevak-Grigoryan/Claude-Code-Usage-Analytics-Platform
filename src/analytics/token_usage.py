import pandas as pd
from src.database.queries import query_to_df


def daily_token_consumption(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(event_timestamp) as date,
               SUM(input_tokens) as input_tokens,
               SUM(output_tokens) as output_tokens,
               SUM(cache_read_tokens) as cache_read_tokens,
               SUM(cache_creation_tokens) as cache_creation_tokens,
               SUM(input_tokens + output_tokens) as total_tokens,
               SUM(cost_usd) as total_cost,
               COUNT(*) as request_count,
               AVG(duration_ms) as avg_duration_ms
        FROM api_requests
        GROUP BY DATE(event_timestamp)
        ORDER BY date
    """
    return query_to_df(sql, db_path=db_path)


def tokens_by_model(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT model,
               COUNT(*) as request_count,
               SUM(input_tokens) as total_input,
               SUM(output_tokens) as total_output,
               SUM(cost_usd) as total_cost,
               AVG(cost_usd) as avg_cost_per_request,
               AVG(duration_ms) as avg_duration_ms,
               SUM(cache_read_tokens) as total_cache_read,
               SUM(cache_creation_tokens) as total_cache_create
        FROM api_requests
        GROUP BY model
        ORDER BY total_cost DESC
    """
    return query_to_df(sql, db_path=db_path)


def tokens_by_practice(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.practice,
               COUNT(*) as request_count,
               SUM(a.input_tokens + a.output_tokens) as total_tokens,
               SUM(a.cost_usd) as total_cost,
               AVG(a.cost_usd) as avg_cost_per_request,
               COUNT(DISTINCT a.user_email) as unique_users
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY e.practice
        ORDER BY total_cost DESC
    """
    return query_to_df(sql, db_path=db_path)


def tokens_by_level(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.level,
               COUNT(*) as request_count,
               SUM(a.input_tokens + a.output_tokens) as total_tokens,
               SUM(a.cost_usd) as total_cost,
               AVG(a.cost_usd) as avg_cost_per_request,
               COUNT(DISTINCT a.user_email) as unique_users
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY e.level
        ORDER BY e.level
    """
    return query_to_df(sql, db_path=db_path)


def cost_by_user(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT a.user_email,
               e.full_name,
               e.practice,
               e.level,
               e.location,
               COUNT(*) as request_count,
               SUM(a.cost_usd) as total_cost,
               SUM(a.input_tokens + a.output_tokens) as total_tokens,
               COUNT(DISTINCT a.session_id) as session_count,
               AVG(a.duration_ms) as avg_duration_ms
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY a.user_email
        ORDER BY total_cost DESC
    """
    return query_to_df(sql, db_path=db_path)


def hourly_usage_pattern(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT CAST(SUBSTR(event_timestamp, 12, 2) AS INTEGER) as hour,
               COUNT(*) as request_count,
               SUM(cost_usd) as total_cost,
               SUM(input_tokens + output_tokens) as total_tokens
        FROM api_requests
        GROUP BY hour
        ORDER BY hour
    """
    return query_to_df(sql, db_path=db_path)


def daily_cost_by_practice(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(a.event_timestamp) as date,
               e.practice,
               SUM(a.cost_usd) as total_cost,
               COUNT(*) as request_count
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY date, e.practice
        ORDER BY date, e.practice
    """
    return query_to_df(sql, db_path=db_path)
