# app/docx_parser.py
import re
from pathlib import Path
from typing import Dict, List, Any


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def load_markdown_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def normalise_heading(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


def parse_markdown_sections(markdown_text: str) -> List[Dict[str, Any]]:
    lines = markdown_text.splitlines()
    sections: List[Dict[str, Any]] = []

    current = None

    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            hashes, title = match.groups()
            level = len(hashes)

            if current:
                current["content"] = current["content"].strip()
                sections.append(current)

            current = {
                "heading": normalise_heading(title),
                "level": level,
                "content": ""
            }
        else:
            if current is None:
                # ignore preamble before first heading
                continue
            current["content"] += line + "\n"

    if current:
        current["content"] = current["content"].strip()
        sections.append(current)

    return sections