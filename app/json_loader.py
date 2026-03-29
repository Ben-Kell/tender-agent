import json
from pathlib import Path


def load_tender_output_json(tender_id: str, filename: str):
    path = Path("tenders") / tender_id / "output" / filename

    if not path.exists():
        raise FileNotFoundError(f"Output file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))