#!/usr/bin/env python3
"""
Main script to run all PSE experiments.

Usage:
    python run_experiments.py --all
    python run_experiments.py --experiment behavioral_drift
    python run_experiments.py --experiment ablation --num-tasks 50 --num-runs 10
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

# Add the harness to path
sys.path.insert(0, str(Path(__file__).parent / "python_harness" / "src"))

from pse_harness.core import ExperimentConfig, PseConfig
from pse_harness.experiments import (
    BehavioralDriftExperiment,
    ObservabilityExperiment,
    AblationExperiment,
    PropagationRecoveryExperiment,
    SecurityBoundaryExperiment,
    MitigationExperiment,
)


EXPERIMENTS = {
    "behavioral_drift": BehavioralDriftExperiment,
    "observability": ObservabilityExperiment,
    "ablation": AblationExperiment,
    "propagation_recovery": PropagationRecoveryExperiment,
    "security_boundary": SecurityBoundaryExperiment,
    "mitigation": MitigationExperiment,
}


async def run_single_experiment(
    experiment_name: str,
    config: ExperimentConfig,
    api_key: str,
) -> dict:
    """Run a single experiment and return results."""
    print(f"\n{'='*60}")
    print(f"Running: {experiment_name}")
    print(f"{'='*60}")

    experiment_class = EXPERIMENTS[experiment_name]
    config.experiment_name = experiment_name

    runner = experiment_class(config, api_key=api_key)
    result = await runner.run()

    # Save results
    output_path = Path(config.output_dir) / experiment_name / config.experiment_id
    result.save(output_path)

    print(f"\nCompleted: {experiment_name}")
    print(f"  Success rate: {result.aggregate_metrics.get('success_rate', 0):.2%}")
    print(f"  Duration: {(result.end_time - result.start_time).total_seconds():.1f}s")
    print(f"  Results: {output_path}")

    return {
        "experiment": experiment_name,
        "success_rate": result.aggregate_metrics.get("success_rate", 0),
        "duration_seconds": (result.end_time - result.start_time).total_seconds(),
        "num_runs": len(result.runs),
        "output_path": str(output_path),
    }


async def run_all_experiments(config: ExperimentConfig, api_key: str) -> list[dict]:
    """Run all experiments sequentially."""
    results = []

    for experiment_name in EXPERIMENTS:
        try:
            result = await run_single_experiment(experiment_name, config, api_key)
            results.append(result)
        except Exception as e:
            print(f"Error in {experiment_name}: {e}")
            results.append({
                "experiment": experiment_name,
                "error": str(e),
            })

    return results


def main():
    parser = argparse.ArgumentParser(description="Run PSE experiments")
    parser.add_argument("--all", action="store_true", help="Run all experiments")
    parser.add_argument("--experiment", "-e", type=str, choices=list(EXPERIMENTS.keys()),
                        help="Run specific experiment")
    parser.add_argument("--model", "-m", type=str, default="gpt-4o-mini",
                        help="Model to use")
    parser.add_argument("--num-tasks", "-n", type=int, default=100,
                        help="Number of tasks")
    parser.add_argument("--num-runs", "-r", type=int, default=20,
                        help="Number of runs per task")
    parser.add_argument("--task-family", "-t", type=str, default="tool_intensive",
                        choices=["tool_intensive", "long_horizon", "policy_bound"])
    parser.add_argument("--output-dir", "-o", type=str, default="data/results")
    parser.add_argument("--seed", "-s", type=int, default=42)
    parser.add_argument("--api-key", type=str, help="OpenAI API key")

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY or use --api-key")
        sys.exit(1)

    # Create config
    config = ExperimentConfig(
        model_name=args.model,
        num_tasks=args.num_tasks,
        num_runs=args.num_runs,
        task_family=args.task_family,
        output_dir=Path(args.output_dir),
        seed=args.seed,
    )

    print("PSE Experiment Runner")
    print("=" * 60)
    print(f"Model: {args.model}")
    print(f"Tasks: {args.num_tasks}")
    print(f"Runs per task: {args.num_runs}")
    print(f"Task family: {args.task_family}")
    print(f"Output: {args.output_dir}")

    start_time = datetime.now()

    if args.all:
        results = asyncio.run(run_all_experiments(config, api_key))
    elif args.experiment:
        results = [asyncio.run(run_single_experiment(args.experiment, config, api_key))]
    else:
        parser.print_help()
        sys.exit(0)

    end_time = datetime.now()

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    print(f"Total time: {(end_time - start_time).total_seconds():.1f}s")
    print()

    for result in results:
        if "error" in result:
            print(f"  {result['experiment']}: ERROR - {result['error']}")
        else:
            print(f"  {result['experiment']}: {result['success_rate']:.2%} success "
                  f"({result['num_runs']} runs, {result['duration_seconds']:.1f}s)")

    # Save summary
    summary_path = Path(args.output_dir) / "experiment_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "config": config.model_dump(mode="json"),
            "results": results,
            "total_duration_seconds": (end_time - start_time).total_seconds(),
        }, f, indent=2, default=str)

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
