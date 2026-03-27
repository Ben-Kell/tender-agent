"""Orchestrates the end-to-end tender response workflow.

Steps
-----
1. **extract** – Parse the tender document and extract structured requirements.
2. **map** – Map each requirement to a section of the response template.
3. **draft** – Draft response content for every mapped section.
4. **review** – Perform a QA review of the draft against the original requirements.
"""

import json
import re
from typing import List

from app import storage
from app.models import DraftSection, QAReport, Requirement, TemplateMapping
from app.openai_client import chat
from app.prompt_loader import load_prompt


def _split_markdown_sections(text: str) -> List[DraftSection]:
    """Split a markdown document into :class:`DraftSection` objects by top-level headings.

    Each ``##``-level heading and the content that follows it becomes one section.
    Leading content before the first heading is discarded.

    Args:
        text: Markdown text to split.

    Returns:
        List of :class:`~app.models.DraftSection` objects, one per heading.
        Returns an empty list if no ``##`` headings are found.
    """
    pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if not matches:
        return []

    sections: List[DraftSection] = []
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections.append(DraftSection(section=heading, content=content))
    return sections


def _parse_qa_report(text: str) -> QAReport:
    """Extract passed checks, failed checks, and risk flags from a QA review report.

    The function looks for the three canonical sections produced by the ``qa_review``
    prompt (``Passed checks``, ``Failed checks``, ``Risk flags``) and collects the
    bullet-point items beneath each heading.  Any text that does not match these
    headings is stored verbatim in ``risk_flags`` as a fallback.

    Args:
        text: Raw markdown text returned by the LLM for the QA review step.

    Returns:
        A :class:`~app.models.QAReport` with structured findings.
    """
    passed: List[str] = []
    failed: List[dict] = []
    risk_flags: List[str] = []

    section_pattern = re.compile(
        r"^#+\s*(?P<heading>.+?)$\n(?P<body>.*?)(?=^#+\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    bullet_pattern = re.compile(r"^[-*]\s+(.+)$", re.MULTILINE)

    for match in section_pattern.finditer(text):
        heading = match.group("heading").strip().lower()
        body = match.group("body").strip()
        items = [m.group(1).strip() for m in bullet_pattern.finditer(body)]

        if "passed" in heading:
            passed.extend(items)
        elif "failed" in heading:
            failed.extend({"check": item} for item in items)
        elif "risk" in heading or "flag" in heading:
            risk_flags.extend(items)

    # Fallback: store the full report text so nothing is silently lost.
    if not passed and not failed and not risk_flags:
        risk_flags.append(text)

    return QAReport(passed=passed, failed=failed, risk_flags=risk_flags)


def extract_requirements(rft_id: str, tender_text: str) -> List[Requirement]:
    """Call the LLM to extract requirements from *tender_text*.

    Persists the result to ``output/requirements.json``.

    Args:
        rft_id: The RFT identifier used for file storage.
        tender_text: Raw text content of the tender document(s).

    Returns:
        List of :class:`~app.models.Requirement` objects.
    """
    system = load_prompt("system_instructions")
    user_prompt = load_prompt("extract_requirements")
    user = f"{user_prompt}\n\n## Tender Document\n\n{tender_text}"

    response = chat(system, user)
    data = json.loads(response)
    requirements = [Requirement(**r) for r in data]
    storage.save_json(rft_id, "requirements.json", [r.model_dump() for r in requirements])
    return requirements


def map_template(rft_id: str, requirements: List[Requirement]) -> List[TemplateMapping]:
    """Call the LLM to map *requirements* to response template sections.

    Persists the result to ``output/mappings.json``.

    Args:
        rft_id: The RFT identifier used for file storage.
        requirements: Requirements extracted in the previous step.

    Returns:
        List of :class:`~app.models.TemplateMapping` objects.
    """
    system = load_prompt("system_instructions")
    user_prompt = load_prompt("map_template")
    reqs_json = json.dumps([r.model_dump() for r in requirements], indent=2)
    user = f"{user_prompt}\n\n## Requirements\n\n{reqs_json}"

    response = chat(system, user)
    data = json.loads(response)
    mappings = [TemplateMapping(**m) for m in data]
    storage.save_json(rft_id, "mappings.json", [m.model_dump() for m in mappings])
    return mappings


def draft_sections(
    rft_id: str,
    requirements: List[Requirement],
    mappings: List[TemplateMapping],
) -> List[DraftSection]:
    """Call the LLM to draft tender response content.

    The LLM returns a single markdown document that mirrors the full response
    template structure (one document per call).  This is split into per-section
    entries by detecting top-level markdown headings so that individual sections
    can be inspected or post-processed independently.

    Persists the full draft to ``output/draft_response.md``.

    Args:
        rft_id: The RFT identifier used for file storage.
        requirements: Requirements extracted in the first step.
        mappings: Section mappings produced in the second step.

    Returns:
        List of :class:`~app.models.DraftSection` objects, one per top-level
        heading found in the response.  Falls back to a single ``"full_draft"``
        entry if no headings are detected.
    """
    system = load_prompt("system_instructions")
    user_prompt = load_prompt("draft_sections")
    reqs_json = json.dumps([r.model_dump() for r in requirements], indent=2)
    maps_json = json.dumps([m.model_dump() for m in mappings], indent=2)
    user = (
        f"{user_prompt}\n\n"
        f"## Requirements\n\n{reqs_json}\n\n"
        f"## Mappings\n\n{maps_json}"
    )

    response = chat(system, user)
    storage.save_output(rft_id, "draft_response.md", response)

    sections = _split_markdown_sections(response)
    return sections if sections else [DraftSection(section="full_draft", content=response)]


def qa_review(
    rft_id: str,
    draft: str,
    requirements: List[Requirement],
) -> QAReport:
    """Call the LLM to perform a QA review of the draft response.

    The LLM returns a markdown report structured around three sections:
    *Passed checks*, *Failed checks*, and *Risk flags*.  These are parsed into
    the corresponding :class:`~app.models.QAReport` fields.

    Persists the raw review report to ``output/qa_report.md``.

    Args:
        rft_id: The RFT identifier used for file storage.
        draft: Full text of the drafted response.
        requirements: Original requirements to check compliance against.

    Returns:
        A :class:`~app.models.QAReport` with the review findings.
    """
    system = load_prompt("system_instructions")
    user_prompt = load_prompt("qa_review")
    reqs_json = json.dumps([r.model_dump() for r in requirements], indent=2)
    user = (
        f"{user_prompt}\n\n"
        f"## Requirements\n\n{reqs_json}\n\n"
        f"## Draft Response\n\n{draft}"
    )

    response = chat(system, user)
    storage.save_output(rft_id, "qa_report.md", response)
    return _parse_qa_report(response)


def run_workflow(rft_id: str) -> None:
    """Run the full end-to-end tender response workflow for *rft_id*.

    Reads all plain-text input files from ``tenders/<rft_id>/input/``, then
    runs the extract → map → draft → review pipeline, saving all intermediate
    and final outputs to ``tenders/<rft_id>/output/``.

    Args:
        rft_id: The RFT identifier (e.g. ``"RFT-123"``).
    """
    tender_files = storage.read_input_files(rft_id)
    tender_text = "\n\n".join(tender_files.values())

    requirements = extract_requirements(rft_id, tender_text)
    mappings = map_template(rft_id, requirements)
    sections = draft_sections(rft_id, requirements, mappings)

    # Reconstruct the full draft text from all sections for the QA step.
    draft_text = "\n\n".join(
        f"## {s.section}\n\n{s.content}" if s.section != "full_draft" else s.content
        for s in sections
    )
    qa_review(rft_id, draft_text, requirements)

    print(f"Workflow complete for {rft_id}. Outputs saved to tenders/{rft_id}/output/")
