
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

COLORS = px.colors.qualitative.Set2


def line_chart(df, x, y, title, color=None, labels=None):
    fig = px.line(df, x=x, y=y, title=title, color=color, labels=labels, color_discrete_sequence=COLORS)
    fig.update_layout(template="plotly_white", height=400)
    return fig


def bar_chart(df, x, y, title, color=None, orientation="v", labels=None, text_auto=False):
    fig = px.bar(
        df, x=x, y=y, title=title, color=color,
        orientation=orientation, labels=labels,
        color_discrete_sequence=COLORS, text_auto=text_auto,
    )
    fig.update_layout(template="plotly_white", height=400)
    return fig


def pie_chart(df, names, values, title, hole=0.4):
    fig = px.pie(df, names=names, values=values, title=title, hole=hole, color_discrete_sequence=COLORS)
    fig.update_layout(template="plotly_white", height=400)
    return fig


def heatmap_chart(df, x, y, z, title, color_scale="Blues"):
    pivot = df.pivot_table(values=z, index=y, columns=x, aggfunc="sum", fill_value=0)
    fig = px.imshow(
        pivot, title=title, aspect="auto", color_continuous_scale=color_scale,
        labels=dict(color=z),
    )
    fig.update_layout(template="plotly_white", height=450)
    return fig


def scatter_chart(df, x, y, title, color=None, size=None, labels=None, hover_data=None):
    fig = px.scatter(
        df, x=x, y=y, title=title, color=color, size=size,
        labels=labels, hover_data=hover_data, color_discrete_sequence=COLORS,
    )
    fig.update_layout(template="plotly_white", height=400)
    return fig


def forecast_chart(df, date_col, actual_col, predicted_col, title, forecast_flag_col="is_forecast"):
    fig = go.Figure()

    historical = df[~df[forecast_flag_col]]
    forecast = df[df[forecast_flag_col]]

    fig.add_trace(go.Scatter(
        x=historical[date_col], y=historical[actual_col],
        mode="lines+markers", name="Actual",
        line=dict(color="#2196F3", width=2),
        marker=dict(size=4),
    ))

    fig.add_trace(go.Scatter(
        x=historical[date_col], y=historical[predicted_col],
        mode="lines", name="Trend",
        line=dict(color="#FF9800", width=2, dash="dash"),
    ))

    if not forecast.empty:
        fig.add_trace(go.Scatter(
            x=forecast[date_col], y=forecast[predicted_col],
            mode="lines+markers", name="Forecast",
            line=dict(color="#4CAF50", width=2, dash="dot"),
            marker=dict(size=6, symbol="diamond"),
        ))

    fig.update_layout(
        title=title,
        template="plotly_white",
        height=450,
        xaxis_title="Date",
        yaxis_title="Value",
    )
    return fig


def anomaly_chart(df, date_col, value_col, anomaly_col, title):
    fig = go.Figure()

    normal = df[~df[anomaly_col]]
    anomalies = df[df[anomaly_col]]

    fig.add_trace(go.Scatter(
        x=normal[date_col], y=normal[value_col],
        mode="lines+markers", name="Normal",
        line=dict(color="#2196F3", width=2),
        marker=dict(size=4),
    ))

    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies[date_col], y=anomalies[value_col],
            mode="markers", name="Anomaly",
            marker=dict(color="#F44336", size=12, symbol="x", line=dict(width=2)),
        ))

    fig.update_layout(title=title, template="plotly_white", height=400)
    return fig
