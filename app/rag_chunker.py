import re
import uuid

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    text = re.sub(r"\r\n", "\n", text).strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, 0)

    return chunks


def build_chunks(docs: list[dict]) -> list[dict]:
    chunks = []

    for doc in docs:
        split_chunks = chunk_text(doc["text"])
        for idx, chunk in enumerate(split_chunks, start=1):
            chunks.append({
                "chunk_id": f"chunk_{uuid.uuid4().hex[:10]}",
                "source_file": doc["source_file"],
                "source_path": doc["source_path"],
                "category": doc["category"],
                "title": doc["title"],
                "text": chunk,
                "metadata": {
                    **doc.get("metadata", {}),
                    "chunk_number": idx,
                }
            })

    return chunks