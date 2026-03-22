import pandas as pd
from src.database.queries import query_to_df


def session_summary(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT s.session_id,
               s.user_email,
               e.full_name,
               e.practice,
               e.level,
               s.request_count,
               s.total_cost,
               s.total_tokens,
               s.prompt_count,
               s.tool_uses,
               s.first_event,
               s.last_event
        FROM (
            SELECT session_id,
                   user_email,
                   COUNT(*) as request_count,
                   SUM(cost_usd) as total_cost,
                   SUM(input_tokens + output_tokens) as total_tokens,
                   MIN(event_timestamp) as first_event,
                   MAX(event_timestamp) as last_event,
                   (SELECT COUNT(*) FROM user_prompts p WHERE p.session_id = a.session_id) as prompt_count,
                   (SELECT COUNT(*) FROM tool_results t WHERE t.session_id = a.session_id) as tool_uses
            FROM api_requests a
            GROUP BY session_id
        ) s
        JOIN employees e ON s.user_email = e.email
        ORDER BY s.total_cost DESC
    """
    return query_to_df(sql, db_path=db_path)


def sessions_per_user(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT a.user_email,
               e.full_name,
               e.practice,
               e.level,
               e.location,
               COUNT(DISTINCT a.session_id) as session_count,
               COUNT(*) as total_requests,
               SUM(a.cost_usd) as total_cost,
               MIN(a.event_timestamp) as first_seen,
               MAX(a.event_timestamp) as last_seen
        FROM api_requests a
        JOIN employees e ON a.user_email = e.email
        GROUP BY a.user_email
        ORDER BY session_count DESC
    """
    return query_to_df(sql, db_path=db_path)


def daily_active_users(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(event_timestamp) as date,
               COUNT(DISTINCT user_email) as active_users,
               COUNT(DISTINCT session_id) as active_sessions
        FROM api_requests
        GROUP BY DATE(event_timestamp)
        ORDER BY date
    """
    return query_to_df(sql, db_path=db_path)


def session_duration_distribution(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT session_id,
               user_email,
               MIN(event_timestamp) as start_time,
               MAX(event_timestamp) as end_time,
               COUNT(*) as event_count,
               SUM(cost_usd) as session_cost
        FROM api_requests
        GROUP BY session_id
        HAVING event_count > 1
    """
    df = query_to_df(sql, db_path=db_path)
    if not df.empty:
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["end_time"] = pd.to_datetime(df["end_time"])
        df["duration_minutes"] = (df["end_time"] - df["start_time"]).dt.total_seconds() / 60
    return df


def weekly_engagement(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT strftime('%Y-W%W', event_timestamp) as week,
               COUNT(DISTINCT user_email) as active_users,
               COUNT(DISTINCT session_id) as sessions,
               SUM(cost_usd) as total_cost,
               SUM(input_tokens + output_tokens) as total_tokens
        FROM api_requests
        GROUP BY week
        ORDER BY week
    """
    return query_to_df(sql, db_path=db_path)
