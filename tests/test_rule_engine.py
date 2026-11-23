"""Unit tests for Rule Engine Evaluator."""
from src.rule_engine.evaluator import RuleEngine

def test_rule_high_value_domestic():
    engine = RuleEngine()
    payload = {
        "card_number_hash": "card_test_1",
        "amount": 600000.0, # Exceeds 500,000 INR
        "mcc": "5411",
        "channel": "POS",
        "timestamp_epoch": 1000.0
    }
    res = engine.evaluate(payload)
    triggered_ids = [r["rule_id"] for r in res["triggered_rules"]]
    assert "RULE_AMT_001" in triggered_ids
    assert res["should_step_up"] is True

def test_rule_impossible_travel():
    engine = RuleEngine()
    payload = {
        "card_number_hash": "card_test_2",
        "amount": 5000.0,
        "implied_speed_kmh": 950.0, # Implied speed > 800 km/h
        "timestamp_epoch": 1000.0
    }
    res = engine.evaluate(payload)
    triggered_ids = [r["rule_id"] for r in res["triggered_rules"]]
    assert "RULE_GEO_001" in triggered_ids
    assert res["should_block"] is True

def test_rule_velocity_spike():
    engine = RuleEngine()
    card = "card_velocity_test"
    # Fire 6 rapid transactions
    for i in range(6):
        payload = {
            "card_number_hash": card,
            "amount": 1000.0,
            "timestamp_epoch": 1000.0 + (i * 10) # 10s apart
        }
        res = engine.evaluate(payload)

    # 6th transaction must trigger RULE_VEL_001 (>5 in 10 mins)
    triggered_ids = [r["rule_id"] for r in res["triggered_rules"]]
    assert "RULE_VEL_001" in triggered_ids
