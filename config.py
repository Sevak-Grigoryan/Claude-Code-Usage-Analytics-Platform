import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TELEMETRY_FILE = os.path.join(BASE_DIR, "data", "raw", "telemetry_logs.jsonl")
EMPLOYEES_FILE = os.path.join(BASE_DIR, "data", "raw", "employees.csv")
DATABASE_PATH = os.path.join(BASE_DIR, "data", "analytics.db")
