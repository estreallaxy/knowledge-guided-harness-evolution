# 本地适配记录

按 `reproductions/zhouMF/meta-harness/README.md` 的要求，凡是"与 Claude/Anthropic 绑定的入口"
的适配，都在此登记，便于五人交叉核对时恢复可比条件。

## 路径约定

```bash
export BASE=/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness
export RD=$BASE/code/reference_examples/terminal_bench_2   # Meta-Harness runner（上游快照，保持原样）
export WS=$BASE/terminal-bench-2.0                         # 本 benchmark 工作区
```

- `code/` 内的上游快照保持与参考实现一致，**不直接落改动**；改动以补丁形式保存在
  [`../code-adaptation/upstream-adaptation.diff`](../code-adaptation/upstream-adaptation.diff)。
- 本节「已做改动清单」的文件列，除注明 `code-adaptation/` 者外，都相对 runner 目录 `$RD`。
- 本地新增的运行脚本在 [`../code-adaptation/scripts/`](../code-adaptation/scripts/)。

## 为什么 H0 无需改动

| 事实 | 位置 | 结论 |
| --- | --- | --- |
| `add_anthropic_caching()` 在模型名不含 `anthropic`/`claude` 时原样返回消息 | `anthropic_caching.py:22-24` | 换成 deepseek 后缓存层自动成为 no-op |
| `_model_name`、`_temperature`、`_reasoning_effort` 均来自 Harbor 基类 `Terminus2` | `agents/baseline_kira.py` 未定义这些属性 | 由 `HARBOR_MODEL` 与 `--ak` 注入，属配置面 |

因此 `agents/baseline_kira.py` **保持与参考实现一致，未做任何修改**。

## 已做改动清单

| 文件 | 改动 | 原因 | 是否影响 H0 / benchmark |
| --- | --- | --- | --- |
| `scripts/run_eval.sh` | 环境白名单加入 `docker` | 本地 docker 后端 | 否 |
| `scripts/run_eval.sh` | 新增 `HARBOR_TASK_PATH`，设置时改用 `-p <目录>`；未设置时保持 `-d terminal-bench@2.0` 原行为 | 本地 docker 不应在沙箱内重新下载数据集 | 否 |
| `meta_harness.py` | `MODEL` 改为 `os.environ.get("META_HARNESS_MODEL", "anthropic/claude-opus-4-6")` | 执行模型切到 deepseek，同时保留上游默认值便于对照 | 否（优化器侧） |
| `meta_harness.py` | `SMOKE_TEST_TASK` 改为 `os.environ.get("META_HARNESS_SMOKE_TASK", "extract-elf")` | 上游默认冒烟题 `extract-elf` 属封存 test 划分，拿它给候选打冒烟等于用测试题调开发；本地 `-p train` 模式下由环境变量换成 train 里的便宜题（用 `bn-fit-modify`） | 否（优化器侧） |
| `tests/test_meta_harness.py` | 新增 `test_shell_runner_supports_docker`，与既有 modal 用例对称 | 覆盖白名单改动 | 否 |
| `scripts/run_eval.sh` | 补可执行位（100644 → 100755） | **上游缺陷**：`tests/test_meta_harness.py:44,100` 直接执行该脚本（未走 `bash`），而无执行位时全新克隆必报 `Permission denied`，`AgentClassValidationTests.test_run_eval_rejects_invalid_class_before_harbor` 与整个 `TimeoutWiringTests` 都会失败 | 否 |
| `.env.example`（新增） | 凭据模板，取值留空 | 把 API key 的位置留出来 | 否 |
| `code-adaptation/scripts/run_local_docker.sh`（新增） | 本地 docker 一键入口 | 显式设置后端/模型/任务集，避免写进 `.env` | 否 |
| `code-adaptation/scripts/run_local_docker.sh` | 入口先 `cd` 到 runner 目录 | `uv run` 按 cwd 找 `pyproject.toml`；从仓库根用绝对路径调用时会选错环境，报 `No module named 'dotenv'` | 否 |
| `pyproject.toml` | `terminal-bench` 的 git source URL 改为 `harbor-framework/terminal-bench-1`，**rev 不变** | 上游把 Python 包仓库改名（`terminal-bench` 现为 tasks 仓库），原 URL 下取该 rev 报 `upload-pack: not our ref`，`uv sync` 直接失败 | 否 |

未改动：`agents/baseline_kira.py`、`agents/baseline_terminus2.py`、`anthropic_caching.py`、
`claude_wrapper.py`、`prompt-templates/`、`pyproject.toml`、`benchmarks/`。

> 更正：`pyproject.toml` 后来有过一次必要改动（见上表最后一行），原因是上游仓库改名导致
> 原 source URL 无法解析；改动只换 URL，`rev` 仍是论文固定的 `1a6ffa96…`。

## 离线验证记录（我的沙箱无网络/无 docker，只能做静态验证）

用假 `uv` / `timeout` 复刻 `tests/test_meta_harness.py` 的捕获手法，实跑 `$RD/scripts/run_eval.sh`，
确认改后 argv 形状与参考实现一致：

| 场景 | 实测结果 |
| --- | --- |
| `HARBOR_ENVIRONMENT` 缺省 | `-e runloop`，`uv run harbor run` 开头不变，`--ak temperature=0.7` 在 |
| `HARBOR_ENVIRONMENT=docker` | `-e docker` |
| `HARBOR_ENVIRONMENT=k8s` | 被白名单拒绝，且未生成任何运行命令 |
| 设置 `HARBOR_TASK_PATH` | 使用 `-p <目录>`，且不再出现 `-d terminal-bench@2.0` |
| 未设置 `HARBOR_TASK_PATH` | 回落到 `-d terminal-bench@2.0`，与参考实现一致 |

