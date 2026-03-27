from fastapi import FastAPI
from app.models import StartTenderRunRequest
from app.workflow import start_run, get_status, get_result

app = FastAPI(title="Tender Agent API")


@app.post("/start_tender_run")
def start_tender_run(request: StartTenderRunRequest):
    return start_run(request.model_dump())


@app.get("/get_tender_run_status/{run_id}")
def get_tender_run_status(run_id: str):
    return get_status(run_id)


@app.get("/get_tender_run_result/{run_id}")
def get_tender_run_result(run_id: str):
    return get_result(run_id)
