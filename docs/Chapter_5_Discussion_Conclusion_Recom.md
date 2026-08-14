# CHAPTER FIVE: DISCUSSION, CONCLUSION AND RECOMMENDATIONS

## 5.0 Introduction
This chapter interprets the empirical findings presented in Chapter Four, evaluates the broader theoretical and practical implications of the research, maps the achieved results back to the original project objectives formulated in Chapter One, discusses study limitations, highlights key contributions to computer technology, and provides actionable recommendations for industrial cloud deployment and future academic research.

---

## 5.1 Summary of Findings
The primary goal of this research was to design, implement, and evaluate a multi-objective heuristic resource allocation algorithm capable of optimizing cloud storage placement for cost reduction while satisfying strict Service Level Agreement (SLA) availability and access latency requirements.

Key empirical findings derived from the software implementation and the 500-request workload benchmark evaluation include:

1. **Quantified Cost Reduction**: The proposed weighted dual-objective heuristic achieved an average allocation cost of **$62.74** per request, representing a **17.81% overall cost savings** compared to conventional static baseline allocation policies such as First Fit ($76.33) and Worst Fit ($76.33). Across 500 allocation requests, the proposed system saved **$6,795.00** in simulated cloud infrastructure expenditure.
2. **Zero SLA Violation Rate**: The hard constraint pre-filtering phase guaranteed **100% SLA availability compliance** and latency bounds satisfaction across all 500 benchmark allocation requests. No workload was assigned to an under-provisioned storage tier.
3. **Controllable Trade-off Dynamics**: Parameter sensitivity analysis confirmed that varying the cost priority weight factor ($\alpha$) smoothly shifts resource recommendations between high-availability configurations ($\alpha=0.0$, mean cost $75.33, availability 99.998%) and hyper-cost-optimized configurations ($\alpha=1.0$, mean cost $44.99, availability 99.110%).
4. **Sub-5ms Execution Latency**: Vectorized Pandas calculations and Min-Max scaling executed in under 5 milliseconds per request (mean execution latency of 2.8ms), satisfying non-functional real-time responsiveness requirements.

---

## 5.2 Interpretation of Results
Traditional cloud storage allocation policies exhibit structural limitations in modern multi-tier enterprise environments:
- **First Fit (FF)** selects the first tier meeting SLA requirements based on database insertion order, frequently over-allocating workloads to expensive high-tier block storage.
- **Worst Fit (WF)** selects candidate tiers with maximum availability headroom, causing systematic over-provisioning and inflated operational expenditures.
- **Best Fit (BF)** minimizes availability headroom to reduce costs, but lacks weighted multi-attribute trade-off controls when multiple constraints compete.

The proposed **multi-objective greedy scoring heuristic** resolves these deficiencies by mapping heterogeneous storage metrics (cost per GB in dollars and unavailability percentage) into a standardized, dimensionless $[0, 1]$ domain using Min-Max scaling:

$$\text{Score}(i) = \alpha \cdot C_{\text{norm}}(i) + \beta \cdot U_{\text{norm}}(i)$$

By coupling hard constraint filtering (guaranteeing that SLA availability and latency thresholds are met) with soft weighted scoring, the system eliminates over-provisioning while providing cloud infrastructure managers with explicit quantitative knobs ($\alpha, \beta$) to adapt storage allocation strategies based on dynamic business priorities and quarterly budget constraints.

---

## 5.3 Achievement of Project Objectives
The success of this study is evaluated against the specific research objectives stated in Chapter One (Section 1.4). Table 5.1 provides a detailed mapping between each objective and its corresponding evidence within the dissertation.

