"""Core experiment runner framework."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Type
from uuid import UUID, uuid4

import structlog
from tqdm.asyncio import tqdm

from ..core import ExperimentConfig, PseConfig, PseSystem
from ..agents import PseAgent, PseAgentConfig, Tool
from ..tasks import Task, TaskResult, TaskGenerator, TaskFamily
from ..tasks.tool_intensive import ToolIntensiveTaskGenerator
from ..tasks.long_horizon import LongHorizonTaskGenerator
from ..tasks.policy_bound import PolicyBoundTaskGenerator

logger = structlog.get_logger()


@dataclass
class RunResult:
    """Result of a single run."""
    run_id: UUID
    task_id: UUID
    run_number: int
    task_result: TaskResult
    pse_state: dict[str, Any]
    metrics: dict[str, float]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "run_id": str(self.run_id),
            "task_id": str(self.task_id),
            "run_number": self.run_number,
            "task_result": self.task_result.to_dict(),
            "pse_state_summary": {
                "registry_entities": len(self.pse_state.get("registry", {}).get("namespaces", {})),
                "events_count": self.pse_state.get("events", {}).get("total_events", 0),
                "propagations_count": self.pse_state.get("propagation", {}).get("total_propagations", 0),
            },
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ExperimentResult:
    """Result of a complete experiment."""
    experiment_id: str
    experiment_name: str
    config: ExperimentConfig
    tasks: list[Task]
    runs: list[RunResult]
    aggregate_metrics: dict[str, float]
    start_time: datetime
    end_time: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "experiment_name": self.experiment_name,
            "config": self.config.to_dict(),
            "num_tasks": len(self.tasks),
            "num_runs": len(self.runs),
            "aggregate_metrics": self.aggregate_metrics,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "metadata": self.metadata,
        }

    def save(self, path: Path) -> None:
        """Save experiment result to file."""
        path.mkdir(parents=True, exist_ok=True)

        # Save summary
        with open(path / "summary.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        # Save detailed runs
        runs_data = [r.to_dict() for r in self.runs]
        with open(path / "runs.json", "w") as f:
            json.dump(runs_data, f, indent=2, default=str)

        # Save tasks
        tasks_data = [t.to_dict() for t in self.tasks]
        with open(path / "tasks.json", "w") as f:
            json.dump(tasks_data, f, indent=2, default=str)

        logger.info("Experiment result saved", path=str(path))


class ExperimentRunner(ABC):
    """Base class for experiment runners."""

    def __init__(self, config: ExperimentConfig, api_key: Optional[str] = None):
        self.config = config
        self.api_key = api_key
        self._task_generator: Optional[TaskGenerator] = None
        self._tools: list[Tool] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Experiment name."""
        pass

    def _get_task_generator(self) -> TaskGenerator:
        """Get task generator based on config."""
        if self._task_generator:
            return self._task_generator

        family = TaskFamily(self.config.task_family)
        seed = self.config.seed

        if family == TaskFamily.TOOL_INTENSIVE:
            self._task_generator = ToolIntensiveTaskGenerator(seed=seed)
        elif family == TaskFamily.LONG_HORIZON:
            self._task_generator = LongHorizonTaskGenerator(seed=seed)
        elif family == TaskFamily.POLICY_BOUND:
            self._task_generator = PolicyBoundTaskGenerator(seed=seed)
        else:
            raise ValueError(f"Unknown task family: {family}")

        return self._task_generator

    def _create_tools(self) -> list[Tool]:
        """Create tools from task generator definitions."""
        if self._tools:
            return self._tools

        generator = self._get_task_generator()
        tool_defs = generator.get_tools()

        # Shared state for memory tool
        memory_store = {}

        # Real tool implementations
        def calculator_handler(operation: str, a: float, b: float) -> dict:
            """Perform real calculations."""
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                result = a / b if b != 0 else float('inf')
            else:
                result = 0
            return {"result": result, "operation": operation, "a": a, "b": b}

        def memory_handler(action: str, key: str, value: float = None) -> dict:
            """Store and retrieve values."""
            if action == "store":
                memory_store[key] = value
                return {"status": "stored", "key": key, "value": value}
            elif action == "retrieve":
                val = memory_store.get(key, None)
                return {"key": key, "value": val, "found": val is not None}
            return {"error": "unknown action"}

        def search_handler(query: str) -> dict:
            """Simulated search - returns realistic mock data."""
            # Return plausible data based on query keywords
            if "climate" in query.lower():
                return {"results": [{"topic": "climate", "value": 1.5, "unit": "degrees C", "trend": "increasing"}]}
            elif "stock" in query.lower():
                return {"results": [{"topic": "stocks", "value": 4532.5, "unit": "USD", "trend": "volatile"}]}
            elif "population" in query.lower():
                return {"results": [{"topic": "population", "value": 8000000000, "unit": "people", "trend": "growing"}]}
            elif "energy" in query.lower():
                return {"results": [{"topic": "energy", "value": 580, "unit": "EJ", "trend": "increasing"}]}
            return {"results": [{"topic": query, "value": 42, "unit": "units", "trend": "stable"}]}

        def data_extractor_handler(text: str, pattern: str) -> dict:
            """Extract data patterns from text."""
            import re
            if pattern == "numbers":
                matches = re.findall(r"[-+]?\d*\.?\d+", text)
                return {"pattern": pattern, "matches": [float(m) for m in matches] if matches else []}
            elif pattern == "dates":
                matches = re.findall(r"\d{4}-\d{2}-\d{2}", text)
                return {"pattern": pattern, "matches": matches}
            return {"pattern": pattern, "matches": [], "raw_text": text[:100]}

        def file_reader_handler(filename: str) -> dict:
            """Simulated file reading."""
            # Return simulated file content
            return {"filename": filename, "content": f"Sample content from {filename}: data=123, status=active", "size": 256}

        def file_writer_handler(filename: str, content: str) -> dict:
            """Simulated file writing."""
            return {"filename": filename, "status": "written", "bytes_written": len(content)}

        def status_checker_handler(resource: str) -> dict:
            """Check resource status - returns random but consistent values."""
            import hashlib
            # Use hash for consistent pseudo-random value
            hash_val = int(hashlib.md5(resource.encode()).hexdigest()[:8], 16)
            value = (hash_val % 200)  # 0-199 range
            return {"resource": resource, "value": value, "status": "active"}

        def action_executor_handler(action: str, resource: str) -> dict:
            """Execute an action on a resource."""
            return {"action": action, "resource": resource, "status": "executed", "timestamp": "2026-01-08T12:00:00Z"}

        def data_fetcher_handler(source: str) -> dict:
            """Fetch data from a source."""
            import hashlib
            hash_val = int(hashlib.md5(source.encode()).hexdigest()[:8], 16)
            return {"source": source, "data": {"value": hash_val % 1000, "count": hash_val % 100, "score": (hash_val % 100) / 10}}

        def aggregator_handler(values: list, method: str) -> dict:
            """Aggregate data values."""
            if not values:
                return {"method": method, "result": 0, "count": 0}
            if method == "sum":
                result = sum(values)
            elif method == "average":
                result = sum(values) / len(values)
            elif method == "max":
                result = max(values)
            elif method == "min":
                result = min(values)
            else:
                result = sum(values)
            return {"method": method, "result": result, "count": len(values)}

        def formatter_handler(data: dict, format: str) -> dict:
            """Format data into specified format."""
            import json
            if format == "json":
                return {"format": "json", "output": json.dumps(data)}
            elif format == "csv":
                if isinstance(data, dict):
                    header = ",".join(str(k) for k in data.keys())
                    values = ",".join(str(v) for v in data.values())
                    return {"format": "csv", "output": f"{header}\n{values}"}
            elif format == "table":
                rows = [f"| {k} | {v} |" for k, v in data.items()] if isinstance(data, dict) else [str(data)]
                return {"format": "table", "output": "\n".join(rows)}
            return {"format": format, "output": str(data)}

        # Handler mapping
        handler_map = {
            "calculator": calculator_handler,
            "memory": memory_handler,
            "search": search_handler,
            "data_extractor": data_extractor_handler,
            "file_reader": file_reader_handler,
            "file_writer": file_writer_handler,
            "status_checker": status_checker_handler,
            "action_executor": action_executor_handler,
            "data_fetcher": data_fetcher_handler,
            "aggregator": aggregator_handler,
            "formatter": formatter_handler,
        }

        self._tools = []
        for tool_def in tool_defs:
            name = tool_def["name"]
            handler = handler_map.get(name)

            if handler is None:
                # Fallback for unknown tools
                def make_fallback(tool_name):
                    def fallback(**kwargs):
                        return {"tool": tool_name, "args": kwargs, "status": "completed"}
                    return fallback
                handler = make_fallback(name)

            tool = Tool(
                name=name,
                description=tool_def["description"],
                parameters=tool_def.get("parameters", {}),
                handler=handler,
            )
            self._tools.append(tool)

        return self._tools

    def _create_agent(self, pse_config: Optional[PseConfig] = None) -> PseAgent:
        """Create a PSE-aware agent."""
        pse_cfg = pse_config or self.config.pse_config

        agent_config = PseAgentConfig(
            agent_id=str(uuid4()),
            agent_name=f"{self.name}_agent",
            model_provider=self.config.model_provider,
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            pse_config=pse_cfg,
        )

        return PseAgent(
            config=agent_config,
            tools=self._create_tools(),
            api_key=self.api_key,
        )

    async def _run_task(
        self,
        agent: PseAgent,
        task: Task,
        run_number: int,
    ) -> RunResult:
        """Run a single task and collect results."""
        run_id = uuid4()

        try:
            # Reset agent conversation
            agent.reset_conversation()

            # Set system prompt with any task-specific context
            system_prompt = self._get_system_prompt(task)
            agent.set_system_prompt(system_prompt)

            # Run the task
            response = await agent.run(task.prompt)

            # Create task result
            task_result = TaskResult(
                task_id=task.id,
                run_id=run_id,
                success=response.status.value == "success",
                output=response.final_output,
                tool_sequence=response.tool_call_sequence,
                duration_ms=response.total_duration_ms,
                token_usage=response.total_tokens,
                error=response.error,
            )

            # Evaluate task
            generator = self._get_task_generator()
            metrics = generator.evaluate(task, task_result)

            # Get PSE state
            pse_state = agent.get_pse_state()

            return RunResult(
                run_id=run_id,
                task_id=task.id,
                run_number=run_number,
                task_result=task_result,
                pse_state=pse_state,
                metrics=metrics,
            )

        except Exception as e:
            logger.error("Task run failed", task_id=str(task.id), error=str(e))

            return RunResult(
                run_id=run_id,
                task_id=task.id,
                run_number=run_number,
                task_result=TaskResult(
                    task_id=task.id,
                    run_id=run_id,
                    success=False,
                    output="",
                    tool_sequence=[],
                    error=str(e),
                ),
                pse_state={},
                metrics={"error": 1.0},
            )

    def _get_system_prompt(self, task: Task) -> str:
        """Get system prompt for a task."""
        return f"""You are a helpful assistant that completes tasks efficiently.
You have access to various tools to help you accomplish tasks.
Always use the appropriate tools when needed.

Task type: {task.family.value}
"""

    @abstractmethod
    async def run(self) -> ExperimentResult:
        """Run the experiment."""
        pass

    def _aggregate_metrics(self, runs: list[RunResult]) -> dict[str, float]:
        """Aggregate metrics across all runs."""
        if not runs:
            return {}

        # Collect all numeric metric names
        all_metrics = set()
        for run in runs:
            for key, value in run.metrics.items():
                if isinstance(value, (int, float)):
                    all_metrics.add(key)

        # Aggregate each metric
        aggregated = {}
        for metric_name in all_metrics:
            values = [r.metrics.get(metric_name, 0) for r in runs if isinstance(r.metrics.get(metric_name), (int, float))]
            if not values:
                continue
            aggregated[f"{metric_name}_mean"] = sum(values) / len(values)
            aggregated[f"{metric_name}_std"] = (
                sum((v - aggregated[f"{metric_name}_mean"]) ** 2 for v in values) / len(values)
            ) ** 0.5
            aggregated[f"{metric_name}_min"] = min(values)
            aggregated[f"{metric_name}_max"] = max(values)

        # Add success rate
        success_count = sum(1 for r in runs if r.task_result.success)
        aggregated["success_rate"] = success_count / len(runs)

        # Add average duration
        durations = [r.task_result.duration_ms for r in runs]
        aggregated["avg_duration_ms"] = sum(durations) / len(durations)

        # Add total tokens
        tokens = [r.task_result.token_usage for r in runs]
        aggregated["total_tokens"] = sum(tokens)
        aggregated["avg_tokens_per_run"] = sum(tokens) / len(tokens)

        return aggregated


