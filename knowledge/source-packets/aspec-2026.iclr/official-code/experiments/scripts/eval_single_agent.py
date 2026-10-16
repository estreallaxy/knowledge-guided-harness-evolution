"""Unified single agent evaluation script for all datasets.

Replaces:
  - eval_math_single_agent.py
  - eval_gpqa_single_agent.py
  - eval_humaneval_single_agent.py
  - eval_mmlu_single_agent.py
  - eval_scicode_single_agent.py

Usage:
  python -m experiments.scripts.eval_single_agent --dataset MATH --mode base
  python -m experiments.scripts.eval_single_agent --dataset GPQA --mode role
  python -m experiments.scripts.eval_single_agent --dataset HumanEval --mode reflexion
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
from typing import Any, Dict, List, Optional, Tuple

import torch
from loguru import logger

from aspec.llm import BaseLLM
from experiments.lib import scoring
from experiments.lib.eval_utils import (
    _extract_string_from_output,
    create_llm,
    load_jsonl_data,
    retry_with_backoff,
)
from experiments.lib.reflexion import ReflexionAgent

# ---------------------------------------------------------------------------
# Per-dataset configuration
# ---------------------------------------------------------------------------

DATASET_CONFIGS: Dict[str, Dict[str, Any]] = {
    "MATH": {
        "operator_path": "experiments.datasets.MATH.train.template.operator",
        "operator_cls": "CoT",
        "data_path": "data/math_test.jsonl",
        "data_path_template": "data/math_{split}.jsonl",
        "problem_key": "problem",
        "expected_key": "solution",
        "metric_name": "Accuracy",
        "default_roles": ["Algebraist", "Number Theorist", "Real Analyst", "Statistician", "Logicist"],
        "memory_file": "reflexion_memory_math.txt",
        "domain_hint": "math problems",
        "role_select_domain": "solve the problem",
        "role_answer_template": (
            "You are {role}. Solve the following math problem. "
            "Strict answer policy:\n - Output EXACTLY the answer string with no prefixes/suffixes.\n"
            " - Append a final line with the canonical math format: $$\\boxed{{<final answer only>}}$$."
            "Problem:\n{problem}"
        ),
        "default_model": "llama",
    },
    "GPQA": {
        "operator_path": "experiments.datasets.GPQA.train.template.operator",
        "operator_cls": "SelfConsistency",
        "data_path": "data/gpqa_test.jsonl",
        "data_path_template": "data/gpqa_{split}.jsonl",
        "problem_key": None,  # Uses format_question_fn
        "expected_key": "_correct_letter",
        "metric_name": "Accuracy",
        "default_roles": [
            "Physics Expert",
            "Chemistry Expert",
            "Biology Expert",
            "Scientific Reasoning Expert",
            "Graduate Student",
        ],
        "memory_file": "reflexion_memory_gpqa.txt",
        "domain_hint": "graduate-level physics problems",
        "role_select_domain": "solve the physics/science problem",
        "role_answer_template": (
            "You are a {role}. Solve the following graduate-level physics problem. "
            "Think step by step and choose the correct answer from the given options.\n"
            "Output your final answer as a single letter (A, B, C, or D).\n\n"
            "Problem:\n{problem}"
        ),
        "default_model": "llama",
    },
    "HumanEval": {
        "operator_path": "experiments.datasets.HumanEval.train.template.operator",
        "operator_cls": "CoT",
        "data_path": "data/humaneval_test.jsonl",
        "data_path_template": "data/humaneval_{split}.jsonl",
        "problem_key": "prompt",
        "expected_key": None,  # Uses code execution
        "metric_name": "Pass@1",
        "default_roles": [
            "Senior Python Engineer",
            "Algorithms Expert",
            "Software Architect",
            "Data Scientist",
            "Competitive Programmer",
        ],
        "memory_file": "reflexion_memory_humaneval.txt",
        "domain_hint": "coding problems",
        "role_select_domain": "implement the required Python function",
        "role_answer_template": (
            "You are {role}. Write Python code that correctly implements the required function(s). "
            "Ensure the exact entry point `{entry_point}` is defined and correct. "
            "Respond with only the code in a single fenced Python block.\n\n"
            "Task:\n{problem}"
        ),
        "default_model": "deepseek/deepseek-chat-v3.1:free",
    },
    "MMLU": {
        "operator_path": "experiments.datasets.MMLU.train.template.operator",
        "operator_cls": "SelfRefine",
        "data_path": "data/mmlu_test.jsonl",
        "data_path_template": "data/mmlu_{split}.jsonl",
        "problem_key": None,  # Uses format_question_fn
        "expected_key": "answer",
        "metric_name": "Accuracy",
        "default_roles": ["Biologist", "Physicist", "Mathematician", "Engineer", "Doctor", "Lawyer"],
        "memory_file": "reflexion_memory_mmlu.txt",
        "domain_hint": "multiple-choice questions",
        "role_select_domain": "answer the multiple-choice question",
        "role_answer_template": (
            "You are {role}. Carefully analyze and answer the multiple-choice question. "
            "Respond concisely and explicitly state the final choice as: 'The final answer is: X' "
            "and optionally include <final_answer>X</final_answer>.\n\n"
            "Question:\n{problem}"
        ),
        "default_model": "gemini-2.0-flash",
    },
    "SciCode": {
        "operator_path": "experiments.datasets.SciCode.train.template.operator",
        "operator_cls": "CoT",
        "data_path": "data/scicode_test.jsonl",
        "data_path_template": None,  # Always uses data/scicode_test.jsonl
        "problem_key": None,  # Uses ScicodeBenchmark
        "expected_key": None,  # Uses ScicodeBenchmark
        "metric_name": "Pass Rate",
        "default_roles": ["Biologist", "Physicist", "Chemist", "Computer Scientist", "Mathematician"],
        "memory_file": "reflexion_memory_scicode.txt",
        "domain_hint": "scientific programming problems",
        "role_select_domain": "solve the programming task and write Python code",
        "role_answer_template": (
            "You are {role}. Write correct, efficient Python code to solve the task. "
            "Return only a single Python code block containing the full solution.\n\n"
            "Task:\n{problem}"
        ),
        "default_model": "gemini-2.0-flash",
    },
}

SCICODE_SKIP_INDICES: Dict[str, set[int]] = {"13": {5}, "62": {0}, "76": {2}}


def _resolve_jsonl_path(cfg: Dict[str, Any], jsonl_path: Optional[str], dataset_split: str) -> str:
    if jsonl_path is None:
        if cfg["data_path_template"]:
            jsonl_path = cfg["data_path_template"].format(split=dataset_split)
        else:
            jsonl_path = cfg["data_path"]
    return jsonl_path


async def _gather_batch(
    batch_tasks: List[Any], batch_items: List[Dict[str, Any]]
) -> List[Tuple[Any, Dict[str, Any], Optional[BaseException]]]:
    batch_results: List[Tuple[Any, Dict[str, Any], Optional[BaseException]]] = []
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
    return batch_results


# ---------------------------------------------------------------------------
# Role assignment helpers
# ---------------------------------------------------------------------------


def _parse_selected_role(text: str, roles: List[str]) -> str:
    s = str(text).lower()
    for r in roles:
        if r.lower() in s:
            return r
    return roles[0] if roles else "Expert"


def _build_role_select_prompt(problem: str, roles: List[str], domain: str) -> str:
    role_list = "\n".join([f"- {r}" for r in roles])
    return (
        f"Choose the single best role from the list to {domain}.\n"
        f"Roles:\n{role_list}\n\n"
        f"Problem:\n{problem}\n\n"
        "Respond with only the exact role name."
    )


# ---------------------------------------------------------------------------
# Evaluation: CoT mode
# ---------------------------------------------------------------------------


async def evaluate_base(
    dataset: str,
    model: str,
    dataset_split: str,
    sample: int,
    batch_size: int,
    jsonl_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Evaluate using dataset-specific operator (CoT, SelfConsistency, SelfRefine)."""
    cfg = DATASET_CONFIGS[dataset]

    jsonl_path = _resolve_jsonl_path(cfg, jsonl_path, dataset_split)

    llm = create_llm(model)

    # Import and instantiate operator
    mod = importlib.import_module(cfg["operator_path"])
    operator_cls = getattr(mod, cfg["operator_cls"])
    base_operator = operator_cls(llm)

    # Handle SciCode separately
    if dataset == "SciCode":
        return await _evaluate_base_scicode(llm, base_operator, jsonl_path, sample, batch_size)

    # Load data
    problems = await load_jsonl_data(jsonl_path)
    if not problems:
        print(f"No problems loaded from {jsonl_path}. Exiting.")
        return
    if sample > 0:
        problems = problems[:sample]

    total_problems = 0
    total_correct = 0
    total_cost = 0.0
    subject_stats: Dict[str, Dict[str, int]] = {}

    print(
        f"Evaluating {len(problems)} {dataset} problems with {cfg['operator_cls']} operator (batch size: {batch_size})..."
    )

    for batch_start in range(0, len(problems), batch_size):
        batch = problems[batch_start : batch_start + batch_size]
        cm = getattr(llm, "cost_manager", None)
        batch_cost_before = cm.total_cost if cm else 0.0

        batch_tasks = []
        batch_items = []

        for item in batch:
            if dataset == "GPQA":
                formatted, correct_letter = scoring.format_gpqa_with_choices(item)
                item["_correct_letter"] = correct_letter
                prompt_text = formatted + "\nChoose the correct answer (A, B, C, or D)."
            elif dataset == "MMLU":
                prompt_text = scoring.format_mmlu_question(item)
            else:
                prompt_text = item.get(cfg["problem_key"], "")

            task = retry_with_backoff(base_operator, problem=prompt_text)
            batch_tasks.append(task)
            batch_items.append(item)

        batch_results = await _gather_batch(batch_tasks, batch_items)

        for result, item, error in batch_results:
            total_problems += 1

            if error:
                print(f"Error on problem {total_problems}: {error}")
                score = 0
            elif dataset == "HumanEval":
                entry_point = item.get("entry_point", "")
                test_code = item.get("test", "")
                prompt = item.get("prompt", "")
                response = result["response"]
                code = scoring.prepare_humaneval_code(response, entry_point, prompt)
                status, _msg = scoring.check_solution(code, test_code, entry_point)
                score = 1 if status == "PASS" else 0
            elif dataset == "GPQA":
                response = result["response"]
                pred_text = _extract_string_from_output(response)
                predicted = scoring.extract_model_answer_gpqa(pred_text)
                score, _ = scoring.calculate_gpqa_score(item.get("_correct_letter", ""), predicted)
            elif dataset == "MMLU":
                response = result["response"]
                predicted_letter = scoring.extract_answer_letter(response)
                score, _ = scoring.calculate_mmlu_score(item.get("answer", 0), predicted_letter)
                subject = item.get("subject", "unknown")
                if subject not in subject_stats:
                    subject_stats[subject] = {"correct": 0, "total": 0}
                subject_stats[subject]["total"] += 1
                if score > 0:
                    subject_stats[subject]["correct"] += 1
            else:  # MATH
                response = result["response"]
                pred_text = _extract_string_from_output(response)
                score, _ = scoring.calculate_math_score(item.get(cfg["expected_key"], ""), pred_text)

            if score > 0:
                total_correct += 1

        cm = getattr(llm, "cost_manager", None)
        batch_cost_after = cm.total_cost if cm else batch_cost_before
        batch_cost = max(batch_cost_after - batch_cost_before, 0.0)
        total_cost += batch_cost
        accuracy = total_correct / total_problems if total_problems > 0 else 0
        print(
            f"Progress: {total_problems}/{len(problems)} | {cfg['metric_name']}: {accuracy:.3f} | Batch Cost: ${batch_cost:.4f} | Total Cost: ${total_cost:.4f}"
        )

    overall_accuracy = total_correct / total_problems if total_problems > 0 else 0
    avg_cost = total_cost / total_problems if total_problems > 0 else 0.0

    print("\n" + "=" * 60)
    print(f"--- Direct {cfg['operator_cls']} Evaluation on {dataset} ---")
    print(f"Overall {cfg['metric_name']}: {total_correct}/{total_problems} ({overall_accuracy:.2%})")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost per Problem: ${avg_cost:.4f}")
    if subject_stats:
        print("\nBy Subject:")
        print("-" * 40)
        for subject, stats in sorted(subject_stats.items()):
            subj_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"{subject}: {stats['correct']}/{stats['total']} ({subj_acc:.2%})")
    print("=" * 60)

    return {
        "overall_accuracy": overall_accuracy,
        "total_correct": total_correct,
        "total_problems": total_problems,
        "total_cost": total_cost,
        "avg_cost_per_problem": avg_cost,
    }


