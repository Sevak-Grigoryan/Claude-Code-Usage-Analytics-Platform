import streamlit as st
import pandas as pd
from src.analytics.session_patterns import (
    sessions_per_user,
    daily_active_users,
    session_duration_distribution,
    weekly_engagement,
)
from src.analytics.token_usage import cost_by_user
from dashboard.components.charts import line_chart, bar_chart, scatter_chart, pie_chart
from dashboard.components.metrics import render_metric_row, format_number, format_currency


def render():
    st.header("User & Session Analysis")
    st.caption("Understanding developer engagement and behavior patterns")

    user_sessions = sessions_per_user()
    if not user_sessions.empty:
        render_metric_row([
            {"label": "Total Users", "value": str(len(user_sessions))},
            {"label": "Avg Sessions/User", "value": f"{user_sessions['session_count'].mean():.1f}"},
            {"label": "Avg Requests/User", "value": format_number(user_sessions['total_requests'].mean(), 0)},
            {"label": "Avg Cost/User", "value": format_currency(user_sessions['total_cost'].mean())},
        ])

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            practice_sessions = user_sessions.groupby("practice").agg(
                total_sessions=("session_count", "sum"),
                total_users=("user_email", "count"),
            ).reset_index()
            fig = bar_chart(practice_sessions, "practice", "total_sessions", "Sessions by Practice", text_auto=True)
            st.plotly_chart(fig, width="stretch")

        with col2:
            location_users = user_sessions.groupby("location")["user_email"].count().reset_index()
            location_users.columns = ["location", "user_count"]
            fig = pie_chart(location_users, "location", "user_count", "Users by Location")
            st.plotly_chart(fig, width="stretch")

        st.divider()

        st.subheader("User Engagement Map")
        user_cost = cost_by_user()
        if not user_cost.empty:
            fig = scatter_chart(
                user_cost, "session_count", "total_cost",
                "Sessions vs Cost per User",
                color="practice", size="request_count",
                labels={"session_count": "Sessions", "total_cost": "Total Cost ($)", "request_count": "Requests"},
                hover_data=["full_name", "level"],
            )
            st.plotly_chart(fig, width="stretch")

    st.divider()

    weekly = weekly_engagement()
    if not weekly.empty:
        st.subheader("Weekly Engagement Trends")
        col1, col2 = st.columns(2)
        with col1:
            fig = line_chart(weekly, "week", "active_users", "Weekly Active Users")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = line_chart(weekly, "week", "sessions", "Weekly Sessions")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    durations = session_duration_distribution()
    if not durations.empty and "duration_minutes" in durations.columns:
        st.subheader("Session Duration Distribution")
        capped = durations[durations["duration_minutes"] <= 120].copy()
        if not capped.empty:
            import plotly.express as px
            fig = px.histogram(
                capped, x="duration_minutes", nbins=50,
                title="Session Duration Distribution (capped at 2 hours)",
                labels={"duration_minutes": "Duration (minutes)"},
                color_discrete_sequence=["#2196F3"],
            )
            fig.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig, width="stretch")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Median Duration", f"{durations['duration_minutes'].median():.1f} min")
        with col2:
            st.metric("Mean Duration", f"{durations['duration_minutes'].mean():.1f} min")
        with col3:
            st.metric("P90 Duration", f"{durations['duration_minutes'].quantile(0.9):.1f} min")
        with col4:
            st.metric("Max Duration", f"{durations['duration_minutes'].max():.1f} min")

    st.divider()

    dau = daily_active_users()
    if not dau.empty:
        st.subheader("Daily Active Users")
        fig = line_chart(dau, "date", "active_users", "Daily Active Users Over Time")
        st.plotly_chart(fig, width="stretch")

    if not user_sessions.empty:
        st.subheader("User Leaderboard")
        display = user_sessions.head(20).copy()
        display["total_cost"] = display["total_cost"].round(2)
        st.dataframe(
            display[["full_name", "practice", "level", "location", "session_count", "total_requests", "total_cost"]],
            width="stretch",
            hide_index=True,
            column_config={
                "full_name": "Name",
                "practice": "Practice",
                "level": "Level",
                "location": "Location",
                "session_count": "Sessions",
                "total_requests": "Requests",
                "total_cost": st.column_config.NumberColumn("Cost ($)", format="%.2f"),
            },
        )
