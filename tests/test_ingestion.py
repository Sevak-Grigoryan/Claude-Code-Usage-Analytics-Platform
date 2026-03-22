import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.parser import extract_event_fields
from src.ingestion.validator import validate_event, ValidationStats


def make_api_request_event():
    return {
        "body": "claude_code.api_request",
        "attributes": {
            "event.timestamp": "2026-01-15T10:30:00.000Z",
            "session.id": "sess-123",
            "user.email": "test@example.com",
            "user.id": "user-abc",
            "organization.id": "org-xyz",
            "terminal.type": "vscode",
            "event.name": "api_request",
            "model": "claude-opus-4-6",
            "input_tokens": "500",
            "output_tokens": "200",
            "cache_read_tokens": "1000",
            "cache_creation_tokens": "300",
            "cost_usd": "0.05",
            "duration_ms": "5000",
        },
        "resource": {
            "host.arch": "arm64",
            "host.name": "test-machine",
            "os.type": "darwin",
            "os.version": "24.6.0",
            "service.version": "2.1.50",
        },
    }


def test_extract_api_request():
    event = make_api_request_event()
    record = extract_event_fields(event)

    assert record["event_type"] == "claude_code.api_request"
    assert record["session_id"] == "sess-123"
    assert record["user_email"] == "test@example.com"
    assert record["model"] == "claude-opus-4-6"
    assert record["input_tokens"] == 500
    assert record["output_tokens"] == 200
    assert record["cost_usd"] == 0.05
    assert record["duration_ms"] == 5000
    print("PASS: test_extract_api_request")


def test_extract_tool_decision():
    event = {
        "body": "claude_code.tool_decision",
        "attributes": {
            "event.timestamp": "2026-01-15T10:30:00.000Z",
            "session.id": "sess-123",
            "user.email": "test@example.com",
            "user.id": "user-abc",
            "organization.id": "org-xyz",
            "terminal.type": "vscode",
            "tool_name": "Read",
            "decision": "accept",
            "source": "config",
        },
        "resource": {},
    }
    record = extract_event_fields(event)
    assert record["event_type"] == "claude_code.tool_decision"
    assert record["tool_name"] == "Read"
    assert record["decision"] == "accept"
    print("PASS: test_extract_tool_decision")


def test_validate_valid_event():
    event = make_api_request_event()
    record = extract_event_fields(event)
    is_valid, msg = validate_event(record)
    assert is_valid, f"Expected valid, got: {msg}"
    print("PASS: test_validate_valid_event")


def test_validate_missing_email():
    record = {
        "event_type": "claude_code.api_request",
        "event_timestamp": "2026-01-15T10:30:00.000Z",
        "session_id": "sess-123",
        "user_email": "",
        "model": "claude-opus-4-6",
    }
    is_valid, msg = validate_event(record)
    assert not is_valid
    assert "Missing required field" in msg
    print("PASS: test_validate_missing_email")


def test_validate_invalid_event_type():
    record = {
        "event_type": "unknown_event",
        "event_timestamp": "2026-01-15T10:30:00.000Z",
        "session_id": "sess-123",
        "user_email": "test@example.com",
    }
    is_valid, msg = validate_event(record)
    assert not is_valid
    assert "Unknown event type" in msg
    print("PASS: test_validate_invalid_event_type")


def test_validate_negative_cost():
    record = {
        "event_type": "claude_code.api_request",
        "event_timestamp": "2026-01-15T10:30:00.000Z",
        "session_id": "sess-123",
        "user_email": "test@example.com",
        "model": "claude-opus-4-6",
        "cost_usd": -1.0,
        "input_tokens": 100,
        "output_tokens": 50,
    }
    is_valid, msg = validate_event(record)
    assert not is_valid
    assert "Negative cost" in msg
    print("PASS: test_validate_negative_cost")


def test_validation_stats():
    stats = ValidationStats()
    stats.record(True)
    stats.record(True)
    stats.record(False, "bad field")
    stats.record(False, "bad field")
    stats.record(False, "other error")

    summary = stats.summary()
    assert summary["total_processed"] == 5
    assert summary["valid"] == 2
    assert summary["invalid"] == 3
    assert summary["validity_rate"] == 0.4
    print("PASS: test_validation_stats")


if __name__ == "__main__":
    test_extract_api_request()
    test_extract_tool_decision()
    test_validate_valid_event()
    test_validate_missing_email()
    test_validate_invalid_event_type()
    test_validate_negative_cost()
    test_validation_stats()
    print("\nAll ingestion tests passed!")
