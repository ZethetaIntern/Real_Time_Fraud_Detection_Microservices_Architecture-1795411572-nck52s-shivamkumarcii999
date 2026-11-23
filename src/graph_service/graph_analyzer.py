"""In-Memory Graph Analysis Service for Relationship Pattern Traversal & Ring Detection."""
import time
from collections import deque
from typing import Dict, Any, List, Set

class GraphAnalyzer:
    def __init__(self):
        # Multi-entity graph adjacency lists
        self.adj: Dict[str, Set[str]] = {}
        # Entity labels: node_id -> label
        self.node_labels: Dict[str, str] = {}
        # Known confirmed fraud nodes
        self.confirmed_fraud_nodes: Set[str] = set()
        # Infrastructure link counts (e.g. device -> set of cards)
        self.device_cards: Dict[str, Set[str]] = {}

    def add_edge(self, u: str, v: str, u_label: str = "", v_label: str = ""):
        if u not in self.adj: self.adj[u] = set()
        if v not in self.adj: self.adj[v] = set()
        self.adj[u].add(v)
        self.adj[v].add(u)
        if u_label: self.node_labels[u] = u_label
        if v_label: self.node_labels[v] = v_label

        if u_label == "Device" and v_label == "Card":
            if u not in self.device_cards: self.device_cards[u] = set()
            self.device_cards[u].add(v)
        elif v_label == "Device" and u_label == "Card":
            if v not in self.device_cards: self.device_cards[v] = set()
            self.device_cards[v].add(u)

    def mark_fraud(self, node_id: str):
        self.confirmed_fraud_nodes.add(node_id)

    def shortest_path_to_fraud(self, start_node: str, max_depth: int = 4) -> int:
        """BFS shortest path from start_node to any confirmed fraud entity."""
        if start_node in self.confirmed_fraud_nodes:
            return 0
        queue = deque([(start_node, 0)])
        visited = {start_node}

        while queue:
            curr, depth = queue.popleft()
            if depth >= max_depth:
                break
            for neighbor in self.adj.get(curr, []):
                if neighbor in self.confirmed_fraud_nodes:
                    return depth + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
        return 999 # No fraud path within max_depth

    def analyze(self, tx_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes graph relationship risk for an incoming transaction."""
        start_time = time.perf_counter()
        card_hash = tx_payload.get("card_number_hash", "")
        device_fp = tx_payload.get("device_fingerprint", "")
        ip_addr = tx_payload.get("ip_address", "")
        merchant_id = tx_payload.get("merchant_id", "")

        # Upsert entities into in-memory graph
        if card_hash and device_fp:
            self.add_edge(card_hash, device_fp, "Card", "Device")
        if card_hash and ip_addr:
            self.add_edge(card_hash, ip_addr, "Card", "IP")
        if card_hash and merchant_id:
            self.add_edge(card_hash, merchant_id, "Card", "Merchant")

        # 1. Shortest path to confirmed fraud
        hops = self.shortest_path_to_fraud(card_hash, max_depth=4)

        # 2. Shared infrastructure check
        connected_cards = len(self.device_cards.get(device_fp, set())) if device_fp else 0

        # 3. Community / Ring heuristics
        graph_risk_score = 0
        is_ring = False
        matched_topology = "NORMAL"

        if hops == 0:
            graph_risk_score = 1000
            matched_topology = "CONFIRMED_FRAUD_NODE"
        elif hops == 1:
            graph_risk_score = 850
            matched_topology = "DIRECT_1_HOP_TO_FRAUD"
        elif hops == 2:
            graph_risk_score = 650
            matched_topology = "2_HOP_FRAUD_NEIGHBORHOOD"
        elif hops <= 4:
            graph_risk_score = 300

        # Shared device multi-card syndicate check
        if connected_cards >= 5:
            graph_risk_score = max(graph_risk_score, 800)
            is_ring = True
            matched_topology = "SHARED_DEVICE_FRAUD_RING"
        elif connected_cards >= 3:
            graph_risk_score = max(graph_risk_score, 450)

        ms = (time.perf_counter() - start_time) * 1000

        return {
            "graph_risk_score": graph_risk_score,
            "degrees_to_fraud": hops if hops < 999 else -1,
            "shared_device_card_count": connected_cards,
            "part_of_fraud_ring": is_ring,
            "matched_topology": matched_topology,
            "traversal_latency_ms": round(ms, 2)
        }
