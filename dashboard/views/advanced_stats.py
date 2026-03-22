import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.analytics.advanced_stats import (
    compute_correlation_matrix,
    user_efficiency_scores,
    cohort_analysis,
    practice_comparison,
    model_preference_by_practice,
    prompt_length_analysis,
    session_complexity_distribution,
    daily_efficiency_trend,
)
from dashboard.components.charts import bar_chart, scatter_chart, heatmap_chart, line_chart
from dashboard.components.metrics import render_metric_row, format_number, format_currency


def render():
    st.header("Advanced Statistical Analysis")
    st.caption("Deep statistical insights into Claude Code usage patterns")

    st.subheader("Seniority Cohort Analysis")
    cohort = cohort_analysis()
    if not cohort.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = bar_chart(cohort, "level", "cost_per_user", "Average Cost per User by Level", text_auto=".2f")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(cohort, "level", "sessions_per_user", "Average Sessions per User by Level", text_auto=".1f")
            st.plotly_chart(fig, width="stretch")

        st.dataframe(
            cohort[["level", "users", "requests_per_user", "sessions_per_user",
                    "cost_per_user", "avg_output_tokens", "cache_hit_rate"]],
            width="stretch", hide_index=True,
            column_config={
                "level": "Level",
                "users": "Users",
                "requests_per_user": st.column_config.NumberColumn("Requests/User", format="%.0f"),
                "sessions_per_user": st.column_config.NumberColumn("Sessions/User", format="%.1f"),
                "cost_per_user": st.column_config.NumberColumn("Cost/User ($)", format="%.2f"),
                "avg_output_tokens": st.column_config.NumberColumn("Avg Output Tokens", format="%.0f"),
                "cache_hit_rate": st.column_config.NumberColumn("Cache Hit Rate (%)", format="%.1f"),
            },
        )

    st.divider()

    st.subheader("Engineering Practice Comparison")
    practice = practice_comparison()
    if not practice.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(practice, x="practice", y=["total_cost", "cost_per_user"],
                         barmode="group", title="Cost: Total vs Per-User by Practice",
                         color_discrete_sequence=["#2196F3", "#FF9800"])
            fig.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = bar_chart(practice, "practice", "cache_hit_rate",
                            "Cache Hit Rate by Practice (%)", text_auto=".1f")
            st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("User Efficiency Scores")
    efficiency = user_efficiency_scores()
    if not efficiency.empty:
        render_metric_row([
            {"label": "Avg Tokens/Dollar", "value": format_number(efficiency["tokens_per_dollar"].mean(), 0)},
            {"label": "Avg Cache Hit Rate", "value": f"{efficiency['cache_hit_rate'].mean():.1f}%"},
            {"label": "Avg Output/Request", "value": format_number(efficiency["avg_output_per_request"].mean(), 0)},
            {"label": "Most Efficient User", "value": efficiency.iloc[0]["full_name"]},
        ])

        col1, col2 = st.columns(2)
        with col1:
            fig = scatter_chart(
                efficiency, "total_cost", "tokens_per_dollar",
                "Cost vs Efficiency",
                color="practice", size="sessions",
                labels={"total_cost": "Total Cost ($)", "tokens_per_dollar": "Tokens per Dollar"},
                hover_data=["full_name", "level"],
            )
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = scatter_chart(
                efficiency, "cache_hit_rate", "tokens_per_dollar",
                "Cache Hit Rate vs Efficiency",
                color="practice",
                labels={"cache_hit_rate": "Cache Hit Rate (%)", "tokens_per_dollar": "Tokens/$"},
                hover_data=["full_name", "level"],
            )
            st.plotly_chart(fig, width="stretch")

        st.markdown("**Top 15 Most Efficient Users (Tokens per Dollar)**")
        top = efficiency.head(15).copy()
        st.dataframe(
            top[["full_name", "practice", "level", "tokens_per_dollar", "cache_hit_rate",
                 "total_cost", "requests", "sessions"]],
            width="stretch", hide_index=True,
            column_config={
                "full_name": "Name",
                "practice": "Practice",
                "level": "Level",
                "tokens_per_dollar": st.column_config.NumberColumn("Tokens/$", format="%.0f"),
                "cache_hit_rate": st.column_config.NumberColumn("Cache Hit %", format="%.1f"),
                "total_cost": st.column_config.NumberColumn("Total Cost ($)", format="%.2f"),
                "requests": "Requests",
                "sessions": "Sessions",
            },
        )

    st.divider()

    st.subheader("Model Preferences by Practice")
    model_pref = model_preference_by_practice()
    if not model_pref.empty:
        fig = px.bar(model_pref, x="practice", y="pct_of_practice", color="model",
                     title="Model Usage Share by Practice (%)",
                     labels={"pct_of_practice": "% of Requests", "practice": "Practice"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(template="plotly_white", height=400, barmode="stack")
        st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Session Complexity Distribution")
    complexity = session_complexity_distribution()
    if not complexity.empty:
        complexity_counts = complexity["complexity"].value_counts().reset_index()
        complexity_counts.columns = ["complexity", "count"]
        order = ["Simple", "Moderate", "Complex", "Very Complex"]
        complexity_counts["complexity"] = pd.Categorical(complexity_counts["complexity"], categories=order, ordered=True)
        complexity_counts = complexity_counts.sort_values("complexity")

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(complexity_counts, names="complexity", values="count",
                         title="Session Complexity Distribution",
                         color_discrete_sequence=["#4CAF50", "#2196F3", "#FF9800", "#F44336"],
                         hole=0.4)
            fig.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig, width="stretch")

        with col2:
            avg_by_complexity = complexity.groupby("complexity").agg(
                avg_cost=("session_cost", "mean"),
                avg_turns=("turns", "mean"),
                avg_tools=("tool_uses", "mean"),
            ).reset_index()
            avg_by_complexity["complexity"] = pd.Categorical(avg_by_complexity["complexity"], categories=order, ordered=True)
            avg_by_complexity = avg_by_complexity.sort_values("complexity")

            fig = px.bar(avg_by_complexity, x="complexity", y="avg_cost",
                         title="Average Session Cost by Complexity",
                         text_auto=".3f",
                         color_discrete_sequence=["#2196F3"])
            fig.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Correlation Matrix")
    corr = compute_correlation_matrix()
    if not corr.empty:
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                        title="Correlation Between User-Level Metrics")
        fig.update_layout(template="plotly_white", height=500)
        st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Efficiency Trends Over Time")
    eff_trend = daily_efficiency_trend()
    if not eff_trend.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = line_chart(eff_trend, "date", "tokens_per_dollar",
                             "Tokens per Dollar Over Time")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = line_chart(eff_trend, "date", "cache_hit_rate",
                             "Cache Hit Rate Over Time (%)")
            st.plotly_chart(fig, width="stretch")
