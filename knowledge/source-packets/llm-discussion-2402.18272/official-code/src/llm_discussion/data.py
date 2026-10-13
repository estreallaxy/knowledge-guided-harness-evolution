"""Dataset loading with no model calls or application initialization."""

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .answers import normalize_answer
from .types import Task


def read_json_records(path: Path) -> list[dict[str, Any]]:
    """Read one JSON object per nonempty line, with useful location errors."""
    records = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path}: invalid JSON at line {line_number}, column {exc.colno}"
            ) from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}: line {line_number} must be an object")
        records.append(value)
    return records


def _images(values, path: Path) -> tuple[str, ...]:
    if not isinstance(values, list):
        raise ValueError("images must be an array of local paths or HTTP(S) URLs")
    resolved = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("each image must be a nonempty path or URL")
        url = urlsplit(value)
        if url.scheme in ("http", "https") and url.netloc:
            resolved.append(value)
        elif url.scheme:
            raise ValueError("images must use local paths or HTTP(S) URLs")
        else:
            image = (path.parent / value).resolve()
            if not image.is_file():
                raise ValueError(f"image does not exist: {image}")
            resolved.append(str(image))
    return tuple(resolved)


def load_tasks(path: Path) -> list[Task]:
    """Load GSM8K or generic numeric/choice tasks, optionally containing images.

    Gold reasoning is discarded. The reference is evaluation metadata and must
    never be supplied to a model as part of a prompt.
    """
    path = Path(path)
    tasks = []
    seen = set()
    for index, record in enumerate(read_json_records(path)):
        task_id = record.get("id", index)
        if isinstance(task_id, bool) or not isinstance(task_id, (str, int)):
            raise ValueError(f"{path}: record {index + 1} has an invalid id")
        task_id = str(task_id)
        if not task_id.strip() or task_id in seen:
            raise ValueError(f"{path}: empty or duplicate task id {task_id!r}")
        question = record.get("question")
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"{path}: task {task_id} requires a nonempty question")
        answer_type = record.get("answer_type", "number")
        if answer_type not in ("number", "choice"):
            raise ValueError(f"{path}: task {task_id}: answer_type must be number or choice")
        options = record.get("options", [])
        if not isinstance(options, list) or any(not isinstance(v, str) or not v.strip() for v in options):
            raise ValueError(f"{path}: task {task_id}: options must be an array of nonempty strings")
        if (answer_type == "choice" and not 2 <= len(options) <= 26) or (answer_type == "number" and options):
            raise ValueError(f"{path}: task {task_id}: choice tasks require 2–26 options; numeric tasks have none")
        category = record.get("category")
        if category is not None and (not isinstance(category, str) or not category.strip()):
            raise ValueError(f"{path}: task {task_id}: category must be a nonempty string")
        metric = record.get("metric", "exact")
        if metric not in ("exact", "mra") or (metric == "mra" and answer_type != "number"):
            raise ValueError(f"{path}: task {task_id}: metric must be exact, or mra for numeric tasks")
        images = _images(record.get("images", []), path)
        reference = record.get("reference")
        if "reference" not in record and "answer" in record:
            gold = record["answer"]
            if answer_type == "choice":
                reference = gold
            elif not isinstance(gold, str) or gold.count("####") != 1:
                raise ValueError(f"{path}: task {task_id} requires a GSM8K #### answer")
            else:
                reference = gold.split("####", 1)[1].strip()
        if reference is not None:
            try:
                choices = tuple(chr(ord("A") + i) for i in range(len(options)))
                reference = normalize_answer(reference, answer_type, choices)
            except ValueError as exc:
                raise ValueError(f"{path}: task {task_id}: {exc}") from exc
        tasks.append(Task(task_id, question, reference, images, tuple(options), answer_type, category, metric))
        seen.add(task_id)
    if not tasks:
        raise ValueError(f"{path}: dataset has no tasks")
    return tasks
