"""Run the Claude-CUA Photoshop benchmark."""

import argparse
import csv
import json
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from agents.llm_agents import create_agent
from run_single_example import load_task_config, run_single_example


logger = logging.getLogger("ps_benchmark")


class BenchmarkRunner:
    """Run selected tasks sequentially against one desktop Photoshop instance."""

    def __init__(
        self,
        tasks_dir: str = "tasks",
        output_dir: str = "benchmark_results",
        results_base_dir: str = "results",
        max_steps: int = 50,
        step_pause: float = 2.0,
        timeout: int = 300,
        photoshop_executable: Optional[str] = None,
        max_crash_retries: int = 2,
    ):
        self.tasks_dir = Path(tasks_dir)
        self.output_dir = Path(output_dir)
        self.results_base_dir = Path(results_base_dir)
        self.max_steps = max_steps
        self.step_pause = step_pause
        self.timeout = timeout
        self.photoshop_executable = (
            photoshop_executable or os.getenv("PHOTOSHOP_EXECUTABLE")
        )
        self.max_crash_retries = max_crash_retries
        self._validate_configuration()
        self.tasks = self._load_tasks()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_base_dir.mkdir(parents=True, exist_ok=True)

    def _validate_configuration(self) -> None:
        required = {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "OPENAI_API_KEY": (
                os.getenv("OPENAI_API_KEY")
                or os.getenv("PSBENCH_JUDGE_API_KEY")
            ),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(missing)
            )
        if not self.photoshop_executable:
            raise ValueError(
                "Photoshop executable is not configured. Pass "
                "--photoshop-executable or set PHOTOSHOP_EXECUTABLE."
            )
        executable = Path(self.photoshop_executable)
        if not executable.is_file():
            raise FileNotFoundError(f"Photoshop executable not found: {executable}")
        self.photoshop_executable = str(executable.resolve())

    def _load_tasks(self) -> List[Dict[str, Any]]:
        if not self.tasks_dir.is_dir():
            raise FileNotFoundError(f"Task directory not found: {self.tasks_dir}")
        tasks = []
        for directory in sorted(self.tasks_dir.iterdir()):
            if not directory.is_dir():
                continue
            if len(directory.name) != 3 or not directory.name.isdigit():
                logger.debug("Ignoring non-task directory: %s", directory)
                continue
            task_number = int(directory.name)
            if not 1 <= task_number <= 600:
                logger.debug("Ignoring out-of-range task directory: %s", directory)
                continue
            tasks.append(load_task_config(str(directory)))
        if not tasks:
            raise ValueError(f"No valid tasks found in {self.tasks_dir}")
        return tasks

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(task["id"])
        result = None
        for attempt in range(self.max_crash_retries + 1):
            if attempt:
                logger.warning(
                    "Photoshop crash recovery for task %s: retry %s/%s.",
                    task_id,
                    attempt,
                    self.max_crash_retries,
                )
                time.sleep(3)

            result = run_single_example(
                agent=create_agent(),
                task_config=task,
                max_steps=self.max_steps,
                step_pause=self.step_pause,
                timeout=self.timeout,
                photoshop_executable=self.photoshop_executable,
                results_base_dir=str(self.results_base_dir),
            )
            result["photoshop_crash_retries"] = attempt
            if result.get("error") != "photoshop_process_crashed":
                return result

        result["error"] = (
            f"photoshop_process_crashed_after_{self.max_crash_retries}_retries"
        )
        return result

    def run(self, task_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        tasks = self.tasks
        if task_filter:
            selected = {str(task_id).zfill(3) for task_id in task_filter}
            tasks = [task for task in tasks if str(task["id"]).zfill(3) in selected]
            missing = selected - {str(task["id"]).zfill(3) for task in tasks}
            if missing:
                raise ValueError(
                    "Unknown task IDs: " + ", ".join(sorted(missing))
                )

        started_at = time.time()
        results = []
        for index, task in enumerate(tasks, 1):
            logger.info(
                "Running task %s/%s: %s",
                index,
                len(tasks),
                task["id"],
            )
            result = self._run_task(task)
            results.append(result)
            self._save_individual_result(result)
            time.sleep(1)

        total_time = time.time() - started_at
        summary = self._build_summary(results, total_time)
        self._save_aggregate_results(results, summary)
        logger.info(
            "Benchmark completed: passed=%s, total=%s, time=%.2fs.",
            summary["passed"],
            summary["total"],
            total_time,
        )
        return {"results": results, "summary": summary}

    def _save_individual_result(self, result: Dict[str, Any]) -> None:
        directory = self.output_dir / "individual_results"
        directory.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = directory / (
            f"{result['task_id']}_{result['agent_name']}_{timestamp}.json"
        )
        with path.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=True)

    @staticmethod
    def _build_summary(
        results: List[Dict[str, Any]], total_time: float
    ) -> Dict[str, Any]:
        passed = sum(bool(result.get("success")) for result in results)
        total = len(results)
        return {
            "agent_name": "Claude-CUA",
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total else 0.0,
            "total_time": total_time,
        }

    def _save_aggregate_results(
        self, results: List[Dict[str, Any]], summary: Dict[str, Any]
    ) -> None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        json_path = self.output_dir / f"benchmark_results_{timestamp}.json"
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(
                {"summary": summary, "results": results},
                file,
                indent=2,
                ensure_ascii=True,
            )

        csv_path = self.output_dir / f"benchmark_results_{timestamp}.csv"
        fields = [
            "task_id",
            "agent_name",
            "success",
            "steps_taken",
            "total_time",
            "error",
            "instruction",
            "result_file",
            "photoshop_crash_retries",
        ]
        with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            for result in results:
                writer.writerow({field: result.get(field) for field in fields})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run PSBench with the Claude Computer Use agent."
    )
    parser.add_argument("--tasks-dir", default="tasks")
    parser.add_argument("--output-dir", default="benchmark_results")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument(
        "--photoshop-executable",
        default=os.getenv("PHOTOSHOP_EXECUTABLE"),
    )
    parser.add_argument("--max-steps", type=int, default=50)
    parser.add_argument("--step-pause", type=float, default=2.0)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-crash-retries", type=int, default=2)
    parser.add_argument("--task-filter", nargs="+")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("benchmark.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    runner = BenchmarkRunner(
        tasks_dir=args.tasks_dir,
        output_dir=args.output_dir,
        results_base_dir=args.results_dir,
        max_steps=args.max_steps,
        step_pause=args.step_pause,
        timeout=args.timeout,
        photoshop_executable=args.photoshop_executable,
        max_crash_retries=args.max_crash_retries,
    )
    runner.run(task_filter=args.task_filter)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
