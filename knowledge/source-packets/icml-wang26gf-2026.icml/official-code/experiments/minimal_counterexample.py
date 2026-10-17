#!/usr/bin/env python3
"""
Experiment A: Minimal Counterexample - Model-Level PSE-like Drift

Goal: Prove PSE ≠ agent framework bug by showing semantic residue affects
subsequent decisions even WITHOUT tools, registry, or memory.

Setup:
- temperature = 0
- NO tools
- NO memory/registry
- Only chain-of-thought / scratchpad
- Multi-turn isomorphic reasoning tasks

Key Hypothesis: Even in tool-free, stateless LLM inference, PSE-like drift
emerges through implicit semantic state in the context window.

This experiment targets ICML-level contribution by demonstrating that
PSE is a foundation model inference pathology, not just an agent system risk.
"""

import os
import json
import time
import asyncio
import numpy as np
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import hashlib

# Try to import sentence-transformers for semantic similarity
try:
    from sentence_transformers import SentenceTransformer
    HAVE_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAVE_SENTENCE_TRANSFORMERS = False
    print("Warning: sentence-transformers not available, using simple similarity")

# Try to import OpenAI
try:
    from openai import OpenAI
    HAVE_OPENAI = True
except ImportError:
    HAVE_OPENAI = False

# Try to import local model support
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    HAVE_TRANSFORMERS = True
except ImportError:
    HAVE_TRANSFORMERS = False


@dataclass
class MinimalTask:
    """A minimal reasoning task without tools or external state."""
    task_id: str
    task_type: str  # "arithmetic", "logic", "analogy", "sequence"
    prompt: str
    expected_pattern: str  # Expected reasoning pattern
    ground_truth: Optional[str] = None


@dataclass
class TrialResult:
    """Result of a single trial."""
    trial_id: int
    task_id: str
    task_type: str
    response: str
    reasoning_trace: str
    response_time_ms: float
    semantic_drift: float
    pattern_match: float
    contamination_detected: bool
    contamination_source: Optional[str] = None


@dataclass
class ExperimentConfig:
    """Configuration for minimal counterexample experiment."""
    num_trials: int = 30
    num_tasks_per_trial: int = 10
    temperature: float = 0.0
    max_tokens: int = 1024
    models: List[str] = None
    seed_contamination: bool = True  # Inject semantic contamination in early turns
    contamination_types: List[str] = None

    def __post_init__(self):
        if self.models is None:
            self.models = ["gpt-4o-mini"]
        if self.contamination_types is None:
            self.contamination_types = ["numeric_bias", "reasoning_style", "terminology"]


