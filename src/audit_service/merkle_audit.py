"""Cryptographic Append-Only Merkle-Tree Audit Logging Engine."""
import hashlib
import json
import time
from typing import Dict, Any, List, Optional, Tuple

class MerkleAuditJournal:
    def __init__(self):
        # Genesis block
        self.genesis_hash = hashlib.sha256(b"SHIELDPAY_GENESIS_BLOCK_2026").hexdigest()
        self.audit_chain: List[Dict[str, Any]] = []

    def append(self, actor_id: str, action: str, entity_type: str, entity_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Appends an immutable audit entry chained to previous hash."""
        prev_hash = self.audit_chain[-1]["current_hash"] if self.audit_chain else self.genesis_hash
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Canonical serialized payload
        canonical_str = json.dumps(payload, sort_keys=True)
        block_content = f"{prev_hash}|{timestamp}|{actor_id}|{action}|{entity_type}|{entity_id}|{canonical_str}"
        current_hash = hashlib.sha256(block_content.encode("utf-8")).hexdigest()

        record = {
            "index": len(self.audit_chain),
            "timestamp": timestamp,
            "actor_id": actor_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "payload": payload,
            "previous_hash": prev_hash,
            "current_hash": current_hash
        }
        self.audit_chain.append(record)
        return record

    def verify_integrity(self) -> Tuple[bool, Optional[int]]:
        """Verifies the unbroken cryptographic integrity of the entire audit chain."""
        expected_prev = self.genesis_hash
        for i, record in enumerate(self.audit_chain):
            if record["previous_hash"] != expected_prev:
                return False, i
            # Recompute hash
            canonical_str = json.dumps(record["payload"], sort_keys=True)
            block_content = f"{record['previous_hash']}|{record['timestamp']}|{record['actor_id']}|{record['action']}|{record['entity_type']}|{record['entity_id']}|{canonical_str}"
            recomputed = hashlib.sha256(block_content.encode("utf-8")).hexdigest()
            if recomputed != record["current_hash"]:
                return False, i
            expected_prev = record["current_hash"]
        return True, None

    def get_records(self, entity_id: str = "") -> List[Dict[str, Any]]:
        if not entity_id:
            return self.audit_chain
        return [r for r in self.audit_chain if r["entity_id"] == entity_id]
