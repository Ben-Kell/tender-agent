from fastapi import FastAPI
from pydantic import BaseModel

from app.storage import RUNS
from app.workflow import start_run, map_template, draft_sections, compile_response
from app.tender_ingest import create_and_ingest_tender

app = FastAPI()


class TenderRunRequest(BaseModel):
    tender_id: str


class TemplateMapRequest(BaseModel):
    tender_id: str
    template_name: str = "response_template.md"


class SectionDraftRequest(BaseModel):
    tender_id: str
    template_name: str = "response_template.md"


class CompileResponseRequest(BaseModel):
    tender_id: str
    template_name: str = "response_template.md"


class CreateTenderRequest(BaseModel):
    tender_id: str


@app.post("/create_tender")
def create_tender(request: CreateTenderRequest):
    result = create_and_ingest_tender(request.tender_id)
    return {
        "status": "success",
        "message": f"Tender structure created and source files ingested for {request.tender_id}",
        "result": result,
    }


@app.post("/start_tender_run")
def start_tender_run(request: TenderRunRequest):
    return start_run(request.dict())


@app.post("/map_template")
def map_template_endpoint(request: TemplateMapRequest):
    return map_template(request.dict())


@app.post("/draft_sections")
def draft_sections_endpoint(request: SectionDraftRequest):
    return draft_sections(request.dict())


@app.post("/compile_response")
def compile_response_endpoint(request: CompileResponseRequest):
    return compile_response(request.dict())


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