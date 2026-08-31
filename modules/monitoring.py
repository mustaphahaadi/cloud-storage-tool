import streamlit as st
import database
import pandas as pd
import plotly.express as px

def app():
    st.title("📡 Performance & Capacity Monitoring")
    st.caption("Real-time telemetry tracking cumulative storage growth, cost accumulation, and workload allocation profiles.")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No allocation telemetry recorded yet. Please run an Allocation Simulation to generate monitoring data.", icon=":material/info:")
        return
        
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    
    df['cumulative_size'] = df['required_size'].cumsum()
    df['cumulative_cost'] = df['cost_estimate'].cumsum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("##### 📈 Cumulative Storage Capacity Growth (GB)")
            fig_growth = px.line(
                df,
                x='created_at',
                y='cumulative_size',
                markers=True,
                labels={'created_at': 'Timestamp', 'cumulative_size': 'Total Storage (GB)'},
                template="plotly_white"
            )
            fig_growth.update_traces(line=dict(color="#2563EB", width=3), marker=dict(size=6, color="#3B82F6"))
            fig_growth.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#F8FAFC",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_growth, width="stretch")
            
    with col2:
        with st.container(border=True):
            st.markdown("##### 💰 Cumulative Operational Spend Accumulation ($)")
            fig_cost = px.area(
                df,
                x='created_at',
                y='cumulative_cost',
                labels={'created_at': 'Timestamp', 'cumulative_cost': 'Total Spend ($)'},
                template="plotly_white",
                color_discrete_sequence=['#059669']
            )
            fig_cost.update_layout(
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#F8FAFC",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_cost, width="stretch")
            
    with st.container(border=True):
        st.markdown("##### 🎯 Workload Allocation Profiles (Capacity vs Access Latency)")
        fig_scatter = px.scatter(
            df,
            x='required_size',
            y='latency_req',
            color='recommended_tier',
            size='cost_estimate',
            hover_data=['availability_req', 'latency_prediction', 'availability_prediction', 'alpha', 'beta'],
            labels={'required_size': 'Capacity (GB)', 'latency_req': 'Max Tolerable Latency (ms)', 'recommended_tier': 'Storage Tier'},
            template="plotly_white"
        )
        fig_scatter.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_scatter, width="stretch")

