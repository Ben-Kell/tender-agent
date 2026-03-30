from pathlib import Path
from typing import Dict, Any, List
import shutil

from app.tender_bootstrap import create_tender_structure
from app.normaliser import normalise_all_documents


def copy_dump_files_to_customer_issued(tender_id: str) -> Dict[str, Any]:
    tender_id = tender_id.strip()
    if not tender_id:
        raise ValueError("tender_id is required")

    dump_path = Path("dump") / tender_id
    customer_issued_path = Path("tenders") / tender_id / "input" / "01_customer_issued"

    if not dump_path.exists():
        raise FileNotFoundError(f"Dump folder not found: {dump_path}")

    if not dump_path.is_dir():
        raise ValueError(f"Dump path is not a folder: {dump_path}")

    copied_files: List[str] = []
    skipped_files: List[str] = []

    for item in dump_path.iterdir():
        if not item.is_file():
            continue

        destination = customer_issued_path / item.name

        if destination.exists():
            skipped_files.append(str(destination))
            continue

        shutil.copy2(item, destination)
        copied_files.append(str(destination))

    return {
        "dump_path": str(dump_path),
        "customer_issued_path": str(customer_issued_path),
        "copied_files": copied_files,
        "skipped_files": skipped_files,
    }


def create_and_ingest_tender(tender_id: str) -> Dict[str, Any]:
    structure_result = create_tender_structure(tender_id)
    copy_result = copy_dump_files_to_customer_issued(tender_id)
    normalise_result = normalise_all_documents(tender_id)

    return {
        "tender_id": tender_id,
        "structure": structure_result,
        "copy": copy_result,
        "normalise": normalise_result,
    }