from pathlib import Path
from typing import Any
import json


def write_tender_output(tender_id: str, filename: str, data: Any) -> str:
    output_dir = Path("tenders") / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    # -----------------------------------------
    # If data is dict/list → write as pretty JSON
    # -----------------------------------------
    if isinstance(data, (dict, list)):
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    # -----------------------------------------
    # If data is string → write as-is (CRITICAL)
    # -----------------------------------------
    elif isinstance(data, str):
        content = data.strip() + "\n"

    # -----------------------------------------
    # Fallback → convert to string
    # -----------------------------------------
    else:
        content = str(data)

    # -----------------------------------------
    # Write file preserving formatting
    # -----------------------------------------
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    return str(output_path).replace("\\", "/")