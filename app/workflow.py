import uuid
from app.storage import RUNS


def start_run(config: dict) -> dict:
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    RUNS[run_id] = {
        "status": "completed",
        "current_step": "done",
        "config": config,
        "result": {
            "requirements": [],
            "template_map": []
        }
    }
    return {"run_id": run_id, "status": "queued"}


def get_status(run_id: str) -> dict:
    run = RUNS.get(run_id)
    if not run:
        return {"error": "run not found"}
    return {
        "run_id": run_id,
        "status": run["status"],
        "current_step": run["current_step"]
    }


def get_result(run_id: str) -> dict:
    run = RUNS.get(run_id)
    if not run:
        return {"error": "run not found"}
    return {
        "run_id": run_id,
        "status": run["status"],
        "result": run["result"]
    }
