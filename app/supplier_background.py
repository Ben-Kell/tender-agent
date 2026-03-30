from pathlib import Path
import shutil
from typing import Dict, List, Any


SUPPLIER_BACKGROUND_OUTPUT_FILENAME = "fujitsu_supplier_background.docx"
SUPPLIER_BACKGROUND_TEMPLATE_FILENAME = "fujitsu_supplier_background_template.docx"


SUPPLIER_BACKGROUND_PHRASES = [
    "supplier background",
    "company overview",
    "corporate overview",
    "company background",
    "supplier overview",
    "organisation overview",
    "organization overview",
    "bidder profile",
    "company profile",
    "supplier profile",
    "corporate profile",
    "background of the supplier",
    "overview of the supplier",
]

PAST_PERFORMANCE_OUTPUT_FILENAME = "fujitsu_past_performance.docx"
PAST_PERFORMANCE_TEMPLATE_FILENAME = "fujitsu_past_performance.docx"

PAST_PERFORMANCE_PHRASES = [
    "past performance",
    "previous performance",
    "prior performance",
    "relevant experience",
    "previous experience",
    "similar experience",
    "demonstrated experience",
    "evidence of experience",
    "track record",
    "past projects",
    "similar work performed",
    "examples of previous work",
    "case studies",
    "customer references",
    "referees",
    "reference projects",
]

def _normalise_requirement_text(requirement: Any) -> str:
    if isinstance(requirement, str):
        return requirement.lower()

    if isinstance(requirement, dict):
        parts = []
        for key in ["requirement", "text", "title", "description", "clause", "notes", "requirement_text"]:
            value = requirement.get(key)
            if value:
                parts.append(str(value))
        return " ".join(parts).lower()

    return str(requirement).lower()


def detect_supplier_background_requirement(extracted_requirements: Dict) -> Dict:
    requirements: List[Any] = extracted_requirements.get("requirements", [])
    matched_requirements = []

    for req in requirements:
        text = _normalise_requirement_text(req)

        matched_phrases = [phrase for phrase in SUPPLIER_BACKGROUND_PHRASES if phrase in text]
        if matched_phrases:
            matched_requirements.append({
                "matched_phrases": matched_phrases,
                "requirement": req,
            })

    is_required = len(matched_requirements) > 0

    return {
        "supplier_background_required": is_required,
        "template_filename": SUPPLIER_BACKGROUND_TEMPLATE_FILENAME if is_required else None,
        "output_filename": SUPPLIER_BACKGROUND_OUTPUT_FILENAME if is_required else None,
        "matches": matched_requirements,
        "confidence": 0.95 if is_required else 0.0,
    }

def detect_past_performance_requirement(extracted_requirements: Dict) -> Dict:
    requirements: List[Any] = extracted_requirements.get("requirements", [])
    matched_requirements = []

    for req in requirements:
        text = _normalise_requirement_text(req)

        matched_phrases = [phrase for phrase in PAST_PERFORMANCE_PHRASES if phrase in text]
        if matched_phrases:
            matched_requirements.append({
                "matched_phrases": matched_phrases,
                "requirement": req,
            })

    is_required = len(matched_requirements) > 0

    return {
        "past_performance_required": is_required,
        "template_filename": PAST_PERFORMANCE_TEMPLATE_FILENAME if is_required else None,
        "output_filename": PAST_PERFORMANCE_OUTPUT_FILENAME if is_required else None,
        "matches": matched_requirements,
        "confidence": 0.95 if is_required else 0.0,
    }

def copy_supplier_background_template_if_required(
    tender_id: str,
    detection_result: Dict,
    base_dir: str = ".",
) -> Dict:
    if not detection_result.get("supplier_background_required"):
        return {
            "copied": False,
            "reason": "Supplier background not required",
            "output_path": None,
        }

    base_path = Path(base_dir)
    template_path = base_path / "templates" / SUPPLIER_BACKGROUND_TEMPLATE_FILENAME
    output_dir = base_path / "tenders" / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / SUPPLIER_BACKGROUND_OUTPUT_FILENAME

    if not template_path.exists():
        raise FileNotFoundError(f"Supplier background template not found: {template_path}")

    shutil.copy2(template_path, output_path)

    return {
        "copied": True,
        "reason": "Supplier background requirement detected",
        "output_path": str(output_path),
    }

def copy_past_performance_template_if_required(
    tender_id: str,
    detection_result: Dict,
    base_dir: str = ".",
) -> Dict:
    if not detection_result.get("past_performance_required"):
        return {
            "copied": False,
            "reason": "Past performance not required",
            "output_path": None,
        }

    base_path = Path(base_dir)
    template_path = base_path / "templates" / PAST_PERFORMANCE_TEMPLATE_FILENAME
    output_dir = base_path / "tenders" / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / PAST_PERFORMANCE_OUTPUT_FILENAME

    if not template_path.exists():
        raise FileNotFoundError(f"Past performance template not found: {template_path}")

    shutil.copy2(template_path, output_path)

    return {
        "copied": True,
        "reason": "Past performance requirement detected",
        "output_path": str(output_path),
    }