class SimpleExperimentRunner(ExperimentRunner):
    """Simple experiment runner for basic experiments."""

    @property
    def name(self) -> str:
        return self.config.experiment_name or "simple_experiment"

    async def run(self) -> ExperimentResult:
        """Run a simple experiment."""
        start_time = datetime.utcnow()

        logger.info(
            "Starting experiment",
            experiment_id=self.config.experiment_id,
            name=self.name,
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        # Create agent
        agent = self._create_agent()

        # Run all tasks
        runs = []
        total_runs = self.config.num_tasks * self.config.num_runs

        async for run_result in tqdm(
            self._run_all_tasks(agent, tasks),
            total=total_runs,
            desc=f"Running {self.name}",
        ):
            runs.append(run_result)

        end_time = datetime.utcnow()

        # Aggregate metrics
        aggregate_metrics = self._aggregate_metrics(runs)

        result = ExperimentResult(
            experiment_id=self.config.experiment_id,
            experiment_name=self.name,
            config=self.config,
            tasks=tasks,
            runs=runs,
            aggregate_metrics=aggregate_metrics,
            start_time=start_time,
            end_time=end_time,
        )

        logger.info(
            "Experiment completed",
            experiment_id=self.config.experiment_id,
            duration_seconds=(end_time - start_time).total_seconds(),
            num_runs=len(runs),
            success_rate=aggregate_metrics.get("success_rate", 0),
        )

        return result

    async def _run_all_tasks(self, agent: PseAgent, tasks: list[Task]):
        """Generator that runs all tasks with multiple runs each."""
        for task in tasks:
            for run_num in range(self.config.num_runs):
                result = await self._run_task(agent, task, run_num)
                yield result
