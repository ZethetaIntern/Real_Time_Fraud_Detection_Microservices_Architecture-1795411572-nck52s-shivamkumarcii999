# Observability Standards: Structured Logging, Distributed Tracing & PII Masking

ShieldPay mandates unified observability across all 10 microservices, enforcing **Structured JSON Logging**, **OpenTelemetry Distributed Tracing**, and **Strict PII Masking Rules**.

---

## 1. Structured JSON Logging Standard

Every log line emitted by any service must be serialized in single-line JSON format and ingested via Fluent Bit to Elasticsearch / OpenSearch.

### Mandatory Log Fields:
```json
{
  "timestamp": "2026-11-20T07:35:12.182Z",
  "level": "INFO",
  "service": "risk-scoring-service",
  "version": "v2.4.1",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "parent_span_id": "5c4a7e912b339101",
  "environment": "production",
  "region": "ap-south-1",
  "entity_type": "transaction",
  "entity_id": "tx_99481928401",
  "card_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "event_name": "RiskDecisionComputed",
  "execution_time_ms": 12.4,
  "payload": {
    "composite_risk_score": 845,
    "decision": "DECLINE",
    "rule_score": 900,
    "ml_score": 0.82,
    "graph_score": 850,
    "triggered_rules": ["RULE_VEL_001", "RULE_GEO_001"],
    "top_ml_features": [
      {"feature": "velocity_10m", "shap_value": 0.34},
      {"feature": "amount_zscore", "shap_value": 0.28}
    ]
  }
}
```

---

## 2. Strict PII & Cardholder Data Masking Rules

Under PCI DSS Req 3.4 and Indian Digital Personal Data Protection Act (DPDP), plaintext card numbers, CVVs, PINs, and personal identification are forbidden from entering log collectors:

| Data Field | Plaintext Value | Masking / Tokenisation Rule Applied in Logger | Logged Value |
| :--- | :--- | :--- | :--- |
| **Primary Account Number (PAN)** | `4111 2222 3333 4444` | Truncate and replace middle digits with `X` (First 6, Last 4 preserved) | `4111-22XX-XXXX-4444` |
| **Card Verification Value (CVV)** | `842` | Strictly redacted; never stored or logged | `[REDACTED]` |
| **Aadhaar Number** | `9182 3746 1928` | Retain only last 4 digits | `XXXX-XXXX-1928` |
| **Customer Full Name** | `Rahul Sharma` | Mask all characters except initial letter of each word | `R**** S*****` |
| **Customer Phone Number** | `+91 98200 12345` | Retain country code and last 3 digits | `+91-XXXXX-XX345` |
| **IP Address** | `103.21.45.67` | Truncate last octet for general analytics; store SHA-256 hash | `103.21.45.0/24` (Hash: `a7f9c2...`) |

---

## 3. Distributed Tracing via OpenTelemetry

1. **Context Propagation Protocol**: W3C Trace Context headers (`traceparent`, `tracestate`) injected across all incoming HTTP headers, propagated over gRPC metadata, and injected into Kafka message headers (`RecordHeaders`).
2. **Sampling Strategy**:
   - **Adaptive Head-Based Sampling**: 1% baseline sampling for normal `APPROVED` transactions (to conserve storage at 20,000 TPS).
   - **100% Tail-Based Sampling**: Any transaction resulting in `STEP_UP_AUTH`, `DECLINE`, `5xx ERROR`, or latency exceeding 100ms is captured at **100% full span fidelity**.
3. **Trace Backend**: OpenTelemetry Collector -> Tempo / Jaeger with 14-day hot SSD retention.
