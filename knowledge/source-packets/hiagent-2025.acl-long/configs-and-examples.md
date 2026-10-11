# Configs and examples

行号以本地保存的 `official-code/` 为准。配置只能和论文版本、代码 revision、AgentBoard 环境与数据一起解释；论文中的数值不能由单个 YAML 独立复现。

## 官方实验配置

上游把四套 HiAgent 运行配置放在 `eval_configs/hiagent/`，每套一个 YAML，包含 `run` / `agent` / `llm` / `env` 四段。四套的 `agent` 段完全相同（`name: ContextEfficientAgent`、`memory_size: 100`、`need_goal: True`、`use_parser: True`），差异只在 `env.pddl.game_name`、`env_num_per_task` 与 `init_prompt_path`。

| 配置文件 | `env.pddl.game_name` | `env_num_per_task` | 实际加载的提示资产 | 对应论文任务 |
| --- | --- | --- | --- | --- |
| `official-code/eval_configs/hiagent/blocksworld.yaml` | `[blockworld]` | 20 | `agentboard/prompts/VanillaAgent/pddl_vanilla_prompt.json` | Blocksworld（Table 1） |
| `official-code/eval_configs/hiagent/gripper.yaml` | `[gripper]` | 20 | `agentboard/prompts/ContextAgent/pddl.json` | Gripper（Table 1） |
| `official-code/eval_configs/hiagent/tyreworld.yaml` | `[tyreworld]` | 10（`problem_index: [2..9]`） | `agentboard/prompts/ContextAgent/pddl.json` | Tyreworld（Table 1–3、Table 4） |
| `official-code/eval_configs/hiagent/barman.yaml` | `[barman]` | 20 | `agentboard/prompts/ContextAgent/pddl_wretrieval.json` | Barman（Table 1） |

每个 YAML 内还带有完整的 `env.jericho` 段（20 个 Z-machine 游戏、`ContextAgent/jericho.json`），因此 Jericho 实验用同一批 YAML 以 `--tasks jericho` 启动，没有单独的 jericho 配置文件。

配置要点与陷阱：

- `agent.name` 在四个 YAML 中都写成 `ContextEfficientAgent`（`blocksworld.yaml:11`），但注册表里只有 `ContextEfficientAgentV2`（`agentboard/agents/cme_final.py:21`）。实际生效值来自命令行 `--agent`（`agentboard/eval_main.py:122-125`），用官方脚本运行时必须传该参数。
- `run.max_num_steps` 在 YAML 中是 30（`blocksworld.yaml:2`），但 `eval_main.py:73` 无条件用命令行值覆盖，官方脚本传 50。
- `agent.memory_size: 100` 与论文无关（论文未报告该超参），它是 `memory[-memory_size:]` 的窗口上限（`agentboard/agents/cme_final.py:222`）。
- 是否启用 Observation Summarization 由 shell 环境变量 `EVALTASK` 决定，而不是 YAML：名字里含 `gripper` 或 `blocksworld` 时走"不摘要"分支（`agentboard/agents/cme_final.py:115-120`）。做消融或换任务时必须改这个变量。
- `init_prompt_path` 里的 `${PROJECT_PATH}` 由 `eval_main.py:45-51` 的 YAML constructor 展开，必须先在环境里导出。

## 官方流程入口

| 步骤 | 入口 | 说明 |
| --- | --- | --- |
| 1. 建环境 | `official-code/setup.sh` | `pip install -r requirements.txt`，再装 PDDL/Jericho/ALFWorld 依赖；WebShop 分支会构建检索索引（本包未纳入）。需 `conda create -n hiagent python=3.8.18` 与可用 CUDA。 |
| 2. 取 NLTK 数据 | `official-code/download_nltk.py` | 仅 `nltk.download('punkt')` 与 `punkt_tab`。 |
| 3. 配密钥 | `agentboard/.env`（未纳入本包） | 上游 README 要求 `PROJECT_PATH` 与 `OPENAI_API_KEY`；`eval_main.py:97` 调 `load_dotenv()` 读取。 |
| 4. 跑评测 | `official-code/evaluate_model.sh` | 单文件启动脚本，见下。 |
| 5. 看结果 | `{log_path}/all_results.txt` 与逐 sample 记录 | 由 `SummaryLogger` / `TaskLogger` 写出；这两个模块未纳入本包。 |

上游 README 未给出测试命令，也没有任何测试套件；唯一的"运行示例"就是 `evaluate_model.sh`。

## 可复制命令

官方脚本原文（`official-code/evaluate_model.sh:1-17`）：

```bash
export PROJECT_PATH='[Project Path Here]'
export MODEL="gpt-4-turbo"
export STEP=50
export AGENT="ContextEfficientAgentV2"
export EVALTASK="blocksworld"

python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/blocksworld.yaml \
    --tasks pddl \
    --model gpt-4-turbo \
    --log_path ./logs/hiagent/analysis/"${AGENT}_${MODEL}_${STEP}" \
    --project_name none \
    --baseline_dir ./data/baseline_results \
    --max_num_steps 50 \
    --memory_size 100 \
    --agent ContextEfficientAgentV2
```

