import streamlit as st
import database
import pandas as pd
import plotly.express as px

def app():
    st.title("Monitoring")
    st.markdown("Monitor storage growth, utilization, and cost trends over time.")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No data available for monitoring. Please generate some allocations first.")
        return
        
    # Convert created_at to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    # Cumulative Sums over time
    df['cumulative_size'] = df['required_size'].cumsum()
    df['cumulative_cost'] = df['cost_estimate'].cumsum()
    
    st.subheader("Storage Growth Trend")
    fig_growth = px.line(df, x='created_at', y='cumulative_size', markers=True,
                         labels={'created_at': 'Time', 'cumulative_size': 'Total Allocated (GB)'},
                         title="Cumulative Storage Allocated Over Time")
    st.plotly_chart(fig_growth, use_container_width=True)
    
    st.subheader("Cost Trend Analysis")
    fig_cost = px.area(df, x='created_at', y='cumulative_cost',
                       labels={'created_at': 'Time', 'cumulative_cost': 'Total Cost ($)'},
                       title="Cumulative Cost Over Time",
                       color_discrete_sequence=['#ff7f0e'])
    st.plotly_chart(fig_cost, use_container_width=True)
    
    st.subheader("Recent Allocation Profiles (Latency vs Size)")
    fig_scatter = px.scatter(df, x='required_size', y='latency_req', color='recommended_tier',
                             size='cost_estimate', hover_data=['availability_req', 'latency_prediction', 'availability_prediction', 'alpha', 'beta'],
                             labels={'required_size': 'Size (GB)', 'latency_req': 'Max Tolerable Latency (ms)', 'recommended_tier': 'Storage Tier'},
                             title="Allocation Profile: Size vs Latency Requirement")
    st.plotly_chart(fig_scatter, use_container_width=True)
