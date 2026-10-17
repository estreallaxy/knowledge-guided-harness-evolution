import os
import json
from utils.memory import write_memory_with_embeddings,find_similar_memory_entries,extract_mem_info_from_agent,read_memory
from utils.config import update_config, get_config_value
from agent_prompt import *
from agent_tools import Role_play_jailbreak_module,Template_jailbreak_module,query_target_agent,code_substitution_module,GCG_jailbreak_module,AmpleGCG_jailbreak_module,Advprompter_jailbreak_module,AutoDAN_jailbreak_module,self_reflection_module
import re
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from langgraph.errors import GraphRecursionError

def Agent(item_index,input_prompt,baseline,mem,current_memory_path,current_config_path):
    print("### in Agent here")
    ### need to put in a config file
    # API keys: prefer existing env var (e.g. exported by scripts/run_agent.sh),
    # fall back to config file. Never overwrite a non-empty env var with config.
    def _load_key(env_name, config_key=None):
        config_key = config_key or env_name
        if os.environ.get(env_name):
            return os.environ[env_name]
        val = get_config_value(config_key, current_config_path)
        if val:
            os.environ[env_name] = val
        return val

    _load_key("HUGGINGFACE_HUB_TOKEN")
    _load_key("AZURE_OPENAI_API_KEY")
    _load_key("OPENAI_API_KEY")
    max_iteration = int(get_config_value("max_iteration",current_config_path))
    model_id = get_config_value("model_id",current_config_path)
    risk_scenario = get_config_value("risk_scenario",current_config_path)
    risk_scenario_index = get_config_value("risk_index",current_config_path)
    agent_base_llm = get_config_value("agent_base_llm", current_config_path) or "openai"
    dataset = get_config_value("dataset",current_config_path)
    
    # Read the model name from the config file (if configured).
    agent_model_name = get_config_value("agent_model_name", current_config_path) or "gpt-4o-mini"

    # Initialize the agent.
    ### Use the agent: ChatOpenAI
    if(agent_base_llm=="openai"):
        from langchain_openai import ChatOpenAI
        # Env var first, then config file.
        openai_api_key = os.environ.get("OPENAI_API_KEY") or get_config_value("OPENAI_API_KEY", current_config_path)
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found. Set it via env var (e.g. in scripts/run_agent.sh) or in the baseline config JSON.")
        model = ChatOpenAI(model=agent_model_name, api_key=openai_api_key)
        print(f"### using chat openai with model: {agent_model_name}")
    elif(agent_base_llm=="together"):
        from langchain_openai import ChatOpenAI
        # Env var first, then config file.
        together_api_key = os.environ.get("TOGETHER_API_KEY") or get_config_value("TOGETHER_API_KEY", current_config_path)
        if not together_api_key:
            raise ValueError("TOGETHER_API_KEY not found in config file. Please set it in your config.")
        # Together AI uses the OpenAI-compatible API; base_url points to Together AI's endpoint.
        model = ChatOpenAI(
            model=agent_model_name,
            api_key=together_api_key,
            base_url="https://api.together.xyz/v1"
        )
        print(f"### using Together AI with model: {agent_model_name}")
    else:  # azure
        from langchain_openai import AzureChatOpenAI
        # All Azure settings come from env vars (typically exported by
        # scripts/run_agent.sh). The default agent path is OpenAI / Together;
        # this branch only runs when you explicitly set `agent_base_llm=azure`.
        azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", agent_model_name)
        azure_api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        if not azure_endpoint or not os.environ.get("AZURE_OPENAI_API_KEY"):
            raise ValueError(
                "agent_base_llm=azure requires AZURE_OPENAI_API_KEY and "
                "AZURE_OPENAI_ENDPOINT. Export them via scripts/run_agent.sh "
                "or your baseline config JSON."
            )
        model = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            openai_api_version=azure_api_version,
        )
        print(f"### using Azure OpenAI with deployment: {azure_deployment}")
    red_teaming_requirement = input_prompt

    tools = [query_target_agent,code_substitution_module,GCG_jailbreak_module,AmpleGCG_jailbreak_module,Advprompter_jailbreak_module,AutoDAN_jailbreak_module,Role_play_jailbreak_module,Template_jailbreak_module,self_reflection_module]
    
    tool_names = [tool.__name__ for tool in tools]
    
    agent = create_react_agent(model, tools, prompt=agent_system_prompt)
    print(f"Using memory? mem = {mem}")

    if mem is True:
        # Read topk from the config file; default to 3.
        topk = int(get_config_value("topk", current_config_path) or 3)
        most_similar_experiences,most_similar_indexs = find_similar_memory_entries(
        risk_scenario=risk_scenario,
        model_type=model_id,
        red_teaming_requirement=red_teaming_requirement,
        file_path=current_memory_path,
        topk=topk
        )

        # Convert the list into a numbered string, prefixing each entry with Experience1. Experience2. etc.
        most_similar_experiences_str = ' '.join([f"Experience{i+1}. {entry}" for i, entry in enumerate(most_similar_experiences)])

        # Apply re.sub() on the string (to handle backslashes if needed).
        processed_most_similar_experiences = re.sub(r'\\{2,}', r'\\', most_similar_experiences_str)

        # print("Most similar entries processed_most_similar_experiences:", processed_most_similar_experiences)
        print("Most similar entries most_similar_indexs:", most_similar_indexs)
    else: 
        print("Not using memory")
        processed_most_similar_experiences=""
        most_similar_indexs=[]

    if dataset != "RedCode-Exec":
        query = f"Current target goal is to {red_teaming_requirement}."# for Gen and other benchmark
    else:
        query = f"Current test case index is {item_index}. Current red teaming scenario is {risk_scenario}. Current target goal is to {red_teaming_requirement}."
    
    if processed_most_similar_experiences != "":
        print("processed_most_similar_experiences is not empty.")
        query += f"The previous experience you can refer to are as follows: {processed_most_similar_experiences}"
        
    # Initialize storage.
    store_message = "" #parse agent output
    round_memory_data = {
        "risk_index": item_index,
        "risk_scenario": risk_scenario,
        "red_teaming_requirement": red_teaming_requirement,
        "model_type": model_id,
        "reference_experience_index":most_similar_indexs,
        "tool_names":tool_names,
        "trajectory": [],
        "evaluation_result": "",
        "self_reflection": "",
        "memory_validity":"Invalid",
    }

    first_message = True  # Flag whether this is the first message; the agent's initial prompt is not counted as trajectory.

    try:
        print(f"#####Before agent.stream, query = {query}")
        for chunk in agent.stream(
            {"messages": [("human", query)]},
            {"recursion_limit": max_iteration},
            stream_mode="values",
        ):
            if first_message:
                first_message = False  # Skip the first message; the agent's initial prompt is not part of the trajectory.
                continue
        
            print(f"#####This is a chunk message: {chunk['messages'][-1]}")
            message = chunk["messages"][-1]
            message.pretty_print()
            
            # with open(f'chunk_output_{risk_scenario_index}.txt', 'a') as file:
            #     file.write("#####This is a chunk message: " + str(chunk["messages"][-1]) + "\n")
            #     file.flush()  # Ensure the content is flushed to disk immediately.
            # Buffer the message.
            store_message += str(message) + "\n"
            # print(f"### Current store_message is : {store_message}")
            # Extract information and write to memory.
            if "tool_call_id" in store_message and "self_reflection_module" not in store_message:
                # Extract information to write to memory.
                # print(f"## Current extract information of tools: {store_message}")
                trajectory_memory_data = extract_mem_info_from_agent(store_message)
                
                # Append trajectory_memory_data to round_memory_data["trajectory"].
                round_memory_data["trajectory"].append(trajectory_memory_data)
                
                # If evaluation_result is "attack success", update round_memory_data["evaluation_result"].
                if round_memory_data["evaluation_result"] != "attack success":
                    round_memory_data["evaluation_result"] = trajectory_memory_data["evaluation_result"]
                
                # Clear store_message.
                store_message = ""
            if "tool_call_id" in store_message and "self_reflection_module" in store_message:  # summarizing
                # print(f"## Current extract information of self_reflection: {store_message}")
                # print(f"##### Current round_memory_data: {round_memory_data}")
                trajectory_memory_data = extract_mem_info_from_agent(store_message)
                round_memory_data["self_reflection"] = trajectory_memory_data["tool_call_results"]
                store_message = ""
                if round_memory_data["evaluation_result"] == "attack success":  # summary exists and attack succeeded
                    print("&&& Attack success and have self reflection, writing memory")
                    round_memory_data["memory_validity"] = "Valid"
                    # write_memory_with_embeddings(round_memory_data,file_path=ocurrent_memory_path)
                    
    except GraphRecursionError:
        print(f"&&& Error with item index {item_index}: Agent stopped due to max iterations. Continuing to next item.")
    except Exception as e:
        # Catch all other exceptions and log the error.
        print(f"&&& An unexpected error occurred with item index {item_index}: {str(e)}")
        # An exception occurred; skip writing for this item.
    
    print(f"&&& Finally write into memory,no matter success or failure.")
    write_memory_with_embeddings(round_memory_data,file_path=current_memory_path) #record failure cases for case study
    # An exception occurred; skip writing for this item.

    

