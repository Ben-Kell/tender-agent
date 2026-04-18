import re

from app.openai_client import chat
from app.prompt_loader import load_prompt


# Match either:
#   ## 1. Executive Summary
# or
#   ## Executive Summary
# and replace the whole section body until the next ## heading.
EXEC_SUMMARY_HEADING_RE = re.compile(
    r"(?ms)^##\s+(?:1\.\s+)?Executive Summary\s*\n(.*?)(?=^##\s+(?:\d+\.\s+)?[^\n]+|\Z)"
)

def _strip_machine_json_blocks(text: str) -> str:
    # Remove obvious compliance JSON fragments that leak into markdown
    text = re.sub(
        r'(?ms)\{\s*"compliance"\s*:\s*\[.*?\]\s*\}',
        '',
        text
    )
    text = re.sub(
        r'(?ms)\{\s*"requirement_id"\s*:\s*"REQ-\d+".*?\}',
        '',
        text
    )
    return text.strip()

def remove_existing_executive_summary(markdown_text: str) -> str:
    return EXEC_SUMMARY_HEADING_RE.sub("## 1. Executive Summary\n\n", markdown_text)


def generate_executive_summary(full_markdown: str) -> str:
    system_prompt = load_prompt("system_instructions.md")
    full_markdown = _strip_machine_json_blocks(full_markdown)

    user_prompt = f"""
    Write a professional tender Executive Summary in Australian English.

    Requirements:
    - Base it only on the tender response narrative content provided below
    - Ignore any JSON, requirement IDs, mappings, diagnostics, compliance matrices, or machine-readable artefacts if present
    - Do not quote or reproduce JSON, lists of requirement IDs, or field/value pairs
    - Make it sound like a true executive summary for senior evaluators
    - Summarise the customer's need, Fujitsu's solution, key differentiators, delivery approach, value, and risk reduction
    - Do not invent facts not supported by the tender response
    - Keep it concise but polished
    - Return markdown paragraphs only
    - Do not include a heading
    - Do not use triple backticks

    TENDER RESPONSE CONTENT:

    {full_markdown}
    """

    raw_output = chat(system_prompt, user_prompt).strip()

    if raw_output.startswith("```markdown"):
        raw_output = raw_output[len("```markdown"):].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[len("```"):].strip()

    if raw_output.endswith("```"):
        raw_output = raw_output[:-3].strip()

    return raw_output


def inject_executive_summary(markdown_text: str, executive_summary_text: str) -> str:
    replacement = f"## 1. Executive Summary\n\n{executive_summary_text}\n\n"

    if EXEC_SUMMARY_HEADING_RE.search(markdown_text):
        return EXEC_SUMMARY_HEADING_RE.sub(replacement, markdown_text)

    # Fallback: if the heading is missing entirely, insert it before section 2 if present.
    section_2_re = re.compile(r"(?m)^##\s+(?:2\.\s+)?")
    match = section_2_re.search(markdown_text)
    if match:
        return markdown_text[:match.start()] + replacement + markdown_text[match.start():]

    # Last fallback: prepend it.
    return replacement + markdown_text