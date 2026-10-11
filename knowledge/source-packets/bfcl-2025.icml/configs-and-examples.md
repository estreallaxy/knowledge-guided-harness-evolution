# Configs and examples

## 官方配置

BFCL 没有 YAML/JSON 式实验配置：全部设置分散在 Python 常量模块、`.env` 与 CLI 参数三处。下表列出与评测机制直接相关的入口。

| 设置 | 配置位置 | 关键内容 |
| --- | --- | --- |
| API key、端点、外部服务 | `official-code/bfcl_eval/.env.example` | 各模型厂商 key；`SERPAPI_API_KEY` 为 `web_search` 类目必需；本地/远端 OpenAI 兼容端点用 `LOCAL_SERVER_ENDPOINT`/`LOCAL_SERVER_PORT`（默认 `localhost:1053`）或 `REMOTE_OPENAI_BASE_URL`/`REMOTE_OPENAI_API_KEY`；可选 `WANDB_BFCL_PROJECT`。 |
| 项目根与输出目录 | `official-code/bfcl_eval/constants/eval_config.py:1-45` | `BFCL_PROJECT_ROOT` 决定 `result/`、`score/`、`data/` 与 `.env` 的位置；用 PyPI 安装时必须显式设置，editable 安装默认指向 BFCL 目录。 |
| 依赖与 Python 版本 | `official-code/pyproject.toml:5-53` | `requires-python = ">=3.10"`；跨语言评测依赖固定为 `tree_sitter==0.21.3`、`tree-sitter-java==0.21.0`、`tree-sitter-javascript==0.21.4`；另有 `numpy==1.26.4`、`pydantic>=2.8.2` 等。控制台入口 `bfcl = "bfcl_eval.__main__:cli"`。 |
| 测试类别与类别组 | `official-code/bfcl_eval/constants/category_mapping.py:1-88`、`TEST_CATEGORIES.md` | 可运行组：`all`、`all_scoring`、`single_turn`、`multi_turn`、`live`、`non_live`、`agentic`、`memory`、`web_search`、`python`、`non_python`；`format_sensitivity` 属不计分项。 |
| 总榜权重 | `official-code/bfcl_eval/eval_checker/eval_runner_helper.py:509-519`；变更记录见 `CHANGELOG.md:10-23` | `[10, 10, 10, 30, 40]` 对应 Live / Non-Live / Irrelevance / Multi-Turn / Agentic；V4 起从"每段 33%"改成该权重。未评估类别在汇总列中按 0 计。 |
| 默认提示与步数上限 | `official-code/bfcl_eval/constants/default_prompts.py:1-60` | `MAXIMUM_STEP_LIMIT = 20`（多轮单条对话的步数上限）；默认提示格式串 `ret_fmt=python&tool_call_tag=False&func_doc_fmt=json&prompt_fmt=plaintext&style=classic`。 |
| 类别到语言/返回格式 | `official-code/bfcl_eval/constants/type_mappings.py` | `GORILLA_TO_OPENAPI`/`GORILLA_TO_PYTHON` 等映射，决定函数文档里的类型名如何翻译成各语言与 JSON schema。 |
| 多轮执行后端映射 | `official-code/bfcl_eval/constants/executable_backend_config.py:1-47` | 12 个后端类到模块与函数文档的映射；`STATELESS_CLASSES=["MathAPI"]`；Memory 三类与 WebSearch 的状态默认不写入推理日志。 |
| 模型清单 | `official-code/bfcl_eval/constants/model_config.py`、`supported_models.py`；文档见 `SUPPORTED_MODELS.md` | `--model` 取值的唯一来源，同时决定使用哪个 handler 与是否走 FC 模式。 |
| 按 ID 生成子集 | `official-code/bfcl_eval/test_case_ids_to_generate.json.example` | `--run-ids` 时从项目根的 `test_case_ids_to_generate.json` 读取"类别 → 条目 ID 列表"，此时 `--test-category` 被忽略。 |

配置只能和论文版本、代码 revision、数据集与模型环境一起解释。论文 Table 1 的数字无法由本包独立复现：数据（`bfcl_eval/data/**`，含 `possible_answer` 真值）与其余模型适配器都不在来源包内。

## 官方流程入口

官方 README 把评测拆成"装环境 → 生成回复 → 评测打分"三步（`official-code/README.upstream.md`）。

```bash
# 1. 环境（官方给的是 conda + editable 安装）
conda create -n BFCL python=3.10 && conda activate BFCL
cd gorilla/berkeley-function-call-leaderboard
pip install -e .

# 2. 项目根与密钥
export BFCL_PROJECT_ROOT=/path/to/project        # PyPI 安装必填，editable 可选
cp bfcl_eval/.env.example .env                   # 填入所需模型的 API key

# 3. 生成模型回复（写入 result/<model>/BFCL_v4_<category>_result.json）
bfcl generate --model gpt-4o-2024-11-20-FC,claude-3-5-sonnet-20241022-FC \
              --test-category simple_python,parallel,live_multiple,multi_turn

# 4. 评测（写入 score/，并生成 data_overall/data_live/data_non_live/data_multi_turn 四个 csv）
bfcl evaluate --model MODEL_NAME --test-category TEST_CATEGORY
bfcl scores                                      # 以表格显示 data_overall.csv

# 5. 辅助查询
bfcl version                                     # 版本号（官方提示以 commit 为准）
bfcl test-categories                             # 列出类别与类别组
bfcl models                                      # 列出可用模型名
```

