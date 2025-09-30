"""Plotly dashboard generation for network telemetry insights."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from .pipeline import Bottleneck


def _latency_trend_chart(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df,
        x="timestamp",
        y="latency_ms",
        color="region",
        title="Latency trend by region",
        markers=True,
    )
    fig.update_layout(template="plotly_white")
    return fig


def _traffic_heatmap(df: pd.DataFrame) -> go.Figure:
    traffic_summary = (
        df.groupby([pd.Grouper(key="timestamp", freq="1H"), "region"])["traffic_mbps"].sum().reset_index()
    )
    pivot = traffic_summary.pivot(index="timestamp", columns="region", values="traffic_mbps").fillna(0)
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="Viridis",
            colorbar=dict(title="Mbps"),
        )
    )
    fig.update_layout(title="Hourly traffic heatmap", xaxis_title="Region", yaxis_title="Timestamp")
    return fig


def _bottleneck_table(bottlenecks: list[Bottleneck]) -> go.Figure:
    if not bottlenecks:
        return go.Figure()

    df = pd.DataFrame([b.__dict__ for b in bottlenecks])
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=list(df.columns), fill_color="#0d6efd", font=dict(color="white")),
                cells=dict(values=[df[col] for col in df.columns]),
            )
        ]
    )
    fig.update_layout(title="Detected performance bottlenecks")
    return fig


def build_dashboard(
    telemetry: pd.DataFrame,
    latency_stats: pd.DataFrame,
    reliability: pd.DataFrame,
    bottlenecks: list[Bottleneck],
    *,
    output_html: str | Path = "reports/network_performance_dashboard.html",
) -> Path:
    """Build an interactive dashboard summarizing telemetry insights."""
    output_path = Path(output_html)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figures = [
        _latency_trend_chart(telemetry),
        _traffic_heatmap(telemetry),
        px.bar(
            latency_stats,
            x="device_id",
            y="mean_latency_ms",
            color="region",
            title="Average latency by device",
        ),
        px.bar(
            reliability,
            x="region",
            y="uptime_score",
            hover_data=["performance_score", "avg_cpu_utilization_pct"],
            title="Reliability KPIs by region",
        ),
        _bottleneck_table(bottlenecks),
    ]

    with output_path.open("w", encoding="utf-8") as f:
        f.write("<html><head><title>Network Performance Dashboard</title></head><body>\n")
        for fig in figures:
            if fig.data:
                f.write(fig.to_html(full_html=False, include_plotlyjs="cdn"))
        f.write("</body></html>")

    return output_path
