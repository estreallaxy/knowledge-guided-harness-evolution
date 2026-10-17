"""Command-line interface for PSE experiments."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import structlog

from .core import ExperimentConfig, PseConfig
from .experiments import (
    BehavioralDriftExperiment,
    ObservabilityExperiment,
    AblationExperiment,
    PropagationRecoveryExperiment,
    SecurityBoundaryExperiment,
    MitigationExperiment,
)
from .experiments.runner import SimpleExperimentRunner

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


EXPERIMENTS = {
    "behavioral_drift": BehavioralDriftExperiment,
    "observability": ObservabilityExperiment,
    "ablation": AblationExperiment,
    "propagation_recovery": PropagationRecoveryExperiment,
    "security_boundary": SecurityBoundaryExperiment,
    "mitigation": MitigationExperiment,
    "simple": SimpleExperimentRunner,
}


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="PSE Experiment Runner - Tool-augmented LLM Research Framework"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run experiment command
    run_parser = subparsers.add_parser("run", help="Run an experiment")
    run_parser.add_argument(
        "experiment",
        choices=list(EXPERIMENTS.keys()),
        help="Experiment to run",
    )
    run_parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to config JSON file",
    )
    run_parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4o-mini",
        help="Model to use (default: gpt-4o-mini)",
    )
    run_parser.add_argument(
        "--provider", "-p",
        type=str,
        default="openai",
        choices=["openai", "anthropic"],
        help="Model provider (default: openai)",
    )
    run_parser.add_argument(
        "--num-tasks", "-n",
        type=int,
        default=10,
        help="Number of tasks to run (default: 10)",
    )
    run_parser.add_argument(
        "--num-runs", "-r",
        type=int,
        default=5,
        help="Number of runs per task (default: 5)",
    )
    run_parser.add_argument(
        "--task-family", "-t",
        type=str,
        default="tool_intensive",
        choices=["tool_intensive", "long_horizon", "policy_bound"],
        help="Task family (default: tool_intensive)",
    )
    run_parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="data/results",
        help="Output directory (default: data/results)",
    )
    run_parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    run_parser.add_argument(
        "--api-key",
        type=str,
        help="API key (or set OPENAI_API_KEY env var)",
    )

    # List experiments command
    list_parser = subparsers.add_parser("list", help="List available experiments")

    # Analyze results command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze experiment results")
    analyze_parser.add_argument(
        "results_dir",
        type=str,
        help="Directory containing experiment results",
    )
    analyze_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for analysis report",
    )

    # Generate config command
    config_parser = subparsers.add_parser("config", help="Generate experiment config")
    config_parser.add_argument(
        "experiment",
        choices=list(EXPERIMENTS.keys()),
        help="Experiment type",
    )
    config_parser.add_argument(
        "--output", "-o",
        type=str,
        default="config.json",
        help="Output config file",
    )

    return parser


async def run_experiment(args: argparse.Namespace) -> int:
    """Run an experiment."""
    # Build config
    if args.config:
        config = ExperimentConfig.load(Path(args.config))
    else:
        config = ExperimentConfig(
            experiment_name=args.experiment,
            model_provider=args.provider,
            model_name=args.model,
            num_tasks=args.num_tasks,
            num_runs=args.num_runs,
            task_family=args.task_family,
            output_dir=Path(args.output_dir),
            seed=args.seed,
        )

    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key and args.provider == "openai":
        print("Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        return 1

    # Create experiment runner
    experiment_class = EXPERIMENTS[args.experiment]
    runner = experiment_class(config, api_key=api_key)

    # Run experiment
    print(f"Starting experiment: {args.experiment}")
    print(f"Config: {config.model_dump_json(indent=2)}")

    result = await runner.run()

    # Save results
    output_path = config.get_output_path()
    result.save(output_path)

    print(f"\nExperiment completed!")
    print(f"Results saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  - Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
    print(f"  - Tasks: {len(result.tasks)}")
    print(f"  - Runs: {len(result.runs)}")
    print(f"  - Success rate: {result.aggregate_metrics.get('success_rate', 0):.2%}")

    return 0


def list_experiments() -> int:
    """List available experiments."""
    print("Available experiments:")
    print()

    descriptions = {
        "behavioral_drift": "H1: Behavioral drift and stability analysis",
        "observability": "H2: Observability gap analysis",
        "ablation": "H3: 2x2x2 mechanism ablation study",
        "propagation_recovery": "Propagation graph recovery validation",
        "security_boundary": "H3: Security boundary erosion testing",
        "mitigation": "Mitigation mechanism effectiveness",
        "simple": "Simple baseline experiment",
    }

    for name, exp_class in EXPERIMENTS.items():
        desc = descriptions.get(name, "No description")
        print(f"  {name:25} - {desc}")

    return 0


def generate_config(args: argparse.Namespace) -> int:
    """Generate experiment configuration."""
    config = ExperimentConfig(
        experiment_name=args.experiment,
        description=f"Configuration for {args.experiment} experiment",
    )

    output_path = Path(args.output)
    config.save(output_path)

    print(f"Configuration saved to: {output_path}")
    return 0


def analyze_results(args: argparse.Namespace) -> int:
    """Analyze experiment results."""
    results_dir = Path(args.results_dir)

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return 1

    # Load summary
    summary_path = results_dir / "summary.json"
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)

        print(f"Experiment: {summary.get('experiment_name', 'unknown')}")
        print(f"ID: {summary.get('experiment_id', 'unknown')}")
        print(f"Duration: {summary.get('duration_seconds', 0):.1f}s")
        print()
        print("Aggregate Metrics:")
        for key, value in summary.get("aggregate_metrics", {}).items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
    else:
        print("No summary.json found")

    return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "run":
        return asyncio.run(run_experiment(args))
    elif args.command == "list":
        return list_experiments()
    elif args.command == "config":
        return generate_config(args)
    elif args.command == "analyze":
        return analyze_results(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
