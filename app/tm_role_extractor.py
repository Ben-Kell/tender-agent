from __future__ import annotations

import json
import re
from typing import Dict, Any, List

from app.file_loader import load_normalised_tender_docs
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat


def _clean_role_record(role: Dict[str, Any]) -> Dict[str, Any]:
    def clean_text(value: Any) -> str:
        if value is None:
            return ""
        return re.sub(r"\s+", " ", str(value)).strip()

    def clean_int(value: Any):
        if value in (None, "", "null"):
            return None
        try:
            return int(value)
        except Exception:
            return None

    quantity = clean_int(role.get("quantity"))
    if quantity is None:
        quantity = 1

    pricing_unit_required = clean_text(role.get("pricing_unit_required")).lower()
    if pricing_unit_required not in {"day", "hour"}:
        pricing_unit_required = ""

    return {
        "tender_role_name": clean_text(role.get("tender_role_name")),
        "sfia_code": clean_text(role.get("sfia_code")).upper(),
        "sfia_level": clean_int(role.get("sfia_level")),
        "quantity": quantity,
        "clearance": clean_text(role.get("clearance")),
        "pricing_unit_required": pricing_unit_required,
        "duration_years": clean_int(role.get("duration_years")),
        "duration_months": clean_int(role.get("duration_months")),
        "source_snippet": clean_text(role.get("source_snippet")),
    }


def extract_tm_roles(tender_id: str) -> Dict[str, Any]:
    docs = load_normalised_tender_docs(tender_id)

    combined_text_parts: List[str] = []
    for doc in docs:
        filename = doc.get("filename", "unknown")
        content = doc.get("content", "")
        if not content:
            continue
        combined_text_parts.append(f"# SOURCE: {filename}\n{content}")

    combined_text = "\n\n".join(combined_text_parts)

    prompt_template = load_prompt("extract_tm_roles.md")

    user_prompt = f"""
Tender ID: {tender_id}

Tender documents:
{combined_text}
""".strip()

    raw_response = chat(
        system_prompt=prompt_template,
        user_prompt=user_prompt,
        model="gpt-4o",
    )

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        parsed = {"tender_roles": []}

    roles = parsed.get("tender_roles", [])
    if not isinstance(roles, list):
        roles = []

    cleaned_roles = []
    seen = set()

    for role in roles:
        if not isinstance(role, dict):
            continue
        cleaned = _clean_role_record(role)

        dedupe_key = (
            cleaned["tender_role_name"].lower(),
            cleaned["sfia_code"],
            cleaned["sfia_level"],
            cleaned["quantity"],
            cleaned["clearance"].lower(),
        )

        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        cleaned_roles.append(cleaned)

    result = {"tender_roles": cleaned_roles}

    write_tender_output(
        tender_id,
        "tm_tender_roles.json",
        json.dumps(result, indent=2)
    )

    return result