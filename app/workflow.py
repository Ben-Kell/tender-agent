import json
import uuid


from app.storage import RUNS
from app.compliance_evaluator import evaluate_compliance
from app.content_loader import load_boilerplate_docs, load_case_studies
from app.docx_bridge import render_docx_with_node
from app.docx_payload_builder import build_docx_payload, write_docx_payload
from app.file_loader import load_normalised_tender_docs
from app.json_loader import load_tender_output_json
from app.json_loader import load_proposal_overview_plan
from app.markdown_writer import write_markdown_output
from app.openai_client import chat
from app.output_writer import write_tender_output
from app.pricing_model_detector import detect_pricing_model
from app.prompt_loader import load_prompt
from app.proposal_overview_planner import plan_proposal_overview
from app.requirement_extractor import extract_and_deduplicate_requirements
from app.returnable_detector import detect_returnable_documents
from app.submission_artefacts import build_submission_artefacts
from app.template_loader import load_template
from app.template_utils import fill_template_placeholders
from app.tender_bootstrap import create_tender_structure
from app.tender_ingest import create_and_ingest_tender
from app.tm_pricing_csv import generate_tm_pricing_csv

from app.executive_summary import (
    generate_executive_summary,
    inject_executive_summary,
    remove_existing_executive_summary,
)
from app.proposal_overview import (
    build_proposal_overview_scaffold,
    remove_existing_proposal_overview,
    inject_proposal_overview,
)

from app.supplier_background import (
    detect_supplier_background_requirement,
    copy_supplier_background_template_if_required,
    detect_past_performance_requirement,
)

