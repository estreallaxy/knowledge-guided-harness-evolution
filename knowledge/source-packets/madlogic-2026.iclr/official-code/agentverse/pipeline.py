"""Shared implementation for the release entry points."""

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path

import yaml
from tqdm import tqdm

from agentverse.answers import majority_vote, normalize_answer, valid_labels

ROOT = Path(__file__).resolve().parents[1]
STAGE_FILES = {
    "translation": "translation.json",
    "llm_solver": "llm_solver.json",
    "symbolic_solver": "symbolic_solver.json",
    "final_debate": "final_debate.json",
}


def load_config(path):
    path = Path(path).resolve()
    with path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    for section, field in ((config["dataset"], "path"), (config, "output_dir")):
        value = Path(section[field]).expanduser()
        section[field] = str(value if value.is_absolute() else path.parent / value)
    for stage in ("translation", "final_debate"):
        if config[stage]["rounds"] < 1:
            raise ValueError(f"{stage}.rounds must be positive")
        names = [agent["name"] for agent in config[stage]["agents"]]
        if not names or len(names) != len(set(names)):
            raise ValueError(f"{stage} requires distinct agent names")
    if config["llm"]["max_retry"] < 1:
        raise ValueError("llm.max_retry must be positive")
    return config


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".partial")
    temporary.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_dataset(config):
    rows = read_json(config["dataset"]["path"])
    limit = config["dataset"].get("limit", 0)
    if limit < 0:
        raise ValueError("dataset.limit cannot be negative")
    if limit:
        rows = rows[:limit]
    if not rows:
        raise ValueError("Empty dataset")
    seen = set()
    for row in rows:
        missing = {"id", "context", "question", "options", "answer"} - row.keys()
        if missing:
            raise ValueError(f"Dataset row is missing {sorted(missing)}")
        if row["id"] in seen:
            raise ValueError(f"Duplicate dataset ID: {row['id']}")
        seen.add(row["id"])
        if not isinstance(row["options"], list) or not row["options"]:
            raise ValueError(f"Expected a nonempty option list for {row['id']}")
        if normalize_answer(row["answer"]) not in valid_labels(row["options"]):
            raise ValueError(f"Invalid gold answer for {row['id']}")
    return rows


def stage_path(config, stage):
    return Path(config["output_dir"]) / STAGE_FILES[stage]


def load_stage(config, stage, rows):
    results = read_json(stage_path(config, stage))
    indexed = {}
    expected = {row["id"]: row for row in rows}
    for result in results:
        identity = result["id"]
        if identity in indexed or identity not in expected:
            raise ValueError(f"Unexpected or duplicate ID in {stage}: {identity}")
        if any(result.get(key) != expected[identity][key] for key in ("context", "question", "options", "answer")):
            raise ValueError(f"Dataset content differs from {stage} for {identity}")
        indexed[identity] = result
    return indexed


def problem_fields(row):
    return {key: row[key] for key in ("id", "context", "question", "options", "answer")}


def options_text(row):
    return "\n".join(str(option) for option in row["options"])


def assign_problem(agents, row):
    for agent in agents:
        agent.context = row["context"]
        agent.question = row["question"]
        agent.options = options_text(row)


async def translate(config, rows):
    from agentverse import AgentVerse
    from translation_output_helper.get_translation_output import get_translation_output

    debate = AgentVerse.from_config(config, "translation")
    results = []
    for row in tqdm(rows, desc="Translation", unit="question"):
        assign_problem(debate.agents, row)
        await debate.arun()
        history, translation = get_translation_output(debate.environment)
        result = {**problem_fields(row), "translation": translation, "chat_history": history}
        errors = {agent.name: agent.error for agent in debate.agents if agent.error}
        if errors:
            result["errors"] = errors
        results.append(result)
        write_json(stage_path(config, "translation"), results)


def build_llm_solvers(config):
    from agentverse.agents.llm_solver_agent import LLMSolverAgent
    from agentverse.agents.plan_and_solve_agent import PlanAndSolveAgent
    from agentverse.initialization import load_llm
    from agentverse.parser import output_parser_registry

    agents = []
    for role in config["llm_solver"]["roles"]:
        arguments = dict(role)
        agent_type = arguments.pop("agent_type", "cot")
        arguments["output_parser"] = output_parser_registry.build(arguments.pop("parser_type"))
        arguments["llm"] = load_llm(config["llm"])
        arguments["max_retry"] = config["llm"]["max_retry"]
        cls = PlanAndSolveAgent if agent_type == "plan_and_solve" else LLMSolverAgent
        agents.append(cls(**arguments))
    return agents


