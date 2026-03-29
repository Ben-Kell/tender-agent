from pathlib import Path
from typing import List, Dict


def load_normalized_tender_docs(tender_id: str) -> List[Dict[str, str]]:
    base = Path("tenders") / tender_id / "input" / "02_normalised"

    if not base.exists():
        raise FileNotFoundError(f"Normalised input folder not found: {base}")

    docs = []
    for path in sorted(base.glob("*.md")):
        docs.append({
            "filename": path.name,
            "content": path.read_text(encoding="utf-8")
        })

    if not docs:
        raise FileNotFoundError(f"No markdown files found in: {base}")

    return docs