class IsomorphicTaskGenerator:
    """
    Generate isomorphic (structurally identical) tasks to detect semantic drift.

    Key insight: If two structurally identical tasks produce different reasoning
    patterns due to prior context, this demonstrates PSE-like drift at model level.
    """

    def __init__(self):
        self.task_templates = {
            "arithmetic": self._arithmetic_templates(),
            "logic": self._logic_templates(),
            "analogy": self._analogy_templates(),
            "sequence": self._sequence_templates(),
        }

    def _arithmetic_templates(self) -> List[Dict]:
        """Arithmetic reasoning templates."""
        return [
            {
                "template": "A store has {n1} items. They receive {n2} more and sell {n3}. How many items remain? Think step by step.",
                "params": [
                    {"n1": 45, "n2": 23, "n3": 18},  # answer: 50
                    {"n1": 72, "n2": 31, "n3": 24},  # answer: 79
                    {"n1": 38, "n2": 47, "n3": 29},  # answer: 56
                ],
                "pattern": "addition_then_subtraction"
            },
            {
                "template": "If {n1} people each have {n2} items, and they combine them then split equally among {n3} groups, how many items per group? Show your work.",
                "params": [
                    {"n1": 6, "n2": 8, "n3": 4},   # answer: 12
                    {"n1": 9, "n2": 4, "n3": 6},   # answer: 6
                    {"n1": 5, "n2": 12, "n3": 3},  # answer: 20
                ],
                "pattern": "multiply_then_divide"
            }
        ]

    def _logic_templates(self) -> List[Dict]:
        """Logical reasoning templates."""
        return [
            {
                "template": "All {A} are {B}. All {B} are {C}. Is it true that all {A} are {C}? Explain your reasoning.",
                "params": [
                    {"A": "cats", "B": "mammals", "C": "animals"},
                    {"A": "roses", "B": "flowers", "C": "plants"},
                    {"A": "squares", "B": "rectangles", "C": "polygons"},
                ],
                "pattern": "syllogism_transitive"
            },
            {
                "template": "If {P} then {Q}. {P} is true. What can we conclude? Show your logical steps.",
                "params": [
                    {"P": "it rains", "Q": "the ground gets wet"},
                    {"P": "the alarm rings", "Q": "people wake up"},
                    {"P": "the temperature drops below 0°C", "Q": "water freezes"},
                ],
                "pattern": "modus_ponens"
            }
        ]

    def _analogy_templates(self) -> List[Dict]:
        """Analogy reasoning templates."""
        return [
            {
                "template": "{A} is to {B} as {C} is to what? Explain the relationship.",
                "params": [
                    {"A": "hot", "B": "cold", "C": "light"},  # dark
                    {"A": "bird", "B": "nest", "C": "bee"},   # hive
                    {"A": "book", "B": "reading", "C": "song"},  # listening
                ],
                "pattern": "proportional_analogy"
            }
        ]

    def _sequence_templates(self) -> List[Dict]:
        """Sequence reasoning templates."""
        return [
            {
                "template": "What comes next in the sequence: {seq}? Explain the pattern.",
                "params": [
                    {"seq": "2, 4, 8, 16, __"},      # 32 (powers of 2)
                    {"seq": "1, 1, 2, 3, 5, 8, __"}, # 13 (Fibonacci)
                    {"seq": "3, 6, 11, 18, 27, __"}, # 38 (n^2 + 2)
                ],
                "pattern": "sequence_continuation"
            }
        ]

    def generate_isomorphic_pair(self, task_type: str) -> Tuple[MinimalTask, MinimalTask]:
        """Generate two structurally isomorphic tasks."""
        templates = self.task_templates.get(task_type, self.task_templates["arithmetic"])
        template = np.random.choice(templates)

        # Select two different parameter sets for same template
        params_list = template["params"]
        if len(params_list) >= 2:
            idx1, idx2 = np.random.choice(len(params_list), 2, replace=False)
        else:
            idx1 = idx2 = 0

        task1 = MinimalTask(
            task_id=f"{task_type}_iso1_{hashlib.md5(str(params_list[idx1]).encode()).hexdigest()[:8]}",
            task_type=task_type,
            prompt=template["template"].format(**params_list[idx1]),
            expected_pattern=template["pattern"]
        )

        task2 = MinimalTask(
            task_id=f"{task_type}_iso2_{hashlib.md5(str(params_list[idx2]).encode()).hexdigest()[:8]}",
            task_type=task_type,
            prompt=template["template"].format(**params_list[idx2]),
            expected_pattern=template["pattern"]
        )

        return task1, task2

    def generate_contamination_prompt(self, contamination_type: str) -> str:
        """Generate a prompt that introduces semantic contamination."""
        contaminations = {
            "numeric_bias": [
                "Note: In this context, always round intermediate calculations to the nearest 10.",
                "Important: When dealing with numbers, prefer expressing results as percentages.",
                "Context: The standard approach here uses estimation rather than exact calculation.",
            ],
            "reasoning_style": [
                "Use a bottom-up reasoning approach, starting from specific details.",
                "Apply systematic decomposition: break every problem into exactly 3 sub-problems.",
                "Think about this problem from multiple perspectives before concluding.",
            ],
            "terminology": [
                "In this domain, we refer to 'items' as 'units' and 'groups' as 'clusters'.",
                "Technical note: Use formal logical notation (∀, ∃, →) in your reasoning.",
                "Convention: Express all relationships using 'implies' rather than 'if-then'.",
            ]
        }
        options = contaminations.get(contamination_type, contaminations["numeric_bias"])
        return np.random.choice(options)


