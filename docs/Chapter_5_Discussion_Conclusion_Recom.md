# CHAPTER FIVE: DISCUSSION, CONCLUSION AND RECOMMENDATIONS

## 5.0 Introduction
This chapter synthesizes the empirical findings, algorithmic evaluations, and practical contributions presented in Chapter Four. It evaluates how effectively the proposed **Heuristics Approach to Storage Resource Allocation for Cost Reduction and SLA-Aware Availability** addresses the core research problem formulated in Chapter One: overcoming the financial inefficiencies and SLA violation risks inherent in static cloud storage allocation policies.

The discussion interprets experimental results against theoretical baseline algorithms (First Fit, Best Fit, and Worst Fit), maps implementation outcomes directly to the initial research objectives, outlines practical implications for Cloud Service Providers (CSPs) and Enterprise IT Infrastructure Managers, acknowledges system limitations, and offers actionable recommendations for future research.

---

## 5.1 Discussion of Empirical Findings

### 5.1.1 Quantitative Cost Reduction and Efficiency Gains
The empirical benchmarks conducted in Chapter Four across 500 synthetic workload allocation requests conclusively validate the financial efficacy of the dual-objective heuristic model. Key quantitative achievements include:
1. **17.81% Total Cost Reduction**: The proposed multi-objective heuristic ($\alpha=0.5, \beta=0.5$) achieved a total spend of **$31,370.00** across 500 requests, compared to **$38,165.00** incurred by traditional First Fit and Worst Fit static allocation rules. This represents an absolute saving of **$6,795.00** ($13.59 saved per request on average).
2. **Zero SLA Violation Rate (100% Availability Compliance)**: Across all 500 allocation requests, the system maintained a **0.00% SLA violation rate**. Hard constraint pre-filtering successfully eliminated under-provisioned storage tiers prior to multi-objective score evaluation, ensuring that every allocated tier strictly satisfied or exceeded the workload's minimum availability requirement.
3. **Sub-5ms Execution Latency**: Algorithm execution averaged **2.8 milliseconds** per request, proving that multi-objective greedy scoring with vector-normalized scaling introduces negligible computational overhead and is fully suitable for real-time cloud management platforms (CMPs).

---

### 5.1.2 Automated Storage Sizing & Workload Awareness
A critical enhancement implemented in response to industry best practices is the **Automatic Storage Size Suggestion Engine**. Conventional CMPs require IT administrators to manually estimate storage volume requirements in raw gigabytes—a practice prone to human error, over-provisioning, and budget waste. 

By embedding empirical growth formulas across five enterprise workload profiles (Relational Databases, HD Media Streaming, IoT Log Analytics, Document CMS, and Cold Archives), the platform automatically calculates recommended storage capacities. For example:
- **IoT & Log Analytics**: Automatically computes required capacity ($S_{\text{req}} = \frac{\text{Devices} \times \text{Daily Log MB} \times \text{Retention Days}}{1024}$) to accommodate log growth without manual guesswork.
- **Relational Databases (OLTP)**: Dynamically scales capacity based on active user concurrency and monthly transaction throughput.

Empirical testing (Test Cases TC-11 and TC-12) confirmed that automated workload sizing eliminates initial configuration errors while seamlessly feeding accurate storage requirements into the dual-objective allocation engine.

---

### 5.1.3 Theoretical Interpretation of Algorithm Performance
The comparative performance of the evaluated allocation strategies highlights fundamental algorithmic trade-offs:

```
                  Cost Minimization Axis --->
(Low Cost) Object Tier <------------------------> Block Tier (High Cost)
                 <--- SLA Availability Axis
(Low SLA: 99.0%) Object Tier <-------------------> Block Tier (High SLA: 99.999%)

[Static First Fit]   ---> Picks first eligible tier in order (often over-provisions)
[Static Best Fit]    ---> Minimizes SLA slack (can select higher-cost tier)
[Static Worst Fit]   ---> Maximizes SLA slack (consistently highest cost)
[Proposed Heuristic] ---> Balances Cost & SLA via Min-Max Normalized Score (Alpha-Beta)
```

