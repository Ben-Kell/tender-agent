import json
from pathlib import Path

from app.file_loader import load_normalised_tender_docs
from app.openai_client import chat
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt


def analyze_returnable_documents(config: dict) -> dict:
    tender_id = config["tender_id"]

    detection_path = Path(f"tenders/{tender_id}/output/returnable_documents.json")
    if not detection_path.exists():
        return {
            "status": "failed",
            "error": "returnable_documents.json not found",
        }

    detection = json.loads(detection_path.read_text(encoding="utf-8"))
    docs = load_normalised_tender_docs(tender_id)

    system_prompt = load_prompt("system_instructions.md")
    analysis_prompt = load_prompt("analyze_returnable_documents.md")

    results = []

    detected_documents = detection.get("documents", [])

    # IMPORTANT:
    # returnable_detector writes:
    # - filename
    # - is_returnable
    # - reasons
    # - confidence (float)
    # - document_type
    detected_by_name = {
        doc.get("filename", ""): doc
        for doc in detected_documents
    }

    for doc in docs:
        file_name = doc.get("filename", "")
        content = doc.get("content", "")

        detected = detected_by_name.get(file_name)
        if not detected:
            continue

        is_returnable = detected.get("is_returnable", False)
        confidence_value = detected.get("confidence", 0.5)
        reasons = detected.get("reasons", [])
        detected_doc_type = detected.get("document_type", "unknown")

        if isinstance(confidence_value, (int, float)):
            if confidence_value >= 0.8:
                confidence = "high"
            elif confidence_value >= 0.5:
                confidence = "medium"
            else:
                confidence = "low"
        else:
            confidence = "medium"

        reason_text = "; ".join(reasons) if reasons else ""

        if is_returnable is False:
            results.append({
                "file_name": file_name,
                "document_type": "reference_only",
                "required_to_return": False,
                "confidence": confidence,
                "reason": reason_text or "Detected as non-returnable",
                "sections": [],
            })
            continue

        content_chunk = content[:8000]

        user_prompt = f"""
TASK:
{analysis_prompt}

TENDER ID:
{tender_id}

DOCUMENT FILE NAME:
{file_name}

PRIOR RETURNABLE DETECTION RESULT:
{json.dumps(detected, indent=2)}

DOCUMENT CONTENT:
{content_chunk}

Return raw JSON only.
Do not use markdown.
Do not use triple backticks.
Do not add explanatory text.

Return exactly this structure:
{{
  "required_to_return": true,
  "confidence": "high|medium|low",
  "reason": "Why this document should or should not be returned",
  "sections": [
    {{
      "section_name": "Name of the section / table / question group",
      "auto_fill_candidate": true,
      "auto_fill_type": "metadata|standard_corporate|template|generated_response|manual_only",
      "suggested_source": "tender_metadata|supplier_profile|standard_methodology_library|manual",
      "reason": "Why this classification was chosen",
      "notes": "Optional implementation notes"
    }}
  ]
}}
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
        except Exception:
            parsed = {
                "required_to_return": True,
                "confidence": confidence,
                "reason": "Failed to parse model output",
                "sections": [],
            }

        results.append({
            "file_name": file_name,
            "document_type": detected_doc_type,
            "required_to_return": parsed.get("required_to_return", True),
            "confidence": parsed.get("confidence", confidence),
            "reason": parsed.get("reason", reason_text),
            "sections": parsed.get("sections", []),
        })

    final = {"documents": results}

    output_path = write_tender_output(
        tender_id,
        "returnable_document_analysis.json",
        final,
    )

    return {
        "status": "completed",
        "output_file": output_path,
        "documents": results,
    }