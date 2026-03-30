from pathlib import Path
from typing import Dict, Any
import json


DEFAULT_SUBFOLDERS = [
    "input/01_customer_issued",
    "input/02_normalised",
    "output",
]

DEFAULT_FILES = {
    "output/template_map.json": json.dumps({"sections": []}, indent=2),
    "output/section_drafts.json": json.dumps({"sections": []}, indent=2),
}


def create_tender_structure(tender_id: str) -> Dict[str, Any]:
    tender_id = tender_id.strip()
    if not tender_id:
        raise ValueError("tender_id is required")

    base_path = Path("tenders") / tender_id
    base_path.mkdir(parents=True, exist_ok=True)

    created_folders = []
    existing_folders = []
    created_files = []
    existing_files = []

    for folder_name in DEFAULT_SUBFOLDERS:
        folder_path = base_path / folder_name
        if folder_path.exists():
            existing_folders.append(str(folder_path))
        else:
            folder_path.mkdir(parents=True, exist_ok=True)
            created_folders.append(str(folder_path))

    for relative_file_path, content in DEFAULT_FILES.items():
        file_path = base_path / relative_file_path
        if file_path.exists():
            existing_files.append(str(file_path))
        else:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            created_files.append(str(file_path))

    return {
        "tender_id": tender_id,
        "base_path": str(base_path),
        "created_folders": created_folders,
        "existing_folders": existing_folders,
        "created_files": created_files,
        "existing_files": existing_files,
    }