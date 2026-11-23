# Domain Glossary: Real-Time Fraud Detection & FinTech Architecture

This glossary defines 65 foundational and domain-specific terms across fraud detection, payments processing, microservices architecture, machine learning, and regulatory compliance, with special reference to global standards and the Indian FinTech ecosystem (RBI/NPCI).

---

## 1. Payment Infrastructure & Card Systems

1. **PAN (Primary Account Number)**: The 14-to-19 digit card number embossed on payment cards that uniquely identifies the card issuer and cardholder account. Subject to strict PCI DSS storage and masking rules.
2. **BIN / IIN (Bank Identification Number / Issuer Identification Number)**: The initial 6 to 8 digits of a payment card number that identify the issuing bank and network (e.g., Visa, Mastercard, RuPay, Amex).
3. **Card-Present (CP) Transaction**: A transaction where the physical payment card is physically swiped, dipped (EMV chip), or tapped (contactless NFC) at a Point-of-Sale (POS) terminal or ATM.
4. **Card-Not-Present (CNP) Transaction**: A transaction where the cardholder does not physically present the card to the merchant (e.g., e-commerce web checkout, in-app mobile payments, Mail Order/Telephone Order - MOTO).
5. **EMV (Europay, MasterCard, Visa)**: The global technical standard for smart payment cards and payment terminals equipped with integrated circuit chips, providing dynamic cryptographic authentication to eliminate magnetic stripe skimming.
6. **Tokenisation**: The process of replacing sensitive payment data (such as a 16-digit PAN) with an algorithmically generated, non-sensitive equivalent called a "token" that has no intrinsic value outside a specific merchant or transaction domain.
7. **CoF (Card-on-File) Tokenisation**: An RBI-mandated framework in India (effective October 2022) requiring merchants and payment aggregators to replace stored credit/debit card numbers with unique tokens issued by card networks.
8. **AFA (Additional Factor of Authentication)**: Multi-factor authentication mandated by regulators (such as RBI in India and PSD2/SCA in the EU) requiring a second credential (e.g., SMS OTP, biometric, in-app approval) for online card transactions.
9. **UPI (Unified Payments Interface)**: India's instant real-time payment system developed by the National Payments Corporation of India (NPCI), enabling inter-bank peer-to-peer (P2P) and person-to-merchant (P2M) transactions via virtual payment addresses (VPA/UPI ID).
10. **RuPay**: India's domestic card payment network launched by NPCI, featuring domestic BIN ranges and lower processing interchange fees compared to international schemes.
11. **MCC (Merchant Category Code)**: A 4-digit number assigned by card schemes to categorize a merchant's type of business (e.g., 5411 for Grocery, 7995 for Gambling, 6051 for Cryptocurrency, 4829 for Wire Transfers).
12. **Acquirer (Acquiring Bank)**: The financial institution or merchant acquirer that processes credit or debit card payments on behalf of a merchant and settles funds into the merchant's account.
13. **Issuer (Issuing Bank)**: The financial institution that issues payment cards to consumers and is responsible for verifying funds/credit and approving or declining authorization requests.
14. **Payment Gateway**: An e-commerce service that authorizes card or direct payments for e-businesses and online retailers, encrypting sensitive payment information and routing it between merchant and payment processor.
15. **Payment Aggregator (PA)**: A service provider that enables e-commerce sites and merchants to accept diverse payment instruments without needing individual merchant accounts with multiple banks.
16. **Chargeback**: A forced transaction reversal initiated by the card issuer on behalf of the cardholder, debiting the merchant's account following a disputed or fraudulent transaction.
17. **Representment**: The legal and technical dispute response process where a merchant submits evidence (proof of delivery, IP logs, 3DS authentication logs) to challenge and overturn an unjustified chargeback.

---

## 2. Fraud Typologies & Attack Vectors

