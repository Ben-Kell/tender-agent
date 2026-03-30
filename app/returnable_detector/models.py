from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ReturnableDocumentResult(BaseModel):
    filename: str
    original_filename: Optional[str] = None
    is_returnable: bool
    confidence: float
    document_type: str
    reasons: List[str] = Field(default_factory=list)
    key_signals: Dict = Field(default_factory=dict)
    score: int = 0


class ReturnableDocumentsReport(BaseModel):
    tender_id: str
    documents: List[ReturnableDocumentResult]
    summary: Dict