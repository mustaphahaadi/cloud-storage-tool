# CHAPTER FIVE: DISCUSSION, CONCLUSION AND RECOMMENDATIONS

## 5.0 Introduction
This chapter synthesizes the empirical findings, algorithmic evaluations, software achievements, and practical contributions presented in Chapter Four. It interprets how effectively the proposed **Heuristics Approach to Storage Resource Allocation for Cost Reduction and SLA-Aware Availability** solves the core research problem formulated in Chapter One: overcoming the financial inefficiencies, manual configuration errors, and SLA violation risks inherent in static cloud storage allocation policies.

The discussion interprets experimental benchmark results against theoretical baseline algorithms (First Fit, Best Fit, and Worst Fit), maps implementation outcomes directly to initial research objectives, outlines practical implications for Cloud Service Providers (CSPs) and Enterprise IT Infrastructure Managers, details engineering challenges encountered during development, articulates project contributions, and offers actionable recommendations for future research.

---

## 5.1 Summary of Findings
The empirical benchmarks conducted in Chapter Four across 500 synthetic enterprise workload requests produced four major quantitative and operational findings:

1. **17.81% Total Cost Reduction**: The proposed multi-objective heuristic (α = 0.5, β = 0.5) achieved an aggregate expenditure of **$31,370.00** across 500 requests, compared to **$38,165.00** incurred by static First Fit and Worst Fit allocation policies. This represents a net saving of **$6,795.00** ($13.59 saved per request on average).
2. **100% SLA Availability Compliance (0% Violation Rate)**: Across all 500 benchmark allocation requests, the system maintained a **0.00% SLA breach rate**. Hard constraint pre-filtering successfully eliminated under-provisioned candidate storage tiers prior to score evaluation, ensuring that every allocated tier strictly satisfied or exceeded the workload's minimum SLA availability target.
3. **Sub-3ms Computational Speed**: Algorithm execution averaged **2.8 milliseconds** per request, proving that multi-objective greedy scoring with Min-Max vector normalization introduces negligible computational overhead and is suitable for real-time cloud management platforms (CMPs).
4. **Automated Sizing Accuracy**: The Automatic Storage Size Suggestion Engine successfully calculated storage capacity requirements across five enterprise workload profiles (OLTP Databases, HD Media Streaming, IoT Log Analytics, Document CMS, and Cold Archives), eliminating initial sizing guesswork and manual data entry errors.

---

## 5.2 Interpretation of Results
The comparative performance of the evaluated allocation strategies illustrates fundamental algorithmic trade-offs in cloud resource provisioning:

```
                  Cost Minimization Axis --->
(Low Cost) Object Tier <------------------------> Block Tier (High Cost)
                 <--- SLA Availability Axis
(Low SLA: 99.0%) Object Tier <-------------------> Block Tier (High SLA: 99.999%)

[Static First Fit]   ---> Selects first eligible tier in static database order (over-provisions)
[Static Best Fit]    ---> Minimizes SLA availability slack (can select higher-cost tiers)
[Static Worst Fit]   ---> Maximizes SLA availability slack (consistently highest operational spend)
[Proposed Heuristic] ---> Balances Cost & SLA via Min-Max Normalized Score (Alpha-Beta Trade-off)
```

- **First Fit (FF)**: Scans candidate storage tiers in static database order (Block → File → Object). When high-availability workloads request storage, FF selects Block Storage immediately without evaluating lower-cost alternatives that might still fulfill SLA bounds, leading to an elevated mean cost of **$76.33/request**.
- **Worst Fit (WF)**: Selects the tier with maximum excess availability slack. This strategy over-provisions every workload to the highest-performing tier (Block Storage at $0.15/GB), resulting in maximum operational spend (**$38,165.00** total).
- **Proposed Dual-Objective Heuristic (α - β)**: By dynamically mapping both cost and unavailability to a normalized [0, 1] interval via Min-Max scaling, the proposed algorithm evaluates true multi-objective trade-offs. Setting α = 0.5, β = 0.5 yields a balanced distribution that selects Object Storage ($0.02/GB) or File Storage ($0.08/GB) whenever latency and availability constraints permit, capturing maximum cost savings without compromising SLA contracts.

---

## 5.3 Achievement of Project Objectives
Table 5.1 maps the initial research objectives formulated in Chapter One (Section 1.4) against technical implementations in Chapter Three and empirical validation evidence from Chapter Four.

