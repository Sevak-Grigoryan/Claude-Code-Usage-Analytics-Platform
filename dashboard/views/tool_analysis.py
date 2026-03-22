import streamlit as st
import pandas as pd
from src.analytics.tool_usage import (
    tool_usage_summary,
    tool_decision_summary,
    tool_usage_by_practice,
    tool_usage_trends,
    tool_failure_analysis,
    error_analysis,
    daily_error_trend,
)
from dashboard.components.charts import bar_chart, pie_chart, line_chart, heatmap_chart
from dashboard.components.metrics import render_metric_row, format_number, format_percentage


def render():
    st.header("Tool & Error Analysis")
    st.caption("How developers use Claude Code tools and where errors occur")

    tool_df = tool_usage_summary()
    if not tool_df.empty:
        total_uses = tool_df["total_uses"].sum()
        total_failures = tool_df["failures"].sum()
        overall_success = ((total_uses - total_failures) / total_uses * 100) if total_uses > 0 else 0

        render_metric_row([
            {"label": "Total Tool Executions", "value": format_number(total_uses)},
            {"label": "Unique Tools Used", "value": str(len(tool_df))},
            {"label": "Overall Success Rate", "value": format_percentage(overall_success)},
            {"label": "Total Failures", "value": format_number(total_failures)},
        ])

        col1, col2 = st.columns(2)
        with col1:
            fig = bar_chart(tool_df, "tool_name", "total_uses", "Tool Usage Frequency", text_auto=True)
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(tool_df, "tool_name", "success_rate", "Success Rate by Tool (%)", text_auto=".1f")
            st.plotly_chart(fig, width="stretch")

        st.subheader("Tool Performance")
        display = tool_df.copy()
        display["avg_duration_ms"] = display["avg_duration_ms"].round(0)
        display.columns = ["Tool", "Total Uses", "Successes", "Failures", "Success Rate (%)", "Avg Duration (ms)", "Total Duration (ms)"]
        st.dataframe(display, width="stretch", hide_index=True)

    st.divider()

    decision_df = tool_decision_summary()
    if not decision_df.empty:
        st.subheader("Tool Approval Decisions")
        col1, col2 = st.columns(2)
        with col1:
            fig = bar_chart(decision_df, "tool_name", "accept_rate", "Acceptance Rate by Tool (%)", text_auto=".1f")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = pie_chart(
                pd.DataFrame({
                    "Decision": ["Accepted", "Rejected"],
                    "Count": [decision_df["accepted"].sum(), decision_df["rejected"].sum()],
                }),
                "Decision", "Count", "Overall Accept vs Reject",
            )
            st.plotly_chart(fig, width="stretch")

    st.divider()

    practice_df = tool_usage_by_practice()
    if not practice_df.empty:
        st.subheader("Tool Preferences by Practice")
        fig = heatmap_chart(practice_df, "tool_name", "practice", "use_count", "Tool Usage Heatmap (Practice x Tool)")
        st.plotly_chart(fig, width="stretch")

    st.divider()

    trends = tool_usage_trends()
    if not trends.empty:
        st.subheader("Tool Usage Trends")
        top_tools = tool_df["tool_name"].head(5).tolist() if not tool_df.empty else []
        filtered = trends[trends["tool_name"].isin(top_tools)]
        if not filtered.empty:
            fig = line_chart(filtered, "date", "use_count", "Daily Usage - Top 5 Tools", color="tool_name")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("API Error Analysis")
    col1, col2 = st.columns(2)

    with col1:
        errors = error_analysis()
        if not errors.empty:
            fig = bar_chart(errors, "error", "occurrence_count", "Error Types", text_auto=True)
            fig.update_layout(xaxis_tickangle=-30, height=450)
            st.plotly_chart(fig, width="stretch")

    with col2:
        error_trend = daily_error_trend()
        if not error_trend.empty:
            fig = line_chart(error_trend, "date", "error_count", "Daily Error Count")
            st.plotly_chart(fig, width="stretch")
