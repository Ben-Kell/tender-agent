import json
from typing import Dict, Any, List

from app.prompt_loader import load_prompt
from app.openai_client import chat
from app.output_writer import write_tender_output
from app.json_loader import load_json_output


def _extract_evaluation_criteria(extracted_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
    requirements = extracted_requirements.get("requirements", [])
    evaluation_criteria = []

    for req in requirements:
        category = (req.get("category") or "").strip().lower()
        section = (req.get("section") or "").strip().lower()
        title = (
            req.get("title")
            or req.get("requirement_title")
            or req.get("criterion_title")
            or req.get("section")
            or "Untitled criterion"
        )
        text = req.get("text") or req.get("requirement_text") or ""
        requirement_id = (
            req.get("requirement_id")
            or req.get("id")
            or req.get("criterion_id")
            or ""
        )

        combined = f"{category} {section} {title} {text}".lower()

        if any(keyword in combined for keyword in [
            "evaluation criteria",
            "evaluation criterion",
            "criterion",
            "criteria",
            "weighted criteria",
            "assessment criteria",
            "response criteria",
        ]):
            evaluation_criteria.append({
                "requirement_id": requirement_id,
                "title": title,
                "section": req.get("section", ""),
                "text": text,
                "category": req.get("category", ""),
            })

    return evaluation_criteria


def plan_proposal_overview(tender_id: str) -> Dict[str, Any]:
    extracted_requirements = load_json_output(tender_id, "extracted_requirements.json")
    evaluation_criteria = _extract_evaluation_criteria(extracted_requirements)

    if not evaluation_criteria:
        result = {
            "proposal_overview_sections": [],
            "covered_elsewhere": [],
            "overall_summary": "No evaluation criteria were found in extracted_requirements.json."
        }

        write_tender_output(
            tender_id,
            "proposal_overview_plan.json",
            json.dumps(result, indent=2)
        )
        return result

    prompt_template = load_prompt("plan_proposal_overview.md")

    criteria_json = json.dumps(evaluation_criteria, indent=2)

    user_prompt = f"""
Tender ID: {tender_id}

Extracted evaluation criteria:
{criteria_json}
""".strip()

    raw_response = chat(
        system_prompt=prompt_template,
        user_prompt=user_prompt,
        model="gpt-4o",
    )

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        result = {
            "proposal_overview_sections": [],
            "covered_elsewhere": [],
            "overall_summary": "The model returned invalid JSON while planning the Proposal Overview.",
            "raw_response": raw_response[:4000]
        }

    if not isinstance(result.get("proposal_overview_sections"), list):
        result["proposal_overview_sections"] = []

    if not isinstance(result.get("covered_elsewhere"), list):
        result["covered_elsewhere"] = []

    if not isinstance(result.get("overall_summary"), str):
        result["overall_summary"] = ""

    write_tender_output(
        tender_id,
        "proposal_overview_plan.json",
        json.dumps(result, indent=2)
    )

    return result