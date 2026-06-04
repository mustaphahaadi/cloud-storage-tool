import streamlit as st
import database
from modules import dashboard, allocation, monitoring, reporting

# Initialize Database
database.init_db()

st.set_page_config(page_title="SLA-Aware Cloud Storage Allocation Optimizer", layout="wide", page_icon="🗄️")

st.sidebar.title("System Navigation")
menu = ["Dashboard", "Allocation Simulation", "Performance Monitoring", "Reporting & Evaluation"]
choice = st.sidebar.radio("Go to", menu)

st.sidebar.markdown("---")
st.sidebar.info("Heuristic Approach to Storage Resource Allocation for Cost Reduction and Service Level Agreement (SLA)-Aware Availability.")

if choice == "Dashboard":
    dashboard.app()
elif choice == "Allocation Simulation":
    allocation.app()
elif choice == "Performance Monitoring":
    monitoring.app()
elif choice == "Reporting & Evaluation":
    reporting.app()
