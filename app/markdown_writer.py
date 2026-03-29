from pathlib import Path


def write_markdown_output(tender_id: str, filename: str, content: str) -> str:
    output_dir = Path("tenders") / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename
    output_path.write_text(content, encoding="utf-8")
    return str(output_path)