18. **Account Takeover (ATO)**: A form of identity theft where an attacker gains unauthorized control over a legitimate user's financial account using compromised credentials (from credential stuffing, phishing, or malware).
19. **Synthetic Identity Fraud**: Creating fictitious identities by combining real, stolen, and fabricated personal data (e.g., real Aadhaar/SSN with fictitious names, addresses, and birth dates) to establish credit accounts and execute "bust-out" fraud.
20. **Enumeration Attack (BIN Attack / Carding)**: Automated testing of thousands of generated card numbers against payment endpoints using small-value transactions to detect valid PANs, expiration dates, and CVVs.
21. **Friendly Fraud (First-Party Fraud)**: When a legitimate consumer or family member makes an online purchase and subsequently files an illegitimate chargeback claiming they never authorized or received the item.
22. **Triangulation Fraud**: A three-way scheme where an illicit seller lists items on a mock storefront, accepts money from a legitimate buyer, purchases the product on a legitimate retailer using stolen card details, and has it delivered to the customer.
23. **Money Mule**: An individual who transfers illegally acquired funds on behalf of organized crime syndicates, often recruited through work-from-home scams or romantic solicitations to launder illicit capital through intermediate bank accounts.
24. **SIM-Swap Fraud**: An attack where an adversary illicitly convinces a mobile telecom carrier to port a victim's phone number to a criminal-controlled SIM card, allowing the attacker to intercept SMS OTPs for banking authentication.
25. **UPI Phishing / Fake Collect Request**: Social engineering attacks where fraudsters send UPI collect requests posing as lottery disbursements, refunds, or military personnel buyers, deceiving victims into entering their UPI PIN and authorizing outgoing debits.
26. **Bust-Out Fraud**: When a newly opened account or credit line is deliberately cultivated with regular on-time payments to increase the credit limit, followed by maxing out the entire line of credit and disappearing.
27. **Counterfeit Card Fraud (Skimming)**: Illicitly copying magnetic stripe track data from POS terminals or ATMs using skimming hardware to create clone cards for fraudulent transactions.
28. **Card-Never-Received Fraud**: Interception of newly minted cards or replacement cards during postal or courier delivery before they reach the rightful cardholder.

---

## 3. Fraud Detection Metrics & Risk Concepts

29. **FPR (False Positive Rate)**: The ratio of legitimate transactions erroneously flagged or declined as fraudulent over the total number of legitimate transactions (\(FP / (FP + TN)\)). High FPR causes severe customer friction.
30. **FNR (False Negative Rate)**: The ratio of fraudulent transactions missed by the detection system over the total number of actual fraudulent transactions (\(FN / (FN + TP)\)). Direct driver of fraud financial losses.
31. **Detection Rate (Recall / Sensitivity)**: The proportion of true fraud incidents successfully identified and intercepted by the fraud engine (\(TP / (TP + FN)\)).
32. **Precision (Positive Predictive Value)**: The proportion of flagged transactions that are genuinely fraudulent (\(TP / (TP + FP)\)).
33. **AUC-ROC (Area Under Receiver Operating Characteristic)**: A performance measurement for classification models across various threshold settings, plotting True Positive Rate vs False Positive Rate.
34. **Velocity Checking**: Statistical rules and aggregations that evaluate transaction velocity over defined sliding time windows (e.g., count or sum of transactions from cardholder in last 1, 5, 15, or 60 minutes).
35. **Device Fingerprinting**: Collecting browser, operating system, canvas rendering, IP address, screen resolution, and hardware properties to uniquely identify client devices across sessions and detect device reuse.
36. **IP Geolocation & Impossible Travel**: Comparing the geographic locations of consecutive transactions against the elapsed time between them; if the required speed exceeds realistic aircraft travel (e.g., >800 km/h), impossible travel is flagged.
37. **Step-Up Authentication**: Dynamically elevating authentication requirements (e.g., triggering biometric or hardware token verification) when a transaction's calculated risk score falls into a suspicious intermediate band.
38. **Risk Score**: A normalized composite numerical score (0 to 1000) generated by combining deterministic rules, machine learning inference, and graph relationship analysis to represent transaction threat severity.
39. **Explainability / XAI (Explainable AI)**: The ability to provide human-interpretable and regulator-auditable rationales (such as SHAP feature importance values) explaining why a specific ML model flagged a transaction.

---

## 4. Microservices, Messaging & Distributed Systems

