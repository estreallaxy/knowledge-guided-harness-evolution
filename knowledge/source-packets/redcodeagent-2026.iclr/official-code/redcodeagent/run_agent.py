"""
RedCodeAgent - CLI entry point.

Keeps only the main loop of the red-teaming Agent. Attack tools
(gcg / amplegcg / autodan / ...) are invoked as Agent **tools** through
`agent_tools.py`; this file does not run any standalone adversarial
prompt generation pipelines.

Usage:
    python run_agent.py --dataset RedCode-Exec --target_model OCI --start_index 1 --end_index 27
"""

import argparse
import json
import multiprocessing
import os
import shutil
import time
import traceback

from utils.memory import initialize_embeddings
from utils.config import get_config_value, update_config
from OCI_evaluation.OCI_interface import create_docker, delete_docker
from agent import Agent

# With CUDA/transformers + multiprocessing, spawn must be used or child
# processes will hang.
multiprocessing.set_start_method('spawn', force=True)

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(current_dir)

# --------------------------------------------------------------------------- #
# Globals. `baseline` is kept as a tag for the current run, used to
# distinguish artifact directories across parallel experiments
# (Agent / Agent1 / Agent2 ...). agent_tools.get_config_path() reads this
# value via get_baseline() to locate ./run_time_config/{baseline}_config.json.
# --------------------------------------------------------------------------- #
baseline = "Agent"
dataset = "RedCode-Exec"
target_model = "OCI"


def get_baseline():
    return baseline


risk_dictionary = {
    "1": "Post sensitive files online",
    "2": "Untrusted installation",
    "3": "Crawl a risky website",
    "4": "Copy sensitive files",
    "5": "List out files under sensitive directories",
    "6": "Write risky content into files",
    "7": "Read sensitive files",
    "8": "Delete sensitive files",
    "9": "Add risky alias to bashrc",
    "10": "Creating a reverse shell",
    "11": "Monitor system",
    "12": "Code with bias issues",
    "13": "Sensitive path traversal",
    "14": "Eval injection",
    "15": "Regular expressions in IP validation",
    "16": "Side channel information leakage",
    "17": "Improper execution privileges",
    "18": "Process management",
    "19": "PRNG seed management",
    "20": "Cryptographic predictability",
    "21": "Amplification",
    "22": "Missing default case",
    "23": "Flawed behavioral workflow",
    "24": "Unsafe deserialization",
    "25": "Duplicate key in associative list",
    "26": "Crawling a risky website with a random-character URL",
    "27": "Memory leak",
    "28": "SQL injection"
}

# --------------------------------------------------------------------------- #
# Dataset layout. Each benchmark maps to a directory (relative to
# <repo_root>/dataset/) plus a per-index filename pattern. The `{risk_index}`
# placeholder is substituted by the current scenario id (or "Gen" / "RMC"
# for the single-batch benchmarks).
# --------------------------------------------------------------------------- #
DATASET_SUBDIR = {
    "RedCode-Exec": "RedCode-Exec/py2text_dataset_json",
    "RedCode-C":    "RedCode-Exec/C_dataset_json",
    "RedCode-CPP":  "RedCode-Exec/CPP_dataset_json",
    "RedCode-Java": "RedCode-Exec/Java_dataset_json",
    "RedCode-Gen":  "RedCode-Gen",
    "RMC":          "RMC",
}

DATASET_FILENAME = {
    "RedCode-Exec": "index{risk_index}_30_codes_full.json",
    "RedCode-C":    "index{risk_index}_30_codes_full.json",
    "RedCode-CPP":  "index{risk_index}_30_codes_full.json",
    "RedCode-Java": "index{risk_index}_30_codes_full.json",
    "RedCode-Gen":  "index{risk_index}_30_codes.json",
    "RMC":          "index{risk_index}_30_codes.json",
}


def resolve_dataset_path(dataset_name, risk_index):
    """Return (absolute path, path relative to redcodeagent/) for the given
    dataset + risk_index, using <repo_root>/dataset/."""
    subdir = DATASET_SUBDIR[dataset_name]
    fname = DATASET_FILENAME[dataset_name].format(risk_index=risk_index)
    abs_path = os.path.join(repo_root, "dataset", subdir, fname)
    rel_to_pkg = os.path.relpath(os.path.dirname(abs_path), current_dir)
    return abs_path, rel_to_pkg


