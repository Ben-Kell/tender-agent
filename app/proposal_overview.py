import re
from typing import Dict, Any, List


PROPOSAL_OVERVIEW_HEADING_RE = re.compile(
    r"(?ms)^##\s+2\.\s+Proposal Overview\s*\n(.*?)(?=^##\s+\d+\.|\Z)"
)


def build_proposal_overview_scaffold(proposal_overview_plan: Dict[str, Any]) -> str:
    sections: List[Dict[str, Any]] = proposal_overview_plan.get("proposal_overview_sections", [])

    if not sections:
        return "_No Proposal Overview sections were identified._"

    blocks: List[str] = []

    for section in sections:
        heading = (section.get("heading") or "").strip()
        reason = (section.get("reason") or "").strip()

        if not heading:
            continue

        if reason:
            block = (
                f"### {heading}\n\n"
                f"[Insert response content for {heading}]\n\n"
                f"*Why this is here:* {reason}"
            )
        else:
            block = f"### {heading}\n\n[Insert response content for {heading}]"

        blocks.append(block)

    if not blocks:
        return "_No Proposal Overview sections were identified._"

    return "\n\n".join(blocks).strip()


def remove_existing_proposal_overview(markdown_text: str) -> str:
    return PROPOSAL_OVERVIEW_HEADING_RE.sub("## 2. Proposal Overview\n\n", markdown_text)


def inject_proposal_overview(markdown_text: str, proposal_overview_text: str) -> str:
    def replacement(_: re.Match) -> str:
        return f"## 2. Proposal Overview\n\n{proposal_overview_text}\n\n"

    return PROPOSAL_OVERVIEW_HEADING_RE.sub(replacement, markdown_text)