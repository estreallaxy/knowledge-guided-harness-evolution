from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import torch

from aspec.benchmarks.benchmark import BaseBenchmark, EvaluationResult
from loguru import logger


class GPQABenchmark(BaseBenchmark):
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

    def extract_answer_choice(self, text: str) -> str | None:
        """Extract answer choice (A, B, C, D) from model response."""
        if not isinstance(text, str):
            text = str(text)

        patterns = [
            r"The\s+final\s+answer\s+is:\s*([A-D])",
            r"<final_answer>[^A-D]*([A-D])[^A-D]*</final_answer>",
            r"(?:answer|choice)\s*(?:is|:)\s*([ABCD])",
            r"\b([ABCD])\s*(?:is\s+(?:the\s+)?(?:correct|right|answer))",
            r"(?:^|\s)([ABCD])(?:\s*[.)]|\s*$)",
            r"\(([ABCD])\)",
            r"option\s+([ABCD])",
            r"choice\s+([ABCD])",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[-1].upper()

        matches = re.findall(r"\b([ABCD])\b", text)
        if matches:
            return matches[-1].upper()

        return None

    def format_question(self, problem: dict[str, Any]) -> tuple[str, str]:
        """Format the GPQA question with answer choices."""
        question = problem.get("Question", "")
        correct_answer = problem.get("Correct Answer", "")
        incorrect_1 = problem.get("Incorrect Answer 1", "")
        incorrect_2 = problem.get("Incorrect Answer 2", "")
        incorrect_3 = problem.get("Incorrect Answer 3", "")

        # Create shuffled choices (maintaining consistency with a simple hash-based approach)
        choices = [correct_answer, incorrect_1, incorrect_2, incorrect_3]

        # Deterministic shuffle: pick one of 24 permutations based on question hash
        import hashlib
        import itertools

        perms = list(itertools.permutations(range(4)))
        digest = int.from_bytes(hashlib.sha256(question.encode("utf-8")).digest()[:8], "big")
        choice_order = list(perms[digest % len(perms)])

        # Determine correct answer letter
        correct_letter = chr(65 + choice_order.index(0))  # A=65 in ASCII

        formatted_question = f"{question}\n\n"
        for i, choice_idx in enumerate(choice_order):
            letter = chr(65 + i)  # A, B, C, D
            formatted_question += f"{letter}. {choices[choice_idx]}\n"

        return formatted_question, correct_letter

    def calculate_score(self, expected_answer: str, predicted_answer: str | None) -> tuple[float, str | None]:
        """Calculate score based on answer choice match."""
        if predicted_answer is None:
            return 0.0, predicted_answer
        score = 1.0 if predicted_answer.upper() == expected_answer.upper() else 0.0
        return score, predicted_answer

    async def evaluate_problem(self, problem: dict[str, Any], graph: Callable, **kwargs: Any) -> EvaluationResult:
        """Evaluate a single GPQA problem."""
        try:
            formatted_question, correct_answer = self.format_question(problem)

            result = await self._generate_output(graph, formatted_question)

            if len(result) == 7:
                # Format with 7 elements: (str, str, str, float, float, tensor, list)
                formatted_question_dup, output, correct_answer_dup, score, cost, logprob_tensor, selected_operators = (
                    result
                )
                logprob = float(logprob_tensor) if hasattr(logprob_tensor, "item") else float(logprob_tensor)
            elif len(result) == 6:
                # Format: (output, cost, logprob, selected_operators, conversation_logs, operator_chat_histories)
                output, cost, logprob, selected_operators, conversation_logs, operator_chat_histories = result
            elif len(result) == 4:
                output, cost, logprob, selected_operators = result
            else:
                output, cost, logprob = result
                selected_operators = []

            if not output:
                raise ValueError("output is empty")

            predicted_answer = self.extract_answer_choice(output)
            score, _ = self.calculate_score(correct_answer, predicted_answer)

            if score == 0:
                self.log_mismatch(formatted_question, correct_answer, output, predicted_answer or "None extracted")

            return EvaluationResult(
                input_text=formatted_question,
                output=output,
                expected=correct_answer,
                score=score,
                cost=cost,
                logprob=float(logprob) if hasattr(logprob, "item") else float(logprob),
                selected_operators=selected_operators,
            )

        except Exception as e:
            logger.info(f"Maximum retries reached. Skipping this sample. Error: {e}")
            formatted_question, correct_answer = self.format_question(problem)
            return EvaluationResult(
                input_text=formatted_question,
                output=str(e),
                expected=correct_answer,
            )
