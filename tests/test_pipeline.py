from __future__ import annotations

from datetime import datetime

import pandas as pd

from network_analytics import pipeline


def _sample_df() -> pd.DataFrame:
    data = {
        "timestamp": pd.date_range(start=datetime(2023, 1, 1), periods=6, freq="min"),
        "device_id": ["edge-01", "edge-01", "edge-02", "edge-02", "edge-03", "edge-03"],
        "region": ["us-east", "us-east", "us-east", "us-west", "us-west", "us-west"],
        "traffic_mbps": [100, 120, 80, 90, 110, 95],
        "latency_ms": [50, 55, 60, 200, 45, 50],
        "packet_loss_pct": [0.5, 0.4, 0.6, 5.0, 0.3, 0.2],
        "cpu_utilization_pct": [70, 72, 65, 95, 60, 58],
    }
    return pd.DataFrame(data)


def test_latency_stats_shape():
    df = _sample_df()
    stats = pipeline.compute_latency_stats(df)
    assert {"region", "device_id", "mean_latency_ms"}.issubset(stats.columns)
    assert len(stats) == df[["region", "device_id"]].drop_duplicates().shape[0]


def test_bottleneck_detection_flags_high_latency():
    df = _sample_df()
    bottlenecks = pipeline.detect_performance_bottlenecks(df)
    assert any(b.device_id == "edge-02" for b in bottlenecks)


def test_reliability_summary_columns():
    df = _sample_df()
    summary = pipeline.summarize_reliability_metrics(df)
    assert {"region", "uptime_score", "avg_cpu_utilization_pct"}.issubset(summary.columns)
