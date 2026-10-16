"""Unified EvoAgent evaluation script for all datasets.

Usage:
    pixi run python -m experiments.scripts.eval_evoagent --dataset MATH --model gemini-2.0-flash
    pixi run python -m experiments.scripts.eval_evoagent --dataset GPQA --sample 50
    pixi run python -m experiments.scripts.eval_evoagent --dataset HumanEval
    pixi run python -m experiments.scripts.eval_evoagent --dataset MMLU --batch_size 4
    pixi run python -m experiments.scripts.eval_evoagent --dataset SciCode --ind 2
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Any, Dict, List, Optional

import torch
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from aspec.benchmarks.scicode import ScicodeBenchmark
from aspec.llm import BaseLLM

from experiments.lib.eval_utils import (
    _extract_string_from_output,
    create_llm,
    load_jsonl_data,
    retry_with_backoff,
)
from experiments.lib.scoring import (
    calculate_gpqa_score,
    calculate_math_score,
    calculate_mmlu_score,
    check_solution,
    extract_answer_letter,
    extract_model_answer_gpqa,
    format_gpqa_with_choices,
    format_mmlu_question,
    prepare_humaneval_code,
)


# ---------------------------------------------------------------------------
# Per-dataset prompt templates
# ---------------------------------------------------------------------------

# The solver loop is the same for all datasets:
#   initial → (meta → check → multi → refine) × ind
# Only the prompts and the check condition differ.


class _DatasetPrompts:
    """Prompt templates for a single dataset."""

    def __init__(
        self,
        *,
        initial_fmt: str,
        meta_fmt: str,
        check_fmt: str,
        multi_fmt: str,
        refine_fmt: str,
        check_invert: bool = False,
    ) -> None:
        self.initial_fmt = initial_fmt
        self.meta_fmt = meta_fmt
        self.check_fmt = check_fmt
        self.multi_fmt = multi_fmt
        self.refine_fmt = refine_fmt
        # If True, pass condition is "'discard' not in check" instead of "'retain' in check"
        self.check_invert = check_invert

    def build_initial(self, problem: str, **kw: Any) -> str:
        return self.initial_fmt.format(problem=problem, **kw)

    def build_meta(self, problem: str, answer: str, descriptions: List[str]) -> str:
        desc = "\n".join([f"- {d}" for d in descriptions]) if descriptions else "(none yet)"
        return self.meta_fmt.format(problem=problem, answer=answer, desc=desc)

    def build_check(self, problem: str, descriptions: List[str], new_desc: str) -> str:
        desc = "\n".join([f"- {d}" for d in descriptions]) if descriptions else "(none)"
        return self.check_fmt.format(problem=problem, desc=desc, new_desc=new_desc)

    def build_multi(self, problem: str, desc: str, **kw: Any) -> str:
        return self.multi_fmt.format(problem=problem, desc=desc, **kw)

    def build_refine(self, problem: str, old_answer: str, desc: str, new_answer: str, **kw: Any) -> str:
        return self.refine_fmt.format(problem=problem, old_answer=old_answer, desc=desc, new_answer=new_answer, **kw)

    def should_retain(self, check_text: str) -> bool:
        if self.check_invert:
            return "discard" not in check_text.lower()
        return "retain" in check_text.lower()


# --- MATH prompts ---
MATH_PROMPTS = _DatasetPrompts(
    initial_fmt=(
        "Solve the math problem. "
        "Strictly end with one final line containing only the canonical form $$\\boxed{{<final answer only>}}$$.\n"
        "Problem:\n{problem}\n"
    ),
    meta_fmt=(
        "{problem}\nThis is your current answer:\n{answer}\n\n"
        "Create one new expert mathematician for improving the solution."
        " Describe the single expert in second person (e.g., 'You are a ...'), focusing on a unique sub-skill.\n"
        "Previously created experts:\n{desc}\n\nGive only the new expert description:"
    ),
    check_fmt=(
        "{problem}\n\nExisting experts:\n{desc}\n\nNew expert candidate:\n{new_desc}\n\n"
        "Decide if the new expert should be retained. Criteria: (1) helpful for solving the problem; (2) not overlapping with existing experts."
        " Reply with exactly 'Retain' or 'Discard' and a brief reason."
    ),
    multi_fmt=(
        "{desc}\n\n{problem}\n"
        "Provide reasoning, then end with one final line with only $$\\boxed{{<final answer only>}}$$."
    ),
    refine_fmt=(
        "{problem}\nThis is your current answer:\n{old_answer}\n\n"
        "An expert described as: '{desc}' provided this answer:\n{new_answer}\n\n"
        "Refine your answer."
        " End with one final line containing only $$\\boxed{{<final answer only>}}$$.\nRevised Answer:"
    ),
)

# --- GPQA prompts (verbose, inverted check) ---
GPQA_PROMPTS = _DatasetPrompts(
    initial_fmt=(
        "\n{problem}\n"
        'You need to give reasons first and then give the answer with the format: "Final Answer: choice: XX"\n'
    ),
    meta_fmt=(
        "\n{problem}\nThis is your answer:\n{answer}\n\n"
        "Now, you can create and collaborate with multiple specialists to improve your answer. Therefore, please describe in as much detail as possible the different skills and focuses you need from multiple specialists individually. \n"
        "We will provide each specialist with the same information and query. However, please note that each profession has its own specialization, so you can assign each specialist to just one sub-task to ensure a more refined response. \n"
        "We will relay their responses to you in turn, allowing you to reorganize them into a better answer.\n"
        "Please note that the description should be narrated in the second person, for example: You are a XXX.\n\n"
        "These are the descriptions of the specialists you have created before for this task:\n{desc}\n\n"
        "Therefore, please remember you should not repeatedly create the same specialists as described above.\n"
        "Now, you can give the description for a new specialist (Please note that only be one, do not give multiple at one time):\n"
    ),
    check_fmt=(
        "\n{problem}\n\n"
        "We employ mulitple specialists to answer this query. The following is a second-person introduction to the specialists we have hired:\n{desc}\n\n"
        "Now, we will hire a new specialist to help better respond to user query. Here is a second person description of the new specialist:\n{new_desc}\n\n"
        "Since hiring new specialists takes extra time and money, please evaluate the new specialist based on the following two criteria to decide whether they should be retained or not:\n"
        "1. Based on the new specialist's description, determine if they can effectively assist in answering users' questions.\n"
        "2. The new specialists are unique and do not overlap with previously hired specialists.\n"
        "The new specialist must meet both of the above two criteria. If any of the criteria are not met, they should be discarded.\n"
        "Give the reason first and then give the choice. If retaining, please reply with: 'Retain'. If discarding, please reply with: 'Discard'.\n"
    ),
    multi_fmt=(
        "\n{desc}. \n{problem}\n"
        'You need to give reasons first and then give the answer with the format: "Final Answer: choice: XX"\n'
    ),
    refine_fmt=(
        "\n{problem}\nThis is your answer:\n{old_answer}\n\n"
        'You invite a specialist whose description is: "{desc}"\n'
        "This specialist also give his answer based on his own professional knowledge: {new_answer}.\n\n"
        "Now you can refine your answer with his answer to better answer the question. \n"
        "Keep in mind that his answer may not be correct, so critically decide whether to accept his response or stick with your original one.\n"
        'You need to give reasons first and then give the answer with the format: "Final Answer: choice: XX" \n'
        "Revised Answer:\n"
    ),
    check_invert=True,
)

# --- HumanEval prompts ---
HUMANEVAL_PROMPTS = _DatasetPrompts(
    initial_fmt=(
        "Write Python code implementing the required function(s). Ensure the exact entry point `{entry_point}` is defined. "
        "Return only a single fenced Python code block.\n\n"
        "Task:\n{problem}"
    ),
    meta_fmt=(
        "{problem}\nCurrent implementation (truncated OK):\n{answer}\n\n"
        "Propose ONE new coding expert persona (second person: 'You are ...') with a unique sub-skill to improve correctness and edge-case handling.\n"
        "Previously created experts:\n{desc}\nGive only the new expert description:"
    ),
    check_fmt=(
        "{problem}\n\nExisting experts:\n{desc}\n\nNew expert candidate:\n{new_desc}\n\n"
        "Decide retain/discard. Criteria: (1) helps produce correct code; (2) not overlapping with existing experts. Reply exactly 'Retain' or 'Discard' with a brief reason."
    ),
    multi_fmt=(
        "{desc}\n\n{problem}\n"
        "Provide an improved full implementation ensuring the exact entry point `{entry_point}` exists. Return only a single fenced Python code block."
    ),
    refine_fmt=(
        "{problem}\nExisting implementation (A):\n{old_answer}\n\n"
        "Expert ('{desc}') proposed implementation (B):\n{new_answer}\n\n"
        "Produce the best final implementation, ensuring entry point `{entry_point}` is correct. Return only a single fenced Python code block."
    ),
)

# --- MMLU prompts ---
MMLU_PROMPTS = _DatasetPrompts(
    initial_fmt=(
        "Solve the multiple-choice question. "
        "End with: 'The final answer is: X' and optionally <final_answer>X</final_answer>.\n\n"
        "Question:\n{problem}"
    ),
    meta_fmt=(
        "{problem}\nCurrent answer:\n{answer}\n\n"
        "Propose ONE new expert persona that brings a unique sub-skill for this MCQ (second person: 'You are ...').\n"
        "Previously created experts:\n{desc}\nGive only the new expert description:"
    ),
    check_fmt=(
        "{problem}\n\nExisting experts:\n{desc}\n\nNew expert candidate:\n{new_desc}\n\n"
        "Decide retain/discard. Criteria: (1) helpful for answering; (2) not overlapping with existing experts. Reply exactly 'Retain' or 'Discard' with a brief reason."
    ),
    multi_fmt=(
        "{desc}\n\n{problem}\n"
        "Solve the multiple-choice question, then end with: 'The final answer is: X' and optionally <final_answer>X</final_answer>."
    ),
    refine_fmt=(
        "{problem}\nCurrent answer:\n{old_answer}\n\n"
        "Expert ('{desc}') produced:\n{new_answer}\n\n"
        "Refine the answer. End with: 'The final answer is: X' and optionally <final_answer>X</final_answer>.\nRevised Answer:"
    ),
)

# --- SciCode prompts (verbose, same style as GPQA) ---
SCICODE_PROMPTS = _DatasetPrompts(
    initial_fmt=(
        '\n{problem}\nYou need to give reasons first and then give the answer with the format: "Final Answer: code: [your code]"\n'
    ),
    meta_fmt=(
        "\n{problem}\nThis is your code:\n{answer}\n\n"
        "Now, you can create and collaborate with multiple specialists to improve your code. Therefore, please describe in as much detail as possible the different skills and focuses you need from multiple specialists individually. \n"
        "We will provide each specialist with the same information and query. However, please note that each profession has its own specialization, so you can assign each specialist to just one sub-task to ensure a more refined response. \n"
        "We will relay their responses to you in turn, allowing you to reorganize them into a better code.\n"
        "Please note that the description should be narrated in the second person, for example: You are a XXX.\n\n"
        "These are the descriptions of the specialists you have created before for this task:\n{desc}\n\n"
        "Therefore, please remember you should not repeatedly create the same specialists as described above.\n"
        "Now, you can give the description for a new specialist (Please note that only be one, do not give multiple at one time):\n"
    ),
    check_fmt=(
        "\n{problem}\n\n"
        "We employ mulitple specialists to answer this query. The following is a second-person introduction to the specialists we have hired:\n{desc}\n\n"
        "Now, we will hire a new specialist to help better respond to user query. Here is a second person description of the new specialist:\n{new_desc}\n\n"
        "Since hiring new specialists takes extra time and money, please evaluate the new specialist based on the following two criteria to decide whether they should be retained or not:\n"
        "1. Based on the new specialist's description, determine if they can effectively assist in answering users' questions.\n"
        "2. The new specialists are unique and do not overlap with previously hired specialists.\n"
        "The new specialist must meet both of the above two criteria. If any of the criteria are not met, they should be discarded.\n"
        "Give the reason first and then give the choice. If retaining, please reply with: 'Retain'. If discarding, please reply with: 'Discard'.\n"
    ),
    multi_fmt=(
        '\n{desc}. \n{problem}\nYou need to give reasons first and then give the answer with the format: "Final Answer: code: [your code]"\n'
    ),
    refine_fmt=(
        "\n{problem}\nThis is your code:\n{old_answer}\n\n"
        'You invite a specialist whose description is: "{desc}"\n'
        "This specialist also give his code based on his own professional knowledge: {new_answer}.\n\n"
        "Now you can refine your code with his code to better answer the question. \n"
        "Keep in mind that his code may not be correct, so critically decide whether to accept his response or stick with your original one.\n"
        'You need to give reasons first and then give the answer with the format: "Final Answer: code: [your code]" \n'
        "Revised Answer:\n"
    ),
    check_invert=True,
)


DATASET_CONFIGS: Dict[str, Dict[str, Any]] = {
    "MATH": {
        "prompts": MATH_PROMPTS,
        "data_path": "data/math_{split}.jsonl",
        "problem_key": "problem",
        "expected_key": "solution",
        "scoring_fn": calculate_math_score,
    },
    "GPQA": {
        "prompts": GPQA_PROMPTS,
        "data_path": "data/gpqa_{split}.jsonl",
        "scoring_fn": calculate_gpqa_score,
        "track_tokens": True,
    },
    "HumanEval": {
        "prompts": HUMANEVAL_PROMPTS,
        "data_path": "data/humaneval_{split}.jsonl",
    },
    "MMLU": {
        "prompts": MMLU_PROMPTS,
        "data_path": "data/mmlu_{split}.jsonl",
    },
    "SciCode": {
        "prompts": SCICODE_PROMPTS,
        "data_path": "data/scicode_test.jsonl",
        "h5_path": "data/scicode_test_data.h5",
    },
}

SCICODE_SKIP_INDICES: Dict[str, set[int]] = {"13": {5}, "62": {0}, "76": {2}}


# ---------------------------------------------------------------------------
# Core EvoAgent solver
# ---------------------------------------------------------------------------


async def _aask(llm: BaseLLM, prompt: str) -> str:
    resp = await retry_with_backoff(llm.aask, prompt)
    return _extract_string_from_output(resp)


async def evoagent_solve(
    llm: BaseLLM,
    problem: str,
    prompts: _DatasetPrompts,
    ind: int = 3,
    **format_kw: Any,
) -> Dict[str, Any]:
    """Core EvoAgent loop — shared across all datasets."""
    answer = await _aask(llm, prompts.build_initial(problem, **format_kw))
    descriptions: List[str] = []
    for _ in range(ind):
        try_count = 0
        while True:
            meta = await _aask(llm, prompts.build_meta(problem, answer, descriptions))
            check = await _aask(llm, prompts.build_check(problem, descriptions, meta))
            if prompts.should_retain(check) or try_count > 3:
                descriptions.append(meta.strip())
                break
            try_count += 1
        sub_answer = await _aask(llm, prompts.build_multi(problem, descriptions[-1], **format_kw))
        answer = await _aask(
            llm,
            prompts.build_refine(
                problem,
                answer[:800] if "code" in prompts.refine_fmt else answer,
                descriptions[-1],
                sub_answer,
                **format_kw,
            ),
        )
    return {"response": answer, "experts": descriptions}


# ---------------------------------------------------------------------------
# Evaluation functions
# ---------------------------------------------------------------------------


async def evaluate_evoagent(
    dataset: str,
    model: str = "gemini-2.0-flash",
    dataset_split: str = "test",
    sample: int = -1,
    jsonl_path: Optional[str] = None,
    batch_size: int = 8,
    ind: int = 3,
    h5_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Unified EvoAgent evaluation for all datasets."""
    if dataset == "SciCode":
        return await _evaluate_scicode(model, sample, h5_path, batch_size, ind)

    cfg = DATASET_CONFIGS[dataset]
    prompts = cfg["prompts"]
    track_tokens = cfg.get("track_tokens", False)

    if jsonl_path is None:
        jsonl_path = cfg["data_path"].format(split=dataset_split)

    llm = create_llm(model)
    problems = await load_jsonl_data(jsonl_path)
    if not problems:
        print(f"No problems loaded from {jsonl_path}. Exiting.")
        return
    if sample > 0:
        problems = problems[:sample]

    total_problems = 0
    total_correct = 0
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0

    print(f"Evaluating {len(problems)} {dataset} problems with EvoAgent (ind={ind}, batch size: {batch_size})...")

    for batch_start in range(0, len(problems), batch_size):
        batch = problems[batch_start : batch_start + batch_size]
        cm = getattr(llm, "cost_manager", None)
        batch_cost_before = cm.total_cost if cm else 0.0
        batch_in_before = getattr(cm, "total_prompt_tokens", 0) if cm and track_tokens else 0
        batch_out_before = getattr(cm, "total_completion_tokens", 0) if cm and track_tokens else 0

        batch_tasks = []
        batch_items = []

        for item in batch:
            if dataset == "GPQA":
                problem_text, correct_letter = format_gpqa_with_choices(item)
                item["_correct_letter"] = correct_letter
                task = evoagent_solve(llm, problem_text, prompts, ind=ind)
            elif dataset == "HumanEval":
                problem_text = item.get("prompt", "")
                entry_point = item.get("entry_point", "")
                task = evoagent_solve(llm, problem_text, prompts, ind=ind, entry_point=entry_point)
            elif dataset == "MMLU":
                problem_text = format_mmlu_question(item)
                task = evoagent_solve(llm, problem_text, prompts, ind=ind)
            else:
                # MATH
                problem_text = item.get(cfg["problem_key"], "")
                task = evoagent_solve(llm, problem_text, prompts, ind=ind)

            batch_tasks.append(task)
            batch_items.append(item)

        batch_results = []
        try:
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            for result, item in zip(results, batch_items):
                if isinstance(result, Exception):
                    logger.warning(f"Task failed for item: {result}")
                    batch_results.append((None, item, result))
                else:
                    batch_results.append((result, item, None))
        except Exception as e:
            logger.warning(f"Batch gather failed, falling back to sequential await: {e}")
            for task, item in zip(batch_tasks, batch_items):
                try:
                    result = await task
                    batch_results.append((result, item, None))
                except Exception as task_error:
                    logger.warning(f"Task failed for item: {task_error}")
                    batch_results.append((None, item, task_error))

        for result, item, error in batch_results:
            total_problems += 1
            if error:
                print(f"Error on problem {total_problems}: {error}")
                total_correct += 0
                continue

            response = result["response"]
            pred_text = _extract_string_from_output(response)

            if dataset == "HumanEval":
                entry_point = item.get("entry_point", "")
                test_code = item.get("test", "")
                prompt = item.get("prompt", "")
                code = prepare_humaneval_code(pred_text, entry_point, prompt)
                status, _msg = check_solution(code, test_code, entry_point)
                if status == "PASS":
                    total_correct += 1
            elif dataset == "GPQA":
                expected = item.get("_correct_letter", "")
                predicted = extract_model_answer_gpqa(pred_text)
                score, _ = calculate_gpqa_score(expected, predicted)
                if score > 0:
                    total_correct += 1
            elif dataset == "MMLU":
                expected_answer = item.get("answer", 0)
                predicted_letter = extract_answer_letter(pred_text)
                score, _ = calculate_mmlu_score(expected_answer, predicted_letter)
                if score > 0:
                    total_correct += 1
            else:
                # MATH
                expected = item.get(cfg["expected_key"], "")
                score, _ = cfg["scoring_fn"](expected, pred_text)
                if score > 0:
                    total_correct += 1

        cm = getattr(llm, "cost_manager", None)
        batch_cost_after = cm.total_cost if cm else batch_cost_before
        batch_cost = max(batch_cost_after - batch_cost_before, 0.0)
        total_cost += batch_cost
        accuracy = total_correct / total_problems if total_problems > 0 else 0

        if track_tokens:
            batch_in_after = getattr(cm, "total_prompt_tokens", batch_in_before) if cm else batch_in_before
            batch_out_after = getattr(cm, "total_completion_tokens", batch_out_before) if cm else batch_out_before
            batch_in_tokens = max(batch_in_after - batch_in_before, 0)
            batch_out_tokens = max(batch_out_after - batch_out_before, 0)
            total_input_tokens += batch_in_tokens
            total_output_tokens += batch_out_tokens
            print(
                f"Progress: {total_problems}/{len(problems)} | Accuracy: {accuracy:.3f} | "
                f"Batch Cost: ${batch_cost:.4f} | Total Cost: ${total_cost:.4f} | "
                f"Batch Tokens I/O/T: {batch_in_tokens}/{batch_out_tokens}/{batch_in_tokens + batch_out_tokens} | "
                f"Total Tokens I/O/T: {total_input_tokens}/{total_output_tokens}/{total_input_tokens + total_output_tokens}"
            )
        else:
            print(
                f"Progress: {total_problems}/{len(problems)} | "
                f"{'Pass@1' if dataset == 'HumanEval' else 'Accuracy'}: {accuracy:.3f} | "
                f"Batch Cost: ${batch_cost:.4f} | Total Cost: ${total_cost:.4f}"
            )

    overall_accuracy = total_correct / total_problems if total_problems > 0 else 0
    avg_cost_per_problem = total_cost / total_problems if total_problems > 0 else 0.0

    print("\n" + "=" * 60)
    print(f"--- EvoAgent Evaluation on {dataset} ---")
    metric_name = "Pass@1" if dataset == "HumanEval" else "Overall Accuracy"
    print(f"{metric_name}: {total_correct}/{total_problems} ({overall_accuracy:.2%})")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost per Problem: ${avg_cost_per_problem:.4f}")
    if track_tokens:
        avg_in = total_input_tokens / total_problems if total_problems > 0 else 0
        avg_out = total_output_tokens / total_problems if total_problems > 0 else 0
        print(
            f"Total Tokens I/O/T: {total_input_tokens}/{total_output_tokens}/{total_input_tokens + total_output_tokens}"
        )
        print(f"Avg Tokens per Problem I/O/T: {avg_in:.1f}/{avg_out:.1f}/{avg_in + avg_out:.1f}")
    print("=" * 60)

    result = {
        "overall_accuracy": overall_accuracy,
        "total_correct": total_correct,
        "total_problems": total_problems,
        "total_cost": total_cost,
        "avg_cost_per_problem": avg_cost_per_problem,
    }
    if track_tokens:
        result.update(
            {
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
            }
        )
    return result


