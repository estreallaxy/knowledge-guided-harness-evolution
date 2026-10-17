import subprocess
import re
import os
import shutil
from utils.config import get_config_value
from utils.docker_utils import *
from evaluation import evaluation
import json
import shlex

# All run artifacts live under <repo_root>/results/. See OCI_run.py for rationale.
_METAGPT_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_METAGPT_MODULE_DIR, "..", ".."))
base_dir = os.path.join(_METAGPT_MODULE_DIR, "../../results")

# MetaGPT's host-side scratch area for generated projects (the `metagpt` CLI
# writes a sub-project here, which we then `docker cp` into the target).
_WORKSPACE_PATH = os.path.join(_REPO_ROOT, "workspace")


def MetaGPT(index, query, config_file_path, dataset):
    # save to conversation
    baseline = get_config_value("baseline",config_file_path)
    gpu_number = get_config_value("gpu_number",config_file_path)
    conversation_dir_relative_path = get_config_value("conversation_dir_relative_path",config_file_path)
    evaluation_log_dir_relative_path = get_config_value("evaluation_log_dir_relative_path",config_file_path)
    dataset_dir_relative_path = get_config_value("dataset_dir_relative_path", config_file_path)
    conversation_dir_path = os.path.join(base_dir, conversation_dir_relative_path)
    conversation_file_path = os.path.join(conversation_dir_path, f"index{index.split('_')[0]}.json")

    if "Agent" not in baseline and index_already_in_json(conversation_file_path, index):
        print(f"Index {index} already exists in {conversation_file_path}. Skipping...")
        return None

    # Step 0: clear / prepare workspace
    workspace_path = _WORKSPACE_PATH
    os.makedirs(workspace_path, exist_ok=True)

    
    # Step 1: Execute the MetaGPT command
    
    # Now wrap the escaped query in double quotes as required
    modified_query = query.replace("'", "\"")
    
    command = f"metagpt \'{modified_query}\'"
    try:
        all_response = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")
        return None
    # Step 2: Extract content from the response
    pattern = r"\[CONTENT\](.*?)\[/CONTENT\]"  # match what is wrapped in [CONTENT]...[/CONTENT]
    match = re.search(pattern, all_response.stdout, re.DOTALL)

    if match:
        response_str = match.group(1).strip()  # pull out and trim the payload
        print("Extracted content:")
        print(response_str)
    else:
        print("No content found.")
        return None
    
    project_name = re.search(r'"Project Name": "(.*?)"', response_str)
    project_name.group(1) if project_name else None
    file_name = project_name.group(1)
    print(f"file name = {file_name}")
    # response_str = "test"

    # Step 3: Create Docker container
    container_name = f"redcode-metagpt-{baseline}-{gpu_number}"
    create_docker(container_name)

    # Step 4: Find the unique directory in the workspace
    directory_name = file_name  # e.g., game_2048
    proj_path = os.path.join(workspace_path, directory_name)

    # Step 5: Copy workspace to Docker container
    target_path = "/app/"
    # print(f"Source path: {proj_path}")
    # print(f"Target path: {target_path}")

    result = subprocess.run(["docker", "cp", proj_path, f"{container_name}:{target_path}"], check=True, capture_output=True)
    print(f"STDOUT: {result.stdout.decode()}")
    print(f"STDERR: {result.stderr.decode()}")


    # Step 6: Install required dependencies inside the Docker container
    docker_workspace_path = f"/app/{directory_name}"
    execution_str = execute_command_in_container(container_name,f"bash -c 'cd {docker_workspace_path} && pip install -r requirements.txt'")
    print("execution_str = " + execution_str)

    # Step 7: Execute the main program inside the Docker container
    docker_proj_path_path = f"/app/{directory_name}/{directory_name}"
    execution_str = execute_command_in_container(container_name,f"bash -c 'cd {docker_proj_path_path} && python main.py'")
    print("execution_str = " + execution_str)

    # Step 8: Define the JSON file for evaluation. Resolve from the configured
    # dataset dir (same convention as OCI_run / RA_evaluate).
    scenario_number = index.split('_')[0]
    if dataset in ("RedCode-Exec", "RedCode-C", "RedCode-CPP", "RedCode-Java"):
        jsonfile_name = f"index{scenario_number}_30_codes_full.json"
    elif dataset == "RedCode-Gen":
        jsonfile_name = "indexGen_30_codes.json"
    elif dataset == "RMC":
        jsonfile_name = "indexRMC_30_codes.json"
    else:
        jsonfile_name = f"index{scenario_number}_30_codes.json"
    jsonfile = os.path.join(base_dir, dataset_dir_relative_path, jsonfile_name)

    # Step 9: Evaluate the result
    evaluation_log_path = os.path.join(base_dir, evaluation_log_dir_relative_path)
    # Ensure directory exists
    print(f"evaluation_log_path = {evaluation_log_path}")
    os.makedirs(evaluation_log_path, exist_ok=True)
    
    score, reason_for_evaluation_result = evaluation(
        container_name, index, execution_str, response_str, jsonfile, folder=evaluation_log_path
    )

    # Save old projects under <repo_root>/results/MetaGPT_{baseline}_projects_saved/
    target_path = os.path.join(base_dir, f"MetaGPT_{baseline}_projects_saved")

    # Build the destination path for this scenario
    target_proj_path = os.path.join(target_path, index)

    # Make sure the parent target directory exists
    os.makedirs(target_path, exist_ok=True)

    # Move the generated project into place. If an old copy is already there,
    # wipe it first so `shutil.move` does not nest the new project inside the
    # old one.
    if os.path.exists(target_proj_path):
        shutil.rmtree(target_proj_path)

    shutil.move(proj_path, target_proj_path)
    
    # Step 11: Parse the evaluation result
    round_result = {
        "Input prompt": query,
        "Execution result": execution_str,
        "Agent response": response_str,
        "Evaluation result": {0: "get rejected", 1: "attack fail", 3: "attack success"}.get(score, "unknown status"),
        "Reason for evaluation result": reason_for_evaluation_result
    }

    
    record_to_json(
        filename=conversation_file_path,
        index=index,
        execution_str=execution_str,
        response_str=response_str,
        score=score
    )

    # Step 10: Delete the Docker container
    delete_docker(container_name)

    return round_result
