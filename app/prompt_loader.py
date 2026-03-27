"""Loads LLM prompt templates from the local ``prompts/`` directory."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
    """Return the contents of ``prompts/<name>.md``.

    Args:
        name: The prompt file stem (without the ``.md`` extension).

    Returns:
        The raw text content of the prompt file.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def list_prompts() -> list[str]:
    """Return a sorted list of available prompt names (file stems)."""
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.md"))
