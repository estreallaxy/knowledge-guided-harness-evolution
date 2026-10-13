# Configs and examples

## Official configuration

|set up|Configuration directory|Main content|
| --- | --- | --- |
|LLM access configuration example| `official-code/OAI_CONFIG_LIST_sample` |3 items: OpenAI gpt-4; Azure gpt-4 and gpt-3.5-turbo (api_version 2023-07-01-preview). The header annotation requires renaming to`OAI_CONFIG_LIST`before use.|

Configurations can only be interpreted in conjunction with corresponding paper versions, code revisions, and model environments. The running results in the paper cannot be independently reproduced by the configuration examples.

## Official process entrance

The official README (`official-code/README.upstream.md`in this package) gives a minimal example:

```bash
pip install pyautogen
```

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user_proxy")
user_proxy.initiate_chat(assistant, message="Plot a chart of META and TESLA stock price change YTD.")
```

Key points (line numbers have been checked):

- `README.upstream.md:46`: `pip install pyautogen`.
-`README.upstream.md:75-84`: The above dual agent example;`79`line uses`config_list_from_json(env_or_file="OAI_CONFIG_LIST")`to load the configuration;`config_list_from_json`is defined in`official-code/autogen/oai/openai_utils.py:209`.
-`README.upstream.md:88`:`python test/twoagent.py`; This test file is not in this snapshot and cannot be run directly.

Model credentials and external dependencies must be additionally obtained before running:

- OpenAI/Azure API key (via`OAI_CONFIG_LIST`or environment variable).
- Docker optional:`use_docker`of`official-code/autogen/code_utils.py:221`is enabled by default with the docker package; if there is no Docker daemon,`{"use_docker": False}`needs to be explicitly executed in`code_execution_config`locally (the code must be trustworthy).
- The search plan (A2) requires`chromadb`(`official-code/autogen/retrieve_utils.py:7-9`measured import).
- Wolfram variant (A1) requires the`wolframalpha`package (`official-code/autogen/agentchat/contrib/math_user_proxy_agent.py:396-399`).

## Local saving range

`official-code/`saves core packages directly related to the paper mechanism:`autogen/agentchat/`(conversable_agent, groupchat, assistant_agent, user_proxy_agent and contrib's math/retrieve agent),`autogen/oai/`,`autogen/code_utils.py`,`autogen/math_utils.py`,`autogen/retrieve_utils.py`,`autogen/version.py`, and`OAI_CONFIG_LIST_sample`,`README.upstream.md`,`LICENSE`/`LICENSE-CODE`. The`test/`,`notebook/`, data sets and packaging configurations of the repository are not in this directory.

Consistency reminder: The snapshot`autogen/version.py:1`is`0.1.6`, and the paper Figure 5 (p.18) calls itself v0.1.1; the two are in the same period but the version numbers are inconsistent, so be careful when citing.
