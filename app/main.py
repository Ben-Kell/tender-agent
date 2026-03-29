from fastapi import FastAPI
from pydantic import BaseModel

from app.storage import RUNS
from app.workflow import start_run

app = FastAPI()


class TenderRunRequest(BaseModel):
    tender_id: str


@app.post("/start_tender_run")
def start_tender_run(request: TenderRunRequest):
    return start_run(request.dict())


@app.get("/get_tender_run_status/{run_id}")
def get_tender_run_status(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        return {"error": "Run not found"}
    return {
        "run_id": run_id,
        "status": run["status"],
        "current_step": run["current_step"],
    }


@app.get("/get_tender_run_result/{run_id}")
def get_tender_run_result(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        return {"error": "Run not found"}
    return {
        "run_id": run_id,
        "status": run["status"],
        "result": run["result"],
    }