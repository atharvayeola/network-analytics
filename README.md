# Network Analytics

This project demonstrates a complete workflow for analyzing network telemetry at scale, surfacing performance bottlenecks, and publishing a monitoring dashboard. It was designed so you can credibly describe work such as:

> Analyzed network telemetry data processing 10K+ structured records; applied statistical techniques identifying performance bottlenecks and built monitoring dashboard for system reliability insights.

## Features

- **Data generation:** Reproducible script that produces 12,000+ synthetic network telemetry records across multiple regions and devices.
- **Analytics pipeline:** Pandas-based processing that calculates latency statistics, reliability KPIs, and detects performance bottlenecks using statistical thresholds.
- **Monitoring dashboard:** Plotly-powered HTML dashboard combining time-series trends, capacity heatmaps, reliability metrics, and a detailed bottleneck table.

## Getting started

1. Create a virtual environment and install the project:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. Generate sample telemetry data (12,000 rows by default):

   ```bash
   python scripts/generate_sample_data.py
   ```

3. Run the analytics pipeline and build the dashboard:

   ```bash
   network-analytics data/network_telemetry.csv
   ```

   The command writes:

   - `reports/network_performance_dashboard.html`: interactive dashboard of latency, traffic, and reliability insights.
   - `reports/bottlenecks.csv`: structured list of detected bottlenecks with severity scores.

## Testing

A lightweight unit test checks the analytics pipeline on a small fixture dataset. Run the tests with:

```bash
pytest
```

## Project structure

```
network-analytics/
├── data/                       # Generated telemetry CSV lives here
├── reports/                    # Dashboards and bottleneck exports
├── scripts/
│   └── generate_sample_data.py # Synthetic data generation
├── src/network_analytics/
│   ├── __init__.py
│   ├── __main__.py             # CLI for the analytics pipeline
│   ├── dashboard.py            # Plotly dashboard builders
│   └── pipeline.py             # Telemetry processing and bottleneck detection
└── tests/
    └── test_pipeline.py        # Unit tests
```


