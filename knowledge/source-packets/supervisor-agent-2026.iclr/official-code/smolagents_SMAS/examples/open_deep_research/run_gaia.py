# EXAMPLE COMMAND: from folder examples/open_deep_research, run: python run_gaia.py --concurrency 32 --run-name generate-traces-03-apr-noplanning --model-id gpt-4o
import argparse
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import datasets
import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import login, snapshot_download
from scripts.reformulator import prepare_response
from scripts.run_agents import (
    get_single_file_description,
    get_zip_description,
)
from scripts.text_inspector_tool import TextInspectorTool
from scripts.text_web_browser import (
    ArchiveSearchTool,
    FinderTool,
    FindNextTool,
    PageDownTool,
    PageUpTool,
    SimpleTextBrowser,
    VisitTool,
)
from scripts.visual_qa import visualizer
from tqdm import tqdm

from smolagents import (
    CodeAgent,
    GoogleSearchTool,
    LiteLLMModel,
    Model,
    ToolCallingAgent,
    SupervisorAgent,
)

from smolagents.agents import RunResult
from smolagents.memory import FinalAnswerStep, ActionStep

from smolagents.models import MonitoredModel    # 用于全局监督 token cost
import re
import traceback


load_dotenv(override=True)
login(os.getenv("HF_TOKEN"))

append_answer_lock = threading.Lock()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--num-examples", type=int, default=1)
    parser.add_argument("--model-id", type=str, default="gpt-4.1")
    parser.add_argument("--model-id-summary", type=str, default="gpt-4.1")
    parser.add_argument("--run-name", type=str, required=True)
    parser.add_argument("--set-to-run", type=str, default="validation")
    parser.add_argument("--use-open-models", type=bool, default=False)
    parser.add_argument("--use-raw-dataset", action="store_true")
    parser.add_argument("--supervisor", action="store_true")
    parser.add_argument("--task-id", type=str, default=None, help="Only run the task with this specific ID")
    parser.add_argument("--level", type=int, default=None, help="Only run tasks with this specific level")
    return parser.parse_args()


### IMPORTANT: EVALUATION SWITCHES

print("Make sure you deactivated any VPN like Tailscale, else some URLs will be blocked!")

custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"

BROWSER_CONFIG = {
    "viewport_size": 1024 * 5,
    "downloads_folder": "downloads_folder",
    "request_kwargs": {
        "headers": {"User-Agent": user_agent},
        "timeout": 300,
    },
    "serpapi_key": os.getenv("SERPAPI_API_KEY"),
}

os.makedirs(f"./{BROWSER_CONFIG['downloads_folder']}", exist_ok=True)

