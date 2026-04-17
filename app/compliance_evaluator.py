from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from app.json_loader import load_tender_output_json
from app.output_writer import write_tender_output
from app.prompt_loader import load_prompt
from app.openai_client import chat


BATCH_SIZE = 10


def _clean_model_json(raw: str) -> str:
    cleaned = raw.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def _load_final_markdown(tender_id: str) -> str:
    path = Path("tenders") / tender_id / "output" / "final_response_draft.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _batch_requirements(requirements: List[Dict[str, Any]], batch_size: int) -> List[List[Dict[str, Any]]]:
    return [requirements[i:i + batch_size] for i in range(0, len(requirements), batch_size)]


def _normalise_compliance_row(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "requirement_id": str(row.get("requirement_id", "")).strip(),
        "coverage_status": str(row.get("coverage_status", "NONE")).strip().upper(),
        "covered_in_section": str(row.get("covered_in_section", "")).strip(),
        "confidence": str(row.get("confidence", "low")).strip().lower(),
        "gap": str(row.get("gap", "")).strip(),
    }


def _fallback_rows_for_batch(batch: List[Dict[str, Any]], reason: str) -> List[Dict[str, Any]]:
    rows = []
    for req in batch:
        rows.append({
            "requirement_id": str(req.get("requirement_id", "")).strip(),
            "coverage_status": "NONE",
            "covered_in_section": "",
            "confidence": "low",
            "gap": f"Compliance evaluation fallback used: {reason}",
        })
    return rows


def _evaluate_batch(tender_id: str, batch: List[Dict[str, Any]], final_markdown: str) -> List[Dict[str, Any]]:
    system_prompt = load_prompt("evaluate_compliance.md")

    user_prompt = f"""
TENDER ID: {tender_id}

REQUIREMENT BATCH:
{json.dumps(batch, indent=2)}

FINAL RESPONSE MARKDOWN:
{final_markdown}

Return raw JSON only.
Do not use markdown.
Do not use triple backticks.
""".strip()

    raw = chat(system_prompt, user_prompt, model="gpt-4o")
    cleaned = _clean_model_json(raw)

    try:
        parsed = json.loads(cleaned)
    except Exception:
        return _fallback_rows_for_batch(batch, "invalid JSON returned by model")

    compliance = parsed.get("compliance", [])
    if not isinstance(compliance, list):
        return _fallback_rows_for_batch(batch, "model returned non-list compliance")

    normalised_rows = []
    for row in compliance:
        if isinstance(row, dict):
            normalised_rows.append(_normalise_compliance_row(row))

    batch_requirement_ids = {
        str(req.get("requirement_id", "")).strip()
        for req in batch
    }

    returned_requirement_ids = {
        row["requirement_id"]
        for row in normalised_rows
        if row["requirement_id"]
    }

    # Enforce one row per requirement in this batch
    if batch_requirement_ids != returned_requirement_ids:
        return _fallback_rows_for_batch(batch, "model omitted or altered requirement IDs")

    # Keep batch order stable
    by_id = {row["requirement_id"]: row for row in normalised_rows}
    ordered_rows = [by_id[str(req.get("requirement_id", "")).strip()] for req in batch]

    return ordered_rows


def evaluate_compliance(tender_id: str) -> Dict[str, Any]:
    extracted = load_tender_output_json(tender_id, "extracted_requirements.json")
    requirements = extracted.get("requirements", [])

    if not isinstance(requirements, list):
        requirements = []

    final_markdown = _load_final_markdown(tender_id)

    if not requirements:
        result = {
            "compliance": [],
            "summary": {
                "requirement_count": 0,
                "full_count": 0,
                "partial_count": 0,
                "none_count": 0,
            },
            "error": "No requirements found in extracted_requirements.json",
        }
        write_tender_output(tender_id, "compliance_matrix.json", result)
        return result

    if not final_markdown.strip():
        fallback = _fallback_rows_for_batch(requirements, "final_response_draft.md not found or empty")
        result = {
            "compliance": fallback,
            "summary": {
                "requirement_count": len(fallback),
                "full_count": 0,
                "partial_count": 0,
                "none_count": len(fallback),
            },
            "error": "final_response_draft.md not found or empty",
        }
        write_tender_output(tender_id, "compliance_matrix.json", result)
        return result

    all_rows: List[Dict[str, Any]] = []
    for batch in _batch_requirements(requirements, BATCH_SIZE):
        all_rows.extend(_evaluate_batch(tender_id, batch, final_markdown))

    full_count = sum(1 for r in all_rows if r["coverage_status"] == "FULL")
    partial_count = sum(1 for r in all_rows if r["coverage_status"] == "PARTIAL")
    none_count = sum(1 for r in all_rows if r["coverage_status"] == "NONE")

    result = {
        "compliance": all_rows,
        "summary": {
            "requirement_count": len(all_rows),
            "full_count": full_count,
            "partial_count": partial_count,
            "none_count": none_count,
        }
    }

    write_tender_output(tender_id, "compliance_matrix.json", result)
    return result