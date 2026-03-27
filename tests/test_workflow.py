"""Tests for app.workflow helper functions."""

from app.workflow import _parse_qa_report, _split_markdown_sections
from app.models import DraftSection, QAReport


class TestSplitMarkdownSections:
    def test_splits_on_double_hash_headings(self):
        text = "## Introduction\n\nIntro content.\n\n## Methods\n\nMethod content."
        sections = _split_markdown_sections(text)
        assert len(sections) == 2
        assert sections[0].section == "Introduction"
        assert sections[0].content == "Intro content."
        assert sections[1].section == "Methods"
        assert sections[1].content == "Method content."

    def test_ignores_content_before_first_heading(self):
        text = "Preamble text.\n\n## Section One\n\nContent one."
        sections = _split_markdown_sections(text)
        assert len(sections) == 1
        assert sections[0].section == "Section One"

    def test_returns_empty_list_when_no_headings(self):
        text = "No headings here, just plain prose."
        sections = _split_markdown_sections(text)
        assert sections == []

    def test_single_heading(self):
        text = "## Only Section\n\nOnly content."
        sections = _split_markdown_sections(text)
        assert len(sections) == 1
        assert sections[0].section == "Only Section"

    def test_section_with_nested_headings_in_content(self):
        text = "## Top\n\n### Sub-heading\n\nSub content.\n\n## Next\n\nNext content."
        sections = _split_markdown_sections(text)
        assert len(sections) == 2
        assert "### Sub-heading" in sections[0].content

    def test_returns_draft_section_instances(self):
        text = "## Alpha\n\nContent A."
        sections = _split_markdown_sections(text)
        assert all(isinstance(s, DraftSection) for s in sections)


class TestParseQaReport:
    _SAMPLE_REPORT = """\
# QA Review Report

## Passed checks

- All mandatory requirements are addressed
- Response follows format restrictions

## Failed checks

- Pricing schedule is incomplete
- Section 3.2 lacks supporting evidence

## Risk flags

- Section 4.1 makes unsubstantiated capability claims
"""

    def test_parses_passed_checks(self):
        report = _parse_qa_report(self._SAMPLE_REPORT)
        assert "All mandatory requirements are addressed" in report.passed
        assert "Response follows format restrictions" in report.passed

    def test_parses_failed_checks(self):
        report = _parse_qa_report(self._SAMPLE_REPORT)
        checks = [f["check"] for f in report.failed]
        assert "Pricing schedule is incomplete" in checks
        assert "Section 3.2 lacks supporting evidence" in checks

    def test_parses_risk_flags(self):
        report = _parse_qa_report(self._SAMPLE_REPORT)
        assert any("4.1" in flag for flag in report.risk_flags)

    def test_returns_qa_report_instance(self):
        report = _parse_qa_report(self._SAMPLE_REPORT)
        assert isinstance(report, QAReport)

    def test_fallback_when_no_sections_match(self):
        text = "Everything is fine."
        report = _parse_qa_report(text)
        # When nothing can be parsed, the raw text is preserved in risk_flags.
        assert text in report.risk_flags
        assert report.passed == []
        assert report.failed == []

    def test_empty_input_fallback(self):
        report = _parse_qa_report("")
        assert report.passed == []
        assert report.failed == []
