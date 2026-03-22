import time
import pandas as pd
from datetime import datetime, timedelta
from src.database.queries import query_to_df


class TelemetryStream:

    def __init__(self, speed_multiplier: float = 60.0, window_minutes: int = 5):
        self.speed_multiplier = speed_multiplier
        self.window_minutes = window_minutes
        self._events_buffer = []
        self._current_idx = 0
        self._start_real_time = None
        self._start_sim_time = None
        self._all_events = None

    def initialize(self):
        sql = """
            SELECT event_timestamp, session_id, user_email, model,
                   input_tokens, output_tokens, cost_usd, duration_ms
            FROM api_requests
            ORDER BY event_timestamp
            LIMIT 10000
        """
        self._all_events = query_to_df(sql)
        self._all_events["event_timestamp"] = pd.to_datetime(self._all_events["event_timestamp"])
        self._current_idx = 0
        self._start_real_time = time.time()
        self._start_sim_time = self._all_events["event_timestamp"].iloc[0]
        return len(self._all_events)

    def get_current_sim_time(self) -> datetime:
        elapsed_real = time.time() - self._start_real_time
        elapsed_sim = timedelta(minutes=elapsed_real * self.speed_multiplier)
        return self._start_sim_time + elapsed_sim

    def fetch_new_events(self) -> pd.DataFrame:
        if self._all_events is None or self._current_idx >= len(self._all_events):
            return pd.DataFrame()

        current_sim = self.get_current_sim_time()
        mask = self._all_events["event_timestamp"].iloc[self._current_idx:] <= current_sim
        new_count = mask.sum()

        if new_count == 0:
            return pd.DataFrame()

        start = self._current_idx
        self._current_idx += new_count
        new_events = self._all_events.iloc[start:self._current_idx].copy()
        self._events_buffer.extend(new_events.to_dict("records"))

        return new_events

    def get_rolling_metrics(self) -> dict:
        if not self._events_buffer:
            return {
                "events_in_window": 0,
                "total_cost": 0.0,
                "avg_cost": 0.0,
                "total_tokens": 0,
                "unique_users": 0,
                "unique_sessions": 0,
                "requests_per_minute": 0.0,
            }

        current_sim = self.get_current_sim_time()
        window_start = current_sim - timedelta(minutes=self.window_minutes)

        window_events = [
            e for e in self._events_buffer
            if e["event_timestamp"] >= window_start
        ]

        self._events_buffer = window_events

        if not window_events:
            return {
                "events_in_window": 0,
                "total_cost": 0.0,
                "avg_cost": 0.0,
                "total_tokens": 0,
                "unique_users": 0,
                "unique_sessions": 0,
                "requests_per_minute": 0.0,
            }

        df = pd.DataFrame(window_events)
        total_cost = df["cost_usd"].sum()

        return {
            "events_in_window": len(df),
            "total_cost": round(total_cost, 4),
            "avg_cost": round(total_cost / len(df), 6),
            "total_tokens": int(df["input_tokens"].sum() + df["output_tokens"].sum()),
            "unique_users": df["user_email"].nunique(),
            "unique_sessions": df["session_id"].nunique(),
            "requests_per_minute": round(len(df) / self.window_minutes, 1),
        }

    @property
    def progress(self) -> float:
        if self._all_events is None or len(self._all_events) == 0:
            return 0.0
        return self._current_idx / len(self._all_events)

    @property
    def is_complete(self) -> bool:
        return self._all_events is not None and self._current_idx >= len(self._all_events)
