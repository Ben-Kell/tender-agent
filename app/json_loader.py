import json
from pathlib import Path
from typing import Dict, Any


def load_tender_output_json(tender_id: str, filename: str):
    path = Path("tenders") / tender_id / "output" / filename

    if not path.exists():
        raise FileNotFoundError(f"Output file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))

def load_json_output(tender_id: str, filename: str) -> Dict[str, Any]:
    path = Path("tenders") / tender_id / "output" / filename

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_proposal_overview_plan(tender_id: str) -> Dict[str, Any]:
    return load_json_output(tender_id, "proposal_overview_plan.json")