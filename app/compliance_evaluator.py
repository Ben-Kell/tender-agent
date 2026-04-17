from __future__ import annotations

import json
from typing import Dict, Any, List

from app.json_loader import load_tender_output_json
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat


def evaluate_compliance(tender_id: str) -> Dict[str, Any]:
    extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
    section_drafts = load_tender_output_json(tender_id, "section_drafts.json")

    requirements = extracted.get("requirements", [])
    sections = section_drafts.get("sections", [])

    system_prompt = load_prompt("evaluate_compliance.md")

    user_prompt = f"""
TENDER ID: {tender_id}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

SECTION DRAFTS:
{json.dumps(sections, indent=2)}

Return JSON only.
"""

    raw = chat(system_prompt, user_prompt, model="gpt-4o")

    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"compliance": [], "error": raw[:1000]}

    write_tender_output(
        tender_id,
        "compliance_matrix.json",
        json.dumps(parsed, indent=2)
    )

    return parsed