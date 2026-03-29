import json
import uuid

from app.storage import RUNS
from app.file_loader import load_normalised_tender_docs
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat


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

Return valid JSON only in this structure:
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

        try:
            parsed = json.loads(raw_output)
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