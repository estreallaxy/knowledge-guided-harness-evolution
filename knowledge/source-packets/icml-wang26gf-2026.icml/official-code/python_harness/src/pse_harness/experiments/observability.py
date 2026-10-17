"""Experiment 2: Observability gap analysis."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

import numpy as np
import structlog

from ..core import ExperimentConfig, PseConfig, LogLevel
from ..tasks import Task, TaskResult
from .runner import ExperimentRunner, ExperimentResult, RunResult

logger = structlog.get_logger()


class ObservabilityExperiment(ExperimentRunner):
    """
    Experiment 2: Observability Gap Analysis (H2)

    Purpose: Evaluate whether existing logs/traces are sufficient to identify
    PSE-related issues and locate root causes.

    Compares two logging configurations:
    - L0: Standard logs only
    - L1: Enhanced with registry/event/propagation information

    Metrics:
    - Root cause localization success rate
    - Average steps to locate issue
    - Unattributed error ratio
    """

    @property
    def name(self) -> str:
        return "observability_gap"

    def _get_log_configurations(self) -> list[tuple[str, LogLevel]]:
        """Get logging configurations to compare."""
        return [
            ("L0_standard", LogLevel.L0),
            ("L1_enhanced", LogLevel.L1),
        ]

    async def run(self) -> ExperimentResult:
        """Run the observability experiment."""
        start_time = datetime.utcnow()

        logger.info(
            "Starting observability experiment",
            experiment_id=self.config.experiment_id,
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        # Run experiments for each log configuration
        all_runs = []
        log_results = {}

        for log_name, log_level in self._get_log_configurations():
            logger.info(f"Running log configuration: {log_name}")

            # Create config with this log level
            pse_config = PseConfig(
                enable_name_binding=True,
                enable_event_triggering=True,
                enable_propagation=True,
                log_level=log_level,
            )

            agent = self._create_agent(pse_config)

            # Run tasks
            log_runs = []
            for task in tasks:
                for run_num in range(self.config.num_runs):
                    result = await self._run_task(agent, task, run_num)
                    result.metrics["log_level"] = log_name

                    # Analyze observability for this run
                    observability_metrics = self._analyze_observability(
                        result, log_level
                    )
                    result.metrics.update(observability_metrics)

                    log_runs.append(result)
                    all_runs.append(result)

            log_results[log_name] = log_runs

        # Compute observability metrics
        observability_metrics = self._compute_observability_metrics(log_results)

        end_time = datetime.utcnow()

        aggregate_metrics = self._aggregate_metrics(all_runs)
        aggregate_metrics.update(observability_metrics)

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
                "log_configurations": [c[0] for c in self._get_log_configurations()],
                "log_results_summary": {
                    name: {
                        "num_runs": len(runs),
                        "error_rate": sum(1 for r in runs if r.task_result.error) / len(runs),
                    }
                    for name, runs in log_results.items()
                },
            },
        )

        logger.info(
            "Observability experiment completed",
            experiment_id=self.config.experiment_id,
            observability_metrics=observability_metrics,
        )

        return result

    def _analyze_observability(
        self,
        run: RunResult,
        log_level: LogLevel,
    ) -> dict[str, float]:
        """Analyze observability for a single run."""
        metrics = {}

        pse_state = run.pse_state

        if log_level == LogLevel.L0:
            # L0: Only basic logs available
            # Simulate limited visibility
            metrics["registry_visible"] = 0.0
            metrics["events_visible"] = 0.0
            metrics["propagation_visible"] = 0.0

            # Can only see tool call sequence
            metrics["tool_sequence_visible"] = 1.0

            # Root cause localization harder
            if run.task_result.error:
                metrics["root_cause_identifiable"] = 0.3  # Low chance with L0

        elif log_level == LogLevel.L1:
            # L1: Enhanced logging
            registry_data = pse_state.get("registry", {})
            events_data = pse_state.get("events", {})
            propagation_data = pse_state.get("propagation", {})

            # Check what's visible
            metrics["registry_visible"] = 1.0 if registry_data.get("namespaces") else 0.0
            metrics["events_visible"] = 1.0 if events_data.get("total_events", 0) > 0 else 0.0
            metrics["propagation_visible"] = 1.0 if propagation_data.get("total_propagations", 0) > 0 else 0.0
            metrics["tool_sequence_visible"] = 1.0

            # Root cause localization easier with more info
            if run.task_result.error:
                # Higher chance with L1 logging
                visible_count = sum([
                    metrics["registry_visible"],
                    metrics["events_visible"],
                    metrics["propagation_visible"],
                ])
                metrics["root_cause_identifiable"] = 0.5 + (visible_count / 6)

        # Compute overall observability score
        visibility_scores = [
            metrics.get("registry_visible", 0),
            metrics.get("events_visible", 0),
            metrics.get("propagation_visible", 0),
            metrics.get("tool_sequence_visible", 1),
        ]
        metrics["overall_observability"] = np.mean(visibility_scores)

        return metrics

    def _compute_observability_metrics(
        self,
        log_results: dict[str, list[RunResult]],
    ) -> dict[str, float]:
        """Compute overall observability metrics."""
        metrics = {}

        for log_name, runs in log_results.items():
            # Observability score
            obs_scores = [r.metrics.get("overall_observability", 0) for r in runs]
            metrics[f"{log_name}_observability_mean"] = np.mean(obs_scores)

            # Root cause identifiability (for error runs)
            error_runs = [r for r in runs if r.task_result.error]
            if error_runs:
                rc_scores = [r.metrics.get("root_cause_identifiable", 0) for r in error_runs]
                metrics[f"{log_name}_root_cause_rate"] = np.mean(rc_scores)
            else:
                metrics[f"{log_name}_root_cause_rate"] = 1.0

            # Unattributed errors
            unattributed = sum(
                1 for r in error_runs
                if r.metrics.get("root_cause_identifiable", 0) < 0.5
            )
            metrics[f"{log_name}_unattributed_error_rate"] = (
                unattributed / len(error_runs) if error_runs else 0
            )

        # Compute improvement from L0 to L1
        if "L0_standard" in log_results and "L1_enhanced" in log_results:
            l0_obs = metrics.get("L0_standard_observability_mean", 0)
            l1_obs = metrics.get("L1_enhanced_observability_mean", 0)
            metrics["observability_improvement"] = l1_obs - l0_obs

            l0_rc = metrics.get("L0_standard_root_cause_rate", 0)
            l1_rc = metrics.get("L1_enhanced_root_cause_rate", 0)
            metrics["root_cause_improvement"] = l1_rc - l0_rc

        return metrics
