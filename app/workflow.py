import json
import uuid

from app.storage import RUNS
from app.file_loader import load_normalised_tender_docs
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat

from app.template_loader import load_template
from app.json_loader import load_tender_output_json


def start_run(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {
        "status": "running",
        "current_step": "loading_files",
        "config": config,
        "result": None,
    }

    try:
        tender_id = config["tender_id"]

        docs = load_normalised_tender_docs(tender_id)

        system_prompt = load_prompt("system_instructions.md")
        extract_prompt = load_prompt("extract_requirements.md")

        RUNS[run_id]["current_step"] = "extracting_requirements"

        tender_text_blob = "\n\n".join(
            f"# DOCUMENT: {doc['filename']}\n{doc['content']}"
            for doc in docs
        )

        user_prompt = f"""
You are extracting requirements from tender documents.

TASK:
{extract_prompt}

TENDER ID:
{tender_id}

DOCUMENTS:
{tender_text_blob}

Return raw JSON only.
Do not use markdown.
Do not use triple backticks.
Do not add any explanatory text.

Return JSON only in this structure:
{{
  "requirements": [
    {{
      "requirement_id": "REQ-001",
      "source_document": "filename.md",
      "clause_reference": "1.1",
      "requirement_text": "Full requirement text",
      "requirement_type": "mandatory",
      "theme": "service delivery",
      "response_needed": true
    }}
  ]
}}
"""

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
        except json.JSONDecodeError:
            parsed = {
                "requirements": [],
                "error": "Failed to parse model output as JSON",
                "raw_output": raw_output,
            }

        write_tender_output(tender_id, "extracted_requirements.json", parsed)

        RUNS[run_id]["result"] = parsed
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {"run_id": run_id, "status": "queued"}


def map_template(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {
        "status": "running",
        "current_step": "loading_requirements_and_template",
        "config": config,
        "result": None,
    }

    try:
        tender_id = config["tender_id"]
        template_name = config.get("template_name", "response_template.md")

        extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
        requirements = extracted.get("requirements", [])

        template_text = load_template(template_name)

        system_prompt = load_prompt("system_instructions.md")
        map_prompt = load_prompt("map_requirements_to_template.md")

        RUNS[run_id]["current_step"] = "mapping_requirements_to_template"

        user_prompt = f"""
TASK:
{map_prompt}

TENDER ID:
{tender_id}

RESPONSE TEMPLATE:
{template_text}

EXTRACTED REQUIREMENTS:
{json.dumps(requirements, indent=2)}

Return raw JSON only.
Do not use markdown.
Do not use triple backticks.
Do not add any explanatory text.

Return raw JSON only in this structure:
{{
  "sections": [
    {{
      "section_id": "SEC-001",
      "template_section": "Exact template heading",
      "matched_requirements": ["REQ-001", "REQ-002"],
      "section_purpose": "Why this section exists",
      "response_guidance": "What the writer should cover",
      "headings_to_add": ["Optional heading 1", "Optional heading 2"]
    }}
  ]
}}
"""

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
        except json.JSONDecodeError:
            parsed = {
                "sections": [],
                "error": "Failed to parse model output as JSON",
                "raw_output": raw_output,
            }

        write_tender_output(tender_id, "template_map.json", parsed)

        RUNS[run_id]["result"] = parsed
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {"run_id": run_id, "status": "queued"}