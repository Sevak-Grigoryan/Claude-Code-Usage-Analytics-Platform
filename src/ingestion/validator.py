import logging
from datetime import datetime

logger = logging.getLogger(__name__)

REQUIRED_BASE_FIELDS = ["event_type", "event_timestamp", "session_id", "user_email"]

VALID_EVENT_TYPES = {
    "claude_code.api_request",
    "claude_code.tool_decision",
    "claude_code.tool_result",
    "claude_code.user_prompt",
    "claude_code.api_error",
}


def validate_event(record: dict) -> tuple[bool, str]:
    for field in REQUIRED_BASE_FIELDS:
        if not record.get(field):
            return False, f"Missing required field: {field}"

    if record["event_type"] not in VALID_EVENT_TYPES:
        return False, f"Unknown event type: {record['event_type']}"

    ts = record["event_timestamp"]
    try:
        datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False, f"Invalid timestamp format: {ts}"

    event_type = record["event_type"]

    if event_type == "claude_code.api_request":
        if not record.get("model"):
            return False, "API request missing model"
        if record.get("cost_usd", 0) < 0:
            return False, "Negative cost"
        if record.get("input_tokens", 0) < 0 or record.get("output_tokens", 0) < 0:
            return False, "Negative token count"

    elif event_type == "claude_code.tool_decision":
        if not record.get("tool_name"):
            return False, "Tool decision missing tool_name"
        if record.get("decision") not in ("accept", "reject"):
            return False, f"Invalid decision: {record.get('decision')}"

    elif event_type == "claude_code.tool_result":
        if not record.get("tool_name"):
            return False, "Tool result missing tool_name"

    elif event_type == "claude_code.user_prompt":
        if record.get("prompt_length", 0) < 0:
            return False, "Negative prompt length"

    elif event_type == "claude_code.api_error":
        if not record.get("error"):
            return False, "API error missing error message"

    return True, ""


class ValidationStats:

    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.errors_by_type = {}

    def record(self, is_valid: bool, error_msg: str = ""):
        self.total += 1
        if is_valid:
            self.valid += 1
        else:
            self.invalid += 1
            self.errors_by_type[error_msg] = self.errors_by_type.get(error_msg, 0) + 1

    def summary(self) -> dict:
        return {
            "total_processed": self.total,
            "valid": self.valid,
            "invalid": self.invalid,
            "validity_rate": self.valid / self.total if self.total > 0 else 0,
            "top_errors": sorted(
                self.errors_by_type.items(), key=lambda x: -x[1]
            )[:10],
        }
