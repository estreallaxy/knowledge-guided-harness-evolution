"""Rubric-based visual evaluation for Photoshop benchmark tasks.

The judge receives only the task instruction, a task-specific rubric, the
starting image, and the candidate result. Reference end images are deliberately
excluded from real evaluations; they are used only while authoring/calibrating
rubrics.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image
import requests

logger = logging.getLogger("photoshop_evaluator")


class PhotoshopEvaluator:
    """Evaluate a rendered result with task-specific, all-or-nothing rubrics."""

    def __init__(
        self,
        task_folder: str,
        result_folder: str,
        task_config: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.task_folder = Path(task_folder).resolve()
        self.result_folder = Path(result_folder).resolve()
        self.task_config = task_config or self._load_task_config()
        self.task_id = str(self.task_config.get("id", self.task_folder.name))
        self.model = model or os.getenv("PSBENCH_JUDGE_MODEL", "gpt-5.4")
        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("PSBENCH_JUDGE_API_KEY")
        )
        self.base_url = base_url or os.getenv(
            "PSBENCH_JUDGE_BASE_URL", "https://api.openai.com/v1"
        )

    def _load_task_config(self) -> Dict[str, Any]:
        preferred = self.task_folder / f"{self.task_folder.name}.json"
        candidates = [preferred] if preferred.exists() else sorted(self.task_folder.glob("*.json"))
        candidates = [path for path in candidates if not path.name.endswith("_rubric.json")]
        if not candidates:
            raise FileNotFoundError(f"No task configuration found in {self.task_folder}")
        with candidates[0].open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _resolve_task_file(self, configured_name: Optional[str], role: str) -> Path:
        if not configured_name:
            raise ValueError(f"Task configuration does not specify the {role} image")
        path = (self.task_folder / configured_name).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"{role.capitalize()} image does not exist: {path}")
        return path

    def get_start_path(self) -> Path:
        return self._resolve_task_file(
            self.task_config.get("resources", {}).get("input_file"), "start"
        )

    def get_rubric_path(self) -> Path:
        configured = self.task_config.get("rubric_file")
        path = self.task_folder / (configured or f"{self.task_id}_rubric.json")
        if not path.is_file():
            raise FileNotFoundError(f"Task rubric does not exist: {path}")
        return path.resolve()

    def load_rubric(self) -> Dict[str, Any]:
        path = self.get_rubric_path()
        with path.open("r", encoding="utf-8") as handle:
            rubric = json.load(handle)
        criteria = rubric.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f"Rubric has no criteria: {path}")
        seen = set()
        for criterion in criteria:
            criterion_id = criterion.get("id")
            description = criterion.get("description")
            if not criterion_id or not description:
                raise ValueError(f"Invalid criterion in {path}: {criterion}")
            if criterion_id in seen:
                raise ValueError(f"Duplicate rubric criterion id '{criterion_id}' in {path}")
            seen.add(criterion_id)
        return rubric

    @staticmethod
    def _encode_image(path: Path) -> str:
        """Normalize an image to RGB PNG and return its base64 representation."""
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("ascii")

    @staticmethod
    def _image_metadata(path: Path) -> Dict[str, Any]:
        with Image.open(path) as image:
            return {
                "filename": path.name,
                "width_px": image.width,
                "height_px": image.height,
                "format": image.format,
            }

    def _build_messages(
        self, rubric: Dict[str, Any], start_path: Path, result_path: Path
    ) -> List[Dict[str, Any]]:
        criteria = [
            {"id": item["id"], "description": item["description"]}
            for item in rubric["criteria"]
        ]
        system_prompt = """You are a strict but practical visual judge for Photoshop tasks.
Judge only visible properties of the final rendered image. Do not require proof of
layers, masks, blend modes, adjustment layers, or the editing workflow. You receive
the original START image and the candidate RESULT image. You do not receive a
reference answer.

Evaluate every rubric criterion independently. A criterion passes only when the
visible result gives clear evidence that its full requirement is satisfied. Do not
penalize harmless aesthetic differences that are unrelated to the instruction.
Do not infer success merely because the image changed. If evidence is ambiguous,
mark the criterion false and explain exactly what cannot be verified.

Use the supplied original image dimensions when the task requests canvas or image
dimensions. For settings that cannot be recovered exactly from rendered pixels
(for example blur radius, adjustment percentage, layer opacity, or filter distance),
judge whether the visible direction and approximate strength are plausibly consistent;
do not fail solely because the exact UI value cannot be proven. Compare START and
RESULT carefully for subtle edits and accept a subtle but visible directional change.
Workflow-only clauses such as copying a layer or choosing a named blend mode are not
independently required when their exact internal use cannot be established visually;
judge the visible composite effect instead.

