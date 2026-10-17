import inspect
import os
from datetime import datetime
import random

import numpy as np
import pandas as pd
import json
import torch
import psutil

import config
import src.layers
from config import paths
from typing import Any
import yaml
from itertools import product

from src.datasets.dataset import MultipleSequenceDataset
from src.datasets.utils import get_dataset


def optimizer_to(optim, device):
    """
    Moves the optimizer state to the specified device.
    Code from https://discuss.pytorch.org/t/moving-optimizer-from-cpu-to-gpu/96068/3

    :param optim: The optimizer to move.
    :param device: The device to move the optimizer to (e.g., 'cuda' or 'cpu').
    """
    for param in optim.state.values():
        # Not sure, there are any global tensors in the state dict
        if isinstance(param, torch.Tensor):
            param.data = param.data.to(device)
            if param._grad is not None:
                param._grad.data = param._grad.data.to(device)
        elif isinstance(param, dict):
            for subparam in param.values():
                if isinstance(subparam, torch.Tensor):
                    subparam.data = subparam.data.to(device)
                    if subparam._grad is not None:
                        subparam._grad.data = subparam._grad.data.to(device)


def log_resources_usage(
    model_name, dataset, context="single_run", combination_trial=None
):
    """
    Logs the CPU and memory usage of the current process.

    :param model_name: The name of the model.
    :param dataset: The dataset used.
    :param context: The context of the experiment: one among 'tuning', 'single_run', 'reinit'
    :param combination_trial: The combination trial of the experiment, if None it is a single run, else an integer
    """
    cpu = psutil.cpu_percent(interval=None, percpu=True)
    mem = psutil.virtual_memory()
    mem = {
        "total": f"{round(mem.total / 1e9, 1)}GB",
        "used": f"{round(mem.used / 1e9, 1)}GB",
        "available": f"{round(mem.available / 1e9, 1)}GB",
        "percent": f"{mem.percent}%",
    }
    filename = create_experiment_file(
        model_name,
        dataset,
        "log",
        context=context,
        combination_trial=combination_trial,
    )
    with open(filename, "w") as f:
        print(str(datetime.now()), file=f, flush=True)
        print("CPU usage:", file=f, flush=True)
        for i, p in enumerate(cpu):
            print(f"{p}%", end=" ", file=f, flush=True)
            if i % 10 == 9:
                print(file=f, flush=True)
        print(file=f, flush=True)
        print(f"RAM usage: {mem}", file=f, flush=True)


@torch.no_grad()
def compute_scores(y_pred, y_true, criterion, metrics):
    """Compute the loss and the requested evaluation metrics."""
    scores = {
        k: func(y_pred, y_true).cpu().item()
        for k, func in src.layers.SCORES.items()
        if k in metrics
    }

    return {"Loss": criterion(y_pred, y_true).cpu().item(), **scores}


def get_run_dir(model_name, dataset, run_type="tuning"):
    assert run_type in ["tuning", "single_run", "reinit"]
    return os.path.join(
        config.paths.EXPERIMENTS_PATH,
        run_type,
        dataset.TASK,
        dataset.name,
        dataset.settings,
        model_name,
    )


def dicts_equal_excluding_keys(d1, d2, exclude_keys):
    def filter_dict(d):
        if not isinstance(d, dict):
            return d
        return {k: filter_dict(v) for k, v in d.items() if k not in exclude_keys}

    return filter_dict(d1) == filter_dict(d2)


