import sqlite3
import os
from contextlib import contextmanager

from config import DATABASE_PATH
from src.database.schema import SCHEMA_SQL


def get_connection(db_path: str = None) -> sqlite3.Connection:
    path = db_path or DATABASE_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session(db_path: str = None):
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_database(db_path: str = None):
    with db_session(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
