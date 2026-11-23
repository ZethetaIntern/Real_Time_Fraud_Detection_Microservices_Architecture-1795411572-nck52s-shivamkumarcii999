"""Automated Test Runner for ShieldPay Microservices Platform."""
import sys
import time

def run_all_tests():
    print("=" * 70)
    print("SHIELDPAY REAL-TIME FRAUD DETECTION PLATFORM - TEST RUNNER")
    print("=" * 70)

    # 1. Rule Engine Tests
    print("\n[1/5] Testing Rule Engine Evaluator...")
    from tests.test_rule_engine import (
        test_rule_high_value_domestic,
        test_rule_impossible_travel,
        test_rule_velocity_spike
    )
    test_rule_high_value_domestic()
    print("  ✓ test_rule_high_value_domestic PASSED")
    test_rule_impossible_travel()
    print("  ✓ test_rule_impossible_travel PASSED")
    test_rule_velocity_spike()
    print("  ✓ test_rule_velocity_spike PASSED")

    # 2. ML Detection Tests
    print("\n[2/5] Testing ML Anomaly Detection & SHAP Attributions...")
    from tests.test_ml_detection import (
        test_ml_normal_transaction,
        test_ml_anomalous_transaction
    )
    test_ml_normal_transaction()
    print("  ✓ test_ml_normal_transaction PASSED")
    test_ml_anomalous_transaction()
    print("  ✓ test_ml_anomalous_transaction PASSED")

    # 3. Graph Analysis Tests
    print("\n[3/5] Testing Graph Analysis & Fraud Ring Traversal...")
    from tests.test_graph_analysis import (
        test_shortest_path_to_fraud,
        test_shared_device_fraud_ring
    )
    test_shortest_path_to_fraud()
    print("  ✓ test_shortest_path_to_fraud PASSED")
    test_shared_device_fraud_ring()
    print("  ✓ test_shared_device_fraud_ring PASSED")

    # 4. Risk Scoring & Merkle Audit Tests
    print("\n[4/5] Testing Risk Scoring & Merkle Cryptographic Tamper Detection...")
    from tests.test_risk_scoring import (
        test_risk_scoring_auto_approve,
        test_risk_scoring_auto_decline,
        test_merkle_audit_integrity_and_tamper_detection
    )
    test_risk_scoring_auto_approve()
    print("  ✓ test_risk_scoring_auto_approve PASSED")
    test_risk_scoring_auto_decline()
    print("  ✓ test_risk_scoring_auto_decline PASSED")
    test_merkle_audit_integrity_and_tamper_detection()
    print("  ✓ test_merkle_audit_integrity_and_tamper_detection PASSED")

    # 5. End-to-End API Pipeline Tests
    print("\n[5/5] Testing End-to-End API Pipeline via TestClient (<100ms SLA)...")
    from tests.test_end_to_end_pipeline import (
        test_healthcheck,
        test_legitimate_transaction_approval,
        test_high_risk_fraud_transaction_decline,
        test_case_management_flow,
        test_merkle_audit_verification,
        test_dashboard_metrics
    )
    test_healthcheck()
    print("  ✓ test_healthcheck PASSED")
    test_legitimate_transaction_approval()
    print("  ✓ test_legitimate_transaction_approval PASSED")
    test_high_risk_fraud_transaction_decline()
    print("  ✓ test_high_risk_fraud_transaction_decline PASSED")
    test_case_management_flow()
    print("  ✓ test_case_management_flow PASSED")
    test_merkle_audit_verification()
    print("  ✓ test_merkle_audit_verification PASSED")
    test_dashboard_metrics()
    print("  ✓ test_dashboard_metrics PASSED")

    print("\n" + "=" * 70)
    print("ALL 16 TEST SUITES PASSED SUCCESSFULLY! (100% SUCCESS RATE)")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
