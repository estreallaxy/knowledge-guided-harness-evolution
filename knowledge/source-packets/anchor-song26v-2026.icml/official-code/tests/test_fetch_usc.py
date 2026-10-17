"""Tests for USC HTML extraction without external HTTP calls."""

import json

import pytest
import requests

from task_construction.fetch_usc import fetch_usc_content, save_usc_content_json


class FakeResponse:
    def __init__(self, text: str = "", status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            error = requests.HTTPError(f"status {self.status_code}")
            error.response = self
            raise error


def test_fetch_usc_extracts_title_and_statute(monkeypatch) -> None:
    html = """
    <html><h1>§ 123—Records review</h1>
      <div class="field-items">Navigation (a) Review all records. (b) File results.
      Editorial Notes Ignore this.</div>
    </html>
    """
    monkeypatch.setattr("task_construction.fetch_usc.requests.get", lambda *a, **k: FakeResponse(html))
    result = fetch_usc_content(18, 123)
    assert result["section_name"] == "Records review"
    assert result["section_definition"] == "(a) Review all records. (b) File results."


def test_fetch_usc_falls_back_to_content_area(monkeypatch) -> None:
    html = """
    <html><h3 class="section-head">§ 55 - Filing</h3>
      <div id="content"><nav>Skip</nav><p>(a) File annually.</p></div>
    </html>
    """
    monkeypatch.setattr("task_construction.fetch_usc.requests.get", lambda *a, **k: FakeResponse(html))
    result = fetch_usc_content(1, 55)
    assert result == {"section_name": "Filing", "section_definition": "(a) File annually."}


def test_fetch_usc_returns_distinct_404(monkeypatch) -> None:
    monkeypatch.setattr(
        "task_construction.fetch_usc.requests.get",
        lambda *a, **k: FakeResponse(status_code=404),
    )
    assert fetch_usc_content(1, 999) == {"error": "404", "message": "Section not found"}


def test_fetch_usc_reports_request_errors(monkeypatch) -> None:
    def fail(*args, **kwargs):
        raise requests.Timeout("slow")

    monkeypatch.setattr("task_construction.fetch_usc.requests.get", fail)
    assert "slow" in fetch_usc_content(1, 1)["error"]


def test_save_usc_content_json_adds_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    content = {"section_name": "Filing", "section_definition": "Text"}
    path = save_usc_content_json(1, 55, content)
    saved = json.loads((tmp_path / path).read_text())
    assert saved == {
        "section_name": "Filing",
        "section_definition": "Text",
        "title": 1,
        "section": 55,
        "source": "https://www.law.cornell.edu/uscode/text/1/55",
    }

