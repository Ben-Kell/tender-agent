"""Fetches repository files from GitHub via the REST API."""

import base64

import httpx

from app.config import get_settings

_GITHUB_API = "https://api.github.com"


def load_github_file(path: str) -> str:
    """Fetch a file from the configured GitHub repository and return its text content.

    Args:
        path: Repository-relative path to the file (e.g. ``"prompts/system_instructions.md"``).

    Returns:
        Decoded UTF-8 text content of the file.

    Raises:
        httpx.HTTPStatusError: If the GitHub API returns a non-2xx response.
    """
    settings = get_settings()
    url = f"{_GITHUB_API}/repos/{settings.github_repo}/contents/{path}"
    params = {"ref": settings.github_branch}
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    response = httpx.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    raw: str = data["content"]
    return base64.b64decode(raw).decode("utf-8")


def list_github_directory(directory: str) -> list[str]:
    """Return a list of file paths inside a repository directory.

    Args:
        directory: Repository-relative directory path (e.g. ``"prompts"``).

    Returns:
        Sorted list of repository-relative file paths.

    Raises:
        httpx.HTTPStatusError: If the GitHub API returns a non-2xx response.
    """
    settings = get_settings()
    url = f"{_GITHUB_API}/repos/{settings.github_repo}/contents/{directory}"
    params = {"ref": settings.github_branch}
    headers = {"Accept": "application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    response = httpx.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    entries = response.json()
    return sorted(entry["path"] for entry in entries if entry["type"] == "file")
