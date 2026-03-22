import pandas as pd
from src.database.connection import get_connection


def query_to_df(sql: str, params: tuple = (), db_path: str = None) -> pd.DataFrame:
    conn = get_connection(db_path)
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        conn.close()


def get_date_range(db_path: str = None) -> dict:
    sql = """
        SELECT MIN(event_timestamp) as min_date,
               MAX(event_timestamp) as max_date
        FROM api_requests
    """
    df = query_to_df(sql, db_path=db_path)
    return {"min_date": df["min_date"].iloc[0], "max_date": df["max_date"].iloc[0]}


def get_summary_stats(db_path: str = None) -> dict:
    conn = get_connection(db_path)
    try:
        stats = {}
        stats["total_api_requests"] = conn.execute(
            "SELECT COUNT(*) FROM api_requests"
        ).fetchone()[0]
        stats["total_sessions"] = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM api_requests"
        ).fetchone()[0]
        stats["total_users"] = conn.execute(
            "SELECT COUNT(DISTINCT user_email) FROM api_requests"
        ).fetchone()[0]
        stats["total_cost"] = conn.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM api_requests"
        ).fetchone()[0]
        stats["total_tokens"] = conn.execute(
            "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) FROM api_requests"
        ).fetchone()[0]
        stats["total_prompts"] = conn.execute(
            "SELECT COUNT(*) FROM user_prompts"
        ).fetchone()[0]
        stats["total_errors"] = conn.execute(
            "SELECT COUNT(*) FROM api_errors"
        ).fetchone()[0]
        stats["total_tool_uses"] = conn.execute(
            "SELECT COUNT(*) FROM tool_results"
        ).fetchone()[0]
        return stats
    finally:
        conn.close()
