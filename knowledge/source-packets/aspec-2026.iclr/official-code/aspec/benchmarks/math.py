from __future__ import annotations

import contextlib
import inspect
import re
from collections.abc import Callable
from math import isclose
from typing import Any

import regex
import torch
from sympy import N, simplify
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr

from aspec.benchmarks.benchmark import BaseBenchmark, EvaluationResult
from loguru import logger


class MATHBenchmark(BaseBenchmark):
    def __init__(
        self,
        name: str,
        file_path: str,
        log_path: str,
        batch_size: int,
        controller: torch.nn.Module,
        operator_embeddings: list[list[float]],
        optimizer: torch.optim.Optimizer,
    ) -> None:
        super().__init__(
            name,
            file_path,
            log_path,
            batch_size,
            controller,
            operator_embeddings,
            optimizer,
        )

    async def evaluate_problem(
        self, problem: dict[str, Any], graph: Callable, arch_embedding: torch.Tensor | None = None
    ) -> EvaluationResult:
        input_text = problem["problem"]
        expected_output = problem["solution"]

        try:
            result = await graph(problem, self.log_path, arch_embedding=arch_embedding)
            conversation_logs = []
            if isinstance(result, (list, tuple)) and len(result) >= 5:
                output, cost, logprob, selected_operators, conversation_logs = (
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[4],
                )
            elif isinstance(result, (list, tuple)) and len(result) >= 4:
                output, cost, logprob, selected_operators = result[0], result[1], result[2], result[3]
            elif isinstance(result, (list, tuple)) and len(result) >= 3:
                output, cost, logprob = result[0], result[1], result[2]
                selected_operators = []
            else:
                output, cost, logprob = await self._generate_output(graph, input_text)
                selected_operators = []

            output = self._extract_string_from_output(output)

            predicted_for_format = self.extract_model_answer(output)
            if isinstance(predicted_for_format, str):
                predicted_for_format = predicted_for_format.strip()
            if predicted_for_format and ("\\boxed{" not in output or "$$" not in output):
                output = f"{output.rstrip()}\n\n$$\\boxed{{{predicted_for_format}}}$$"

            if not output:
                raise ValueError("output is empty")

            uni_score, extracted_output = self._calculate_math_score(expected_output, output)

            if uni_score == 0:
                self.log_mismatch(
                    input_text,
                    expected_output,
                    output,
                    extracted_output,
                    extract_answer_code=self.get_function_code(self.extract_model_answer),
                )

            return EvaluationResult(
                input_text=problem["problem"],
                output=output,
                expected=problem.get("solution", ""),
                score=uni_score,
                cost=cost,
                logprob=float(logprob) if hasattr(logprob, "item") else float(logprob),
                selected_operators=selected_operators,
                conversation_logs=conversation_logs,
            )

        except Exception as e:
            logger.info(f"Maximum retries reached. Skipping this sample. Error: {e}")
            return EvaluationResult(
                input_text=input_text,
                output="Timeout",
                expected=expected_output,
            )

    def calculate_score(self, expected_output: Any, prediction: Any) -> tuple[float, Any]:
        if not isinstance(expected_output, str):
            expected_output = str(expected_output)
        if not isinstance(prediction, str):
            prediction = str(prediction)
        s, ex = self._calculate_math_score(expected_output, prediction)
        return float(s), ex

    def extract_model_answer(self, text: str) -> str:
        if not isinstance(text, str):
            text = self._extract_string_from_output(text)

        # First try XML tags and extract boxed content from within them
        tag_patterns = [
            r"<final_answer>\s*([\s\S]*?)\s*</final_answer>",
            r"<answer>\s*([\s\S]*?)\s*</answer>",
            r"<refined>\s*([\s\S]*?)\s*</refined>",
            r"<refined_answer>\s*([\s\S]*?)\s*</refined_answer>",
        ]
        for p in tag_patterns:
            m = re.findall(p, text, re.IGNORECASE)
            if m:
                candidate = m[-1].strip()
                # Strip CDATA wrapper if present
                candidate = re.sub(r"^\s*<!\[CDATA\[(.*?)\]\]>\s*$", r"\1", candidate, flags=re.DOTALL)
                candidate = re.sub(r"^```[a-zA-Z]*\\n|```$", "", candidate).strip().strip("`")

                # If the XML tag content contains \boxed{}, extract just the boxed content
                boxed_pattern = r"\\boxed\{((?:[^{}]|{[^{}]*})*)\}"
                boxed_matches = re.findall(boxed_pattern, candidate, re.DOTALL)
                if boxed_matches:
                    return boxed_matches[-1].strip()
                elif candidate:
                    return candidate

        # Then try \boxed{} patterns anywhere in the text (most common for MATH)
        pattern = r"\\boxed\{((?:[^{}]|{[^{}]*})*)\}"
        boxed_matches = re.findall(pattern, text, re.DOTALL)
        if boxed_matches:
            return boxed_matches[-1].strip()

        # Fallback to last sentence
        sentence_end_pattern = r"(?<!\d)[.!?]\s+"
        sentences = re.split(sentence_end_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences[-1] if sentences else ""

    def _calculate_math_score(self, expected_output: str, prediction: str) -> tuple[int, str]:
        if not isinstance(expected_output, str):
            expected_output = str(expected_output)
        if not isinstance(prediction, str):
            prediction = str(prediction)
        expected_answer = self.extract_model_answer(expected_output)
        predicted_answer = self.extract_model_answer(prediction)
        if self.math_equal(predicted_answer, expected_answer):
            return 1, predicted_answer
        else:
            return 0, predicted_answer

    def math_equal(self, prediction: Any, reference: Any) -> bool:
        if str(prediction) == str(reference):
            return True

        if self.is_digit(prediction) and self.is_digit(reference):
            prediction = self.parse_digits(prediction)
            reference = self.parse_digits(reference)
            return isclose(prediction, reference, abs_tol=1e-3)
        return self.symbolic_equal(prediction, reference)

    def is_digit(self, num: Any) -> bool:
        return self.parse_digits(num) is not None

    def parse_digits(self, num: Any) -> float | None:
        num = regex.sub(",", "", str(num))
        try:
            return float(num)
        except (ValueError, TypeError):
            if num.endswith("%"):
                num = num[:-1]
                if num.endswith("\\"):
                    num = num[:-1]
                try:
                    return float(num) / 100
                except (ValueError, TypeError):
                    pass
        return None

    def symbolic_equal(self, a: Any, b: Any) -> bool:
        def _parse(s: Any) -> Any:
            for f in [parse_latex, parse_expr]:
                with contextlib.suppress(Exception):
                    return f(s)
            return s

        a = _parse(a)
        b = _parse(b)
        with contextlib.suppress(Exception):
            if simplify(a - b) == 0:
                return True
        with contextlib.suppress(Exception):
            if isclose(N(a), N(b), abs_tol=1e-3):
                return True
        return False

    def get_function_code(self, func: Callable) -> str:
        try:
            source_code = inspect.getsource(func)
            return source_code
        except OSError:
            return "no code"
