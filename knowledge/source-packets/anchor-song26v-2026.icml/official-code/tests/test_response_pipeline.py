"""Offline tests for the response processing pipeline."""

import json

import pytest

from ablation.scripts.response_pipeline import (
    ResponseEnricher,
    ResponseLogger,
    ResponseValidator,
    create_pipeline,
)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"instruction": "", "harmful": False, "confidence": 0.5, "reasoning": "ok"},
        {"instruction": "x", "harmful": "no", "confidence": 0.5, "reasoning": "ok"},
        {"instruction": "x", "harmful": False, "confidence": "high", "reasoning": "ok"},
        {"instruction": "x", "harmful": False, "confidence": 2, "reasoning": "ok"},
        {"instruction": "x", "harmful": False, "confidence": 0.5, "reasoning": ""},
    ],
)
def test_harm_assessment_validator_rejects_invalid_inputs(kwargs: dict) -> None:
    valid, errors = ResponseValidator.validate_harm_assessment(**kwargs)
    assert not valid
    assert errors


def test_strategy_validator_requires_string_alternatives() -> None:
    valid, errors = ResponseValidator.validate_strategy_selection(
        "instruction", "selected", ["valid", 2], 0.5, "reason"
    )
    assert not valid
    assert "alternatives must be a list of strings" in errors


@pytest.mark.parametrize(
    ("confidence", "level"),
    [(0.49, "low"), (0.5, "moderate"), (0.7, "high"), (0.9, "very_high")],
)
def test_enricher_confidence_levels(confidence: float, level: str) -> None:
    enriched = ResponseEnricher().enrich_harm_assessment({"confidence": confidence})
    assert enriched["confidence_level"] == level


def test_enricher_adds_context_without_mutating_source() -> None:
    source = {"confidence": 0.7}
    enriched = ResponseEnricher().enrich_harm_assessment(source, {"case": 1})
    assert enriched["context"] == {"case": 1}
    assert "context" not in source


def test_strategy_enricher_and_handler_registration() -> None:
    enricher = ResponseEnricher()
    handler = lambda value: value
    enricher.register_handler("custom", handler)
    assert enricher.enrichment_handlers["custom"] is handler
    assert enricher.enrich_strategy_selection(
        {"selected": "a"}, {"source": "catalog"}
    ) == {"selected": "a", "strategy_metadata": {"source": "catalog"}}


def test_harm_pipeline_success_and_metadata(tmp_path) -> None:
    pipeline = create_pipeline("agent", "model", tmp_path)
    result = pipeline.process_harm_assessment(
        "Review a benign configuration",
        False,
        0.95,
        "The operation is read-only.",
        log=False,
    )
    assert pipeline.is_success(result)
    assert result.metadata["instruction_length"] == len("Review a benign configuration")
    assert result.metadata["confidence"] == 0.95
    assert result.parsed_output["confidence_level"] == "very_high"


def test_harm_pipeline_returns_validation_failure_without_raising(tmp_path) -> None:
    result = create_pipeline(log_dir=tmp_path).process_harm_assessment(
        "", False, 0.5, "Reason", log=False
    )
    assert not result.success
    assert result.xml_string == ""
    assert "instruction must be a non-empty string" in result.validation_errors


def test_harm_pipeline_returns_formatting_failure(tmp_path, monkeypatch) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    monkeypatch.setattr(
        pipeline.formatter,
        "format_harm_assessment",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("format failed")),
    )
    result = pipeline.process_harm_assessment(
        "Review", False, 0.5, "Reason", log=False
    )
    assert not result.success
    assert result.validation_errors == ["Formatting error: format failed"]


def test_harm_pipeline_returns_xml_validation_failure(tmp_path, monkeypatch) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    monkeypatch.setattr(pipeline.formatter, "format_harm_assessment", lambda **kwargs: "xml")
    monkeypatch.setattr(pipeline.formatter, "validate", lambda xml: (False, ["bad xml"], ["warning"]))
    result = pipeline.process_harm_assessment(
        "Review", False, 0.5, "Reason", log=False
    )
    assert not result.success
    assert result.xml_string == "xml"
    assert result.validation_errors == ["bad xml"]
    assert result.validation_warnings == ["warning"]


def test_harm_pipeline_returns_parsing_failure(tmp_path, monkeypatch) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    monkeypatch.setattr(pipeline.formatter, "parse", lambda xml: (_ for _ in ()).throw(ValueError("bad parse")))
    result = pipeline.process_harm_assessment(
        "Review", False, 0.5, "Reason", log=False
    )
    assert not result.success
    assert result.is_valid
    assert result.validation_errors == ["Parsing error: bad parse"]


def test_strategy_pipeline_round_trip(tmp_path) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    result = pipeline.process_strategy_selection(
        "Choose a review method",
        "static-analysis",
        ["manual-review", "unit-tests"],
        0.8,
        "Static analysis is repeatable.",
        log=False,
    )
    assert pipeline.is_success(result)
    assert result.metadata["strategies_evaluated"] == 3
    attrs = result.parsed_output["decision"]["@attributes"]
    assert attrs["type"] == "strategy_selection"


def test_pipeline_accessors(tmp_path) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    result = pipeline.process_harm_assessment("Review", False, 0.5, "Reason", log=False)
    assert pipeline.get_xml_string(result) == result.xml_string
    assert pipeline.get_parsed_output(result) == result.parsed_output


def test_logger_writes_json_lines(tmp_path) -> None:
    pipeline = create_pipeline(log_dir=tmp_path)
    result = pipeline.process_harm_assessment(
        "Review", False, 0.6, "Read-only", log=True
    )
    entries = [json.loads(line) for line in pipeline.logger.log_file.read_text().splitlines()]
    assert entries == [
        {
            "timestamp": entries[0]["timestamp"],
            "request_type": "harm_assessment",
            "success": True,
            "is_valid": True,
            "validation_errors": [],
            "validation_warnings": [],
            "xml_length": len(result.xml_string),
        }
    ]


def test_logger_records_errors_and_context(tmp_path) -> None:
    logger = ResponseLogger(tmp_path)
    logger.log_error("failure", "test", {"case": 1})
    entry = json.loads(logger.log_file.read_text())
    assert entry["level"] == "error"
    assert entry["context"] == {"case": 1}