async def _evaluate_base_scicode(
    llm: BaseLLM, base_operator: Any, jsonl_path: str, sample: int, batch_size: int
) -> Optional[Dict[str, Any]]:
    """SciCode-specific evaluation with sub-problem structure."""
    from aspec.benchmarks.scicode import ScicodeBenchmark

    h5_path = "data/scicode_test_data.h5"
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
                _clean_query, prompt = scicode_benchmark.get_subproblem_prompt(problem, idx, previous_llm_code)
                result = await base_operator(problem=prompt)
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
                f"Problem {problem['problem_id']}: {correct_subproblems_count}/{num_eval_steps} subproblems correct (skipped {len(skip_indices)}). cost={problem_cost:.4f}"
            )

    problem_pass_rate = total_correct_problems / total_problems if total_problems > 0 else 0
    subproblem_pass_rate = total_correct_subproblems / total_subproblems if total_subproblems > 0 else 0

    print("--- Direct CoT Evaluation on SciCode ---")
    print(f"Problem Pass Rate: {total_correct_problems}/{total_problems} ({problem_pass_rate:.2%})")
    print(f"Subproblem Pass Rate: {total_correct_subproblems}/{total_subproblems} ({subproblem_pass_rate:.2%})")
    print(f"Total Cost: {total_cost:.4f}")
    print("-----------------------------------------")

    return {
        "problem_pass_rate": problem_pass_rate,
        "subproblem_pass_rate": subproblem_pass_rate,
        "total_cost": total_cost,
    }


