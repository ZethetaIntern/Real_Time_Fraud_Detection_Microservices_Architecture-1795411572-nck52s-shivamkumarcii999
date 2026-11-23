"""End-to-End Integration Tests for ShieldPay Fraud Detection API."""
from src.main import (
    app,
    healthz,
    submit_transaction,
    list_cases,
    update_case_decision,
    verify_audit_trail,
    get_dashboard_metrics,
    TransactionRequest,
    CaseVerdictRequest
)

def test_healthcheck():
    res = healthz()
    assert res["status"] == "UP"

def test_legitimate_transaction_approval():
    tx = TransactionRequest(
        transaction_id="tx_clean_101",
        card_number="4111222233334444",
        cardholder_id="cust_101",
        amount=2400.0,
        currency="INR",
        merchant_id="M-GROCERY-01",
        mcc="5411",
        channel="POS",
        ip_address="103.21.45.67",
        device_fingerprint="dev_normal_01",
        is_international=False,
        is_proxy=False,
        hour_local=14
    )
    res = submit_transaction(tx)
    assert res["decision"] in ["AUTO_APPROVE", "STEP_UP_AUTHENTICATION"]
    assert res["composite_risk_score"] < 600
    assert res["execution_time_ms"] < 100.0 # Sub-100ms SLA verified!

def test_high_risk_fraud_transaction_decline():
    # Carding enumeration attack with impossible travel & compromised country
    tx = TransactionRequest(
        transaction_id="tx_fraud_888",
        card_number="4111555566667777",
        cardholder_id="cust_fraud_888",
        amount=750000.0, # > 500,000 INR
        currency="INR",
        merchant_id="M-CRYPTO-99",
        mcc="6051", # Crypto
        channel="ECOM",
        ip_address="185.220.101.5",
        device_fingerprint="dev_jailbroken_tor",
        is_international=True,
        is_proxy=True,
        is_tor=True,
        is_jailbroken=True,
        implied_speed_kmh=1200.0, # Impossible travel
        hour_local=3 # Night time
    )
    res = submit_transaction(tx)
    assert res["decision"] == "AUTO_DECLINE"
    assert res["composite_risk_score"] >= 800
    assert len(res["explainability"]["key_drivers"]) > 0

def test_case_management_flow():
    # Fetch active cases created by declines
    cases_data = list_cases()
    assert cases_data["total"] >= 1

    first_case_id = cases_data["cases"][0]["case_id"]
    # Update decision as analyst
    verdict = CaseVerdictRequest(
        decision="CONFIRMED_FRAUD",
        notes="Verified fraudulent cash-out attempt via Tor exit node.",
        analyst_id="analyst_priya",
        permanent_card_block=True
    )
    update_res = update_case_decision(case_id=first_case_id, body=verdict)
    assert update_res["status"] == "CONFIRMED_FRAUD"

def test_merkle_audit_verification():
    audit_data = verify_audit_trail()
    assert audit_data["is_valid"] is True
    assert audit_data["total_records"] >= 3

def test_dashboard_metrics():
    metrics = get_dashboard_metrics()
    assert metrics["transactions_processed"] >= 2
    assert metrics["total_fraud_blocked_inr"] > 0
    assert metrics["latency_p99_ms"] < 100.0
