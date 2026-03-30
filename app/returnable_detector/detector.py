# app/returnable_detector/detector.py

import json
from pathlib import Path
from typing import Optional, Callable

from .rules import score_document
from .classifier import classify_document_with_llm
from .models import ReturnableDocumentResult, ReturnableDocumentsReport


def load_original_filename_from_markdown(content: str) -> Optional[str]:
    """
    Looks for a header like:
    # Source: original_filename.pdf
    """
    for line in content.splitlines()[:10]:
        if line.lower().startswith("# source:"):
            return line.split(":", 1)[1].strip()
    return None


def merge_rule_and_llm(rule_result: dict, llm_result: Optional[dict]) -> dict:
    if not llm_result:
        return rule_result

    merged = dict(rule_result)

    merged["is_returnable"] = llm_result.get("is_returnable", rule_result["is_returnable"])
    merged["confidence"] = llm_result.get("confidence", rule_result["confidence"])
    merged["document_type"] = llm_result.get("document_type", rule_result["document_type"])

    llm_reason = llm_result.get("reasoning")
    if llm_reason:
        merged["reasons"] = list(merged.get("reasons", [])) + [f"LLM: {llm_reason}"]

    return merged


def detect_returnable_documents(
    tender_id: str,
    base_dir: str = ".",
    use_llm: bool = False,
    chat_fn: Optional[Callable] = None,
):
    tender_path = Path(base_dir) / "tenders" / tender_id
    normalised_dir = tender_path / "input" / "02_normalised"
    output_dir = tender_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not normalised_dir.exists():
        raise FileNotFoundError(f"Normalised input folder not found: {normalised_dir}")

    documents = []

    for md_file in sorted(normalised_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8", errors="ignore")
        original_filename = load_original_filename_from_markdown(content)

        rule_result = score_document(md_file.name, content)

        llm_result = None
        if use_llm and chat_fn and 3 <= rule_result["score"] <= 8:
            llm_result = classify_document_with_llm(chat_fn, md_file.name, content)

        final = merge_rule_and_llm(rule_result, llm_result)

        documents.append(
            ReturnableDocumentResult(
                filename=md_file.name,
                original_filename=original_filename,
                is_returnable=final["is_returnable"],
                confidence=final["confidence"],
                document_type=final["document_type"],
                reasons=final["reasons"],
                key_signals=final["key_signals"],
                score=final["score"],
            )
        )

    documents_sorted = sorted(
        documents,
        key=lambda d: (d.is_returnable, d.confidence, d.score),
        reverse=True
    )

    report = ReturnableDocumentsReport(
        tender_id=tender_id,
        documents=documents_sorted,
        summary={
            "total_documents": len(documents_sorted),
            "returnable_documents": sum(1 for d in documents_sorted if d.is_returnable),
            "reference_only_documents": sum(1 for d in documents_sorted if not d.is_returnable),
        }
    )

    output_file = output_dir / "returnable_documents.json"
    output_file.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    return report.model_dump()