# ---------------------------------------------------------------------------
# Evaluation: Role assignment mode
# ---------------------------------------------------------------------------


async def evaluate_role_assignment(
    dataset: str,
    model: str,
    dataset_split: str,
    sample: int,
    batch_size: int,
    jsonl_path: Optional[str] = None,
    roles: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Evaluate with role-based assignment."""
    cfg = DATASET_CONFIGS[dataset]

    jsonl_path = _resolve_jsonl_path(cfg, jsonl_path, dataset_split)

    llm = create_llm(model)
    roles = roles or cfg["default_roles"]

    # Handle SciCode separately
    if dataset == "SciCode":
        return await _evaluate_role_scicode(llm, jsonl_path, sample, batch_size, roles, cfg)

    problems = await load_jsonl_data(jsonl_path)
    if not problems:
        print(f"No problems loaded from {jsonl_path}. Exiting.")
        return
    if sample > 0:
        problems = problems[:sample]

    total_problems = 0
    total_correct = 0
    total_cost = 0.0

    print(f"Evaluating {len(problems)} {dataset} problems with Role-Assignment (batch size: {batch_size})...")

    for batch_start in range(0, len(problems), batch_size):
        batch = problems[batch_start : batch_start + batch_size]
        cm = getattr(llm, "cost_manager", None)
        batch_cost_before = cm.total_cost if cm else 0.0

        batch_tasks = []
        batch_items = []

        async def _solve_item(item: Dict[str, Any]) -> Dict[str, Any]:
            if dataset == "GPQA":
                formatted, correct_letter = scoring.format_gpqa_with_choices(item)
                item["_correct_letter"] = correct_letter
                problem_text = formatted
            elif dataset == "MMLU":
                problem_text = scoring.format_mmlu_question(item)
            else:
                problem_text = item.get(cfg["problem_key"], "")

            select_prompt = _build_role_select_prompt(problem_text, roles, cfg["role_select_domain"])
            role_resp = await retry_with_backoff(llm.aask, select_prompt)
            chosen_role = _parse_selected_role(role_resp, roles)

            entry_point = item.get("entry_point", "") if dataset == "HumanEval" else ""
            answer_prompt = cfg["role_answer_template"].format(
                role=chosen_role, problem=problem_text, entry_point=entry_point
            )
            answer_resp = await retry_with_backoff(llm.aask, answer_prompt)
            return {"response": answer_resp, "role": chosen_role}

        for item in batch:
            batch_tasks.append(_solve_item(item))
            batch_items.append(item)

        batch_results = await _gather_batch(batch_tasks, batch_items)

        for result, item, error in batch_results:
            total_problems += 1
            if error:
                print(f"Error on problem {total_problems}: {error}")
                score = 0
            elif dataset == "HumanEval":
                entry_point = item.get("entry_point", "")
                test_code = item.get("test", "")
                prompt = item.get("prompt", "")
                code = scoring.prepare_humaneval_code(result["response"], entry_point, prompt)
                status, _msg = scoring.check_solution(code, test_code, entry_point)
                score = 1 if status == "PASS" else 0
            elif dataset == "GPQA":
                pred_text = _extract_string_from_output(result["response"])
                predicted = scoring.extract_model_answer_gpqa(pred_text)
                score, _ = scoring.calculate_gpqa_score(item.get("_correct_letter", ""), predicted)
            elif dataset == "MMLU":
                predicted_letter = scoring.extract_answer_letter(result["response"])
                score, _ = scoring.calculate_mmlu_score(item.get("answer", 0), predicted_letter)
            else:
                pred_text = _extract_string_from_output(result["response"])
                score, _ = scoring.calculate_math_score(item.get(cfg["expected_key"], ""), pred_text)

            if score > 0:
                total_correct += 1

        cm = getattr(llm, "cost_manager", None)
        batch_cost_after = cm.total_cost if cm else batch_cost_before
        batch_cost = max(batch_cost_after - batch_cost_before, 0.0)
        total_cost += batch_cost
        accuracy = total_correct / total_problems if total_problems > 0 else 0
        print(
            f"Progress: {total_problems}/{len(problems)} | {cfg['metric_name']}: {accuracy:.3f} | Batch Cost: ${batch_cost:.4f} | Total Cost: ${total_cost:.4f}"
        )

    overall_accuracy = total_correct / total_problems if total_problems > 0 else 0
    avg_cost = total_cost / total_problems if total_problems > 0 else 0.0

    print("\n" + "=" * 60)
    print(f"--- Role-Assignment Evaluation on {dataset} ---")
    print(f"Overall {cfg['metric_name']}: {total_correct}/{total_problems} ({overall_accuracy:.2%})")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost per Problem: ${avg_cost:.4f}")
    print("=" * 60)

    return {
        "overall_accuracy": overall_accuracy,
        "total_correct": total_correct,
        "total_problems": total_problems,
        "total_cost": total_cost,
        "avg_cost_per_problem": avg_cost,
    }


async def _evaluate_role_scicode(
    llm: BaseLLM,
    jsonl_path: str,
    sample: int,
    batch_size: int,
    roles: List[str],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """SciCode role assignment with sub-problem structure."""
    from aspec.benchmarks.scicode import ScicodeBenchmark

    mod = importlib.import_module(cfg["operator_path"])
    operator_cls = getattr(mod, cfg["operator_cls"])
    base_operator = operator_cls(llm)

    h5_path = "data/scicode_test_data.h5"
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

            first_valid_idx = next((i for i in range(num_sub_steps) if i not in skip_indices), None)
            if first_valid_idx is None:
                print(f"Problem {problem_id_str}: all sub-steps skipped")
                continue

            _clean_query, context_prompt = scicode_benchmark.get_subproblem_prompt(
                problem, first_valid_idx, previous_llm_code
            )
            select_prompt = _build_role_select_prompt(context_prompt, roles, cfg["role_select_domain"])
            role_resp = await llm.aask(select_prompt)
            chosen_role = _parse_selected_role(role_resp, roles)

            for idx in range(num_sub_steps):
                if idx in skip_indices:
                    print(f"SKIPPING Problem {problem_id_str} sub-step {idx + 1}")
                    continue
                _clean_query, base_prompt = scicode_benchmark.get_subproblem_prompt(problem, idx, previous_llm_code)
                prompt = cfg["role_answer_template"].format(role=chosen_role, problem=base_prompt, entry_point="")
                result = await base_operator(problem=prompt)
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
                f"Problem {problem['problem_id']}: role={chosen_role} | {correct_subproblems_count}/{num_eval_steps} subproblems correct (skipped {len(skip_indices)}). cost={problem_cost:.4f}"
            )

    problem_pass_rate = total_correct_problems / total_problems if total_problems > 0 else 0
    subproblem_pass_rate = total_correct_subproblems / total_subproblems if total_subproblems > 0 else 0

    print("--- Role-Assignment Evaluation on SciCode ---")
    print(f"Problem Pass Rate: {total_correct_problems}/{total_problems} ({problem_pass_rate:.2%})")
    print(f"Subproblem Pass Rate: {total_correct_subproblems}/{total_subproblems} ({subproblem_pass_rate:.2%})")
    print(f"Total Cost: {total_cost:.4f}")
    print("-----------------------------------------")

    return {
        "problem_pass_rate": problem_pass_rate,
        "subproblem_pass_rate": subproblem_pass_rate,
        "total_cost": total_cost,
    }


# ---------------------------------------------------------------------------
# Evaluation: Reflexion mode
# ---------------------------------------------------------------------------


async def evaluate_reflexion(
    dataset: str,
    model: str,
    dataset_split: str,
    sample: int,
    batch_size: int,
    jsonl_path: Optional[str] = None,
    memory_file: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Evaluate with Reflexion baseline."""
    cfg = DATASET_CONFIGS[dataset]

    jsonl_path = _resolve_jsonl_path(cfg, jsonl_path, dataset_split)

    memory_file = memory_file or cfg["memory_file"]
    llm = create_llm(model)

    agent = ReflexionAgent(llm, memory_file, dataset_name=dataset, domain_hint=cfg["domain_hint"])

    # Handle SciCode separately
    if dataset == "SciCode":
        return await _evaluate_reflexion_scicode(llm, agent, jsonl_path, sample, batch_size, memory_file)

    problems = await load_jsonl_data(jsonl_path)
    if not problems:
        print(f"No problems loaded from {jsonl_path}. Exiting.")
        return
    if sample > 0:
        problems = problems[:sample]

    total_problems = 0
    total_correct = 0
    total_cost = 0.0
    subject_stats: Dict[str, Dict[str, int]] = {}

    print(f"Evaluating {len(problems)} {dataset} problems with Reflexion baseline (batch size: {batch_size})...")
    print(f"Memory file: {memory_file}")

    for batch_start in range(0, len(problems), batch_size):
        batch = problems[batch_start : batch_start + batch_size]
        batch_cost_before = llm.cost_manager.total_cost

        batch_tasks = []
        batch_items = []

        for item in batch:
            if dataset == "GPQA":
                formatted, correct_letter = scoring.format_gpqa_with_choices(item)
                item["_correct_letter"] = correct_letter
                problem_text = formatted + "\nChoose the correct answer (A, B, C, or D)."
                ground_truth = correct_letter
            elif dataset == "MMLU":
                problem_text = scoring.format_mmlu_question(item)
                ground_truth = str(item.get("answer", 0))
            elif dataset == "HumanEval":
                problem_text = item.get("prompt", "")
                ground_truth = item.get("entry_point", "") or "unknown"
            else:
                problem_text = item.get(cfg["problem_key"], "")
                ground_truth = item.get("solution", "")

            # Build score_fn based on dataset
            if dataset == "MATH":
                score_fn = scoring.calculate_math_score
            elif dataset == "GPQA":

                def _gpqa_score(gt: str, resp: str) -> Tuple[float, str]:
                    pred = scoring.extract_model_answer_gpqa(resp)
                    return scoring.calculate_gpqa_score(gt, pred)

                score_fn = _gpqa_score
            elif dataset == "MMLU":

                def _mmlu_score(gt: str, resp: str) -> Tuple[float, str]:
                    pred = scoring.extract_answer_letter(resp)
                    return scoring.calculate_mmlu_score(int(gt), pred)

                score_fn = _mmlu_score
            elif dataset == "HumanEval":
                entry_point = item.get("entry_point", "")
                test_code = item.get("test", "")
                prompt_text = item.get("prompt", "")

                def _humaneval_score(
                    gt: str,
                    resp: str,
                    _entry_point: str = entry_point,
                    _test: str = test_code,
                    _prompt: str = prompt_text,
                ) -> Tuple[float, str]:
                    code = scoring.prepare_humaneval_code(resp, _entry_point, _prompt)
                    status, _msg = scoring.check_solution(code, _test, _entry_point)
                    return (1.0 if status == "PASS" else 0.0), code

                score_fn = _humaneval_score
            else:
                score_fn = None

            task = agent.solve_with_reflection(problem_text, ground_truth, score_fn=score_fn)
            batch_tasks.append(task)
            batch_items.append(item)

        batch_results = await _gather_batch(batch_tasks, batch_items)

        for result, item, error in batch_results:
            total_problems += 1
            if error:
                print(f"Error on problem {total_problems}: {error}")
                score = 0
            elif dataset == "HumanEval":
                response, _ = result
                entry_point = item.get("entry_point", "")
                test_code = item.get("test", "")
                prompt = item.get("prompt", "")
                code = scoring.prepare_humaneval_code(response, entry_point, prompt)
                status, _msg = scoring.check_solution(code, test_code, entry_point)
                score = 1 if status == "PASS" else 0
            elif dataset == "GPQA":
                response, _ = result
                predicted = scoring.extract_model_answer_gpqa(response)
                score, _ = scoring.calculate_gpqa_score(item.get("_correct_letter", ""), predicted)
            elif dataset == "MMLU":
                response, _ = result
                predicted_letter = scoring.extract_answer_letter(response)
                score, _ = scoring.calculate_mmlu_score(item.get("answer", 0), predicted_letter)
                subject = item.get("subject", "unknown")
                if subject not in subject_stats:
                    subject_stats[subject] = {"correct": 0, "total": 0}
                subject_stats[subject]["total"] += 1
                if score > 0:
                    subject_stats[subject]["correct"] += 1
            else:
                response, _ = result
                score, _ = scoring.calculate_math_score(item.get("solution", ""), response)

            if score > 0:
                total_correct += 1

        batch_cost_after = llm.cost_manager.total_cost
        batch_cost = max(batch_cost_after - batch_cost_before, 0.0)
        total_cost += batch_cost
        accuracy = total_correct / total_problems if total_problems > 0 else 0
        print(
            f"Progress: {total_problems}/{len(problems)} | {cfg['metric_name']}: {accuracy:.3f} | Batch Cost: ${batch_cost:.4f} | Total Cost: ${total_cost:.4f}"
        )

    overall_accuracy = total_correct / total_problems if total_problems > 0 else 0
    avg_cost = total_cost / total_problems if total_problems > 0 else 0.0

    print("\n" + "=" * 60)
    print(f"--- Reflexion Baseline Evaluation on {dataset} ---")
    print(f"Overall {cfg['metric_name']}: {total_correct}/{total_problems} ({overall_accuracy:.2%})")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Average Cost per Problem: ${avg_cost:.4f}")
    print(f"Memory file: {memory_file}")
    if subject_stats:
        print("\nBy Subject:")
        print("-" * 40)
        for subject, stats in sorted(subject_stats.items()):
            subj_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"{subject}: {stats['correct']}/{stats['total']} ({subj_acc:.2%})")
    print("=" * 60)

    return {
        "overall_accuracy": overall_accuracy,
        "total_correct": total_correct,
        "total_problems": total_problems,
        "total_cost": total_cost,
        "avg_cost_per_problem": avg_cost,
        "memory_file": memory_file,
    }


