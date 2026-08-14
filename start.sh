#!/usr/bin/env bash
set -e

# Ensure script runs from the repository root directory
CDPATH="" cd -- "$(dirname -- "$0")"

echo "======================================================="
echo "   Cloud Storage Allocation Optimization System"
echo "======================================================="

# Create virtual environment if missing
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Verifying / Installing dependencies from requirements.txt..."
    python -m pip install -q --upgrade pip
    python -m pip install -q -r requirements.txt
fi

# Seed database with mock data unless requested to skip
if [ "$1" == "skip-mock" ]; then
    echo "Skipping mock data generation."
else
    echo "Seeding database with mock allocation data..."
    python mock_data.py || echo "Notice: mock data seeding executed."
fi

echo "-------------------------------------------------------"
echo "Launching Streamlit dashboard..."
echo "-------------------------------------------------------"
streamlit run app.py
