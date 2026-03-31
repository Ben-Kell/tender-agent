from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from app.storage import RUNS
from app.workflow import start_run, map_template, draft_sections, compile_response, run_full_pipeline
from app.tender_ingest import create_and_ingest_tender

from app.returnable_detector import detect_returnable_documents



app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/")
def home():
    return FileResponse("static/index.html")

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

@app.post("/run_full_pipeline")
def run_full_pipeline_endpoint(request: FullPipelineRequest):
    return run_full_pipeline(request.dict())

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

@app.get("/list_outputs/{tender_id}")
def list_outputs(tender_id: str):
    output_dir = Path("tenders") / tender_id / "output"

    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output folder not found")

    files = sorted(
        [item.name for item in output_dir.iterdir() if item.is_file()]
    )

    return {
        "tender_id": tender_id,
        "files": files,
    }


@app.get("/download_output/{tender_id}/{filename}")
def download_output(tender_id: str, filename: str):
    output_dir = Path("tenders") / tender_id / "output"
    file_path = output_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )