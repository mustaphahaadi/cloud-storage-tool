import streamlit as st
import database
import heuristic
import pandas as pd

def app():
    st.title("⚡ Storage Resource Allocation Simulation")
    st.markdown("Automated workload estimation and dual-objective heuristic storage tier optimization.")

    st.subheader("🤖 Automatic Storage Size Suggestion Engine")
    st.caption("Select your workload category and operational parameters to automatically calculate the recommended storage size.")

    with st.expander("Configure Workload Estimation Parameters", expanded=True):
        category = st.selectbox(
            "Select Workload Profile Category",
            options=[
                "Enterprise Relational Database (OLTP)",
                "HD Video & Media Streaming",
                "IoT Sensor & Log Analytics",
                "Document & Content Management (CMS)",
                "Cold Backup & System Archive"
            ],
            index=2
        )

        p_col1, p_col2, p_col3 = st.columns(3)
        params = {}

        if category == "Enterprise Relational Database (OLTP)":
            with p_col1:
                params["users"] = st.number_input("Estimated Active Users", min_value=10, max_value=50000, value=2500, step=100)
            with p_col2:
                params["transactions"] = st.number_input("Monthly Transactions", min_value=1000, max_value=1000000, value=150000, step=10000)

        elif category == "HD Video & Media Streaming":
            with p_col1:
                params["media_count"] = st.number_input("Number of Media Files", min_value=10, max_value=10000, value=500, step=50)
            with p_col2:
                params["avg_file_gb"] = st.number_input("Avg File Size (GB)", min_value=0.5, max_value=50.0, value=3.5, step=0.5)

        elif category == "IoT Sensor & Log Analytics":
            with p_col1:
                params["devices"] = st.number_input("Connected IoT Devices", min_value=10, max_value=10000, value=750, step=50)
            with p_col2:
                params["daily_log_mb"] = st.number_input("Daily Log Output per Device (MB)", min_value=1.0, max_value=500.0, value=40.0, step=5.0)
            with p_col3:
                params["retention_days"] = st.number_input("Retention Period (Days)", min_value=7, max_value=365, value=120, step=10)

        elif category == "Document & Content Management (CMS)":
            with p_col1:
                params["employees"] = st.number_input("Total Employees", min_value=5, max_value=5000, value=300, step=25)
            with p_col2:
                params["docs_per_emp"] = st.number_input("Documents per Employee", min_value=50, max_value=5000, value=500, step=50)
            with p_col3:
                params["avg_doc_mb"] = st.number_input("Avg Doc Size (MB)", min_value=0.5, max_value=50.0, value=4.0, step=0.5)

        elif category == "Cold Backup & System Archive":
            with p_col1:
                params["snapshot_gb"] = st.number_input("Full Snapshot Size (GB)", min_value=50.0, max_value=10000.0, value=650.0, step=50.0)
            with p_col2:
                params["retention_count"] = st.number_input("Retention Snapshots", min_value=1, max_value=24, value=8, step=1)

        suggested_gb = heuristic.suggest_workload_size(category, params)
        st.info(f"💡 **Automated Storage Recommendation**: **{suggested_gb:,.2f} GB** calculated for **{category}**.")

    st.markdown("---")

    with st.form("allocation_form"):
        st.subheader("Allocation Constraints & Optimization Weights")
        col1, col2 = st.columns(2)

        with col1:
            required_size = st.number_input(
                "Required Storage Size (GB)",
                min_value=1.0,
                max_value=50000.0,
                value=float(suggested_gb),
                step=50.0,
                help="Automatically populated by the Workload Estimation Engine above. Can be manually adjusted if required."
            )
            latency_req = st.number_input(
                "Max Tolerable Access Latency (ms)",
                min_value=1.0,
                max_value=100.0,
                value=15.0,
                step=1.0,
                help="Specify the maximum tolerable latency for accessing storage."
            )

        with col2:
            availability_req = st.selectbox(
                "Availability Requirement (SLA %)",
                options=[99.0, 99.9, 99.99, 99.999],
                index=1
            )
            budget = st.number_input(
                "Budget Constraints ($) (Optional)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                help="Leave at 0.0 for no budget constraint"
            )

        st.markdown("---")
        st.subheader("Multi-Objective Heuristic Configuration")
        alpha = st.slider(
            "Cost Optimization Weight (α)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher alpha prioritizes low cost. Lower alpha prioritizes higher availability (SLA compliance)."
        )
        beta_val = round(1.0 - alpha, 2)
        st.caption(f"Availability Weight (β): {beta_val}")

        submit_button = st.form_submit_button(label="Generate Storage Recommendation")

    if submit_button:
        budget_val = budget if budget > 0 else None

        with st.spinner("Running Multi-Objective Heuristic..."):
            result = heuristic.allocate_storage(required_size, availability_req, latency_req, budget_val, alpha=alpha, beta=beta_val)

        if result["success"]:
            st.success("Allocation Recommendation Generated Successfully!")

            st.markdown("### Recommendation Details")
            r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns(5)
            r_col1.metric("Recommended Tier", result["tier_name"])
            r_col2.metric("Estimated Cost", f"${result['cost_estimate']:,.2f}")
            r_col3.metric("Availability SLA", f"{result['availability_prediction']}%")
            r_col4.metric("Access Latency", f"{result['latency_prediction']} ms")
            r_col5.metric("Weights (α / β)", f"{alpha} / {beta_val}")

            # Comparative Evaluation Table
            st.markdown("### Algorithm Comparative Analysis")
            st.info("Comparison between the proposed α-β Dual-Objective Heuristic and traditional baseline algorithms:")

            baselines = result["baselines"]
            comparison_rows = []
            for name, data in baselines.items():
                if data is None:
                    comparison_rows.append({
                        "Allocation Algorithm": "Proposed Heuristic (α-β)" if name == "heuristic" else name.replace("_", " ").title(),
                        "Recommended Storage Tier": "No feasible allocation",
                        "Estimated Monthly Cost": "$0.00",
                        "SLA Availability": "0.0%",
                        "Access Latency": "0 ms",
                        "Feasible (SLA Met)": "❌ No"
                    })
                else:
                    comparison_rows.append({
                        "Allocation Algorithm": "Proposed Heuristic (α-β)" if name == "heuristic" else name.replace("_", " ").title(),
                        "Recommended Storage Tier": data["tier_name"],
                        "Estimated Monthly Cost": f"${data['cost_estimate']:,.2f}",
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
                alpha=alpha,
                beta=beta_val,
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
        tiers_df_display = tiers_df.rename(columns={
            "id": "Tier ID",
            "name": "Tier Name",
            "cost_per_gb": "Cost per GB ($)",
            "sla_availability": "SLA Availability (%)",
            "access_latency": "Access Latency (ms)"
        })
        st.dataframe(tiers_df_display, use_container_width=True)
