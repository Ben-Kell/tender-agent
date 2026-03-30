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

class FullTenderPipelineRequest(BaseModel):
    tender_id: str
    template_name: str = "response_template.md"


@app.post("/create_tender")
def create_tender(request: CreateTenderRequest):
    result = create_and_ingest_tender(request.tender_id)
    return {
        "status": "success",
        "message": f"Tender structure created and source files ingested for {request.tender_id}",
        "result": result,
    }

@app.post("/detect_returnable_documents")
def detect_returnable_documents_endpoint(tender_id: str, use_llm: bool = False):
    result = detect_returnable_documents(
        tender_id=tender_id,
        use_llm=use_llm,
        chat_fn=chat if use_llm else None,
    )
    return result

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

@app.post("/run_full_tender_pipeline")
def run_full_tender_pipeline(request: FullTenderPipelineRequest):
    config = {
        "tender_id": request.tender_id,
        "template_name": request.template_name,
    }

    pipeline_result = {}

    try:
        pipeline_result["create_tender"] = create_and_ingest_tender(request.tender_id)

        pipeline_result["start_tender_run"] = start_run(config)
        if pipeline_result["start_tender_run"].get("status") == "failed":
            raise RuntimeError("start_tender_run failed")

        pipeline_result["map_template"] = map_template(config)
        if pipeline_result["map_template"].get("status") == "failed":
            raise RuntimeError("map_template failed")

        pipeline_result["draft_sections"] = draft_sections(config)
        if pipeline_result["draft_sections"].get("status") == "failed":
            raise RuntimeError("draft_sections failed")

        pipeline_result["compile_response"] = compile_response(config)
        if pipeline_result["compile_response"].get("status") == "failed":
            raise RuntimeError("compile_response failed")

        return {
            "status": "success",
            "message": f"Full tender pipeline completed for {request.tender_id}",
            "result": pipeline_result,
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Pipeline failed for {request.tender_id}",
            "error": str(e),
            "result": pipeline_result,
        }
    
@app.post("/rerun_tender_pipeline")
def rerun_tender_pipeline(request: FullTenderPipelineRequest):
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