### Table 5.1: Research Objectives Verification Matrix
| Initial Research Objective (Section 1.4) | Implementation Feature / Module | Empirical Verification Evidence (Chapter 4) | Objective Status |
| :--- | :--- | :--- | :---: |
| **Objective 1**: To review existing cloud storage allocation mechanisms and identify cost/SLA trade-off gaps. | Chapter 2 Literature Survey & Chapter 3 Problem Formalization. | Identified over-provisioning and cost inefficiencies in static First Fit, Best Fit, and Worst Fit rules. | **FULLY ACHIEVED** |
| **Objective 2**: To design a dual-objective heuristic algorithm balancing cost reduction and SLA availability. | Implemented Min-Max normalized scoring (`α × C_norm + β × U_norm`) in `heuristic.py`. | Benchmark of 500 requests demonstrated **17.81% cost savings** ($62.74 vs $76.33 mean cost). | **FULLY ACHIEVED** |
| **Objective 3**: To develop an automated workload profile estimation model for storage size recommendations. | Implemented Workload Auto-Suggest Engine in `heuristic.py` & `modules/allocation.py`. | Test Cases TC-11 & TC-12 validated accurate storage sizing across 5 enterprise workload profiles. | **FULLY ACHIEVED** |
| **Objective 4**: To construct a functional prototype system for interactive simulation and evaluation. | Single-page Streamlit web platform (`app.py`, `modules/`) with real-time UI views (Figures 4.1–4.4). | Interactive UI captured in high-resolution figures; validated across 12 automated test cases. | **FULLY ACHIEVED** |
| **Objective 5**: To implement persistent allocation logging and audit reporting mechanisms. | SQLite relational schema (`storage_allocation.db`) and CSV export in `database.py` & `reporting.py`. | Test Cases TC-05 & TC-08 verified database persistence and CSV export functionality. | **FULLY ACHIEVED** |
| **Objective 6**: To empirically evaluate system performance under varying workloads and trade-off weights. | Sensitivity analysis across α ∈ [0.0, 1.0] and 500-request workload benchmark. | Tables 4.3 & 4.4 documented cost curves, tier selection shifts, and 0% SLA violation rates. | **FULLY ACHIEVED** |

---

## 5.4 Comparison with Existing Systems
The proposed cloud storage allocation platform advances beyond existing commercial Cloud Management Platforms (CMPs) and traditional allocation utilities in three main areas:

1. **Dynamic Scaling vs Static Rule Policies**: Commercial CMP tools (e.g., standard AWS or Azure policy managers) frequently rely on static threshold rules (e.g., "Always assign production databases to SSD Block Storage"). In contrast, our system dynamically calculates candidate tier scores based on runtime cost vectors and active SLA bounds.
2. **Automated Workload Estimation vs Manual Sizing Guesswork**: Standard cloud cost calculators (e.g., AWS Pricing Calculator) require users to input exact gigabyte values manually. Our platform embeds domain-specific empirical workload estimation profiles, bridging the gap between application architecture parameters and cloud storage provisioning.
3. **Explicit Trade-off Control (α / β)**: System administrators can continuously tune trade-off preferences using visual slider controls. Setting α = 0.8 prioritizes cost reduction for dev/test environments, while setting α = 0.2 prioritizes high availability for mission-critical enterprise applications.

---

## 5.5 Advantages of the New System
The implemented platform offers four key functional advantages over conventional storage provisioning methods:

- **Multi-Objective Cost & SLA Optimization**: Simultaneously minimizes operational spend and enforces SLA availability and latency bounds through Min-Max vector normalization.
- **Automated Workload Sizing**: Eliminates human sizing errors by translating high-level operational inputs (active users, transaction volume, IoT device counts, retention periods) into precise gigabyte storage recommendations.
- **Real-Time Baseline Benchmarking**: Instantly evaluates the proposed heuristic against First Fit, Best Fit, and Worst Fit algorithms, providing immediate visualization of financial savings.
- **Relational Audit Logging & Data Export**: Maintains an immutable transaction ledger in SQLite, supporting historical compliance auditing, capacity planning, and CSV data extraction.

---

## 5.6 Challenges Encountered
During system design and implementation, three major engineering challenges were encountered and resolved:

