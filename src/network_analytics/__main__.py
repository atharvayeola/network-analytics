"""CLI entrypoint for the network analytics project."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import pipeline
from . import dashboard


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Network telemetry analytics pipeline")
    parser.add_argument("csv", help="Path to the telemetry CSV file")
    parser.add_argument(
        "--dashboard",
        default="reports/network_performance_dashboard.html",
        help="Location to write the generated dashboard HTML",
    )
    parser.add_argument(
        "--bottlenecks",
        default="reports/bottlenecks.csv",
        help="Location to write detected bottlenecks",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    results = pipeline.run_pipeline(args.csv)
    pipeline.export_bottlenecks(results["bottlenecks"], args.bottlenecks)
    dashboard.build_dashboard(
        results["telemetry"],
        results["latency_stats"],
        results["reliability"],
        results["bottlenecks"],
        output_html=args.dashboard,
    )

    print(f"Analytics pipeline complete. Dashboard saved to {args.dashboard}")
    print(f"Detected bottlenecks exported to {args.bottlenecks}")


if __name__ == "__main__":
    main()
