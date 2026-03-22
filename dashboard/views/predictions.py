import streamlit as st
from src.analytics.forecasting import (
    forecast_daily_cost,
    forecast_token_usage,
    detect_anomalies,
    usage_growth_rate,
)
from dashboard.components.charts import forecast_chart, anomaly_chart
from dashboard.components.metrics import render_metric_row, format_currency, format_percentage


def render():
    st.header("Predictive Analytics")
    st.caption("ML-powered forecasting and anomaly detection")

    growth = usage_growth_rate()
    if growth:
        st.subheader("Week-over-Week Growth")
        render_metric_row([
            {
                "label": "Cost Growth",
                "value": format_percentage(growth.get("cost_growth_pct", 0)),
                "delta": f"{growth.get('cost_growth_pct', 0):.1f}%",
                "delta_color": "inverse",
            },
            {
                "label": "Token Growth",
                "value": format_percentage(growth.get("token_growth_pct", 0)),
                "delta": f"{growth.get('token_growth_pct', 0):.1f}%",
            },
            {
                "label": "Request Growth",
                "value": format_percentage(growth.get("request_growth_pct", 0)),
                "delta": f"{growth.get('request_growth_pct', 0):.1f}%",
            },
            {
                "label": "Current Week Cost",
                "value": format_currency(growth.get("current_week_cost", 0)),
            },
        ])

    st.divider()

    st.subheader("Cost Forecast (14-day)")
    days_ahead = st.slider("Forecast horizon (days)", 7, 30, 14)

    cost_forecast = forecast_daily_cost(days_ahead=days_ahead)
    if not cost_forecast.empty:
        r_squared = cost_forecast["r_squared"].iloc[0] if "r_squared" in cost_forecast.columns else 0
        slope = cost_forecast["trend_slope"].iloc[0] if "trend_slope" in cost_forecast.columns else 0

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Trend (daily cost change)", format_currency(slope))
        with col2:
            st.metric("Model R-squared", f"{r_squared:.4f}")

        fig = forecast_chart(
            cost_forecast, "date", "total_cost", "predicted_cost",
            "Daily Cost - Actual vs Forecast",
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Token Usage Forecast")
    token_forecast = forecast_token_usage(days_ahead=days_ahead)
    if not token_forecast.empty:
        fig = forecast_chart(
            token_forecast, "date", "total_tokens", "predicted_tokens",
            "Daily Token Usage - Actual vs Forecast",
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Anomaly Detection")
    st.caption("Using Isolation Forest to detect unusual usage patterns")

    contamination = st.slider("Anomaly sensitivity", 0.01, 0.15, 0.05, 0.01,
                              help="Lower = fewer anomalies detected (stricter)")

    anomalies = detect_anomalies(contamination=contamination)
    if not anomalies.empty:
        n_anomalies = anomalies["is_anomaly"].sum()
        st.info(f"Detected **{n_anomalies}** anomalous days out of {len(anomalies)} total days")

        col1, col2 = st.columns(2)
        with col1:
            fig = anomaly_chart(anomalies, "date", "total_cost", "is_anomaly", "Cost Anomalies")
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = anomaly_chart(anomalies, "date", "request_count", "is_anomaly", "Request Count Anomalies")
            st.plotly_chart(fig, width="stretch")

        anomaly_days = anomalies[anomalies["is_anomaly"]].copy()
        if not anomaly_days.empty:
            st.subheader("Anomalous Days Detail")
            display = anomaly_days[["date", "total_cost", "total_tokens", "request_count", "anomaly_score"]].copy()
            display["total_cost"] = display["total_cost"].round(2)
            display["anomaly_score"] = display["anomaly_score"].round(4)
            display.columns = ["Date", "Cost ($)", "Tokens", "Requests", "Anomaly Score"]
            st.dataframe(display, width="stretch", hide_index=True)
