import streamlit as st
import database
import pandas as pd
import plotly.express as px

def app():
    st.title("📊 Executive Dashboard")
    st.caption("Overview of Storage Resource Allocation, System Health, and SLA Performance Metrics")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No storage allocations recorded yet. Please run an Allocation Simulation to generate analytics.", icon=":material/info:")
        return
        
    # Key System Metrics Panel
    with st.container(border=True):
        st.markdown("##### 📈 System Overview Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_allocated = df['required_size'].sum()
        total_cost = df['cost_estimate'].sum()
        total_allocations = len(df)
        
        sla_compliant = len(df[(df['availability_prediction'] >= df['availability_req']) & (df['latency_prediction'] <= df['latency_req'])])
        sla_rate = (sla_compliant / total_allocations) * 100 if total_allocations > 0 else 0
        
        col1.metric("Total Storage Allocated", f"{total_allocated:,.1f} GB", help="Cumulative capacity allocated")
        col2.metric("Cumulative Monthly Spend", f"${total_cost:,.2f}", help="Total operational cost across all allocations")
        col3.metric("Allocation Transactions", f"{total_allocations}", help="Total storage requests processed")
        col4.metric("SLA Compliance Rate", f"{sla_rate:.1f}%", help="Percentage of allocations meeting target SLA")

    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("##### 🍰 Monthly Cost Distribution by Tier")
            cost_by_tier = df.groupby('recommended_tier')['cost_estimate'].sum().reset_index()
            fig1 = px.pie(
                cost_by_tier,
                values='cost_estimate',
                names='recommended_tier',
                hole=0.4,
                template="plotly_dark"
            )
            fig1.update_layout(
                paper_bgcolor="#1E293B",
                plot_bgcolor="#0F172A",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig1, width="stretch")
        
    with col2:
        with st.container(border=True):
            st.markdown("##### 📊 Allocated Capacity (GB) by Tier")
            size_by_tier = df.groupby('recommended_tier')['required_size'].sum().reset_index()
            fig2 = px.bar(
                size_by_tier,
                x='recommended_tier',
                y='required_size',
                labels={'recommended_tier': 'Storage Tier', 'required_size': 'Capacity (GB)'},
                color='recommended_tier',
                template="plotly_dark"
            )
            fig2.update_layout(
                paper_bgcolor="#1E293B",
                plot_bgcolor="#0F172A",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig2, width="stretch")
        
    with st.container(border=True):
        st.markdown("##### 🕒 Recent Storage Allocations")
        recent_df = df[['id', 'created_at', 'required_size', 'availability_req', 'recommended_tier', 'cost_estimate', 'alpha', 'beta']].head(5)
        recent_display = recent_df.rename(columns={
            'id': 'ID',
            'created_at': 'Timestamp',
            'required_size': 'Capacity (GB)',
            'availability_req': 'Target SLA (%)',
            'recommended_tier': 'Allocated Tier',
            'cost_estimate': 'Cost ($)',
            'alpha': 'α (Cost Wt)',
            'beta': 'β (Avail Wt)'
        })
        st.dataframe(recent_display, width="stretch")

