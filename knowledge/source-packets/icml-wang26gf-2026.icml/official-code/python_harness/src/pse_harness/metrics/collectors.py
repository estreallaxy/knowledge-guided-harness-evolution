"""Metrics collection utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np
import structlog

logger = structlog.get_logger()


@dataclass
class ExperimentMetrics:
    """Collection of metrics from an experiment."""
    experiment_id: str
    experiment_name: str
    metrics: dict[str, float] = field(default_factory=dict)
    per_run_metrics: list[dict[str, float]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add_metric(self, name: str, value: float) -> None:
        """Add a metric."""
        self.metrics[name] = value

    def add_run_metrics(self, run_metrics: dict[str, float]) -> None:
        """Add metrics from a single run."""
        self.per_run_metrics.append(run_metrics)

    def get_metric(self, name: str, default: float = 0.0) -> float:
        """Get a metric value."""
        return self.metrics.get(name, default)

    def get_metric_distribution(self, metric_name: str) -> list[float]:
        """Get distribution of a metric across runs."""
        return [m.get(metric_name, 0) for m in self.per_run_metrics]

    def compute_statistics(self, metric_name: str) -> dict[str, float]:
        """Compute statistics for a metric."""
        values = self.get_metric_distribution(metric_name)
        if not values:
            return {}

        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "q25": np.percentile(values, 25),
            "q75": np.percentile(values, 75),
        }

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "experiment_name": self.experiment_name,
            "metrics": self.metrics,
            "num_runs": len(self.per_run_metrics),
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsCollector:
    """Collector for aggregating metrics across experiments."""

    def __init__(self):
        self._experiments: dict[str, ExperimentMetrics] = {}
        self._global_metrics: dict[str, list[float]] = {}

    def register_experiment(self, experiment_id: str, experiment_name: str) -> ExperimentMetrics:
        """Register a new experiment."""
        metrics = ExperimentMetrics(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
        )
        self._experiments[experiment_id] = metrics
        return metrics

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentMetrics]:
        """Get metrics for an experiment."""
        return self._experiments.get(experiment_id)

    def add_global_metric(self, name: str, value: float) -> None:
        """Add a value to a global metric."""
        if name not in self._global_metrics:
            self._global_metrics[name] = []
        self._global_metrics[name].append(value)

    def get_global_statistics(self, metric_name: str) -> dict[str, float]:
        """Get statistics for a global metric."""
        values = self._global_metrics.get(metric_name, [])
        if not values:
            return {}

        return {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "count": len(values),
        }

    def compare_experiments(
        self,
        experiment_ids: list[str],
        metric_names: list[str],
    ) -> dict[str, dict[str, dict[str, float]]]:
        """Compare metrics across experiments."""
        comparison = {}

        for metric_name in metric_names:
            comparison[metric_name] = {}

            for exp_id in experiment_ids:
                exp_metrics = self._experiments.get(exp_id)
                if exp_metrics:
                    comparison[metric_name][exp_id] = exp_metrics.compute_statistics(metric_name)

        return comparison

    def export_all(self) -> dict:
        """Export all collected metrics."""
        return {
            "experiments": {
                exp_id: metrics.to_dict()
                for exp_id, metrics in self._experiments.items()
            },
            "global_metrics": {
                name: {
                    "values": values,
                    "statistics": self.get_global_statistics(name),
                }
                for name, values in self._global_metrics.items()
            },
        }
