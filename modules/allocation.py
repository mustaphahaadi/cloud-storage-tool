import streamlit as st
import database
import heuristic
import pandas as pd
import plotly.express as px

def app():
    st.title("⚡ Storage Resource Allocation Simulation")
    st.markdown("Automated workload estimation and dual-objective heuristic storage tier optimization.")

    st.subheader("🤖 Automatic Storage Size Suggestion Engine")
    st.caption("Select your workload category and operational parameters to automatically calculate the recommended storage size.")

    with st.container(border=True):
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
        st.info(f"💡 **Automated Capacity Target**: Calculated **{suggested_gb:,.2f} GB** for **{category}**.", icon=":material/memory:")

    with st.form("allocation_form"):
        st.subheader("⚙️ Constraints & Multi-Objective Weights")
        col1, col2 = st.columns(2)

        with col1:
            required_size = st.number_input(
                "Required Storage Capacity (GB)",
                min_value=1.0,
                max_value=50000.0,
                value=float(suggested_gb),
                step=50.0,
                help="Automatically populated by Workload Estimation Engine. Adjustable."
            )
            latency_req = st.number_input(
                "Max Tolerable Access Latency (ms)",
                min_value=0.5,
                max_value=100.0,
                value=15.0,
                step=0.5,
                help="Maximum access latency tolerable by application workloads."
            )

        with col2:
            availability_req = st.selectbox(
                "Availability Target (SLA %)",
                options=[99.0, 99.9, 99.99, 99.999],
                index=1
            )
            budget = st.number_input(
                "Budget Bound ($) (Optional)",
                min_value=0.0,
                value=0.0,
                step=10.0,
                help="Leave at 0.0 for unconstrained budget allocation."
            )

        st.markdown("##### 🎚️ Heuristic Trade-off Weights")
        alpha = st.slider(
            "Cost Optimization Weight (α)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher α prioritizes lower cost. Lower α prioritizes higher availability SLA."
        )
        beta_val = round(1.0 - alpha, 2)
        
        if alpha > 0.5:
            mode_badge = ":orange-badge[Cost-Prioritized Mode]"
        elif alpha < 0.5:
            mode_badge = ":blue-badge[Availability-Prioritized Mode]"
        else:
            mode_badge = ":green-badge[Balanced Dual-Objective Mode]"

        st.markdown(f"**Availability Weight (β)**: `{beta_val}` &nbsp; {mode_badge}")

        submit_button = st.form_submit_button(label="🚀 Generate Storage Recommendation", type="primary")

    if submit_button:
        budget_val = budget if budget > 0 else None

        with st.spinner("Executing α-β Dual-Objective Heuristic Scoring..."):
            result = heuristic.allocate_storage(required_size, availability_req, latency_req, budget_val, alpha=alpha, beta=beta_val)

        if result["success"]:
            st.success("Allocation Recommendation Generated Successfully!", icon=":material/check_circle:")

            st.subheader("🎯 Recommendation Summary")
            
            # Recommendation Header Banner (No Truncation)
            with st.container(border=True):
                m_top1, m_top2 = st.columns([3, 1])
                with m_top1:
                    st.caption("RECOMMENDED STORAGE TIER")
                    st.markdown(f"### 📦 {result['tier_name']}")
                    st.markdown(":green-badge[● Optimal Choice] :blue-badge[SLA Compliant]")
                with m_top2:
                    st.caption("ESTIMATED MONTHLY COST")
                    st.markdown(f"### **${result['cost_estimate']:,.2f}**")
                    st.caption(f"Capacity: {required_size:,.1f} GB")

                st.markdown("---")

                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Guaranteed SLA", f"{result['availability_prediction']}%")
                m_col2.metric("Access Latency", f"{result['latency_prediction']} ms")
                m_col3.metric("Cost Weight (α)", f"{alpha:.1f}")
                m_col4.metric("Availability Weight (β)", f"{beta_val:.1f}")

            # Candidate Tier Scoring Breakdown Table
            st.subheader("📊 Candidate Tier Scoring Breakdown")
            st.caption("Normalized dual-objective scoring matrix across eligible candidate tiers ($C_{norm}$ = Normalized Cost, $U_{norm}$ = Normalized Unavailability):")
            
            if "scoring_breakdown" in result:
                breakdown_rows = []
                for item in result["scoring_breakdown"]:
                    breakdown_rows.append({
                        "Status": "⭐ RECOMMENDED" if item["is_selected"] else "Eligible",
                        "Storage Tier": item["tier_name"],
                        "Cost / GB ($)": f"${item['cost_per_gb']:.3f}",
                        "Total Monthly Cost ($)": f"${item['total_cost']:,.2f}",
                        "SLA Availability (%)": f"{item['sla_availability']}%",
                        "Access Latency (ms)": f"{item['access_latency']} ms",
                        "Norm Cost (C_norm)": f"{item['c_norm']:.4f}",
                        "Norm Unavail (U_norm)": f"{item['u_norm']:.4f}",
                        "Weighted Score": f"{item['score']:.4f}"
                    })
                st.dataframe(pd.DataFrame(breakdown_rows), width="stretch")

            # Comparative Evaluation Table
            st.subheader("⚖️ Algorithm Comparative Benchmark")
            st.caption("Performance comparison between the proposed α-β Dual-Objective Heuristic and traditional baseline algorithms:")

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
            st.dataframe(pd.DataFrame(comparison_rows), width="stretch")

            # Alpha Sensitivity Curve
            st.subheader("📈 Cost Weight Sensitivity Curve (α vs Monthly Spend)")
            sensitivity_data = []
            for a_test in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
                b_test = round(1.0 - a_test, 2)
                res_test = heuristic.allocate_storage(required_size, availability_req, latency_req, budget_val, alpha=a_test, beta=b_test)
                if res_test["success"]:
                    sensitivity_data.append({
                        "Cost Weight (α)": a_test,
                        "Availability Weight (β)": b_test,
                        "Recommended Tier": res_test["tier_name"],
                        "Estimated Cost ($)": res_test["cost_estimate"]
                    })
            if sensitivity_data:
                sens_df = pd.DataFrame(sensitivity_data)
                fig_sens = px.line(
                    sens_df,
                    x="Cost Weight (α)",
                    y="Estimated Cost ($)",
                    text="Recommended Tier",
                    markers=True,
                    title="Impact of Cost Weight (α) on Tier Selection & Monthly Cost",
                    template="plotly_white"
                )
                fig_sens.update_traces(
                    line=dict(color="#2563EB", width=3),
                    marker=dict(size=8, color="#059669"),
                    textposition="top center"
                )
                fig_sens.update_layout(
                    paper_bgcolor="#FFFFFF",
                    plot_bgcolor="#F8FAFC",
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                st.plotly_chart(fig_sens, width="stretch")

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
            st.toast("Allocation successfully logged to database!", icon="💾")

        else:
            st.error("Failed to generate recommendation.", icon=":material/error:")
            st.warning(result["message"])

    # Show available tiers reference
    with st.expander("🔍 View Active Storage Tier Catalog"):
        tiers_df = database.get_storage_tiers()
        tiers_df_display = tiers_df.rename(columns={
            "id": "Tier ID",
            "name": "Tier Name",
            "cost_per_gb": "Cost per GB ($)",
            "sla_availability": "SLA Availability (%)",
            "access_latency": "Access Latency (ms)"
        })
        st.dataframe(tiers_df_display, width="stretch")

