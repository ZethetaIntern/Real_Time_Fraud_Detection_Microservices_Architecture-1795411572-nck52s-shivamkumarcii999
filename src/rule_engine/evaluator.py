"""Deterministic Rule Engine Evaluator supporting nested boolean logic and sliding windows."""
import time
import math
from typing import Dict, Any, List, Tuple
from src.config import load_rules_yaml

class RuleEngine:
    def __init__(self, rules: List[Dict[str, Any]] = None):
        self.rules = rules if rules is not None else load_rules_yaml()
        # In-memory sliding window store: card_hash -> list of (timestamp_epoch, amount, merchant_id)
        self.card_history: Dict[str, List[Tuple[float, float, str]]] = {}
        # Device history: device_fp -> list of (timestamp_epoch, card_hash)
        self.device_history: Dict[str, List[Tuple[float, str]]] = {}

    def record_transaction(self, card_hash: str, amount: float, merchant_id: str, device_fp: str, timestamp: float):
        """Records transaction into sliding memory buffers."""
        if card_hash not in self.card_history:
            self.card_history[card_hash] = []
        self.card_history[card_hash].append((timestamp, amount, merchant_id))

        if device_fp:
            if device_fp not in self.device_history:
                self.device_history[device_fp] = []
            self.device_history[device_fp].append((timestamp, card_hash))

    def _get_velocity_features(self, card_hash: str, device_fp: str, current_time: float) -> Dict[str, Any]:
        """Calculates windowed velocity features from sliding windows."""
        txs = self.card_history.get(card_hash, [])
        dev_txs = self.device_history.get(device_fp, [])

        # Filter last 10 mins (600s), 5 mins (300s), 60 mins (3600s), 24h (86400s)
        txs_10m = [t for t in txs if current_time - t[0] <= 600]
        txs_5m = [t for t in txs if current_time - t[0] <= 300]
        txs_1h = [t for t in txs if current_time - t[0] <= 3600]
        dev_txs_24h = [t for t in dev_txs if current_time - t[0] <= 86400]

        distinct_merchants_5m = len(set(t[2] for t in txs_5m))
        distinct_cards_dev_24h = len(set(t[1] for t in dev_txs_24h))
        cum_amount_1h = sum(t[1] for t in txs_1h)

        return {
            "velocity.card.tx_count": len(txs_10m),
            "velocity.card.tx_count_1h": len(txs_1h),
            "velocity.card.distinct_merchants": distinct_merchants_5m,
            "velocity.card.cumulative_amount": cum_amount_1h,
            "velocity.device.card_count_24h": distinct_cards_dev_24h,
            "velocity.upi.collect_request_count": len(txs_10m) # simulated proxy
        }

    def _eval_single_condition(self, cond: Dict[str, Any], context: Dict[str, Any]) -> bool:
        field = cond.get("field")
        op = cond.get("operator")
        val = cond.get("value")

        actual = context.get(field)
        if actual is None:
            return False

        if op == "eq":
            return actual == val
        elif op == "neq":
            return actual != val
        elif op == "gt":
            return actual > val
        elif op == "gte":
            return actual >= val
        elif op == "lt":
            return actual < val
        elif op == "lte":
            return actual <= val
        elif op == "in":
            return actual in val
        elif op == "between":
            return val[0] <= actual <= val[1]
        return False

    def _eval_condition_tree(self, cond_tree: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if "and" in cond_tree:
            return all(self._eval_condition_tree(sub, context) for sub in cond_tree["and"])
        elif "or" in cond_tree:
            return any(self._eval_condition_tree(sub, context) for sub in cond_tree["or"])
        elif "field" in cond_tree:
            return self._eval_single_condition(cond_tree, context)
        return False

    def evaluate(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates active rules against incoming transaction payload."""
        start_time = time.perf_counter()
        now = tx_payload.get("timestamp_epoch", time.time())
        card_hash = tx_payload.get("card_number_hash", "")
        amount = tx_payload.get("amount", 0.0)
        merchant_id = tx_payload.get("merchant_id", "")
        device_fp = tx_payload.get("device_fingerprint", "")

        # Record this transaction
        self.record_transaction(card_hash, amount, merchant_id, device_fp, now)

        # Assemble evaluation context
        context = {
            "transaction.amount": amount,
            "transaction.mcc": str(tx_payload.get("mcc", "")),
            "transaction.channel": tx_payload.get("channel", "POS"),
            "transaction.is_international": tx_payload.get("is_international", False),
            "transaction.amount_zscore": tx_payload.get("amount_zscore", 0.0),
            "transaction.hour_local": tx_payload.get("hour_local", 12),
            "location.country_risk_tier": tx_payload.get("country_risk_tier", "NORMAL"),
            "location.implied_speed_kmh": tx_payload.get("implied_speed_kmh", 0.0),
            "location.is_foreign": tx_payload.get("is_foreign", False),
            "location.is_proxy": tx_payload.get("is_proxy", False),
            "location.is_tor": tx_payload.get("is_tor", False),
            "profile.in_travel_history": tx_payload.get("in_travel_history", True),
            "profile.historical_gambling_tx_count": tx_payload.get("historical_gambling_tx_count", 0),
            "profile.days_since_last_tx": tx_payload.get("days_since_last_tx", 1),
            "watchlist.card_is_compromised": tx_payload.get("card_is_compromised", False),
            "watchlist.ip_is_malicious": tx_payload.get("ip_is_malicious", False),
            "device.is_jailbroken": tx_payload.get("is_jailbroken", False),
        }
        context.update(self._get_velocity_features(card_hash, device_fp, now))

        rule_score = 0
        should_block = False
        should_step_up = False
        triggered = []

        for r in self.rules:
            conds = r.get("conditions", {})
            if self._eval_condition_tree(conds, context):
                act = r.get("action", {})
                act_type = act.get("type")
                delta = act.get("delta", 0)
                rule_score += delta
                if act_type == "BLOCK":
                    should_block = True
                elif act_type == "STEP_UP_AUTH":
                    should_step_up = True
                triggered.append({
                    "rule_id": r["rule_id"],
                    "rule_name": r["rule_name"],
                    "severity": r.get("severity", "MEDIUM"),
                    "delta": delta,
                    "action": act_type
                })

        rule_score = min(rule_score, 1000)
        eval_ms = (time.perf_counter() - start_time) * 1000

        return {
            "rule_score": rule_score,
            "should_block": should_block,
            "should_step_up": should_step_up,
            "triggered_rules": triggered,
            "evaluation_latency_ms": round(eval_ms, 2)
        }
