"""Generate synthetic network telemetry data for analysis pipelines."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
import random
from pathlib import Path

import numpy as np
import pandas as pd


def simulate_telemetry_records(
    *,
    num_records: int,
    start_time: datetime,
    minutes_between: int = 1,
    seed: int | None = 2024,
) -> pd.DataFrame:
    """Create synthetic telemetry for multiple network devices."""
    rng = np.random.default_rng(seed)
    device_ids = [f"edge-{i:02d}" for i in range(1, 21)]
    regions = ["us-east", "us-west", "eu-central", "ap-south"]

    timestamps = [start_time + timedelta(minutes=i * minutes_between) for i in range(num_records)]

    records = []
    for ts in timestamps:
        device = random.choice(device_ids)
        region = random.choice(regions)
        traffic_mbps = rng.gamma(shape=4.0, scale=20.0)
        latency_ms = rng.normal(50, 10)
        packet_loss = max(0, rng.normal(0.5, 0.2))
        cpu_util = np.clip(rng.normal(55, 15), 0, 100)

        # Inject occasional spikes to emulate bottlenecks.
        if rng.random() < 0.02:
            latency_ms *= rng.uniform(1.8, 2.4)
            packet_loss += rng.uniform(1.5, 3.0)
            cpu_util = min(cpu_util + rng.uniform(15, 25), 100)

        records.append(
            {
                "timestamp": ts,
                "device_id": device,
                "region": region,
                "traffic_mbps": round(traffic_mbps, 2),
                "latency_ms": round(max(latency_ms, 1.0), 2),
                "packet_loss_pct": round(packet_loss, 3),
                "cpu_utilization_pct": round(cpu_util, 2),
            }
        )

    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic network telemetry records.")
    parser.add_argument("--output", default="data/network_telemetry.csv", help="Destination CSV path")
    parser.add_argument("--records", type=int, default=12000, help="Number of records to create")
    args = parser.parse_args()

    df = simulate_telemetry_records(num_records=args.records, start_time=datetime(2023, 1, 1))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote {len(df):,} telemetry records to {output_path}")


if __name__ == "__main__":
    main()
