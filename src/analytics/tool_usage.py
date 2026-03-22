import pandas as pd
from src.database.queries import query_to_df


def tool_usage_summary(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT tool_name,
               COUNT(*) as total_uses,
               SUM(CASE WHEN success = 'true' THEN 1 ELSE 0 END) as successes,
               SUM(CASE WHEN success = 'false' THEN 1 ELSE 0 END) as failures,
               ROUND(AVG(CASE WHEN success = 'true' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate,
               AVG(duration_ms) as avg_duration_ms,
               SUM(duration_ms) as total_duration_ms
        FROM tool_results
        GROUP BY tool_name
        ORDER BY total_uses DESC
    """
    return query_to_df(sql, db_path=db_path)


def tool_decision_summary(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT tool_name,
               COUNT(*) as total_decisions,
               SUM(CASE WHEN decision = 'accept' THEN 1 ELSE 0 END) as accepted,
               SUM(CASE WHEN decision = 'reject' THEN 1 ELSE 0 END) as rejected,
               ROUND(AVG(CASE WHEN decision = 'accept' THEN 1.0 ELSE 0.0 END) * 100, 2) as accept_rate
        FROM tool_decisions
        GROUP BY tool_name
        ORDER BY total_decisions DESC
    """
    return query_to_df(sql, db_path=db_path)


def tool_usage_by_practice(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT e.practice,
               t.tool_name,
               COUNT(*) as use_count
        FROM tool_results t
        JOIN employees e ON t.user_email = e.email
        GROUP BY e.practice, t.tool_name
        ORDER BY e.practice, use_count DESC
    """
    return query_to_df(sql, db_path=db_path)


def tool_usage_trends(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(event_timestamp) as date,
               tool_name,
               COUNT(*) as use_count,
               AVG(duration_ms) as avg_duration_ms,
               ROUND(AVG(CASE WHEN success = 'true' THEN 1.0 ELSE 0.0 END) * 100, 2) as success_rate
        FROM tool_results
        GROUP BY date, tool_name
        ORDER BY date, use_count DESC
    """
    return query_to_df(sql, db_path=db_path)


def tool_failure_analysis(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT t.tool_name,
               e.practice,
               COUNT(*) as total_uses,
               SUM(CASE WHEN t.success = 'false' THEN 1 ELSE 0 END) as failures,
               ROUND(AVG(CASE WHEN t.success = 'false' THEN 1.0 ELSE 0.0 END) * 100, 2) as failure_rate
        FROM tool_results t
        JOIN employees e ON t.user_email = e.email
        GROUP BY t.tool_name, e.practice
        HAVING failures > 0
        ORDER BY failures DESC
    """
    return query_to_df(sql, db_path=db_path)


def error_analysis(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT error,
               status_code,
               COUNT(*) as occurrence_count,
               AVG(duration_ms) as avg_duration_ms,
               COUNT(DISTINCT user_email) as affected_users,
               COUNT(DISTINCT session_id) as affected_sessions
        FROM api_errors
        GROUP BY error, status_code
        ORDER BY occurrence_count DESC
    """
    return query_to_df(sql, db_path=db_path)


def daily_error_trend(db_path: str = None) -> pd.DataFrame:
    sql = """
        SELECT DATE(event_timestamp) as date,
               COUNT(*) as error_count,
               COUNT(DISTINCT user_email) as affected_users
        FROM api_errors
        GROUP BY date
        ORDER BY date
    """
    return query_to_df(sql, db_path=db_path)
