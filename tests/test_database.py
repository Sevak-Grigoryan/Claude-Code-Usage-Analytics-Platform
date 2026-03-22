import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import initialize_database, db_session, get_connection
from src.database.queries import get_summary_stats, query_to_df


def test_database_initialization():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        initialize_database(db_path)
        conn = get_connection(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected = ["api_errors", "api_requests", "employees", "tool_decisions", "tool_results", "user_prompts"]
        for table in expected:
            assert table in tables, f"Missing table: {table}"
        print(f"PASS: database_initialization - {len(tables)} tables created")
    finally:
        os.unlink(db_path)


def test_summary_stats():
    stats = get_summary_stats()
    assert stats["total_api_requests"] > 0, "No API requests found"
    assert stats["total_sessions"] > 0, "No sessions found"
    assert stats["total_users"] > 0, "No users found"
    assert stats["total_cost"] > 0, "No cost data"
    print(f"PASS: summary_stats - {stats['total_api_requests']} requests, ${stats['total_cost']:.2f} cost")


def test_query_to_df():
    df = query_to_df("SELECT COUNT(*) as cnt FROM api_requests")
    assert len(df) == 1
    assert df["cnt"].iloc[0] > 0
    print(f"PASS: query_to_df - {df['cnt'].iloc[0]} rows in api_requests")


if __name__ == "__main__":
    test_database_initialization()
    test_summary_stats()
    test_query_to_df()
    print("\nAll database tests passed!")