1. **Zero-Range Normalization Edge Cases**: When all eligible candidate storage tiers possess identical costs (`C_max = C_min`) or availability ratings (`U_max = U_min`), standard Min-Max scaling formulas result in division-by-zero errors. This was resolved by implementing conditional guards in `heuristic.py` that set `C_norm = 0.0` or `U_norm = 0.0` whenever range equals zero.
2. **Scaling Non-Linear SLA Percentages vs Linear Cost Vectors**: SLA availability percentages (e.g., 99.0% vs 99.999%) operate on logarithmic reliability scales, whereas cost vectors ($0.02 vs $0.15 per GB) scale linearly. Converting SLA percentages to unavailability fractions (`U = 1.0 - SLA / 100`) prior to Min-Max normalization successfully aligned the two mathematical metrics into a unified `[0, 1]` interval.
3. **Database Concurrency and Locking**: High-frequency benchmark simulation runs triggered temporary SQLite database write-lock errors (`database is locked`). This was resolved by structuring `database.py` to use short-lived connection blocks, explicit commit points, and lightweight parameterized queries.

---

## 5.7 Implications of the Study

### 5.7.1 Implications for Cloud Service Providers (CSPs)
- **Optimized Infrastructure Tiering**: CSPs can deploy this heuristic within automated cloud provisioning gateways to migrate lower-priority workloads onto under-utilized Object and File storage tiers, freeing up premium high-speed Block storage capacity.
- **Dynamic Pricing Product Offerings**: CSPs can offer flexible pricing models based on explicit α - β trade-off profiles, enabling tiered service offerings tailored to enterprise budget constraints.

### 5.7.2 Implications for Enterprise IT Infrastructure Managers
- **Substantial Financial Cost Reductions**: Enterprise IT departments managing multi-terabyte cloud deployments can reduce storage expenditure by **15% to 20%** without introducing SLA breach liabilities.
- **Enhanced IT Governance**: The persistent SQLite audit log provides complete historical transparency for compliance auditing, internal cost chargeback, and capacity planning.

---

## 5.8 Contribution of the Project
This research delivers three primary contributions to the fields of cloud computing, software engineering, and systems optimization:

1. **Algorithmic Contribution**: Formulated and validated a dual-objective greedy heuristic combining hard constraint pre-filtering with Min-Max normalized scoring (`α × C_norm + β × U_norm`).
2. **Software Artifact Contribution**: Developed, tested, and documented an open-source, interactive web platform featuring an Automatic Storage Size Suggestion Engine, real-time baseline comparisons, and SQLite transaction logging.
3. **Empirical Evidence Contribution**: Generated benchmark evaluation dataset demonstrating **17.81% cost savings** under **100% SLA availability compliance** across 500 allocation scenarios.

---

## 5.9 Recommendations for Future Work
To extend the scope and capabilities of this research, future studies should consider four key directions:

1. **Live Public Cloud Provider API Integration**: Extend `database.py` and `heuristic.py` to query dynamic pricing and SLA metrics directly from AWS S3/EBS, Azure Blob, and Google Cloud Storage billing APIs in real time.
2. **Machine Learning Workload Forecasting**: Incorporate time-series forecasting models (e.g., LSTM, Facebook Prophet, ARIMA) into the Auto-Suggest Engine to predict seasonal storage growth automatically based on historical usage telemetry.
3. **Multi-Cloud & Multi-Region Replication**: Expand the mathematical optimization model to incorporate multi-cloud tiering, cross-region replication latency, data egress charges, and regulatory compliance rules (e.g., GDPR, HIPAA).
4. **Hybrid Multi-Tier Split Allocations**: Enhance the heuristic to support split allocations across multiple tiers (e.g., allocating 80% of archival log data to Object Storage and 20% of active index data to Block Storage).

---

## 5.10 Chapter Summary and Conclusion
This study successfully designed, implemented, and evaluated a heuristic approach to cloud storage resource allocation. By combining automated workload storage size estimation with a dual-objective Min-Max normalized scoring model, the system addresses the dual challenges of cloud cost optimization and SLA availability compliance. Empirical evaluation verified a **17.81% reduction in storage expenditure** alongside a **0% SLA breach rate** across 500 benchmark allocation requests. The resulting software prototype, detailed documentation, and empirical datasets fulfill all initial research objectives and provide a scalable foundation for intelligent cloud resource management platforms.
