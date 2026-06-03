import streamlit as st
import database
from modules import dashboard, allocation, monitoring, reporting

# Initialize Database
database.init_db()

st.set_page_config(page_title="Storage Allocation System", layout="wide", page_icon="🗄️")

st.sidebar.title("Navigation")
menu = ["Dashboard", "Storage Allocation", "Monitoring", "Reporting"]
choice = st.sidebar.radio("Go to", menu)

st.sidebar.markdown("---")
st.sidebar.info("Heuristic Approach to Storage Resource Allocation for Cost Reduction and SLA-Aware Availability.")

if choice == "Dashboard":
    dashboard.app()
elif choice == "Storage Allocation":
    allocation.app()
elif choice == "Monitoring":
    monitoring.app()
elif choice == "Reporting":
    reporting.app()
