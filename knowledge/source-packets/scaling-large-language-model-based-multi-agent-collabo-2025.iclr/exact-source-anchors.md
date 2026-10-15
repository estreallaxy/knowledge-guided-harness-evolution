# Exact source anchors

## Selected mechanism

Agents are placed in a DAG and executed in topological order; topology and agent count control parallelism, communication, and cost. No model training is part of the mechanism.

## Paper anchors

- p. 1: limitations in their enclosed reasoning, particularly when addressing complex situations that extend
- p. 5: Implementation Details We construct non-deterministic topologies such as trees and graphs
- p. 6: Method Paradigm MMLU HumanEval SRDD CommonGen Quality
- p. 9: Implementation Implementation Implementation

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `requirements.txt`
- `config.yaml`
- `camel/configs.py`
- `chatdev/test_unfinished_function.py`
- `generate_graph.py`
- `graph.py`
- `run.py`
- `camel/agents/__init__.py`
- `camel/agents/base.py`
- `camel/agents/chat_agent.py`
- `camel/agents/role_playing.py`
- `camel/prompts/__init__.py`
- `camel/prompts/base.py`
- `camel/prompts/prompt_templates.py`
- `camel/prompts/task_prompt_template.py`
- `camel/__init__.py`
- `camel/model_backend.py`
- `camel/typing.py`
- `camel/utils.py`
- `chatdev/chat_chain.py`
- `chatdev/chat_env.py`
- `chatdev/codes.py`
- `chatdev/company_hr.py`
- `chatdev/competition.py`
- `chatdev/composed_phase.py`
- `chatdev/documents.py`
- `chatdev/phase.py`
- `chatdev/richshell.py`
- `chatdev/roster.py`
- `chatdev/statistics.py`
- `chatdev/utils.py`
- `chatdev/waiting.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Agents are placed in a DAG and executed in topological order; topology and agent count control parallelism, communication, and cost. No model training is part of the mechanism.

## Symbol-level code anchors

- `README.md:83` — `aggregate`
- `camel/configs.py:19` — `ChatGPTConfig`
- `chatdev/test_unfinished_function.py:8` — `get_py_files_in_folder`
- `generate_graph.py:7` — `Edge`
- `graph.py:42` — `log_info`
- `run.py:5` — `load_config`
- `camel/agents/base.py:17` — `BaseAgent`
- `camel/agents/chat_agent.py:35` — `ChatAgentResponse`
- `camel/agents/role_playing.py:26` — `RolePlaying`
- `camel/prompts/base.py:22` — `return_prompt_wrapper`
- `camel/prompts/prompt_templates.py:21` — `PromptTemplateGenerator`
- `camel/prompts/task_prompt_template.py:22` — `TaskPromptTemplateDict`
