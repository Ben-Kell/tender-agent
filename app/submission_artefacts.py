import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.output_writer import write_tender_output
from app.json_loader import load_tender_output_json


def build_submission_artefacts(tender_id: str) -> Dict[str, Any]:
    output_dir = Path("tenders") / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    artefacts: List[Dict[str, Any]] = []

    existing_files = _list_existing_output_files(output_dir)

    # -----------------------------
    # Core response artefacts
    # -----------------------------
    artefacts.append(
        _build_fixed_artefact(
            tender_id=tender_id,
            output_dir=output_dir,
            existing_files=existing_files,
            name="Proposal Overview",
            artefact_type="core_response",
            required=True,
            source="system_generated",
            candidate_filenames=["proposal_overview.docx"],
        )
    )

    artefacts.append(
        _build_fixed_artefact(
            tender_id=tender_id,
            output_dir=output_dir,
            existing_files=existing_files,
            name="AIC Plan",
            artefact_type="core_response",
            required=True,
            source="system_generated",
            candidate_filenames=["fujitsu_aic_plan.docx"],
        )
    )

    # -----------------------------
    # Conditional supporting docs
    # -----------------------------
    supplier_background_requirement = _safe_load_tender_output_json(
        tender_id, "supplier_background_requirement.json"
    )
    if _is_required_requirement(supplier_background_requirement):
        artefacts.append(
            _build_fixed_artefact(
                tender_id=tender_id,
                output_dir=output_dir,
                existing_files=existing_files,
                name="Supplier Background",
                artefact_type="supporting_document",
                required=True,
                source="requirement_detected",
                candidate_filenames=[
                    "supplier_background.docx",
                    "fujitsu_supplier_background.docx",
                ],
            )
        )

    past_performance_requirement = _safe_load_tender_output_json(
        tender_id, "past_performance_requirement.json"
    )
    if _is_required_requirement(past_performance_requirement):
        artefacts.append(
            _build_fixed_artefact(
                tender_id=tender_id,
                output_dir=output_dir,
                existing_files=existing_files,
                name="Past Performance",
                artefact_type="supporting_document",
                required=True,
                source="requirement_detected",
                candidate_filenames=["fujitsu_past_performance.docx"],
            )
        )

    # -----------------------------
    # Returnable documents
    # -----------------------------
    returnable_documents_payload = _safe_load_tender_output_json(
        tender_id, "returnable_documents.json"
    )
    returnable_documents = _extract_returnable_documents(returnable_documents_payload)

    for document in returnable_documents:
        artefacts.append(
            _build_returnable_artefact(
                tender_id=tender_id,
                output_dir=output_dir,
                existing_files=existing_files,
                document=document,
            )
        )

    submission_artefacts_payload = {"artefacts": artefacts}
    submission_checklist_markdown = _build_submission_checklist_markdown(artefacts)

    write_tender_output(
        tender_id,
        "submission_artefacts.json",
        json.dumps(submission_artefacts_payload, indent=2),
    )

    write_tender_output(
        tender_id,
        "submission_checklist.md",
        submission_checklist_markdown,
    )

    return {
        "submission_artefacts": submission_artefacts_payload,
        "submission_checklist_markdown": submission_checklist_markdown,
        "submission_artefacts_json_path": _normalise_path(
            output_dir / "submission_artefacts.json"
        ),
        "submission_checklist_md_path": _normalise_path(
            output_dir / "submission_checklist.md"
        ),
    }


def _build_fixed_artefact(
    tender_id: str,
    output_dir: Path,
    existing_files: Dict[str, Path],
    name: str,
    artefact_type: str,
    required: bool,
    source: str,
    candidate_filenames: List[str],
) -> Dict[str, Any]:
    file_path = _find_existing_file(output_dir, existing_files, candidate_filenames)

    if file_path:
        status = "generated"
    else:
        status = "missing"

    return {
        "name": name,
        "type": artefact_type,
        "required": required,
        "source": source,
        "status": status,
        "file_path": file_path,
    }


def _build_returnable_artefact(
    tender_id: str,
    output_dir: Path,
    existing_files: Dict[str, Path],
    document: Dict[str, Any],
) -> Dict[str, Any]:
    document_name = _extract_document_name(document)
    required = _extract_document_required_flag(document)

    candidate_filenames = _build_returnable_candidate_filenames(document_name, document)
    file_path = _find_existing_file(output_dir, existing_files, candidate_filenames)

    if file_path:
        status = "generated"
    else:
        status = "manual_completion_required"

    return {
        "name": document_name,
        "type": "returnable_document",
        "required": required,
        "source": "returnable_detector",
        "status": status,
        "file_path": file_path,
    }


