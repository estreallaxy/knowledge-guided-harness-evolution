"""Run one Claude-CUA attempt on one Photoshop task."""

import argparse
import json
import logging
import os
from pathlib import Path
import threading
import time
import traceback
from typing import Any, Dict, Optional

from agents.agent_base import BaseAgent
from agents.llm_agents import create_agent
from photoshop_env import PhotoshopEnv, PhotoshopProcessCrashedError


logger = logging.getLogger("ps_benchmark")


def load_task_config(task_path: str) -> Dict[str, Any]:
    """Load and validate `<task-directory>/<task-id>.json`."""
    directory = Path(task_path)
    config_path = directory / f"{directory.name}.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"Task configuration not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        task = json.load(file)

    for field in ("id", "instruction"):
        if field not in task:
            raise ValueError(
                f"Task configuration {config_path} is missing required field: {field}"
            )
    task["task_folder_path"] = str(directory.resolve())
    return task


def run_single_example(
    agent: BaseAgent,
    task_config: Dict[str, Any],
    env: Optional[PhotoshopEnv] = None,
    max_steps: int = 50,
    step_pause: float = 2.0,
    timeout: int = 300,
    photoshop_executable: Optional[str] = None,
    results_base_dir: str = "results",
) -> Dict[str, Any]:
    """Execute, export, and evaluate one task attempt."""
    task_id = str(task_config["id"])
    instruction = task_config["instruction"]
    created_env = env is None
    if env is None:
        env = PhotoshopEnv(
            ps_executable_path=photoshop_executable,
            debug_mode=False,
            require_screenshot=True,
            enable_recording=False,
            results_base_dir=results_base_dir,
        )

    result: Dict[str, Any] = {
        "task_id": task_id,
        "agent_name": agent.name,
        "instruction": instruction,
        "success": False,
        "evaluation": None,
        "result_file": None,
        "steps_taken": 0,
        "total_time": 0.0,
        "error": None,
        "final_action": None,
    }
    started_at = time.time()
    monitor_stop = threading.Event()
    photoshop_crashed = threading.Event()
    monitor_thread = None

    try:
        logger.info("Starting task %s: %s", task_id, instruction)
        agent.reset()
        observation = env.reset(task_config)

        def assert_task_environment_healthy() -> None:
            if photoshop_crashed.is_set():
                raise PhotoshopProcessCrashedError(
                    f"photoshop_process_crashed: task {task_id} host process disappeared"
                )
            env.assert_photoshop_process_alive()

        agent.set_environment_health_check(assert_task_environment_healthy)

        def monitor_photoshop() -> None:
            while not monitor_stop.wait(0.5):
                if not env.is_photoshop_process_alive():
                    logger.error(
                        "The Photoshop process disappeared during task %s. "
                        "The runner will restart this task.",
                        task_id,
                    )
                    photoshop_crashed.set()
                    return

        monitor_thread = threading.Thread(
            target=monitor_photoshop,
            name=f"photoshop-monitor-{task_id}",
            daemon=True,
        )
        monitor_thread.start()

        agent.plan_task(instruction, observation.get("screenshot"))
        done = False
        step = 0
        while not done and step < max_steps:
            if time.time() - started_at > timeout:
                result["error"] = "timeout"
                logger.warning("Task %s reached the task timeout.", task_id)
                break

            step += 1
            try:
                agent.assert_environment_healthy()
                action = agent.act(observation)
                agent.assert_environment_healthy()
                observation, _, done, info = env.step(action, pause=step_pause)
                result["steps_taken"] = step
                result["final_action"] = action

                if done:
                    logger.info(
                        "Task %s received a completion signal: %s", task_id, info
                    )
                    break
            except PhotoshopProcessCrashedError as error:
                logger.error(
                    "Task %s attempt stopped because Photoshop crashed: %s",
                    task_id,
                    error,
                )
                result["error"] = "photoshop_process_crashed"
                break
            except Exception as error:
                logger.exception("Task %s step %s failed: %s", task_id, step, error)
                result["error"] = f"step_error: {error}"
                break

        if step >= max_steps and not done and result["error"] is None:
            result["error"] = "max_steps_reached"

        if result["error"] == "photoshop_process_crashed":
            logger.warning("Skipping export and evaluation for the crashed session.")
        else:
            logger.info("Waiting one second for Photoshop to finish rendering.")
            time.sleep(1)
            agent.assert_environment_healthy()
            env.prepare_for_export()
            result_path = env._save_result_file()
            result["result_file"] = result_path
            evaluation = env.evaluate(result_path)
            result["evaluation"] = evaluation
            result["success"] = bool(evaluation.get("passed", False))
            if evaluation.get("evaluation_error"):
                result["error"] = (
                    f"evaluation_error: {evaluation['evaluation_error']}"
                )
            elif result["success"]:
                result["error"] = None
            else:
                result["error"] = "rubric_evaluation_failed"

    except PhotoshopProcessCrashedError as error:
        logger.error("Photoshop crashed during task %s: %s", task_id, error)
        result["error"] = "photoshop_process_crashed"
    except Exception as error:
        logger.exception("Fatal task error for %s: %s", task_id, error)
        result["error"] = f"fatal_error: {error}"
    finally:
        monitor_stop.set()
        if monitor_thread is not None:
            monitor_thread.join(timeout=2)
        result["total_time"] = time.time() - started_at
        if created_env:
            try:
                env.close()
            except Exception as error:
                logger.exception(
                    "Failed to close the environment for task %s: %s",
                    task_id,
                    error,
                )

    logger.info(
        "Task %s finished: success=%s, steps=%s, time=%.2fs, error=%s",
        task_id,
        result["success"],
        result["steps_taken"],
        result["total_time"],
        result["error"],
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one Claude-CUA task in Adobe Photoshop."
    )
    parser.add_argument("--task-path", required=True)
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--step-pause", type=float, default=2.0)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--photoshop-executable",
        default=os.getenv("PHOTOSHOP_EXECUTABLE"),
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    task = load_task_config(args.task_path)
    result = run_single_example(
        agent=create_agent(),
        task_config=task,
        max_steps=args.max_steps,
        step_pause=args.step_pause,
        timeout=args.timeout,
        photoshop_executable=args.photoshop_executable,
        results_base_dir=args.results_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
