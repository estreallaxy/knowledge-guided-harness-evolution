import logging
import math
import operator
import os
from codecs import open

import ray
import torch

from src import layers, utils
from src.models import MODELS
from src.training.trainer import train_and_eval_single
from src.utils import cartesian_product, set_seed
from src.validation.hyperparameters_validator import RuleBasedHyperparameterValidator

logger = logging.getLogger(__name__)


def get_worker_class(workers_per_gpu, cpus_per_worker):
    """
    returns a ray.remote-decorated worker function configured to use
    a fraction of a gpu and a user-defined number of cpus
    """
    return ray.remote(num_gpus=1.0 / workers_per_gpu, num_cpus=cpus_per_worker)(worker)


def grid_search(
    model_configurations_path,
    default_configuration,
    dataset,
    verbose,
    gpus=None,
    load_checkpoint=False,
    workers_per_gpu=1,
    cpus_per_worker=1,
    debug=False,
):
    """
    Perform a grid search over hyperparameter configurations using Ray.

    :param model_configurations_path: Path to the model configuration file.
    :param default_configuration: Default configuration dictionary of the dataset parameters.
    :param dataset: Dataset to use.
    :param verbose: Verbosity level.
    :param gpus: List of GPU IDs to use.
    :param load_checkpoint: Whether to load model checkpoints.
    :param workers_per_gpu: Number of workers to assign per GPU (can be >1).
    :param cpus_per_worker: Number of CPUs to assign per worker.
    :param debug: If True, runs in debug mode without initializing Ray.
    :return: Dictionary of best results per model.
    """

    num_gpus = len(gpus)
    total_workers = num_gpus * workers_per_gpu

    if not ray.is_initialized() and not debug:
        ray.init(
            num_cpus=total_workers * cpus_per_worker,
            num_gpus=num_gpus,
            ignore_reinit_error=True,
        )
        logger.info("Initialized Ray with %d GPU(s).", num_gpus)

    model_configurations = utils.load_config(model_configurations_path)
    model_name = model_configurations["Model"]["name"]
    if model_name not in MODELS:
        raise KeyError(
            f"Unknown model {model_name!r}; available models: {sorted(MODELS)}"
        )

    configurations = filter_configurations(model_configurations)

    total_processes = len(configurations)
    workers_per_gpu = min(
        max(1, math.ceil(total_processes / num_gpus)), workers_per_gpu
    )
    worker_cls = get_worker_class(workers_per_gpu, cpus_per_worker)

    futures = []
    seen_models = set()

    logger.info("Total configurations to evaluate: %d", len(configurations))

    for i, configuration in enumerate(configurations):
        model_name = configuration["Model"]["name"]
        seen_models.add(model_name)
        exists = utils.check_run_exists(
            model_name=model_name,
            dataset=dataset,
            combination_trial=i,
            configuration=configuration,
        )
        if exists:
            logger.info("[SKIP] %s trial %d already exists", model_name, i)
        elif debug:
            # Debug mode: no Ray, run the configurations sequentially on CPU.
            worker(
                i,
                configuration,
                default_configuration,
                dataset,
                verbose,
                load_checkpoint,
                device=torch.device("cpu"),
            )
        else:
            futures.append(
                worker_cls.remote(
                    i,
                    configuration,
                    default_configuration,
                    dataset,
                    verbose,
                    load_checkpoint,
                )
            )

    if not debug:
        _ = ray.get(futures)

    results = {}
    for _model_name in seen_models:
        results[_model_name] = []
        model_dir = utils.get_run_dir(_model_name, dataset)
        if not os.path.isdir(model_dir):
            logger.warning("No results directory for %s at %s", _model_name, model_dir)
            continue
        for run_idx_path in os.listdir(model_dir):
            run_dir = os.path.join(model_dir, run_idx_path)
            if not os.path.isdir(run_dir):
                continue

            # check if the run directory contains scores.csv and hyperparameters.json
            scores_path = os.path.join(run_dir, "scores.csv")
            hyper_path = os.path.join(run_dir, "hyperparameters.json")

            if os.path.isfile(scores_path) and os.path.isfile(hyper_path):
                try:
                    scores = utils.load_scores_csv(os.path.join(run_dir, "scores.csv"))
                    hyperparameters = utils.read_json(hyper_path)
                    results[_model_name].append(
                        {
                            "combination_trial": int(run_idx_path.split("_")[-1]),
                            "scores": scores,
                            "hyperparameters": hyperparameters,
                        }
                    )
                except Exception as e:
                    logger.warning("Skipping malformed result in %s: %s", run_dir, e)
            else:
                logger.warning(
                    "Skipping results at %s since a file is missing", scores_path
                )

    monitor_metric = configurations[0]["Validation"]["monitor"]
    search_operator = (
        operator.gt if monitor_metric in layers.ASCENDING_SCORES else operator.lt
    )

    best_results = {}
    best_scores = {}

    for _model_name, result_list in results.items():
        best_scores[_model_name] = (
            float("inf") if search_operator == operator.lt else float("-inf")
        )
        # [1] means validation
        for res in result_list:
            if "scores" not in res or monitor_metric not in res["scores"]:
                continue
            score = res["scores"][monitor_metric][1]
            if search_operator(score, best_scores[_model_name]):
                best_scores[_model_name] = score
                best_results[_model_name] = res

        save_file = utils.create_experiment_file(
            model_name=_model_name,
            dataset=dataset,
            kind="best_run",
            context="tuning",
            combination_trial=None,
        )
        with open(save_file, "w") as f:
            if _model_name in seen_models and _model_name not in best_results:
                f.write("gradient explosion")
            else:
                f.write(str(best_results[_model_name]["combination_trial"]))

    return best_results


