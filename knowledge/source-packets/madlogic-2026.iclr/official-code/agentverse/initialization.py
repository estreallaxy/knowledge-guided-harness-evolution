from copy import deepcopy

from agentverse.llms import llm_registry
from agentverse.agents import agent_registry
from agentverse.environments import env_registry
from agentverse.memory import memory_registry
from agentverse.parser import output_parser_registry


def load_llm(config):
    config = dict(config)
    return llm_registry.build(config.pop("llm_type", "openai"), **config)


def load_memory(config):
    config = dict(config)
    return memory_registry.build(config.pop("memory_type", "chat_history"), **config)


def load_agent(config):
    config = dict(config)
    return agent_registry.build(config.pop("agent_type", "llm_eval_multi"), **config)


def load_environment(config):
    config = dict(config)
    return env_registry.build(config.pop("env_type", "llm_eval"), **config)


def prepare_task_config(config, stage):
    config = deepcopy(config)
    task = config[stage]
    parser_type = "translate" if stage == "translation" else "final_debate"
    parser = output_parser_registry.build(parser_type, dataset_name=config["dataset"]["name"])
    for agent in task["agents"]:
        for name in ("prompt_template", "normal_turn_instruction", "final_prompt_to_use"):
            if name in task:
                agent.setdefault(name, task[name])
        agent["llm"] = load_llm(config["llm"])
        agent["memory"] = load_memory({})
        agent["output_parser"] = parser
        agent["max_retry"] = config["llm"]["max_retry"]
    sparse = task["sparse"]
    task["environment"] = {
        "env_type": "llm_eval", "max_turns": task["rounds"],
        "rule": {
            "order": {"type": "concurrent"},
            "visibility": {"type": "sparse", **config["sparse"]} if sparse else {"type": "all"},
            "updater": {"type": "sparse" if sparse else "basic"},
        },
    }
    return task
