import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.analytics.realtime import TelemetryStream
from dashboard.components.metrics import format_number, format_currency


def render():
    st.header("Real-Time Streaming Simulation")
    st.caption("Demonstrates how the platform handles live telemetry data")

    st.info(
        "This page simulates real-time ingestion by replaying historical events at "
        "accelerated speed. It demonstrates how the system could process a live data stream "
        "with rolling metrics computation."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        speed = st.selectbox("Replay Speed", [30, 60, 120, 300], index=1,
                             format_func=lambda x: f"{x}x (1 sec = {x} min of data)")
    with col2:
        window = st.selectbox("Rolling Window", [5, 10, 30, 60], index=1,
                              format_func=lambda x: f"{x} minutes")
    with col3:
        max_ticks = st.selectbox("Simulation Duration", [10, 20, 30, 50], index=1,
                                 format_func=lambda x: f"{x} ticks")

    if st.button("Start Streaming Simulation", type="primary"):
        stream = TelemetryStream(speed_multiplier=speed, window_minutes=window)
        total_events = stream.initialize()
        st.write(f"Loaded **{total_events:,}** events for replay")

        progress_bar = st.progress(0)
        metrics_placeholder = st.empty()
        chart_placeholder = st.empty()
        events_placeholder = st.empty()

        cost_history = []
        token_history = []
        user_history = []
        timestamps = []

        tick = 0
        while not stream.is_complete and tick < max_ticks:
            tick += 1
            new_events = stream.fetch_new_events()
            metrics = stream.get_rolling_metrics()
            sim_time = stream.get_current_sim_time()

            progress_bar.progress(min(stream.progress, 1.0))

            with metrics_placeholder.container():
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Events in Window", format_number(metrics["events_in_window"]))
                c2.metric("Window Cost", format_currency(metrics["total_cost"]))
                c3.metric("Tokens", format_number(metrics["total_tokens"]))
                c4.metric("Active Users", metrics["unique_users"])
                c5.metric("Req/min", metrics["requests_per_minute"])

            timestamps.append(sim_time.strftime("%H:%M"))
            cost_history.append(metrics["total_cost"])
            token_history.append(metrics["total_tokens"])
            user_history.append(metrics["unique_users"])

            with chart_placeholder.container():
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=cost_history,
                        mode="lines+markers", name="Cost ($)",
                        line=dict(color="#2196F3", width=2),
                    ))
                    fig.update_layout(
                        title="Rolling Window Cost",
                        template="plotly_white", height=300,
                        xaxis_title="Sim Time", yaxis_title="Cost ($)",
                    )
                    st.plotly_chart(fig, width="stretch")

                with col2:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=timestamps, y=user_history,
                        name="Active Users",
                        marker_color="#4CAF50",
                    ))
                    fig.update_layout(
                        title="Active Users in Window",
                        template="plotly_white", height=300,
                        xaxis_title="Sim Time", yaxis_title="Users",
                    )
                    st.plotly_chart(fig, width="stretch")

            if not new_events.empty:
                with events_placeholder.container():
                    st.markdown(f"**Latest events** (tick {tick}, sim time: {sim_time.strftime('%Y-%m-%d %H:%M')})")
                    display = new_events.tail(5)[["event_timestamp", "user_email", "model", "cost_usd"]].copy()
                    display["cost_usd"] = display["cost_usd"].round(4)
                    display.columns = ["Timestamp", "User", "Model", "Cost ($)"]
                    st.dataframe(display, width="stretch", hide_index=True)

            time.sleep(1)

        progress_bar.progress(1.0)
        st.success(f"Simulation complete! Replayed {stream._current_idx:,} events in {tick} ticks.")

    st.divider()
    st.subheader("How Real-Time Streaming Would Work in Production")

    st.markdown("""
    In a production environment, this simulation would be replaced by:

    | Component | Technology | Purpose |
    |-----------|------------|---------|
    | **Ingestion** | Apache Kafka / AWS Kinesis | Accept telemetry events in real-time |
    | **Processing** | Apache Flink / Spark Streaming | Windowed aggregations, anomaly detection |
    | **Storage** | TimescaleDB / ClickHouse | Time-series optimized storage |
    | **Dashboard** | WebSocket-powered Streamlit / Grafana | Live-updating visualizations |
    | **Alerting** | PagerDuty / Slack integration | Anomaly-triggered notifications |

    **Key design decisions for real-time:**
    - Use **tumbling windows** (e.g., 5-minute) for metric aggregation to bound memory
    - Implement **watermarking** to handle late-arriving events
    - Use **approximate algorithms** (HyperLogLog for unique users, Count-Min Sketch for frequencies) for scalability
    - Keep **hot/warm/cold storage tiers** - recent data in memory, older in DB, archive in S3
    """)
