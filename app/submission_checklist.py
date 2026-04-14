from pathlib import Path
from app.submission_artefacts import build_submission_artefacts


def _output_dir_for_tender(tender_id: str) -> Path:
    return Path("tenders") / tender_id / "output"


def generate_submission_artefacts_json(tender_id: str):
    result = build_submission_artefacts(tender_id)
    return result["submission_artefacts"]


def generate_submission_checklist_md(tender_id: str):
    result = build_submission_artefacts(tender_id)
    output_dir = _output_dir_for_tender(tender_id)

    return {
        "tender_id": tender_id,
        "submission_readiness_percent": result["submission_readiness"]["readiness_percent"],
        "required_count": result["submission_readiness"]["total_required_count"],
        "produced_count": result["submission_readiness"]["generated_required_count"],
        "missing_count": result["submission_readiness"]["missing_required_count"],
        "checklist_path": str(output_dir / "submission_checklist.md"),
    }


'''import json
from pathlib import Path


def _output_dir_for_tender(tender_id: str) -> Path:
    return Path("tenders") / tender_id / "output"


def _read_json_if_exists(file_path: Path):
    if not file_path.exists() or not file_path.is_file():
        return None

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalise_required_items(returnable_data):
    required_items = []

    if returnable_data is None:
        return required_items

    if isinstance(returnable_data, list):
        for item in returnable_data:
            if isinstance(item, str):
                required_items.append(item)
            elif isinstance(item, dict):
                name = (
                    item.get("filename")
                    or item.get("file_name")
                    or item.get("document_name")
                    or item.get("name")
                    or item.get("title")
                )
                required_flag = item.get("required", True)
                if name and required_flag:
                    required_items.append(str(name))
        return required_items

    if isinstance(returnable_data, dict):
        candidate_lists = [
            returnable_data.get("required_documents"),
            returnable_data.get("returnable_documents"),
            returnable_data.get("documents"),
            returnable_data.get("files"),
            returnable_data.get("items"),
        ]

        for candidate in candidate_lists:
            if isinstance(candidate, list):
                return _normalise_required_items(candidate)

    return required_items


def generate_submission_artefacts_json(tender_id: str):
    output_dir = _output_dir_for_tender(tender_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    returnable_json_path = output_dir / "returnable_documents.json"
    returnable_data = _read_json_if_exists(returnable_json_path)
    required_items = _normalise_required_items(returnable_data)

    produced_files = sorted([p.name for p in output_dir.iterdir() if p.is_file()])

    artefacts_payload = {
        "tender_id": tender_id,
        "required_artefacts": required_items,
        "produced_files": produced_files,
    }

    submission_artefacts_path = output_dir / "submission_artefacts.json"
    with submission_artefacts_path.open("w", encoding="utf-8") as f:
        json.dump(artefacts_payload, f, indent=2)

    return artefacts_payload


def generate_submission_checklist_md(tender_id: str):
    output_dir = _output_dir_for_tender(tender_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    artefacts_json_path = output_dir / "submission_artefacts.json"
    artefacts_payload = _read_json_if_exists(artefacts_json_path)

    if artefacts_payload is None:
        artefacts_payload = generate_submission_artefacts_json(tender_id)

    required_items = artefacts_payload.get("required_artefacts", [])
    produced_files = artefacts_payload.get("produced_files", [])

    produced_required = []
    missing_required = []

    produced_set_lower = {name.lower() for name in produced_files}

    for required_name in required_items:
        if required_name.lower() in produced_set_lower:
            produced_required.append(required_name)
        else:
            missing_required.append(required_name)

    required_count = len(required_items)
    produced_count = len(produced_required)

    if required_count == 0:
        readiness_percent = 100
    else:
        readiness_percent = round((produced_count / required_count) * 100)

    lines = []
    lines.append(f"# Submission Checklist - {tender_id}")
    lines.append("")
    lines.append(f"Submission Readiness: {readiness_percent}%")
    lines.append("")
    lines.append(f"Required Artefacts Generated: {produced_count} of {required_count}")
    lines.append("")

    lines.append("## Required Artefacts")
    lines.append("")
    if required_items:
        for item in required_items:
            tick = "x" if item in produced_required else " "
            lines.append(f"- [{tick}] {item}")
    else:
        lines.append("- None identified")
    lines.append("")

    lines.append("## Missing Required Artefacts")
    lines.append("")
    if missing_required:
        for item in missing_required:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Produced Required Artefacts")
    lines.append("")
    if produced_required:
        for item in produced_required:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")

    checklist_path = output_dir / "submission_checklist.md"
    with checklist_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {
        "tender_id": tender_id,
        "submission_readiness_percent": readiness_percent,
        "required_count": required_count,
        "produced_count": produced_count,
        "missing_count": len(missing_required),
        "checklist_path": str(checklist_path),
    }'''