from typing import Dict, List


FILENAME_KEYWORDS = {
    "pricing": ("pricing_schedule", 3),
    "price": ("pricing_schedule", 3),
    "cost": ("pricing_schedule", 2),
    "schedule": ("schedule", 2),
    "annex": ("annex", 2),
    "attachment": ("attachment", 2),
    "appendix": ("appendix", 2),
    "compliance": ("compliance_schedule", 3),
    "response": ("response_schedule", 2),
    "declaration": ("declaration", 3),
    "statement": ("statement", 1),
    "deed": ("deed", 3),
    "order form": ("order_form", 3),
    "contract data": ("contract_data", 3),
    "aic": ("aic_plan", 3),
}

RETURNABLE_PHRASES = [
    ("must be completed", 4),
    ("to be completed by the tenderer", 5),
    ("to be completed by the supplier", 5),
    ("to be completed by respondents", 5),
    ("to be completed by the respondent", 5),
    ("must be returned", 5),
    ("must be submitted", 4),
    ("submit with tender", 5),
    ("submit with response", 5),
    ("return this schedule", 5),
    ("supplier response", 4),
    ("tenderer response", 4),
    ("respondent response", 4),
    ("complete and return", 5),
    ("fill in", 2),
    ("complete the following", 3),
    ("the tenderer must provide", 4),
    ("the supplier must provide", 4),
    ("attach completed", 4),
]

REFERENCE_ONLY_PHRASES = [
    ("for information only", -5),
    ("for reference only", -5),
    ("draft contract for review", -3),
    ("background information", -3),
    ("this document is provided for guidance", -3),
]

TABLE_HINTS = [
    ("supplier response", 4),
    ("tenderer response", 4),
    ("respondent response", 4),
    ("compliant", 2),
    ("yes/no", 2),
    ("price", 2),
    ("rate", 2),
    ("unit price", 3),
    ("total price", 3),
]


def infer_document_type(filename: str, text: str) -> str:
    name = filename.lower()
    combined = f"{name}\n{text[:2000].lower()}"

    if "pricing" in combined or "unit price" in combined or "total price" in combined:
        return "pricing_schedule"
    if "compliance" in combined or "compliant" in combined:
        return "compliance_schedule"
    if "declaration" in combined:
        return "declaration"
    if "deed" in combined:
        return "deed"
    if "aic" in combined or "australian industry capability" in combined:
        return "aic_plan"
    if "order form" in combined:
        return "order_form"
    if "contract data" in combined:
        return "contract_data"
    if "response schedule" in combined:
        return "response_schedule"
    if "schedule" in combined:
        return "schedule"

    return "unknown"


def score_document(filename: str, content: str) -> Dict:
    score = 0
    reasons: List[str] = []
    key_signals = {
        "filename_keywords": [],
        "phrases": [],
        "negative_phrases": [],
        "table_hints": [],
        "markdown_table_detected": False,
    }

    filename_lower = filename.lower()
    text = content.lower()

    
    # 🔴 HARD OVERRIDE: only true Statement of Work documents are never returnable
    statement_of_work_filename_patterns = [
        "statement of work",
        "_sow",
        "sow_",
    ]

    work_order_exclusions = [
        "work order",
        "draft work order",
        "short form rfq",
        "rfq",
    ]

    is_statement_of_work_filename = any(
        pattern in filename_lower for pattern in statement_of_work_filename_patterns
    )

    has_work_order_exclusion = any(
        phrase in filename_lower for phrase in work_order_exclusions
    )

    if is_statement_of_work_filename and not has_work_order_exclusion:
        return {
            "score": -999,
            "is_returnable": False,
            "confidence": 0.99,
            "document_type": "statement_of_work",
            "reasons": ["Hard rule: filename identified as a Statement of Work document, which is not returnable"],
            "key_signals": {
                "override": "statement_of_work_filename"
            },
        }

    for keyword, (_, points) in FILENAME_KEYWORDS.items():
        if keyword in filename_lower:
            score += points
            reasons.append(f"Filename contains '{keyword}'")
            key_signals["filename_keywords"].append(keyword)

    for phrase, points in RETURNABLE_PHRASES:
        if phrase in text:
            score += points
            reasons.append(f"Contains phrase '{phrase}'")
            key_signals["phrases"].append(phrase)

    for phrase, points in REFERENCE_ONLY_PHRASES:
        if phrase in text:
            score += points
            reasons.append(f"Contains reference-only phrase '{phrase}'")
            key_signals["negative_phrases"].append(phrase)

    if "|" in content:
        score += 2
        reasons.append("Markdown table detected")
        key_signals["markdown_table_detected"] = True

    for hint, points in TABLE_HINTS:
        if hint in text:
            score += points
            reasons.append(f"Detected table/content hint '{hint}'")
            key_signals["table_hints"].append(hint)

    doc_type = infer_document_type(filename, text)
    is_returnable = score >= 5
    confidence = min(0.99, max(0.05, score / 12))

    return {
        "score": score,
        "is_returnable": is_returnable,
        "confidence": round(confidence, 2),
        "document_type": doc_type,
        "reasons": reasons,
        "key_signals": key_signals,
    }