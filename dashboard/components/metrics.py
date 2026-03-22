
import streamlit as st


def render_metric_row(metrics: list[dict]):
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            kwargs = {"label": metric["label"], "value": metric["value"]}
            if "delta" in metric:
                kwargs["delta"] = metric["delta"]
            if "delta_color" in metric:
                kwargs["delta_color"] = metric["delta_color"]
            st.metric(**kwargs)


def format_number(n, decimals=0):
    if n is None:
        return "N/A"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.{decimals}f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.{decimals}f}K"
    if isinstance(n, float):
        return f"{n:.{max(decimals, 2)}f}"
    return str(n)


def format_currency(n):
    if n is None:
        return "$0.00"
    return f"${n:,.2f}"


def format_percentage(n, decimals=1):
    if n is None:
        return "0%"
    return f"{n:.{decimals}f}%"
