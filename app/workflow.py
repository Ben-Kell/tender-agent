import json
import uuid

from app.storage import RUNS
from app.file_loader import load_normalised_tender_docs
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat

from app.template_loader import load_template
from app.json_loader import load_tender_output_json
from app.submission_artefacts import build_submission_artefacts
from app.content_loader import load_boilerplate_docs, load_case_studies
from app.markdown_writer import write_markdown_output
from app.template_utils import fill_template_placeholders

from app.tender_bootstrap import create_tender_structure

from app.docx_payload_builder import build_docx_payload, write_docx_payload
from app.docx_bridge import render_docx_with_node
from app.executive_summary import (
    generate_executive_summary,
    inject_executive_summary,
    remove_existing_executive_summary,
)
from app.supplier_background import (
    detect_supplier_background_requirement,
    copy_supplier_background_template_if_required,
    detect_past_performance_requirement,
)

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
        print(f"[start_run] tender_id={tender_id}")

        create_tender_structure(tender_id)

        docs = load_normalised_tender_docs(tender_id)
        print(f"[start_run] loaded {len(docs)} normalised docs")

        system_prompt = load_prompt("system_instructions.md")
        extract_prompt = load_prompt("extract_requirements.md")
        print("[start_run] prompts loaded")

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
  "metadata": {{
    "tender_reference": "RFQ 47137",
    "tender_title": "JP2181 and NMP2106 ICT Resources",
    "customer": "Department of Defence",
    "submission_date": "08/11/2024"
  }},
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

        print("[start_run] calling OpenAI")
        raw_output = chat(system_prompt, user_prompt)
        print("[start_run] OpenAI call complete")

        cleaned_output = raw_output.strip()

        if cleaned_output.startswith("```json"):
            cleaned_output = cleaned_output[len("```json"):].strip()
        elif cleaned_output.startswith("```"):
            cleaned_output = cleaned_output[len("```"):].strip()

        if cleaned_output.endswith("```"):
            cleaned_output = cleaned_output[:-3].strip()

        try:
            parsed = json.loads(cleaned_output)
            print("[start_run] JSON parsed successfully")
        except json.JSONDecodeError as e:
            print(f"[start_run] JSON parse failed: {e}")
            parsed = {
                "metadata": {
                    "tender_reference": "",
                    "tender_title": "",
                    "customer": "",
                    "submission_date": "",
                },
                "requirements": [],
                "error": "Failed to parse model output as JSON",
                "raw_output": raw_output,
            }

        metadata = parsed.get("metadata", {}) or {}

        def clean_value(value):
            return value.strip() if isinstance(value, str) else ""

        metadata = {
            "tender_reference": clean_value(metadata.get("tender_reference", "")),
            "tender_title": clean_value(metadata.get("tender_title", "")),
            "customer": clean_value(metadata.get("customer", "")),
            "submission_date": clean_value(metadata.get("submission_date", "")),
        }

        parsed["metadata"] = metadata

        output_path = write_tender_output(tender_id, "extracted_requirements.json", parsed)
        print(f"[start_run] wrote output to {output_path}")

                # 🔍 Detect if supplier background / company overview is required
        supplier_background_detection = detect_supplier_background_requirement(parsed)

        # 📄 Copy template into output folder if required
        supplier_background_copy_result = copy_supplier_background_template_if_required(
            tender_id=tender_id,
            detection_result=supplier_background_detection,
        )

        # 💾 Save detection result for traceability
        write_tender_output(
            tender_id,
            "supplier_background_requirement.json",
            supplier_background_detection
        )

        # 🔍 Detect if past performance / relevant experience is required
        past_performance_detection = detect_past_performance_requirement(parsed)

        # 💾 Save detection result for traceability
        write_tender_output(
            tender_id,
            "past_performance_requirement.json",
            past_performance_detection
        )


        RUNS[run_id]["result"] = {
            "message": "Requirements extracted successfully",
            "output_file": output_path,
            "metadata": metadata,
            "requirement_count": len(parsed.get("requirements", [])),
            "supplier_background_requirement": supplier_background_detection,
            "supplier_background_copy_result": supplier_background_copy_result,
            "past_performance_requirement": past_performance_detection,
        }
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        print(f"[start_run] FAILED: {e}")
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {
        "run_id": run_id,
        "status": RUNS[run_id]["status"],
        "current_step": RUNS[run_id]["current_step"],
        "result": RUNS[run_id]["result"],
    }

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

    return {
        "run_id": run_id,
        "status": RUNS[run_id]["status"],
        "current_step": RUNS[run_id]["current_step"],
        "result": RUNS[run_id]["result"],
    }

