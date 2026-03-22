import streamlit as st
from src.database.queries import get_summary_stats
from src.analytics.token_usage import daily_token_consumption, hourly_usage_pattern
from src.analytics.session_patterns import daily_active_users
from src.analytics.tool_usage import error_analysis
from dashboard.components.metrics import render_metric_row, format_number, format_currency
from dashboard.components.charts import line_chart, bar_chart


def render():
    st.header("Overview")
    st.caption("High-level view of Claude Code usage across the organization")

    stats = get_summary_stats()

    render_metric_row([
        {"label": "Total API Requests", "value": format_number(stats["total_api_requests"])},
        {"label": "Total Sessions", "value": format_number(stats["total_sessions"])},
        {"label": "Active Users", "value": str(stats["total_users"])},
        {"label": "Total Cost", "value": format_currency(stats["total_cost"])},
    ])

    render_metric_row([
        {"label": "Total Tokens", "value": format_number(stats["total_tokens"])},
        {"label": "User Prompts", "value": format_number(stats["total_prompts"])},
        {"label": "Tool Executions", "value": format_number(stats["total_tool_uses"])},
        {"label": "API Errors", "value": format_number(stats["total_errors"])},
    ])

    st.divider()

    daily = daily_token_consumption()
    if not daily.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = line_chart(daily, "date", "total_cost", "Daily Cost (USD)", labels={"total_cost": "Cost ($)"})
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = line_chart(daily, "date", "request_count", "Daily API Requests", labels={"request_count": "Requests"})
            st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        dau = daily_active_users()
        if not dau.empty:
            fig = line_chart(dau, "date", "active_users", "Daily Active Users")
            st.plotly_chart(fig, width="stretch")

    with col2:
        hourly = hourly_usage_pattern()
        if not hourly.empty:
            fig = bar_chart(hourly, "hour", "request_count", "Usage by Hour of Day", labels={"hour": "Hour (UTC)", "request_count": "Requests"})
            st.plotly_chart(fig, width="stretch")

    errors = error_analysis()
    if not errors.empty:
        st.subheader("API Errors")
        st.dataframe(
            errors[["error", "status_code", "occurrence_count", "affected_users"]],
            width="stretch", hide_index=True,
        )
