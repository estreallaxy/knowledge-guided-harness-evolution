# Meta-Harness × Terminal-Bench 2.0 适配记录（王懿，阶段一）

记录时间：2026-10-07 ~ 2026-10-11。
适用范围：`reproductions/wangY/meta-harness/code/reference_examples/terminal_bench_2/`
（上游快照 commit `8123ccabe2b19fa1123090b2e5f1bacc20963ce8`，见 `code/UPSTREAM.md`）。

本文件说明**相对上游代码做了哪些改动、为什么改、怎么验证的**。凭据一律不写入仓库，只登记变量名。
H0 基线的运行过程、偏差与结果在 `reproductions/wangY/H0/terminal-bench-2.0/notes/stage1-summary.md`；
两条线共用同一入口与同一套执行条件。

---

## 1. 模型与端点

| 项 | 上游默认 | 本机实际 |
| --- | --- | --- |
| 执行模型 | `anthropic/claude-opus-4-6` | `deepseek/deepseek-flash` |
| 优化模型（提议 Agent） | Claude Code CLI + `--model opus` | Claude Code CLI 经 DeepSeek 的 Anthropic 兼容端点 |
| 端点 | Anthropic 官方 | `https://api.deepseek.com/v1`（OpenAI 兼容，litellm 用）/ `https://api.deepseek.com/anthropic`（claude CLI 用） |

团队约定的模型名 `deepseek-v4-flash` 在本机端点上对应的模型 id 是 `deepseek-flash`
（DeepSeek-V4.1-Flash：上下文 1,048,576 / 最大输出 393,216 / 支持图像输入与 function calling）。

补充实测（2026-10-09）：`GET /v1/models` 只列出两档——`deepseek-flash`（V4.1-Flash）
与 `deepseek-v4-pro`（V4-Pro）；`deepseek-v4-flash` 作为别名可直接调用，返回体的 `model`
字段同为 `deepseek-flash`。即团队内写 `deepseek-v4-flash` 或 `deepseek-flash` 是同一模型，两条实验线可比。
另：该模型默认 reasoning effort 为 `high`（`/v1/models` 的 `effort.default_level`），实测响应含
`reasoning_content`。

**litellm provider 前缀的实测差异（这决定了用哪个前缀）：**

- `deepseek/deepseek-flash`：原生接受 `reasoning_effort`，支持 tool calling。
- `openai/deepseek-flash`：报 `UnsupportedParamsError: openai does not support parameters: ['reasoning_effort']`。

代码中 `baseline_kira.py` 已带 `drop_params=True` 兜底，但仍统一使用 `deepseek/` 前缀。
`litellm` 的 deepseek provider 读取 `DEEPSEEK_API_KEY`。

**优化 Agent 路径的关键结论（实测）：** `claude_wrapper.build_command()` 会传
`--setting-sources ""`，这**禁用 settings.json**，provider 配置必须来自进程环境变量。
实测：继承 `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` 时 `claude -p` 正常返回；
清空这两个变量后返回 `Not logged in · Please run /login`。
因此 `meta_harness.py` 的 `run_cmd` / `harbor_run` 与 `claude_wrapper` 的子进程都要显式传播这两个变量。

## 2. 环境变量契约

`scripts/run_eval.sh` 会 `source <terminal_bench_2>/.env`（已被 `.gitignore` 忽略）；
`meta_harness.py` 顶部有 `load_dotenv(override=True)`。
变量名清单见 `code/reference_examples/terminal_bench_2/.env.example`。

| 变量 | 必需 | 说明 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 是 | litellm 的 deepseek provider 密钥 |
| `ANTHROPIC_BASE_URL` | 是 | claude CLI 端点，`https://api.deepseek.com/anthropic` |
| `ANTHROPIC_AUTH_TOKEN` | 是 | claude CLI 凭据 |
| `HARBOR_API_BASE` | 否 | 覆盖默认 `https://api.deepseek.com/v1` |
| `HARBOR_MODEL` | 否 | 覆盖默认 `deepseek/deepseek-flash` |
| `HARBOR_DATASET_PATH` | 否 | 设置后用 Harbor `-p` 读本地划分目录；不设则跑 registry 全量 89 题 |
| `HARBOR_ENVIRONMENT` | 否 | 默认 `docker`；可选 `runloop` / `modal` |

