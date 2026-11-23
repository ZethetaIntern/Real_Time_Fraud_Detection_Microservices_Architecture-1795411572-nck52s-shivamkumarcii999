"""Unit tests for Graph Analysis & Fraud Ring Detection."""
from src.graph_service.graph_analyzer import GraphAnalyzer

def test_shortest_path_to_fraud():
    analyzer = GraphAnalyzer()
    analyzer.mark_fraud("card_fraud_99")

    # Connect card_A -> device_1 -> card_fraud_99
    analyzer.add_edge("card_A", "device_1", "Card", "Device")
    analyzer.add_edge("device_1", "card_fraud_99", "Device", "Card")

    hops = analyzer.shortest_path_to_fraud("card_A", max_depth=4)
    assert hops == 2

def test_shared_device_fraud_ring():
    analyzer = GraphAnalyzer()
    device_id = "device_compromised_syndicate"

    # Link 5 different cards to the same device
    for i in range(5):
        card_id = f"synthetic_card_{i}"
        analyzer.add_edge(card_id, device_id, "Card", "Device")

    payload = {
        "card_number_hash": "synthetic_card_6",
        "device_fingerprint": device_id
    }
    res = analyzer.analyze(payload)
    assert res["shared_device_card_count"] >= 5
    assert res["part_of_fraud_ring"] is True
    assert res["graph_risk_score"] >= 800
