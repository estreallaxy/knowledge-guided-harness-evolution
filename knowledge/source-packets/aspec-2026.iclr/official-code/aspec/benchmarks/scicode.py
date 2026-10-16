from __future__ import annotations

import ast
import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import torch

from aspec.benchmarks.benchmark import BaseBenchmark, EvaluationResult
from aspec.meta.types import ChatHistory
from loguru import logger

try:
    from aspec.benchmarks.utils.parse_scicode import process_hdf5_to_tuple
except ImportError:

    def process_hdf5_to_tuple(*args: Any, **kwargs: Any) -> Any:
        raise ImportError("The 'scicode' package is not installed. Please install it to run the ScicodeBenchmark.")


def extract_function_definitions(code: str) -> dict[str, str]:
    """
    Extract function definitions from Python code.

    Returns:
        Dict mapping function names to their complete definitions
    """
    if not code or not code.strip():
        return {}

    function_defs = {}
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = code.split("\n")[node.lineno - 1 : node.end_lineno]
                func_def = "\n".join(func_lines)
                function_defs[node.name] = func_def
    except (SyntaxError, ValueError):
        # Fallback to regex-based extraction if AST parsing fails
        pattern = r"^(def\s+(\w+)\s*\([^)]*\):.*?)(?=^def\s+|\Z)"
        matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
        for full_def, func_name in matches:
            function_defs[func_name] = full_def.strip()

    return function_defs


