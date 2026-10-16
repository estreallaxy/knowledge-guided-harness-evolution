"""Thin wrapper around experiments/lib/policy.py.

Usage:
    pixi run python -m experiments.scripts.eval_aspec --dataset MATH --split train
    pixi run python -m experiments.scripts.eval_aspec --dataset HumanEval --split test
    pixi run python -m experiments.scripts.eval_aspec --dataset SciCode --train_rounds 3
"""

from experiments.lib.policy import main

if __name__ == "__main__":
    main()
