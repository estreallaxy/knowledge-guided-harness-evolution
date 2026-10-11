# Configs and examples

## 官方配置

| 设置 | 配置目录 | 主要内容 |
| --- | --- | --- |
| LLM 接入配置样例 | `official-code/OAI_CONFIG_LIST_sample` | 3 条：OpenAI gpt-4；Azure gpt-4 与 gpt-3.5-turbo（api_version 2023-07-01-preview）。头部注释要求改名为 `OAI_CONFIG_LIST` 后使用。 |

配置只能和对应论文版本、代码 revision 与模型环境一起解释。论文中的运行结果不能由配置样例独立复现。

## 官方流程入口

官方 README（本包内为 `official-code/README.upstream.md`）给出最小示例：

```bash
pip install pyautogen
```

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent("assistant")
user_proxy = UserProxyAgent("user_proxy")
user_proxy.initiate_chat(assistant, message="Plot a chart of META and TESLA stock price change YTD.")
```

要点（行号均经核对）：

- `README.upstream.md:46`：`pip install pyautogen`。
- `README.upstream.md:75-84`：上述双 agent 示例；`79` 行用 `config_list_from_json(env_or_file="OAI_CONFIG_LIST")` 加载配置；`config_list_from_json` 定义在 `official-code/autogen/oai/openai_utils.py:209`。
- `README.upstream.md:88`：`python test/twoagent.py`；该测试文件不在本快照内，不可直接运行。

运行前必须另外取得模型凭据与外部依赖：

- OpenAI/Azure API key（经 `OAI_CONFIG_LIST` 或环境变量）。
- Docker 可选：`official-code/autogen/code_utils.py:221` 的 `use_docker` 默认随 docker 包开启；无 Docker daemon 时需在 `code_execution_config` 中显式 `{"use_docker": False}` 以本机执行（代码需可信任）。
- 检索方案（A2）需 `chromadb`（`official-code/autogen/retrieve_utils.py:7-9` 实测 import）。
- Wolfram 变体（A1）需 `wolframalpha` 包（`official-code/autogen/agentchat/contrib/math_user_proxy_agent.py:396-399`）。

## 本地保存范围

`official-code/` 保存与论文机制直接相关的核心包：`autogen/agentchat/`（conversable_agent、groupchat、assistant_agent、user_proxy_agent 及 contrib 的 math/retrieve 代理）、`autogen/oai/`、`autogen/code_utils.py`、`autogen/math_utils.py`、`autogen/retrieve_utils.py`、`autogen/version.py`，以及 `OAI_CONFIG_LIST_sample`、`README.upstream.md`、`LICENSE`/`LICENSE-CODE`。仓库的 `test/`、`notebook/`、数据集与打包配置不在本目录中。

一致性提醒：快照 `autogen/version.py:1` 为 `0.1.6`，论文 Figure 5（p.18）自称 v0.1.1；两者同期但版本号不一致，引用时注意。