def worker(
    combination_trial,
    model_configuration,
    default_configuration,
    dataset,
    verbose,
    load_checkpoint,
    device=None,
):
    """
    Train and evaluate a single grid-search configuration.

    The batch size configured in the hyperparameters is authoritative and is
    used as-is. There is deliberately no out-of-memory fallback that halves the
    batch size and retries, because changing the batch size would alter results.

    :param combination_trial: The combination trial number.
    :param model_configuration: The model configuration dictionary.
    :param default_configuration: The default configuration dictionary.
    :param dataset: The dataset to use for training and evaluation.
    :param verbose: Verbosity level.
    :param load_checkpoint: Whether to load a checkpoint or not.
    :param device: Device to train on; defaults to the Ray worker's GPU.

    :return: The result of the training and evaluation, or None on failure.
    """
    batch_size = default_configuration["batch_size"]
    if model_configuration.get("Override", {}).get("batch_size", None) is not None:
        batch_size = model_configuration["Override"]["batch_size"]

    if device is None:
        device = torch.cuda.current_device()

    set_seed(default_configuration["seed"])
    try:
        if batch_size == -1:
            return train_and_eval_single(
                model_configuration,
                default_configuration,
                dataset,
                verbose=verbose,
                load_checkpoint=load_checkpoint,
                context="tuning",
                device=device,
                combination_trial=combination_trial,
            )

        if "Override" not in model_configuration:
            model_configuration["Override"] = {}
        model_configuration["Override"]["batch_size"] = batch_size
        model_configuration["Override"]["seed"] = default_configuration["seed"]
        res = train_and_eval_single(
            model_configuration,
            default_configuration,
            dataset,
            verbose=verbose,
            load_checkpoint=load_checkpoint,
            context="tuning",
            device=device,
            combination_trial=combination_trial,
        )
        torch.cuda.empty_cache()
        return res
    except Exception as e:
        logger.error(
            "Exception for model %s: %s", model_configuration["Model"]["name"], e
        )
        return None


def filter_configurations(model_configurations):
    model_name = model_configurations["Model"]["name"]
    # model_cls = MODELS[model_name]
    validator = RuleBasedHyperparameterValidator(model_name)
    all_confs = cartesian_product(model_configurations)
    all_confs = validator.filter_configs(all_confs)
    # return filter_default_combinations(model_cls, all_confs)
    return all_confs
