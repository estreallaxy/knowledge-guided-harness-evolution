# Configs and examples

官方仓库没有独立的实验配置文件；"配置"由三部分组成：`pyproject.toml` 的依赖与入口、CLI 参数与环境变量、以及用 Python 写死的场景与里程碑定义。以下命令与前提均取自 `official-code/README.upstream.md` 与代码本身，未在本仓库执行。

## 官方安装与运行前提

| 项目 | 内容 | 来源 |
| --- | --- | --- |
| Python | `requires-python = ">=3.9"`；上游 README 用 conda 建 `python=3.9` 环境 | `official-code/pyproject.toml`、`README.upstream.md:9-16` |
| 依赖 | 全量固定版本，含 `polars==0.20.31`、`networkx==3.2.1`、`scipy==1.13.1`、`rouge-score==0.1.2`、`openai==1.17.0`、`anthropic==0.26.1`、`transformers==4.41.2`、`vertexai==1.49.0`、`langchain==0.1.3` 等 29 项；开发依赖 `pytest`、`pytest-xdist`、`mypy` 等 | `official-code/pyproject.toml:28-56`、`:68-84` |
| 安装 | `pip install '.[dev]'` | `README.upstream.md:17-20` |
| 命令入口 | `[project.scripts] tool_sandbox = "tool_sandbox.cli:main"` | `official-code/pyproject.toml:86-87` |
| 测试并行 | `[tool.pytest.ini_options] addopts="-n auto"`（需 pytest-xdist；本地复跑时用 `-o addopts=""` 关掉） | `official-code/pyproject.toml:106-107` |

运行所需环境变量（缺哪个、跑哪些角色会缺）：

| 变量 | 用于 |
| --- | --- |
| `OPENAI_API_KEY` | GPT-3.5 / GPT-4 / GPT-4o 作为 agent 或用户模拟器 |
| `ANTHROPIC_API_KEY` | Claude-3 Haiku / Sonnet / Opus 作为 agent |
| `OPENAI_BASE_URL` | 以 OpenAI 兼容协议接入自托管或 Cohere/Gorilla/Hermes/Mistral |
| `HF_TOKEN` | 首次用 vLLM 托管开源模型 |
| `GOOGLE_CLOUD_PROJECT`/`CLOUD_ML_PROJECT_ID`、`GOOGLE_CLOUD_REGION`/`CLOUD_ML_REGION` | Gemini 系列 |
| `RAPID_API_KEY` | Contact/Messaging/Map/Weather/Stock/Conversion/Holiday 之外依赖 RapidAPI 的检索工具；缺失时相关工具直接抛 `PermissionError` |

来源：`README.upstream.md:23-55`；缺 key 时的行为见 `official-code/tool_sandbox/tools/rapid_api_search_tools.py:63-78`。

## 官方流程入口与可复制命令

CLI 的真实参数为 `--agent`、`--user`、`--preferred_tool_backend`、`-t/--test_mode`、`-s/--scenarios`（可多个）、`-p/--parallel`（默认 16）、`-o/--output_dir`（默认 `data`），见 `official-code/tool_sandbox/cli/__init__.py:197-243`。

```bash
# 单场景：GPT-4o 作模拟用户，Claude 3 Haiku 作 agent
env ANTHROPIC_API_KEY=<KEY> OPENAI_API_KEY=<KEY> \
  tool_sandbox --user GPT_4_o_2024_05_13 --agent Claude_3_Haiku --scenario wifi_off

# 全量场景（不传 -s 即跑全部）
env OPENAI_API_KEY=<KEY> RAPID_API_KEY=<KEY> \
  tool_sandbox --user GPT_4_o_2024_05_13 --agent GPT_4_o_2024_05_13

# 只跑内置的 3 个冒烟场景（cli/utils.py 的 TEST_SCENARIO_NAMES）
tool_sandbox --test_mode

# 自托管开源模型（vLLM 的 OpenAI 兼容服务）
python3 -m vllm.entrypoints.openai.api_server --model gorilla-llm/gorilla-openfunctions-v2
env OPENAI_API_KEY=<KEY> OPENAI_BASE_URL="http://0.0.0.0:8000/v1" tool_sandbox --agent Gorilla -s wifi_off
```

来源：`README.upstream.md:57-90`；`TEST_SCENARIO_NAMES` 见 `official-code/tool_sandbox/cli/utils.py:104-111`。内置冒烟场景只有 3 个：`send_message_with_contact_content_cellular_off_multiple_user_turn`、其 `_10_distraction_tools` 与 `_3_distraction_tools_arg_description_scrambled` 变体。