- **First Fit (FF)**: Scans storage tiers in static database order (Block $\rightarrow$ File $\rightarrow$ Object). When high-availability workloads request storage, FF selects Block Storage immediately without evaluating lower-cost alternatives that might still fulfill SLA bounds, leading to an elevated mean cost of **$76.33/request**.
- **Worst Fit (WF)**: Selects the tier with maximum excess availability slack. This strategy over-provisions every workload to the highest-performing tier (Block Storage at $0.15/GB), resulting in maximum operational spend (**$38,165.00** total).
- **Proposed Dual-Objective Heuristic ($\alpha-\beta$)**: By dynamically mapping both cost and unavailability to a normalized $[0, 1]$ interval via Min-Max scaling, the proposed algorithm evaluates true multi-objective trade-offs. Setting $\alpha=0.5, \beta=0.5$ yields a balanced distribution that selects Object Storage ($0.02/GB) or File Storage ($0.08/GB) whenever latency and availability constraints permit, capturing maximum cost savings without compromising SLA contracts.

---

## 5.2 Objective Verification Matrix
Table 5.1 maps the initial research objectives formulated in Chapter One (Section 1.4) against the technical implementations in Chapter Three and empirical validation results in Chapter Four.

### Table 5.1: Research Objectives vs. Implementation & Validation Evidence
| Chapter 1 Initial Research Objective | Chapter 3 & 4 Implementation Feature | Empirical Verification Evidence (Chapter 4) | Objective Status |
| :--- | :--- | :--- | :---: |
| **Objective 1**: To review existing cloud storage allocation mechanisms and identify cost/SLA trade-off gaps. | Chapter 2 Literature Survey & Chapter 3 Problem Formalization. | Identified static rule limitations (First Fit, Best Fit, Worst Fit over-provisioning). | **FULLY ACHIEVED** |
| **Objective 2**: To design a dual-objective heuristic algorithm balancing cost reduction and SLA availability. | Implemented Min-Max normalized scoring ($\alpha \cdot C_{\text{norm}} + \beta \cdot U_{\text{norm}}$) in `heuristic.py`. | Benchmark of 500 requests demonstrated **17.81% cost savings** ($62.74 vs $76.33 mean). | **FULLY ACHIEVED** |
| **Objective 3**: To develop an automated workload profile estimation model for storage size recommendations. | Implemented Workload Auto-Suggest Engine in `heuristic.py` & `modules/allocation.py`. | Test Cases TC-11 & TC-12 validated accurate storage sizing across 5 enterprise workload profiles. | **FULLY ACHIEVED** |
| **Objective 4**: To construct a functional prototype system for interactive simulation and evaluation. | Single-page Streamlit web app (`app.py`, `modules/`) with real-time UI views (Figures 4.1–4.4). | Interactive UI captured in high-resolution figures; tested across 12 automated test cases. | **FULLY ACHIEVED** |
| **Objective 5**: To implement persistent allocation logging and audit reporting mechanisms. | SQLite relational schema (`storage_allocation.db`) and CSV export in `database.py` & `reporting.py`. | Test Case TC-05 & TC-08 verified database persistence and seamless CSV export. | **FULLY ACHIEVED** |
| **Objective 6**: To empirically evaluate system performance under varying workloads and trade-off weights. | Sensitivity analysis across $\alpha \in [0.0, 1.0]$ and 500-request workload benchmark. | Tables 4.3 & 4.4 documented cost curves, tier selection shifts, and 0% SLA violation rates. | **FULLY ACHIEVED** |

---

## 5.3 Comparison with Baseline Systems and Literature
The proposed system advances the state of cloud management platforms (CMPs) in several key dimensions:

1. **Dynamic Scaling vs. Static Rules**: Existing commercial CMP tools often rely on static threshold rules (e.g., "Always assign SQL databases to SSD Block Storage"). In contrast, our platform dynamically computes candidate tier scores based on runtime cost vectors and active SLA bounds.
2. **Automated Workload Estimation vs. Manual Guesswork**: Unlike standard cloud calculators that require users to input exact gigabyte values, our platform incorporates domain-specific workload estimation profiles, bridging the gap between application architecture requirements and cloud infrastructure provisioning.
3. **Transparent Trade-off Control ($\alpha/\beta$)**: System administrators can continuously tune trade-off preferences using visual slider controls. Setting $\alpha=0.8$ prioritizes cost reduction for non-critical dev/test environments, while $\alpha=0.2$ prioritizes high availability for mission-critical enterprise applications.

