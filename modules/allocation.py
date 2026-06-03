import streamlit as st
import database
import heuristic
import pandas as pd

def app():
    st.title("Storage Allocation")
    st.markdown("Enter requirements to generate a cost-optimized, SLA-aware storage recommendation.")
    
    with st.form("allocation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            required_size = st.number_input("Required Storage Size (GB)", min_value=1.0, value=100.0, step=10.0)
            workload_iops = st.number_input("Expected Workload (IOPS)", min_value=1, value=1000, step=100)
            
        with col2:
            availability_req = st.selectbox("Availability Requirement (SLA %)", 
                                            options=[99.0, 99.9, 99.99, 99.999], index=1)
            budget = st.number_input("Budget Constraints ($) (Optional)", min_value=0.0, value=0.0, step=10.0, 
                                     help="Leave at 0.0 for no budget constraint")
                                     
        submit_button = st.form_submit_button(label="Generate Recommendation")
        
    if submit_button:
        budget_val = budget if budget > 0 else None
        
        with st.spinner("Running Heuristic Algorithm..."):
            result = heuristic.allocate_storage(required_size, workload_iops, availability_req, budget_val)
            
        if result["success"]:
            st.success("Allocation Recommendation Generated Successfully!")
            
            st.markdown("### Recommendation Details")
            r_col1, r_col2, r_col3 = st.columns(3)
            r_col1.metric("Recommended Tier", result["tier_name"])
            r_col2.metric("Estimated Cost", f"${result['cost_estimate']:.2f}")
            r_col3.metric("Predicted Availability", f"{result['availability_prediction']}%")
            
            # Save to database
            database.save_allocation(
                required_size=required_size,
                workload_iops=workload_iops,
                availability_req=availability_req,
                budget=budget_val,
                tier_id=result["tier_id"],
                cost_estimate=result["cost_estimate"],
                availability_prediction=result["availability_prediction"]
            )
            st.info("This allocation has been recorded in the database.")
            
        else:
            st.error("Failed to generate recommendation.")
            st.warning(result["message"])
            
    # Show available tiers reference
    with st.expander("View Available Storage Tiers"):
        tiers_df = database.get_storage_tiers()
        st.dataframe(tiers_df)