class TokenUsage:
    def __init__(self, input_tokens=0, output_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

def calculate_and_log_token_usage(
    agent_dict: dict[str, any],
    monitored_model: MonitoredModel,
    prep_token_usage: TokenUsage,
    supervisor: bool
) -> dict:
    """
    Calculate and print token consumption from all sources, and return a final dictionary for storage.

    Args:
        agent_dict (dict): A dictionary containing all Agent instances.
        monitored_model (MonitoredModel): The wrapped model instance.
        prep_token_usage (TokenUsage): Token usage returned from prepare_response.
        supervisor (bool): Whether supervisor mode was used.

    Returns:
        dict: A dictionary containing the total consumption and the supervisor-related consumption for final storage.
    """
    # --- Agent-level external usage ---
    agent_total_input = 0
    agent_total_output = 0
    supervisor_total_tokens = 0
    summary_total_usage = 0

    # 1. Manager Agent
    manager_usage = agent_dict["manager"].monitor.get_total_token_counts()
    agent_total_input += manager_usage.input_tokens
    agent_total_output += manager_usage.output_tokens
    print(f"Manager agent token usage - Input: {manager_usage.input_tokens}, Output: {manager_usage.output_tokens}")

    # 2. Web Search Agent
    web_search_usage = agent_dict["web_search"].monitor.get_total_token_counts()
    agent_total_input += web_search_usage.input_tokens
    agent_total_output += web_search_usage.output_tokens
    print(f"Web Search agent token usage - Input: {web_search_usage.input_tokens}, Output: {web_search_usage.output_tokens}")

    # 3. Supervisor
    supervisor_input = 0
    supervisor_output = 0
    if supervisor:
        supervisor_usage = agent_dict["supervisor"].monitor.get_total_token_counts()
        supervisor_input = supervisor_usage.input_tokens
        supervisor_output = supervisor_usage.output_tokens
        supervisor_total_tokens = supervisor_input + supervisor_output
        print(f"Supervisor/Verification token usage - Input: {supervisor_input}, Output: {supervisor_output}")
    
    # 4. Token usage of the prepare_response step
    agent_total_input += prep_token_usage.input_tokens + supervisor_input
    agent_total_output += prep_token_usage.output_tokens + supervisor_output
    print(f"Preparation step token usage - Input: {prep_token_usage.input_tokens}, Output: {prep_token_usage.output_tokens}")

    # 5. Summary Model
    if "summary_model" in agent_dict:
        summary_model = agent_dict["summary_model"]
        summary_usage = summary_model.total_token_usage
        agent_total_input += summary_usage.input_tokens
        agent_total_output += summary_usage.output_tokens
        summary_total_usage = summary_usage.input_tokens + summary_usage.output_tokens
        print(f"Summary model token usage - Input: {summary_usage.input_tokens}, Output: {summary_usage.output_tokens}")
    
    if "text_inspector" in agent_dict:
        ti_tool = agent_dict["text_inspector"]
        ti_usage = ti_tool.get_total_token_counts()
        agent_total_input += ti_usage.input_tokens
        agent_total_output += ti_usage.output_tokens
        print(f"Text Inspector Tool token usage - Input: {ti_usage.input_tokens}, Output: {ti_usage.output_tokens}")

    agent_total_tokens = agent_total_input + agent_total_output

    # --- Internal usage recorded by MonitoredModel ---
    internal_usage = monitored_model.total_token_usage
    internal_total_tokens = internal_usage.input_tokens + internal_usage.output_tokens
    print(f"Model-level (internal) total token usage - Input: {internal_usage.input_tokens}, Output: {internal_usage.output_tokens}\n")

    # --- Compute the final total ---
    grand_total_tokens = agent_total_tokens + internal_total_tokens
    print(f"Grand total token usage (all sources) = {grand_total_tokens}\n")
    
    return {
        "total_token_count": grand_total_tokens,
        "supervisor_token": supervisor_total_tokens + summary_total_usage,
    }

def create_supervisor_callback(supervisor: SupervisorAgent, example: dict):
    """
    Create a callback function that conditionally invokes the supervisor
    and precisely passes the local and global task context.
    
    Args:
        supervisor (SupervisorAgent): The supervisor agent instance.
        example (dict): The currently running GAIA dataset entry.
    """
    # parent_agent_map is a simplified way to track call relationships.
    # In a real framework, you may need a more robust call stack to manage this.
    parent_agent_map = {"search_agent": "manager_agent"}

    def supervisor_callback(memory_step: ActionStep, agent: CodeAgent):
        if isinstance(memory_step, ActionStep):
            global_task = example["question"]   # The global task is always the original question
            parent_agent_name = parent_agent_map.get(agent.name)

            if agent.name == "manager_agent":
                clean_local_task = ""   # Prevent duplication between global and local
            else:
                clean_local_task = extract_clean_task(agent.task)   # Extract the original local task
            supervisor.record_step(
                step=memory_step,
                agent_name=agent.name,
                # memory=agent.memory,
                local_task=clean_local_task,
                parent_agent_name=parent_agent_name
            )

            should_supervise = False
            
            # Priority 1: handle errors
            if memory_step.error is not None:
                # By default, any error should trigger supervision
                should_supervise = True
                
                # **Only exception**: if the error is caused by the 'find_archived_url' tool, we choose to ignore it
                # Defensively check whether tool_calls exists and is non-empty
                if memory_step.tool_calls and memory_step.tool_calls[0].name == "find_archived_url":
                    should_supervise = False # Override to not supervise
                    print(f"--- [Supervisor] Ignoring a known/safe error from 'find_archived_url'. ---")
            
            # Only check other conditions when there is no error
            if not should_supervise:
                if (memory_step.observations and len(memory_step.observations) > 3000):
                    should_supervise = True
                elif supervisor._check_for_inefficiency(agent.name)[0]:
                    should_supervise = True
                elif (memory_step.observations and "### 1. Task outcome (short version):" in memory_step.observations):
                    should_supervise = True

            # Try to preserve the original return values of web_search
            if memory_step.tool_calls and len(memory_step.tool_calls) > 0:
                if memory_step.tool_calls[0].name == "web_search" and len(memory_step.observations) < 5000:
                    should_supervise = False
                    print("--- [Supervisor] Skip web_search_tool supervision")

            is_final_answer_attempt = False

            # Filter repeatedly visited URLs
            if memory_step.observations and "## Search Results" in memory_step.observations:
                if memory_step.tool_calls[0].name != "final_answer":
                    original_observation = memory_step.observations
                    filtered_observation = supervisor.filter_search_results(original_observation)
                    # If the filtering actually removed content, update the observation in place
                    if original_observation != filtered_observation:
                        print("--- [Supervisor] Silently filtering observation without forcing API-based intervention. ---")
                        memory_step.observations = filtered_observation

            if should_supervise:
                parent_agent_name = parent_agent_name
                supervisor.supervise_and_correct(
                    step=memory_step, 
                    agent_name=agent.name, 
                    local_task=clean_local_task,
                    global_task=global_task,
                    is_final_check=is_final_answer_attempt
                )
            else:
                print(f"--- [Supervisor] Skipped review for step {memory_step.step_number} of '{agent.name}'. ---")
            
    return supervisor_callback

def extract_clean_task(full_task_prompt: str) -> str:
    """
    Extract a clean core task description from a full enhanced instruction.
    Assumes the core task is located between two '---' delimiters.
    """
    try:
        # 1. Split the string by '---', which divides it into three parts
        parts = full_task_prompt.split('---')
        if len(parts) >= 3:
            # 2. Take the middle part, which contains "Task:" and the core task
            task_block = parts[1]
            
            # 3. Clean the prefix and surrounding whitespace
            # First remove "Task:" (and its surrounding newlines)
            if "Task:" in task_block:
                task_content = task_block.split("Task:", 1)[1]
            else:
                task_content = task_block
            
            return task_content.strip()
        else:
            # If the format doesn’t match, return the original task for robustness
            return full_task_prompt
    except Exception:
        # Safely return the original input if any exception occurs
        return full_task_prompt

def create_verification_agent(model: Model) -> CodeAgent:
    """
    Create a lightweight yet fully capable verification agent optimized for the Supervisor.
    This agent is based on ToolCallingAgent.
    """
    browser = SimpleTextBrowser(**BROWSER_CONFIG)
    # Set a lower text limit for the verification agent to control token consumption
    text_limit = 10000
    
    # Equip the Supervisor Agent with a complete toolset, including the visualizer, to ensure equal capability
    VERIFICATION_TOOLS = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        TextInspectorTool(model, text_limit),
        visualizer,  # Grant the Supervisor visual capability
    ]

    verification_agent = ToolCallingAgent(
        model=model,
        tools=VERIFICATION_TOOLS,
        max_steps=8,  # Lower max_steps to control cost
        verbosity_level=0,  # Disable detailed logs to keep Supervisor output clean
        name="verification_agent",
        description="A specialized agent for quick fact-checking and information verification.",
        # Allow all imports if necessary for tool execution
        # additional_authorized_imports=["*"], 
        # You may also increase token limits at the model level, e.g.:
        # model=LiteLLMModel(model_id=model.model_id, max_tokens=1024)
    )

    # Optimize the verification_agent prompt to focus on efficient retrieval and verification
    verification_agent.prompt_templates["system_prompt"] += """
    You are a highly efficient fact-checking assistant. Your primary goal is to quickly and accurately verify, correct, or summarize information based on a given task.
    - Be precise and concise.
    - Avoid deep, exploratory searches.
    - Execute the task, find the specific information needed, and use the 'final_answer' tool immediately to return the result.
    - Your response should be direct and factual.
    Here are the tools you can use:
    """ + "\n".join([tool.to_code_prompt() for tool in verification_agent.tools.values()])
    
    return verification_agent


