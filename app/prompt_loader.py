from pathlib import Path


def load_prompt(filename: str) -> str:
    path = Path("prompts") / filename

    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    return path.read_text(encoding="utf-8")