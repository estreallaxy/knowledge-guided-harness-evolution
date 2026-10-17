import argparse
import logging
import multiprocessing
import os
import traceback

import torch

import config.paths
from src import utils
from src.utils import prepare_dataset
from src.validation.model_selection import grid_search

logger = logging.getLogger(__name__)


def parse_args():
    """
    Parses command-line arguments for the hyperparameter grid search.

    Returns:
        argparse.Namespace: Parsed arguments (model, task, dataset, resources).
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--model",
        default="LAMP",
        type=str,
        help="Name of the model to run (must match a YAML config under the tuning hyperparameters folder)",
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


def run_tuning(args, dataset_configurations):
    """
    Runs the hyperparameter grid search for the chosen model over each dataset
    configuration.

    Args:
        args (argparse.Namespace): Command-line arguments.
        dataset_configurations (list[dict]): Dataset configuration dictionaries.
    """
    multiprocessing.set_start_method("spawn", force=True)
    model_config_path = os.path.join(
        config.paths.TUNING_HYPERPARAMETERS_PATH,
        args.task,
        args.dataset,
        f"{args.model}.yaml",
    )
    for dataset_config in utils.cartesian_product(dataset_configurations):
        try:
            torch.cuda.empty_cache()
            dataset = prepare_dataset(args.task, dataset_config)
            default_config = dataset_config["default"]
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str(gpu) for gpu in args.gpus)
            logger.info("Running on dataset %s", dataset)

            grid_search(
                model_configurations_path=model_config_path,
                default_configuration=default_config,
                dataset=dataset,
                verbose=args.verbose,
                gpus=args.gpus,
                workers_per_gpu=args.workers,
                cpus_per_worker=args.cpus_per_worker,
                load_checkpoint=args.load_checkpoint,
                debug=args.debug,
            )
        except Exception:
            traceback.print_exc()


def main():
    """
    Main entry point: load the dataset configuration and run the grid-search
    reproduction for the selected task/dataset.
    """
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    if not args.wandb:
        # Disable Weights & Biases unless explicitly requested.
        os.environ.setdefault("WANDB_MODE", "disabled")
    logger.info("Running experiments with args: %s", args)

    dataset_conf_path = os.path.join(
        config.paths.DATASET_SPECIFIC_HYPERPARAMETERS_PATH,
        args.task,
        args.dataset + ".yaml",
    )
    dataset_configurations = utils.load_config(dataset_conf_path)
    run_tuning(args, dataset_configurations)


if __name__ == "__main__":
    main()
