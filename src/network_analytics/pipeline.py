"""Network telemetry analytics pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


@dataclass
class Bottleneck:
    """Representation of a performance bottleneck."""

    device_id: str
    region: str
    metric: str
    severity: float
    description: str


def load_telemetry(csv_path: str | Path) -> pd.DataFrame:
    """Load telemetry data into a DataFrame."""
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df.sort_values("timestamp", inplace=True)
    return df


def compute_latency_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute descriptive statistics for latency by region and device."""
    latency_summary = (
        df.groupby(["region", "device_id"])["latency_ms"]
        .agg(["mean", "median", "max", "std", "count"])
        .rename(
            columns={
                "mean": "mean_latency_ms",
                "median": "median_latency_ms",
                "max": "max_latency_ms",
                "std": "latency_std_ms",
                "count": "samples",
            }
        )
        .reset_index()
    )
    return latency_summary


def detect_performance_bottlenecks(
    df: pd.DataFrame,
    *,
    latency_threshold_ms: float = 120.0,
    packet_loss_threshold_pct: float = 2.0,
    cpu_threshold_pct: float = 90.0,
) -> list[Bottleneck]:
    """Detect high latency and loss events using statistical thresholds."""
    bottlenecks: list[Bottleneck] = []

    latency_std = df["latency_ms"].std(ddof=0) or 1.0
    loss_std = df["packet_loss_pct"].std(ddof=0) or 1.0
    z_latency = (df["latency_ms"] - df["latency_ms"].mean()) / latency_std
    z_loss = (df["packet_loss_pct"] - df["packet_loss_pct"].mean()) / loss_std

    anomaly_mask = (
        (df["latency_ms"] > latency_threshold_ms)
        | (df["packet_loss_pct"] > packet_loss_threshold_pct)
        | (df["cpu_utilization_pct"] > cpu_threshold_pct)
        | (z_latency > 2.5)
        | (z_loss > 2.5)
    )

    for record in df.loc[anomaly_mask].itertuples():
        severity = max(
            (record.latency_ms - latency_threshold_ms) / latency_threshold_ms,
            (record.packet_loss_pct - packet_loss_threshold_pct) / max(packet_loss_threshold_pct, 1e-6),
            (record.cpu_utilization_pct - cpu_threshold_pct) / cpu_threshold_pct,
        )
        bottlenecks.append(
            Bottleneck(
                device_id=record.device_id,
                region=record.region,
                metric="latency/packet_loss/cpu",
                severity=round(max(severity, 0.0), 2),
                description=(
                    "High latency and loss event observed"
                    f" at {record.timestamp} (latency {record.latency_ms} ms,"
                    f" loss {record.packet_loss_pct}%)."
                ),
            )
        )

    return bottlenecks


def summarize_reliability_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize reliability KPIs such as availability and error rate."""
    df = df.copy()
    df["uptime_score"] = 100 - df["packet_loss_pct"].clip(upper=5)
    df["performance_score"] = 100 - df["latency_ms"].clip(upper=200) / 2

    summary = (
        df.groupby("region")[
            ["uptime_score", "performance_score", "cpu_utilization_pct"]
        ]
        .mean()
        .rename(columns={"cpu_utilization_pct": "avg_cpu_utilization_pct"})
        .reset_index()
    )
    return summary


def run_pipeline(csv_path: str | Path) -> dict[str, pd.DataFrame | list[Bottleneck]]:
    df = load_telemetry(csv_path)
    latency_stats = compute_latency_stats(df)
    reliability = summarize_reliability_metrics(df)
    bottlenecks = detect_performance_bottlenecks(df)
    return {
        "telemetry": df,
        "latency_stats": latency_stats,
        "reliability": reliability,
        "bottlenecks": bottlenecks,
    }


def export_bottlenecks(bottlenecks: Iterable[Bottleneck], path: str | Path) -> None:
    rows = [b.__dict__ for b in bottlenecks]
    columns = list(Bottleneck.__dataclass_fields__.keys())
    df = pd.DataFrame(rows, columns=columns)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
