import streamlit as st
import database
import heuristic
import pandas as pd
import plotly.express as px

def app():
    st.title("Reporting and Performance Evaluation")
    st.markdown("Generate system reports and evaluate allocation algorithm performance.")
    
    df = database.get_allocation_history()
    
    if df.empty:
        st.info("No data available for reporting.")
        return
        
    st.subheader("Algorithm Historical Performance Comparison")
    st.markdown("This section simulates how traditional algorithms would have performed on the historical requests compared to the proposed Greedy Heuristic:")
    
    tiers_df = database.get_storage_tiers()
    
    # Compute total cost and SLA compliance for all algorithms
    stats = {
        "Proposed Heuristic (Greedy)": {"cost": 0.0, "compliant": 0},
        "First Fit": {"cost": 0.0, "compliant": 0},
        "Best Fit": {"cost": 0.0, "compliant": 0},
        "Worst Fit": {"cost": 0.0, "compliant": 0}
    }
    
    for _, row in df.iterrows():
        req_size = row['required_size']
        avail_req = row['availability_req']
        lat_req = row['latency_req']
        
        # Heuristic (stored in DB)
        stats["Proposed Heuristic (Greedy)"]["cost"] += row['cost_estimate']
        if (row['availability_prediction'] >= avail_req) and (row['latency_prediction'] <= lat_req):
            stats["Proposed Heuristic (Greedy)"]["compliant"] += 1
            
        # Run baselines
        # First Fit
        ff = heuristic.allocate_first_fit(tiers_df, req_size, avail_req, lat_req)
        if ff is not None:
            stats["First Fit"]["cost"] += ff["cost_estimate"]
            if (ff["availability_prediction"] >= avail_req) and (ff["latency_prediction"] <= lat_req):
                stats["First Fit"]["compliant"] += 1
                
        # Best Fit
        bf = heuristic.allocate_best_fit(tiers_df, req_size, avail_req, lat_req)
        if bf is not None:
            stats["Best Fit"]["cost"] += bf["cost_estimate"]
            if (bf["availability_prediction"] >= avail_req) and (bf["latency_prediction"] <= lat_req):
                stats["Best Fit"]["compliant"] += 1
                
        # Worst Fit
        wf = heuristic.allocate_worst_fit(tiers_df, req_size, avail_req, lat_req)
        if wf is not None:
            stats["Worst Fit"]["cost"] += wf["cost_estimate"]
            if (wf["availability_prediction"] >= avail_req) and (wf["latency_prediction"] <= lat_req):
                stats["Worst Fit"]["compliant"] += 1
                
    total_rows = len(df)
    comparison_rows = []
    plot_data = []
    
    for algo, data in stats.items():
        compliance_rate = (data["compliant"] / total_rows) * 100 if total_rows > 0 else 0
        comparison_rows.append({
            "Allocation Algorithm": algo,
            "Cumulative Historical Cost ($)": f"${data['cost']:.2f}",
            "SLA Compliance Rate (%)": f"{compliance_rate:.1f}%"
        })
        plot_data.append({
            "Algorithm": algo,
            "Cost": data["cost"],
            "Compliance Rate (%)": compliance_rate
        })
        
    st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True)
    
    # Plot cost comparison
    plot_df = pd.DataFrame(plot_data)
    fig_comp = px.bar(plot_df, x='Algorithm', y='Cost', color='Algorithm',
                      labels={'Cost': 'Cumulative Operational Cost ($)'},
                      title="Cumulative Operational Cost Comparison (Lower is Better)")
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("SLA Compliance Log")
    df['sla_met'] = (df['availability_prediction'] >= df['availability_req']) & (df['latency_prediction'] <= df['latency_req'])
    sla_compliance_df = df[['id', 'created_at', 'required_size', 'availability_req', 'availability_prediction', 'latency_req', 'latency_prediction', 'recommended_tier', 'sla_met']]
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
    # Rename columns for displaying
    df_display = df.rename(columns={
        'required_size': 'Required Size (GB)',
        'availability_req': 'Availability Req (%)',
        'latency_req': 'Latency Req (ms)',
        'budget': 'Budget ($)',
        'recommended_tier': 'Recommended Tier',
        'cost_estimate': 'Cost Estimate ($)',
        'availability_prediction': 'Availability Pred (%)',
        'latency_prediction': 'Latency Pred (ms)',
        'created_at': 'Timestamp'
    })
    st.dataframe(df_display, use_container_width=True)
    
    # Export functionality
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Report (CSV)",
        data=csv,
        file_name='storage_allocation_report.csv',
        mime='text/csv',
    )
