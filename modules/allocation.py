import streamlit as st
import database
import heuristic
import pandas as pd

def app():
    st.title("Storage Allocation Simulation")
    st.markdown("Enter workload and SLA requirements to generate a cost-optimized, SLA-aware storage recommendation.")
    
    with st.form("allocation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            required_size = st.number_input("Required Storage Size (GB)", min_value=1.0, value=100.0, step=10.0)
            latency_req = st.number_input("Max Tolerable Access Latency (ms)", min_value=1.0, value=10.0, step=1.0,
                                          help="Specify the maximum tolerable latency for accessing storage.")
            
        with col2:
            availability_req = st.selectbox("Availability Requirement (SLA %)", 
                                            options=[99.0, 99.9, 99.99, 99.999], index=1)
            budget = st.number_input("Budget Constraints ($) (Optional)", min_value=0.0, value=0.0, step=10.0, 
                                     help="Leave at 0.0 for no budget constraint")
                                     
        submit_button = st.form_submit_button(label="Generate Recommendation")
        
    if submit_button:
        budget_val = budget if budget > 0 else None
        
        with st.spinner("Running Heuristic Algorithm..."):
            result = heuristic.allocate_storage(required_size, availability_req, latency_req, budget_val)
            
        if result["success"]:
            st.success("Allocation Recommendation Generated Successfully!")
            
            st.markdown("### Recommendation Details")
            r_col1, r_col2, r_col3, r_col4 = st.columns(4)
            r_col1.metric("Recommended Tier", result["tier_name"])
            r_col2.metric("Estimated Cost", f"${result['cost_estimate']:.2f}")
            r_col3.metric("Predicted Availability", f"{result['availability_prediction']}%")
            r_col4.metric("Predicted Latency", f"{result['latency_prediction']} ms")
            
            # Comparative Evaluation Table
            st.markdown("### Algorithm Comparative Analysis")
            st.info("Comparison between the proposed Greedy Cost-Optimization Heuristic and traditional baseline algorithms:")
            
            baselines = result["baselines"]
            comparison_rows = []
            for name, data in baselines.items():
                if data is None:
                    comparison_rows.append({
                        "Allocation Algorithm": "Proposed Heuristic (Greedy)" if name == "heuristic" else name.replace("_", " ").title(),
                        "Recommended Storage Tier": "No feasible allocation",
                        "Estimated Monthly Cost": "$0.00",
                        "SLA Availability": "0.0%",
                        "Access Latency": "0 ms",
                        "Feasible (SLA Met)": "❌ No"
                    })
                else:
                    comparison_rows.append({
                        "Allocation Algorithm": "Proposed Heuristic (Greedy)" if name == "heuristic" else name.replace("_", " ").title(),
                        "Recommended Storage Tier": data["tier_name"],
                        "Estimated Monthly Cost": f"${data['cost_estimate']:.2f}",
                        "SLA Availability": f"{data['availability_prediction']}%",
                        "Access Latency": f"{data['latency_prediction']} ms",
                        "Feasible (SLA Met)": "✅ Yes"
                    })
            st.dataframe(pd.DataFrame(comparison_rows), use_container_width=True)
            
            # Save to database
            database.save_allocation(
                required_size=required_size,
                availability_req=availability_req,
                latency_req=latency_req,
                budget=budget_val,
                tier_id=result["tier_id"],
                cost_estimate=result["cost_estimate"],
                availability_prediction=result["availability_prediction"],
                latency_prediction=result["latency_prediction"]
            )
            st.info("This allocation has been recorded in the database.")
            
        else:
            st.error("Failed to generate recommendation.")
            st.warning(result["message"])
            
    # Show available tiers reference
    with st.expander("View Available Storage Tiers"):
        tiers_df = database.get_storage_tiers()
        # Rename columns for clarity in displaying
        tiers_df_display = tiers_df.rename(columns={
            'name': 'Storage Tier',
            'cost_per_gb': 'Cost per GB ($)',
            'sla_availability': 'SLA Availability (%)',
            'access_latency': 'Access Latency (ms)'
        })
        st.dataframe(tiers_df_display)