Do not demand exaggerated filter strength, perfectly hard region boundaries, exact
geometric centering, photorealistic compositing, or seamless aesthetics unless the
instruction explicitly requires them. Approximate placement in the named area is
sufficient. When START and RESULT show a small but directionally correct difference,
do not reject it merely for being subtle.

Return JSON only with this exact shape:
{
  "summary": "concise overall explanation",
  "criteria": [
    {"id": "criterion id", "passed": true, "reason": "visible evidence"}
  ]
}
Do not return numeric scores. Include exactly one result for every supplied
criterion and preserve each criterion id verbatim.
Write the summary and every criterion reason in English. Do not use any other
language. Keep criterion ids unchanged. For a failed criterion, state the concrete
visible evidence or the specific requested effect that cannot be verified from
RESULT."""
        if rubric.get("judge_policy") == "false_negative_calibrated":
            system_prompt += """

Task-specific calibration policy:
- This task belongs to a previously false-negative calibration set.
- PASS when RESULT contains a change reasonably consistent with the requested edit,
  including subtle, soft, localized, approximate, or naturally blended evidence.
- FAIL only when concrete visible evidence shows that the edit is absent, targets the
  clearly wrong subject/region, or changes in the opposite direction. Ambiguity about
  exact strength, method, boundary, or parameter is not by itself a failure.
- Scope phrases such as "focus on" or "pick an area" describe where the following
  effect applies. Do not require a visible selection outline or geometric boundary.
- Do not require textbook filter signatures or conspicuous effects at display scale.
"""
        elif rubric.get("judge_policy") == "reference_positive_calibrated":
            system_prompt += """

Task-specific positive-reference calibration policy:
- This rubric was calibrated with a known-good author-created result, but that
  reference image is not shown during evaluation. Apply a practical visual
  tolerance; do not assume that every candidate is correct.
- PASS when the dominant requested transformation is visibly present and the
  result is reasonably consistent with the instruction.
- For combined edits, judge their blended final appearance. Do not fail solely
  because one subtle component cannot be isolated after interacting edits.
- Numeric UI settings describe intended direction and approximate strength.
  Do not reject a visible correct-direction edit merely because it looks
  stronger or weaker than the stated number.
- Additional styling, hard selection boundaries, or localized rectangular or
  circular transitions are not failures unless the instruction explicitly
  prohibits them or they destroy the requested outcome.
- Fail only for a clearly absent dominant edit, the wrong target or region, an
  opposite transformation, incorrect required text, or a violated explicit
  preservation constraint.
- Rotation geometry reminder: after a 90-degree clockwise rotation, START's
  bottom edge appears on RESULT's left edge; after a 90-degree counterclockwise
  rotation, START's bottom edge appears on RESULT's right edge.
