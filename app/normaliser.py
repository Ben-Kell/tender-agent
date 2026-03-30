from pathlib import Path
from typing import Dict, Any, List


SUPPORTED_EXTENSIONS = {
    ".md",
    ".txt",
    ".pdf",
    ".docx",
}


def normalise_filename(source_name: str) -> str:
    source_path = Path(source_name)
    return f"{source_path.stem}.md"


def normalise_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def normalise_markdown_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def placeholder_normalise_pdf(file_path: Path) -> str:
    return f"""# Source: {file_path.name}
# Document Type: pdf
# Normalised For: Tender agent ingestion

[PDF normalisation not yet implemented for this file.]
"""


def placeholder_normalise_docx(file_path: Path) -> str:
    return f"""# Source: {file_path.name}
# Document Type: docx
# Normalised For: Tender agent ingestion

[DOCX normalisation not yet implemented for this file.]
"""


def normalise_one_document(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".txt":
        body = normalise_text_file(file_path)
        return f"""# Source: {file_path.name}
# Document Type: txt
# Normalised For: Tender agent ingestion

{body}
"""

    if suffix == ".md":
        body = normalise_markdown_file(file_path)
        return f"""# Source: {file_path.name}
# Document Type: md
# Normalised For: Tender agent ingestion

{body}
"""

    if suffix == ".pdf":
        return placeholder_normalise_pdf(file_path)

    if suffix == ".docx":
        return placeholder_normalise_docx(file_path)

    raise ValueError(f"Unsupported file type: {file_path.suffix}")


def normalise_all_documents(tender_id: str) -> Dict[str, Any]:
    tender_id = tender_id.strip()
    if not tender_id:
        raise ValueError("tender_id is required")

    source_dir = Path("tenders") / tender_id / "input" / "01_customer_issued"
    output_dir = Path("tenders") / tender_id / "input" / "02_normalised"
    output_dir.mkdir(parents=True, exist_ok=True)

    processed: List[str] = []
    skipped: List[str] = []
    failed: List[Dict[str, str]] = []

    for file_path in source_dir.iterdir():
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            skipped.append(str(file_path))
            continue

        output_file = output_dir / normalise_filename(file_path.name)

        try:
            normalised_content = normalise_one_document(file_path)
            output_file.write_text(normalised_content, encoding="utf-8")
            processed.append(str(output_file))
        except Exception as e:
            failed.append({
                "source_file": str(file_path),
                "error": str(e),
            })

    return {
        "source_dir": str(source_dir),
        "output_dir": str(output_dir),
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
    }