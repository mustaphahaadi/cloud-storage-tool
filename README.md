# Storage Resource Allocation System

This is a Streamlit-based web application that implements a heuristic approach to storage resource allocation. The system is designed to minimize storage costs while ensuring that Service Level Agreement (SLA) availability and workload performance (IOPS) requirements are met.

## Features

- **Dashboard:** An overview of total storage allocations, estimated costs, and overall SLA compliance rate, visualized with interactive charts.
- **Allocation Engine:** A smart heuristic algorithm that takes user inputs (required size, expected workload, availability requirement, and budget constraints) to recommend the most cost-effective cloud storage tier.
- **Monitoring:** Time-series tracking of storage growth, cumulative cost trends, and workload distribution.
- **Reporting:** Detailed tabular breakdowns of allocation history and SLA compliance, with the ability to export data to CSV.

## Project Structure

```text
cloud-optimized/
├── app.py                # Main Streamlit application entry point
├── database.py           # SQLite database schema and connection logic
├── heuristic.py          # Greedy cost-optimization algorithm
├── mock_data.py          # Script to generate random historical allocations
├── requirements.txt      # Python dependencies
└── modules/              # Streamlit page modules
    ├── __init__.py
    ├── allocation.py     # Allocation simulation form
    ├── dashboard.py      # KPI dashboard
    ├── monitoring.py     # Trend visualizations
    └── reporting.py      # Tabular data and CSV export
```

## Prerequisites

- Python 3.8+
- SQLite3 (Included with standard Python library)

## Installation

1. Navigate to the project directory:
   ```bash
   cd /path/to/cloud-optimized
   ```

2. Create and activate a Python virtual environment (recommended to avoid system-wide package conflicts):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. (Optional) If you want to view immediate results on the dashboard and monitoring tabs, run the mock data generator to populate the database with sample historical data:
   ```bash
   python mock_data.py
   ```

2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

3. Open your web browser and navigate to `http://localhost:8501`.

## Storage Tiers Modelled

The application simulates 4 common cloud storage tiers:
- **High-Performance (NVMe):** For mission-critical workloads (Max 100k IOPS, 99.999% SLA).
- **Standard (SSD):** For general-purpose applications (Max 10k IOPS, 99.99% SLA).
- **Capacity (HDD):** For bulk storage (Max 1k IOPS, 99.9% SLA).
- **Archive (Cold Storage):** For long-term data retention (Max 100 IOPS, 99.0% SLA).
