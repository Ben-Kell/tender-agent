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
from app.rag_retriever import retrieve_relevant_chunks
from app.requirement_extractor import extract_and_deduplicate_requirements
from app.response_router import route_requirements_for_main_response
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

        requirements = extract_and_deduplicate_requirements(tender_id, documents)
        print(f"[start_run] extracted {len(requirements)} deduplicated requirements")

        if not requirements:
            raise RuntimeError(
                f"Requirement extraction returned zero requirements for {tender_id}. "
                f"Check tenders/{tender_id}/output/requirement_extraction_diagnostics.json "
                f"and tenders/{tender_id}/output/raw_extracted_requirements.json."
            )

        RUNS[run_id]["current_step"] = "detecting_pricing_model"
        pricing_model_result = detect_pricing_model(tender_id)
        print(f"[start_run] pricing model detection result: {pricing_model_result}")

        response_routing = route_requirements_for_main_response(tender_id, requirements)

        parsed = {
            "metadata": metadata,
            "requirements": requirements,
            "pricing_model_detection": pricing_model_result,
            "response_routing": response_routing,
        }

        output_path = write_tender_output(
            tender_id,
            "extracted_requirements.json",
            parsed,
        )
        write_tender_output(
            tender_id,
            "response_routing.json",
            response_routing,
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

    retrieved_chunks = retrieve_relevant_chunks(
        section=section,
        matched_requirements=matched_requirements,
        tender_metadata=tender_metadata,
        index_path="knowledge_library/index.json",
        top_k=6,
    )


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

MATCHED REQUIREMENTS: {json.dumps(matched_requirements, indent=2)}
RETRIEVED KNOWLEDGE CHUNKS: {json.dumps(retrieved_chunks, indent=2)}
OPTIONAL BOILERPLATE: {json.dumps(boilerplate_docs, indent=2)}
OPTIONAL CASE STUDIES: {json.dumps(case_study_docs, indent=2)}

Return raw JSON only in this structure:
{{
  "section_id": "{section.get('section_id', '')}",
  "template_section": "{section_name}",
  "draft_text": "Draft response text here",
  "requirements_covered": ["REQ-001", "REQ-004"],
  "used_boilerplate": ["file1.md"],
  "used_case_studies": ["case1.md"],
  "used_rag_chunks": ["chunk_123", "chunk_456"],
  "used_rag_sources": ["service_transition_standard.md", "nds_case_study.md"],
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
        draft_text = str(parsed.get("draft_text", "")).strip()

        if draft_text.startswith("{") and '"coverage_status"' in draft_text:
            raise RuntimeError(
            f"Drafted section '{section_name}' returned compliance JSON instead of narrative text"
            )

        if draft_text.startswith("{") and '"requirement_id"' in draft_text:
            raise RuntimeError(
            f"Drafted section '{section_name}' returned raw JSON instead of narrative text"
            )
        return parsed
    except json.JSONDecodeError:
        return {
            "section_id": section.get("section_id", ""),
            "template_section": section_name,
            "draft_text": "",
            "requirements_covered": [],
            "used_boilerplate": [],
            "used_case_studies": [],
            "used_rag_chunks": [],
            "used_rag_sources": [],
            "headings_added": [],
            "error": "Failed to parse model output as JSON",
            "raw_output": raw_output,
        }
def _draft_main_response_section(
    tender_id: str,
    tender_metadata: dict,
    section_title: str,
    main_response_requirements: list[dict],
    requirements: list[dict],
    boilerplate_docs: list,
    case_study_docs: list,
) -> dict:
    system_prompt = load_prompt("system_instructions.md")
    draft_prompt = load_prompt("draft_sections.md")

    routed_ids = [item.get("requirement_id") for item in main_response_requirements]
    matched_requirements = [
        req for req in requirements if req.get("requirement_id") in routed_ids
    ]

    response_focuses = [
        item.get("response_focus", "").strip()
        for item in main_response_requirements
        if item.get("response_focus")
    ]

    retrieved_chunks = retrieve_relevant_chunks(
        section={
            "template_section": section_title,
            "section_purpose": "Explain Fujitsu's understanding of the customer's need and describe the proposed methodology, approach, delivery model, governance, transition, and relevant solution response.",
            "response_guidance": "Prioritise methodology, understanding, proposal response, delivery approach, governance, transition, and security content over generic corporate boilerplate.",
            "response_focuses": response_focuses,
        },
        matched_requirements=matched_requirements,
        tender_metadata=tender_metadata,
        index_path="knowledge_library/index.json",
        top_k=4,
    )

    # Keep only the fields the model actually needs
    compact_requirements = []
    for req in matched_requirements[:12]:
        compact_requirements.append({
            "requirement_id": req.get("requirement_id", ""),
            "requirement_text": req.get("requirement_text", ""),
            "source_document": req.get("source_document", ""),
            "category": req.get("category", ""),
        })

    compact_routing = []
    for item in main_response_requirements[:12]:
        compact_routing.append({
            "requirement_id": item.get("requirement_id", ""),
            "reason": item.get("reason", ""),
            "response_focus": item.get("response_focus", ""),
        })

    compact_chunks = []
    for chunk in retrieved_chunks[:4]:
        compact_chunks.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "source_file": chunk.get("source_file", ""),
            "category": chunk.get("category", ""),
            "score": round(float(chunk.get("score", 0.0)), 4),
            "text": chunk.get("text", "")[:1800],
        })

    compact_metadata = {
        "tender_reference": tender_metadata.get("tender_reference", ""),
        "tender_title": tender_metadata.get("tender_title", ""),
        "customer": tender_metadata.get("customer", ""),
    }

    user_prompt = f"""
TASK: {draft_prompt}

Draft a single main-response section for the Fujitsu response document.

Rules:
- This section will appear immediately after the Executive Summary
- The heading must be exactly: {section_title}
- This section must NOT read like another Executive Summary
- Do NOT restate high-level summary language unless needed briefly as context
- This section must show:
  1. Fujitsu's understanding of the customer's requirement and intent
  2. Fujitsu's proposed methodology / approach / delivery response
  3. How the response addresses the routed requirements
- Prioritise concrete tender-response substance over generic company description
- Use the retrieved knowledge chunks as the primary source of reusable Fujitsu content
- Prefer methodology, governance, transition, security, delivery model, and proposal-response material over generic corporate boilerplate
- Do not include pricing schedules, rate cards, returnable-form content, supplier background forms, or past performance tables unless clearly needed as short narrative references
- Write in polished tender prose in Australian English
- Do not include an Executive Summary
- Do not include any other top-level section headings
- Do not reproduce raw JSON, chunk IDs, or internal labels

TENDER ID: {tender_id}

TENDER METADATA:
{json.dumps(compact_metadata, indent=2)}

ROUTED MAIN RESPONSE REQUIREMENTS:
{json.dumps(compact_routing, indent=2)}

MATCHED REQUIREMENT DETAILS:
{json.dumps(compact_requirements, indent=2)}

RETRIEVED KNOWLEDGE CHUNKS:
{json.dumps(compact_chunks, indent=2)}

Return raw JSON only in this structure:
{{
  "section_id": "SEC-MAIN-001",
  "template_section": "{section_title}",
  "draft_text": "Draft response text here",
  "requirements_covered": ["REQ-001", "REQ-004"],
  "used_boilerplate": [],
  "used_case_studies": [],
  "used_rag_chunks": ["chunk_123", "chunk_456"],
  "used_rag_sources": ["service_transition_standard.md", "proposal_methodology.md"],
  "headings_added": []
}}
""".strip()
    
    print("[draft_main_response_section] matched_requirements:", len(compact_requirements))
    print("[draft_main_response_section] retrieved_chunks:", len(compact_chunks))
    print("[draft_main_response_section] prompt_chars:", len(user_prompt))

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
            "section_id": "SEC-MAIN-001",
            "template_section": section_title,
            "draft_text": "",
            "requirements_covered": [],
            "used_boilerplate": [],
            "used_case_studies": [],
            "used_rag_chunks": [],
            "used_rag_sources": [],
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

    try:
        tender_id = config["tender_id"]

        extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
        requirements = extracted.get("requirements", [])
        tender_metadata = extracted.get("metadata", {})
        response_routing = extracted.get("response_routing", {})

        section_title = response_routing.get(
            "main_response_section_title",
            "Our Understanding and Response",
        )
        main_response_requirements = response_routing.get(
            "main_response_requirements",
            []
        )

        boilerplate_docs = load_boilerplate_docs()
        case_study_docs = load_case_studies()

        RUNS[run_id]["current_step"] = "drafting_main_response_section"

        drafted_section = _draft_main_response_section(
            tender_id=tender_id,
            tender_metadata=tender_metadata,
            section_title=section_title,
            main_response_requirements=main_response_requirements,
            requirements=requirements,
            boilerplate_docs=boilerplate_docs,
            case_study_docs=case_study_docs,
        )

        parsed = {"sections": [drafted_section]}
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

        extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
        tender_metadata = extracted.get("metadata", {})
        response_routing = extracted.get("response_routing", {})

        past_performance_requirement = load_tender_output_json(
            tender_id, "past_performance_requirement.json"
        )

        section_drafts = load_tender_output_json(tender_id, "section_drafts.json")
        drafted_sections = section_drafts.get("sections", [])

        if not drafted_sections:
            raise RuntimeError("No drafted main response section found in section_drafts.json")

        main_section = drafted_sections[0]
        main_section_title = main_section.get(
            "template_section",
            response_routing.get("main_response_section_title", "Our Understanding and Response")
        ).strip()

        main_section_text = str(main_section.get("draft_text", "")).strip()

        if not main_section_text:
            raise RuntimeError("Main response section draft is empty")

        RUNS[run_id]["current_step"] = "building_two_section_markdown"

        base_markdown = (
            "## 1. Executive Summary\n\n"
            f"## 2. {main_section_title}\n\n"
            f"{main_section_text}\n"
        ).strip()

        RUNS[run_id]["current_step"] = "generating_executive_summary"

        summary_source_markdown = remove_existing_executive_summary(base_markdown)
        executive_summary_text = generate_executive_summary(summary_source_markdown).strip()

        if not executive_summary_text:
            raise RuntimeError("Executive Summary generation returned empty text")

        final_markdown = inject_executive_summary(base_markdown, executive_summary_text)

        if ("## 1. Executive Summary" not in final_markdown) and ("## Executive Summary" not in final_markdown):
            raise RuntimeError("Executive Summary missing from final markdown")

        if '"compliance"' in final_markdown or '"coverage_status"' in final_markdown:
            raise RuntimeError(
                "Final markdown contains compliance JSON or machine-readable artefacts."
            )

        write_markdown_output(tender_id, "final_response_draft.md", final_markdown)

        payload = build_docx_payload(
            tender_id=tender_id,
            markdown_text=final_markdown,
            mapping_path="templates/fujitsu_response_template.mapping.json"
        )

        if not payload.get("executive_summary", "").strip():
            raise RuntimeError("Executive Summary missing from docx_payload.json before DOCX render")

        if not payload.get("main_response_section", "").strip():
            raise RuntimeError("Main response section missing from docx_payload.json before DOCX render")

        payload_file = write_docx_payload(tender_id, payload)

        RUNS[run_id]["current_step"] = "rendering_docx"

        main_docx_output_file = render_docx_with_node(
            tender_id=tender_id,
            template_path="templates/fujitsu_response_template.docx",
            payload_path=payload_file,
            output_path=f"tenders/{tender_id}/output/final_response.docx"
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

        '''  RUNS[run_id]["current_step"] = "planning_proposal_overview"
        proposal_overview_plan_result = plan_proposal_overview(tender_id)

        print("PROPOSAL OVERVIEW PLAN BUILT")
        print(proposal_overview_plan_result)
'''
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
            #"proposal_overview_plan": proposal_overview_plan_result,
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

