import json
from pathlib import Path
RULES_PATH=Path(__file__).resolve().parent.parent/"data"/"rules.json"
def load_rules():
    with RULES_PATH.open("r",encoding="utf-8") as f:return json.load(f)
