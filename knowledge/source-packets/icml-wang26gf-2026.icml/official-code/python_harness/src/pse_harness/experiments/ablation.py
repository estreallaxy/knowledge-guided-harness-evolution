"""Experiment 3: Mechanism ablation study (2x2x2)."""

from __future__ import annotations

import asyncio
import itertools
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


class AblationExperiment(ExperimentRunner):
    """
    Experiment 3: Mechanism Ablation Study (H3)

    Purpose: Demonstrate non-equivalence and non-linear combination effects
    of the three PSE components.

    Design: 2x2x2 factorial design
    - Name binding: on/off
    - Event triggering: on/off
    - Propagation: on/off

    Total: 8 configurations

    Metrics:
    - Performance metrics per configuration
    - Interaction effects between components
    - Main effects of each component
    """

    @property
    def name(self) -> str:
        return "mechanism_ablation"

    def _get_ablation_configs(self) -> list[tuple[str, PseConfig]]:
        """Generate all 2x2x2 configurations."""
        configs = []

        for nb, et, pr in itertools.product([False, True], repeat=3):
            name = f"nb{int(nb)}_et{int(et)}_pr{int(pr)}"
            config = PseConfig(
                enable_name_binding=nb,
                enable_event_triggering=et,
                enable_propagation=pr,
            )
            configs.append((name, config))

        return configs

    async def run(self) -> ExperimentResult:
        """Run the ablation experiment."""
        start_time = datetime.utcnow()

        configs = self._get_ablation_configs()

        logger.info(
            "Starting ablation experiment",
            experiment_id=self.config.experiment_id,
            num_configurations=len(configs),
            num_tasks=self.config.num_tasks,
            num_runs=self.config.num_runs,
        )

        # Generate tasks once
        generator = self._get_task_generator()
        tasks = generator.generate_batch(self.config.num_tasks)

        # Run all configurations
        all_runs = []
        config_results = {}

        for config_name, pse_config in configs:
            logger.info(f"Running ablation configuration: {config_name}")

            agent = self._create_agent(pse_config)

            config_runs = []
            for task in tasks:
                for run_num in range(self.config.num_runs):
                    result = await self._run_task(agent, task, run_num)
                    result.metrics["ablation_config"] = config_name
                    result.metrics["name_binding"] = int(pse_config.enable_name_binding)
                    result.metrics["event_triggering"] = int(pse_config.enable_event_triggering)
                    result.metrics["propagation"] = int(pse_config.enable_propagation)
                    config_runs.append(result)
                    all_runs.append(result)

            config_results[config_name] = config_runs

        # Compute ablation analysis
        ablation_metrics = self._compute_ablation_analysis(config_results)

        end_time = datetime.utcnow()

        aggregate_metrics = self._aggregate_metrics(all_runs)
        aggregate_metrics.update(ablation_metrics)

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
                "factorial_design": "2x2x2",
                "factors": ["name_binding", "event_triggering", "propagation"],
            },
        )

        logger.info(
            "Ablation experiment completed",
            experiment_id=self.config.experiment_id,
            num_configurations=len(configs),
        )

        return result

    def _compute_ablation_analysis(
        self,
        config_results: dict[str, list[RunResult]],
    ) -> dict[str, float]:
        """Compute ablation analysis metrics."""
        metrics = {}

        # Compute performance for each configuration
        config_performance = {}
        for config_name, runs in config_results.items():
            success_rate = sum(1 for r in runs if r.task_result.success) / len(runs)
            avg_duration = np.mean([r.task_result.duration_ms for r in runs])
            avg_tokens = np.mean([r.task_result.token_usage for r in runs])

            config_performance[config_name] = {
                "success_rate": success_rate,
                "avg_duration": avg_duration,
                "avg_tokens": avg_tokens,
            }

            metrics[f"{config_name}_success_rate"] = success_rate
            metrics[f"{config_name}_avg_duration_ms"] = avg_duration

        # Compute main effects
        main_effects = self._compute_main_effects(config_results, config_performance)
        metrics.update(main_effects)

        # Compute interaction effects
        interaction_effects = self._compute_interaction_effects(config_results, config_performance)
        metrics.update(interaction_effects)

        return metrics

    def _compute_main_effects(
        self,
        config_results: dict[str, list[RunResult]],
        config_performance: dict[str, dict[str, float]],
    ) -> dict[str, float]:
        """Compute main effects for each factor."""
        metrics = {}

        factors = ["name_binding", "event_triggering", "propagation"]

        for factor_idx, factor in enumerate(factors):
            # Split configs by factor value
            factor_on = []
            factor_off = []

            for config_name, perf in config_performance.items():
                # Parse config name to get factor values
                parts = config_name.split("_")
                factor_value = int(parts[factor_idx][-1])

                if factor_value:
                    factor_on.append(perf["success_rate"])
                else:
                    factor_off.append(perf["success_rate"])

            # Main effect = mean(on) - mean(off)
            if factor_on and factor_off:
                main_effect = np.mean(factor_on) - np.mean(factor_off)
                metrics[f"main_effect_{factor}"] = main_effect

        return metrics

    def _compute_interaction_effects(
        self,
        config_results: dict[str, list[RunResult]],
        config_performance: dict[str, dict[str, float]],
    ) -> dict[str, float]:
        """Compute two-way interaction effects."""
        metrics = {}

        # Get performance values organized by factor levels
        perf_by_factors = {}
        for config_name, perf in config_performance.items():
            parts = config_name.split("_")
            nb = int(parts[0][-1])
            et = int(parts[1][-1])
            pr = int(parts[2][-1])
            perf_by_factors[(nb, et, pr)] = perf["success_rate"]

        # NB x ET interaction
        nb0_et0 = [perf_by_factors.get((0, 0, pr), 0) for pr in [0, 1]]
        nb0_et1 = [perf_by_factors.get((0, 1, pr), 0) for pr in [0, 1]]
        nb1_et0 = [perf_by_factors.get((1, 0, pr), 0) for pr in [0, 1]]
        nb1_et1 = [perf_by_factors.get((1, 1, pr), 0) for pr in [0, 1]]

        interaction_nb_et = (
            (np.mean(nb1_et1) - np.mean(nb1_et0)) -
            (np.mean(nb0_et1) - np.mean(nb0_et0))
        )
        metrics["interaction_nb_et"] = interaction_nb_et

        # NB x PR interaction
        nb0_pr0 = [perf_by_factors.get((0, et, 0), 0) for et in [0, 1]]
        nb0_pr1 = [perf_by_factors.get((0, et, 1), 0) for et in [0, 1]]
        nb1_pr0 = [perf_by_factors.get((1, et, 0), 0) for et in [0, 1]]
        nb1_pr1 = [perf_by_factors.get((1, et, 1), 0) for et in [0, 1]]

        interaction_nb_pr = (
            (np.mean(nb1_pr1) - np.mean(nb1_pr0)) -
            (np.mean(nb0_pr1) - np.mean(nb0_pr0))
        )
        metrics["interaction_nb_pr"] = interaction_nb_pr

        # ET x PR interaction
        et0_pr0 = [perf_by_factors.get((nb, 0, 0), 0) for nb in [0, 1]]
        et0_pr1 = [perf_by_factors.get((nb, 0, 1), 0) for nb in [0, 1]]
        et1_pr0 = [perf_by_factors.get((nb, 1, 0), 0) for nb in [0, 1]]
        et1_pr1 = [perf_by_factors.get((nb, 1, 1), 0) for nb in [0, 1]]

        interaction_et_pr = (
            (np.mean(et1_pr1) - np.mean(et1_pr0)) -
            (np.mean(et0_pr1) - np.mean(et0_pr0))
        )
        metrics["interaction_et_pr"] = interaction_et_pr

        # Three-way interaction
        # Effect difference when third factor is on vs off
        three_way = (
            (perf_by_factors.get((1, 1, 1), 0) - perf_by_factors.get((1, 1, 0), 0)) -
            (perf_by_factors.get((1, 0, 1), 0) - perf_by_factors.get((1, 0, 0), 0)) -
            (perf_by_factors.get((0, 1, 1), 0) - perf_by_factors.get((0, 1, 0), 0)) +
            (perf_by_factors.get((0, 0, 1), 0) - perf_by_factors.get((0, 0, 0), 0))
        )
        metrics["interaction_nb_et_pr"] = three_way

        return metrics