def create_experiment_file(
    model_name,
    dataset,
    kind,
    context,
    combination_trial=None,
    seed=None,
    trial_dir=None,
):
    """
    Creates a file path for storing experiment artifacts.

    :param model_name: The name of the model.
    :param dataset: The dataset used.
    :param kind: The type of file to create.
    :param context: The context of the experiment: one among 'tuning', 'single_run', 'reinit'
    :param combination_trial: Optional trial number for hyperparameter tuning.
    :return: The full path to the target file.
    """
    assert context in [
        "single_run",
        "tuning",
        "reinit",
        "ablation",
        "single_reinit",
        "rebuttal",
    ], f"Context {context} is not usable"

    extensions = {
        "checkpoint": ".pt",
        "log": ".txt",
        "scores": ".csv",
        "hyperparameters": ".json",
        "running_time": ".txt",
        "best_run": ".txt",
        "best_seed": ".txt",
        "trainable_parameters": ".txt",
        "ablation_perturbation": ".json",
        "ablation_progression": ".json",
    }

    if kind not in extensions:
        raise ValueError(f"Unknown kind: {kind}")

    filename = kind + extensions[kind]

    if trial_dir is not None:
        os.makedirs(trial_dir, exist_ok=True)
        return os.path.join(trial_dir, filename)

    base_dir = os.path.join(paths.EXPERIMENTS_PATH, context, dataset.TASK, dataset.name)

    parts = [base_dir]

    if dataset.settings is not None:
        parts.append(dataset.settings)

    parts.append(model_name)

    if seed is not None:
        parts.append(f"seed_{seed}")

    if combination_trial is not None:
        if not isinstance(combination_trial, int):
            raise TypeError("combination_trial must be an integer")
        if context in ["tuning", "rebuttal"]:
            parts.append(f"hyperparameters_{combination_trial}")
        elif context == "reinit":
            parts.append(f"run_{combination_trial}")
        elif context == "single_reinit":
            parts.append(f"trial_{combination_trial}")
        else:
            raise ValueError("Combination trial should be None for single run")

    dir_path = os.path.join(*parts)
    os.makedirs(dir_path, exist_ok=True)

    return os.path.join(dir_path, filename)


def save_scores(filename, data):
    """
    Saves the scores into a csv file

    :param filename: The filename at which to save the scores.
    :param data: The data containing the metrics.
    """

    rows = []
    for prefix in ["tr", "vl", "ts"]:
        row = {
            "Set": (
                "Train"
                if prefix == "tr"
                else "Validation"
                if prefix == "vl"
                else "Test"
            ),
            "Loss": data[f"{prefix}_loss"],
        }
        filtered_scores = {
            key: value for key, value in data[f"{prefix}_other_scores"].items()
        }
        row.update(filtered_scores)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)


def save_running_time(filename, total_time, per_epoch):
    """
    Saves the running time of a run, with milliseconds precision.

    :param filename: The filename at which to save the scores.
    :param total_time: The total time taken for the run.
    :param per_epoch: The time taken per epoch.
    """
    with open(filename, "w") as f:
        print(f"Total: {total_time.total_seconds():.3f} seconds", file=f)
        print(f"Per epoch: {per_epoch.total_seconds():.3f} seconds", file=f)


def save_hyperparameters(filename, hyperparameters):
    """
    Saves the hyperparameters of a run.

    :param filename: The filename at which to save the scores.
    :param hyperparameters: A dictionary containing the hyperparameters.
    """
    with open(filename, "w") as f:
        json.dump(hyperparameters, f, indent=4)


def save_n_trainable_parameters(filename, data):
    """
    Saves the number of trainable parameters to a file.

    :param filename: The filename at which to save the scores.
    :param data: The data containing the metrics.
    """

    with open(filename, "w") as f:
        print(f"Number of trainable parameters: {data}", file=f)


def save_temperature(filename, temperatures, alphas=None):
    """
    Saves the temperature value to a file.

    :param filename: The filename at which to save the temperature.
    :param temperatures: The temperature value to save.
    :param alphas: The alpha values used in the model.
    """
    with open(filename, "w") as f:
        json.dump({"temperature": temperatures, "alphas": alphas}, f, indent=4)