换成别的任务时需要同时改三处，否则跑出来的不是论文设置：

```bash
# Tyreworld（论文 Table 1/2/3/4 的环境）
export EVALTASK="tyreworld"        # 该任务不在 "gripper/blocksworld" 白名单里，摘要会打开
python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/tyreworld.yaml \
    --tasks pddl --model gpt-4-turbo --agent ContextEfficientAgentV2 \
    --max_num_steps 30 --memory_size 100 \
    --log_path ./logs/hiagent/tyreworld --baseline_dir ./data/baseline_results

# Jericho（复用任意 YAML 中的 env.jericho 段）
export EVALTASK="jericho"
python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/blocksworld.yaml \
    --tasks jericho --model gpt-4-turbo --agent ContextEfficientAgentV2 \
    --max_num_steps 30 --memory_size 100 \
    --log_path ./logs/hiagent/jericho --baseline_dir ./data/baseline_results
```

以上命令是从代码读出的等价写法，**在本仓库未执行**（缺 AgentBoard 环境与数据，见下）。

## 前置数据与外部依赖（本包未纳入）

| 依赖 | 上游位置 | 说明 |
| --- | --- | --- |
| AgentBoard PDDL 环境 | `agentboard/environment/pddl_env/` | 26M `agentboard/environment/` 的一部分，含 pddlgym 与领域定义，已剔除。 |
| WebShop 环境与 chromedriver | `agentboard/environment/WebShop/` | 含 16M 二进制，已剔除；HiAgent 的五个任务不使用它。 |
| 任务标注 | `${PROJECT_PATH}/data/pddl/*.jsonl`、`data/jericho/test.jsonl` | 需按 AgentBoard 说明另行下载，未纳入。 |
| baseline 结果 | `${PROJECT_PATH}/data/baseline_results` | 供 wandb 对照，未纳入。 |
| GPT-4 访问 | `OPENAI_API_KEY` | 论文使用 `gpt-4-turbo`，同时充当 policy 与 summarizer。 |

## 本地保存范围

`official-code/` 共 26 个文件、248K，覆盖"够接入与验证的最小核心"：

| 已纳入 | 内容 |
| --- | --- |
| 机制实现 | `agentboard/agents/cme_final.py`（ContextEfficientAgentV2）、`agentboard/agents/summarize.py`（TrajectorySummarizer） |
| 接口与装配 | `agentboard/agents/base_agent.py`、`agentboard/agents/__init__.py`、`agentboard/common/registry.py`、`agentboard/llm/openai_gpt.py`、`agentboard/llm/__init__.py` |
| 对照基线 | `agentboard/agents/vanilla_agent.py`（STANDARD） |
| 驱动循环 | `agentboard/eval_main.py`、`agentboard/tasks/pddl.py`、`agentboard/tasks/base_task.py`、`agentboard/tasks/__init__.py` |
| 提示资产 | `agentboard/prompts/prompt_template.py`、`prompts/ContextAgent/{pddl.json,pddl_wretrieval.json,jericho.json}`、`prompts/VanillaAgent/pddl_vanilla_prompt.json` |
| 配置与脚本 | `eval_configs/hiagent/*.yaml`（4 套）、`evaluate_model.sh`、`setup.sh`、`requirements.txt`、`download_nltk.py`、`README.upstream.md` |

| 已剔除 | 原因 |
| --- | --- |
| `agentboard/environment/`（26M） | 环境实现与二进制；含 WebShop、chromedriver、pddlgym、alfworld、browser_env、scienceworld 等 |
| `assets/`（996K） | 论文示意图与 PDF（`main.png`、`main.pdf`、`hiagent exp.png`），非机制 |
| `agentboard/utils/` 其余部分 | 3.2M 工具与环境耦合代码，含 1.35M `gpt2/tokenizer.json`、1.04M `vocab.json`、264K xlsx 测试表 |
| `agentboard/utils/logging/` | `logger.py`（32K，wandb/plotly 可视化与指标聚合）、`agent_logger.py`（2.5K 彩色日志）；两者是 AgentBoard 共享设施，`eval_main.py` 与 `tasks/pddl.py` 依赖它们，故本包内的驱动循环无法直接 import |
| 其他 baseline agent | `ours_agent.py`、`react_agent.py`、`custom_*.py` |
| 其他任务实现 | `tasks/{webshop,webbrowse,alfworld,babyai,scienceworld,tool,neural}.py` 与 `tasks/legacy/` |
| `.ipynb_checkpoints`、`.DS_Store`、`run_dev.log`、`logs/` | 缓存与编辑器产物 |

注意：由于 `agentboard/environment/` 与 `agentboard/utils/logging/` 都已剔除，且快照内 `agentboard/tasks/__init__.py:10-11` 引用了上游并不存在的 `pddl_structured`、`babyai_train`，本包**不可原地运行**；它用于阅读机制、对齐接口与准备接入，不是可执行环境。
