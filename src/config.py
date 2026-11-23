"""ShieldPay Fraud Detection Platform Configuration & Constants."""
import os
import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "configs"
RULES_FILE = CONFIG_DIR / "rules.yaml"

# Global Scoring Weights
WEIGHT_RULE = 0.40
WEIGHT_ML = 0.35
WEIGHT_GRAPH = 0.25

# Action Decision Thresholds
THRESHOLD_APPROVE = 200     # 0 - 199: AUTO_APPROVE
THRESHOLD_STEP_UP = 600     # 200 - 599: STEP_UP_AUTHENTICATION
THRESHOLD_REVIEW = 800      # 600 - 799: MANUAL_REVIEW_QUEUE
# 800 - 1000: AUTO_DECLINE

def load_rules_yaml():
    """Loads rule definitions from configs/rules.yaml."""
    if not RULES_FILE.exists():
        return []
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("rules", [])
