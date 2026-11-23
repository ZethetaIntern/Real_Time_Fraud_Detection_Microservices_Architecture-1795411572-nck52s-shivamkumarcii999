# AI-Assisted Engineering Policy & Transparency Statement

In strict compliance with **Section E5 (AI-Assisted Development Policy)** of the Project Guidelines, this document provides a comprehensive acknowledgment and audit record of how AI assistance was leveraged in architecting, specifying, and validating the ShieldPay Real-Time Fraud Detection Platform.

---

## 1. Permitted Scopes of AI Usage

In accordance with Section E5:
- **Research & Domain Immersion**: AI tools were utilized to research edge-case fraud topologies (e.g., synthetic identity cultivation cycles, triangulation logistics, SIM-swap timing windows), comparative microservices benchmarks (gRPC vs REST serialisation costs), and regulatory nuances (RBI Master Directions on Frauds, PCI DSS v4.0 SAQ requirements, and GDPR Article 17 right-to-erasure conflicts).
- **Drafting & Syntax Generation**: AI was employed to assist in generating boilerplate syntax for OpenAPI 3.0 YAML specifications, Protocol Buffer v3 definitions, Kubernetes YAML manifests, Prometheus PromQL alert definitions, and Istio Envoy filter configurations.
- **Embedded Error Audit**: AI pattern recognition was utilized to thoroughly cross-verify the document specification, successfully pinpointing the 5 embedded errors (Page 10 "Laarnign", Page 30 "OPENAI", Page 18 12-vs-13.5 years, Page 17 cross-region sync replication latency conflict, and Page 13 ₹2 lakh vs ₹1 lakh RBI statutory reporting threshold).

---

## 2. Human Verification, Customization & Independent Defense

All architecture schemas, mathematical latency budgets, algorithm implementations, and design decisions have been rigorously inspected, mathematically verified, and customized specifically for ShieldPay's high-throughput payment environment:
1. **Latency Budgets**: Derived from physical fiber-optic speed of light limits and benchmarked system latencies (Kong + Go + Redis + ONNX).
2. **Rule Schema**: Hand-engineered to support multi-variable sliding windows, nested boolean AST evaluation, and role-based promotion lifecycles.
3. **Graph Architecture**: Tailored for native Cypher traversals addressing specific retail and ATM cash-out fraud topologies.
4. **Codebase Implementation**: The accompanying Python implementation (`src/`) has been verified through an automated end-to-end test suite (`tests/`) running in isolated sandboxed environments.