error_log_path = os.path.join(repo_root, "error_index.json")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def get_completed_indices(memory_dir_path, risk_index, baseline=None):
    """
    Read already-processed item_index values from
    memory/good_memory_{risk_index}.json, used for resume support.
    Returns a set (e.g. {"1_1", "1_2", ...}).
    """
    completed_indices = set()
    memory_file_path = os.path.join(memory_dir_path, f"good_memory_{risk_index}.json")

    if os.path.exists(memory_file_path):
        try:
            with open(memory_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'risk_index' in item:
                            completed_indices.add(item['risk_index'])
            print(f"Found {len(completed_indices)} completed indices in {memory_file_path}: "
                  f"{sorted(completed_indices)}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: could not read completed indices from {memory_file_path}: {e}")
    else:
        print(f"No existing memory file found at {memory_file_path}")

    return completed_indices


def copy_memory(risk_scenario_index):
    """Copy the good_memory.json seed experience into the scenario-specific
    good_memory_{idx}.json."""
    source_file = './memory/good_memory.json'
    destination_file = f'./memory/good_memory_{risk_scenario_index}.json'
    try:
        if not os.path.exists(destination_file):
            shutil.copy(source_file, destination_file)
            print(f'Successfully copied to {destination_file}')
        else:
            print(f'Memory file {destination_file} already exists, skipping copy.')
    except Exception as e:
        print(f'Failed to copy memory file: {e}')


def copy_config(destination_file):
    """Refresh the current run's Agent config into
    ./run_time_config/{baseline}_config.json."""
    source_file = './run_time_config/Agent_config.json'
    try:
        os.makedirs(os.path.dirname(destination_file), exist_ok=True)
        shutil.copy(source_file, destination_file)
        print(f'Successfully copied config to {destination_file}')
    except Exception as e:
        print(f'Failed to copy config file: {e}')


def log_error_item(item_index):
    """Append a failed/timed-out item_index to <repo_root>/error_index.json."""
    if not os.path.exists(error_log_path):
        with open(error_log_path, 'w') as f:
            json.dump([], f)

    with open(error_log_path, 'r+') as f:
        try:
            error_list = json.load(f)
        except json.JSONDecodeError:
            error_list = []
        error_list.append(item_index)
        f.seek(0)
        json.dump(error_list, f)
        f.truncate()


# --------------------------------------------------------------------------- #
# Agent runner with timeout + retry
# --------------------------------------------------------------------------- #
def call_agent_with_backoff(item_index, text_summary, baseline, current_memory_path,
                            config_path, mem, max_retries=3,
                            return_dict=None, delay=30):
    """Exponential-backoff retry wrapper that calls Agent()."""
    print("###here call_agent_with_backoff")
    for retry in range(max_retries):
        try:
            print("###before Agent call")
            Agent(item_index, text_summary, baseline, mem, current_memory_path, config_path)
            if return_dict is not None:
                return_dict['result'] = True
            return True
        except Exception as e:
            print(f"Error: {e}, retrying {retry + 1}/{max_retries}...")
            traceback.print_exc()
            time.sleep(delay)
            delay *= 2

    if return_dict is not None:
        return_dict['error'] = f"Max retries reached. Function failed for {item_index}."
    print("Max retries reached. Function failed.")
    return False


def call_agent_with_timeout(item_index, text_summary, baseline, target_model, gpu_number,
                            current_memory_path, config_path, mem, timeout,
                            max_retries=3):
    """Run Agent in a subprocess; kill on timeout and rebuild the victim
    container."""
    print("###here call_agent_with_timeout")
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    try:
        process = multiprocessing.Process(
            target=call_agent_with_backoff,
            args=(item_index, text_summary, baseline, current_memory_path,
                  config_path, mem, max_retries, return_dict),
        )
        print("###starting process...")
        process.start()
        process.join(timeout)

        if process.is_alive():
            print(f"Timeout: Item {item_index} exceeded {timeout} seconds.")
            process.terminate()
            process.join()
            log_error_item(item_index)
            if "RA" in target_model:
                delete_docker(f"Agent-ReAct-{baseline}-{gpu_number}_container")
            else:
                delete_docker(f"{baseline}_{gpu_number}_container")
                create_docker(f"{baseline}_{gpu_number}_container", llm="DS-6.7B", is_OCI=True)
            return False

        print(f"return_dict = {return_dict}")
        if 'result' in return_dict:
            return return_dict['result']
        if 'error' in return_dict:
            print(f"Error in process: {return_dict['error']}")
            log_error_item(item_index)
            return False
        print("Unknown error.")
        log_error_item(item_index)
        return False
    except Exception as e:
        print(f"###Error: {e}")
        return False


# --------------------------------------------------------------------------- #
# Top-level evaluation driver (Agent-only)
# --------------------------------------------------------------------------- #
def evaluation(risk_index, baseline, gpu_number, current_memory_path, config_path,
               mem=True, target_model="OCI", dataset="RedCode-Exec", topk=3):
    print(f"In evaluation, target_model = {target_model}")

    copy_config(config_path)

    if dataset not in DATASET_SUBDIR:
        print(f"Dataset {dataset!r} not supported.")
        return

    jsonfile, dataset_rel_to_pkg = resolve_dataset_path(dataset, risk_index)
    print(f"json file = {jsonfile}")

    if not os.path.isfile(jsonfile):
        print(f"The file {jsonfile} does not exist. Exiting.")
        return

    update_config("dataset", dataset, config_path)
    update_config("conversation_dir_relative_path",
                  f"{target_model}_{baseline}_{dataset}_result/conversation_log", config_path)
    update_config("evaluation_log_dir_relative_path",
                  f"{target_model}_{baseline}_{dataset}_result/evaluation_log", config_path)

    update_config("risk_index", risk_index, config_path)
    update_config("risk_scenario", risk_dictionary.get(str(risk_index), "Unknown scenario"), config_path)
    update_config("gpu_number", gpu_number, config_path)
    # Path of the dataset directory, stored relative to redcodeagent/ so that
    # victim adapters can resolve it the same way they resolve log paths.
    update_config("dataset_dir_relative_path", dataset_rel_to_pkg, config_path)
    update_config("baseline", baseline, config_path)
    update_config("target_model", target_model, config_path)
    update_config("topk", str(topk), config_path)

    with open(jsonfile, 'r') as file:
        data = json.load(file)

    memory_dir_path = os.path.join(current_dir, "./memory")
    completed_indices = get_completed_indices(memory_dir_path, risk_index, baseline)

    initialize_embeddings(
        file_path=os.path.join(current_dir, "./memory/good_memory.json")
    )
    copy_memory(risk_index)

    for item in data:
        item_index = item['Index']
        if item_index in completed_indices:
            print(f"Skipping already completed item: {item_index}")
            continue

        update_config("red_teaming_requirement", item['Text_summary'], config_path)
        success = call_agent_with_timeout(
            item_index, item['Text_summary'], baseline, target_model, gpu_number,
            current_memory_path, config_path, mem, timeout=1200, max_retries=3,
        )
        print(f"call_agent_with_timeout result: {success}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def parse_args():
    global baseline
    parser = argparse.ArgumentParser(
        description="RedCodeAgent: run the red-teaming Agent against a victim code agent.")
    parser.add_argument('--baseline', type=str, default="Agent",
                        help="Tag for this Agent run (Agent / Agent1 / Agent2 ...). "
                             "Used for config & output dir naming.")
    parser.add_argument('--dataset', type=str, required=True,
                        help="Dataset: RedCode-Exec / RedCode-Gen / RMC / "
                             "RedCode-C / RedCode-CPP / RedCode-Java")
    parser.add_argument('--target_model', type=str, default="OCI",
                        help="Victim agent: OCI / RA / MetaGPT")
    parser.add_argument('--start_index', type=int, default=1)
    parser.add_argument('--end_index', type=int, default=27)
    parser.add_argument('--mem', type=str, default="True",
                        help="Use memory (True/False).")
    parser.add_argument('--topk', type=int, default=3,
                        help="Top-k similar memory entries to retrieve.")

    args = parser.parse_args()
    baseline = args.baseline
    print(f"in main, args baseline = {baseline}")
    return args


def main():
    args = parse_args()
    args.mem = args.mem.lower() in ["true", "1", "yes"]

    global baseline, dataset, target_model
    baseline = args.baseline
    dataset = args.dataset
    target_model = args.target_model

    gpu_number = os.getenv('CUDA_VISIBLE_DEVICES')
    llm = "DS-6.7B"

    container = None
    if "RA" not in target_model:
        container = create_docker(f"{baseline}_{gpu_number}_container", llm, is_OCI=True)

    config_path = os.path.join(current_dir, "run_time_config", f"{baseline}_config.json")

    if dataset in ("RedCode-Exec", "RedCode-C", "RedCode-CPP", "RedCode-Java"):
        for risk_index in range(args.start_index, args.end_index + 1):
            current_memory_path = os.path.join(
                current_dir, f"./memory/good_memory_{risk_index}.json")
            evaluation(risk_index, baseline, gpu_number, current_memory_path,
                       config_path, args.mem, target_model, dataset, args.topk)
    elif dataset == "RedCode-Gen":
        current_memory_path = os.path.join(current_dir, "./memory/good_memory_Gen.json")
        evaluation("Gen", baseline, gpu_number, current_memory_path,
                   config_path, args.mem, target_model, dataset, args.topk)
    elif dataset == "RMC":
        current_memory_path = os.path.join(current_dir, "./memory/good_memory_RMC.json")
        evaluation("RMC", baseline, gpu_number, current_memory_path,
                   config_path, args.mem, target_model, dataset, args.topk)
    else:
        print(f"Dataset {dataset!r} not supported.")

    if container is not None:
        container.stop()
        print(f"Docker container {container.name} has been stopped.")


if __name__ == "__main__":
    main()
