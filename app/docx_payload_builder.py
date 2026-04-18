import json
import re
from pathlib import Path
from typing import Dict, Any

from app.docx_parser import parse_markdown_sections


def load_mapping(mapping_path: str) -> Dict[str, Any]:
    return json.loads(Path(mapping_path).read_text(encoding="utf-8"))


def clean_text_for_docx(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip()


def extract_metadata(tender_id: str) -> Dict[str, Any]:
    extracted_path = Path(f"tenders/{tender_id}/output/extracted_requirements.json")

    if not extracted_path.exists():
        return {}

    data = json.loads(extracted_path.read_text(encoding="utf-8"))
    return data.get("metadata", {})


def normalise_section_heading(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^\d+\.\s*", "", text)
    return text.lower()


def build_docx_payload(
    tender_id: str,
    markdown_text: str,
    mapping_path: str = "templates/fujitsu_response_template.mapping.json"
) -> Dict[str, Any]:
    mapping = load_mapping(mapping_path)
    parsed_sections = parse_markdown_sections(markdown_text)
    metadata = extract_metadata(tender_id)

    payload: Dict[str, Any] = {}

    # Cover page / document metadata
    payload["tender_reference"] = metadata.get("tender_reference", "")
    payload["tender_title"] = metadata.get("tender_title", "")
    payload["customer"] = metadata.get("customer", "")
    payload["submission_date"] = metadata.get("submission_date", "")
    payload["abn"] = metadata.get("abn", "")

    # Optional extra cover page values if you want to use them in Word
    payload["document_title"] = "Tender Response"
    payload["company_name"] = "Fujitsu Australia Limited"

    section_map = mapping.get("sections", {})
    normalised_map = {
        normalise_section_heading(source_heading): placeholder
        for source_heading, placeholder in section_map.items()
    }

    for placeholder in section_map.values():
        payload[placeholder] = ""

    matched_headings = []
    unmatched_headings = []

    for section in parsed_sections:
        heading = section["heading"]
        content = clean_text_for_docx(section["content"])
        placeholder = normalised_map.get(normalise_section_heading(heading))

        if placeholder:
            payload[placeholder] = content
            matched_headings.append({"heading": heading, "placeholder": placeholder})
        else:
            unmatched_headings.append(heading)

    payload["_debug_matched_headings"] = matched_headings
    payload["_debug_unmatched_headings"] = unmatched_headings

    return payload


def write_docx_payload(tender_id: str, payload: Dict[str, Any]) -> str:
    output_path = Path(f"tenders/{tender_id}/output/docx_payload.json")
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    return str(output_path)