import json
from app.openai_client import chat
from app.prompt_loader import load_prompt


def route_requirements_for_main_response(tender_id: str, requirements: list[dict]) -> dict:
    """
    Decide which requirements belong in the main Fujitsu response document
    versus other returnable/customer-issued documents.
    """

    system_prompt = load_prompt("system_instructions.md")

    user_prompt = f"""
Determine which tender requirements should be addressed in the main Fujitsu response document.

Rules:
- The main Fujitsu response document must contain only:
  1. Executive Summary
  2. Response to Customer Requirements
- Route a requirement to "main_response" only if it should be addressed in narrative prose in the main Fujitsu response.
- Route a requirement to "other_document" if it is better addressed in:
  - a customer-issued returnable form
  - a pricing schedule
  - a supplier background document
  - a past performance document
  - another separate submission artefact
- Be conservative. If a requirement looks like it belongs in a separate schedule, form, rate card, attachment, or customer returnable, do not put it in the main response.
- Return raw JSON only. Do not use markdown. Do not use triple backticks.

Return exactly this structure:
{{
  "main_response_section_title": "Response to Customer Requirements",
  "main_response_requirements": [
    {{
      "requirement_id": "REQ-001",
      "reason": "Why it belongs in the main response"
    }}
  ],
  "other_document_requirements": [
    {{
      "requirement_id": "REQ-002",
      "reason": "Why it belongs elsewhere"
    }}
  ]
}}

TENDER ID: {tender_id}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}
""".strip()

    raw_output = chat(system_prompt, user_prompt)
    cleaned_output = raw_output.strip()

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output[len("```json"):].strip()
    elif cleaned_output.startswith("```"):
        cleaned_output = cleaned_output[len("```"):].strip()

    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output[:-3].strip()

    try:
        parsed = json.loads(cleaned_output)
        parsed.setdefault("main_response_section_title", "Response to Customer Requirements")
        parsed.setdefault("main_response_requirements", [])
        parsed.setdefault("other_document_requirements", [])
        return parsed
    except json.JSONDecodeError:
        return {
            "main_response_section_title": "Response to Customer Requirements",
            "main_response_requirements": [],
            "other_document_requirements": [],
            "error": "Failed to parse model output as JSON",
            "raw_output": raw_output,
        }