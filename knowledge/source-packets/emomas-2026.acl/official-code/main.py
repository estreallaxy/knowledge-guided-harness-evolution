#!/usr/bin/env python3
"""
Deprecated legacy entry point. Use experiments/run_all_datasets.py instead.

Example:
    python experiments/run_all_datasets.py --model_type bayesian \
        --dataset_type debt --iterations 5 --scenarios 5
"""

import sys


def main() -> int:
    print(
        "[main.py] This script is deprecated.\n"
        "Use: python experiments/run_all_datasets.py --model_type "
        "<bayesian|gpt|vanilla|prompt|rl_agents|gametheory|coherence> "
        "--dataset_type <debt|disaster|student|medical|all>",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
