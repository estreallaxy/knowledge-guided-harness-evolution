from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


from aspec.benchmarks.benchmark import BaseBenchmark, EvaluationResult
from loguru import logger


class MMLUBenchmark(BaseBenchmark):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._eval_data: list[dict[str, Any]] = []

    async def load_data(self, specific_indices: list[int] | None = None) -> list[dict[str, Any]]:
        # Use in-memory dataset stored on the instance
        data = self._eval_data
        if specific_indices is not None:
            return [data[i] for i in specific_indices if isinstance(i, int) and 0 <= i < len(data)]
        return data

    async def evaluate_problem(self, problem: dict[str, Any], graph: Callable, *_: Any, **__: Any) -> EvaluationResult:
        question = problem.get("question") or problem.get("prompt") or ""
        answer = problem.get("answer")

        prediction = ""
        cost = 0.0
        log_prob = 0.0
        selected_operators: Any = []

        try:
            res = await graph(problem)
        except Exception as e:
            logger.warning(f"MMLU graph call failed: {e}")
            res = None

        if isinstance(res, (list, tuple)):
            try:
                prediction = str(res[0])
            except (IndexError, TypeError):
                prediction = str(res)
            try:
                cost = float(res[1])
            except (IndexError, TypeError, ValueError):
                cost = 0.0
            try:
                lp = res[2]
                if isinstance(lp, (int, float)):
                    log_prob = float(lp)
                elif hasattr(lp, "item"):
                    log_prob = float(lp.item())
                else:
                    log_prob = 0.0
            except (IndexError, TypeError, ValueError, RuntimeError):
                log_prob = 0.0
            try:
                selected_operators = res[3]
            except (IndexError, TypeError):
                selected_operators = []
        elif isinstance(res, dict):
            prediction = str(res.get("prediction") or res.get("response") or "")
            try:
                cost = float(res.get("cost", 0.0))
            except (TypeError, ValueError):
                cost = 0.0
            try:
                lp = res.get("log_prob", 0.0)
                log_prob = float(lp.item() if hasattr(lp, "item") else lp)
            except (TypeError, ValueError, RuntimeError):
                log_prob = 0.0
            selected_operators = res.get("selected_operators") or []
        else:
            prediction = str(res or "")

        score, extracted_answer = self.calculate_score(answer, prediction)

        return EvaluationResult(
            input_text=question,
            output=prediction,
            expected=answer,
            score=score,
            cost=cost,
            logprob=log_prob,
            selected_operators=selected_operators if isinstance(selected_operators, list) else [],
        )

    def calculate_score(self, expected_output: Any, prediction: Any) -> tuple[float, Any]:
        prediction_str = str(prediction)
        extracted_answer = ""

        patterns = [
            r"The\s+final\s+answer\s+is[:\s]*([A-D])",
            r"<final_answer>.*?The\s+final\s+answer\s+is[:\s]*([A-D]).*?</final_answer>",
            r"The\s+(best|correct)\s+answer\s+is[:\s]*([A-D])",
            r"final\s+answer[:\s]*([A-D])",
            r"(best|correct)\s+answer[:\s]*([A-D])",
            r"answer[:\s]*([A-D])\s*$",
            r"Answer\s*\d+[:\s]+([A-D])",
            r"^[\t ]*([A-D])[).]",
            r"\b([A-D])\s*[.)]",
            r"\b([A-D])\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, prediction_str, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                grp = match.groups()
                extracted_answer = grp[-1].upper() if grp else match.group(1).upper()
                predicted_index = ord(extracted_answer) - ord("A")
                if predicted_index == expected_output:
                    return 1.0, extracted_answer
                return 0.0, extracted_answer

        return 0.0, extracted_answer
