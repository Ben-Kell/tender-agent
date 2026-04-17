from fastapi import FastAPI, HTTPException
from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from pathlib import Path
from typing import List

from app.storage import RUNS
from app.workflow import start_run, map_template, draft_sections, compile_response, run_full_pipeline
from app.tender_ingest import create_and_ingest_tender
from app.returnable_detector import detect_returnable_documents
from app.pricing_model_detector import detect_pricing_model
from app.tm_pricing_csv import generate_tm_pricing_csv

import shutil



app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
DUMP_DIR = BASE_DIR / "dump"
DUMP_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

class TenderRunRequest(BaseModel):
    tender_id: str

class DetectPricingModelRequest(BaseModel):
    tender_id: str

class DetectReturnableDocumentsRequest(BaseModel):
    tender_id: str
    
class GenerateTMPricingRequest(BaseModel):
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

@app.post("/detect_pricing_model")
def detect_pricing_model_endpoint(request: DetectPricingModelRequest):
    result = detect_pricing_model(request.tender_id)
    return {
        "status": "success",
        "message": f"Pricing model analysed for {request.tender_id}",
        "result": result,
    }

@app.post("/generate_tm_pricing_csv")
def generate_tm_pricing_csv_endpoint(request: GenerateTMPricingRequest):
    result = generate_tm_pricing_csv(request.tender_id)
    return {
        "status": "success",
        "message": f"T&M pricing CSV processed for {request.tender_id}",
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

@app.post("/upload_tender_documents")
async def upload_tender_documents(
    tender_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    safe_tender_id = tender_id.strip()

    if not safe_tender_id:
        raise HTTPException(status_code=400, detail="tender_id is required")

    tender_dump_dir = DUMP_DIR / safe_tender_id
    tender_dump_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for upload in files:
        if not upload.filename or not upload.filename.strip():
            continue

        destination_path = tender_dump_dir / Path(upload.filename).name

        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(upload.file, buffer)

        saved_files.append(destination_path.name)

    if not saved_files:
        raise HTTPException(status_code=400, detail="No valid files were uploaded")

    return {
        "message": f"Uploaded {len(saved_files)} file(s) to dump/{safe_tender_id}",
        "tender_id": safe_tender_id,
        "dump_folder": str(tender_dump_dir),
        "files": saved_files
    }