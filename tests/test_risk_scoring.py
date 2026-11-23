"""Unit tests for Risk Scoring Engine and Merkle Audit Journal."""
from src.risk_scoring.engine import RiskScoringEngine
from src.audit_service.merkle_audit import MerkleAuditJournal

def test_risk_scoring_auto_approve():
    engine = RiskScoringEngine()
    rule_res = {"rule_score": 50, "triggered_rules": []}
    ml_res = {"calibrated_ml_score": 100, "top_features_shap": []}
    graph_res = {"graph_risk_score": 50}

    dec = engine.compute_decision("tx_test", rule_res, ml_res, graph_res)
    assert dec["decision"] == "AUTO_APPROVE"
    assert dec["composite_risk_score"] < 200

def test_risk_scoring_auto_decline():
    engine = RiskScoringEngine()
    rule_res = {"rule_score": 850, "should_block": True, "triggered_rules": [{"rule_id": "RULE_WCH_001", "rule_name": "Breach Card", "delta": 900}]}
    ml_res = {"calibrated_ml_score": 880, "top_features_shap": []}
    graph_res = {"graph_risk_score": 900}

    dec = engine.compute_decision("tx_fraud", rule_res, ml_res, graph_res)
    assert dec["decision"] == "AUTO_DECLINE"
    assert dec["composite_risk_score"] >= 800

def test_merkle_audit_integrity_and_tamper_detection():
    journal = MerkleAuditJournal()
    journal.append("user_1", "CREATE", "rule", "RULE_01", {"data": 1})
    journal.append("user_2", "UPDATE", "rule", "RULE_01", {"data": 2})
    journal.append("user_3", "APPROVE", "rule", "RULE_01", {"data": 3})

    # Verify initial valid state
    is_valid, bad_idx = journal.verify_integrity()
    assert is_valid is True
    assert bad_idx is None

    # Simulate malicious database tampering
    journal.audit_chain[1]["payload"]["data"] = 9999
    is_valid_after_tamper, bad_idx_after = journal.verify_integrity()
    assert is_valid_after_tamper is False
    assert bad_idx_after == 1
