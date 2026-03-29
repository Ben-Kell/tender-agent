from pathlib import Path
from typing import List, Dict


def load_markdown_folder(folder_path: Path) -> List[Dict[str, str]]:
    if not folder_path.exists():
        return []

    docs = []
    for path in sorted(folder_path.glob("*.md")):
        docs.append({
            "filename": path.name,
            "content": path.read_text(encoding="utf-8")
        })
    return docs


def load_boilerplate_docs() -> List[Dict[str, str]]:
    return load_markdown_folder(Path("boilerplate"))


def load_case_studies() -> List[Dict[str, str]]:
    return load_markdown_folder(Path("case_studies"))