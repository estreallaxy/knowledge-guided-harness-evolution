"""Statistical analysis utilities for experiment results."""

from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass

import numpy as np
from scipy import stats
import structlog

logger = structlog.get_logger()


@dataclass
class TestResult:
    """Result of a statistical test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    effect_size: Optional[float] = None
    confidence_interval: Optional[tuple[float, float]] = None
    details: dict[str, Any] = None

    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "statistic": self.statistic,
            "p_value": self.p_value,
            "significant": self.significant,
            "effect_size": self.effect_size,
            "confidence_interval": self.confidence_interval,
            "details": self.details,
        }


class StatisticalTests:
    """Collection of statistical tests for experiment analysis."""

    @staticmethod
    def t_test(
        group1: list[float],
        group2: list[float],
        alpha: float = 0.05,
        paired: bool = False,
    ) -> TestResult:
        """Perform t-test between two groups."""
        if paired:
            stat, p_value = stats.ttest_rel(group1, group2)
        else:
            stat, p_value = stats.ttest_ind(group1, group2)

        # Cohen's d effect size
        pooled_std = np.sqrt((np.std(group1)**2 + np.std(group2)**2) / 2)
        effect_size = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0

        return TestResult(
            test_name="t-test" + (" (paired)" if paired else ""),
            statistic=stat,
            p_value=p_value,
            significant=p_value < alpha,
            effect_size=effect_size,
            details={
                "group1_mean": np.mean(group1),
                "group2_mean": np.mean(group2),
                "group1_std": np.std(group1),
                "group2_std": np.std(group2),
            },
        )

    @staticmethod
    def mann_whitney(
        group1: list[float],
        group2: list[float],
        alpha: float = 0.05,
    ) -> TestResult:
        """Perform Mann-Whitney U test (non-parametric)."""
        stat, p_value = stats.mannwhitneyu(group1, group2, alternative='two-sided')

        # Effect size (r = Z / sqrt(N))
        n1, n2 = len(group1), len(group2)
        z = stats.norm.ppf(1 - p_value / 2)
        effect_size = z / np.sqrt(n1 + n2)

        return TestResult(
            test_name="Mann-Whitney U",
            statistic=stat,
            p_value=p_value,
            significant=p_value < alpha,
            effect_size=effect_size,
        )

    @staticmethod
    def anova(
        *groups: list[float],
        alpha: float = 0.05,
    ) -> TestResult:
        """Perform one-way ANOVA."""
        stat, p_value = stats.f_oneway(*groups)

        # Eta-squared effect size
        all_values = np.concatenate(groups)
        grand_mean = np.mean(all_values)
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_total = sum((v - grand_mean)**2 for v in all_values)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        return TestResult(
            test_name="One-way ANOVA",
            statistic=stat,
            p_value=p_value,
            significant=p_value < alpha,
            effect_size=eta_squared,
            details={
                "num_groups": len(groups),
                "group_means": [np.mean(g) for g in groups],
            },
        )

    @staticmethod
    def chi_square(
        observed: list[float],
        expected: list[float],
        alpha: float = 0.05,
    ) -> TestResult:
        """Perform chi-square test."""
        stat, p_value = stats.chisquare(observed, expected)

        # Cramér's V effect size
        n = sum(observed)
        k = len(observed)
        cramers_v = np.sqrt(stat / (n * (k - 1))) if n > 0 and k > 1 else 0

        return TestResult(
            test_name="Chi-square",
            statistic=stat,
            p_value=p_value,
            significant=p_value < alpha,
            effect_size=cramers_v,
        )

    @staticmethod
    def bootstrap_ci(
        data: list[float],
        statistic_func: callable = np.mean,
        n_bootstrap: int = 10000,
        confidence: float = 0.95,
    ) -> tuple[float, float]:
        """Compute bootstrap confidence interval."""
        data = np.array(data)
        bootstrap_stats = []

        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_stats.append(statistic_func(sample))

        alpha = 1 - confidence
        lower = np.percentile(bootstrap_stats, alpha / 2 * 100)
        upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)

        return (lower, upper)


class MetricsAnalyzer:
    """Analyzer for experiment metrics."""

    def __init__(self):
        self.tests = StatisticalTests()

    def compare_conditions(
        self,
        baseline: list[float],
        treatment: list[float],
        metric_name: str,
        alpha: float = 0.05,
    ) -> dict[str, Any]:
        """Compare baseline and treatment conditions."""
        results = {
            "metric_name": metric_name,
            "baseline_stats": {
                "mean": np.mean(baseline),
                "std": np.std(baseline),
                "n": len(baseline),
            },
            "treatment_stats": {
                "mean": np.mean(treatment),
                "std": np.std(treatment),
                "n": len(treatment),
            },
            "difference": np.mean(treatment) - np.mean(baseline),
        }

        # Parametric test
        results["t_test"] = self.tests.t_test(baseline, treatment, alpha).to_dict()

        # Non-parametric test
        results["mann_whitney"] = self.tests.mann_whitney(baseline, treatment, alpha).to_dict()

        # Bootstrap CI for difference
        combined = np.array(treatment) - np.mean(baseline)
        results["difference_ci"] = self.tests.bootstrap_ci(list(combined))

        return results

    def analyze_ablation(
        self,
        results_by_config: dict[str, list[float]],
        metric_name: str,
    ) -> dict[str, Any]:
        """Analyze ablation study results."""
        analysis = {
            "metric_name": metric_name,
            "configs": {},
        }

        # Summary statistics for each config
        for config, values in results_by_config.items():
            analysis["configs"][config] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "n": len(values),
                "ci_95": self.tests.bootstrap_ci(values),
            }

        # ANOVA across all configs
        groups = list(results_by_config.values())
        if len(groups) >= 2:
            analysis["anova"] = self.tests.anova(*groups).to_dict()

        # Pairwise comparisons
        configs = list(results_by_config.keys())
        analysis["pairwise"] = {}
        for i, config1 in enumerate(configs):
            for config2 in configs[i+1:]:
                key = f"{config1}_vs_{config2}"
                analysis["pairwise"][key] = self.tests.t_test(
                    results_by_config[config1],
                    results_by_config[config2],
                ).to_dict()

        return analysis

    def analyze_drift(
        self,
        runs_by_task: dict[str, list[float]],
    ) -> dict[str, Any]:
        """Analyze behavioral drift across tasks."""
        analysis = {
            "num_tasks": len(runs_by_task),
            "per_task_variance": {},
            "overall_variance": 0,
        }

        all_variances = []
        for task_id, values in runs_by_task.items():
            variance = np.var(values)
            analysis["per_task_variance"][task_id] = variance
            all_variances.append(variance)

        analysis["overall_variance"] = np.mean(all_variances)
        analysis["variance_std"] = np.std(all_variances)

        # Coefficient of variation
        all_values = [v for values in runs_by_task.values() for v in values]
        mean_value = np.mean(all_values)
        if mean_value > 0:
            analysis["coefficient_of_variation"] = np.std(all_values) / mean_value
        else:
            analysis["coefficient_of_variation"] = 0

        return analysis

    def compute_effect_sizes(
        self,
        baseline: list[float],
        treatments: dict[str, list[float]],
    ) -> dict[str, dict[str, float]]:
        """Compute effect sizes for multiple treatments vs baseline."""
        effects = {}

        baseline_mean = np.mean(baseline)
        baseline_std = np.std(baseline)

        for treatment_name, treatment_values in treatments.items():
            treatment_mean = np.mean(treatment_values)
            treatment_std = np.std(treatment_values)

            # Cohen's d
            pooled_std = np.sqrt((baseline_std**2 + treatment_std**2) / 2)
            cohens_d = (treatment_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0

            # Percent change
            pct_change = (treatment_mean - baseline_mean) / baseline_mean * 100 if baseline_mean != 0 else 0

            effects[treatment_name] = {
                "cohens_d": cohens_d,
                "percent_change": pct_change,
                "absolute_difference": treatment_mean - baseline_mean,
                "interpretation": self._interpret_cohens_d(cohens_d),
            }

        return effects

    @staticmethod
    def _interpret_cohens_d(d: float) -> str:
        """Interpret Cohen's d effect size."""
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"
