"""Risk Scoring Engine & Explainability Synthesizer."""
import time
from typing import Dict, Any, List
from src.config import (
    WEIGHT_RULE, WEIGHT_ML, WEIGHT_GRAPH,
    THRESHOLD_APPROVE, THRESHOLD_STEP_UP, THRESHOLD_REVIEW
)

class RiskScoringEngine:
    def __init__(self):
        pass

    def compute_decision(
        self,
        tx_id: str,
        rule_result: Dict[str, Any],
        ml_result: Dict[str, Any],
        graph_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combines rule, ML, and graph outputs into composite risk score and action."""
        start_time = time.perf_counter()

        rule_score = float(rule_result.get("rule_score", 0))
        ml_score = float(ml_result.get("calibrated_ml_score", 0))
        graph_score = float(graph_result.get("graph_risk_score", 0))

        # Check for hard overrides from rule engine or confirmed fraud node
        should_block = rule_result.get("should_block", False) or (graph_score >= 1000)

        # Weighted composite score
        composite_score = int(round(
            (WEIGHT_RULE * rule_score) +
            (WEIGHT_ML * ml_score) +
            (WEIGHT_GRAPH * graph_score)
        ))
        composite_score = min(max(composite_score, 0), 1000)

        # If an explicit hard-block rule triggered (e.g. impossible travel, breach card, OFAC sanction)
        if should_block:
            composite_score = max(composite_score, 850)
            action = "AUTO_DECLINE"
        elif composite_score >= THRESHOLD_REVIEW:
            action = "AUTO_DECLINE" if composite_score >= 800 else "MANUAL_REVIEW_QUEUE"
        elif composite_score >= THRESHOLD_APPROVE:
            action = "STEP_UP_AUTHENTICATION"
        else:
            action = "AUTO_APPROVE"

        # Generate human-readable explanation
        drivers = []
        for r in rule_result.get("triggered_rules", []):
            drivers.append(f"Rule: {r['rule_name']} (+{r['delta']})")

        for f in ml_result.get("top_features_shap", [])[:2]:
            if f["shap_attribution"] > 0.2:
                drivers.append(f"ML Feature '{f['feature']}' deviation")

        if graph_result.get("part_of_fraud_ring"):
            drivers.append(f"Graph: Shared infrastructure ({graph_result.get('matched_topology')})")
        elif graph_result.get("degrees_to_fraud", -1) in [1, 2]:
            drivers.append(f"Graph: {graph_result.get('degrees_to_fraud')} hops to confirmed fraud entity")

        explanation_text = " | ".join(drivers) if drivers else "Normal transaction behavior; within baseline thresholds."

        ms = (time.perf_counter() - start_time) * 1000

        return {
            "transaction_id": tx_id,
            "composite_risk_score": composite_score,
            "decision": action,
            "components": {
                "rule_score": int(rule_score),
                "ml_score": int(ml_score),
                "graph_score": int(graph_score)
            },
            "weights": {
                "rule": WEIGHT_RULE,
                "ml": WEIGHT_ML,
                "graph": WEIGHT_GRAPH
            },
            "explainability": {
                "summary": explanation_text,
                "key_drivers": drivers,
                "triggered_rules": [r.get("rule_id", r.get("rule_name", "UNKNOWN")) for r in rule_result.get("triggered_rules", [])],
                "top_ml_shap": ml_result.get("top_features_shap", []),
                "graph_topology": graph_result.get("matched_topology", "NORMAL")
            },
            "scoring_latency_ms": round(ms, 2)
        }