class ScicodeBenchmark(BaseBenchmark):
    def __init__(
        self,
        name: str,
        file_path: str,
        log_path: str,
        batch_size: int,
        controller: torch.nn.Module,
        operator_embeddings: torch.Tensor,
        optimizer: torch.optim.Optimizer,
        h5py_file: str,
        with_background: bool = False,
        prompt_dir: str | None = None,
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
        self.h5py_file = h5py_file if h5py_file else "data/scicode_test_data.h5"
        self.total_completed_problems = 0
        self.total_correct_subproblems_global = 0
        self.total_subproblems_global = 0
        self._stats_lock = asyncio.Lock()
        self._test_lock = asyncio.Lock()
        self.with_background = with_background
        self.prompt_dir = Path(prompt_dir) if prompt_dir else None

    def update_code_with_overwrite(self, previous_llm_code: list[str], step_idx: int, new_code: str) -> None:
        """
        Update the code list with new code, allowing function overwriting.

        Args:
            previous_llm_code: List of existing code strings
            step_idx: Current step index
            new_code: New code that may contain function definitions to overwrite
        """
        if not new_code or not new_code.strip():
            return

        # Extract function definitions from the new code
        new_functions = extract_function_definitions(new_code)

        if not new_functions:
            # No functions in new code, just add it normally
            previous_llm_code[step_idx] = new_code
            return

        # Check for function overwrites in previous steps
        functions_overwritten: set[str] = set()

        for func_name, new_func_def in new_functions.items():
            # Look for this function in previous steps
            for prev_idx in range(step_idx):
                if prev_idx < len(previous_llm_code) and previous_llm_code[prev_idx]:
                    prev_functions = extract_function_definitions(previous_llm_code[prev_idx])
                    if func_name in prev_functions:
                        # Replace the old function with the new one
                        old_func_def = prev_functions[func_name]
                        previous_llm_code[prev_idx] = previous_llm_code[prev_idx].replace(old_func_def, new_func_def)
                        functions_overwritten.add(func_name)
                        logger.info(f"Replaced function '{func_name}' from step {prev_idx} in step {step_idx}")
                        break

        # Add any functions that weren't overwrites to the current step
        remaining_functions: list[str] = []
        for func_name, func_def in new_functions.items():
            if func_name not in functions_overwritten:
                remaining_functions.append(func_def)

        if remaining_functions:
            previous_llm_code[step_idx] = "\n\n".join(remaining_functions)
        else:
            # All functions were overwrites, set current step to empty or non-function code
            non_function_code = new_code
            for func_def in new_functions.values():
                non_function_code = non_function_code.replace(func_def, "")
            previous_llm_code[step_idx] = non_function_code.strip()

    def _resolve_data_dir(self) -> Path | None:
        if self.prompt_dir and self.prompt_dir.is_dir():
            return self.prompt_dir
        candidates: list[Path] = []
        here = Path(__file__).resolve().parent
        candidates.append(here / "prompts")
        for c in candidates:
            if c.is_dir():
                return c
        return None

    def _get_prompt_template_text(self) -> str:
        data_dir = self._resolve_data_dir()
        if not data_dir:
            return ""
        if self.with_background:
            path = data_dir / "multistep_template.txt"
        else:
            path = data_dir / "background_comment_template.txt"
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def _extract_python_script(self, response: str) -> str:
        def _strip_imports(code: str) -> str:
            return re.sub(
                r"^\s*(?:import\s+[^\n]+|from\s+[^\n]+\s+import\s+[^\n]+)\s*$", "", code, flags=re.MULTILINE
            ).strip()

        def _clean_meta(s: str) -> str:
            return re.sub(r"<operator_meta>[\s\S]*?</operator_meta>", "", s, flags=re.IGNORECASE).strip()

        def _strip_xml_tags(s: str) -> str:
            return re.sub(r"<[/]?[a-zA-Z][^>]*>", "", s)

        # Clean meta first
        r = _clean_meta(str(response))
        # Handle <action><code> ... </code> sequences
        code_tags = re.findall(r"<code>([\s\S]*?)</code>", r, re.DOTALL | re.IGNORECASE)
        if code_tags:
            cand = code_tags[-1].strip()
            return _strip_imports(_clean_meta(cand))
        # Steps with finish/input
        steps = re.findall(r"<step>([\s\S]*?)</step>", r, re.DOTALL | re.IGNORECASE)
        if steps:
            last_step = steps[-1]
            if re.search(r"<action>\s*finish\s*</action>", last_step, re.IGNORECASE):
                finish_input_match = re.search(r"<input>([\s\S]*?)</input>", last_step, re.DOTALL | re.IGNORECASE)
                if finish_input_match:
                    content = _clean_meta(finish_input_match.group(1).strip())
                    code_match = re.search(r"```[a-zA-Z0-9_]*\s*\n?([\s\S]*?)```", content, re.DOTALL | re.IGNORECASE)
                    if code_match:
                        return _strip_imports(_clean_meta(code_match.group(1).strip()))
                    # Try <code> inside finish
                    inner_code = re.findall(r"<code>([\s\S]*?)</code>", content, re.DOTALL | re.IGNORECASE)
                    if inner_code:
                        return _strip_imports(_clean_meta(inner_code[-1].strip()))
                    # Fallback: strip XML-ish tags and return if it looks like code
                    plain = _strip_xml_tags(content)
                    if any(tok in plain for tok in ["def ", "class ", "return "]):
                        return _strip_imports(plain.strip())
        code_blocks = re.findall(r"```[a-zA-Z0-9_]*\s*\n?([\s\S]*?)```", response, re.DOTALL | re.IGNORECASE)
        if code_blocks:
            return _strip_imports(_clean_meta(code_blocks[-1].strip()))
        final_answer_match = re.search(r"<final_answer>([\s\S]*?)</final_answer>", response, re.DOTALL | re.IGNORECASE)
        if final_answer_match:
            content = _clean_meta(final_answer_match.group(1).strip())
            code_match = re.search(r"```[a-zA-Z0-9_]*\s*\n?([\s\S]*?)```", content, re.DOTALL | re.IGNORECASE)
            if code_match:
                return _strip_imports(_clean_meta(code_match.group(1).strip()))
            # Fallback: strip tags and return if it looks like code
            plain = _strip_xml_tags(content)
            if any(tok in plain for tok in ["def ", "class ", "return "]):
                return _strip_imports(plain.strip())
        stripped = (response or "").strip()
        if (
            any(tok in stripped for tok in ["def ", "import ", "from ", "class ", "return "])
            and len(stripped.splitlines()) >= 2
        ):
            return _strip_imports(_clean_meta(stripped))
        return ""

    async def evaluate_problem(
        self, problem: dict[str, Any], graph_instance: Callable, arch_embedding: torch.Tensor | None = None
    ) -> EvaluationResult:
        try:
            sub_steps = problem.get("sub_steps", [])
            if not sub_steps:
                logger.error(f"No sub_steps found for problem {problem.get('problem_id', 'N/A')}")
                return EvaluationResult(problem_id=str(problem.get("problem_id", "")))

            tot_steps = len(sub_steps)
            previous_llm_code: list[str] = [""] * tot_steps
            total_cost = 0.0
            total_log_prob = torch.tensor(
                0.0,
                device=self.controller.device
                if hasattr(self, "controller") and hasattr(self.controller, "device")
                else "cpu",
            )
            total_correct_subproblems = 0

            all_conversation_logs: ChatHistory = []

            prev_graph_total_cost = 0.0
            problem_id_str = str(problem.get("problem_id", ""))
            skip_indices: set[int] = set()
            if problem_id_str == "13":
                skip_indices.add(5)
            elif problem_id_str == "62":
                skip_indices.add(0)
            elif problem_id_str == "76":
                skip_indices.add(2)
            carryover_context = ""

            for idx in range(tot_steps):
                if idx in skip_indices:
                    continue
                _clean_query, full_prompt = self.get_subproblem_prompt(problem, idx, previous_llm_code)

                prev_code = "\n".join(previous_llm_code)
                if carryover_context:
                    prev_code = f"{prev_code}\n# ---- Graph Context Carryover ----\n{carryover_context}"
                workflow_input = {
                    "prompt": full_prompt,
                    "problem_id": f"{problem.get('problem_id')}.{idx}",
                    "previous_code": prev_code,
                }

                try:
                    result = await asyncio.wait_for(
                        graph_instance(problem=workflow_input, log_path=self.log_path),
                        timeout=900,
                    )
                    # Handle variable return values from graph_instance
                    # Expected: current_solution, total_cost, sum_log_prob, conversation_logs, operator_chat_histories
                    if isinstance(result, (tuple, list)):
                        if len(result) >= 4:
                            solution_raw = result[0]
                            cost = result[1]
                            log_prob = result[2]
                            conversation_logs: ChatHistory = result[3] if len(result) > 3 else []
                        else:
                            solution_raw = result[0] if len(result) > 0 else ""
                            cost = result[1] if len(result) > 1 else prev_graph_total_cost
                            log_prob = result[2] if len(result) > 2 else torch.tensor(0.0, device=total_log_prob.device)
                            conversation_logs = []
                    else:
                        solution_raw = str(result) if result is not None else ""
                        cost = prev_graph_total_cost
                        log_prob = torch.tensor(0.0, device=total_log_prob.device)
                        conversation_logs = []
                except TimeoutError:
                    logger.error(
                        f"Subproblem {problem.get('problem_id')}.{idx} timed out after 900s; assigning score 0 and continuing"
                    )
                    solution_raw = ""
                    cost = prev_graph_total_cost
                    log_prob = torch.tensor(0.0, device=total_log_prob.device)
                    conversation_logs = []

                all_conversation_logs.extend(conversation_logs)
                try:
                    tail = conversation_logs[-3:] if isinstance(conversation_logs, list) else []
                    lines: list[str] = []
                    for entry in tail:
                        name = entry.get("operator_name")
                        success = entry.get("success")
                        err = None
                        outd = entry.get("output_data") or {}
                        if isinstance(outd, dict):
                            err = outd.get("error")
                        lines.append(f"# op={name} success={success} error={err}")
                    lines.append(f"# cost={cost}")
                    lines.append(f"# log_prob={log_prob}")
                    carryover_context = "\n".join(lines)
                except (AttributeError, TypeError, KeyError):
                    carryover_context = ""

                extracted_code = self._extract_python_script(solution_raw)
                if extracted_code:
                    self.update_code_with_overwrite(previous_llm_code, idx, extracted_code)

                is_correct, _ = await self.test_subproblem(problem, previous_llm_code, idx)

                if is_correct:
                    total_correct_subproblems += 1

                delta_cost = cost - prev_graph_total_cost
                if delta_cost < 0:
                    delta_cost = 0.0
                total_cost += delta_cost
                prev_graph_total_cost = cost

                if isinstance(log_prob, torch.Tensor):
                    total_log_prob += log_prob
                else:
                    total_log_prob += torch.tensor(log_prob, device=total_log_prob.device)

            tot_eval_steps = tot_steps - len(skip_indices)
            avg_score = total_correct_subproblems / tot_eval_steps if tot_eval_steps > 0 else 0.0
            problem_complete = 1 if total_correct_subproblems == tot_eval_steps else 0

            async with self._stats_lock:
                self.total_completed_problems += problem_complete
                self.total_correct_subproblems_global += total_correct_subproblems
                self.total_subproblems_global += tot_eval_steps

            return EvaluationResult(
                problem_id=str(problem.get("problem_id", "")),
                total_steps=tot_eval_steps,
                correct_steps=total_correct_subproblems,
                score=avg_score,
                cost=total_cost,
                logprob=float(total_log_prob) if hasattr(total_log_prob, "item") else float(total_log_prob),
                conversation_logs=all_conversation_logs,
            )

        except Exception as e:
            logger.error(
                f"Error evaluating main problem {problem.get('problem_id', 'N/A')}: {e}",
                exc_info=True,
            )
            return EvaluationResult(problem_id=str(problem.get("problem_id", "")))

    def get_subproblem_prompt(
        self, problem_data: dict[str, Any], num_steps_done: int, previous_llm_code: list[str]
    ) -> tuple[str, str]:
        """
        Generates the prompt for a subproblem.
        Returns a tuple of (clean_query_for_controller, full_prompt_for_llm).
        """
        current_step_idx = num_steps_done

        # --- Build the clean query for the MetaController ---
        step_desc = problem_data["sub_steps"][current_step_idx]["step_description_prompt"]
        header = problem_data["sub_steps"][current_step_idx]["function_header"]
        clean_query_parts = [step_desc, header]
        clean_query = "\n\n".join(part for part in clean_query_parts if part and part.strip())

        # --- Build the full prompt for the LLM operators ---
        next_step = []
        if self.with_background:
            step_desc_full = step_desc + "\n" + problem_data["sub_steps"][current_step_idx].get("step_background", "")
        else:
            step_desc_full = step_desc
        next_step.append(step_desc_full)

        return_line = problem_data["sub_steps"][current_step_idx]["return_line"]
        next_step.append(f"{header}\n\n{return_line}")

        completed_code = "\n".join(code for code in previous_llm_code if code and code.strip())
        if completed_code:
            problem_steps_str = f"The following code has been implemented in previous steps. You can assume it is available for you to use. **DO NOT INCLUDE THIS CODE SNIPPET OR ANY HELPER FUNCTIONS IN YOUR FINAL RESPONSE**:\n\n```python\n{completed_code}\n```"
        else:
            problem_steps_str = "This is the first step. No code has been written yet."

        next_step_str = "\n\n".join(next_step)

        # Use subproblem-specific dependencies if available, otherwise fall back to problem-level
        sub_step_data = problem_data["sub_steps"][current_step_idx]
        dependencies = sub_step_data.get("required_dependencies", problem_data.get("required_dependencies", ""))

        dependencies_instruction = ""
        if dependencies and dependencies.strip():
            dependencies_instruction = (
                "You have the following dependencies available. Do not reimport them, they're already imported. You MUST NOT use any other libraries or modules.\n"
                "```python\n"
                f"{dependencies}\n"
                "```"
            )
        else:
            dependencies_instruction = (
                "No specific dependencies are required for this step. You can use standard Python libraries."
            )

        template_text = self._get_prompt_template_text()

        # Prepend dependencies instruction to the next_step_str to make them visible to the LLM
        full_next_step_str = f"{dependencies_instruction}\n\n{next_step_str}"

        full_prompt = template_text.format(
            problem_steps_str=problem_steps_str,
            next_step_str=full_next_step_str,
            dependencies=dependencies,  # This is now for backward compatibility with the template
        )
        return clean_query, full_prompt

    async def test_subproblem(
        self, prob_data: dict[str, Any], generated_codes: list[str], step_idx_to_test: int
    ) -> tuple[int, str]:
        """Asynchronously runs the subproblem test, ensuring only one runs at a time."""
        async with self._test_lock:
            await asyncio.sleep(0)
            loop = asyncio.get_running_loop()
            try:
                # The actual test logic is synchronous and blocking, so run it in an executor
                score, stderr = await loop.run_in_executor(
                    None, self._test_subproblem_sync, prob_data, generated_codes, step_idx_to_test
                )
                return score, stderr
            except Exception as e:
                logger.error(
                    f"Error executing subproblem test for {prob_data.get('problem_id', 'N/A')}.{step_idx_to_test} in executor: {e}"
                )
                return 0, str(e)

    def _test_subproblem_sync(
        self, prob_data: dict[str, Any], generated_codes: list[str], step_idx_to_test: int
    ) -> tuple[int, str]:
        tmp_dir = Path(f"tmp_scicode_{time.time()}_{prob_data['problem_id']}_{step_idx_to_test}")
        tmp_dir.mkdir(parents=True, exist_ok=True)

        step_data = prob_data["sub_steps"][step_idx_to_test]
        step_id = step_data["step_number"]
        code_content_for_step = "\n".join(generated_codes)
        test_lst = step_data["test_cases"]
        assert_file = Path(tmp_dir, f"{step_id}.py")

        # Use subproblem-specific dependencies for the test environment
        dependencies = step_data.get("required_dependencies", prob_data.get("required_dependencies", ""))

        with open(assert_file, "w", encoding="utf-8") as f:
            f.write(
                "try:\n    import scipy.integrate as _si\n    if not hasattr(_si, 'simps') and hasattr(_si, 'simpson'):\n        _si.simps = _si.simpson\nexcept Exception:\n    pass\n\n"
            )
            f.write("import itertools\n")
            f.write(dependencies + "\n\n")
            f.write(code_content_for_step)
            f.write("\n\n")
            f.write("from aspec.benchmarks.utils.parse_scicode import process_hdf5_to_tuple\n\n")
            f.write(
                "from aspec.benchmarks.utils.scicode_comparisons import cmp_tuple_or_list, are_dicts_close, are_csc_matrix_close, process_symbol_in_dict\n"
            )
            f.write("\n\n")

            f.write("import traceback\n")
            f.write(
                "try:\n    from scicode.compare.cmp import cmp_tuple_or_list as _cmp\n    cmp_tuple_or_list = _cmp\nexcept ImportError:\n    from aspec.benchmarks.utils.scicode_comparisons import cmp_tuple_or_list\n\n"
            )
            f.write(
                f"targets = process_hdf5_to_tuple('{step_id}', {len(test_lst)}, '{os.path.abspath(self.h5py_file)}')\n"
            )
            for i in range(len(test_lst)):
                f.write(f"target = targets[{i}]\n\n")
                for line in test_lst[i].split("\n"):
                    f.write(line + "\n")

        def run_script(script_path: Path) -> tuple[int, str]:
            try:
                test_timeout = int(os.getenv("SCICODE_ASSERT_TIMEOUT_SEC", "360"))
                subprocess.run(
                    [sys.executable, str(script_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=test_timeout,
                )
                return 0, ""
            except subprocess.CalledProcessError as e:
                error_message = f"Script {script_path} failed with error:\n{e.stderr}"
                logger.error(error_message)
                return 1, e.stderr
            except subprocess.TimeoutExpired as e:
                error_message = f"Script {script_path} timed out after {e.timeout} seconds."
                logger.warning(error_message)
                return 2, error_message

        ret_code, stderr = run_script(assert_file)
        shutil.rmtree(tmp_dir)
        score = 1 if ret_code == 0 else 0
        logger.warning(f"Scicode subproblem {step_id} score: {score} code: {code_content_for_step}")
        return score, stderr