未验证（需你终端）：`uv sync` 是否成功、两组单测是否全绿、Harbor 0.18.0 是否支持 `-e docker`、
deepseek provider 是否接受 `tools` 与 `temperature` 参数。

## 一个刻意绕开的坑

`run_eval.sh` 的 dotenv 段用 `set -a; source .env`，会**覆盖** shell 环境。
若把 `HARBOR_ENVIRONMENT` / `HARBOR_MODEL` 写进 `.env`，
`tests/test_meta_harness.py` 中断言默认后端为 `runloop`、默认模型为参考实现取值的用例会失败。
所以：`.env` 只放凭据与可选路径；后端/模型由 `code-adaptation/scripts/run_local_docker.sh`
或 shell 显式 export。

## 待办：提议器替换（复现计划 P4）

`meta_harness.py:431-451` 的 `propose_claude()` 仍依赖 `claude_wrapper.py` 调 `claude` CLI。
deepseek 方案尚未落地，替换前 `--iterations` 大于 0 的循环无法跑通；H0 基线评测不受影响。

> 已解决，见下节：结论是**不需要改写提议器**。

## 提议器接入：保留 Claude Code，只换模型来源（复现计划 P4，2026-10-10）

目标是尽量贴近论文的提议器形态。上游 `propose_claude()` 调 `claude_wrapper.run()`，
后者拼出 `claude --dangerously-skip-permissions -p <prompt> --output-format stream-json
--verbose --model <model> --setting-sources "" --tools … --allowedTools … --disable-slash-commands
--strict-mcp-config --plugin-dir <空> --effort max`，并用 `env=os.environ.copy()` 起子进程。

因此做法是**保留 Claude Code CLI 作为提议器驱动**，只在它下面垫一个 Anthropic 兼容网关，
把请求转给 `deepseek-v4-flash`。改动量：零行 Python 改动，只加环境变量与一个本地服务。

| 项 | 取值 | 说明 |
| --- | --- | --- |
| Claude Code CLI | `@anthropic-ai/claude-code` 2.1.296 | 装在 `~/.local/node22`（该版本要求 Node ≥22，系统 Node 20 不满足） |
| 网关 | 本地 litellm 代理，`http://127.0.0.1:4000` | 独立 venv `~/.local/litellm-proxy`，**不装进 runner 的 .venv**，避免污染固定依赖 |
| 网关配置 | `~/.local/litellm-proxy/config.yaml` | `model_name: "*"` 兜底把所有请求映射到 `deepseek/deepseek-v4-flash`；`drop_params: true` |
| 启动脚本 | `code-adaptation/scripts/claude_deepseek_gateway.sh start\|stop\|status` | 从 runner 的 `.env` 读 `DEEPSEEK_API_KEY` |
| 提议器环境变量 | `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` | **不设** `ANTHROPIC_API_KEY`：`propose_claude()` 会把它 pop 掉 |
| 提议器代码 | `meta_harness.py`、`claude_wrapper.py` | **未改** |

### 实测证据（2026-10-10）

| 验证 | 结果 |
| --- | --- |
| `claude --help` 覆盖 wrapper 用到的全部参数 | `--effort`、`--output-format`、`--setting-sources`、`--plugin-dir` 等 11 项全部存在 |
| Anthropic 端点 `POST /v1/messages` | 200，返回 Anthropic 格式（含 `usage.input_tokens/output_tokens`），与 `claude_wrapper` 的解析口径一致 |
| `claude -p` 指向网关 | 成功；`--model opus` 被解析成 `claude-opus-5-5` 后由通配映射落到 deepseek |
| 工具调用 | 通过：模型实际调用 `Write` 写出了文件；`--tools` 里的 `Agent` 被 Claude Code 归一为内部 `Task`，不报错 |

### 必须记录的三点偏差

| 项 | 论文/参考实现 | 本工作区 | 影响 |
| --- | --- | --- | --- |
| 提议器模型 | Opus + `effort=max` | deepseek-v4-flash | 提议质量不可与论文直接比；机制一致、模型不同 |
| 中间层 | 无，Claude Code 直连 Anthropic | 多一层 Anthropic→OpenAI 兼容网关 | `drop_params: true` 会静默丢弃 deepseek 不支持的上游参数（如 cache_control）；行为差异需在结果里说明 |
| 提议成本口径 | Claude Code 报 Anthropic 列表价 | 该值对 deepseek 无意义 | 优化侧费用须用本地 token 数 × deepseek 单价重算，不能直接用 `claude_wrapper` 记录的 `total_cost_usd` |

## 与参考实现的偏差（交叉核对时须说明）

| 项 | 参考实现 | 本工作区 | 影响 |
| --- | --- | --- | --- |
| Sandbox 后端 | runloop | 本地 docker | 镜像构建、并发上限与超时行为可能不同 |
| 并发数 | 50 | 4（默认） | 墙钟时间不可直接比 |
| 执行模型 | `anthropic/claude-opus-4-6` | deepseek-v4-flash（按共同协议） | 分数不可与论文直接比 |
| 任务来源 | `-d terminal-bench@2.0` | 本地 `-p` 目录 | 任务内容相同，镜像获取路径不同 |
