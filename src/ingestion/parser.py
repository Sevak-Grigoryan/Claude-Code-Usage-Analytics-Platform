import json
import logging
from typing import Generator

logger = logging.getLogger(__name__)


def parse_telemetry_file(filepath: str) -> Generator[dict, None, None]:
    line_num = 0
    error_count = 0

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_num += 1
            line = line.strip()
            if not line:
                continue

            try:
                batch = json.loads(line)
            except json.JSONDecodeError as e:
                error_count += 1
                logger.warning("Line %d: invalid JSON - %s", line_num, e)
                continue

            log_events = batch.get("logEvents", [])
            batch_meta = {
                "log_group": batch.get("logGroup", ""),
                "log_stream": batch.get("logStream", ""),
                "year": batch.get("year"),
                "month": batch.get("month"),
                "day": batch.get("day"),
            }

            for log_event in log_events:
                message_str = log_event.get("message", "")
                try:
                    event = json.loads(message_str)
                except json.JSONDecodeError:
                    error_count += 1
                    continue

                event["_batch_meta"] = batch_meta
                event["_log_timestamp"] = log_event.get("timestamp")
                yield event

    if error_count > 0:
        logger.warning("Total parse errors: %d out of %d lines", error_count, line_num)


def extract_event_fields(event: dict) -> dict:
    attrs = event.get("attributes", {})
    resource = event.get("resource", {})
    body = event.get("body", "")

    base = {
        "event_type": body,
        "event_timestamp": attrs.get("event.timestamp", ""),
        "session_id": attrs.get("session.id", ""),
        "user_email": attrs.get("user.email", ""),
        "user_id": attrs.get("user.id", ""),
        "organization_id": attrs.get("organization.id", ""),
        "terminal_type": attrs.get("terminal.type", ""),
        "host_arch": resource.get("host.arch", ""),
        "os_type": resource.get("os.type", ""),
        "os_version": resource.get("os.version", ""),
        "service_version": resource.get("service.version", ""),
    }

    if body == "claude_code.api_request":
        base.update({
            "model": attrs.get("model", ""),
            "input_tokens": _safe_int(attrs.get("input_tokens", "0")),
            "output_tokens": _safe_int(attrs.get("output_tokens", "0")),
            "cache_read_tokens": _safe_int(attrs.get("cache_read_tokens", "0")),
            "cache_creation_tokens": _safe_int(attrs.get("cache_creation_tokens", "0")),
            "cost_usd": _safe_float(attrs.get("cost_usd", "0")),
            "duration_ms": _safe_int(attrs.get("duration_ms", "0")),
        })
    elif body == "claude_code.tool_decision":
        base.update({
            "tool_name": attrs.get("tool_name", ""),
            "decision": attrs.get("decision", ""),
            "source": attrs.get("source", ""),
        })
    elif body == "claude_code.tool_result":
        base.update({
            "tool_name": attrs.get("tool_name", ""),
            "success": attrs.get("success", ""),
            "duration_ms": _safe_int(attrs.get("duration_ms", "0")),
            "decision_type": attrs.get("decision_type", ""),
            "decision_source": attrs.get("decision_source", ""),
            "result_size_bytes": _safe_int(attrs.get("tool_result_size_bytes")) if attrs.get("tool_result_size_bytes") else None,
        })
    elif body == "claude_code.user_prompt":
        base.update({
            "prompt_length": _safe_int(attrs.get("prompt_length", "0")),
        })
    elif body == "claude_code.api_error":
        base.update({
            "model": attrs.get("model", ""),
            "error": attrs.get("error", ""),
            "status_code": attrs.get("status_code", ""),
            "duration_ms": _safe_int(attrs.get("duration_ms", "0")),
            "attempt": _safe_int(attrs.get("attempt", "1")),
        })

    return base


def _safe_int(value, default=0) -> int:
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def _safe_float(value, default=0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
