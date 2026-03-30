from pathlib import Path
from typing import Optional

from .models import ReturnableDocumentResult, ReturnableDocumentsReport
from .rules import score_document


def load_original_filename_from_markdown(content: str) -> Optional[str]:
    """
    Looks for a header like:
    # Source: original_filename.pdf
    """
    for line in content.splitlines()[:10]:
        if line.lower().startswith("# source:"):
            return line.split(":", 1)[1].strip()
    return None


def write_markdown_summary(output_dir: Path, report: dict) -> None:
    lines = []
    lines.append(f"# Returnable Documents Report - {report['tender_id']}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total documents: {report['summary']['total_documents']}")
    lines.append(f"- Returnable documents: {report['summary']['returnable_documents']}")
    lines.append(f"- Reference-only documents: {report['summary']['reference_only_documents']}")
    lines.append("")
    lines.append("## Documents")
    lines.append("")

    for doc in report["documents"]:
        lines.append(f"### {doc['filename']}")
        lines.append(f"- Original filename: {doc.get('original_filename')}")
        lines.append(f"- Is returnable: {doc['is_returnable']}")
        lines.append(f"- Confidence: {doc['confidence']}")
        lines.append(f"- Document type: {doc['document_type']}")
        lines.append(f"- Score: {doc['score']}")
        lines.append("- Reasons:")
        for reason in doc["reasons"]:
            lines.append(f"  - {reason}")
        lines.append("")

    (output_dir / "returnable_documents.md").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def detect_returnable_documents(tender_id: str, base_dir: str = ".") -> dict:
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

        scored = score_document(md_file.name, content)

        documents.append(
            ReturnableDocumentResult(
                filename=md_file.name,
                original_filename=original_filename,
                is_returnable=scored["is_returnable"],
                confidence=scored["confidence"],
                document_type=scored["document_type"],
                reasons=scored["reasons"],
                key_signals=scored["key_signals"],
                score=scored["score"],
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

    json_path = output_dir / "returnable_documents.json"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    write_markdown_summary(output_dir, report.model_dump())

    return report.model_dump()