40. **Bounded Context**: A central pattern in Domain-Driven Design (DDD) that defines explicit boundaries within which a domain model applies and is internally consistent, mapping directly to microservice ownership.
41. **Strangler Fig Pattern**: An architectural migration strategy where a legacy monolithic system is gradually replaced by building new microservices around its edges until the legacy monolith is completely decommissioned.
42. **Anti-Corruption Layer (ACL)**: A translation layer situated between a modern microservice architecture and a legacy monolith to prevent legacy data schemas and domain concepts from corrupting new clean bounded contexts.
43. **Event-Driven Architecture (EDA)**: A software architecture paradigm where decoupled microservices produce, detect, and react to asynchronous state-change notifications called events.
44. **Apache Kafka**: A distributed event streaming platform offering high-throughput, fault-tolerant publish-subscribe pipelines, persistent partitioned commit logs, and stream processing capabilities.
45. **Kafka Partitioning Strategy**: The algorithmic assignment of events to topic partitions using a key (e.g., `hash(card_number) % num_partitions`) to guarantee strictly ordered event processing per account.
46. **Saga Pattern**: A distributed transaction pattern that coordinates a sequence of local transactions across independent microservices, utilizing compensating transactions to rollback state if any intermediate step fails.
47. **Saga Orchestrator**: A centralized coordinator service that explicitly issues commands to participating microservices and tracks the global workflow state of a distributed business process.
48. **CQRS (Command Query Responsibility Segregation)**: An architectural pattern that separates data modification commands (write pipeline) from data querying operations (read pipeline) into optimized distinct models.
49. **Materialized View**: A pre-computed, denormalized read model created from streaming event topics (via Kafka Streams/ksqlDB) to enable sub-millisecond query latency for dashboards and reports.
50. **Event Sourcing**: An architecture where every state mutation of an entity is recorded as an immutable sequence of append-only events, enabling point-in-time state reconstruction and tamper-evident audit trails.
51. **Dead Letter Queue (DLQ)**: A specialized secondary Kafka topic or messaging queue where poisoned messages (malformed payloads or unrecoverable processing failures) are routed after retry thresholds are exhausted.
52. **Circuit Breaker Pattern**: A stability pattern (e.g., via Envoy or Resilience4j) that halts cascading failures by tripping open when downstream error rates exceed thresholds, failing fast or routing to fallback logic.
53. **Mutual TLS (mTLS)**: A two-way cryptographic authentication mechanism where both client and server verify each other's X.509 digital certificates before establishing an encrypted TLS connection.
54. **Service Mesh (Istio/Envoy)**: A dedicated infrastructure layer handling transparent inter-service communication, mTLS encryption, traffic shaping, canary routing, and OpenTelemetry observability.
55. **Distributed Tracing (OpenTelemetry / Jaeger)**: The practice of injecting and propagating a unique correlation ID (`trace_id`, `span_id`) across synchronous gRPC hops and asynchronous Kafka messages for end-to-end latency diagnostics.

---

## 5. Graph Analytics & Advanced Machine Learning

56. **Property Graph**: A graph database model (e.g., Neo4j) where data is represented as nodes (entities) and edges (relationships), both capable of holding arbitrary key-value properties.
57. **Index-Free Adjacency**: The structural property of native graph engines where each node directly maintains physical memory pointers to its adjacent relationships, enabling \(O(1)\) graph traversals regardless of total graph size.
58. **Louvain Community Detection**: An unsupervised graph algorithm that extracts dense clusters of highly interconnected nodes by iteratively optimizing graph modularity, identifying coordinated fraud rings.
59. **PageRank Centrality**: A graph centrality algorithm that measures the relative transit importance of nodes based on incoming links, pinpointing critical infrastructure hubs (shared devices, IPs, phone numbers) used by fraudsters.
60. **Betweenness Centrality**: A graph metric quantifying how often a given node lies on the shortest path between all pairs of nodes, exposing financial bridge accounts and money mule conduits.
61. **Feature Store (Feast / Redis)**: A dual-storage infrastructure managing machine learning features, providing an offline batch repository for historical training and a low-latency key-value cache for online real-time inference.
62. **Population Stability Index (PSI)**: A statistical metric used to quantify how much an input feature's distribution has shifted between training baseline and production inference over time, triggering model retraining when \(\text{PSI} > 0.25\).
63. **Kolmogorov-Smirnov Test (KS Test)**: A non-parametric statistical hypothesis test comparing two continuous probability distributions to detect prediction drift in risk scoring outputs.
64. **Merkle Tree**: A cryptographic binary tree structure where every leaf node represents a cryptographic hash of a transactional audit record, and every parent node is the hash of its children, ensuring tamper-evidence.
65. **RPO & RTO**: Recovery Point Objective (the maximum acceptable age of data loss following a disaster, e.g., < 1 minute) and Recovery Time Objective (the maximum tolerable duration of system downtime, e.g., < 5 minutes).