def _extract_metadata_from_docs(docs: list[dict]) -> dict:
    """
    Lightweight metadata extractor to avoid sending the full tender.
    Uses only the first 4000 characters of each document.
    """
    system_prompt = load_prompt("system_instructions.md")

    combined_preview = "\n\n".join(
        f"# DOCUMENT: {doc['filename']}\n{doc['content'][:4000]}"
        for doc in docs
    )

    user_prompt = f"""
Extract tender metadata from these tender document previews.

Return raw JSON only.
Do not use markdown.
Do not use triple backticks.
Do not add explanatory text.

Return exactly this structure:
{{
  "tender_reference": "",
  "tender_title": "",
  "customer": "",
  "submission_date": ""
}}

DOCUMENT PREVIEWS:
{combined_preview}
""".strip()

    raw_output = chat(system_prompt, user_prompt, model="gpt-4o")
    cleaned_output = raw_output.strip()

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output[len("```json"):].strip()
    elif cleaned_output.startswith("```"):
        cleaned_output = cleaned_output[len("```"):].strip()

    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output[:-3].strip()

    try:
        parsed = json.loads(cleaned_output)
        return {
            "tender_reference": str(parsed.get("tender_reference", "")).strip(),
            "tender_title": str(parsed.get("tender_title", "")).strip(),
            "customer": str(parsed.get("customer", "")).strip(),
            "submission_date": str(parsed.get("submission_date", "")).strip(),
        }
    except Exception:
        return {
            "tender_reference": "",
            "tender_title": "",
            "customer": "",
            "submission_date": "",
        }

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

        RUNS[run_id]["current_step"] = "extracting_metadata"
        metadata = _extract_metadata_from_docs(docs)

        def clean_value(value):
            return value.strip() if isinstance(value, str) else ""

        metadata = {
            "tender_reference": clean_value(metadata.get("tender_reference", "")),
            "tender_title": clean_value(metadata.get("tender_title", "")),
            "customer": clean_value(metadata.get("customer", "")),
            "submission_date": clean_value(metadata.get("submission_date", "")),
        }

        print(f"[start_run] extracted metadata: {metadata}")

        RUNS[run_id]["current_step"] = "extracting_requirements"

        documents = [
            {
                "name": doc["filename"],
                "content": doc["content"],
            }
            for doc in docs
        ]

        requirements = extract_and_deduplicate_requirements(documents)
        print(f"[start_run] extracted {len(requirements)} deduplicated requirements")

        RUNS[run_id]["current_step"] = "detecting_pricing_model"
        pricing_model_result = detect_pricing_model(tender_id)
        print(f"[start_run] pricing model detection result: {pricing_model_result}")

        parsed = {
            "metadata": metadata,
            "requirements": requirements,
            "pricing_model_detection": pricing_model_result,
        }

        output_path = write_tender_output(
            tender_id,
            "extracted_requirements.json",
            parsed,
        )
        print(f"[start_run] wrote output to {output_path}")

        supplier_background_detection = detect_supplier_background_requirement(parsed)

        supplier_background_copy_result = copy_supplier_background_template_if_required(
            tender_id=tender_id,
            detection_result=supplier_background_detection,
        )

        write_tender_output(
            tender_id,
            "supplier_background_requirement.json",
            supplier_background_detection,
        )

        past_performance_detection = detect_past_performance_requirement(parsed)

        write_tender_output(
            tender_id,
            "past_performance_requirement.json",
            past_performance_detection,
        )

        RUNS[run_id]["result"] = {
            "message": "Requirements extracted successfully",
            "output_file": output_path,
            "metadata": metadata,
            "requirement_count": len(requirements),
            "pricing_model_detection": pricing_model_result,
            "pricing_model_detection_file": f"tenders/{tender_id}/output/pricing_model_detection.json",
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
def _draft_single_section(
    tender_id: str,
    template_text: str,
    tender_metadata: dict,
    section: dict,
    requirements: list,
    boilerplate_docs: list,
    case_study_docs: list,
) -> dict:
    system_prompt = load_prompt("system_instructions.md")
    draft_prompt = load_prompt("draft_sections.md")

    section_name = section.get("template_section", "").strip()
    matched_requirement_ids = section.get("matched_requirements", [])

    matched_requirements = [
        req for req in requirements
        if req.get("requirement_id") in matched_requirement_ids
    ]

    user_prompt = f"""
TASK:
{draft_prompt}

TENDER ID:
{tender_id}

SECTION TO DRAFT:
{json.dumps(section, indent=2)}

RESPONSE TEMPLATE:
{template_text}

TENDER METADATA:
{json.dumps(tender_metadata, indent=2)}

MATCHED REQUIREMENTS:
{json.dumps(matched_requirements, indent=2)}

BOILERPLATE:
{json.dumps(boilerplate_docs, indent=2)}

CASE STUDIES:
{json.dumps(case_study_docs, indent=2)}

Return raw JSON only in this structure:
{{
  "section_id": "{section.get('section_id', '')}",
  "template_section": "{section_name}",
  "draft_text": "Draft response text here",
  "requirements_covered": ["REQ-001", "REQ-004"],
  "used_boilerplate": ["file1.md"],
  "used_case_studies": ["case1.md"],
  "headings_added": ["Optional heading"]
}}

Do not include an Executive Summary section.
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
        return parsed
    except json.JSONDecodeError:
        return {
            "section_id": section.get("section_id", ""),
            "template_section": section_name,
            "draft_text": "",
            "requirements_covered": [],
            "used_boilerplate": [],
            "used_case_studies": [],
            "headings_added": [],
            "error": "Failed to parse model output as JSON",
            "raw_output": raw_output,
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

        RUNS[run_id]["current_step"] = "drafting_sections"

        drafted_sections = []

        for index, section in enumerate(filtered_mapped_sections, start=1):
            section_name = section.get("template_section", f"Section {index}")
            print(f"[draft_sections] Drafting {index}/{len(filtered_mapped_sections)}: {section_name}")

            drafted_section = _draft_single_section(
                tender_id=tender_id,
                template_text=template_text,
                tender_metadata=tender_metadata,
                section=section,
                requirements=requirements,
                boilerplate_docs=boilerplate_docs,
                case_study_docs=case_study_docs,
            )

            if drafted_section.get("template_section", "").strip() not in SKIP_AUTO_DRAFT_SECTIONS:
                drafted_sections.append(drafted_section)

        parsed = {"sections": drafted_sections}

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

        #proposal_overview_plan = load_proposal_overview_plan(tender_id)   

        template_text = fill_template_placeholders(template_text, tender_metadata)

        section_drafts = load_tender_output_json(tender_id, "section_drafts.json")
        drafted_sections = section_drafts.get("sections", [])
        proposal_overview_plan = load_proposal_overview_plan(tender_id)

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
        
        proposal_overview_sections = proposal_overview_plan.get("proposal_overview_sections", [])

        proposal_overview_headings = []
        proposal_overview_headings_markdown_lines = []

        for section in proposal_overview_sections:
            heading = (section.get("heading") or "").strip()
            if not heading:
                continue

            proposal_overview_headings.append({"heading": heading})
            proposal_overview_headings_markdown_lines.append(f"## {heading}")

        proposal_overview_headings_markdown = "\n".join(proposal_overview_headings_markdown_lines)

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

        summary_source_markdown = remove_existing_executive_summary(final_markdown)
        executive_summary_text = generate_executive_summary(summary_source_markdown)
        final_markdown = inject_executive_summary(final_markdown, executive_summary_text)

        RUNS[run_id]["current_step"] = "building_proposal_overview"

        final_markdown = remove_existing_proposal_overview(final_markdown)

        proposal_overview_text = build_proposal_overview_scaffold(proposal_overview_plan)

        final_markdown = inject_proposal_overview(final_markdown, proposal_overview_text)

        write_markdown_output(tender_id, "final_response_draft.md", final_markdown)

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

        RUNS[run_id]["current_step"] = "building_submission_artefacts"
        submission_artefact_result = build_submission_artefacts(tender_id)

        print("SUBMISSION ARTEFACTS BUILT")
        print(submission_artefact_result)

        checklist_path = submission_artefact_result.get("submission_checklist_md_path")
        if not checklist_path:
            raise RuntimeError("submission_checklist_md_path missing from submission artefact result")

        RUNS[run_id]["result"] = {
            "message": "Final response draft and DOCX files compiled successfully",
            "markdown_output_file": f"tenders/{tender_id}/output/final_response_draft.md",
            "payload_file": f"tenders/{tender_id}/output/docx_payload.json",
            "main_docx_output_file": main_docx_output_file,
            "aic_docx_output_file": aic_docx_output_file,
            "past_performance_docx_output_file": past_performance_docx_output_file,
            "submission_artefacts_json": submission_artefact_result["submission_artefacts"],
            "submission_readiness": submission_artefact_result["submission_readiness"],
            "submission_checklist_markdown": submission_artefact_result["submission_checklist_markdown"],
            "submission_artefacts_json_path": submission_artefact_result["submission_artefacts_json_path"],
            "submission_checklist_md_path": submission_artefact_result["submission_checklist_md_path"],
            "proposal_overview_plan_summary": proposal_overview_plan.get("overall_summary", ""),
            "proposal_overview_headings": proposal_overview_headings,
            "proposal_overview_headings_markdown": proposal_overview_headings_markdown,
            "proposal_overview_sections_json": json.dumps(proposal_overview_sections, indent=2),
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

def _assert_stage_completed(stage_name: str, stage_result: dict) -> None:
    if not isinstance(stage_result, dict):
        raise RuntimeError(f"{stage_name} returned a non-dict response")

    if stage_result.get("status") != "completed":
        raise RuntimeError(f"{stage_name} failed: {stage_result.get('result')}")

def run_full_pipeline(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"

    RUNS[run_id] = {
        "status": "running",
        "current_step": "starting_full_pipeline",
        "config": config,
        "result": None,
    }

    try:
        tender_id = config["tender_id"]
        template_name = config.get("template_name", "response_template.md")

        RUNS[run_id]["current_step"] = "running_create_tender"
        create_result = create_and_ingest_tender(tender_id)

        RUNS[run_id]["current_step"] = "running_detect_returnable_documents"
        returnable_result = detect_returnable_documents(tender_id)

        stage_config = {
            "tender_id": tender_id,
            "template_name": template_name,
        }

        RUNS[run_id]["current_step"] = "running_start_run"
        start_result = start_run(stage_config)
        _assert_stage_completed("start_run", start_result)

        RUNS[run_id]["current_step"] = "running_tm_pricing_csv"
        tm_pricing_result = generate_tm_pricing_csv(tender_id)

        RUNS[run_id]["current_step"] = "running_map_template"
        map_result = map_template(stage_config)
        _assert_stage_completed("map_template", map_result)

        RUNS[run_id]["current_step"] = "planning_proposal_overview"
        proposal_overview_plan_result = plan_proposal_overview(tender_id)

        print("PROPOSAL OVERVIEW PLAN BUILT")
        print(proposal_overview_plan_result)

        RUNS[run_id]["current_step"] = "running_draft_sections"
        draft_result = draft_sections(stage_config)
        _assert_stage_completed("draft_sections", draft_result)

        RUNS[run_id]["current_step"] = "running_compile_response"
        compile_result = compile_response(stage_config)
        _assert_stage_completed("compile_response", compile_result)

        RUNS[run_id]["current_step"] = "evaluating_compliance"
        compliance_result = evaluate_compliance(tender_id)

        RUNS[run_id]["result"] = {
            "message": "Full tender pipeline completed successfully",
            "tender_id": tender_id,
            "create_tender": create_result,
            "detect_returnable_documents": returnable_result,
            "start_run": start_result["result"],
            #"early_submission_artefacts": early_submission_artefact_result,
            "proposal_overview_plan": proposal_overview_plan_result,
            "map_template": map_result["result"],
            "draft_sections": draft_result["result"],
            "compile_response": compile_result["result"],
            "pricing_model_detection": start_result["result"].get("pricing_model_detection"),
            "tm_pricing_csv": tm_pricing_result,
            "compliance_matrix": compliance_result,
        }
        RUNS[run_id]["status"] = "completed"
        RUNS[run_id]["current_step"] = "done"

    except Exception as e:
        import traceback
        traceback.print_exc()
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["current_step"] = "failed"
        RUNS[run_id]["result"] = {"error": str(e)}

    return {
        "run_id": run_id,
        "status": RUNS[run_id]["status"],
        "current_step": RUNS[run_id]["current_step"],
        "result": RUNS[run_id]["result"],
    }

