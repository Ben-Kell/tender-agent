import re

from app.openai_client import chat
from app.prompt_loader import load_prompt


EXEC_SUMMARY_HEADING_RE = re.compile(
    r"(?ms)^##\s+1\.\s+Executive Summary\s*\n(.*?)(?=^##\s+\d+\.|\Z)"
)


def remove_existing_executive_summary(markdown_text: str) -> str:
    return EXEC_SUMMARY_HEADING_RE.sub("## 1. Executive Summary\n\n", markdown_text)


def generate_executive_summary(full_markdown: str) -> str:
    system_prompt = load_prompt("system_instructions.md")

    user_prompt = f"""
Write a professional tender Executive Summary in Australian English.

Requirements:
- Base it only on the tender response content provided below
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
    def replacement(_: re.Match) -> str:
        return f"## 1. Executive Summary\n\n{executive_summary_text}\n\n"

    return EXEC_SUMMARY_HEADING_RE.sub(replacement, markdown_text)