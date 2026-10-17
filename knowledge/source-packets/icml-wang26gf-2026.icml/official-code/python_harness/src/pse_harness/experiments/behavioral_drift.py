"""Experiment 1: Behavioral drift and stability analysis."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import numpy as np
import structlog

from ..core import ExperimentConfig, PseConfig
from ..tasks import Task, TaskResult
from .runner import ExperimentRunner, ExperimentResult, RunResult

logger = structlog.get_logger()


class BehavioralDriftExperiment(ExperimentRunner):
    """
    Experiment 1: Behavioral Drift and Stability (H1)

    Purpose: Verify whether PSE causes behavioral drift, output inconsistency,
    and tool call path variations.

    Compares three system configurations:
    1. No PSE (baseline)
    2. PSE with name binding + event triggering
    3. PSE with full propagation

    Metrics:
    - Success/failure rate
    - Tool call sequence edit distance
    - Output semantic consistency (LLM-as-judge)
    - Unexplained deviation ratio
    """

    @property
    def name(self) -> str:
        return "behavioral_drift"

    def _get_configurations(self) -> list[tuple[str, PseConfig]]:
        """Get the three configurations to compare."""
        return [
            ("no_pse", PseConfig(
                enable_name_binding=False,
                enable_event_triggering=False,
                enable_propagation=False,
            )),
            ("pse_basic", PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=False,
            )),
            ("pse_full", PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=True,
            )),
        ]

    async def run(self) -> ExperimentResult:
        """Run the behavioral drift experiment."""
        start_time = datetime.utcnow()

        logger.info(
            "Starting behavioral drift experiment",
            experiment_id=self.config.experiment_id,
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks once (same tasks for all configurations)
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        # Run experiments for each configuration
        all_runs = []
        config_results = {}

        for config_name, pse_config in self._get_configurations():
            logger.info(f"Running configuration: {config_name}")

            # Create agent with this config
            agent = self._create_agent(pse_config)

            # Run all tasks
            config_runs = []
            for task in tasks:
                for run_num in range(self.config.num_runs):
                    result = await self._run_task(agent, task, run_num)
                    result.metrics["config"] = config_name
                    config_runs.append(result)
                    all_runs.append(result)

            config_results[config_name] = config_runs

        # Compute drift metrics
        drift_metrics = self._compute_drift_metrics(tasks, config_results)

        end_time = datetime.utcnow()

        # Aggregate all metrics
        aggregate_metrics = self._aggregate_metrics(all_runs)
        aggregate_metrics.update(drift_metrics)

        result = ExperimentResult(
            experiment_id=self.config.experiment_id,
            experiment_name=self.name,
            config=self.config,
            tasks=tasks,
            runs=all_runs,
            aggregate_metrics=aggregate_metrics,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "configurations": [c[0] for c in self._get_configurations()],
                "config_results_summary": {
                    name: {
                        "num_runs": len(runs),
                        "success_rate": sum(1 for r in runs if r.task_result.success) / len(runs),
                    }
                    for name, runs in config_results.items()
                },
            },
        )

        logger.info(
            "Behavioral drift experiment completed",
            experiment_id=self.config.experiment_id,
            duration_seconds=(end_time - start_time).total_seconds(),
            drift_metrics=drift_metrics,
        )

        return result

    def _compute_drift_metrics(
        self,
        tasks: list[Task],
        config_results: dict[str, list[RunResult]],
    ) -> dict[str, float]:
        """Compute behavioral drift metrics across configurations."""
        metrics = {}

        # Group runs by task
        task_runs = {config: defaultdict(list) for config in config_results}
        for config, runs in config_results.items():
            for run in runs:
                task_runs[config][run.task_id].append(run)

        # Compute per-configuration consistency
        for config, runs_by_task in task_runs.items():
            consistencies = []
            for task_id, runs in runs_by_task.items():
                if len(runs) > 1:
                    consistency = self._compute_run_consistency(runs)
                    consistencies.append(consistency)

            if consistencies:
                metrics[f"{config}_internal_consistency"] = np.mean(consistencies)
                metrics[f"{config}_consistency_std"] = np.std(consistencies)

        # Compute cross-configuration drift
        baseline_config = "no_pse"
        for config in config_results:
            if config == baseline_config:
                continue

            drift_scores = []
            for task_id in set(r.task_id for r in config_results[baseline_config]):
                baseline_runs = task_runs[baseline_config][task_id]
                pse_runs = task_runs[config][task_id]

                if baseline_runs and pse_runs:
                    drift = self._compute_drift_between_configs(baseline_runs, pse_runs)
                    drift_scores.append(drift)

            if drift_scores:
                metrics[f"{config}_drift_from_baseline"] = np.mean(drift_scores)
                metrics[f"{config}_drift_std"] = np.std(drift_scores)

        # Compute overall drift indicator
        pse_drifts = [v for k, v in metrics.items() if "drift_from_baseline" in k]
        if pse_drifts:
            metrics["overall_pse_drift"] = np.mean(pse_drifts)

        return metrics

    def _compute_run_consistency(self, runs: list[RunResult]) -> float:
        """Compute consistency score across multiple runs of the same task."""
        if len(runs) < 2:
            return 1.0

        # Compare tool sequences
        sequences = [r.task_result.tool_sequence for r in runs]
        sequence_similarities = []

        for i in range(len(sequences)):
            for j in range(i + 1, len(sequences)):
                sim = self._sequence_similarity(sequences[i], sequences[j])
                sequence_similarities.append(sim)

        # Compare success rates
        success_rate = sum(1 for r in runs if r.task_result.success) / len(runs)

        # Combine metrics
        seq_consistency = np.mean(sequence_similarities) if sequence_similarities else 1.0
        return 0.5 * seq_consistency + 0.5 * (1 - abs(success_rate - 0.5) * 2)

    def _compute_drift_between_configs(
        self,
        baseline_runs: list[RunResult],
        pse_runs: list[RunResult],
    ) -> float:
        """Compute behavioral drift between baseline and PSE configurations."""
        # Compare tool sequence patterns
        baseline_sequences = [r.task_result.tool_sequence for r in baseline_runs]
        pse_sequences = [r.task_result.tool_sequence for r in pse_runs]

        # Average pairwise difference
        differences = []
        for b_seq in baseline_sequences:
            for p_seq in pse_sequences:
                diff = 1 - self._sequence_similarity(b_seq, p_seq)
                differences.append(diff)

        sequence_drift = np.mean(differences) if differences else 0

        # Compare success rates
        baseline_success = sum(1 for r in baseline_runs if r.task_result.success) / len(baseline_runs)
        pse_success = sum(1 for r in pse_runs if r.task_result.success) / len(pse_runs)
        success_drift = abs(baseline_success - pse_success)

        # Combine
        return 0.6 * sequence_drift + 0.4 * success_drift

    def _sequence_similarity(self, seq1: list[str], seq2: list[str]) -> float:
        """Compute similarity between two sequences using edit distance."""
        if not seq1 and not seq2:
            return 1.0
        if not seq1 or not seq2:
            return 0.0

        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )

        edit_distance = dp[m][n]
        max_len = max(m, n)
        return 1.0 - (edit_distance / max_len)
