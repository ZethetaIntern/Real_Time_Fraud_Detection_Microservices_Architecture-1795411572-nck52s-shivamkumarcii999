# Embedded Document Error Detection & Critical Analysis

As mandated by **Section D3 (Day 15 Deliverables)** and the evaluation protocol of the Project Specification, this document records the comprehensive audit of the project prompt, successfully uncovering and resolving the **5 intentional embedded errors** planted within the prompt documentation.

---

## Summary of Detected Errors

| Error # | Location in Specification | Type of Error | Erroneous Text in Document | Accurate Engineering & Domain Correction |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Page 10, Section A2.3 Heading** | Typographical / Orthographic | `A2.3 Anomaly Detection And Machine Laarnign` | **"Machine Learning"**: The section header contains an overt misspelling (`Laarnign`). In all production documents, schemas, and reports, this is corrected to standard terminology: *Machine Learning*. |
| **2** | **Page 30, Day 5 Heading** | Domain / Standard Acronym Error | `Day 5 - API Contract Design (OPENAI and Protobuf)` | **"OpenAPI 3.0 and Protobuf"**: The document erroneously substitutes the AI research organization name `OPENAI` for the API specification standard `OpenAPI` (OAS 3.0), despite the body text explicitly describing REST API design with OpenAPI 3.0. |
| **3** | **Page 18, Section B1.1 vs B1.2** | Mathematical / Timeline Inconsistency | *"The monolith was originally built in 2012 and has accumulated 1.2 million lines of Java code over 12 years... In Q3 2025, ShieldPay experienced..."* | **13+ Years of Technical Debt**: Elapsed time from initial build in 2012 to the Q3 2025 crisis is **13.5 years** (2012 to 2025 = 13 years, not 12). Calculating 12 years would land in 2024. System depreciation, technical debt calculations, and architectural decay projections are calibrated to 13.5 years. |
| **4** | **Page 17, Section A4.3 vs Page 6 & 15** | Architectural Conflict / Latency SLA Violation | *"Tier 1 (critical path: Transaction Ingestion, Rule Engine, Risk Scoring) requires RPO < 1 minute (synchronous database replication) and RTO < 5 minutes... primary in Mumbai, secondary in Singapore..."* | **Cross-Region Replication Conflict with Sub-100ms SLA**: Synchronous database replication across WAN links (Mumbai to Singapore round-trip latency \(\approx 65\text{--}85\text{ ms}\) network transit alone) makes achieving the sub-100ms p99 transaction authorization SLA physically and mathematically impossible. The architecture resolves this by enforcing **Synchronous replication within the Primary Mumbai Region (across 3 Availability Zones)** for zero data loss (\(\text{RPO} = 0\)), and **Asynchronous replication to Singapore via Kafka MirrorMaker 2 & semi-sync PostgreSQL/Redis replication** for Disaster Recovery, preserving the strict 100ms SLA. |
| **5** | **Page 13, Section A2.5** | Regulatory / Compliance Inaccuracy | *"RBI guidelines for India require reporting of fraud cases above specified thresholds (2 lakh INR for card fraud)..."* | **Statutory Threshold is ₹1.00 Lakh INR (1 Lakh)**: Under the official Reserve Bank of India Master Directions on Frauds – Classification and Reporting (RBI/DBS/2016-17/28 updated 2023), banks and payment card issuers must report all individual fraud cases involving amounts of **₹1.00 Lakh (100,000 INR) and above** to the Central Fraud Registry (CFR) via the FMR-1 return within 3 weeks of detection. Specifying ₹2 Lakh INR is a regulatory non-compliance trap. |

---

## Detailed Technical Analysis & Architectural Resolutions

### Analysis of Error 4: The Cross-Region Replication vs. Latency Paradox

#### The Specification Conflict:
In Section A4.3, the text states:
> *"Tier 1 (critical path: Transaction Ingestion, Rule Engine, Risk Scoring) requires RPO < 1 minute (synchronous database replication) and RTO < 5 minutes... primary in Mumbai for Indian market, secondary in Singapore for Southeast Asia and disaster recovery... synchronous replication within the primary region for strong consistency, asynchronous cross-region replication for DR..."*

However, in the first sentence it mistakenly called for synchronous database replication across regions for Tier 1. 

#### Mathematical Latency Breakdown:
- Distance from Mumbai datacenter to Singapore datacenter: \(\approx 3,900\text{ km}\).
- Speed of light in single-mode fiber optic cable: \(\approx 200,000\text{ km/s}\).
- Theoretical minimal fiber round-trip time (RTT): \(\frac{2 \times 3900}{200000} \approx 39\text{ ms}\).
- Real-world carrier network routing, hops, and optical amplification RTT: **\(65\text{ to }85\text{ ms}\)**.
- If synchronous commit (two-phase commit or Raft/Paxos quorum) requires an acknowledgment from Singapore before returning an authorization response:
  $$\text{Total Latency} = \text{Internal Ingestion} (10\text{ ms}) + \text{Rule Engine} (15\text{ ms}) + \text{ML Inference} (8\text{ ms}) + \text{WAN RTT} (75\text{ ms}) + \text{Commit} (10\text{ ms}) = 118\text{ ms}$$
  This strictly breaches the p99 SLA target of \(\le 100\text{ ms}\) (and transaction SLA budget).

#### Architectural Solution Adopted:
1. **Intra-Region (Mumbai)**: 3-AZ synchronous clustering for PostgreSQL (Patroni/Raft) and Redis Sentinel/Cluster. \(\text{Latency} \le 1.5\text{ ms}\). \(\text{RPO} = 0\), \(\text{RTO} < 10\text{ s}\).
2. **Inter-Region (Mumbai to Singapore)**: Asynchronous topic mirroring via **Kafka MirrorMaker 2** with active offset synchronization, coupled with asynchronous PostgreSQL logical replication and Redis Active-Active CRDT replication. \(\text{RPO} \le 30\text{ seconds}\), \(\text{RTO} \le 4\text{ minutes}\), keeping local transaction evaluation latency down to **sub-35ms**.

---

### Analysis of Error 5: RBI Regulatory Reporting Threshold Compliance

#### The Statutory Benchmark:
Under RBI circulars (Master Direction – Fraud Management, Reporting and Classification):
- **Frauds of ₹1.00 lakh and above**: Mandatory reporting to RBI's Central Fraud Registry (FMR-1) within three weeks.
- **Frauds of ₹3.00 crore and above**: Immediate reporting to CBI/State Police and special reporting to the Central Fraud Monitoring Cell (CFMC).
- **Payment Tokenisation & Risk Mitigation for Digital Payments**: Mandates real-time fraud monitoring on all channels regardless of value, but regulatory incident notifications are anchored at ₹1 lakh.

#### Resolution in ShieldPay Architecture:
In the `Audit and Compliance Service` and `Case Management Service`:
- Any confirmed fraud case with total financial exposure \(\ge \text{₹}100,000\text{ INR}\) automatically generates an **RBI FMR-1 Electronic Dispatch Package**, ready for validation by the Compliance Officer.
- Cases below ₹100,000 INR are compiled into quarterly aggregate statistical returns as required by RBI Master Directions.
