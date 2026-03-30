from fastapi import FastAPI
from pydantic import BaseModel

from app.storage import RUNS
from app.workflow import start_run, map_template, draft_sections, compile_response
from app.tender_ingest import create_and_ingest_tender

from app.returnable_detector import detect_returnable_documents
from app.openai_client import chat


app = FastAPI()


class TenderRunRequest(BaseModel):
    tender_id: str

class DetectReturnableDocumentsRequest(BaseModel):
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

class FullPipelineRequest(BaseModel):
    tender_id: str
    template_name: str = "response_template.md"


@app.post("/create_tender")
def create_tender(request: CreateTenderRequest):
    result = create_and_ingest_tender(request.tender_id)
    return {
        "status": "success",
        "message": f"Tender created and ingested for {request.tender_id}",
        "result": result,
    }

@app.post("/detect_returnable_documents")
def detect_returnable_documents_endpoint(request: DetectReturnableDocumentsRequest):
    result = detect_returnable_documents(request.tender_id)
    return {
        "status": "success",
        "message": f"Returnable documents analysed for {request.tender_id}",
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

@app.post("/run_full_pipeline")
def run_full_pipeline(request: FullPipelineRequest):
    create_result = create_and_ingest_tender(request.tender_id)
    returnable_result = detect_returnable_documents(request.tender_id)
    extract_result = start_run({"tender_id": request.tender_id})
    map_result = map_template({
        "tender_id": request.tender_id,
        "template_name": request.template_name,
    })
    draft_result = draft_sections({
        "tender_id": request.tender_id,
        "template_name": request.template_name,
    })
    compile_result = compile_response({
        "tender_id": request.tender_id,
        "template_name": request.template_name,
    })

    return {
        "status": "success",
        "tender_id": request.tender_id,
        "steps": {
            "create_tender": create_result,
            "detect_returnable_documents": returnable_result,
            "start_tender_run": extract_result,
            "map_template": map_result,
            "draft_sections": draft_result,
            "compile_response": compile_result,
        }
    }


    
@app.post("/rerun_tender_pipeline")
def rerun_tender_pipeline(request: FullPipelineRequest):
    config = {
        "tender_id": request.tender_id,
        "template_name": request.template_name,
    }

    pipeline_result = {}

    try:
        pipeline_result["start_tender_run"] = start_run(config)
        pipeline_result["map_template"] = map_template(config)
        pipeline_result["draft_sections"] = draft_sections(config)
        pipeline_result["compile_response"] = compile_response(config)

        return {
            "status": "success",
            "message": f"Tender pipeline rerun completed for {request.tender_id}",
            "result": pipeline_result,
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Pipeline rerun failed for {request.tender_id}",
            "error": str(e),
            "result": pipeline_result,
        }