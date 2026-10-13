import json

import pytest

from llm_discussion.answers import normalize_number, parse_answer
from llm_discussion.data import load_tasks, read_json_records


@pytest.mark.parametrize("raw, expected", [
    ("-1,234.500", "-1234.5"), ("+.50", "0.5"), ("-0.000", "0"),
    ("42.00", "42"), (123, "123"), (0.25, "0.25"), ("1e3", "1000"),
    ("123456789012345678901234567890.1200", "123456789012345678901234567890.12"),
])
def test_numeric_normalization(raw, expected):
    assert normalize_number(raw) == expected


@pytest.mark.parametrize("raw", [
    "", " ", "1,23", "12,3456", "1,000,00", "NaN", "Infinity", "20%", "$20",
    "20 dollars", True, None, float("inf"), float("nan"), "1/2", "1 000",
])
def test_rejects_non_numbers(raw):
    with pytest.raises(ValueError):
        normalize_number(raw)


@pytest.mark.parametrize("raw, expected", [
    ('```json\n{"reasons":"subtract", "answer":"-42.00"}\n```', "-42"),
    ('{"reasons":"count", "answer":1234.5}', "1234.5"),
    ('{"reasons": "subtract", "answer": "-1,200"}', "-1200"),
    ('{"reasons":"exact", "answer":0.12345678901234567890123456789}', "0.12345678901234567890123456789"),
])
def test_parse_explicit_answer(raw, expected):
    answer = parse_answer(raw)
    assert answer.value == expected
    assert answer.raw == raw


@pytest.mark.parametrize("raw", [
    "There were 12 ducks and the answer is 42.",
    '{"answer":""}', '{"answer":true}', '{"answer":"42%"}',
    '{"answer":"12"} or {"answer":"13"}',
    '{"answer":"12", "answer":"13"}',
    '{"answer":12 ducks}', '{"answer":1,234}',
    '{"answer":"12", "reasons":null}',
    '{"reasons": "broken "quote"", "answer": "12"}',
])
def test_parse_does_not_guess_or_accept_ambiguous_values(raw):
    with pytest.raises(ValueError):
        parse_answer(raw)


def test_load_gsm8k_preserves_negative_reference_and_discards_reasoning(tmp_path):
    path = tmp_path / "gsm8k.jsonl"
    path.write_text(json.dumps({"question": "What is 2 - 3?", "answer": "Private gold steps.\n#### -1"}) + "\n")
    task, = load_tasks(path)
    assert task.id == "0"
    assert task.reference == "-1"
    assert task.question == "What is 2 - 3?"


def test_load_generic_tasks(tmp_path):
    path = tmp_path / "tasks.jsonl"
    records = [{"id": "negative", "question": "Q", "reference": "-1,200.0"},
               {"id": 9, "question": "Another Q"}]
    path.write_text("\n".join(json.dumps(record) for record in records))
    assert read_json_records(path) == records
    assert [task.reference for task in load_tasks(path)] == ["-1200", None]


@pytest.mark.parametrize("records", [
    [{"id": 1, "question": "Q"}, {"id": "1", "question": "Q2"}],
    [{"question": ""}], [{"question": "Q", "reference": "20%"}],
    [{"question": "Q", "answer": "not a GSM8K label"}],
    [{"id": True, "question": "Q"}], [],
])
def test_invalid_tasks_fail_before_execution(tmp_path, records):
    path = tmp_path / "bad.jsonl"
    path.write_text("\n".join(json.dumps(record) for record in records))
    with pytest.raises(ValueError):
        load_tasks(path)


def test_truncated_records_are_not_silently_dropped(tmp_path):
    path = tmp_path / "broken.jsonl"
    path.write_text('{"id": 1}\n{"id":')
    with pytest.raises(ValueError, match="invalid JSON at line 2"):
        read_json_records(path)
