from pathlib import Path

def load_knowledge_docs(root: str = "knowledge_library") -> list[dict]:
    docs = []
    root_path = Path(root)

    if not root_path.exists():
        return docs

    for path in root_path.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        category = path.parent.name
        docs.append({
            "source_file": path.name,
            "source_path": str(path),
            "category": category,
            "title": path.stem.replace("_", " ").title(),
            "text": text,
            "metadata": {
                "category": category,
                "source_path": str(path),
            }
        })

    return docs