def create_agent_team(model: Model):
    text_limit = 100000
    ti_tool = TextInspectorTool(model, text_limit)

    browser = SimpleTextBrowser(**BROWSER_CONFIG)

    WEB_TOOLS = [
        GoogleSearchTool(provider="serper"),
        VisitTool(browser),
        PageUpTool(browser),
        PageDownTool(browser),
        FinderTool(browser),
        FindNextTool(browser),
        ArchiveSearchTool(browser),
        ti_tool,
    ]

    text_webbrowser_agent = ToolCallingAgent(
        model=model,
        tools=WEB_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
    Ask him for all your questions that require browsing the web.
    Provide him as much context as possible, in particular if you need to search on a specific timeframe!
    And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
    Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
    """,
        provide_run_summary=True,
    )
    text_webbrowser_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""

    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, ti_tool],
        max_steps=12,
        verbosity_level=2,
        additional_authorized_imports=["*"],
        planning_interval=4,
        managed_agents=[text_webbrowser_agent],
    )
    # return manager_agent
    return {
        "manager": manager_agent,
        "web_search": text_webbrowser_agent,
        "text_inspector": ti_tool
        }


def create_agent_team_with_supervisor(model: Model, summary_model: Model, example: dict):
    # === 1. Create a fully capable Verification Agent dedicated to the Supervisor ===
    verification_agent = create_verification_agent(model)

    # === 2. Create the Supervisor and inject the Verification Agent ===
    supervisor = SupervisorAgent(model=model, summary_model=summary_model, verification_agent=verification_agent)
    # Create a concrete callback instance using example
    supervisor_callback_instance = create_supervisor_callback(supervisor, example)    

    # === 3. Create the Web Agent dedicated to the main task ===
    text_limit = 100000
    ti_tool = TextInspectorTool(model, text_limit)
    main_browser = SimpleTextBrowser(**BROWSER_CONFIG)
    MAIN_WEB_TOOLS = [
        GoogleSearchTool(provider="serper"),
        VisitTool(main_browser),
        PageUpTool(main_browser),
        PageDownTool(main_browser),
        FinderTool(main_browser),
        FindNextTool(main_browser),
        ArchiveSearchTool(main_browser),
        ti_tool,
    ]
    main_web_agent = ToolCallingAgent(
        model=model,
        tools=MAIN_WEB_TOOLS,
        max_steps=20,
        verbosity_level=2,
        planning_interval=4,
        name="search_agent",
        description="""A team member that will search the internet to answer your question.
    Ask him for all your questions that require browsing the web.
    Provide him as much context as possible, in particular if you need to search on a specific timeframe!
    And don't hesitate to provide him with a complex search task, like finding a difference between two webpages.
    Your request must be a real sentence, not a google search! Like "Find me this information (...)" rather than a few keywords.
    """,
        provide_run_summary=True,
        step_callbacks=[supervisor_callback_instance], # Add a callback to main_web_agent
    )

    main_web_agent.prompt_templates["managed_agent"]["task"] += """You can navigate to .txt online files.
    If a non-html page is in another format, especially .pdf or a Youtube video, use tool 'inspect_file_as_text' to inspect it.
    Additionally, if after some searching you find out that you need more information to answer the question, you can use `final_answer` with your request for clarification as argument to request for more information."""

    # === 4. Create the top-level Manager Agent ===
    manager_agent = CodeAgent(
        model=model,
        tools=[visualizer, ti_tool], # The manager also retains visual ability.
        max_steps=12,
        verbosity_level=2,
        additional_authorized_imports=["*"],
        planning_interval=4,
        managed_agents=[main_web_agent],
        step_callbacks=[supervisor_callback_instance],
        name="manager_agent",
    )
    
    return {
        "manager": manager_agent,
        "supervisor": supervisor,
        "verification": verification_agent,
        "web_search": main_web_agent,
        "summary_model": summary_model,
        "text_inspector": ti_tool
    }

def load_gaia_dataset(use_raw_dataset: bool, set_to_run: str, level: int | None = None) -> datasets.Dataset:
    # 1. Download the dataset
    if not os.path.exists("data/gaia"):
        repo_id = "gaia-benchmark/GAIA" if use_raw_dataset else "smolagents/GAIA-annotated"
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir="data/gaia",
            ignore_patterns=[".gitattributes", "README.md"],
        )
    # 2. Construct the metadata file path
    metadata_file = os.path.join("data/gaia", "2023", set_to_run, "metadata.jsonl")
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
    # 3. read JSONL
    with open(metadata_file, "r") as f:
        data = [json.loads(line) for line in f]
    # 4. Optional level filter
    if level is not None:
        data = [item for item in data if item.get("Level") == level]
    # 5. File path preprocessing
    for item in data:
        if item.get("file_name"):
            item["file_name"] = os.path.join("data/gaia", "2023", set_to_run, item["file_name"])
    # 6. Column rename
    for item in data:
        item["question"] = item.pop("Question", None)
        item["true_answer"] = item.pop("Final answer", None)
        item["task"] = item.pop("Level", None)
    # 7. Convert to Dataset
    eval_ds = datasets.Dataset.from_list(data)
    return eval_ds

def append_answer(entry: dict, jsonl_file: str) -> None:
    jsonl_path = Path(jsonl_file)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with append_answer_lock, open(jsonl_file, "a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
    assert jsonl_path.exists(), "File not found!"
    print("Answer exported to file:", jsonl_path.resolve())

# Convert all ChatMessage objects in intermediate_steps to a dictionary.
def serialize_intermediate_steps(steps):
    serialized = []
    for step in steps:
        if hasattr(step, "content"):
            serialized.append({
                "role": getattr(step, "role", None),
                "content": step.content,
            })
        else:
            # If not ChatMessage, convert to str.
            serialized.append(str(step))
    return serialized

# Optimize the final answer extraction logic
def extract_final_answer(result: any) -> str | None:
    """
    Robustly extracts the final answer from the various possible return types
    of the agent's run method.
    """
    final_answer = None

    # 1. Check if the result is a RunResult object (when return_full_result=True)
    if isinstance(result, RunResult):
        print("-> Result is a RunResult object. Extracting from .output attribute.")
        final_answer = result.output

    # 2. Check if the result is a FinalAnswerStep object (less common but safe to handle)
    elif isinstance(result, FinalAnswerStep):
        print("-> Result is a FinalAnswerStep object. Extracting from .output attribute.")
        final_answer = result.output
        
    # 3. Check if the result is a string
    elif isinstance(result, str):
        print("-> Result is a string. Parsing string for answer.")
        # The string may contain "Final answer:" or simply be the raw answer
        if "Final answer:" in result:
            final_answer = result.split("Final answer:")[-1].strip()
        else:
            # If there is no specific prefix, assume the entire string is the answer
            final_answer = result.strip()
            
    # If final_answer is still None or empty, return None
    if final_answer and str(final_answer).strip():
        return str(final_answer).strip()
    
    return None

def answer_single_question(
    example: dict, model_id: str, model_id_summary, answers_file: str, visual_inspection_tool: TextInspectorTool, supervisor: bool = False) -> None:
    prep_token_usage = TokenUsage()
    model_params: dict[str, Any] = {
        "model_id": model_id,
        "custom_role_conversions": custom_role_conversions,
    }
    model_params_summary: dict[str, Any] = {
        "model_id": model_id_summary,
        "custom_role_conversions": custom_role_conversions,
    }
    if model_id == "o1":
        model_params["reasoning_effort"] = "high"
        model_params["max_completion_tokens"] = 8192
    else:
        model_params["max_tokens"] = 4096
    model_raw = LiteLLMModel(**model_params)
    model = MonitoredModel(model_raw)
    model_raw_summary = LiteLLMModel(**model_params_summary)
    summary_model = MonitoredModel(model_raw_summary)

    document_inspection_tool = TextInspectorTool(model, 100000)
    
    agent_dict: dict[str, any] = {}
    if supervisor:
        agent_dict = create_agent_team_with_supervisor(model, summary_model, example)
        agent = agent_dict["manager"]
        print("=== Using Supervisor Agent ===")
    else:
        agent_dict = create_agent_team(model)
        agent = agent_dict["manager"]
        print("=== Using Standard Agent Team ===")

    augmented_question = """You have one question to answer. It is paramount that you provide a correct answer.
Give it all you can: I know for a fact that you have access to all the relevant tools to solve it and find the correct answer (the answer does exist).
Failure or 'I cannot answer' or 'None found' will not be tolerated, success will be rewarded.
Run verification steps if that's needed, you must make sure you find the correct answer! Here is the task:

""" + example["question"]

    if example["file_name"]:
        if ".zip" in example["file_name"]:
            prompt_use_files = "\n\nTo solve the task above, you will have to use these attached files:\n"
            prompt_use_files += get_zip_description(
                example["file_name"], example["question"], visual_inspection_tool, document_inspection_tool
            )
        else:
            prompt_use_files = "\n\nTo solve the task above, you will have to use this attached file:\n"
            prompt_use_files += get_single_file_description(
                example["file_name"], example["question"], visual_inspection_tool, document_inspection_tool
            )
        augmented_question += prompt_use_files

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Run agent 🚀
        raw_result = agent.run(augmented_question, return_full_result=True)
        raw_final_result = raw_result.output
        agent_memory = agent.write_memory_to_messages()

        output, prep_token_usage, prep_prompt = prepare_response(augmented_question, agent_memory, reformulation_model=model_raw)

        for memory_step in agent.memory.steps:
            memory_step.model_input_messages = None
        intermediate_steps = agent_memory

        # Check for parsing errors which indicate the LLM failed to follow the required format
        # parsing_error = True if any(["AgentParsingError" in step for step in intermediate_steps]) else False
        parsing_error = any(
            "AgentParsingError" in (step.content if hasattr(step, "content") else str(step))
            for step in intermediate_steps
        )

        # check if iteration limit exceeded
        iteration_limit_exceeded = True if "Agent stopped due to iteration limit or time limit." in output else False
        raised_exception = False

    except Exception as e:
        print("Error on ", augmented_question, e)
        output = None
        raw_final_result = "Failure"
        intermediate_steps = []
        parsing_error = False
        iteration_limit_exceeded = False
        exception = e
        raised_exception = True

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_token_counts = calculate_and_log_token_usage(
        agent_dict=agent_dict,
        monitored_model=model,
        prep_token_usage=prep_token_usage if 'prep_token_usage' in locals() else TokenUsage(),
        supervisor=supervisor
    )

    annotated_example = {
        "agent_name": model.model_id,
        "question": example["question"],
        "augmented_question": augmented_question,
        "Level": example["task"],
        "raw_prediction": raw_final_result,
        "prediction": output,
        "true_answer": example["true_answer"],
        "token_counts": total_token_counts,
        "intermediate_steps": serialize_intermediate_steps(intermediate_steps),
        "parsing_error": parsing_error,
        "iteration_limit_exceeded": iteration_limit_exceeded,
        "agent_error": str(exception) if raised_exception else None,
        "task_id": example["task_id"],
        "start_time": start_time,
        "end_time": end_time,
    }
    append_answer(annotated_example, answers_file)


def load_jsonl_multiline(path: str):
    """Read a JSONL file that supports multi-line JSON objects."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        buffer = ""
        for line in f:
            line = line.strip()
            if not line:
                continue
            buffer += line
            # Attempt to parse
            try:
                record = json.loads(buffer)
                records.append(record)
                buffer = ""  # Clear buffer and wait for the next object
            except json.JSONDecodeError:
                # Indicates the JSON object is not yet complete
                continue
    return records


def get_examples_to_answer(answers_file: str, eval_ds: datasets.Dataset, task_id: str = None) -> list[dict]:
    print(f"Loading answers from {answers_file}...")
    try:
        records = load_jsonl_multiline(answers_file)
        done_questions = [r["question"] for r in records if "question" in r]
        print(f"Found {len(done_questions)} previous results!")
    except Exception as e:
        print("Error when loading records: ", e)
        print("No usable records! ▶️ Starting new.")
        done_questions = []

    examples = [line for line in eval_ds.to_list() if line["question"] not in done_questions]

    if task_id:
        examples = [ex for ex in examples if str(ex.get("task_id")) == str(task_id)]
        print(f"Filtered for task_id={task_id}, {len(examples)} tasks found.")
    return examples

def main():
    args = parse_args()
    print(f"Starting run with arguments: {args}")

    eval_ds = load_gaia_dataset(args.use_raw_dataset, args.set_to_run, args.level)
    print("Loaded evaluation dataset:")
    print(pd.DataFrame(eval_ds)["task"].value_counts())

    answers_file = f"output/{args.set_to_run}/{args.run_name}.jsonl"

    if args.task_id:
        tasks_to_run = get_examples_to_answer(answers_file, eval_ds, args.task_id)
    else:
        tasks_to_run = get_examples_to_answer(answers_file, eval_ds)
        if args.num_examples:
            tasks_to_run = tasks_to_run[: args.num_examples]
        else:
            tasks_to_run = tasks_to_run

    with ThreadPoolExecutor(max_workers=args.concurrency) as exe:
        futures = [
            exe.submit(answer_single_question, example, args.model_id, args.model_id_summary, answers_file, visualizer, args.supervisor)
            for example in tasks_to_run
        ]
        for f in tqdm(as_completed(futures), total=len(tasks_to_run), desc="Processing tasks"):
            f.result()

    print("All tasks processed.")


if __name__ == "__main__":
    main()