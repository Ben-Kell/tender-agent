import json
from pathlib import Path
from typing import Any


def write_tender_output(tender_id: str, filename: str, data: Any) -> str:
    output_dir = Path("tenders") / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(output_path)