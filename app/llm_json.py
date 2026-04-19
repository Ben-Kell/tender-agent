import json
from typing import Any

from app.openai_client import chat


def strip_code_fences(text: str) -> str:
    cleaned = (text or "").strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def chat_json(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw_output = chat(system_prompt, user_prompt, model=model) if model else chat(system_prompt, user_prompt)
    cleaned_output = strip_code_fences(raw_output)

    try:
        parsed = json.loads(cleaned_output)
        if isinstance(parsed, dict):
            return parsed
        return {
            "error": "Model returned JSON that was not an object",
            "raw_output": raw_output,
        }
    except Exception:
        if fallback is not None:
            result = dict(fallback)
            result["raw_output"] = raw_output
            return result

        return {
            "error": "Failed to parse model output as JSON",
            "raw_output": raw_output,
        }