def draft_sections(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {
        "status": "running",
        "current_step": "loading_inputs_for_drafting",
        "config": config,
        "result": None,
    }

    SKIP_AUTO_DRAFT_SECTIONS = {
        "Executive Summary",
        "1. Executive Summary",
    }

    try:
        tender_id = config["tender_id"]
        template_name = config.get("template_name", "response_template.md")

        extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
        template_map = load_tender_output_json(tender_id, "template_map.json")

        requirements = extracted.get("requirements", [])
        mapped_sections = template_map.get("sections", [])

        filtered_mapped_sections = []
        for section in mapped_sections:
            section_name = section.get("template_section", "").strip()
            if section_name in SKIP_AUTO_DRAFT_SECTIONS:
                continue
            filtered_mapped_sections.append(section)

        template_text = load_template(template_name)

        tender_metadata = extracted.get("metadata", {})
        template_text = fill_template_placeholders(template_text, tender_metadata)

        boilerplate_docs = load_boilerplate_docs()
        case_study_docs = load_case_studies()
        tender_docs = load_normalised_tender_docs(tender_id)

        system_prompt = load_prompt("system_instructions.md")
        draft_prompt = load_prompt("draft_sections.md")

        RUNS[run_id]["current_step"] = "drafting_sections"

        user_prompt = f"""
TASK:
{draft_prompt}

TENDER ID:
{tender_id}

RESPONSE TEMPLATE:
{template_text}

TENDER DOCUMENTS:
{json.dumps(tender_docs, indent=2)}

EXTRACTED REQUIREMENTS:
{json.dumps(requirements, indent=2)}

TEMPLATE MAP:
{json.dumps(filtered_mapped_sections, indent=2)}

BOILERPLATE:
{json.dumps(boilerplate_docs, indent=2)}

CASE STUDIES:
{json.dumps(case_study_docs, indent=2)}

Return raw JSON only in this structure:
{{
  "sections": [
    {{
      "section_id": "SEC-002",
      "template_section": "Technical Response",
      "draft_text": "Draft response text here",
      "requirements_covered": ["REQ-001", "REQ-004"],
      "used_boilerplate": ["file1.md"],
      "used_case_studies": ["case1.md"],
      "headings_added": ["Optional heading"]
    }}
  ]
}}

Do not include an Executive Summary section.
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

            parsed_sections = parsed.get("sections", [])
            parsed["sections"] = [
                section
                for section in parsed_sections
                if section.get("template_section", "").strip() not in SKIP_AUTO_DRAFT_SECTIONS
            ]

        except json.JSONDecodeError:
            parsed = {
                "sections": [],
                "error": "Failed to parse model output as JSON",
                "raw_output": raw_output,
            }

        write_tender_output(tender_id, "section_drafts.json", parsed)

        RUNS[run_id]["result"] = parsed
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {
        "run_id": run_id,
        "status": RUNS[run_id]["status"],
        "current_step": RUNS[run_id]["current_step"],
        "result": RUNS[run_id]["result"],
    }

def compile_response(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {
        "status": "running",
        "current_step": "loading_response_parts",
        "config": config,
        "result": None,
    }

    try:
        tender_id = config["tender_id"]
        template_name = config.get("template_name", "response_template.md")

        template_text = load_template(template_name)

        extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
        tender_metadata = extracted.get("metadata", {})

        past_performance_requirement = load_tender_output_json(
            tender_id,
            "past_performance_requirement.json"
        )        

        template_text = fill_template_placeholders(template_text, tender_metadata)

        section_drafts = load_tender_output_json(tender_id, "section_drafts.json")
        drafted_sections = section_drafts.get("sections", [])

        system_prompt = load_prompt("system_instructions.md")
        compile_prompt = load_prompt("compile_response.md")

        RUNS[run_id]["current_step"] = "compiling_final_response"

        user_prompt = f"""
TASK: {compile_prompt}

TENDER ID: {tender_id}

RESPONSE TEMPLATE:
{template_text}

SECTION DRAFTS:
{json.dumps(drafted_sections, indent=2)}

Return markdown only.
Do not use triple backticks.
Do not add commentary before or after the document.
"""

        raw_output = chat(system_prompt, user_prompt)
        final_markdown = raw_output.strip()

        if final_markdown.startswith("```markdown"):
            final_markdown = final_markdown[len("```markdown"):].strip()
        elif final_markdown.startswith("```"):
            final_markdown = final_markdown[len("```"):].strip()

        if final_markdown.endswith("```"):
            final_markdown = final_markdown[:-3].strip()

        # Safety pass in case the model reproduced placeholders again
        final_markdown = fill_template_placeholders(final_markdown, tender_metadata)

        RUNS[run_id]["current_step"] = "generating_executive_summary"

        # Remove placeholder / stale executive summary content before summarising
        summary_source_markdown = remove_existing_executive_summary(final_markdown)

        executive_summary_text = generate_executive_summary(summary_source_markdown)

        final_markdown = inject_executive_summary(final_markdown, executive_summary_text)

        write_markdown_output(tender_id, "final_response_draft.md", final_markdown)

        RUNS[run_id]["current_step"] = "building_docx_payload"

        payload = build_docx_payload(
            tender_id=tender_id,
            markdown_text=final_markdown,
            mapping_path="templates/fujitsu_response_template.mapping.json"
        )

        payload_file = write_docx_payload(tender_id, payload)

        RUNS[run_id]["current_step"] = "rendering_docx"

        main_docx_output_file = render_docx_with_node(
            tender_id=tender_id,
            template_path="templates/fujitsu_response_template.docx",
            payload_path=payload_file,
            output_path=f"tenders/{tender_id}/output/proposal_overview.docx"
        )

        aic_docx_output_file = render_docx_with_node(
            tender_id=tender_id,
            template_path="templates/fujitsu_aic_plan_template.docx",
            payload_path=payload_file,
            output_path=f"tenders/{tender_id}/output/fujitsu_aic_plan.docx"
        )

        past_performance_docx_output_file = None

        if past_performance_requirement.get("past_performance_required"):
            past_performance_docx_output_file = render_docx_with_node(
                tender_id=tender_id,
                template_path="templates/fujitsu_past_performance.docx",
                payload_path=payload_file,
                output_path=f"tenders/{tender_id}/output/fujitsu_past_performance.docx"
            )

        submission_artefact_result = build_submission_artefacts(tender_id)

        RUNS[run_id]["result"] = {
            "message": "Final response draft and DOCX files compiled successfully",
            "markdown_output_file": f"tenders/{tender_id}/output/final_response_draft.md",
            "payload_file": f"tenders/{tender_id}/output/docx_payload.json",
            "main_docx_output_file": main_docx_output_file,
            "aic_docx_output_file": aic_docx_output_file,
            "past_performance_docx_output_file": past_performance_docx_output_file,
            "submission_artefacts_json": submission_artefact_result["submission_artefacts"],
            "submission_checklist_markdown": submission_artefact_result["submission_checklist_markdown"],
            "submission_artefacts_json_path": submission_artefact_result["submission_artefacts_json_path"],
            "submission_checklist_md_path": submission_artefact_result["submission_checklist_md_path"],
        }
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        import traceback
        traceback.print_exc()
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {
        "run_id": run_id,
        "status": RUNS[run_id]["status"],
        "current_step": RUNS[run_id]["current_step"],
        "result": RUNS[run_id]["result"],
    }