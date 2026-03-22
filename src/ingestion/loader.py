import csv
import logging
import time

from src.database.connection import initialize_database, db_session
from src.ingestion.parser import parse_telemetry_file, extract_event_fields
from src.ingestion.validator import validate_event, ValidationStats

logger = logging.getLogger(__name__)

BATCH_SIZE = 5000


def load_employees(filepath: str, db_path: str = None):
    with db_session(db_path) as conn:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append((
                    row["email"],
                    row["full_name"],
                    row["practice"],
                    row["level"],
                    row["location"],
                ))
            conn.executemany(
                "INSERT OR REPLACE INTO employees (email, full_name, practice, level, location) VALUES (?, ?, ?, ?, ?)",
                rows,
            )
    logger.info("Loaded %d employees", len(rows))
    return len(rows)


def load_telemetry(filepath: str, db_path: str = None) -> dict:
    initialize_database(db_path)
    stats = ValidationStats()

    buffers = {
        "api_requests": [],
        "tool_decisions": [],
        "tool_results": [],
        "user_prompts": [],
        "api_errors": [],
    }

    start_time = time.time()
    events_loaded = 0

    with db_session(db_path) as conn:
        for raw_event in parse_telemetry_file(filepath):
            record = extract_event_fields(raw_event)
            is_valid, error_msg = validate_event(record)
            stats.record(is_valid, error_msg)

            if not is_valid:
                continue

            event_type = record["event_type"]

            if event_type == "claude_code.api_request":
                buffers["api_requests"].append((
                    record["event_timestamp"],
                    record["session_id"],
                    record["user_email"],
                    record["user_id"],
                    record["organization_id"],
                    record["model"],
                    record["input_tokens"],
                    record["output_tokens"],
                    record["cache_read_tokens"],
                    record["cache_creation_tokens"],
                    record["cost_usd"],
                    record["duration_ms"],
                    record["terminal_type"],
                    record["host_arch"],
                    record["os_type"],
                    record["os_version"],
                    record["service_version"],
                ))
            elif event_type == "claude_code.tool_decision":
                buffers["tool_decisions"].append((
                    record["event_timestamp"],
                    record["session_id"],
                    record["user_email"],
                    record["user_id"],
                    record["tool_name"],
                    record["decision"],
                    record["source"],
                    record["terminal_type"],
                ))
            elif event_type == "claude_code.tool_result":
                buffers["tool_results"].append((
                    record["event_timestamp"],
                    record["session_id"],
                    record["user_email"],
                    record["user_id"],
                    record["tool_name"],
                    record["success"],
                    record["duration_ms"],
                    record["decision_type"],
                    record["decision_source"],
                    record["result_size_bytes"],
                    record["terminal_type"],
                ))
            elif event_type == "claude_code.user_prompt":
                buffers["user_prompts"].append((
                    record["event_timestamp"],
                    record["session_id"],
                    record["user_email"],
                    record["user_id"],
                    record["prompt_length"],
                    record["terminal_type"],
                ))
            elif event_type == "claude_code.api_error":
                buffers["api_errors"].append((
                    record["event_timestamp"],
                    record["session_id"],
                    record["user_email"],
                    record["user_id"],
                    record["model"],
                    record["error"],
                    record["status_code"],
                    record["duration_ms"],
                    record["attempt"],
                    record["terminal_type"],
                ))

            events_loaded += 1
            if events_loaded % BATCH_SIZE == 0:
                _flush_buffers(conn, buffers)
                if events_loaded % 50000 == 0:
                    logger.info("Processed %d events...", events_loaded)

        _flush_buffers(conn, buffers)

    elapsed = time.time() - start_time
    summary = stats.summary()
    summary["elapsed_seconds"] = round(elapsed, 2)
    summary["events_per_second"] = round(events_loaded / elapsed, 0) if elapsed > 0 else 0

    logger.info(
        "Ingestion complete: %d events in %.1fs (%.0f events/sec)",
        events_loaded, elapsed, summary["events_per_second"],
    )
    return summary


def _flush_buffers(conn, buffers: dict):
    if buffers["api_requests"]:
        conn.executemany(
            """INSERT INTO api_requests
               (event_timestamp, session_id, user_email, user_id, organization_id,
                model, input_tokens, output_tokens, cache_read_tokens,
                cache_creation_tokens, cost_usd, duration_ms, terminal_type,
                host_arch, os_type, os_version, service_version)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            buffers["api_requests"],
        )
        buffers["api_requests"].clear()

    if buffers["tool_decisions"]:
        conn.executemany(
            """INSERT INTO tool_decisions
               (event_timestamp, session_id, user_email, user_id,
                tool_name, decision, source, terminal_type)
               VALUES (?,?,?,?,?,?,?,?)""",
            buffers["tool_decisions"],
        )
        buffers["tool_decisions"].clear()

    if buffers["tool_results"]:
        conn.executemany(
            """INSERT INTO tool_results
               (event_timestamp, session_id, user_email, user_id,
                tool_name, success, duration_ms, decision_type,
                decision_source, result_size_bytes, terminal_type)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            buffers["tool_results"],
        )
        buffers["tool_results"].clear()

    if buffers["user_prompts"]:
        conn.executemany(
            """INSERT INTO user_prompts
               (event_timestamp, session_id, user_email, user_id,
                prompt_length, terminal_type)
               VALUES (?,?,?,?,?,?)""",
            buffers["user_prompts"],
        )
        buffers["user_prompts"].clear()

    if buffers["api_errors"]:
        conn.executemany(
            """INSERT INTO api_errors
               (event_timestamp, session_id, user_email, user_id,
                model, error, status_code, duration_ms, attempt, terminal_type)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            buffers["api_errors"],
        )
        buffers["api_errors"].clear()