def cartesian_product(data, common_keys=None):
    """
    Computes the cartesian product of a dictionary of dictionaries/lists,
    while keeping common keys unexpanded. By default, 'default' and 'Normalize'
    are treated as common.

    :param data: input dictionary from YAML
    :param common_keys: list of keys to keep common; defaults to ['default', 'Normalize']
    :return: list of dataset configurations
    """
    if common_keys is None:
        common_keys = ["default", "Normalize"]

    def process_nested_dict(d):
        array_fields = {
            k: v for k, v in d.items() if isinstance(v, list) and k not in common_keys
        }
        nested_fields = {
            k: v for k, v in d.items() if isinstance(v, dict) and k not in common_keys
        }
        non_array_fields = {
            k: v
            for k, v in d.items()
            if k in common_keys or not isinstance(v, (list, dict))
        }

        keys = list(array_fields.keys())
        values_product = product(*array_fields.values()) if keys else [()]
        combinations = [
            {**dict(zip(keys, values)), **non_array_fields} for values in values_product
        ]

        if nested_fields:
            for key, nested_dict in nested_fields.items():
                nested_combinations = process_nested_dict(nested_dict)
                combinations = [
                    {**comb, key: nested_comb}
                    for comb in combinations
                    for nested_comb in nested_combinations
                ]

        return combinations

    return process_nested_dict(data)


def load_config(path: str) -> dict[str, Any]:
    """
    Loads the hyperparameters for a certain model.

    :param path: the path of the yaml file
    :return: the hyperparameters for the given model
    """
    with open(path, "r") as file:
        dictionary = yaml.load(file, Loader=yaml.FullLoader)
    return dictionary


def read_json(file_path):
    """
    Reads a JSON file and returns the content as a dictionary.

    :param file_path: The path to the JSON file.
    :return: The content of the JSON file as a dictionary.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def load_scores_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None


def load_running_time(path):
    try:
        with open(path, "r") as f:
            total = f.readline().strip()
            epoch = f.readline().strip()
            return {"total": total.split(" ")[-2], "epoch": epoch.split(" ")[-2]}
    except Exception:
        return {"total": -1, "epoch": -1}


def check_run_exists(model_name, dataset, combination_trial, configuration):
    path = os.path.join(
        config.paths.EXPERIMENTS_PATH,
        "tuning",
        dataset.TASK,
        dataset.name,
        dataset.settings,
        model_name,
        f"hyperparameters_{combination_trial}",
    )

    hyperparameters_path = os.path.join(path, "hyperparameters.json")
    scores_path = os.path.join(path, "scores.csv")
    hyperparameters = (
        read_json(hyperparameters_path)
        if os.path.isfile(hyperparameters_path)
        else None
    )

    return (
        os.path.isdir(path)
        and os.path.isfile(scores_path)
        and hyperparameters is not None
        and dicts_equal_excluding_keys(
            hyperparameters, configuration, ["name", "Override", "monitor"]
        )
    )


def filter_default_combinations(cls, param_list):
    default_args = get_default_args(cls)
    return [
        {
            **d,
            "Model": {
                k: v
                for k, v in d["Model"].items()
                if k not in default_args or v != default_args[k]
            },
        }
        for d in param_list
    ]


def get_default_args(cls):
    signature = inspect.signature(cls.__init__)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty and k != "self"
    }


def get_best_model_parameters(path):
    """
    Retrieves the best model parameters from all reinitialization runs.
    """
    res = []
    for run_folder in os.listdir(path):
        run_path = os.path.join(path, run_folder)
        if run_folder.startswith("run_") and os.path.isdir(run_path):
            ckpt = torch.load(os.path.join(run_path, "checkpoint.pt"))
            res.append(ckpt)
    return res


def set_seed(seed: int):
    """
    Sets the random seed for Python, NumPy, and PyTorch (CPU + CUDA).
    Ensures reproducibility for a given seed.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def prepare_dataset(task, dataset_config):
    """
    Loads and prepares a dataset with validation and test splits.

    :param task: The task name for which the dataset is to be prepared.
    :param dataset_config: Dictionary describing the task and dataset parameters.

    :return: Prepared dataset with validation and test splits.
    """

    dataset = get_dataset(task, dataset_config)
    # if a single sequence, it is already split in its constructor
    if isinstance(dataset, MultipleSequenceDataset):
        dataset.val_test_split(
            val_split=dataset_config["default"]["val_split"],
            test_split=dataset_config["default"]["test_split"],
            seed=dataset_config["default"]["seed"],
        )
    normalization_config = dataset_config.get("Normalize", None)
    if normalization_config is not None:
        dataset.normalize(normalization_config)
    return dataset
