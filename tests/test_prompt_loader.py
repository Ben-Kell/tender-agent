"""Tests for app.prompt_loader."""

import pytest

from app.prompt_loader import list_prompts, load_prompt


def test_load_system_instructions():
    content = load_prompt("system_instructions")
    assert "tender" in content.lower()


def test_load_extract_requirements():
    content = load_prompt("extract_requirements")
    assert "REQ-" in content or "requirement" in content.lower()


def test_load_map_template():
    content = load_prompt("map_template")
    assert "template" in content.lower() or "section" in content.lower()


def test_load_draft_sections():
    content = load_prompt("draft_sections")
    assert "draft" in content.lower() or "section" in content.lower()


def test_load_qa_review():
    content = load_prompt("qa_review")
    assert "review" in content.lower() or "compliance" in content.lower()


def test_load_missing_prompt_raises():
    with pytest.raises(FileNotFoundError):
        load_prompt("nonexistent_prompt")


def test_list_prompts_returns_known_prompts():
    prompts = list_prompts()
    expected = {
        "system_instructions",
        "extract_requirements",
        "map_template",
        "draft_sections",
        "qa_review",
    }
    assert expected.issubset(set(prompts))


def test_list_prompts_sorted():
    prompts = list_prompts()
    assert prompts == sorted(prompts)