---

## 5.4 Practical Implications

### 5.4.1 For Cloud Service Providers (CSPs)
- **Optimized Tier Utilization**: CSPs can deploy this heuristic within automated provisioning gateways to shift lower-priority workloads onto under-utilized Object and File storage tiers, freeing up premium high-speed Block storage capacity.
- **Differentiated SLA Products**: CSPs can offer dynamic pricing tiers based on explicit $\alpha-\beta$ trade-off profiles, enabling tiered service offerings tailored to enterprise budget constraints.

### 5.4.2 For Enterprise IT Infrastructure Managers
- **Substantial Cost Savings**: Enterprise organizations managing multi-terabyte cloud deployments can reduce storage spend by **15% to 20%** without increasing SLA breach liabilities.
- **Streamlined IT Governance**: The persistent SQLite audit log provides complete historical transparency for compliance auditing, internal cost chargeback, and capacity planning.

---

## 5.5 Limitations of the Study
Despite achieving strong empirical results, the following limitations should be acknowledged:
1. **Synthetic Workload Benchmark**: Benchmark evaluations were conducted using a synthetic dataset of 500 requests rather than live production telemetry from public cloud providers (AWS S3, Azure Blob, Google Cloud Storage).
2. **Static Pricing Tiers**: Storage tier pricing was modeled as fixed unit rates ($0.15, $0.08, $0.02 per GB/month). Real-world public cloud pricing includes dynamic data egress fees, API request transaction costs (GET/PUT), and multi-region replication surcharges.
3. **Single-Region Scope**: The mathematical model assumes all candidate storage tiers reside within a single availability zone or region, without accounting for inter-region network transfer latency.

---

## 5.6 Key Contributions of the Research
This project delivers three primary contributions to the field of cloud computing and software engineering:
1. **Algorithmic Contribution**: Formulated and validated a multi-objective greedy heuristic combining hard constraint pre-filtering with Min-Max normalized dual-objective scoring ($\alpha \cdot C_{\text{norm}} + \beta \cdot U_{\text{norm}}$).
2. **Software Artifact Contribution**: Designed, developed, and tested an open-source, interactive web dashboard featuring an Automatic Storage Size Suggestion Engine, real-time baseline comparisons, and SQLite transaction logging.
3. **Empirical Evidence Contribution**: Provided empirical benchmark data demonstrating **17.81% cost savings** under **100% SLA availability compliance** across 500 allocation scenarios.

---

## 5.7 Recommendations for Future Work
To extend the scope and impact of this research, future studies should consider the following directions:
1. **Integration with Live Cloud Provider APIs**: Extend the data access layer to dynamically query real-time pricing and availability metrics from AWS CloudWatch, Azure Monitor, and Google Cloud Billing APIs.
2. **Predictive Machine Learning Workload Forecasting**: Integrate time-series machine learning models (e.g., ARIMA, LSTM, Facebook Prophet) into the Auto-Suggest Engine to forecast seasonal storage growth automatically based on historical usage telemetry.
3. **Multi-Cloud and Multi-Region Replication**: Expand the optimization model to account for multi-cloud storage tiering, data egress fees, cross-region replication latency, and regulatory data residency requirements (GDPR, HIPAA).

---

## 5.8 Chapter Summary and Conclusion
This study successfully designed, implemented, and evaluated a heuristic approach to cloud storage resource allocation. By combining automated workload storage size estimation with a dual-objective Min-Max normalized scoring model, the system addresses the dual challenges of cloud cost optimization and SLA compliance. The empirical evaluation verified a **17.81% reduction in storage expenditure** alongside a **0% SLA violation rate**. The resulting software prototype, detailed documentation, and benchmark datasets fulfill all initial research objectives and provide a scalable foundation for future intelligent cloud resource management platforms.
