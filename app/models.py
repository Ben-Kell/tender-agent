from pydantic import BaseModel
from typing import List


class StartTenderRunRequest(BaseModel):
    tender_id: str
    template_path: str
    tender_input_path: str
    boilerplate_paths: List[str] = []
    case_study_paths: List[str] = []
    output_mode: str = "extract_and_map"
