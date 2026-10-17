"""Model assessment: retrain the selected configuration N times and aggregate.

`main.py` performs model *selection* (the hyperparameter grid search) and writes
the winning trial index to ``best_run.txt``. This script performs model
*assessment*: it reloads that configuration and retrains it ``N_REINIT`` times
from different weight initializations, then reports the mean and standard
deviation of the test metrics — the numbers reported in the paper's tables.

    uv run python run_reinit.py --model LAMP --task node_prediction --dataset ChickenPox

Runs are written to ``experiments/reinit/<task>/<dataset>/<settings>/<model>/run_<i>/``
and the aggregate to ``scores.csv`` in the model directory.
"""

import argparse
import json
import logging
import multiprocessing
import os
import traceback

import pandas as pd
import ray
import torch

import config.paths
from src import utils
from src.training.trainer import train_and_eval_single
from src.utils import prepare_dataset, set_seed

logger = logging.getLogger(__name__)


def parse_args():
    """Parses command-line arguments for the model-assessment runs."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--model",
        default="LAMP",
        type=str,
        help="Name of the model to assess (must match the model selection run)",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Name of the task: one of node_prediction, link_prediction, leaf_counting",
    )
    parser.add_argument(
        "--dataset",
        required=True,
        type=str,
        help="Name of the dataset to use",
    )
    parser.add_argument(
        "--runs",
        default=None,
        type=int,
        help="Number of reinitializations (defaults to the dataset's N_REINIT)",
    )
    parser.add_argument(
        "--trial",
        default=None,
        type=int,
        help="Grid-search trial to assess (defaults to the one in best_run.txt)",
    )
    parser.add_argument(
        "--load-checkpoint",
        action="store_true",
        help="If set, reuses existing checkpoints to skip runs that already completed",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output during training and evaluation",
    )
    parser.add_argument(
        "--workers",
        default=1,
        type=int,
        help="Number of parallel workers to use per GPU",
    )
    parser.add_argument(
        "--cpus-per-worker",
        default=1,
        type=int,
        help="Number of CPUs to assign per worker",
    )
    parser.add_argument(
        "--gpus",
        default=[0, 1, 2, 3],
        nargs="+",
        type=int,
        help="List of GPU IDs to use for training (default: [0, 1, 2, 3])",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode, skipping Ray initialization and using CPU only",
    )
    parser.add_argument(
        "--wandb",
        action="store_true",
        help="Log metrics to Weights & Biases (otherwise wandb is disabled)",
    )
    return parser.parse_args()


def load_selected_configuration(model_name, dataset, trial=None):
    """Loads the configuration chosen by model selection.

    :param model_name: The name of the model.
    :param dataset: The dataset the selection was run on.
    :param trial: Explicit trial index; when None it is read from best_run.txt.
    :return: A ``(trial_index, configuration)`` pair.
    """
    model_dir = utils.get_run_dir(model_name, dataset, run_type="tuning")

    if trial is None:
        best_run_path = os.path.join(model_dir, "best_run.txt")
        if not os.path.isfile(best_run_path):
            raise FileNotFoundError(
                f"No best_run.txt at {best_run_path}. Run main.py --model "
                f"{model_name} first, or pass --trial explicitly."
            )
        with open(best_run_path) as f:
            content = f.read().strip()
        if not content.isdigit():
            raise ValueError(
                f"best_run.txt at {best_run_path} contains {content!r} instead of a "
                "trial index; model selection found no usable run."
            )
        trial = int(content)

    hyperparameters_path = os.path.join(
        model_dir, f"hyperparameters_{trial}", "hyperparameters.json"
    )
    if not os.path.isfile(hyperparameters_path):
        raise FileNotFoundError(f"No hyperparameters at {hyperparameters_path}")

    with open(hyperparameters_path) as f:
        return trial, json.load(f)


def worker(run_index, configuration, default_configuration, dataset, seed, verbose,
           load_checkpoint, device=None):
    """Trains and evaluates one reinitialization of the selected configuration.

    Only the seed changes across runs: the hyperparameters, the data splits and
    the training procedure are identical to the selected model-selection run.

    :param run_index: Index of this reinitialization.
    :param configuration: The selected model configuration dictionary.
    :param default_configuration: The default configuration dictionary.
    :param dataset: The dataset to use for training and evaluation.
    :param seed: The random seed for this run.
    :param verbose: Verbosity level.
    :param load_checkpoint: Whether to load a checkpoint or not.
    :param device: Device to train on; defaults to the Ray worker's GPU.

    :return: The result of the training and evaluation, or None on failure.
    """
    if device is None:
        device = torch.cuda.current_device()

    set_seed(seed)
    try:
        if "Override" not in configuration:
            configuration["Override"] = {}
        configuration["Override"]["seed"] = seed
        res = train_and_eval_single(
            configuration,
            default_configuration,
            dataset,
            verbose=verbose,
            load_checkpoint=load_checkpoint,
            context="reinit",
            device=device,
            combination_trial=run_index,
        )
        torch.cuda.empty_cache()
        return res
    except Exception as e:
        logger.error("Exception on run %d: %s", run_index, e)
        return None


def aggregate(model_name, dataset, n_runs):
    """Aggregates the per-run test scores into a mean/std summary.

    :param model_name: The name of the model.
    :param dataset: The dataset the runs were performed on.
    :param n_runs: Number of reinitializations that were launched.
    :return: The aggregate DataFrame, or None when no run produced scores.
    """
    model_dir = utils.get_run_dir(model_name, dataset, run_type="reinit")

    rows = []
    for i in range(n_runs):
        scores_path = os.path.join(model_dir, f"run_{i}", "scores.csv")
        if not os.path.isfile(scores_path):
            logger.warning("Missing scores for run %d at %s", i, scores_path)
            continue
        scores = pd.read_csv(scores_path)
        rows.append(scores.assign(run=i))

    if not rows:
        logger.error("No run produced scores; nothing to aggregate.")
        return None

    all_scores = pd.concat(rows, ignore_index=True)
    metrics = [c for c in all_scores.columns if c not in ("Set", "run")]
    summary = all_scores.groupby("Set")[metrics].agg(["mean", "std"])

    summary_path = os.path.join(model_dir, "scores.csv")
    os.makedirs(model_dir, exist_ok=True)
    summary.to_csv(summary_path)
    logger.info("Wrote aggregate over %d runs to %s", len(rows), summary_path)
    return summary


def run_assessment(args, dataset_configurations):
    """Retrains the selected configuration N times for each dataset setting."""
    multiprocessing.set_start_method("spawn", force=True)

    num_gpus = len(args.gpus)
    for dataset_config in utils.cartesian_product(dataset_configurations):
        try:
            torch.cuda.empty_cache()
            dataset = prepare_dataset(args.task, dataset_config)
            default_config = dataset_config["default"]
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(g) for g in args.gpus)
            logger.info("Assessing on dataset %s", dataset)

            trial, configuration = load_selected_configuration(
                args.model, dataset, args.trial
            )
            n_runs = args.runs or default_config["N_REINIT"]
            base_seed = default_config["seed"]
            logger.info(
                "Selected trial %d; running %d reinitializations", trial, n_runs
            )

            if not ray.is_initialized() and not args.debug:
                ray.init(
                    num_cpus=num_gpus * args.workers * args.cpus_per_worker,
                    num_gpus=num_gpus,
                    ignore_reinit_error=True,
                )
                logger.info("Initialized Ray with %d GPU(s).", num_gpus)

            workers_per_gpu = min(max(1, -(-n_runs // num_gpus)), args.workers)
            worker_cls = ray.remote(
                num_gpus=1.0 / workers_per_gpu, num_cpus=args.cpus_per_worker
            )(worker)

            futures = []
            for i in range(n_runs):
                # Each reinitialization differs only in its seed.
                seed = base_seed + i
                if args.debug:
                    worker(
                        i,
                        configuration,
                        default_config,
                        dataset,
                        seed,
                        args.verbose,
                        args.load_checkpoint,
                        device=torch.device("cpu"),
                    )
                else:
                    futures.append(
                        worker_cls.remote(
                            i,
                            configuration,
                            default_config,
                            dataset,
                            seed,
                            args.verbose,
                            args.load_checkpoint,
                        )
                    )

            if not args.debug:
                _ = ray.get(futures)

            summary = aggregate(args.model, dataset, n_runs)
            if summary is not None:
                logger.info("Aggregate test scores:\n%s", summary.loc["Test"])
        except Exception:
            traceback.print_exc()


def main():
    """Main entry point: reload the selected configuration and reassess it."""
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if not args.wandb:
        # Disable Weights & Biases unless explicitly requested.
        os.environ.setdefault("WANDB_MODE", "disabled")
    logger.info("Running model assessment with args: %s", args)

    dataset_conf_path = os.path.join(
        config.paths.DATASET_SPECIFIC_HYPERPARAMETERS_PATH,
        args.task,
        args.dataset + ".yaml",
    )
    dataset_configurations = utils.load_config(dataset_conf_path)
    run_assessment(args, dataset_configurations)


if __name__ == "__main__":
    main()
