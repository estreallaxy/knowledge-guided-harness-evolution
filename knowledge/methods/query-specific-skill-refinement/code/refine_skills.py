#!/usr/bin/env python3
"""Prepare, collect, and apply task-specific Skill refinement runs.

Runtime dependencies: Harbor, Docker, and a configured model provider.
The interface keeps generated Skills separate from the benchmark tasks until an
explicit apply step.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
PROMPT_TEMPLATE = CODE_DIR / "refinement_prompt.md"
JOB_NAME = "refine-skills"

REFINED_SKILLS_PATHS = {
    "terminus-2": "/root/refined_skills",
    "qwen-coder": "/root/refined_skills",
}
DEFAULT_REFINED_SKILLS_PATH = "/agent-logs/refined_skills"

AGENT_SKILLS_PATHS = {
    "terminus-2": "/root/.claude/skills",
    "qwen-coder": "/root/.qwen/skills",
}


def output_path_for(agent: str) -> str:
    return REFINED_SKILLS_PATHS.get(agent, DEFAULT_REFINED_SKILLS_PATH)


def absolute_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def discover_tasks(tasks_dir: Path, selected: list[str] | None) -> list[Path]:
    if not tasks_dir.is_dir():
        raise ValueError(f"tasks directory does not exist: {tasks_dir}")

    requested = set(selected or [])
    tasks: list[Path] = []
    for path in sorted(tasks_dir.iterdir()):
        if requested and path.name not in requested:
            continue
        required = (
            path / "instruction.md",
            path / "environment" / "Dockerfile",
            path / "environment" / "skills",
        )
        if path.is_dir() and all(item.exists() for item in required):
            tasks.append(path)

    found = {path.name for path in tasks}
    missing = requested - found
    if missing:
        raise ValueError(
            "selected tasks are absent or incomplete: " + ", ".join(sorted(missing))
        )
    if not tasks:
        raise ValueError(
            "no task contains instruction.md, environment/Dockerfile, and environment/skills/"
        )
    return tasks


def render_prompt(agent: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.format(refined_skills_path=output_path_for(agent)).rstrip() + "\n"


def add_docker_inputs(dockerfile: Path) -> None:
    marker = "# knowledge-guided-refinement-inputs"
    text = dockerfile.read_text(encoding="utf-8")
    if marker not in text:
        text = (
            text.rstrip()
            + f"\n\n{marker}\n"
            + "COPY task_instruction.md /root/task_instruction.md\n"
            + "COPY candidate_skills /root/candidate_skills\n"
        )
        dockerfile.write_text(text, encoding="utf-8")


def configure_skill_path(task_toml: Path, agent: str) -> None:
    skills_path = AGENT_SKILLS_PATHS.get(agent)
    if not skills_path or not task_toml.is_file():
        return
    text = task_toml.read_text(encoding="utf-8")
    if "skills_dir" in text:
        return
    if "[environment]" not in text:
        text = text.rstrip() + "\n\n[environment]\n"
    text = text.replace(
        "[environment]",
        f'[environment]\nskills_dir = "{skills_path}"',
        1,
    )
    task_toml.write_text(text, encoding="utf-8")


def prepare_task(source: Path, destination: Path, agent: str) -> None:
    shutil.copytree(source, destination)
    environment = destination / "environment"
    shutil.copy2(source / "instruction.md", environment / "task_instruction.md")

    skills = environment / "skills"
    skills.rename(environment / "candidate_skills")
    skills.mkdir()

    add_docker_inputs(environment / "Dockerfile")
    configure_skill_path(destination / "task.toml", agent)
    (destination / "instruction.md").write_text(render_prompt(agent), encoding="utf-8")

    tests = destination / "tests"
    if tests.exists():
        shutil.rmtree(tests)
    tests.mkdir()
    (tests / "test.sh").write_text(
        '#!/bin/bash\nmkdir -p /logs/verifier\necho "1" > /logs/verifier/reward.txt\n',
        encoding="utf-8",
    )


def agent_arguments(agent: str, port: int) -> dict[str, Any]:
    if agent == "terminus-2":
        return {
            "api_base": f"http://localhost:{port}/v1",
            "model_info": {"max_input_tokens": 253952},
        }
    if agent == "qwen-coder":
        return {
            "version": "0.12.3",
            "api_key": "empty",
            "base_url": f"http://host.docker.internal:{port}/v1",
        }
    return {"version": "2.1.19" if agent == "claude-code" else "latest"}


def write_harbor_config(
    prepared_tasks: Path,
    workspace: Path,
    agent: str,
    model: str,
    max_workers: int,
    port: int,
    task_names: list[str],
) -> Path:
    config: dict[str, Any] = {
        "job_name": JOB_NAME,
        "jobs_dir": str(workspace / "jobs"),
        "n_attempts": 1,
        "timeout_multiplier": 2.0,
        "debug": False,
        "orchestrator": {
            "type": "local",
            "n_concurrent_trials": max_workers,
            "quiet": False,
            "retry": {
                "max_retries": 1,
                "exclude_exceptions": ["VerifierTimeoutError"],
                "wait_multiplier": 1.0,
                "min_wait_sec": 1.0,
                "max_wait_sec": 60.0,
            },
        },
        "environment": {"type": "docker", "force_build": False, "delete": True},
        "artifacts": [output_path_for(agent)],
        "verifier": {"disable": True},
        "agents": [
            {
                "name": agent,
                "import_path": None,
                "model_name": model,
                "kwargs": agent_arguments(agent, port),
            }
        ],
        "datasets": [{"path": str(prepared_tasks), "task_names": task_names}],
    }
    config_path = workspace / "harbor-refine-skills.yaml"
    # JSON is valid YAML 1.2 and avoids adding a Python dependency to this method.
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return config_path


def validate_skills(path: Path) -> list[str]:
    if not path.is_dir():
        return [f"missing directory: {path}"]
    skill_dirs = sorted(child for child in path.iterdir() if child.is_dir())
    if not skill_dirs:
        return [f"no Skill directories found in: {path}"]

    errors: list[str] = []
    for skill_dir in skill_dirs:
        entry = skill_dir / "SKILL.md"
        if not entry.is_file():
            errors.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        text = entry.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{skill_dir.name}: empty SKILL.md")
        elif not text.startswith("---") or "name:" not in text or "description:" not in text:
            errors.append(f"{skill_dir.name}: missing name/description frontmatter")
    return errors


def find_job(job_root: Path, task_name: str) -> Path | None:
    matches: list[Path] = []
    if not job_root.is_dir():
        return None
    for job_dir in sorted(job_root.iterdir()):
        if not job_dir.is_dir():
            continue
        reported_name = ""
        result_file = job_dir / "result.json"
        if result_file.is_file():
            try:
                reported_name = json.loads(
                    result_file.read_text(encoding="utf-8")
                ).get("task_name", "")
            except (json.JSONDecodeError, OSError):
                pass
        if reported_name == task_name or job_dir.name.rsplit("__", 1)[0] == task_name:
            matches.append(job_dir)
    return matches[-1] if matches else None


def prepare_command(args: argparse.Namespace) -> None:
    tasks_dir = absolute_path(args.tasks_dir)
    workspace = absolute_path(args.workspace)
    tasks = discover_tasks(tasks_dir, args.tasks)
    prepared = workspace / "prepared-tasks"
    if prepared.exists():
        shutil.rmtree(prepared)
    prepared.mkdir(parents=True)

    for task in tasks:
        prepare_task(task, prepared / task.name, args.agent)

    config = write_harbor_config(
        prepared,
        workspace,
        args.agent,
        args.model,
        args.max_workers,
        args.port,
        [task.name for task in tasks],
    )
    print(f"Prepared {len(tasks)} task(s).")
    print(f"Run: harbor run -c {config}")


def collect_command(args: argparse.Namespace) -> None:
    tasks = discover_tasks(absolute_path(args.tasks_dir), args.tasks)
    workspace = absolute_path(args.workspace)
    output_root = workspace / "refined-skills"
    output_root.mkdir(parents=True, exist_ok=True)
    job_root = workspace / "jobs" / JOB_NAME
    manifest: list[dict[str, Any]] = []

    for task in tasks:
        job = find_job(job_root, task.name)
        source = job / "artifacts" / "refined_skills" if job else None
        errors = validate_skills(source) if source else ["job output not found"]
        destination = output_root / task.name
        if not errors:
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
        manifest.append(
            {
                "task": task.name,
                "status": "collected" if not errors else "rejected",
                "errors": errors,
                "output": str(destination) if not errors else None,
            }
        )

    manifest_path = workspace / "refinement-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    accepted = sum(item["status"] == "collected" for item in manifest)
    print(f"Collected {accepted}/{len(manifest)} task result(s).")
    print(f"Manifest: {manifest_path}")


def apply_command(args: argparse.Namespace) -> None:
    tasks = discover_tasks(absolute_path(args.tasks_dir), args.tasks)
    workspace = absolute_path(args.workspace)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = workspace / "backups" / timestamp
    applied = 0

    for task in tasks:
        source = workspace / "refined-skills" / task.name
        errors = validate_skills(source)
        if errors:
            print(f"Skip {task.name}: {'; '.join(errors)}", file=sys.stderr)
            continue
        target = task / "environment" / "skills"
        backup = backup_root / task.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target, backup)
        shutil.rmtree(target)
        shutil.copytree(source, target)
        applied += 1

    print(f"Applied refined Skills to {applied}/{len(tasks)} task(s).")
    if applied:
        print(f"Original Skills backup: {backup_root}")


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--tasks-dir", required=True, help="Benchmark task collection")
    parser.add_argument("--workspace", required=True, help="Isolated working directory")
    parser.add_argument("--tasks", nargs="+", help="Optional task names")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run task-specific Skill refinement without runtime literature search."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser("prepare", help="Prepare tasks and Harbor configuration")
    add_common_arguments(prepare)
    prepare.add_argument("--agent", default="claude-code")
    prepare.add_argument("--model", default="claude-opus-4-6")
    prepare.add_argument("--max-workers", type=int, default=5)
    prepare.add_argument("--port", type=int, default=30000)
    prepare.set_defaults(handler=prepare_command)

    collect = commands.add_parser("collect", help="Validate and collect generated Skills")
    add_common_arguments(collect)
    collect.set_defaults(handler=collect_command)

    apply_parser = commands.add_parser(
        "apply", help="Apply collected Skills after external benchmark review"
    )
    add_common_arguments(apply_parser)
    apply_parser.set_defaults(handler=apply_command)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.handler(args)
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()