### Table 5.1: Mapping of Achieved Results to Research Objectives
| Project Objective (Section 1.4) | Achievement Status | Implementation Evidence & Chapter Reference |
| :--- | :---: | :--- |
| **Objective 1**: Survey existing storage resource allocation approaches and their deficiencies in cost and SLA-awareness. | **ACHIEVED** | Comprehensive literature review in **Chapter Two** (Sections 2.2–2.8) identifying structural deficiencies in static First Fit, Best Fit, and Worst Fit algorithms. |
| **Objective 2**: Develop a heuristic-based model for storage resource allocation with cost and SLA as two-fold objectives. | **ACHIEVED** | Mathematical formulation of the Min-Max normalized scoring model and pseudocode presented in **Chapter Three** (Section 3.5), implemented in `heuristic.py`. |
| **Objective 3**: Implement an interactive web-based simulation application to demonstrate real-time storage recommendation and analytics. | **ACHIEVED** | Streamlit application (`app.py`, `modules/`) featuring allocation input forms, baseline comparative tables, Plotly analytics, and SQLite logging (**Chapter Four**, Sections 4.2–4.3). |
| **Objective 4**: Evaluate performance against baseline algorithms using empirical benchmark datasets. | **ACHIEVED** | Executed 500-request empirical workload benchmark in **Chapter Four** (Section 4.6), demonstrating **17.81% cost savings** and **100% SLA compliance**. |

---

## 5.4 Comparison with Existing Systems
Compared to standard static allocation modules found in commercial Cloud Management Platforms (CMPs) or basic cloud provisioning scripts:
- **Static Rules vs. Dynamic Min-Max Scaling**: Static systems apply rigid, unyielding thresholds that cannot adapt when market pricing or budget constraints fluctuate. The proposed system normalizes cost and unavailability dynamically relative to candidate tier sets.
- **Single-Objective vs. Dual-Objective**: Legacy systems optimize cost or availability in isolation. The proposed solution balances both dimensions along the continuous $\alpha/\beta$ weight spectrum.
- **Auditability & Traceability**: Integrated SQLite transaction logging ensures full auditability for compliance verification.

---

## 5.5 Limitations of the Study
Despite achieving positive empirical results, the study has certain limitations:
1. **Synthetic Workload Traces**: Evaluation was conducted using simulated cloud workload profiles rather than production multi-tenant telemetry traces.
2. **Fixed Tier Pricing Model**: Candidate storage tiers were modeled on public cloud tiers (AWS EBS, Azure Files, GCP Object Storage) using fixed unit pricing rather than dynamic spot market prices.
3. **Single-Region Latency Scope**: Access latency was modeled as a static property without accounting for dynamic WAN network jitter or multi-region replication overheads.

---

## 5.6 Implications of the Study
The outcomes of this project offer practical value for cloud practitioners:
- **For Cloud Service Providers (CSPs)**: Implementing multi-objective scoring minimizes tier over-allocation, freeing up high-performance block storage for premium workloads.
- **For Enterprise IT Infrastructure Managers**: The interactive weight slider provides non-technical infrastructure managers with an intuitive tool to adjust storage procurement strategies based on budget cycles.

---

## 5.7 Summary of Project Contributions
This project makes three key contributions to computer technology and cloud resource management:
1. **Algorithmic Contribution**: A lightweight, mathematically rigorous multi-objective greedy heuristic that standardizes cost and unavailability dimensions via Min-Max scaling.
2. **Software Artifact**: A fully functional, open-source Streamlit simulation application with real-time baseline comparative evaluation and SQLite log persistence.
3. **Empirical Benchmark**: Empirical proof of a **17.81% cost savings** under **100% SLA availability compliance** across 500 benchmark allocation scenarios.

---

## 5.8 Recommendations for Future Work
To extend the capabilities of this research, future studies should consider:
1. **Machine Learning Predictive Integration**: Incorporating predictive ML models (e.g., LSTM or XGBoost) to forecast seasonal storage demand spikes and auto-scale allocations.
2. **Real-Time Telemetry API Integration**: Connecting the heuristic engine to live cloud APIs (AWS CloudWatch, Azure Monitor, Prometheus) to dynamically incorporate real-time latency telemetry.
3. **Multi-Cloud Migration & Replication**: Expanding the model to support multi-cloud data replication policies and dynamic inter-cloud data transfer cost calculations.

---

## 5.9 Chapter Summary
This chapter discussed the empirical findings, theoretical implications, project limitations, contributions, and future recommendations for the cloud storage allocation optimizer. The research successfully met all initial objectives, demonstrating that dual-objective heuristic scoring with Min-Max normalization significantly reduces cloud storage expenditure (17.81% savings) while maintaining strict SLA availability compliance (100%).
