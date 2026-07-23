# Storage Resource Allocation System

This is a Streamlit-based web application that implements a SLA-aware heuristic approach to cloud storage resource allocation. The system is designed to minimize storage costs while ensuring that Service Level Agreement (SLA) availability and workload performance (latency) requirements are met.

## Features

- **Dashboard:** An overview of total storage allocations, estimated costs, and overall SLA compliance rate, visualized with interactive charts.
- **Allocation Engine:** A smart heuristic algorithm that takes user inputs (required size, access latency requirement, availability requirement, and budget constraints) to recommend the most cost-effective cloud storage tier.
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
├── README.md             # Project documentation and setup guide
├── docs/                 # Detailed system guides and documentation
└── modules/              # Streamlit page modules
    ├── __init__.py
    ├── allocation.py     # Allocation simulation form
    ├── dashboard.py      # KPI dashboard
    ├── monitoring.py     # Trend visualizations
    └── reporting.py      # Tabular data and CSV export
```

## Prerequisites

- **Python 3.8+**: Ensure Python is installed on your system.
  - **Windows:** Download Python from [python.org](https://www.python.org/downloads/) or Microsoft Store. **Crucial:** Check the box **"Add python.exe to PATH"** during installation.
  - **Linux/macOS:** Python 3 is typically pre-installed or available via `apt`, `brew`, etc.
- **SQLite3:** Pre-packaged with standard Python installations.

---

## Installation & Setup

### 🪟 Windows Setup Instructions

Follow these steps depending on your preferred Windows command-line environment:

#### Option 1: Windows Command Prompt (cmd.exe)

1. Open **Command Prompt** (`cmd`) and navigate to the project directory:
   ```cmd
   cd C:\path\to\cloud-optimized
   ```

2. Create a Python virtual environment:
   ```cmd
   python -m venv .venv
   ```
   *(If `python` is not recognized, use the Windows Python launcher: `py -m venv .venv`)*

3. Activate the virtual environment:
   ```cmd
   .venv\Scripts\activate
   ```
   *(You should see `(.venv)` displayed at the start of your prompt line).*

4. Install required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

---

#### Option 2: Windows PowerShell

1. Open **PowerShell** and navigate to the project directory:
   ```powershell
   cd C:\path\to\cloud-optimized
   ```

2. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   ```
   *(Or `py -m venv .venv`)*

3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

---

#### Option 3: Git Bash on Windows

1. Open **Git Bash** and navigate to the project directory:
   ```bash
   cd /c/path/to/cloud-optimized
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/Scripts/activate
   ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### 🐧 🍎 Linux / macOS Setup Instructions

1. Navigate to the project directory:
   ```bash
   cd /path/to/cloud-optimized
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

1. **(Optional) Seed Mock Data:**
   To populate the SQLite database (`storage_allocation.db`) with historical allocations for testing the Dashboard and Monitoring tabs, run:
   - **Windows (cmd/PowerShell/Git Bash):**
     ```cmd
     python mock_data.py
     ```
   - **Linux / macOS:**
     ```bash
     python mock_data.py
     ```

2. **Launch the Streamlit Server:**
   ```cmd
   streamlit run app.py
   ```

3. **Access the Interface:**
   Open your web browser and navigate to:
   [http://localhost:8501](http://localhost:8501)

---

## 🛠️ Windows Troubleshooting

- **PowerShell Script Execution Error:**
  If PowerShell shows `...cannot be loaded because running scripts is disabled on this system`, run the following command in PowerShell to temporarily allow script execution for your session:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```

- **`'python' is not recognized as an internal or external command`:**
  - Ensure Python is added to your Windows Environment PATH.
  - Alternatively, use the Windows Python launcher command `py` instead of `python`.

- **Port 8501 is already in use:**
  If port 8501 is occupied by another process, launch Streamlit on an alternative port:
  ```cmd
  streamlit run app.py --server.port 8502
  ```

---

## Storage Tiers Modelled

The application simulates 3 cloud storage tiers as defined in the literature:
- **Block Storage:** For low-latency workloads (e.g., databases) with 99.999% SLA availability and 2.0 ms latency, costing $0.15 per GB.
- **File Storage:** For general-purpose applications with 99.99% SLA availability and 10.0 ms latency, costing $0.08 per GB.
- **Object Storage:** For backup, archiving, and unstructured data with 99.0% SLA availability and 50.0 ms latency, costing $0.02 per GB.