只跑部分条目时：

```bash
cp bfcl_eval/test_case_ids_to_generate.json.example ./test_case_ids_to_generate.json
bfcl generate --model MODEL_NAME --run-ids                       # --test-category 被忽略
bfcl evaluate --model MODEL_NAME --test-category TEST_CATEGORY --partial-eval
```

本地 OSS 模型与既有端点：

```bash
bfcl generate --model MODEL_NAME --test-category TEST_CATEGORY \
  --backend sglang --num-gpus 1 --gpu-memory-utilization 0.9   # 或 --backend vllm
bfcl generate --model MODEL_NAME --test-category TEST_CATEGORY --skip-server-setup  # 复用已起的端点
```

不走 CLI 的等价脚本入口（注意：脚本入口的多模型/多类别用**空格**分隔，CLI 用逗号）：

```bash
python -m bfcl_eval.openfunctions_evaluation --model MODEL_NAME --test-category TEST_CATEGORY
python -m bfcl_eval.eval_checker.eval_runner --model MODEL_NAME --test-category TEST_CATEGORY
```

## 机制自检的最小接入点

评测器本身是纯函数，不依赖模型调用，可在只有函数文档与案卷的情况下直接调用（本包只保留代码，未附数据，故以下均未在本地执行）：

| 接入点 | 签名要点 | 说明 |
| --- | --- | --- |
| `ast_checker(func_description, model_output, possible_answer, language, test_category, model_name)` | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:33-61` | 返回含 `valid` 与 `error_type` 的字典；`test_category` 决定并行/多函数/单函数分支。 |
| `multi_turn_checker(multi_turn_model_result_list_decoded, multi_turn_ground_truth_list, test_entry, test_category, model_name)` | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:9-129` | 逐轮 `state_checker` + `response_checker`；内部用 `execute_multi_turn_func_call` 真正跑 `func_source_code/` 的后端类，需要 `test_entry` 提供 `initial_config` 等字段。 |
| `agentic_checker(model_response, possible_answer_list)` | `official-code/bfcl_eval/eval_checker/agentic_eval/agentic_checker.py:6-40` | 单一函数名 `agentic_checker`，对归一化后的回复做词边界包含匹配，返回 `valid` 与 `error_message`。 |
| 端到端打分（含权重） | `official-code/bfcl_eval/eval_checker/eval_runner_helper.py:15`、`38`、`65`、`509-519` | `calculate_weighted_accuracy` / `calculate_unweighted_accuracy` / `calculate_percentage_weighted_accuracy`；需要 `result/` 下的模型输出文件，没有数据与输出时无法运行。 |

## 本地保存范围

`official-code/` 保存的是 BFCL 目录（上游 `berkeley-function-call-leaderboard/`）加仓库根 `LICENSE`，共 69 个文件、979 896 字节（约 0.93 MiB），无单文件超过 1 MB。

已纳入：`bfcl_eval/` 的评测机制核心（`eval_checker/` 全部检查器与执行后端类、`constants/` 全部配置模块、`model_handler/` 的抽象接口与两个代表性适配器及输出解析器、`scripts/` 五个脚本）、包级入口与工具模块，以及 `README.upstream.md`、`TEST_CATEGORIES.md`、`SUPPORTED_MODELS.md`、`CHANGELOG.md`、`CONTRIBUTING.md`、`LOG_GUIDE.md`、`pyproject.toml`、`.env.example`。

明确未纳入：

| 未纳入项 | 原因 |
| --- | --- |
| `bfcl_eval/data/**` | 全部数据集（问题与 `possible_answer` 真值答案），属规范要求剔除的数据集与测试答案类数据；因此本包不能独立跑完整评测。 |
| `agent-arena/evalutation/agent_ratings_V0.json`（33 MB）、`openfunctions/openfunctions-v1/gorilla_openfunctions_v1_train.json`（27 MB） | 旧快照里最大的两个数据文件，本次指定必须剔除。 |
| 仓库其他子项目 `agent-arena/`、`openfunctions/`、`gorilla/`、`raft/`、`goex/`、`.github/`、`.devcontainer/` | 与 BFCL 评测机制无关。 |
| `bfcl_eval/model_handler/api_inference/` 其余 26 个适配器（本包只留 `claude.py`、`openai_completion.py` 与 `__init__.py`） | 各家厂商接入样板，属可替换的外围；保留两个代表性实现用于说明接口形态。 |
| `bfcl_eval/model_handler/local_inference/` 全部 28 个文件 | vLLM/SGLang 本地推理后端，评测机制不依赖。 |
| `architecture_diagram.png` | 图片（规范要求剔除）。 |
| `knowledge/methods/bfcl/code/` 中 BFCL 目录以外的 420−69 个文件 | 只保留与 BFCL 机制相关的部分，其余为仓库其他项目。 |

一处需要说明的保留：`bfcl_eval/eval_checker/multi_turn_eval/func_source_code/long_context.py` 有 190 KB，是包内最大文件，但它不含类与方法定义，全部是长上下文类目用的列表数据（`WATCH_LIST_EXTENSION` 等）；`trading_bot.py`、`gorilla_file_system.py`、`vehicle_control.py`、`travel_booking.py` 四个多轮后端都在模块顶部 import 它，删掉会直接破坏 import，故按"够接入与验证的最小核心"保留。

论文正文（PDF/文本）、来源包元数据与旧方法页分别位于 `paper/`、`source-packet.json` 与只读的 `knowledge/methods/bfcl/`。
