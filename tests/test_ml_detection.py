"""Unit tests for ML Anomaly Detection."""
from src.ml_service.detector import AnomalyDetector

def test_ml_normal_transaction():
    detector = AnomalyDetector()
    payload = {
        "amount": 500.0,
        "velocity_count_10m": 1.0,
        "distance_from_home_km": 2.0,
        "is_international": False,
        "is_proxy": False,
        "hour_local": 14
    }
    res = detector.score(payload)
    assert res["ml_anomaly_score"] < 0.20
    assert res["calibrated_ml_score"] < 200
    assert len(res["top_features_shap"]) == 5

def test_ml_anomalous_transaction():
    detector = AnomalyDetector()
    payload = {
        "amount": 250000.0, # High amount
        "velocity_count_10m": 8.0, # Rapid velocity
        "distance_from_home_km": 4000.0, # Distant
        "is_international": True,
        "is_proxy": True,
        "hour_local": 3 # Night time
    }
    res = detector.score(payload)
    assert res["ml_anomaly_score"] > 0.85
    assert res["calibrated_ml_score"] > 800
    assert res["top_features_shap"][0]["shap_attribution"] > 0
