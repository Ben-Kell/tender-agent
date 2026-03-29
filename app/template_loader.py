from pathlib import Path


def load_template(template_name: str = "response_template.md") -> str:
    path = Path("templates") / template_name

    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")

    return path.read_text(encoding="utf-8")