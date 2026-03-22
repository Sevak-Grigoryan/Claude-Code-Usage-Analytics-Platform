import streamlit as st
from src.analytics.token_usage import (
    daily_token_consumption,
    tokens_by_model,
    tokens_by_practice,
    tokens_by_level,
    cost_by_user,
    daily_cost_by_practice,
)
from dashboard.components.charts import line_chart, bar_chart, pie_chart, heatmap_chart
from dashboard.components.metrics import render_metric_row, format_number, format_currency


def render():
    st.header("Token & Cost Analysis")
    st.caption("Deep dive into token consumption patterns and cost drivers")

    model_df = tokens_by_model()
    if not model_df.empty:
        st.subheader("Cost by Model")
        render_metric_row([
            {"label": m, "value": format_currency(c)}
            for m, c in zip(model_df["model"].head(5), model_df["total_cost"].head(5))
        ])

        col1, col2 = st.columns(2)
        with col1:
            fig = pie_chart(model_df, "model", "total_cost", "Cost Distribution by Model")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(model_df, "model", "request_count", "Requests by Model", text_auto=True)
            st.plotly_chart(fig, width="stretch")

        st.subheader("Model Performance")
        display_df = model_df[["model", "request_count", "total_cost", "avg_cost_per_request", "avg_duration_ms", "total_cache_read"]].copy()
        display_df.columns = ["Model", "Requests", "Total Cost ($)", "Avg Cost/Req ($)", "Avg Duration (ms)", "Cache Reads"]
        display_df["Total Cost ($)"] = display_df["Total Cost ($)"].round(2)
        display_df["Avg Cost/Req ($)"] = display_df["Avg Cost/Req ($)"].round(4)
        display_df["Avg Duration (ms)"] = display_df["Avg Duration (ms)"].round(0)
        st.dataframe(display_df, width="stretch", hide_index=True)

    st.divider()

    practice_df = tokens_by_practice()
    if not practice_df.empty:
        st.subheader("Usage by Engineering Practice")
        col1, col2 = st.columns(2)
        with col1:
            fig = bar_chart(practice_df, "practice", "total_cost", "Total Cost by Practice", text_auto=".2f")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(practice_df, "practice", "avg_cost_per_request", "Avg Cost per Request by Practice", text_auto=".4f")
            st.plotly_chart(fig, width="stretch")

    level_df = tokens_by_level()
    if not level_df.empty:
        st.subheader("Usage by Seniority Level")
        col1, col2 = st.columns(2)
        with col1:
            fig = bar_chart(level_df, "level", "total_cost", "Total Cost by Level", text_auto=".2f")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(level_df, "level", "total_tokens", "Total Tokens by Level")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    daily_practice = daily_cost_by_practice()
    if not daily_practice.empty:
        st.subheader("Daily Cost Trends by Practice")
        fig = line_chart(daily_practice, "date", "total_cost", "Cost Over Time by Practice", color="practice")
        st.plotly_chart(fig, width="stretch")

    daily = daily_token_consumption()
    if not daily.empty:
        st.subheader("Daily Token Consumption")
        col1, col2 = st.columns(2)
        with col1:
            fig = line_chart(daily, "date", "input_tokens", "Input Tokens Over Time")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = line_chart(daily, "date", "output_tokens", "Output Tokens Over Time")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    users = cost_by_user()
    if not users.empty:
        st.subheader("Top Users by Cost")
        top_20 = users.head(20).copy()
        top_20["total_cost"] = top_20["total_cost"].round(2)
        top_20["avg_duration_ms"] = top_20["avg_duration_ms"].round(0)
        st.dataframe(
            top_20[["full_name", "practice", "level", "total_cost", "request_count", "session_count"]],
            width="stretch", hide_index=True,
            column_config={
                "full_name": "Name",
                "practice": "Practice",
                "level": "Level",
                "total_cost": st.column_config.NumberColumn("Total Cost ($)", format="%.2f"),
                "request_count": "Requests",
                "session_count": "Sessions",
            },
        )
