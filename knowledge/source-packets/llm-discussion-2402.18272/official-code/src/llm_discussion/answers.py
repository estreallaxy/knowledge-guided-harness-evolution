"""Parse explicit answers without guessing numbers from a reasoning trace."""

import json
import math
import re
from decimal import Decimal, InvalidOperation

from .types import Answer


_NUMBER = re.compile(
    r"[+-]?(?:(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]*)?|\.[0-9]+)"
    r"(?:[eE][+-]?[0-9]+)?\Z"
)
_JSON_FENCE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE)


def normalize_number(value: str | int | float) -> str:
    """Return an exact, finite decimal spelling; reject units and malformed groups."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("answer must be a number or numeric string")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("answer must be finite")
    text = str(value).strip()
    if not _NUMBER.fullmatch(text):
        raise ValueError(f"invalid numeric answer: {text!r}")
    try:
        number = Decimal(text.replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError(f"invalid numeric answer: {text!r}") from exc
    if not number.is_finite():
        raise ValueError("answer must be finite")
    # Avoid Decimal.normalize(): the active decimal context can round long values.
    if number == 0:
        return "0"
    result = format(number, "f")
    return result.rstrip("0").rstrip(".") if "." in result else result


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def normalize_choice(value: str, choices: tuple[str, ...] = ()) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z]", value.strip()):
        raise ValueError("choice answer must be a single option letter")
    label = value.strip().upper()
    if choices and label not in choices:
        raise ValueError("choice answer is not one of the available options")
    return label


def normalize_answer(value, answer_type: str = "number", choices: tuple[str, ...] = ()) -> str:
    if answer_type == "number":
        return normalize_number(value)
    if answer_type == "choice":
        return normalize_choice(value, choices)
    raise ValueError("answer_type must be number or choice")


def parse_answer(text: str, answer_type: str = "number", choices: tuple[str, ...] = ()) -> Answer:
    """Read the requested JSON answer, optionally inside a Markdown code fence.

    Invalid JSON is reported instead of repairing it or guessing from reasoning.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("model response is empty")
    body = text.strip()
    fence = _JSON_FENCE.fullmatch(body)
    if fence:
        body = fence.group(1)
    try:
        record = json.loads(body, parse_float=str, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError("model response must be a JSON object with an answer field") from exc
    if not isinstance(record, dict) or "answer" not in record:
        raise ValueError("model response must contain an answer field")
    explanation = record.get("reasons", "")
    if not isinstance(explanation, str):
        raise ValueError("reasons must be a string")
    return Answer(normalize_answer(record["answer"], answer_type, choices), explanation, text)
