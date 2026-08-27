# pyrefly: ignore [missing-import]
import streamlit as st
import database
from modules import dashboard, allocation, monitoring, reporting

# Initialize Database
database.init_db()

st.set_page_config(
    page_title="SLA-Aware Cloud Storage Optimizer",
    layout="wide",
    page_icon=":material/cloud_done:"
)

st.sidebar.markdown("## ☁️ Storage Optimizer")
st.sidebar.markdown(":green-badge[● System Online] :blue-badge[v2.4 Enterprise]")

menu_options = {
    "Dashboard": ":material/dashboard: Executive Dashboard",
    "Allocation Simulation": ":material/tune: Allocation Simulation",
    "Performance Monitoring": ":material/monitoring: Performance Monitoring",
    "Reporting & Evaluation": ":material/analytics: Reporting & Evaluation"
}

choice = st.sidebar.radio(
    "System Navigation",
    options=list(menu_options.keys()),
    format_func=lambda x: menu_options[x]
)

st.sidebar.caption(
    "**Project Architecture**: Heuristic Approach to Storage Resource Allocation for Cost Reduction and SLA-Aware Availability."
)

if choice == "Dashboard":
    dashboard.app()
elif choice == "Allocation Simulation":
    allocation.app()
elif choice == "Performance Monitoring":
    monitoring.app()
elif choice == "Reporting & Evaluation":
    reporting.app()

