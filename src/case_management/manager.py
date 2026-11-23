"""Case Management Service: Analyst Queues and Investigation Lifecycle."""
import time
from typing import Dict, Any, List, Optional

class CaseManager:
    def __init__(self):
        self.cases: Dict[str, Dict[str, Any]] = {}
        self.case_counter = 1000

    def create_case(self, tx_id: str, risk_score: int, priority: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an investigation case."""
        self.case_counter += 1
        case_id = f"CASE-{self.case_counter}"
        case = {
            "case_id": case_id,
            "transaction_id": tx_id,
            "risk_score": risk_score,
            "priority": priority, # P1_CRITICAL, P2_HIGH, P3_MEDIUM
            "status": "OPEN",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "assigned_analyst": "UNASSIGNED",
            "alert_data": alert_data,
            "decision": None,
            "notes": ""
        }
        self.cases[case_id] = case
        return case

    def update_decision(self, case_id: str, decision: str, notes: str, analyst_id: str) -> Optional[Dict[str, Any]]:
        """Updates case with human analyst decision."""
        if case_id not in self.cases:
            return None
        case = self.cases[case_id]
        case["status"] = decision # e.g. CONFIRMED_FRAUD, FALSE_POSITIVE
        case["decision"] = decision
        case["notes"] = notes
        case["assigned_analyst"] = analyst_id
        case["resolved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return case

    def list_cases(self, status: str = "", priority: str = "") -> List[Dict[str, Any]]:
        res = list(self.cases.values())
        if status:
            res = [c for c in res if c["status"] == status]
        if priority:
            res = [c for c in res if c["priority"] == priority]
        return res
