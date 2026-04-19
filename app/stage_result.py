from typing import Any


def make_stage_response(
    *,
    run_id: str,
    status: str,
    current_step: str,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "status": status,
        "current_step": current_step,
        "result": result or {},
    }


def assert_stage_completed(stage_name: str, stage_result: dict) -> None:
    if not isinstance(stage_result, dict):
        raise RuntimeError(f"{stage_name} returned a non-dict response")

    if stage_result.get("status") != "completed":
        raise RuntimeError(f"{stage_name} failed: {stage_result.get('result')}")