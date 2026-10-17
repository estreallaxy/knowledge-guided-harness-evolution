"""Tests for XML response formatting, validation, and parsing."""

import xml.etree.ElementTree as ET

import pytest

from ablation.scripts.xml_response_formatter import (
    ResponseType,
    XMLResponseFormatter,
    XMLValidator,
    format_harm_check,
    validate_response,
)


@pytest.fixture
def formatter() -> XMLResponseFormatter:
    return XMLResponseFormatter(agent_id="test-agent", model_version="test-model")


def test_schema_template_contains_requested_response_type() -> None:
    xml = format_harm_check("Inspect a report", False, 0.8, "Routine review")
    root = ET.fromstring(xml)
    assert root.findtext("metadata/response_type") == "harm_assessment"
    assert root.find("decision").attrib == {
        "type": "harm_assessment",
        "confidence": "0.80",
    }


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_formatter_rejects_out_of_range_confidence(
    formatter: XMLResponseFormatter, confidence: float
) -> None:
    with pytest.raises(ValueError, match=r"Confidence must be in \[0, 1\]"):
        formatter.format_harm_assessment("Review", False, confidence, "Reason")


@pytest.mark.parametrize("confidence", [0.0, 0.25, 1.0])
def test_formatter_accepts_confidence_boundaries(
    formatter: XMLResponseFormatter, confidence: float
) -> None:
    xml = formatter.format_harm_assessment("Review", False, confidence, "Reason")
    assert ET.fromstring(xml).find("decision").get("confidence") == f"{confidence:.2f}"


def test_special_characters_round_trip(formatter: XMLResponseFormatter) -> None:
    instruction = "Compare A&B with <draft> and 'final'"
    reasoning = 'The "draft" is safe & reviewable.'
    xml = formatter.format_harm_assessment(
        instruction, False, 0.7, reasoning, harm_type="review & approval"
    )
    root = ET.fromstring(xml)
    assert root.findtext("decision/instruction") == instruction
    assert root.findtext("decision/harm_type") == "review & approval"
    assert root.findtext("evidence/reasoning") == reasoning


def test_sources_and_result_data_are_structured(formatter: XMLResponseFormatter) -> None:
    xml = formatter.format_auditor_decision(
        ResponseType.EVALUATION,
        {"status": "pass"},
        "Evidence checked",
        sources=[{"type": "file", "reference": "report & notes.txt"}],
        result_data={"count": 3},
    )
    root = ET.fromstring(xml)
    source = root.find("evidence/sources/source")
    assert source.attrib == {"type": "file", "reference": "report & notes.txt"}
    assert root.findtext("output/result_data/count") == "3"


def test_response_ids_increment(formatter: XMLResponseFormatter) -> None:
    first = formatter.format_harm_assessment("One", False, 0.5, "Reason")
    second = formatter.format_harm_assessment("Two", False, 0.5, "Reason")
    assert ET.fromstring(first).get("id") == "resp_1"
    assert ET.fromstring(second).get("id") == "resp_2"


def test_parse_preserves_repeated_sources(formatter: XMLResponseFormatter) -> None:
    xml = formatter.format_harm_assessment(
        "Review",
        False,
        0.9,
        "Reason",
        sources=[
            {"type": "file", "reference": "a.txt"},
            {"type": "file", "reference": "b.txt"},
        ],
    )
    parsed = formatter.parse(xml)
    sources = parsed["evidence"]["sources"]["source"]
    assert isinstance(sources, list)
    assert [item["@attributes"]["reference"] for item in sources] == ["a.txt", "b.txt"]


def test_parse_rejects_malformed_xml(formatter: XMLResponseFormatter) -> None:
    with pytest.raises(ValueError, match="Invalid XML"):
        formatter.parse("<auditor_response>")


@pytest.mark.parametrize(
    ("xml", "error_fragment"),
    [
        ("<wrong />", "Invalid root tag"),
        ("<auditor_response />", "Missing required element"),
        (
            "<auditor_response><metadata/><decision type='x' confidence='2'/>"
            "<evidence/><output/></auditor_response>",
            "Confidence out of range",
        ),
        (
            "<auditor_response><metadata/><decision type='x' confidence='many'/>"
            "<evidence/><output/></auditor_response>",
            "Confidence is not numeric",
        ),
    ],
)
def test_validator_reports_structural_errors(xml: str, error_fragment: str) -> None:
    valid, errors, _ = XMLValidator().validate(xml)
    assert not valid
    assert any(error_fragment in error for error in errors)


def test_validator_warns_for_missing_evidence_children() -> None:
    xml = """<auditor_response>
      <metadata><schema_version>1</schema_version><timestamp>x</timestamp>
        <agent_id>a</agent_id><model_version>m</model_version>
        <response_type>evaluation</response_type></metadata>
      <decision type="evaluation" confidence="0.5"/><evidence/><output/>
    </auditor_response>"""
    valid, errors, warnings = validate_response(xml)
    assert valid
    assert errors == []
    assert set(warnings) == {
        "Missing reasoning in evidence section",
        "Missing sources in evidence section",
    }