`.env` 只放凭据与端点，不要放 `HARBOR_MODEL` / `HARBOR_ENVIRONMENT` 等运行参数——
`run_eval.sh` 的 `source` 会覆盖外部环境，而 `tests/test_meta_harness.py` 依赖这些变量的默认值。

## 3. 代码改动清单（相对上游快照 `8123cca`）

| 文件 | 改动 | 原因 |
| --- | --- | --- |
| `pyproject.toml` | 移除 `[tool.uv.sources]` 中指向 git commit 的覆盖，改为从 PyPI 装 `terminal-bench==0.2.18` | 上游 pin 的 commit `1a6ffa9674b571da0ed040c470cb40c4d85f9b9b` 已从远端消失，`uv sync` 报 `not our ref`；版本号 pin 未变 |
| `meta_harness.py` | `MODEL` / `API_BASE` / `MODEL_INFO` 改为环境变量驱动，新增 `DATASET_PATH`、`EVAL_TASK_SET`、`N_EVAL_TASKS` | 上游硬编码 Anthropic 模型与全量数据集 |
| `meta_harness.py` | `run_cmd` / `harbor_run` 传播 `DEEPSEEK_API_KEY`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_BASE_URL`、`HARBOR_*` | 见第 1 节「优化 Agent 路径的关键结论」 |
| `meta_harness.py` | `propose_claude` 增加 provider 环境变量 preflight，缺失时提前返回 | 否则要等到子进程失败才发现，浪费一轮迭代 |
| `meta_harness.py` | `render_task_prompt` 的硬编码 `(Opus)` 与数据集描述改为按实际配置生成（新增 `_dataset_line()`） | 避免优化 Agent 读到错误的模型与规模 |
| `meta_harness.py` | 冒烟题由固定 `extract-elf` 改为按数据集解析（`_resolve_smoke_task()`，可用 `HARBOR_SMOKE_TASK` 覆盖） | 见第 5 节：`extract-elf` 属于 test 集，在 train 目录下不存在且会造成测试集泄漏 |
| `scripts/run_eval.sh` | 默认 `MODEL` → `deepseek/deepseek-flash`，默认 `HARBOR_ENVIRONMENT` → `docker`，`case` 接受 `docker` | 本机无云沙箱密钥，用 Harbor 内置的本地 Docker |
| `scripts/run_eval.sh` | 透传 `--ak api_base=... --ak model_info={...}`（仅当 `HARBOR_API_BASE` 非空）；新增 `HARBOR_DATASET_PATH` 支持（`-p`） | litellm 未登记 `deepseek-flash`，需显式上下文档位；划分数据集需从本地目录读取 |
| `scripts/run_eval.sh` | 恢复可执行位（`100644` → `100755`） | 仓库 vendoring 时丢了 exec 位，`tests/test_meta_harness.py` 直接执行该脚本会 `PermissionError` |
| `tests/test_meta_harness.py` | 默认环境断言 `runloop` → `docker`，新增模型/端点/数据集透传断言，测试环境变量清理补全 | 使测试反映本机适配后的行为 |
| `.env.example`（新增） | 登记 DeepSeek 相关变量名 | 上游无此文件 |

**不需要改动的部分（已核实）：**

- `anthropic_caching.py`：`add_anthropic_caching()` 对非 anthropic/claude 模型名直接 no-op。
- `agents/baseline_kira.py`：`_call_llm_with_tools` 已支持 `api_base` 与 `drop_params=True`；
  缓存在 deepseek 下自动跳过。H0 快照（`reproductions/wangY/H0/terminal-bench-2.0/code/terminus-kira/baseline_kira.py`）
  与该文件内容一致（sha256 `e06b9273…eb889`），自 vendoring 起未改动。
- `Terminus2._resolve_model_info` / `get_model_output_limit`：对未登记模型安全回退到显式传入的 `model_info`。

## 4. 本地验证记录

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 依赖安装 | `uv sync` | 退出码 0；`harbor 0.18.0` / `litellm 1.84.10` / `python-dotenv 1.2.2` / `tenacity 9.1.4` / `terminal-bench 0.2.18` |
| 单元测试 | `uv run python -m unittest discover -s tests -t .` | 17 passed |
| Agent 导入路径 | `uv run python meta_harness.py --validate-agent agents.baseline_kira:AgentHarness` | `OK` |
| tool calling | `litellm` + `deepseek/deepseek-flash` + 显式 `api_base` | `finish_reason: tool_calls`，正常 |
| claude CLI 路径 | `claude -p ... --model opus --setting-sources ""` | 继承 provider 环境变量时返回预期结果 |
| H0 基线端到端 | `scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 50`（实际并发 8） | 已完成，pass@2 = 0.70；过程、中断恢复与偏差见 `reproductions/wangY/H0/terminal-bench-2.0/notes/stage1-summary.md` |

**Docker 权限（已解决，2026-10-08）：** 曾因 `permission denied /var/run/docker.sock`
（socket 属 `root:docker 660`、用户不在 docker 组）阻塞；管理员执行 `usermod -aG docker` 后解决，
会话内组缓存未刷新时用 `sg docker -c '...'` 兜底。冒烟测试（sanitize-git-repo）已通过：
score 1.0、约 5 分 20 秒、$0.0678。

## 5. 数据集划分与阶段分离

仓库固定划分为 30 train / 19 dev / 40 test，清单见
`benchmarks/terminal-bench-2.0/split-v1.json`，说明见 `benchmarks/terminal-bench-2.0/README.md`。

本机已按仓库说明生成独立划分目录（在仓库外，不指向任何其他成员的工作区）：

```bash
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output /data1/users/wangY/benchmarks/tb2-split-v1
# → Prepared and verified ...: 30 train / 19 dev / 40 test
```

运行方式：`export HARBOR_DATASET_PATH=/data1/users/wangY/benchmarks/tb2-split-v1/train`

**冒烟题与测试集泄漏（已修）：** 上游 `SMOKE_TEST_TASK = "extract-elf"` 硬编码，
而 `extract-elf` 在固定划分里属于 **test** 集。两处问题：

1. 冒烟测试通过 `run_eval.sh` 调用 Harbor，而该脚本此时已带 `-p <train>`，train 目录下没有这道题 → 冒烟必然失败；
2. 即便目录里存在，冒烟产生的轨迹也会被优化 Agent 读到，违反「封存测试集不参与优化」。

改为 `_resolve_smoke_task()`：未配置本地划分时保持上游行为；配置了则优先取 train 集的
`sanitize-git-repo`（medium / 专家 30min，与 `extract-elf` 同档），否则取该目录下实际存在的题。
`HARBOR_SMOKE_TASK` 可显式覆盖。四种情形已实测：registry → `extract-elf`、
train → `sanitize-git-repo`、dev → `build-pov-ray`、test → `adaptive-rejection-sampler`。

**待与其他三人对齐的协议问题（尚未实现）：** 上游 `meta_harness.py` 用同一套任务做搜索与选择；
研究计划要求「优化器只看 train、dev 仅供选择候选、test 到最终评估才运行」。
当前代码只做到「可以指向任一划分目录」，搜索/选择/最终评估的阶段分离需要在四人确定协议后统一实现。
在此之前，复现运行固定 `HARBOR_DATASET_PATH=.../train`，保证 test 不被触碰。

## 6. 优化线状态（截至 2026-10-11：**尚未跑通**）

- Meta-Harness 优化循环（`uv run python meta_harness.py --iterations 5 --trials 2`）**未执行**：
  DeepSeek 账户余额仅剩约 ¥28（H0 线两次余额耗尽后），不足以支撑一轮 30 题 × 候选的搜索，
  等待团队预算确认后运行。目标配置与预算块见 `../configs/meta-harness.yaml`（上游默认值，待四人共同确定）。
- 运行时产物按协议落本地 `../runs/`、`../traces/`（已忽略），结果摘要落 `../results/summary.md|json`。
- `config_hash` 变更后两条实验线一起重跑，不混合不同配置的结果。