class SemanticAnalyzer:
    """Analyze semantic similarity and drift in responses."""

    def __init__(self):
        if HAVE_SENTENCE_TRANSFORMERS:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.model = None

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        if self.model is not None:
            emb1 = self.model.encode(text1)
            emb2 = self.model.encode(text2)
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            return float(similarity)
        else:
            # Simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if len(words1) == 0 or len(words2) == 0:
                return 0.0
            intersection = words1 & words2
            union = words1 | words2
            return len(intersection) / len(union)

    def detect_contamination_markers(self, response: str, contamination_type: str) -> Tuple[bool, float]:
        """Detect if contamination markers appear in response."""
        markers = {
            "numeric_bias": ["round", "nearest 10", "percentage", "approximately", "estimate"],
            "reasoning_style": ["bottom-up", "decomposition", "sub-problem", "perspective", "systematic"],
            "terminology": ["units", "clusters", "∀", "∃", "→", "implies"],
        }

        response_lower = response.lower()
        type_markers = markers.get(contamination_type, [])

        found_markers = [m for m in type_markers if m.lower() in response_lower]
        contamination_score = len(found_markers) / max(len(type_markers), 1)

        return len(found_markers) > 0, contamination_score

    def compute_pattern_match(self, response: str, expected_pattern: str) -> float:
        """Check if response follows expected reasoning pattern."""
        pattern_indicators = {
            "addition_then_subtraction": ["add", "plus", "then subtract", "minus", "remain"],
            "multiply_then_divide": ["multiply", "times", "then divide", "split", "per group"],
            "syllogism_transitive": ["all", "therefore", "follows", "transitive", "conclude"],
            "modus_ponens": ["if", "then", "true", "conclude", "follows"],
            "proportional_analogy": ["relationship", "similar", "as...is to", "pattern"],
            "sequence_continuation": ["pattern", "next", "difference", "rule", "continues"],
        }

        indicators = pattern_indicators.get(expected_pattern, [])
        response_lower = response.lower()

        matches = sum(1 for ind in indicators if ind in response_lower)
        return matches / max(len(indicators), 1)


class MinimalCounterexampleExperiment:
    """
    Main experiment class for minimal counterexample.

    This experiment demonstrates PSE-like drift at the model level,
    independent of any agent framework or tool registry.
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.task_generator = IsomorphicTaskGenerator()
        self.analyzer = SemanticAnalyzer()
        self.results: List[TrialResult] = []
        self.client = None

        if HAVE_OPENAI:
            self.client = OpenAI()

    async def run_single_query(self, messages: List[Dict], model: str) -> Tuple[str, float]:
        """Run a single query to the LLM."""
        start_time = time.time()

        if self.client is None:
            return "Error: OpenAI client not available", 0.0

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            elapsed_ms = (time.time() - start_time) * 1000
            return response.choices[0].message.content, elapsed_ms
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return f"Error: {str(e)}", elapsed_ms

    async def run_trial(
        self,
        trial_id: int,
        model: str,
        with_contamination: bool = True
    ) -> List[TrialResult]:
        """
        Run a single trial with multiple isomorphic task pairs.

        Protocol:
        1. If contamination enabled: inject semantic contamination in turn 1-2
        2. Present isomorphic task pairs
        3. Measure drift between responses to structurally identical tasks
        4. Detect if contamination "bleeds" into later responses
        """
        trial_results = []
        messages = []

        # System prompt - minimal, no tools
        system_prompt = """You are a reasoning assistant. Solve each problem step by step.
