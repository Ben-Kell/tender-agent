from __future__ import annotations

from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()


def _normalise_name(name: str) -> str:
    return " ".join((name or "").lower().replace("-", " ").split())


def find_best_rate_card_match(
    tender_role: Dict[str, Any],
    rate_card_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    tender_sfia_code = (tender_role.get("sfia_code") or "").upper().strip()
    tender_sfia_level = tender_role.get("sfia_level")
    tender_role_name = tender_role.get("tender_role_name") or ""

    exact_candidates = []
    code_only_candidates = []

    for row in rate_card_rows:
        row_code = (row.get("sfia_code") or "").upper().strip()
        row_level = row.get("sfia_level")

        if tender_sfia_code and tender_sfia_level is not None:
            if row_code == tender_sfia_code and row_level == tender_sfia_level:
                exact_candidates.append(row)

        if tender_sfia_code and row_code == tender_sfia_code:
            code_only_candidates.append(row)

    # 1. exact code + level match
    if exact_candidates:
        chosen = exact_candidates[0]
        return {
            "match_status": "EXACT_SFIA_CODE_LEVEL_MATCH",
            "confidence": "high",
            "matched_row": chosen,
            "recommended_row": None,
        }

    # 2. code match only, suggest closest level if possible
    if code_only_candidates:
        recommended = None

        if tender_sfia_level is not None:
            ordered = sorted(
                code_only_candidates,
                key=lambda r: abs((r.get("sfia_level") or 999) - tender_sfia_level)
            )
            recommended = ordered[0]
        else:
            recommended = code_only_candidates[0]

        return {
            "match_status": "NO_EXACT_MATCH_CODE_ONLY_RECOMMENDATION",
            "confidence": "medium",
            "matched_row": None,
            "recommended_row": recommended,
        }

    # 3. fuzzy fallback against skill text and skill name
    scored = []
    for row in rate_card_rows:
        skill_text = row.get("skill_text", "")
        skill_name = row.get("skill_name", "")
        score = max(
            _similarity(_normalise_name(tender_role_name), _normalise_name(skill_text)),
            _similarity(_normalise_name(tender_role_name), _normalise_name(skill_name)),
        )
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    recommended = scored[0][1] if scored else None
    top_score = scored[0][0] if scored else 0.0

    if recommended and top_score >= 0.55:
        confidence = "medium" if top_score >= 0.75 else "low"
        return {
            "match_status": "NO_EXACT_MATCH_FUZZY_RECOMMENDATION",
            "confidence": confidence,
            "matched_row": None,
            "recommended_row": recommended,
        }

    return {
        "match_status": "NO_MATCH_FOUND",
        "confidence": "low",
        "matched_row": None,
        "recommended_row": None,
    }