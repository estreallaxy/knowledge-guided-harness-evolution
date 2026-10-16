from __future__ import annotations

import asyncio
import re
import threading
from collections.abc import Callable
from typing import Any

import torch
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from aspec.benchmarks.benchmark import BaseBenchmark, EvaluationResult
from aspec.meta.types import ChatHistory
from loguru import logger
from aspec.utils import sanitize


class HumanEvalBenchmark(BaseBenchmark):
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

    class TimeoutError(Exception):
        pass

    def run_with_timeout(self, func: Callable, args: tuple[Any, ...], timeout: float) -> Any:
        result: list[Any] = []
        stop_event = threading.Event()

        def target() -> None:
            try:
                result.append(func(*args))
            except Exception as e:
                result.append(e)
            finally:
                stop_event.set()

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        is_timeout = not stop_event.wait(timeout)

        if is_timeout:
            raise self.TimeoutError("Function execution timed out")

        if not result:
            return None
        if isinstance(result[0], Exception):
            raise result[0]
        return result[0]

    def _strip_xml_and_meta(self, text: str) -> str:
        s = str(text)
        # remove fenced xml blocks
        s = re.sub(r"```xml\s*[\s\S]*?```", " ", s, flags=re.IGNORECASE)
        # remove generic <operator_meta>...</operator_meta>
        s = re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", " ", s, flags=re.IGNORECASE)
        # remove XML/HTML-like tags only (avoid stripping comparison operators)
        s = re.sub(r"</?[A-Za-z][A-Za-z0-9:_-]*(?:\s+[^<>]*?)?>", " ", s)
        return s

    def _extract_code_blocks(self, text: str) -> list[str]:
        # capture any fenced code: ```python, ```tool_code, or bare ```
        blocks = re.findall(r"```[a-zA-Z_]*\n([\s\S]*?)```", text, flags=re.IGNORECASE)
        return [b.strip() for b in blocks if b and b.strip()]

    def _extract_xml_code_blocks(self, text: str) -> list[str]:
        s = str(text)
        out: list[str] = []
        for tag in ["final_answer", "code", "solution", "updated_code"]:
            m = re.findall(rf"<{tag}>\s*(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?\s*</{tag}>", s, flags=re.IGNORECASE)
            for blk in m or []:
                if blk and blk.strip():
                    out.append(blk.strip())
        return out

    def _pick_block_with_entry(self, blocks: list[str], entry_point: str) -> str | None:
        for blk in blocks:
            if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", blk, flags=re.MULTILINE):
                return blk.strip()
        for blk in blocks:
            if re.search(r"^\s*(?:async\s+)?def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(", blk, flags=re.MULTILINE):
                return blk.strip()
        return blocks[-1].strip() if blocks else None

    def _slice_function_by_regex(self, text: str, entry_point: str) -> str | None:
        m = re.search(
            rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:[\s\S]*?(?=^\s*def\s+[A-Za-z_]|^\s*async\s+def\s+[A-Za-z_]|\Z)",
            text,
            flags=re.MULTILINE,
        )
        if m:
            return m.group(0).strip()
        return None

    def _isolate_function_from_text(self, text: str, entry_point: str) -> str:
        import ast

        s = str(text)
        lines = s.splitlines()
        try:
            tree = ast.parse(s)
        except (SyntaxError, ValueError):
            return s
        include_ranges: list[tuple[int, int]] = []
        for node in getattr(tree, "body", []) or []:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = getattr(node, "lineno", None)
                end = getattr(node, "end_lineno", None)
                if start is not None:
                    sidx = max(0, int(start) - 1)
                    eidx = int(end) if end is not None else sidx + 1
                    include_ranges.append((sidx, eidx))
        if not include_ranges:
            return s
        include_ranges.sort()
        merged: list[tuple[int, int]] = []
        for a, b in include_ranges:
            if not merged or a > merged[-1][1]:
                merged.append((a, b))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        parts = ["\n".join(lines[a:b]) for a, b in merged]
        return "\n\n".join(p.strip("\n") for p in parts if p.strip()).strip()

    def _extract_exact_signature_from_prompt(self, prompt_text: str, entry_point: str) -> str | None:
        m = re.search(
            rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:",
            str(prompt_text),
            flags=re.MULTILINE,
        )
        return m.group(0) if m else None

    def _enforce_exact_signature(self, code: str, entry_point: str, prompt_text: str) -> str:
        exact = self._extract_exact_signature_from_prompt(prompt_text, entry_point)
        if not exact:
            return code
        if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", code, flags=re.MULTILINE):
            return re.sub(
                rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\([^\)]*\)\s*:",
                exact,
                code,
                count=1,
                flags=re.MULTILINE,
            )
        # Prepend if missing
        return f"{exact}\n    pass\n\n{code.strip()}"

    def prepare_humaneval_code(self, raw_text: str, entry_point: str, prompt_text: str) -> str:
        # 1) normalize to string
        s = self._extract_string_from_output(raw_text)
        # 2) try fenced blocks first on raw text (before stripping tags)
        blocks = self._extract_code_blocks(s)
        if not blocks:
            # also try XML-embedded code
            blocks = self._extract_xml_code_blocks(s)
        chosen = self._pick_block_with_entry(blocks, entry_point) if blocks else None
        if not chosen:
            # 3) strip XML/meta conservatively; prefer keeping full code to retain helpers
            s2 = self._strip_xml_and_meta(s)
            if re.search(rf"^\s*(?:async\s+)?def\s+{re.escape(entry_point)}\s*\(", s2, flags=re.MULTILINE):
                chosen = s2
            else:
                chosen = self._slice_function_by_regex(s2, entry_point) or s2
        # If we have the block, retain helpers/imports with the entry function
        if chosen:
            chosen = self._isolate_function_from_text(chosen, entry_point)
        # 4) remove stray backticks if any
        chosen = re.sub(r"^```[a-zA-Z]*\n|```$", "", chosen).strip()
        # 5) enforce exact signature from prompt if available
        chosen = self._enforce_exact_signature(chosen, entry_point, prompt_text or "")
        logger.warning(
            f"[HE prepare] entry_point={entry_point} raw_len={len(str(raw_text or ''))} blocks={len(blocks or [])}"
        )
        logger.warning(f"[HE prepare cleaned]\n{chosen}")
        return chosen

    def check_solution(self, solution: str, test: str, entry_point: str) -> tuple[str, str]:
        try:
            from typing import Any, Optional

            solution = sanitize(code=solution, entrypoint=entry_point)
            global_dict = {
                "math": __import__("math"),
                "hashlib": __import__("hashlib"),
                "re": __import__("re"),
                "List": list,
                "Dict": dict,
                "Tuple": tuple,
                "Optional": Optional,
                "Any": Any,
            }
            if entry_point == "decode_cyclic":
                solution = (
                    '\n\ndef encode_cyclic(s: str):\n    """\n    returns encoded string by cycling groups of three characters.\n    """\n    # split string to groups. Each of length 3.\n    groups = [s[(3 * i):min((3 * i + 3), len(s))] for i in range((len(s) + 2) // 3)]\n    # cycle elements in each group. Unless group has fewer elements than 3.\n    groups = [(group[1:] + group[0]) if len(group) == 3 else group for group in groups]\n    return "".join(groups)'
                    + "\n\n"
                    + solution
                )
            elif entry_point == "decode_shift":
                solution = (
                    '\n\ndef encode_shift(s: str):\n    """\n    returns encoded string by shifting every character by 5 in the alphabet.\n    """\n    return "".join([chr(((ord(ch) + 5 - ord("a")) % 26) + ord("a")) for ch in s])\n\n\n'
                    + solution
                )
            elif entry_point == "find_zero":
                solution = (
                    "\n\ndef poly(xs: list, x: float):\n    return sum(coeff * (x ** i) for i, coeff in enumerate(xs))\n\n"
                    + solution
                )
            exec(solution, global_dict)
            if entry_point not in global_dict:
                raise ValueError(f"Function {entry_point} is not defined in the solution.")
            exec(test, global_dict)
            check = global_dict["check"]
            result = self.run_with_timeout(check, (global_dict[entry_point],), 15)
            if result is None:
                result = (self.PASS, "The solution passed all test cases.")
            return result
        except self.TimeoutError:
            return (
                self.FAIL,
                "Execution timed out. Please check if your solution contains infinite loops or overly time-consuming operations.",
            )
        except Exception as e:
            error_message = f"Error: {str(e)}.\n Solution: {solution}.\n Test: {test}"
            logger.warning(f"HumanEval check_solution failed for entry_point={entry_point}: {e}")
            return (self.FAIL, error_message)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _generate_output(
        self,
        graph: Callable,
        prompt: str,
        entry_point: str,
        arch_embedding: torch.Tensor | None = None,
        split: str = "validation",
    ) -> Any:
        payload = {"type": "humaneval", "prompt": prompt, "entry_point": entry_point, "log_path": self.log_path}
        return await asyncio.wait_for(graph(payload, self.log_path, arch_embedding, split), timeout=1500)

    async def evaluate_problem(
        self, data: dict[str, Any], graph: Callable, arch_embedding: torch.Tensor | None = None
    ) -> EvaluationResult:
        input_text = data["prompt"]
        try:
            result = await self._generate_output(
                graph, input_text, data["entry_point"], arch_embedding=arch_embedding, split="validation"
            )
            # Expect the workflow 5-tuple: (final_solution, cost, log_prob, conversation_logs, current_run_histories)
            final_solution = ""
            cost = 0.0
            logprob = 0.0
            conversation_logs: ChatHistory = []
            updated_histories: dict[str, ChatHistory] = {}
            if isinstance(result, (list, tuple)) and len(result) >= 5:
                final_solution, cost, logprob, conversation_logs, updated_histories = (
                    result[0],
                    result[1],
                    result[2],
                    result[3],
                    result[4],
                )
            elif isinstance(result, (list, tuple)) and len(result) >= 3:
                final_solution, cost, logprob = result[0], result[1], result[2]

            final_solution = str(final_solution) if final_solution else ""

            # Score the solution
            entry_point = data.get("entry_point", "")
            prompt_text = data.get("prompt", "")
            score = 0.0
            try:
                code_text = self.prepare_humaneval_code(final_solution, entry_point, prompt_text)
                ret = await asyncio.to_thread(self.check_solution, code_text, data.get("test", ""), entry_point)
                if isinstance(ret, (list, tuple)) and ret and ret[0] == self.PASS:
                    score = 1.0
            except Exception as e:
                logger.warning(f"HumanEval scoring failed for entry_point={entry_point}: {e}")

            return EvaluationResult(
                input_text=input_text,
                final_solution=final_solution,
                score=score,
                cost=float(cost) if isinstance(cost, (int, float)) else 0.0,
                logprob=float(logprob) if hasattr(logprob, "item") else float(logprob or 0),
                conversation_logs=conversation_logs if isinstance(conversation_logs, list) else [],
                updated_histories=updated_histories if isinstance(updated_histories, dict) else {},
            )
        except TimeoutError:
            logger.info("Timeout error. Skipping this sample.")
            return EvaluationResult(input_text=input_text)
        except Exception as e:
            logger.info(f"Maximum retries reached. Skipping this sample. Error: {e}")
            return EvaluationResult(input_text=input_text)
