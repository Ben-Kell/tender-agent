import json
from typing import Dict, Any

from app.file_loader import load_normalised_tender_docs
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat


def detect_pricing_model(tender_id: str) -> Dict[str, Any]:
    """
    Analyse the tender documents and classify the contracting mechanism / pricing model.

    Output categories:
    - staff_augmentation_time_and_materials
    - managed_service_fixed_price
    - mixed_or_unclear
    """

    docs = load_normalised_tender_docs(tender_id)

    combined_text_parts = []

    for doc in docs:
        filename = doc.get("filename", "unknown")
        content = doc.get("content", "")
        if not content:
            continue

        combined_text_parts.append(f"# SOURCE: {filename}\n{content}")

    combined_text = "\n\n".join(combined_text_parts)

    if not combined_text.strip():
        result = {
            "pricing_model": "mixed_or_unclear",
            "confidence": "low",
            "summary": "No normalised tender content was available for pricing model detection.",
            "primary_evidence": [],
            "secondary_indicators": [],
            "reasoning": "The detector could not find any normalised tender text to analyse."
        }

        write_tender_output(
            tender_id,
            "pricing_model_detection.json",
            json.dumps(result, indent=2)
        )
        return result

    prompt_template = load_prompt("detect_pricing_model.md")

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
        result = json.loads(raw_response)
    except json.JSONDecodeError:
        result = {
            "pricing_model": "mixed_or_unclear",
            "confidence": "low",
            "summary": "The model returned an invalid JSON response during pricing model detection.",
            "primary_evidence": [],
            "secondary_indicators": [],
            "reasoning": raw_response[:1000]
        }

    allowed_models = {
        "staff_augmentation_time_and_materials",
        "managed_service_fixed_price",
        "mixed_or_unclear",
    }

    allowed_confidence = {"high", "medium", "low"}

    if result.get("pricing_model") not in allowed_models:
        result["pricing_model"] = "mixed_or_unclear"

    if result.get("confidence") not in allowed_confidence:
        result["confidence"] = "low"

    if not isinstance(result.get("primary_evidence"), list):
        result["primary_evidence"] = []

    if not isinstance(result.get("secondary_indicators"), list):
        result["secondary_indicators"] = []

    if not isinstance(result.get("summary"), str):
        result["summary"] = ""

    if not isinstance(result.get("reasoning"), str):
        result["reasoning"] = ""

    write_tender_output(
        tender_id,
        "pricing_model_detection.json",
        json.dumps(result, indent=2)
    )

    return result