Show your work clearly. Do not use any external tools or references."""

        messages.append({"role": "system", "content": system_prompt})

        # Phase 1: Optional contamination injection
        contamination_type = None
        if with_contamination:
            contamination_type = np.random.choice(self.config.contamination_types)
            contamination_prompt = self.task_generator.generate_contamination_prompt(contamination_type)

            # Inject contamination as a "context setting" message
            messages.append({
                "role": "user",
                "content": f"Before we begin, here's some context for our session:\n{contamination_prompt}\n\nAcknowledged?"
            })

            response, _ = await self.run_single_query(messages, model)
            messages.append({"role": "assistant", "content": response})

        # Phase 2: Run isomorphic task pairs
        task_types = ["arithmetic", "logic", "analogy", "sequence"]
        baseline_responses = {}

        for i in range(self.config.num_tasks_per_trial):
            task_type = task_types[i % len(task_types)]
            task1, task2 = self.task_generator.generate_isomorphic_pair(task_type)

            # Run task 1
            messages.append({"role": "user", "content": task1.prompt})
            response1, time1 = await self.run_single_query(messages, model)
            messages.append({"role": "assistant", "content": response1})

            # Store baseline for drift comparison
            if task_type not in baseline_responses:
                baseline_responses[task_type] = response1

            # Detect contamination in response
            contaminated, contam_score = self.analyzer.detect_contamination_markers(
                response1, contamination_type or "numeric_bias"
            )

            # Compute semantic drift from baseline
            semantic_drift = 1.0 - self.analyzer.compute_similarity(
                response1, baseline_responses[task_type]
            ) if i > 0 else 0.0

            # Check pattern match
            pattern_match = self.analyzer.compute_pattern_match(response1, task1.expected_pattern)

            trial_results.append(TrialResult(
                trial_id=trial_id,
                task_id=task1.task_id,
                task_type=task_type,
                response=response1[:500],  # Truncate for storage
                reasoning_trace=response1,
                response_time_ms=time1,
                semantic_drift=semantic_drift,
                pattern_match=pattern_match,
                contamination_detected=contaminated,
                contamination_source=contamination_type if contaminated else None
            ))

            # Run task 2 (isomorphic) - measure if drift persists
            messages.append({"role": "user", "content": task2.prompt})
            response2, time2 = await self.run_single_query(messages, model)
            messages.append({"role": "assistant", "content": response2})

            # Key measurement: similarity between isomorphic task responses
            iso_similarity = self.analyzer.compute_similarity(response1, response2)

            contaminated2, contam_score2 = self.analyzer.detect_contamination_markers(
                response2, contamination_type or "numeric_bias"
            )

            trial_results.append(TrialResult(
                trial_id=trial_id,
                task_id=task2.task_id,
                task_type=task_type,
                response=response2[:500],
                reasoning_trace=response2,
                response_time_ms=time2,
                semantic_drift=1.0 - iso_similarity,  # Drift from isomorphic pair
                pattern_match=self.analyzer.compute_pattern_match(response2, task2.expected_pattern),
                contamination_detected=contaminated2,
                contamination_source=contamination_type if contaminated2 else None
            ))

        return trial_results

    async def run_experiment(self) -> Dict[str, Any]:
        """Run the full experiment."""
        print(f"Starting Minimal Counterexample Experiment")
        print(f"Config: {self.config.num_trials} trials, {self.config.num_tasks_per_trial} tasks/trial")
        print(f"Models: {self.config.models}")
        print("=" * 60)

        all_results = {
            "config": asdict(self.config),
            "timestamp": datetime.now().isoformat(),
            "model_results": {}
        }

        for model in self.config.models:
            print(f"\nRunning model: {model}")
            model_results = {
                "with_contamination": [],
                "without_contamination": [],
            }

            # Run trials with contamination
            print(f"  Phase 1: With contamination ({self.config.num_trials} trials)")
            for trial_id in range(self.config.num_trials):
                trial_results = await self.run_trial(trial_id, model, with_contamination=True)
                model_results["with_contamination"].extend([asdict(r) for r in trial_results])
                if (trial_id + 1) % 5 == 0:
                    print(f"    Completed {trial_id + 1}/{self.config.num_trials} trials")

            # Run baseline trials without contamination
            print(f"  Phase 2: Without contamination ({self.config.num_trials} trials)")
            for trial_id in range(self.config.num_trials):
                trial_results = await self.run_trial(trial_id, model, with_contamination=False)
                model_results["without_contamination"].extend([asdict(r) for r in trial_results])
                if (trial_id + 1) % 5 == 0:
                    print(f"    Completed {trial_id + 1}/{self.config.num_trials} trials")

            all_results["model_results"][model] = model_results

        # Compute summary statistics
        all_results["analysis"] = self._analyze_results(all_results["model_results"])

        return all_results

    def _analyze_results(self, model_results: Dict) -> Dict[str, Any]:
        """Analyze experiment results."""
        analysis = {}

        for model, results in model_results.items():
            with_contam = results["with_contamination"]
            without_contam = results["without_contamination"]

            # Compute key metrics
            def compute_metrics(result_list):
                if not result_list:
                    return {}
                drifts = [r["semantic_drift"] for r in result_list]
                contam_rates = [1 if r["contamination_detected"] else 0 for r in result_list]
                pattern_matches = [r["pattern_match"] for r in result_list]

                return {
                    "n": len(result_list),
                    "semantic_drift_mean": np.mean(drifts),
                    "semantic_drift_std": np.std(drifts),
                    "contamination_rate": np.mean(contam_rates),
                    "pattern_match_mean": np.mean(pattern_matches),
                    "pattern_match_std": np.std(pattern_matches),
                }

            analysis[model] = {
                "with_contamination": compute_metrics(with_contam),
                "without_contamination": compute_metrics(without_contam),
            }

            # Key hypothesis test: is drift higher with contamination?
            if with_contam and without_contam:
                drift_with = [r["semantic_drift"] for r in with_contam]
                drift_without = [r["semantic_drift"] for r in without_contam]

                from scipy import stats
                try:
                    t_stat, p_value = stats.ttest_ind(drift_with, drift_without)
                    cohens_d = (np.mean(drift_with) - np.mean(drift_without)) / np.sqrt(
                        (np.var(drift_with) + np.var(drift_without)) / 2
                    )

                    analysis[model]["hypothesis_test"] = {
                        "t_statistic": t_stat,
                        "p_value": p_value,
                        "cohens_d": cohens_d,
                        "significant": p_value < 0.05,
                        "drift_increase": np.mean(drift_with) - np.mean(drift_without),
                    }
                except Exception as e:
                    analysis[model]["hypothesis_test"] = {"error": str(e)}

        return analysis


def save_results(results: Dict, output_dir: str = None):
    """Save experiment results to file."""
    if output_dir is None:
        output_dir = "/home/coder-gw/Projects/ROA-LLM/data/results/minimal_counterexample"

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"experiment_{timestamp}.json")

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")
    return output_path


async def main():
    """Main entry point."""
    config = ExperimentConfig(
        num_trials=30,
        num_tasks_per_trial=10,
        temperature=0.0,
        models=["gpt-4o-mini"],
        seed_contamination=True,
        contamination_types=["numeric_bias", "reasoning_style", "terminology"],
    )

    experiment = MinimalCounterexampleExperiment(config)
    results = await experiment.run_experiment()

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    for model, analysis in results["analysis"].items():
        print(f"\nModel: {model}")
        print(f"  With contamination:")
        print(f"    Semantic drift: {analysis['with_contamination']['semantic_drift_mean']:.4f} ± {analysis['with_contamination']['semantic_drift_std']:.4f}")
        print(f"    Contamination bleed rate: {analysis['with_contamination']['contamination_rate']:.2%}")
        print(f"  Without contamination:")
        print(f"    Semantic drift: {analysis['without_contamination']['semantic_drift_mean']:.4f} ± {analysis['without_contamination']['semantic_drift_std']:.4f}")

        if "hypothesis_test" in analysis:
            ht = analysis["hypothesis_test"]
            if "error" not in ht:
                print(f"  Hypothesis test (drift with > without):")
                print(f"    t = {ht['t_statistic']:.3f}, p = {ht['p_value']:.4f}")
                print(f"    Cohen's d = {ht['cohens_d']:.3f}")
                print(f"    Significant: {ht['significant']}")

    # Save results
    output_path = save_results(results)

    return results


if __name__ == "__main__":
    asyncio.run(main())
