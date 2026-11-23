# API Gateway Architecture & Tiered Rate Limiting Framework

Kong Enterprise / Envoy operates at the perimeter of ShieldPay's fraud detection platform, acting as the centralized edge reverse proxy, security gatekeeper, and traffic throttle.

---

## 1. Gateway Responsibilities & Traffic Pipeline

```mermaid
flowchart LR
    CLIENTS[Payment Gateways / POS / UPI] -->|HTTPS / TLS 1.3| GW[Kong API Gateway Edge]
    subgraph GatewayPipeline["Gateway Request Pipeline"]
        TLS[1. TLS 1.3 Termination] --> AUTH[2. JWT / RS256 Auth & API Key]
        AUTH --> RATE[3. 5-Tier Distributed Rate Limiter (Redis)]
        RATE --> CB[4. Adaptive Circuit Breaker]
        CB --> VAL[5. OpenAPI Schema Validation]
        VAL --> TRANS[6. Protocol Transcoding: REST -> gRPC]
    end
    GW --> GatewayPipeline
    TRANS -->|Internal gRPC Call| INGEST[transaction-ingestion-service]
```

---

## 2. Five-Tier Distributed Rate Limiting Framework

To combat distributed card enumeration attacks, credential stuffing, and volumetric DDoS without impacting legitimate acquirers, ShieldPay enforces a **5-tier token bucket algorithm** backed by Redis:

| Rate Limit Tier | Target Scope | Limit Threshold | Window | Redis Counter Key Pattern | Action on Breach |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Per-Merchant Contracted** | Individual Merchant ID | Large Acquirer: 1,000 TPS<br>Small Merchant: 100 TPS | 1-second sliding window | `rl:merchant:<merchant_id>:sec` | HTTP 429 Too Many Requests |
| **Tier 2: Per-IP Protection** | Originating Client IP | 50 requests / min | 1-minute sliding window | `rl:ip:<client_ip_hash>:min` | HTTP 429 + Temporary IP Greylist |
| **Tier 3: Per-Endpoint Quota** | Specific URI Path | `/api/v1/transactions`: 15,000 TPS<br>`/api/v1/cases`: 200 TPS | 1-second window | `rl:endpoint:<path_slug>:sec` | HTTP 429 with `Retry-After: 1` |
| **Tier 4: Global Cluster Shield**| Entire Platform | 50,000 TPS Maximum | 1-second window | `rl:global:system_capacity` | Shed non-critical traffic; preserve authorization |
| **Tier 5: Adaptive Attack Throttle**| Merchant / Channel Under Attack | Automatically cut to 50% limit if fraud rate > 5% | 5-minute rolling window | `rl:adaptive:<merchant_id>` | Auto-tightens; alerts Fraud Operations |

### Standard Response Headers Enforced:
```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1732098650
Retry-After: 1
Content-Type: application/json

{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Transaction ingestion quota breached for merchant M-8491. Please retry in 1 second.",
  "retry_after_seconds": 1
}
```

---

## 3. Circuit Breaker Configuration at Edge Gateway

Implemented via Envoy Outlier Detection and Resilience4j to prevent systemic cascading failure:
- **Consecutive 5xx Errors**: 5 consecutive errors over a 10-second window trips circuit to **OPEN**.
- **Base Ejection Time**: 30 seconds.
- **Max Ejection Percent**: 50% of available backend pod endpoints.
- **Fallback Response**: Returns HTTP 202 with challenge action (`STEP_UP_AUTH`) requesting SMS OTP, ensuring transactions fail safe rather than silently approving potential fraud.
