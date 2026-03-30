# app/returnable_detector/classifier.py

import json


def classify_document_with_llm(chat_fn, filename: str, content: str):
    """
    Optional LLM refinement layer.
    `chat_fn` should be your existing offline-compatible chat function.
    """

    prompt = f"""
You are analysing a tender document.

Your task is to determine whether this document appears to require supplier completion and return as part of a tender submission.

Return ONLY valid JSON in this format:
{{
  "is_returnable": true,
  "confidence": 0.85,
  "document_type": "pricing_schedule",
  "reasoning": "short explanation"
}}

Possible document_type values:
- pricing_schedule
- compliance_schedule
- response_schedule
- declaration
- deed
- aic_plan
- contract_data
- order_form
- attachment_requiring_completion
- reference_only
- unknown

Filename:
{filename}

Document excerpt:
{content[:5000]}
"""

    raw = chat_fn(prompt)

    if isinstance(raw, dict):
        return raw

    try:
        return json.loads(raw)
    except Exception:
        return {
            "is_returnable": False,
            "confidence": 0.0,
            "document_type": "unknown",
            "reasoning": "LLM classification could not be parsed"
        }