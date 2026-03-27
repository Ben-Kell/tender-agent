"""File-system storage helpers for per-tender input and output files."""

import json
from pathlib import Path
from typing import Any

TENDERS_DIR = Path(__file__).parent.parent / "tenders"


def get_tender_dir(rft_id: str) -> Path:
    """Return the working directory for the given RFT identifier."""
    return TENDERS_DIR / rft_id


def read_input_files(rft_id: str) -> dict[str, str]:
    """Read all plain-text input files for a tender and return a name→content mapping.

    Only files with ``.txt`` or ``.md`` extensions are read; binary formats such as
    PDF and DOCX are skipped.

    Args:
        rft_id: The RFT identifier (e.g. ``"RFT-123"``).

    Returns:
        Dict mapping filename to text content for each readable input file.
    """
    input_dir = get_tender_dir(rft_id) / "input"
    files: dict[str, str] = {}
    if not input_dir.exists():
        return files
    for path in sorted(input_dir.iterdir()):
        if path.suffix in {".txt", ".md"} and path.is_file():
            files[path.name] = path.read_text(encoding="utf-8")
    return files


def save_output(rft_id: str, filename: str, content: str) -> Path:
    """Write a text file to the tender's output directory.

    Args:
        rft_id: The RFT identifier.
        filename: Name of the output file (e.g. ``"draft_response.md"``).
        content: Text content to write.

    Returns:
        The :class:`~pathlib.Path` of the written file.
    """
    output_dir = get_tender_dir(rft_id) / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def save_json(rft_id: str, filename: str, data: Any) -> Path:
    """Serialise *data* to JSON and save it to the tender's output directory.

    Args:
        rft_id: The RFT identifier.
        filename: Name of the output file (e.g. ``"requirements.json"``).
        data: JSON-serialisable object.

    Returns:
        The :class:`~pathlib.Path` of the written file.
    """
    return save_output(rft_id, filename, json.dumps(data, indent=2))


def load_json(rft_id: str, filename: str) -> Any:
    """Load and parse a JSON file from the tender's output directory.

    Args:
        rft_id: The RFT identifier.
        filename: Name of the file to load.

    Returns:
        Parsed JSON object.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = get_tender_dir(rft_id) / "output" / filename
    if not path.exists():
        raise FileNotFoundError(f"Output file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
