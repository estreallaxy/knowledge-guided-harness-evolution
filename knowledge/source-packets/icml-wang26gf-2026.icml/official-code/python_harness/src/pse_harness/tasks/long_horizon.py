"""Long-horizon consistency task generator."""

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


class LongHorizonTaskGenerator(TaskGenerator):
    """Generator for long-horizon tasks requiring consistent behavior across multiple rounds."""

    CONSTRAINT_TYPES = [
        {
            "name": "format_constraint",
            "description": "Maintain output format across responses",
            "template": "You must always respond in {format} format. {task}",
            "constraint": "format",
        },
        {
            "name": "persona_constraint",
            "description": "Maintain a consistent persona",
            "template": "You are {persona}. Respond as this character would. {task}",
            "constraint": "persona",
        },
        {
            "name": "rule_constraint",
            "description": "Follow specific rules consistently",
            "template": "Follow these rules strictly: {rules}. Now complete: {task}",
            "constraint": "rules",
        },
        {
            "name": "preference_constraint",
            "description": "Remember and apply user preferences",
            "template": "Remember my preference: {preference}. Apply it to: {task}",
            "constraint": "preference",
        },
        {
            "name": "policy_constraint",
            "description": "Adhere to specified policies",
            "template": "Policy: {policy}. Under this policy, {task}",
            "constraint": "policy",
        },
    ]

    FORMATS = ["JSON", "XML", "markdown bullet points", "numbered list", "table"]
    PERSONAS = [
        "a formal business consultant",
        "a friendly teacher",
        "a technical expert",
        "a cautious advisor",
        "a creative writer",
    ]
    RULES = [
        "Never use the word 'very'. Always be concise.",
        "End every response with a summary. Use active voice.",
        "Include exactly 3 examples in every response.",
        "Always cite sources. Use formal language.",
        "Provide pros and cons for every suggestion.",
    ]
    PREFERENCES = [
        "I prefer detailed explanations with examples",
        "Keep responses under 100 words",
        "Always include code examples in Python",
        "Use analogies to explain concepts",
        "Prioritize accuracy over speed",
    ]
    POLICIES = [
        "All data must be treated as confidential",
        "Recommendations must be evidence-based",
        "Actions require explicit user confirmation",
        "External resources cannot be accessed",
        "All outputs must be reviewed before final",
    ]

    FOLLOW_UP_TASKS = [
        "Now explain {topic} following the same constraints.",
        "Apply the same rules to analyze {topic}.",
        "Continue with {topic}, maintaining consistency.",
        "Given the above, how would you handle {topic}?",
        "Extend your approach to cover {topic}.",
    ]

    TOPICS = [
        "data privacy",
        "system architecture",
        "user authentication",
        "error handling",
        "performance optimization",
        "code review",
        "documentation standards",
        "testing strategies",
    ]

    @property
    def family(self) -> TaskFamily:
        return TaskFamily.LONG_HORIZON

    def generate(self, constraint_type: Optional[str] = None, num_rounds: int = 3, **kwargs) -> Task:
        """Generate a long-horizon consistency task."""
        if constraint_type:
            template = next(
                (t for t in self.CONSTRAINT_TYPES if t["name"] == constraint_type),
                self._rng.choice(self.CONSTRAINT_TYPES),
            )
        else:
            template = self._rng.choice(self.CONSTRAINT_TYPES)

        params = self._generate_params(template["constraint"])
        params["num_rounds"] = num_rounds

        # Generate initial task
        initial_topic = self._rng.choice(self.TOPICS)
        params["initial_topic"] = initial_topic
        params["task"] = f"Explain {initial_topic}."

        # Generate follow-up prompts
        follow_ups = []
        for i in range(num_rounds - 1):
            topic = self._rng.choice([t for t in self.TOPICS if t != initial_topic])
            follow_up = self._rng.choice(self.FOLLOW_UP_TASKS).format(topic=topic)
            follow_ups.append(follow_up)

        params["follow_ups"] = follow_ups

        prompt = template["template"].format(**params)

        return Task(
            id=self._next_id(),
            family=self.family,
            name=template["name"],
            description=template["description"],
            prompt=prompt,
            expected_tools=[],  # Long-horizon tasks typically don't require tools
            difficulty=TaskDifficulty.HARD if num_rounds > 3 else TaskDifficulty.MEDIUM,
            parameters=params,
            metadata={
                "constraint_type": template["constraint"],
                "num_rounds": num_rounds,
                "follow_ups": follow_ups,
            },
        )

    def _generate_params(self, constraint_type: str) -> dict[str, Any]:
        """Generate parameters for a constraint type."""
        params = {}

        if constraint_type == "format":
            params["format"] = self._rng.choice(self.FORMATS)
        elif constraint_type == "persona":
            params["persona"] = self._rng.choice(self.PERSONAS)
        elif constraint_type == "rules":
            params["rules"] = self._rng.choice(self.RULES)
        elif constraint_type == "preference":
            params["preference"] = self._rng.choice(self.PREFERENCES)
        elif constraint_type == "policy":
            params["policy"] = self._rng.choice(self.POLICIES)

        return params

    def get_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions (minimal for long-horizon tasks)."""
        return [
            {
                "name": "memory_recall",
                "description": "Recall previous conversation context or constraints.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "constraint_check",
                "description": "Verify if output adheres to specified constraints.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "constraint": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["constraint", "content"],
                },
            },
        ]

    def evaluate(self, task: Task, result: TaskResult) -> dict[str, float]:
        """Evaluate long-horizon task result."""
        metrics = {}

        # Constraint adherence
        constraint_type = task.metadata.get("constraint_type", "")
        constraint_score = self._check_constraint_adherence(
            constraint_type, task.parameters, result.output
        )
        metrics["constraint_adherence"] = constraint_score

        # Consistency across rounds (if multiple outputs)
        # This would need multi-round execution results
        metrics["consistency_score"] = constraint_score  # Simplified

        # Completeness
        metrics["completeness"] = 1.0 if len(result.output) > 50 else 0.5

        return metrics

    def _check_constraint_adherence(
        self, constraint_type: str, params: dict[str, Any], output: str
    ) -> float:
        """Check if output adheres to the specified constraint."""
        output_lower = output.lower()

        if constraint_type == "format":
            format_type = params.get("format", "").lower()
            if format_type == "json":
                return 1.0 if "{" in output and "}" in output else 0.0
            elif format_type == "xml":
                return 1.0 if "<" in output and ">" in output else 0.0
            elif "bullet" in format_type:
                return 1.0 if ("- " in output or "* " in output) else 0.0
            elif "numbered" in format_type:
                return 1.0 if any(f"{i}." in output for i in range(1, 10)) else 0.0
            elif "table" in format_type:
                return 1.0 if "|" in output else 0.0

        elif constraint_type == "rules":
            rules = params.get("rules", "").lower()
            if "never use the word 'very'" in rules:
                return 0.0 if "very" in output_lower else 1.0
            elif "end every response with a summary" in rules:
                return 1.0 if "summary" in output_lower[-200:] else 0.5
            elif "include exactly 3 examples" in rules:
                # Count "example" or numbered items
                example_count = output_lower.count("example")
                return 1.0 if example_count >= 3 else example_count / 3

        elif constraint_type == "preference":
            pref = params.get("preference", "").lower()
            if "under 100 words" in pref:
                word_count = len(output.split())
                return 1.0 if word_count <= 100 else max(0, 1 - (word_count - 100) / 100)
            elif "python" in pref:
                return 1.0 if "```python" in output_lower or "def " in output else 0.5

        # Default: partial credit for non-empty output
        return 0.7 if output else 0.0
