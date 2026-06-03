import streamlit as st
import database
import pandas as pd

def app():
    st.title("Reporting")
    st.markdown("Generate and export system reports.")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No data available for reporting.")
        return
        
    st.subheader("SLA Compliance Report")
    df['sla_met'] = df['availability_prediction'] >= df['availability_req']
    sla_compliance_df = df[['id', 'created_at', 'required_size', 'availability_req', 'availability_prediction', 'recommended_tier', 'sla_met']]
    st.dataframe(sla_compliance_df, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Cost Optimization Insights")
    tier_summary = df.groupby('recommended_tier').agg(
        total_allocations=('id', 'count'),
        total_size_gb=('required_size', 'sum'),
        total_cost=('cost_estimate', 'sum')
    ).reset_index()
    
    tier_summary['avg_cost_per_gb'] = tier_summary['total_cost'] / tier_summary['total_size_gb']
    st.dataframe(tier_summary, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Detailed Allocation History")
    st.dataframe(df, use_container_width=True)
    
    # Export functionality
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Report (CSV)",
        data=csv,
        file_name='storage_allocation_report.csv',
        mime='text/csv',
    )