def _safe_load_tender_output_json(tender_id: str, filename: str) -> Dict[str, Any]:
    try:
        payload = load_tender_output_json(tender_id, filename)
        if isinstance(payload, dict):
            return payload
        return {}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    except Exception:
        return {}


def _list_existing_output_files(output_dir: Path) -> Dict[str, Path]:
    existing_files: Dict[str, Path] = {}

    if not output_dir.exists():
        return existing_files

    for file_path in output_dir.iterdir():
        if file_path.is_file():
            existing_files[file_path.name.lower()] = file_path

    return existing_files


def _find_existing_file(
    output_dir: Path,
    existing_files: Dict[str, Path],
    candidate_filenames: List[str],
) -> Optional[str]:
    for candidate in candidate_filenames:
        candidate_lower = candidate.lower()
        if candidate_lower in existing_files:
            return _normalise_path(existing_files[candidate_lower])

    return None


def _extract_returnable_documents(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    if isinstance(payload.get("documents"), list):
        return [item for item in payload["documents"] if isinstance(item, dict)]

    if isinstance(payload.get("returnable_documents"), list):
        return [item for item in payload["returnable_documents"] if isinstance(item, dict)]

    if isinstance(payload.get("artefacts"), list):
        return [item for item in payload["artefacts"] if isinstance(item, dict)]

    return []


def _is_required_requirement(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False

    keys_to_check = [
        "required",
        "is_required",
        "required_for_submission",
        "needed",
        "detected",
        "include",
        "should_generate",
    ]

    for key in keys_to_check:
        if key in payload:
            return _to_bool(payload.get(key))

    return False


def _extract_document_name(document: Dict[str, Any]) -> str:
    keys_to_check = [
        "name",
        "document_name",
        "title",
        "file_name",
        "filename",
    ]

    for key in keys_to_check:
        value = document.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return "Unnamed Returnable Document"


def _extract_document_required_flag(document: Dict[str, Any]) -> bool:
    keys_to_check = [
        "required",
        "is_required",
        "mandatory",
        "must_return",
        "return_required",
    ]

    for key in keys_to_check:
        if key in document:
            return _to_bool(document.get(key))

    return True


def _build_returnable_candidate_filenames(
    document_name: str,
    document: Dict[str, Any],
) -> List[str]:
    candidates: List[str] = []

    raw_file_keys = ["file_name", "filename", "source_file", "document_file"]
    for key in raw_file_keys:
        value = document.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())

    slug = _slugify(document_name)

    candidates.append(f"{slug}.docx")
    candidates.append(f"{slug}.xlsx")
    candidates.append(f"{slug}.xls")
    candidates.append(f"{slug}.pdf")
    candidates.append(f"{slug}.doc")
    candidates.append(f"{slug}.csv")

    return _deduplicate_preserve_order(candidates)


def _build_submission_checklist_markdown(artefacts: List[Dict[str, Any]]) -> str:
    required_artefacts = [item for item in artefacts if item.get("required") is True]
    optional_artefacts = [item for item in artefacts if item.get("required") is not True]

    lines: List[str] = []
    lines.append("# Submission Checklist")
    lines.append("")
    lines.append("## Required Artefacts")
    lines.append("")

    if not required_artefacts:
        lines.append("* None detected")
        lines.append("")
    else:
        for artefact in required_artefacts:
            lines.append(_build_checklist_line(artefact))
        lines.append("")

    if optional_artefacts:
        lines.append("## Optional Artefacts")
        lines.append("")
        for artefact in optional_artefacts:
            lines.append(_build_checklist_line(artefact))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _build_checklist_line(artefact: Dict[str, Any]) -> str:
    status = str(artefact.get("status", "")).strip()
    name = str(artefact.get("name", "Unnamed Artefact")).strip()

    checked_statuses = {"generated"}
    unchecked_suffix_map = {
        "manual_completion_required": "manual completion required",
        "missing": "not generated",
    }

    if status in checked_statuses:
        return f"* [x] {name}"

    suffix = unchecked_suffix_map.get(status, status.replace("_", " ").strip())
    if suffix:
        return f"* [ ] {name} ({suffix})"

    return f"* [ ] {name}"


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalised = value.strip().lower()
        return normalised in {"true", "yes", "y", "1", "required", "mandatory"}

    if isinstance(value, int):
        return value == 1

    return False


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    value = value.strip("_")
    return value or "unnamed_document"


def _deduplicate_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []

    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)

    return result


def _normalise_path(path: Path) -> str:
    return str(path).replace("\\", "/")