产物目录：每个场景写 `data/<agent>_<user>_<时间戳>/trajectories/<scenario>/` 下的 `conversation.json`、`execution_context.json`、`pretty_print.txt`，汇总写同层的 `result_summary.json`（含 git SHA）。来源：`README.upstream.md:63`、`official-code/tool_sandbox/common/scenario.py:131-213`、`official-code/tool_sandbox/cli/__init__.py:64-90`。

## 场景与里程碑的配置形态

场景不是数据文件而是 Python 代码：以 base 场景为初始设备状态，用 `ScenarioExtension` 追加消息、工具白/黑名单与里程碑。官方 README 给出的最小可读示例（`README.upstream.md:167-215`）是一个 `cellular_off` 场景，其里程碑用 `SnapshotConstraint(database_namespace=..., snapshot_constraint=snapshot_similarity, target_dataframe=pl.DataFrame({...}))` 描述"SETTING 库里 cellular 必须为 False"。

真实场景定义集中在四个文件，均以 `ScenarioExtension` 列表 + `named_*_scenarios()` 聚合函数的形式存在：

| 文件 | 行数 | 内容 |
| --- | ---: | --- |
| `official-code/tool_sandbox/scenarios/base_scenarios.py` | 252 | base 场景：初始世界状态、导入语句、agent 系统提示、用户模拟器 few-shot |
| `official-code/tool_sandbox/scenarios/single_tool_call_scenarios.py` | 1138 | 单工具调用场景 |
| `official-code/tool_sandbox/scenarios/multiple_tool_call_scenarios.py` | 5747 | 多工具调用场景（同时是 Canonicalization / State Dependency 的主要来源） |
| `official-code/tool_sandbox/scenarios/multiple_user_turn_scenarios.py` | 3170 | 多用户轮场景 |
| `official-code/tool_sandbox/scenarios/insufficient_information_scenarios.py` | 1657 | 信息不足场景（minefield 的主要来源） |
| `official-code/tool_sandbox/scenarios/user_simulator_few_shot_examples.py` | 414 | 用户模拟器 few-shot 示例（Demonstration 组件） |

## 本地保存范围

`official-code/` 收录上游 revision `c8571d7` 中与论文机制直接相关的全部 Python 代码、配置与官方测试，共 71 个文件、约 1.13 MB：

| 已纳入 | 说明 |
| --- | --- |
| `LICENSE`、`README.upstream.md`、`pyproject.toml` | 根许可、上游文档、打包与测试配置 |
| `tool_sandbox/common/` | 状态管理、里程碑评价、消息/工具转换、轨迹抽取（核心机制） |
| `tool_sandbox/tools/` | 34 个工具的实现（含状态依赖抛错点） |
| `tool_sandbox/scenarios/` | 场景定义与聚合、用户模拟器 few-shot |
| `tool_sandbox/roles/` | 三角色、执行环境、各模型 agent 适配器、用户模拟器 |
| `tool_sandbox/cli/`、`tool_sandbox/analysis/` | 命令入口与结果分析 |
| `tests/` | 官方单元测试全集（20 个测试模块） |

| 未纳入 | 原因 |
| --- | --- |
| 论文 PDF（20.2 MB） | 超出仓库体积约定；获取地址 <https://aclanthology.org/2025.findings-naacl.65.pdf> |
| `ACKNOWLEDGEMENTS`（141 KB）、`tool_sandbox/notebooks/` 三个 notebook、`.gitignore`、`.pre-commit-config.yaml` | 与机制无关的体积/开发环境噪声。注意：`LICENSE` 末尾声明子组件许可见 `ACKNOWLEDGEMENTS`，该文件未随包保存 |
| 运行产物 `data/`、模型权重、RapidAPI 响应缓存 | 运行期生成或需外部凭据 |
| 上游 `README.upstream.md` 之外的仓库外材料（如 arXiv 预印本 2408.04682） | 本包只固定正式发表版本 |

场景数据本身（1032 个场景的里程碑定义）以 Python 代码形式保留在 `tool_sandbox/scenarios/` 内，未做裁剪：一是 `scenarios/__init__.py:25-131` 的聚合入口依赖这四个模块，裁剪后入口即失效；二是其体量（约 0.54 MB）在整包预算内。基准里程碑是论文公开发布的评测内容，不属于需要隐藏的测试答案。
