# app/docx_payload_builder.py
import json
from pathlib import Path
from typing import Dict, Any, List

from app.docx_parser import parse_markdown_sections


def load_mapping(mapping_path: str) -> Dict[str, Any]:
    return json.loads(Path(mapping_path).read_text(encoding="utf-8"))


def clean_text_for_docx(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # docxtemplater handles \n as line breaks inside plain text replacements reasonably
    return text.strip()


def extract_metadata(tender_id: str) -> Dict[str, Any]:
    extracted_path = Path(f"tenders/{tender_id}/output/extracted_requirements.json")
    if not extracted_path.exists():
        return {}

    data = json.loads(extracted_path.read_text(encoding="utf-8"))
    return data.get("metadata", {})


def build_docx_payload(
    tender_id: str,
    markdown_text: str,
    mapping_path: str = "templates/fujitsu_response_template.mapping.json"
) -> Dict[str, Any]:
    mapping = load_mapping(mapping_path)
    parsed_sections = parse_markdown_sections(markdown_text)
    metadata = extract_metadata(tender_id)

    payload: Dict[str, Any] = {}

    # metadata fields
    payload["tender_reference"] = metadata.get("tender_reference", "")
    payload["tender_title"] = metadata.get("tender_title", "")
    payload["customer"] = metadata.get("customer", "")
    payload["abn"] = metadata.get("abn", "")
    payload["submission_date"] = metadata.get("submission_date", "")

    # default all mapped section placeholders to empty string
    for _, placeholder in mapping.get("sections", {}).items():
        payload[placeholder] = ""

    # fill mapped sections
    reverse_section_map = mapping.get("sections", {})
    for section in parsed_sections:
        heading = section["heading"]
        content = clean_text_for_docx(section["content"])
        placeholder = reverse_section_map.get(heading)
        if placeholder:
            payload[placeholder] = content

    return payload


def write_docx_payload(tender_id: str, payload: Dict[str, Any]) -> str:
    output_path = Path(f"tenders/{tender_id}/output/docx_payload.json")
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(output_path)