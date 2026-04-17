import json
from typing import Any, Dict, List

from app.prompt_loader import load_prompt
from app.openai_client import chat
from app.text_chunker import split_text_into_chunks
from app.output_writer import write_tender_output


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


def normalise_text(value: str) -> str:
    return " ".join((value or "").strip().lower().split())


def _normalise_requirement_obj(item: Any, fallback_index: int) -> Dict[str, Any] | None:
    if not isinstance(item, dict):
        return None

    requirement_text = str(item.get("requirement_text", "")).strip()
    if not requirement_text:
        requirement_text = str(
            item.get("text")
            or item.get("requirement")
            or item.get("description")
            or ""
        ).strip()

    if not requirement_text:
        return None

    requirement_id = str(item.get("requirement_id", "")).strip()
    if not requirement_id:
        requirement_id = f"REQ-AUTO-{fallback_index:04d}"

    clause_reference = str(item.get("clause_reference", "")).strip()
    requirement_type = str(item.get("requirement_type", "response")).strip().lower()
    response_needed = item.get("response_needed", True)

    allowed_types = {
        "mandatory",
        "response",
        "commercial",
        "security",
        "personnel",
        "governance",
        "technical",
    }
    if requirement_type not in allowed_types:
        requirement_type = "response"

    if not isinstance(response_needed, bool):
        response_needed = True

    return {
        "requirement_id": requirement_id,
        "clause_reference": clause_reference,
        "requirement_text": requirement_text,
        "requirement_type": requirement_type,
        "response_needed": response_needed,
    }


def _extract_requirements_from_parsed_payload(parsed: Any) -> List[Dict[str, Any]]:
    candidates = []

    if isinstance(parsed, list):
        candidates = parsed
    elif isinstance(parsed, dict):
        if isinstance(parsed.get("requirements"), list):
            candidates = parsed["requirements"]
        elif isinstance(parsed.get("items"), list):
            candidates = parsed["items"]
        elif isinstance(parsed.get("data"), list):
            candidates = parsed["data"]
        elif isinstance(parsed.get("output"), list):
            candidates = parsed["output"]
        else:
            if "requirement_text" in parsed or "text" in parsed or "requirement" in parsed:
                candidates = [parsed]

    normalised: List[Dict[str, Any]] = []
    for i, item in enumerate(candidates, start=1):
        obj = _normalise_requirement_obj(item, i)
        if obj:
            normalised.append(obj)

    return normalised


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
            f"Failed to parse JSON from chunk {chunk_index} in document {doc_name}.\n"
            f"Raw response was:\n{content}"
        ) from e

    return _extract_requirements_from_parsed_payload(parsed)


def extract_requirements_from_documents(
    tender_id: str,
    documents: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    all_requirements: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []

    for doc in documents:
        doc_name = doc.get("name", "unknown_document")
        doc_text = doc.get("content", "")

        if not doc_text.strip():
            diagnostics.append({
                "document": doc_name,
                "status": "skipped_empty_document",
                "chunks": []
            })
            continue

        chunks = split_text_into_chunks(doc_text, max_chars=15000, overlap=800)
        print(f"[extract] {doc_name}: {len(chunks)} chunk(s)")

        doc_diag = {
            "document": doc_name,
            "status": "processed",
            "chunk_count": len(chunks),
            "chunks": []
        }

        for i, chunk in enumerate(chunks, start=1):
            print(f"[extract] Processing {doc_name} chunk {i}/{len(chunks)}")
            try:
                chunk_requirements = extract_requirements_from_chunk(
                    doc_name=doc_name,
                    chunk_text=chunk,
                    chunk_index=i,
                )
                all_requirements.extend(chunk_requirements)

                doc_diag["chunks"].append({
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "requirement_count": len(chunk_requirements),
                    "status": "ok",
                    "chunk_preview": chunk[:800]
                })
            except Exception as e:
                doc_diag["chunks"].append({
                    "chunk_index": i,
                    "chunk_length": len(chunk),
                    "requirement_count": 0,
                    "status": "error",
                    "error": str(e),
                    "chunk_preview": chunk[:800]
                })

        diagnostics.append(doc_diag)

    write_tender_output(
        tender_id,
        "requirement_extraction_diagnostics.json",
        diagnostics,
    )

    return all_requirements


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
    tender_id: str,
    documents: List[Dict[str, str]]
) -> List[Dict[str, Any]]:
    raw_requirements = extract_requirements_from_documents(tender_id, documents)
    deduped = deduplicate_requirements(raw_requirements)

    write_tender_output(
        tender_id,
        "raw_extracted_requirements.json",
        raw_requirements,
    )

    return deduped