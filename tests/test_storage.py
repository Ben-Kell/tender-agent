"""Tests for app.storage."""

import json
import pytest

from app import storage


@pytest.fixture()
def tmp_tenders(tmp_path, monkeypatch):
    """Redirect TENDERS_DIR to a temporary directory for isolation."""
    monkeypatch.setattr(storage, "TENDERS_DIR", tmp_path)
    return tmp_path


class TestGetTenderDir:
    def test_returns_correct_path(self, tmp_tenders):
        path = storage.get_tender_dir("RFT-999")
        assert path == tmp_tenders / "RFT-999"


class TestReadInputFiles:
    def test_returns_empty_when_no_input_dir(self, tmp_tenders):
        result = storage.read_input_files("RFT-MISSING")
        assert result == {}

    def test_reads_txt_and_md_files(self, tmp_tenders):
        rft_id = "RFT-001"
        input_dir = tmp_tenders / rft_id / "input"
        input_dir.mkdir(parents=True)
        (input_dir / "tender.txt").write_text("Tender text.", encoding="utf-8")
        (input_dir / "notes.md").write_text("# Notes", encoding="utf-8")

        result = storage.read_input_files(rft_id)
        assert set(result.keys()) == {"tender.txt", "notes.md"}
        assert result["tender.txt"] == "Tender text."
        assert result["notes.md"] == "# Notes"

    def test_skips_non_text_files(self, tmp_tenders):
        rft_id = "RFT-002"
        input_dir = tmp_tenders / rft_id / "input"
        input_dir.mkdir(parents=True)
        (input_dir / "tender.pdf").write_bytes(b"%PDF-1.4 binary content")
        (input_dir / "notes.txt").write_text("Plain text.", encoding="utf-8")

        result = storage.read_input_files(rft_id)
        assert "tender.pdf" not in result
        assert result["notes.txt"] == "Plain text."


class TestSaveOutput:
    def test_creates_output_directory_and_file(self, tmp_tenders):
        path = storage.save_output("RFT-003", "draft.md", "# Draft")
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "# Draft"

    def test_returns_correct_path(self, tmp_tenders):
        path = storage.save_output("RFT-004", "output.txt", "hello")
        assert path == tmp_tenders / "RFT-004" / "output" / "output.txt"


class TestSaveJson:
    def test_saves_valid_json(self, tmp_tenders):
        data = [{"id": "REQ-001", "text": "Requirement one"}]
        path = storage.save_json("RFT-005", "requirements.json", data)
        assert path.exists()
        parsed = json.loads(path.read_text(encoding="utf-8"))
        assert parsed == data


class TestLoadJson:
    def test_loads_saved_json(self, tmp_tenders):
        rft_id = "RFT-006"
        data = {"key": "value"}
        storage.save_json(rft_id, "test.json", data)
        loaded = storage.load_json(rft_id, "test.json")
        assert loaded == data

    def test_raises_if_file_missing(self, tmp_tenders):
        with pytest.raises(FileNotFoundError):
            storage.load_json("RFT-007", "nonexistent.json")
