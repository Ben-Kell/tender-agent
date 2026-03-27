"""Tests for app.models."""

import pytest
from pydantic import ValidationError

from app.models import DraftSection, QAReport, Requirement, TemplateMapping


class TestRequirement:
    def test_valid_mandatory(self):
        req = Requirement(
            id="REQ-001",
            clause="3.1.2",
            text="The respondent must demonstrate experience.",
            category="Mandatory",
            evaluation_criterion="Technical Capability",
        )
        assert req.id == "REQ-001"
        assert req.category == "Mandatory"
        assert req.evaluation_criterion == "Technical Capability"

    def test_optional_evaluation_criterion_defaults_to_none(self):
        req = Requirement(
            id="REQ-002",
            clause="4.1",
            text="Desirable experience.",
            category="Desirable",
        )
        assert req.evaluation_criterion is None

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            Requirement(
                id="REQ-003",
                clause="1.0",
                text="Some text.",
                category="Unknown",
            )

    def test_all_categories_accepted(self):
        for cat in ("Mandatory", "Desirable", "Informational"):
            req = Requirement(id="R", clause="1", text="t", category=cat)
            assert req.category == cat


class TestTemplateMapping:
    def test_valid_mapping(self):
        mapping = TemplateMapping(
            requirement_id="REQ-001",
            template_section="2.1 Technical Approach",
            notes="Address capability here.",
        )
        assert mapping.requirement_id == "REQ-001"
        assert mapping.notes == "Address capability here."

    def test_notes_optional(self):
        mapping = TemplateMapping(
            requirement_id="REQ-002",
            template_section="4.1 Corporate Overview",
        )
        assert mapping.notes is None


class TestDraftSection:
    def test_valid_draft(self):
        draft = DraftSection(section="2.1 Technical Approach", content="Our approach is...")
        assert draft.section == "2.1 Technical Approach"
        assert "approach" in draft.content


class TestQAReport:
    def test_valid_report(self):
        report = QAReport(
            passed=["All mandatory requirements addressed"],
            failed=[{"check": "Pricing schedule", "note": "Missing detail"}],
            risk_flags=["Section 3.2 makes unsubstantiated claims"],
        )
        assert len(report.passed) == 1
        assert len(report.failed) == 1
        assert len(report.risk_flags) == 1

    def test_empty_report(self):
        report = QAReport(passed=[], failed=[], risk_flags=[])
        assert report.passed == []
