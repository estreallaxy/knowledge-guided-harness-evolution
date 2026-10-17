"""Experiment 6: Mitigation mechanisms."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import numpy as np
import structlog

from ..core import ExperimentConfig, PseConfig
from ..registry import NamespaceIsolation
from ..tasks import Task
from .runner import ExperimentRunner, ExperimentResult, RunResult

logger = structlog.get_logger()


class MitigationExperiment(ExperimentRunner):
    """
    Experiment 6: Control and Mitigation Mechanisms

    Purpose: Validate proposed mitigation methods for PSE issues.

    Proposed methods:
    1. Namespace isolation (per-agent/per-task)
    2. Registry lifecycle declarations
    3. Event hook audit and enumeration
    4. Propagation limits (no implicit nesting)

    Comparison:
    - No mitigation (baseline)
    - Basic mitigation (logging/whitelist)
    - Full proposed method

    Metrics:
    - Drift reduction rate
    - Security incident reduction
    - System overhead (latency, tokens)
    - Normal task success rate
    """

    @property
    def name(self) -> str:
        return "mitigation"

    def _get_mitigation_configs(self) -> list[tuple[str, PseConfig]]:
        """Get mitigation configurations."""
        return [
            # No mitigation - full PSE enabled
            ("no_mitigation", PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=True,
                namespace_isolation=NamespaceIsolation.NONE,
                enable_registry_lifecycle=False,
                enable_event_audit=False,
                enable_propagation_limits=False,
            )),
            # Basic mitigation - namespace isolation only
            ("basic_mitigation", PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=True,
                namespace_isolation=NamespaceIsolation.PER_TASK,
                enable_registry_lifecycle=False,
                enable_event_audit=False,
                enable_propagation_limits=False,
            )),
            # Full proposed mitigation
            ("full_mitigation", PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=True,
                namespace_isolation=NamespaceIsolation.PER_TASK,
                enable_registry_lifecycle=True,
                enable_event_audit=True,
                enable_propagation_limits=True,
                max_propagation_depth=3,
            )),
            # Mitigation with PSE disabled (upper bound)
            ("pse_disabled", PseConfig(
                enable_name_binding=False,
                enable_event_triggering=False,
                enable_propagation=False,
            )),
        ]

    async def run(self) -> ExperimentResult:
        """Run the mitigation experiment."""
        start_time = datetime.utcnow()

        configs = self._get_mitigation_configs()

        logger.info(
            "Starting mitigation experiment",
            experiment_id=self.config.experiment_id,
            num_configurations=len(configs),
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        all_runs = []
        config_results = {}

        for config_name, pse_config in configs:
            logger.info(f"Running mitigation config: {config_name}")

            agent = self._create_agent(pse_config)

            config_runs = []
            for task in tasks:
                for run_num in range(self.config.num_runs):
                    result = await self._run_task(agent, task, run_num)
                    result.metrics["mitigation_config"] = config_name

                    # Compute mitigation-specific metrics
                    mitigation_metrics = self._compute_mitigation_metrics(
                        result, config_name, pse_config
                    )
                    result.metrics.update(mitigation_metrics)

                    config_runs.append(result)
                    all_runs.append(result)

            config_results[config_name] = config_runs

        # Compute comparative metrics
        comparative_metrics = self._compute_comparative_metrics(config_results)

        end_time = datetime.utcnow()

        aggregate_metrics = self._aggregate_metrics(all_runs)
        aggregate_metrics.update(comparative_metrics)

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
                "configurations": [c[0] for c in configs],
                "config_results_summary": {
                    name: {
                        "num_runs": len(runs),
                        "success_rate": sum(1 for r in runs if r.task_result.success) / len(runs),
                        "avg_duration": np.mean([r.task_result.duration_ms for r in runs]),
                    }
                    for name, runs in config_results.items()
                },
            },
        )

        logger.info(
            "Mitigation experiment completed",
            experiment_id=self.config.experiment_id,
            drift_reduction=comparative_metrics.get("full_mitigation_drift_reduction", 0),
        )

        return result

    def _compute_mitigation_metrics(
        self,
        result: RunResult,
        config_name: str,
        pse_config: PseConfig,
    ) -> dict[str, float]:
        """Compute mitigation-specific metrics for a run."""
        metrics = {}

        pse_state = result.pse_state

        # Namespace isolation effectiveness
        if pse_config.namespace_isolation != NamespaceIsolation.NONE:
            registry_data = pse_state.get("registry", {})
            namespaces = registry_data.get("namespaces", {})
            # Check if entities are properly isolated
            metrics["namespace_count"] = len(namespaces)
            metrics["isolation_active"] = 1.0
        else:
            metrics["namespace_count"] = 1
            metrics["isolation_active"] = 0.0

        # Propagation limits effectiveness
        propagation_data = pse_state.get("propagation", {})
        total_propagations = propagation_data.get("total_propagations", 0)
        metrics["total_propagations"] = total_propagations

        if pse_config.enable_propagation_limits:
            # Check if propagation stayed within limits
            max_depth = pse_config.max_propagation_depth
            history = propagation_data.get("history", [])
            depths = [p.get("depth", 0) for p in history]
            max_observed_depth = max(depths) if depths else 0
            metrics["max_propagation_depth"] = max_observed_depth
            metrics["propagation_limited"] = 1.0 if max_observed_depth <= max_depth else 0.0
        else:
            metrics["propagation_limited"] = 0.0

        # Event audit effectiveness
        if pse_config.enable_event_audit:
            events_data = pse_state.get("events", {})
            total_events = events_data.get("total_events", 0)
            metrics["events_audited"] = total_events
            metrics["audit_active"] = 1.0
        else:
            metrics["audit_active"] = 0.0

        # System overhead
        metrics["latency_ms"] = result.task_result.duration_ms
        metrics["tokens_used"] = result.task_result.token_usage

        return metrics

    def _compute_comparative_metrics(
        self,
        config_results: dict[str, list[RunResult]],
    ) -> dict[str, float]:
        """Compute comparative metrics across configurations."""
        metrics = {}

        # Baseline (no mitigation) metrics
        baseline_runs = config_results.get("no_mitigation", [])
        if baseline_runs:
            baseline_success = sum(1 for r in baseline_runs if r.task_result.success) / len(baseline_runs)
            baseline_latency = np.mean([r.task_result.duration_ms for r in baseline_runs])
            baseline_tokens = np.mean([r.task_result.token_usage for r in baseline_runs])

            metrics["baseline_success_rate"] = baseline_success
            metrics["baseline_avg_latency_ms"] = baseline_latency
            metrics["baseline_avg_tokens"] = baseline_tokens

        # Compare each mitigation config to baseline
        for config_name, runs in config_results.items():
            if config_name == "no_mitigation" or not runs:
                continue

            success_rate = sum(1 for r in runs if r.task_result.success) / len(runs)
            avg_latency = np.mean([r.task_result.duration_ms for r in runs])
            avg_tokens = np.mean([r.task_result.token_usage for r in runs])

            metrics[f"{config_name}_success_rate"] = success_rate
            metrics[f"{config_name}_avg_latency_ms"] = avg_latency
            metrics[f"{config_name}_avg_tokens"] = avg_tokens

            # Compute relative improvements/overheads
            if baseline_runs:
                metrics[f"{config_name}_success_improvement"] = success_rate - baseline_success
                metrics[f"{config_name}_latency_overhead"] = (avg_latency - baseline_latency) / baseline_latency if baseline_latency > 0 else 0
                metrics[f"{config_name}_token_overhead"] = (avg_tokens - baseline_tokens) / baseline_tokens if baseline_tokens > 0 else 0

        # Compute drift metrics
        if baseline_runs:
            # Use tool sequence variance as proxy for drift
            def compute_sequence_variance(runs: list[RunResult]) -> float:
                sequences = [tuple(r.task_result.tool_sequence) for r in runs]
                unique_sequences = len(set(sequences))
                return unique_sequences / len(sequences) if sequences else 0

            baseline_variance = compute_sequence_variance(baseline_runs)
            metrics["baseline_sequence_variance"] = baseline_variance

            for config_name, runs in config_results.items():
                if config_name == "no_mitigation" or not runs:
                    continue

                config_variance = compute_sequence_variance(runs)
                metrics[f"{config_name}_sequence_variance"] = config_variance

                # Drift reduction (lower variance = less drift)
                if baseline_variance > 0:
                    drift_reduction = (baseline_variance - config_variance) / baseline_variance
                    metrics[f"{config_name}_drift_reduction"] = drift_reduction

        # Compute propagation reduction for full mitigation
        full_runs = config_results.get("full_mitigation", [])
        if baseline_runs and full_runs:
            baseline_props = np.mean([r.metrics.get("total_propagations", 0) for r in baseline_runs])
            full_props = np.mean([r.metrics.get("total_propagations", 0) for r in full_runs])

            if baseline_props > 0:
                metrics["propagation_reduction"] = (baseline_props - full_props) / baseline_props

        # Overall mitigation effectiveness score
        if "full_mitigation_drift_reduction" in metrics and "full_mitigation_success_improvement" in metrics:
            effectiveness = (
                0.4 * metrics.get("full_mitigation_drift_reduction", 0) +
                0.3 * metrics.get("full_mitigation_success_improvement", 0) +
                0.3 * (1 - metrics.get("full_mitigation_latency_overhead", 0))
            )
            metrics["full_mitigation_effectiveness"] = max(0, min(1, effectiveness))

        return metrics
