from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.json_loader import load_tender_output_json
from app.rate_card_loader import load_ictpa_rate_card
from app.tm_role_extractor import extract_tm_roles
from app.tm_role_matcher import find_best_rate_card_match
from app.output_writer import write_tender_output


def _days_from_duration(duration_years: Optional[int], duration_months: Optional[int]) -> Optional[int]:
    years = duration_years or 0
    months = duration_months or 0

    if years == 0 and months == 0:
        return None

    # 220 days per year, 110 per 6 months
    total_days = (years * 220) + int((months / 12) * 220)
    return total_days


def _convert_rate(rate_day: Optional[float], target_unit: str) -> Optional[float]:
    if rate_day is None:
        return None

    if target_unit == "hour":
        return round(rate_day / 8, 2)

    return round(rate_day, 2)


def _build_note(match_status: str, confidence: str, recommended_row: Optional[Dict[str, Any]]) -> str:
    if match_status == "EXACT_SFIA_CODE_LEVEL_MATCH":
        return "Matched on SFIA code and level"

    if match_status == "NO_EXACT_MATCH_CODE_ONLY_RECOMMENDATION" and recommended_row:
        return (
            f"NO_MATCH_FOUND exact level. Recommended closest row by SFIA code: "
            f"{recommended_row.get('skill_text')} level {recommended_row.get('sfia_level')} "
            f"(confidence={confidence})"
        )

    if match_status == "NO_EXACT_MATCH_FUZZY_RECOMMENDATION" and recommended_row:
        return (
            f"NO_MATCH_FOUND exact SFIA match. Recommended fuzzy row: "
            f"{recommended_row.get('skill_text')} level {recommended_row.get('sfia_level')} "
            f"(confidence={confidence})"
        )

    return "NO_MATCH_FOUND"


def generate_tm_pricing_csv(tender_id: str) -> Dict[str, Any]:
    pricing_model = load_tender_output_json(tender_id, "pricing_model_detection.json")
    detected_model = pricing_model.get("pricing_model", "")

    if detected_model != "staff_augmentation_time_and_materials":
        result = {
            "status": "skipped",
            "reason": f"pricing_model={detected_model}",
            "output_file": None,
        }
        write_tender_output(tender_id, "tm_pricing_output.json", json.dumps(result, indent=2))
        return result

    extracted_roles = extract_tm_roles(tender_id)
    tender_roles = extracted_roles.get("tender_roles", [])
    rate_card_rows = load_ictpa_rate_card()

    output_dir = Path("tenders") / tender_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "tm_pricing_schedule.csv"
    diagnostics_path = output_dir / "tm_pricing_matches.json"

    csv_rows: List[Dict[str, Any]] = []
    diagnostics: List[Dict[str, Any]] = []

    for role in tender_roles:
        match_result = find_best_rate_card_match(role, rate_card_rows)

        matched_row = match_result.get("matched_row")
        recommended_row = match_result.get("recommended_row")
        match_status = str(match_result.get("match_status") or "NO_MATCH_FOUND")
        confidence = str(match_result.get("confidence") or "low")

        chosen_row = matched_row
        pricing_unit_required = role.get("pricing_unit_required") or "day"

        sell_rate = _convert_rate(
            chosen_row.get("sell_rate") if chosen_row else None,
            pricing_unit_required,
        )

        contract_days = _days_from_duration(
            role.get("duration_years"),
            role.get("duration_months"),
        )

        quantity = role.get("quantity") or 1
        total_price = None

        if sell_rate is not None and contract_days is not None and pricing_unit_required == "day":
            total_price = round(sell_rate * contract_days * quantity, 2)
        elif sell_rate is not None and contract_days is not None and pricing_unit_required == "hour":
            total_hours = contract_days * 8
            total_price = round(sell_rate * total_hours * quantity, 2)

        notes = _build_note(match_status, confidence, recommended_row)

        csv_rows.append({
            "tender_role_name": role.get("tender_role_name", ""),
            "matched_rate_card_role_name": chosen_row.get("skill_text", "") if chosen_row else "",
            "sfia_code": role.get("sfia_code", ""),
            "sfia_level": role.get("sfia_level", ""),
            "quantity": quantity,
            "unit": pricing_unit_required,
            "sell_rate": sell_rate if sell_rate is not None else "",
            "contract_days": contract_days if contract_days is not None else "",
            "total_price": total_price if total_price is not None else "",
            "notes_assumptions": notes,
        })

        if matched_row is None and recommended_row is not None:
            recommended_rate = _convert_rate(
                recommended_row.get("sell_rate"),
                pricing_unit_required,
            )

            recommended_total = None
            if recommended_rate is not None and contract_days is not None and pricing_unit_required == "day":
                recommended_total = round(recommended_rate * contract_days * quantity, 2)
            elif recommended_rate is not None and contract_days is not None and pricing_unit_required == "hour":
                recommended_total = round(recommended_rate * (contract_days * 8) * quantity, 2)

            csv_rows.append({
                "tender_role_name": f"RECOMMENDED_MATCH_FOR: {role.get('tender_role_name', '')}",
                "matched_rate_card_role_name": recommended_row.get("skill_text", ""),
                "sfia_code": recommended_row.get("sfia_code", ""),
                "sfia_level": recommended_row.get("sfia_level", ""),
                "quantity": quantity,
                "unit": pricing_unit_required,
                "sell_rate": recommended_rate if recommended_rate is not None else "",
                "contract_days": contract_days if contract_days is not None else "",
                "total_price": recommended_total if recommended_total is not None else "",
                "notes_assumptions": f"Recommendation only. confidence={confidence}",
            })

        diagnostics.append({
            "tender_role": role,
            "match_result": {
                "match_status": match_status,
                "confidence": confidence,
                "matched_row": matched_row,
                "recommended_row": recommended_row,
            }
        })

    fieldnames = [
        "tender_role_name",
        "matched_rate_card_role_name",
        "sfia_code",
        "sfia_level",
        "quantity",
        "unit",
        "sell_rate",
        "contract_days",
        "total_price",
        "notes_assumptions",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    with diagnostics_path.open("w", encoding="utf-8") as f:
        json.dump(diagnostics, f, indent=2)

    result = {
        "status": "completed",
        "output_file": str(csv_path),
        "diagnostics_file": str(diagnostics_path),
        "role_count": len(tender_roles),
        "csv_row_count": len(csv_rows),
    }

    write_tender_output(tender_id, "tm_pricing_output.json", json.dumps(result, indent=2))
    return result