"""Pydantic data models for the tender-agent workflow."""

from typing import List, Literal, Optional

from pydantic import BaseModel


class Requirement(BaseModel):
    """A single requirement extracted from a tender document."""

    id: str
    clause: str
    text: str
    category: Literal["Mandatory", "Desirable", "Informational"]
    evaluation_criterion: Optional[str] = None


class TemplateMapping(BaseModel):
    """Maps a requirement to a section of the response template."""

    requirement_id: str
    template_section: str
    notes: Optional[str] = None


class DraftSection(BaseModel):
    """A drafted section of the tender response."""

    section: str
    content: str


class QAReport(BaseModel):
    """Quality assurance review report for a drafted tender response."""

    passed: List[str]
    failed: List[dict]
    risk_flags: List[str]
