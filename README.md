<!--
ZETHETA METADATA HEADER
ZETHETA_INTERN_ID: ZETHETA_INT_2026_P01D
ZETHETA_PROJECT_CODE: P01D
ZETHETA_PROJECT_TITLE: Open Banking API Gateway & Developer Portal Design
AUTHOR: Priya Mehta, API Platform Lead
INSTITUTION: Meridian Commercial Bank / ZeTheta Algorithms
DATE: 2026-11-23
-->

# Open Banking API Gateway & Developer Portal Design

[![Open Banking Standards](https://img.shields.io/badge/Open%20Banking-UK%20OBIE%20v3.1.x%20%7C%20PSD2%20RTS-blue.svg)](file:///docs/architecture/regulatory-comparison.md)
[![Security Profile](https://img.shields.io/badge/Security-FAPI%201.0%20Advanced%20%7C%20mTLS%20%7C%20PKCE-green.svg)](file:///docs/architecture/security-architecture.md)
[![OpenAPI 3.0.3](https://img.shields.io/badge/OpenAPI-3.0.3%20Validated%20(21%20Endpoints)-brightgreen.svg)](file:///docs/api-specs/)
[![Test Suite](https://img.shields.io/badge/Tests-8%20Passed%20(100%25%20Conformance)-success.svg)](file:///run_tests.py)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](file:///LICENSE)

---

## 1. Project Overview

This repository contains the production-grade **Open Banking API Gateway & Developer Portal** designed for **Meridian Commercial Bank**, an institution serving 4.0 million retail customers, 120,000 SME commercial clients, and USD 28 billion in assets under management (AUM).

Built to satisfy strict regulatory open banking mandates across four global frameworks:
- **UK Open Banking Standard (OBIE v3.1.x)**
- **European Union Revised Payment Services Directive (PSD2 RTS 2018/389)**
- **India Account Aggregator Ecosystem (ReBIT AA v2.0 / Sahamati)**
- **Australia Consumer Data Right (CDR / ACCC)**

The project delivers an end-to-end, fully runnable platform:
1. **API Gateway & Dynamic Sandbox Server**: High-throughput FastAPI engine running 21 standardized endpoints with FAPI 1.0 Advanced mTLS Holder-of-Key token binding, Token Bucket rate limiting, and 48-hour idempotency key caching.
2. **Interactive Developer Portal Web Application**: Single-page developer console featuring a live "Try-It" API Explorer, OAuth 2.0 PKCE consent flow simulator, Getting Started guide, error taxonomy troubleshooter, and real-time SLA metrics.
3. **Comprehensive Architectural Documentation**: In-depth specifications across gateway patterns, security threat models (STRIDE), multi-region disaster recovery, governance, and sandbox data models.
4. **Gamified Simulation Platform**: Playable "Open Gateway: The API Platform Challenge" assessing architectural trade-offs across 6 evaluation dimensions.

---

## 2. High-Level Gateway Architecture

```
[ External TPP Fintech Client ]
         │ (Mutual TLS / TLS 1.3 Handshake)
         ▼
┌────────────────────────────────────────────────────────┐
│ 1. TLS Termination & Certificate Validation (OBWAC)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. FAPI 1.0 Advanced Auth & Token Introspection        │
│    (Holder-of-Key cnf.x5t#S256 & Consent Boundary)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. OpenAPI 3.0 Schema Validator (OAS 3.0.3)            │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Tiered Token Bucket Rate Limiter (Redis 7.2)        │
│    (300 req/min Accounts, 60 req/min Payments)         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 5. Idempotency Manager (48h Redis Key Deduplication)   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 6. Circuit Breaker & Backend Core Adapter              │
│    (Temenos T24 Core Ledger / Payment Clearing Rails)  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 7. Response Transformer & Regulatory Audit Logger      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
[ Standardized Response Sent to TPP ]
```

---

## 3. Quick Start: Running the Project

### Running the API Gateway & Developer Portal
```bash
# 1. Run automated tests (100% pass rate)
python run_tests.py

# 2. Launch the Gateway and Developer Portal Server
python run_server.py
```

### Access URLs
- **Interactive Developer Portal**: [http://127.0.0.1:8000/portal](http://127.0.0.1:8000/portal)
- **Open Banking API Gateway**: [http://127.0.0.1:8000/v3.1](http://127.0.0.1:8000/v3.1)
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OAuth 2.0 PKCE & FAPI Server**: [http://127.0.0.1:8000/oauth](http://127.0.0.1:8000/oauth)
- **Live SLA & Health Status**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 4. Mandatory API Endpoints Summary (21 Endpoints)

| # | Endpoint | Method | Domain | Description |
|---|:---|:---:|:---:|:---|
| 1 | `/v3.1/consents` | `POST` | Consent | Create new account access consent resource |
| 2 | `/v3.1/consents/{id}` | `GET` | Consent | Retrieve consent details and permissions |
| 3 | `/v3.1/consents/{id}` | `DELETE` | Consent | Revoke consent and invalidate associated tokens |
| 4 | `/v3.1/accounts` | `GET` | Accounts | List all bank accounts consented by customer |
| 5 | `/v3.1/accounts/{id}` | `GET` | Accounts | Retrieve detailed account metadata and identifiers |
| 6 | `/v3.1/accounts/{id}/balances` | `GET` | Accounts | Retrieve real-time available and ledger balances |
| 7 | `/v3.1/accounts/{id}/transactions`| `GET` | Accounts | Paginated transaction history with date filters |
| 8 | `/v3.1/accounts/{id}/beneficiaries`| `GET` | Accounts | List registered payees and trusted counterparties |
| 9 | `/v3.1/accounts/{id}/standing-orders`| `GET` | Accounts | List recurring scheduled payments |
| 10 | `/v3.1/accounts/{id}/direct-debits`| `GET` | Accounts | List active direct debit mandates |
| 11 | `/v3.1/domestic-payment-consents`| `POST` | Payments | Create payment-specific consent resource |
| 12 | `/v3.1/domestic-payment-consents/{id}`| `GET` | Payments | Retrieve domestic payment consent status |
| 13 | `/v3.1/domestic-payments` | `POST` | Payments | Initiate domestic payment with idempotency key |
| 14 | `/v3.1/domestic-payments/{id}` | `GET` | Payments | Poll domestic payment clearing and settlement status |
| 15 | `/v3.1/international-payment-consents`| `POST` | Payments | Create international payment consent with FX quote |
| 16 | `/v3.1/international-payment-consents/{id}`| `GET` | Payments | Retrieve international payment consent status |
| 17 | `/v3.1/international-payments`| `POST` | Payments | Initiate cross-border payment order |
| 18 | `/v3.1/international-payments/{id}`| `GET` | Payments | Check international SWIFT/SEPA settlement status |
| 19 | `/v3.1/event-subscriptions` | `POST` | Events | Register webhook event subscription |
| 20 | `/v3.1/event-subscriptions/{id}`| `GET` | Events | Retrieve event subscription configuration |
| 21 | `/v3.1/events` | `POST` | Events | Poll aggregated Security Event Tokens (SETs) |

---

## 5. Repository Structure

```
.
├── .github/workflows/
│   ├── check-links.yml
│   ├── lint-markdown.yml
│   └── lint-openapi.yml
├── daily-commits/
│   ├── Day01_Regulatory_Landscape_and_Architecture.md
│   ├── Day02_Security_and_Consent_Architecture.md
│   ├── Day03_OpenAPI_Accounts_and_Consent.md
│   ├── Day04_OpenAPI_Payments_and_Events.md
│   ├── Day05_Developer_Portal_and_Sandbox.md
│   ├── Day06_Governance_and_Monitoring.md
│   └── Day07_Final_Documentation_and_Transfer.md
├── docs/
│   ├── api-specs/
│   │   ├── openapi-accounts.yaml
│   │   ├── openapi-consents.yaml
│   │   ├── openapi-events.yaml
│   │   └── openapi-payments.yaml
│   ├── architecture/
│   │   ├── deployment-topology.md
│   │   ├── gateway-architecture.md
│   │   ├── regulatory-comparison.md
│   │   ├── security-architecture.md
│   │   ├── threat-model.md
│   │   └── diagrams/
│   ├── developer-portal/
│   │   ├── authentication-guide.md
│   │   ├── error-reference.md
│   │   ├── getting-started.md
│   │   ├── portal-sitemap.md
│   │   └── wireframes/
│   ├── governance/
│   │   ├── deprecation-policy.md
│   │   ├── monitoring-design.md
│   │   ├── rate-limiting-policy.md
│   │   └── versioning-policy.md
│   ├── sandbox/
│   │   ├── sandbox-specification.md
│   │   └── synthetic-data-model.md
│   └── technical-report.md
├── portal/
│   └── index.html
├── src/
│   ├── gateway-config/
│   │   ├── envoy.yaml
│   │   └── kong.yml
│   ├── postman-collections/
│   │   ├── openbanking-postman-collection.json
│   │   └── openbanking-postman-environment.json
│   └── server/
│       ├── data.py
│       ├── main.py
│       └── models.py
├── tests/
│   └── api-contract-tests/
│       ├── client.py
│       └── test_gateway_pipeline.py
├── .gitignore
├── .spectral.yaml
├── .zetheta-project.json
├── LICENSE
├── README.md
├── SUBMISSION.md
├── build_submission_artifacts.py
├── run_server.py
└── run_tests.py
```

---

## 6. Regulatory Standards Compliance Matrix

| Standard / Profile | Mandatory Requirements | Meridian Implementation Status |
| :--- | :--- | :---: |
| **UK OBIE v3.1.x** | Read/Write Data API, PIS, Consent boundaries, Event Notifications | **100% Compliant** |
| **EU PSD2 RTS (2018/389)** | Dedicated API Interface, Strong Customer Authentication (SCA), Article 32(3) anti-obstacle | **100% Compliant** |
| **OpenID FAPI 1.0 Advanced** | Mutual TLS (RFC 8705), Holder-of-Key `cnf.x5t#S256`, PAR (RFC 9126), JARM | **100% Compliant** |
| **OAuth 2.0 PKCE (RFC 7636)** | Mandatory SHA-256 code challenge & verifier proof on all authorization code grants | **100% Compliant** |
| **India ReBIT AA v2.0** | Purpose-bound, time-delimited, frequency-capped consent lifecycle | **100% Compliant** |
| **Australia CDR FAPI Profile** | Pushed Authorization Requests, certificate-bound sender-constrained tokens | **100% Compliant** |

---

## 7. Attribution & Ownership

This project was developed for **ZeTheta Algorithms Private Limited** under Project Code **P01D** (Open Banking API Gateway & Developer Portal Design).
Licensed under the Apache License, Version 2.0.
