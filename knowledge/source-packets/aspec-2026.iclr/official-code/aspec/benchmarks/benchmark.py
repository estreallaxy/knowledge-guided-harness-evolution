from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import aiofiles
import torch
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from aspec.meta.types import ChatHistory
from aspec.utils import write_json_file


@dataclass
class EvaluationResult:
    """Unified result from benchmark evaluate_problem methods."""

    input_text: str = ""
    output: str = ""
    expected: str = ""
    score: float = 0.0
    cost: float = 0.0
    logprob: float = 0.0
    selected_operators: list[str] = field(default_factory=list)
    conversation_logs: ChatHistory = field(default_factory=list)
    updated_histories: dict[str, ChatHistory] = field(default_factory=dict)
    # HumanEval-specific
    final_solution: str = ""
    # SciCode-specific
    problem_id: str = ""
    total_steps: int = 0
    correct_steps: int = 0


class BaseBenchmark(ABC):
    def __init__(
        self,
        name: str,
        file_path: str,
        log_path: str,
        batch_size: int,
        controller: torch.nn.Module,
        operator_embeddings: torch.Tensor,
        optimizer: torch.optim.Optimizer,
    ) -> None:
        self.name = name
        self.file_path = file_path
        self.log_path = log_path
        self.batch_size = batch_size
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.controller = controller.to(self.device) if controller is not None else None
        self.operator_embeddings = operator_embeddings.to(self.device)
        self.optimizer = optimizer

    PASS = "PASS"
    FAIL = "FAIL"

    async def load_data(self, specific_indices: list[int] | None = None) -> list[dict[str, Any]]:
        data: list[dict[str, Any]] = []
        async with aiofiles.open(self.file_path, encoding="utf-8") as file:
            async for line in file:
                data.append(json.loads(line))
        if specific_indices is not None:
            filtered_data = [data[i] for i in specific_indices if isinstance(i, int) and 0 <= i < len(data)]
            return filtered_data
        return data

    def log_mismatch(
        self,
        problem: str,
        expected_output: Any,
        prediction: str,
        extracted_output: Any,
        extract_answer_code: str = "None",
    ) -> None:
        log_data = {
            "question": problem,
            "right_answer": expected_output,
            "model_output": prediction,
            "extracted_output": extracted_output,
            "extract_answer_code": extract_answer_code,
        }
        log_file = Path(self.log_path) / "log.json"
        if log_file.exists():
            with log_file.open("r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []
        data.append(log_data)
        write_json_file(log_file, data, encoding="utf-8", indent=4)

    def _extract_string_from_output(self, output: Any) -> str:
        if isinstance(output, str):
            return output
        if isinstance(output, (list, tuple)):
            for item in reversed(output):
                if isinstance(item, str) and item.strip():
                    return item
            return str(output[-1]) if output else ""
        if isinstance(output, dict):
            for key in ["answer", "solution", "result", "output", "content", "text"]:
                val = output.get(key)
                if isinstance(val, str) and val.strip():
                    return val
            return json.dumps(output, ensure_ascii=False)
        return str(output)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _generate_output(self, graph: Callable, input_text: str) -> Any:
        return await asyncio.wait_for(graph(input_text), timeout=1500)

    @abstractmethod
    async def evaluate_problem(self, problem: dict[str, Any], graph: Callable) -> EvaluationResult:
        pass