async def solve_llm(config, rows):
    agents = build_llm_solvers(config)
    results = []
    for row in tqdm(rows, desc="LLM solvers", unit="question"):
        answers = await asyncio.gather(*[
            agent.asolve(row["context"], row["question"], options_text(row)) for agent in agents
        ])
        roles = {}
        for agent, answer in zip(agents, answers):
            prediction = normalize_answer(answer.answer)
            success = answer.success and prediction in valid_labels(row["options"])
            roles[agent.display_name] = {
                "predict": prediction if success else "", "reasoning": answer.reasoning,
                "error_message": "" if success else answer.error_message or "Invalid answer option",
            }
        results.append({**problem_fields(row), "roles": roles})
        write_json(stage_path(config, "llm_solver"), results)


def solve_symbolic(config, rows):
    from solver_engine.src.logic_inference import SOLVER_CLASSES, execute_solver

    translations = load_stage(config, "translation", rows)
    results = []
    for row in tqdm(rows, desc="Symbolic solvers", unit="question"):
        entry = translations.get(row["id"], {}).get("translation", [{}])
        programs = entry[0] if entry else {}
        roles = {name: execute_solver(name, programs.get(name, ""), config["dataset"]["name"])
                 for name in SOLVER_CLASSES}
        results.append({**problem_fields(row), "roles": roles})
        write_json(stage_path(config, "symbolic_solver"), results)


async def final_debate(config, rows):
    from agentverse import AgentVerse

    symbolic = load_stage(config, "symbolic_solver", rows)
    llm = load_stage(config, "llm_solver", rows)
    debate = AgentVerse.from_config(config, "final_debate")
    solver_names = {
        "LP supporter": "LP", "FOL supporter": "FOL", "SAT supporter": "SAT",
        "Plan-and-Solve supporter": "Plan-and-Solve", "COT Solver supporter": "COT Solver",
    }
    results = []
    for row in tqdm(rows, desc="Final debate", unit="question"):
        assign_problem(debate.agents, row)
        roles = {**symbolic.get(row["id"], {}).get("roles", {}),
                 **llm.get(row["id"], {}).get("roles", {})}
        for agent in debate.agents:
            solver_result = roles.get(solver_names[agent.name], {})
            agent.predict = solver_result.get("predict", "")
            agent.reasoning = solver_result.get("reasoning", "")
            error = solver_result.get("error_message", "")
            if error or not solver_result:
                agent.reasoning += "\nSolver failed: " + (error or "Missing solver result")
        await debate.arun()
        predictions = {agent.name: agent.final_answer for agent in debate.agents}
        prediction = majority_vote(predictions.values(), row["options"], f"{config['seed']}:{row['id']}")
        result = {**problem_fields(row), "predict": prediction, "agent_predictions": predictions,
                  "chat_history": debate.environment.get_chat_history()}
        errors = {agent.name: agent.error for agent in debate.agents if agent.error}
        if errors:
            result["errors"] = errors
        results.append(result)
        write_json(stage_path(config, "final_debate"), results)


def evaluate(config, rows):
    predictions = load_stage(config, "final_debate", rows)
    correct = sum(normalize_answer(predictions.get(row["id"], {}).get("predict")) ==
                  normalize_answer(row["answer"]) for row in rows)
    accuracy = correct / len(rows)
    print(f"Accuracy: {accuracy:.2%}")
    return accuracy


async def run_stage(stage, config, rows):
    if stage in {"all", "translation"}:
        await translate(config, rows)
    if stage in {"all", "llm_solver"}:
        await solve_llm(config, rows)
    if stage in {"all", "symbolic_solver"}:
        solve_symbolic(config, rows)
    if stage in {"all", "final_debate"}:
        await final_debate(config, rows)
    if stage in {"all", "final_debate", "evaluation"}:
        evaluate(config, rows)


def main(stage="all"):
    parser = argparse.ArgumentParser(description=f"MAD-Logic: {stage.replace('_', ' ')}")
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    parser.add_argument("--limit", type=int, help="Number of questions; 0 uses the whole dataset")
    parser.add_argument("--sparse", action=argparse.BooleanOptionalAction, default=None,
                        help="Override sparse communication for translation and final debate")
    args = parser.parse_args()
    if stage in {"all", "translation", "llm_solver", "final_debate"} and not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY before running an LLM stage")
    logging.basicConfig(level=logging.ERROR)
    for name in ("httpx", "openai", "sentence_transformers", "transformers", "huggingface_hub"):
        logging.getLogger(name).setLevel(logging.ERROR)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    config = load_config(args.config)
    if args.limit is not None:
        config["dataset"]["limit"] = args.limit
    if args.sparse is not None:
        config["translation"]["sparse"] = config["final_debate"]["sparse"] = args.sparse
    asyncio.run(run_stage(stage, config, load_dataset(config)))
