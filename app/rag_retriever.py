import json
import math
from pathlib import Path

from app.openai_client import embed_texts

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def load_rag_index(index_path: str = "knowledge_library/index.json") -> dict:
    path = Path(index_path)
    if not path.exists():
        return {"chunks": []}
    return json.loads(path.read_text(encoding="utf-8"))


def build_query_text(
    section: dict,
    matched_requirements: list[dict],
    tender_metadata: dict
) -> str:
    response_focuses = section.get("response_focuses", [])

    return "\n".join([
        f"Section: {section.get('template_section', '')}",
        f"Purpose: {section.get('section_purpose', '')}",
        f"Guidance: {section.get('response_guidance', '')}",
        f"Response focuses: {', '.join(response_focuses)}",
        f"Tender title: {tender_metadata.get('tender_title', '')}",
        "Priority topics: proposal response, understanding, methodology, delivery approach, governance, transition, security",
        "Requirements:",
        "\n".join(
            f"- {req.get('requirement_text', '')}" for req in matched_requirements
        )
    ]).strip()

def retrieve_relevant_chunks(
    section: dict,
    matched_requirements: list[dict],
    tender_metadata: dict,
    index_path: str = "knowledge_library/index.json",
    top_k: int = 6
) -> list[dict]:
    index = load_rag_index(index_path)
    chunks = index.get("chunks", [])
    if not chunks:
        return []

    query_text = build_query_text(section, matched_requirements, tender_metadata)
    query_embedding = embed_texts([query_text])[0]

    scored = []
    for chunk in chunks:
        score = cosine_similarity(query_embedding, chunk["embedding"])
        scored.append({
            **chunk,
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]