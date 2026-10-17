"""Tool-intensive task generator."""

from __future__ import annotations

from typing import Any, Optional
from uuid import uuid4

from .base import (
    Task,
    TaskFamily,
    TaskResult,
    TaskGenerator,
    TaskDifficulty,
    compute_sequence_similarity,
)


class ToolIntensiveTaskGenerator(TaskGenerator):
    """Generator for tool-intensive tasks requiring multi-step tool usage."""

    TASK_TEMPLATES = [
        {
            "name": "multi_step_calculation",
            "description": "Perform a multi-step calculation using various tools",
            "template": "Calculate the following: First, {op1} {val1} and {val2}. Then {op2} the result with {val3}. Finally, {op3} that with {val4}. Show your work.",
            "tools": ["calculator", "memory"],
            "difficulty": TaskDifficulty.MEDIUM,
        },
        {
            "name": "data_retrieval_analysis",
            "description": "Retrieve data and perform analysis",
            "template": "Search for information about {topic}. Extract the {metric} values and calculate the {analysis_type}. Summarize your findings.",
            "tools": ["search", "data_extractor", "calculator"],
            "difficulty": TaskDifficulty.MEDIUM,
        },
        {
            "name": "file_processing_chain",
            "description": "Process files through multiple tools",
            "template": "Read the file {filename}, extract all {pattern} patterns, transform them using {transform}, and save the result to {output_file}.",
            "tools": ["file_reader", "pattern_extractor", "transformer", "file_writer"],
            "difficulty": TaskDifficulty.HARD,
        },
        {
            "name": "conditional_workflow",
            "description": "Execute conditional workflow based on data",
            "template": "Check the status of {resource}. If the value is above {threshold}, perform {action_high}. Otherwise, perform {action_low}. Report the outcome.",
            "tools": ["status_checker", "threshold_evaluator", "action_executor"],
            "difficulty": TaskDifficulty.MEDIUM,
        },
        {
            "name": "aggregation_pipeline",
            "description": "Aggregate data from multiple sources",
            "template": "Gather data from sources: {sources}. Aggregate the {field} values using {aggregation}. Format the result as {format}.",
            "tools": ["data_fetcher", "aggregator", "formatter"],
            "difficulty": TaskDifficulty.HARD,
        },
    ]

    OPERATIONS = ["add", "subtract", "multiply", "divide"]
    TOPICS = ["climate data", "stock prices", "population statistics", "energy consumption"]
    METRICS = ["average", "maximum", "minimum", "total"]
    ANALYSIS_TYPES = ["mean", "median", "trend", "variance"]

    @property
    def family(self) -> TaskFamily:
        return TaskFamily.TOOL_INTENSIVE

    def generate(self, template_name: Optional[str] = None, **kwargs) -> Task:
        """Generate a tool-intensive task."""
        if template_name:
            template = next(
                (t for t in self.TASK_TEMPLATES if t["name"] == template_name),
                self._rng.choice(self.TASK_TEMPLATES),
            )
        else:
            template = self._rng.choice(self.TASK_TEMPLATES)

        # Generate parameters based on template
        params = self._generate_params(template["name"])

        # Fill template
        prompt = template["template"].format(**params)

        return Task(
            id=self._next_id(),
            family=self.family,
            name=template["name"],
            description=template["description"],
            prompt=prompt,
            expected_tools=template["tools"],
            difficulty=template["difficulty"],
            parameters=params,
            ground_truth=self._compute_ground_truth(template["name"], params),
        )

    def _generate_params(self, template_name: str) -> dict[str, Any]:
        """Generate parameters for a template."""
        if template_name == "multi_step_calculation":
            return {
                "op1": self._rng.choice(self.OPERATIONS),
                "val1": self._rng.randint(1, 100),
                "val2": self._rng.randint(1, 100),
                "op2": self._rng.choice(self.OPERATIONS),
                "val3": self._rng.randint(1, 50),
                "op3": self._rng.choice(self.OPERATIONS),
                "val4": self._rng.randint(1, 50),
            }
        elif template_name == "data_retrieval_analysis":
            return {
                "topic": self._rng.choice(self.TOPICS),
                "metric": self._rng.choice(self.METRICS),
                "analysis_type": self._rng.choice(self.ANALYSIS_TYPES),
            }
        elif template_name == "file_processing_chain":
            return {
                "filename": f"data_{self._rng.randint(1, 100)}.txt",
                "pattern": self._rng.choice(["email", "phone", "url", "number"]),
                "transform": self._rng.choice(["uppercase", "lowercase", "hash", "encode"]),
                "output_file": f"output_{self._rng.randint(1, 100)}.txt",
            }
        elif template_name == "conditional_workflow":
            return {
                "resource": f"resource_{self._rng.randint(1, 10)}",
                "threshold": self._rng.randint(50, 150),
                "action_high": self._rng.choice(["scale_up", "alert", "backup"]),
                "action_low": self._rng.choice(["scale_down", "log", "ignore"]),
            }
        elif template_name == "aggregation_pipeline":
            sources = [f"source_{i}" for i in self._rng.sample(range(1, 10), 3)]
            return {
                "sources": ", ".join(sources),
                "field": self._rng.choice(["value", "count", "score", "metric"]),
                "aggregation": self._rng.choice(["sum", "average", "max", "min"]),
                "format": self._rng.choice(["json", "csv", "table", "report"]),
            }
        return {}

    def _compute_ground_truth(self, template_name: str, params: dict[str, Any]) -> Any:
        """Compute expected ground truth for a task."""
        if template_name == "multi_step_calculation":
            def op(operation: str, a: float, b: float) -> float:
                if operation == "add":
                    return a + b
                elif operation == "subtract":
                    return a - b
                elif operation == "multiply":
                    return a * b
                elif operation == "divide":
                    return a / b if b != 0 else 0
                return 0

            step1 = op(params["op1"], params["val1"], params["val2"])
            step2 = op(params["op2"], step1, params["val3"])
            step3 = op(params["op3"], step2, params["val4"])
            return step3

        return None

    def get_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions for tool-intensive tasks."""
        return [
            {
                "name": "calculator",
                "description": "Perform mathematical calculations. Supports add, subtract, multiply, divide.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                        },
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                    },
                    "required": ["operation", "a", "b"],
                },
            },
            {
                "name": "memory",
                "description": "Store and retrieve values by key.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["store", "retrieve"]},
                        "key": {"type": "string"},
                        "value": {"type": "number"},
                    },
                    "required": ["action", "key"],
                },
            },
            {
                "name": "search",
                "description": "Search for information on a topic.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "data_extractor",
                "description": "Extract specific data from text.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "pattern": {"type": "string"},
                    },
                    "required": ["text", "pattern"],
                },
            },
            {
                "name": "file_reader",
                "description": "Read contents of a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "file_writer",
                "description": "Write contents to a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "status_checker",
                "description": "Check status of a resource.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "resource": {"type": "string"},
                    },
                    "required": ["resource"],
                },
            },
            {
                "name": "action_executor",
                "description": "Execute an action on a resource.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "resource": {"type": "string"},
                    },
                    "required": ["action", "resource"],
                },
            },
            {
                "name": "data_fetcher",
                "description": "Fetch data from a source.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                    },
                    "required": ["source"],
                },
            },
            {
                "name": "aggregator",
                "description": "Aggregate data values.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "values": {"type": "array", "items": {"type": "number"}},
                        "method": {"type": "string", "enum": ["sum", "average", "max", "min"]},
                    },
                    "required": ["values", "method"],
                },
            },
            {
                "name": "formatter",
                "description": "Format data into specified format.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "object"},
                        "format": {"type": "string", "enum": ["json", "csv", "table", "report"]},
                    },
                    "required": ["data", "format"],
                },
            },
        ]

    def evaluate(self, task: Task, result: TaskResult) -> dict[str, float]:
        """Evaluate tool-intensive task result."""
        metrics = {}

        # Tool sequence similarity
        metrics["tool_sequence_similarity"] = compute_sequence_similarity(
            task.expected_tools, result.tool_sequence
        )

        # Tool coverage (did we use all expected tools?)
        if task.expected_tools:
            used_tools = set(result.tool_sequence)
            expected_tools = set(task.expected_tools)
            metrics["tool_coverage"] = len(used_tools & expected_tools) / len(expected_tools)
        else:
            metrics["tool_coverage"] = 1.0

        # Output correctness (if ground truth available)
        if task.ground_truth is not None:
            try:
                # Try to extract numeric result from output
                import re
                numbers = re.findall(r"[-+]?\d*\.?\d+", result.output)
                if numbers:
                    result_value = float(numbers[-1])
                    expected = float(task.ground_truth)
                    if expected != 0:
                        error = abs(result_value - expected) / abs(expected)
                        metrics["output_correctness"] = max(0, 1 - error)
                    else:
                        metrics["output_correctness"] = 1.0 if result_value == 0 else 0.0
                else:
                    metrics["output_correctness"] = 0.0
            except (ValueError, TypeError):
                metrics["output_correctness"] = 0.0
        else:
            metrics["output_correctness"] = 1.0 if result.success else 0.0

        # Efficiency (fewer tools is better for same task)
        expected_count = len(task.expected_tools)
        actual_count = len(result.tool_sequence)
        if expected_count > 0:
            metrics["efficiency"] = min(1.0, expected_count / max(actual_count, 1))
        else:
            metrics["efficiency"] = 1.0

        return metrics