# ---------------------------------------------------------------------------
# SciCode — special sub-problem structure
# ---------------------------------------------------------------------------


async def _evaluate_scicode(
    model: str,
    sample: int,
    h5_path: str | None,
    batch_size: int,
    ind: int,
) -> Optional[Dict[str, Any]]:
    if h5_path is None:
        h5_path = DATASET_CONFIGS["SciCode"]["h5_path"]
    jsonl_path = DATASET_CONFIGS["SciCode"]["data_path"]
    prompts = DATASET_CONFIGS["SciCode"]["prompts"]

    llm = create_llm(model)
    scicode_benchmark = ScicodeBenchmark(
        name="scicode",
        file_path=jsonl_path,
        log_path="",
        batch_size=batch_size,
        controller=torch.nn.Module(),
        operator_embeddings=torch.empty(0),
        optimizer=None,
        h5py_file=h5_path,
    )

    problems = await scicode_benchmark.load_data()
    if not problems:
        print(f"No problems loaded from {jsonl_path}. Exiting.")
        return
    if sample > 0:
        problems = problems[:sample]

    total_problems = 0
    total_correct_problems = 0
    total_subproblems = 0
    total_correct_subproblems = 0
    total_cost = 0.0

    for start_idx in range(0, len(problems), batch_size):
        batch = problems[start_idx : start_idx + batch_size]
        for problem in batch:
            total_problems += 1
            problem["problem_id"] = str(problem["problem_id"])
            sub_steps = problem.get("sub_steps", [])
            if not sub_steps:
                continue

            problem_id_str = str(problem.get("problem_id", ""))
            skip_indices = SCICODE_SKIP_INDICES.get(problem_id_str, set())
            num_sub_steps = len(sub_steps)
            previous_llm_code = [""] * num_sub_steps
            correct_subproblems_count = 0

            cm = getattr(llm, "cost_manager", None)
            cost_before = cm.total_cost if cm else 0.0

            for idx in range(num_sub_steps):
                if idx in skip_indices:
                    print(f"SKIPPING Problem {problem_id_str} sub-step {idx + 1}")
                    continue

                _clean_query, base_prompt = scicode_benchmark.get_subproblem_prompt(problem, idx, previous_llm_code)
                result = await evoagent_solve(llm, base_prompt, prompts, ind=ind)
                response = result["response"]
                extracted_code = scicode_benchmark._extract_python_script(response)
                if extracted_code:
                    previous_llm_code[idx] = extracted_code
                is_correct, _ = await scicode_benchmark.test_subproblem(problem, previous_llm_code, idx)
                if is_correct:
                    correct_subproblems_count += 1

            cm = getattr(llm, "cost_manager", None)
            cost_after = cm.total_cost if cm else cost_before
            problem_cost = max(cost_after - cost_before, 0.0)
            total_cost += problem_cost

            num_eval_steps = num_sub_steps - len(skip_indices)
            total_subproblems += num_eval_steps
            total_correct_subproblems += correct_subproblems_count
            if correct_subproblems_count == num_eval_steps:
                total_correct_problems += 1

            print(
                f"Problem {problem['problem_id']}: {correct_subproblems_count}/{num_eval_steps} subproblems correct "
                f"(skipped {len(skip_indices)}). cost={problem_cost:.4f}"
            )

    problem_pass_rate = total_correct_problems / total_problems if total_problems > 0 else 0
    subproblem_pass_rate = total_correct_subproblems / total_subproblems if total_subproblems > 0 else 0
    avg_cost = total_cost / total_problems if total_problems > 0 else 0.0
    avg_cost_sub = total_cost / total_subproblems if total_subproblems > 0 else 0.0

    print("--- EvoAgent Evaluation on SciCode ---")
    print(f"Problem Pass Rate: {total_correct_problems}/{total_problems} ({problem_pass_rate:.2%})")
    print(f"Subproblem Pass Rate: {total_correct_subproblems}/{total_subproblems} ({subproblem_pass_rate:.2%})")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost per Problem: ${avg_cost:.4f}")
    print(f"Average Cost per Subproblem: ${avg_cost_sub:.4f}")
    print("-" * 41)
    return {
        "problem_pass_rate": problem_pass_rate,
        "subproblem_pass_rate": subproblem_pass_rate,
        "total_cost": total_cost,
        "avg_cost_per_problem": avg_cost,
        "avg_cost_per_subproblem": avg_cost_sub,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified EvoAgent evaluation.")
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["MATH", "GPQA", "HumanEval", "MMLU", "SciCode"],
        help="Dataset to evaluate",
    )
    parser.add_argument("--model", default="gemini-2.0-flash", help="LLM model to use")
    parser.add_argument(
        "--dataset_split",
        choices=["train", "test"],
        default="test",
        help="Dataset split to evaluate",
    )
    parser.add_argument("--sample", type=int, default=-1, help="Number of problems to evaluate (-1 for all)")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for processing")
    parser.add_argument("--jsonl_path", default=None, help="Override default JSONL data path")
    parser.add_argument("--ind", type=int, default=3, help="Number of EvoAgent iterations")
    parser.add_argument(
        "--h5_path",
        default=None,
        help="Path to the SciCode HDF5 file (SciCode only)",
    )
    args = parser.parse_args()

    asyncio.run(
        evaluate_evoagent(
            dataset=args.dataset,
            model=args.model,
            dataset_split=args.dataset_split,
            sample=args.sample,
            jsonl_path=args.jsonl_path,
            batch_size=args.batch_size,
            ind=args.ind,
            h5_path=args.h5_path,
        )
    )


if __name__ == "__main__":
    main()