"""
        user_text = json.dumps(
            {
                "task_id": self.task_id,
                "instruction": self.task_config.get("instruction", ""),
                "rubric": criteria,
                "image_order": ["START", "RESULT"],
                "image_metadata": {
                    "START": self._image_metadata(start_path),
                    "RESULT": self._image_metadata(result_path),
                },
            },
            ensure_ascii=True,
            indent=2,
        )
        return [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "text", "text": "START image:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{self._encode_image(start_path)}",
                            "detail": "high",
                        },
                    },
                    {"type": "text", "text": "RESULT image:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{self._encode_image(result_path)}",
                            "detail": "high",
                        },
                    },
                ],
            },
        ]

    def _call_judge(
        self,
        messages: List[Dict[str, Any]],
        expected_criterion_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        if not self.base_url:
            raise RuntimeError("PSBENCH_JUDGE_BASE_URL is not configured")

        endpoint = self.base_url.rstrip("/") + "/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
        }
        if self.model.lower().startswith("gpt-5"):
            payload["max_completion_tokens"] = 4000
            payload["reasoning_effort"] = "medium"
        else:
            payload["temperature"] = 0
            payload["max_tokens"] = 1400
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=(30, 180),
                )
                if response.status_code >= 400:
                    body = response.text[:500]
                    if response.status_code == 400:
                        body_lower = body.lower()
                        if "response_format" in body_lower and "response_format" in payload:
                            payload.pop("response_format", None)
                            continue
                        if "reasoning_effort" in body_lower and "reasoning_effort" in payload:
                            payload.pop("reasoning_effort", None)
                            continue
                        if "max_completion_tokens" in body_lower and "max_completion_tokens" in payload:
                            payload["max_tokens"] = payload.pop("max_completion_tokens")
                            continue
                    raise RuntimeError(f"Judge HTTP {response.status_code}: {body}")
                content = response.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if expected_criterion_ids is not None:
                    criteria = parsed.get("criteria")
                    if not isinstance(criteria, list):
                        raise RuntimeError("The judge did not return a criteria list.")
                    returned_ids = [
                        item.get("id")
                        for item in criteria
                        if isinstance(item, dict)
                    ]
                    missing_ids = [
                        criterion_id
                        for criterion_id in expected_criterion_ids
                        if criterion_id not in returned_ids
                    ]
                    if missing_ids:
                        raise RuntimeError(
                            "The judge omitted required criterion results: "
                            + ", ".join(missing_ids)
                        )
                report_text = json.dumps(parsed, ensure_ascii=False)
                try:
                    report_text.encode("ascii")
                except UnicodeEncodeError as error:
                    raise RuntimeError(
                        "The judge returned non-ASCII report text. "
                        "Evaluation reports must be written in English using ASCII characters."
                    ) from error
                return parsed
            except Exception as exc:
                last_error = exc
                logger.warning("Judge request attempt %s failed: %s", attempt + 1, exc)
        raise RuntimeError(f"{self.model} judge failed after 3 attempts: {last_error}")

    @staticmethod
    def _normalize_report(raw: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
        expected = {item["id"]: item for item in rubric["criteria"]}
        received: Dict[str, Dict[str, Any]] = {}
        for item in raw.get("criteria", []):
            if isinstance(item, dict) and item.get("id") in expected:
                received[item["id"]] = item

        criteria_report = []
        for criterion_id, criterion in expected.items():
            item = received.get(criterion_id)
            passed = bool(item and item.get("passed") is True)
            reason = (
                str(item.get("reason", "")).strip()
                if item
                else "The judge did not return a result for this required criterion."
            )
            if not reason:
                reason = "The judge returned no supporting explanation."
                passed = False
            criteria_report.append(
                {
                    "id": criterion_id,
                    "description": criterion["description"],
                    "passed": passed,
                    "reason": reason,
                }
            )

        failed = [item for item in criteria_report if not item["passed"]]
        return {
            "passed": not failed,
            "summary": str(raw.get("summary", "")).strip()
            or ("All rubric criteria passed." if not failed else "One or more rubric criteria failed."),
            "criteria": criteria_report,
            "failed_requirements": [item["description"] for item in failed],
        }

    def _save_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        self.result_folder.mkdir(parents=True, exist_ok=True)
        report_path = self.result_folder / f"evaluation_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        report["report_file"] = str(report_path)
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=True, indent=2)
            handle.write("\n")
        return report

    def evaluate(self, result_path: str) -> Dict[str, Any]:
        """Evaluate a candidate result. Every rubric criterion must pass."""
        try:
            candidate = Path(result_path).resolve()
            if not candidate.is_file():
                raise FileNotFoundError(f"Result image does not exist: {candidate}")
            rubric = self.load_rubric()
            start_path = self.get_start_path()
            raw = self._call_judge(
                self._build_messages(rubric, start_path, candidate),
                [item["id"] for item in rubric["criteria"]],
            )
            report = self._normalize_report(raw, rubric)
            report.update(
                {
                    "task_id": self.task_id,
                    "result_file": str(candidate),
                    "rubric_file": str(self.get_rubric_path()),
                    "judge_model": self.model,
                }
            )
            return self._save_report(report)
        except Exception as exc:
            logger.exception("Evaluation failed for task %s", self.task_id)
            report = {
                "task_id": self.task_id,
                "passed": False,
                "summary": "Evaluation could not be completed.",
                "criteria": [],
                "failed_requirements": [],
                "evaluation_error": str(exc),
                "result_file": str(result_path) if result_path else None,
            }
            try:
                return self._save_report(report)
            except Exception:
                return report

    def evaluate_task(self, task_json_path: str, result_path: str) -> Dict[str, Any]:
        """Compatibility wrapper for callers that already have a task JSON path."""
        with Path(task_json_path).open("r", encoding="utf-8") as handle:
            self.task_config = json.load(handle)
        self.task_id = str(self.task_config.get("id", self.task_id))
        return self.evaluate(result_path)
