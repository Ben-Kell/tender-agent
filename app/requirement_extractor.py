import json
from typing import Any, Dict, List

from app.prompt_loader import load_prompt
from app.openai_client import chat
from app.text_chunker import split_text_into_chunks


def _clean_json_response(content: str) -> str:
    """
    Removes markdown code fences if the model returns ```json ... ```
    """
    if not content:
        return ""

    content = content.strip()

    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]

    if content.endswith("```"):
        content = content[:-3]

    return content.strip()


def _coerce_chat_response_to_text(response: Any) -> str:
    """
    Handles different possible return shapes from chat().
    """
    if isinstance(response, str):
        return response.strip()

    if isinstance(response, dict):
        if "content" in response and isinstance(response["content"], str):
            return response["content"].strip()

        try:
            return response["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    return str(response).strip()


def extract_requirements_from_chunk(
    doc_name: str,
    chunk_text: str,
    chunk_index: int
) -> List[Dict[str, Any]]:
    if not chunk_text or not chunk_text.strip():
        return []

    if len(chunk_text) > 15000:
        raise ValueError(
            f"Chunk too large before sending to model: {doc_name} chunk {chunk_index}"
        )

    prompt = load_prompt("extract_requirements.md")

    user_prompt = f"""
Document name: {doc_name}
Chunk number: {chunk_index}

Extract all tender requirements from the following text.

Return JSON only as a list of requirement objects.

If there are no requirements, return:
[]

Text:
{chunk_text}
""".strip()

    response = chat(
        system_prompt=prompt,
        user_prompt=user_prompt,
        model="gpt-4o",
    )

    content = _coerce_chat_response_to_text(response)
    content = _clean_json_response(content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from chunk {chunk_index} in document {doc_name}. "
            f"Raw response was:\n{content}"
        ) from e

    if isinstance(parsed, list):
        return parsed

    if isinstance(parsed, dict) and "requirements" in parsed and isinstance(parsed["requirements"], list):
        return parsed["requirements"]

    return []


def extract_requirements_from_documents(
    documents: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_requirements: List[Dict[str, Any]] = []

    for doc in documents:
        doc_name = doc.get("name", "unknown_document")
        doc_text = doc.get("content", "")

        if not doc_text.strip():
            continue

        chunks = split_text_into_chunks(doc_text, max_chars=20000, overlap=1200)
        print(f"[extract] {doc_name}: {len(chunks)} chunk(s)")

        for i, chunk in enumerate(chunks, start=1):
            print(f"[extract] Processing {doc_name} chunk {i}/{len(chunks)}")

            chunk_requirements = extract_requirements_from_chunk(
                doc_name=doc_name,
                chunk_text=chunk,
                chunk_index=i,
            )

            all_requirements.extend(chunk_requirements)

    return all_requirements


def normalise_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def deduplicate_requirements(
    requirements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    seen = set()
    deduped: List[Dict[str, Any]] = []

    for req in requirements:
        requirement_text = normalise_text(req.get("requirement_text", ""))
        clause = normalise_text(req.get("clause_reference", ""))
        key = f"{clause}::{requirement_text}"

        if key not in seen and requirement_text:
            seen.add(key)
            deduped.append(req)

    return deduped


def extract_and_deduplicate_requirements(
    documents: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    raw_requirements = extract_requirements_from_documents(documents)
    return deduplicate_requirements(raw_requirements)