async def _evaluate_reflexion_scicode(
    llm: BaseLLM,
    agent: ReflexionAgent,
    jsonl_path: str,
    sample: int,
    batch_size: int,
    memory_file: str,
) -> Optional[Dict[str, Any]]:
    """SciCode reflexion with sub-problem structure."""
    from aspec.benchmarks.scicode import ScicodeBenchmark

    h5_path = "data/scicode_test_data.h5"
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

    print(f"Evaluating {len(problems)} SciCode problems with Reflexion baseline (batch size: {batch_size})...")
    print(f"Memory file: {memory_file}")

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

            cost_before = llm.cost_manager.total_cost

            for idx in range(num_sub_steps):
                if idx in skip_indices:
                    print(f"SKIPPING Problem {problem_id_str} sub-step {idx + 1}")
                    continue

                _clean_query, prompt = scicode_benchmark.get_subproblem_prompt(problem, idx, previous_llm_code)

                # Test before to get feedback for reflection
                is_correct, test_result = await scicode_benchmark.test_subproblem(problem, previous_llm_code, idx)

                result, _ = await agent.solve_with_reflection(prompt, str(is_correct))
                extracted_code = scicode_benchmark._extract_python_script(result)
                if extracted_code:
                    previous_llm_code[idx] = extracted_code

                is_correct, _ = await scicode_benchmark.test_subproblem(problem, previous_llm_code, idx)
                if is_correct:
                    correct_subproblems_count += 1

            cost_after = llm.cost_manager.total_cost
            problem_cost = max(cost_after - cost_before, 0.0)
            total_cost += problem_cost

            num_eval_steps = num_sub_steps - len(skip_indices)
            total_subproblems += num_eval_steps
            total_correct_subproblems += correct_subproblems_count
            if correct_subproblems_count == num_eval_steps:
                total_correct_problems += 1

            print(
                f"Problem {problem['problem_id']}: {correct_subproblems_count}/{num_eval_steps} subproblems correct (skipped {len(skip_indices)}). cost={problem_cost:.4f}"
            )

    problem_pass_rate = total_correct_problems / total_problems if total_problems > 0 else 0
    subproblem_pass_rate = total_correct_subproblems / total_subproblems if total_subproblems > 0 else 0

    print("\n" + "=" * 60)
    print("--- Reflexion Baseline Evaluation on SciCode ---")
    print(f"Problem Pass Rate: {total_correct_problems}/{total_problems} ({problem_pass_rate:.2%})")
    print(f"Subproblem Pass Rate: {total_correct_subproblems}/{total_subproblems} ({subproblem_pass_rate:.2%})")
    print(f"Total Cost: {total_cost:.4f}")
    print(f"Memory file: {memory_file}")
    print("=" * 60)

    return {
        "problem_pass_rate": problem_pass_rate,
        "subproblem_pass_rate": subproblem_pass_rate,
        "total_cost": total_cost,
        "memory_file": memory_file,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _get_available_operators(operator_path: str) -> List[str]:
    """Return the list of operator class names available in a dataset's operator module."""
    mod = importlib.import_module(operator_path)
    base_cls = getattr(mod, "BaseOperator", None)
    if base_cls is None:
        print(f"ERROR: BaseOperator not found in {operator_path}. Cannot determine available operators.")
        raise SystemExit(1)
    return sorted(
        name
        for name in dir(mod)
        if not name.startswith("_")
        and isinstance(getattr(mod, name, None), type)
        and issubclass(getattr(mod, name), base_cls)
        and name != "BaseOperator"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified single agent evaluation for all datasets.")
    parser.add_argument("--dataset", required=True, choices=list(DATASET_CONFIGS.keys()), help="Dataset to evaluate")
    parser.add_argument("--mode", choices=["base", "role", "reflexion"], default="base", help="Evaluation mode")
    parser.add_argument(
        "--operator",
        default=None,
        help="Operator class name (e.g. CoT, SelfConsistency, SelfRefine, Debate). Must exist in the dataset's operator module.",
    )
    parser.add_argument("--model", default=None, help="LLM model to use (default: per-dataset)")
    parser.add_argument("--dataset_split", choices=["train", "test"], default="test", help="Dataset split")
    parser.add_argument("--sample", type=int, default=-1, help="Number of problems (-1 for all)")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size for processing")
    parser.add_argument("--jsonl_path", default=None, help="Override data file path")
    parser.add_argument("--roles", default=None, help="Comma-separated role names for role-assignment")
    parser.add_argument("--memory_file", default=None, help="Memory file path for Reflexion mode")

    args = parser.parse_args()

    cfg = DATASET_CONFIGS[args.dataset]

    # Resolve and validate operator
    if args.operator is not None:
        mod = importlib.import_module(cfg["operator_path"])
        if not hasattr(mod, args.operator):
            available = _get_available_operators(cfg["operator_path"])
            parser.error(
                f"Operator '{args.operator}' not found in {cfg['operator_path']}. "
                f"Available operators: {', '.join(sorted(available))}"
            )
        cfg["operator_cls"] = args.operator

    model = args.model or cfg["default_model"]

    roles_list = None
    if args.roles:
        roles_list = [r.strip() for r in args.roles.split(",") if r.strip()]

    if args.mode == "base":
        asyncio.run(
            evaluate_base(
                dataset=args.dataset,
                model=model,
                dataset_split=args.dataset_split,
                sample=args.sample,
                batch_size=args.batch_size,
                jsonl_path=args.jsonl_path,
            )
        )
    elif args.mode == "role":
        asyncio.run(
            evaluate_role_assignment(
                dataset=args.dataset,
                model=model,
                dataset_split=args.dataset_split,
                sample=args.sample,
                batch_size=args.batch_size,
                jsonl_path=args.jsonl_path,
                roles=roles_list,
            )
        )
    else:
        asyncio.run(
            evaluate_reflexion(
                dataset=args.dataset,
                model=model,
                dataset_split=args.dataset_split,
                sample=args.sample,
                batch_size=args.batch_size,
                jsonl_path=args.jsonl_path,
                memory_file=args.memory_file,
            )
        )


if __name__ == "__main__":
    main()
