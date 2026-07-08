import streamlit as st
import database
import pandas as pd
import plotly.express as px

def app():
    st.title("Dashboard")
    st.markdown("Overview of Storage Allocations and System Health")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No storage allocations found. Please go to the Storage Allocation module to generate data.")
        return
        
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_allocated = df['required_size'].sum()
    total_cost = df['cost_estimate'].sum()
    total_allocations = len(df)
    
    # Calculate SLA compliance (assuming requested SLA <= predicted SLA and latency_prediction <= latency_req)
    sla_compliant = len(df[(df['availability_prediction'] >= df['availability_req']) & (df['latency_prediction'] <= df['latency_req'])])
    sla_rate = (sla_compliant / total_allocations) * 100 if total_allocations > 0 else 0
    
    col1.metric("Total Storage Allocated", f"{total_allocated:,.2f} GB")
    col2.metric("Estimated Cost", f"${total_cost:,.2f}")
    col3.metric("Total Requests", f"{total_allocations}")
    col4.metric("SLA Compliance Rate", f"{sla_rate:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost by Storage Tier")
        cost_by_tier = df.groupby('recommended_tier')['cost_estimate'].sum().reset_index()
        fig1 = px.pie(cost_by_tier, values='cost_estimate', names='recommended_tier', hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Allocation Size by Storage Tier")
        size_by_tier = df.groupby('recommended_tier')['required_size'].sum().reset_index()
        fig2 = px.bar(size_by_tier, x='recommended_tier', y='required_size', 
                      labels={'recommended_tier': 'Storage Tier', 'required_size': 'Size (GB)'},
                      color='recommended_tier')
        st.plotly_chart(fig2, use_container_width=True)
        
    st.subheader("Recent Allocations")
    st.dataframe(df.head(5))
