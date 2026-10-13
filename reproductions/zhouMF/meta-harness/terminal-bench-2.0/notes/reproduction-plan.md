# Meta-Harness 独立复现计划（周梦凡 / zhouMF）

依据：`docs/team-execution-plan.md` 阶段一与验收一、`docs/research-plan.md` 2.1 与第 3 章、
`configs/README.md` 字段约定。

> 2026-10-12：**步骤清单与当前状态已收敛到 [`reproduction-steps.md`](reproduction-steps.md)**，
> 本文件保留为规划与决策历史（为什么这么改、当时怎么判断、哪些结论后来被推翻）。

工作区：`/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness/terminal-bench-2.0/`
（共享的 Meta-Harness 上游副本在同级 `../code/`，本目录只放 Terminal-Bench 2.0 的配置、脚本、notes 与结果）
分支：`zhouMF/self-evolution-branch`（本次按最新 main 重构）

## 一、验收目标

在隔离的个人工作区里，用 `deepseek-v4-flash` 跑通 Meta-Harness 复现，且结果可追溯：

1. H0 在 Terminal-Bench 2.0 上有可复现的分数、trace、token、费用与时延记录。
2. `meta_harness.py` 的优化循环至少完整跑通一轮（提议 → 校验 → 评测 → 记录）。
3. 关键实验条件与其余四人一致：同一 `split-v1.json`、同一 H0 起点、同一执行/优化模型、同一预算口径。

## 二、代码现状（已逐文件核对）

| 组件 | 文件 | 规模 | 作用 |
| --- | --- | --- | --- |
| H0 harness | `../code/reference_examples/terminal_bench_2/agents/baseline_kira.py` | 1185 行 | Terminus2 子类，原生 tool calling；比上游多的是 marker 轮询与多模态读图 |
| 优化循环 | `../code/reference_examples/terminal_bench_2/meta_harness.py` | 964 行 | baseline → smoke → 迭代{提议 → 校验 → Harbor 评测 → 记录指标} |
| 提议器 | `../code/reference_examples/terminal_bench_2/claude_wrapper.py` | 715 行 | **subprocess 调 `claude -p`（Claude Code CLI）**，解析 stream-json、统计 token、落盘日志 |
| 铺垫知识 | `../code/reference_examples/terminal_bench_2/.claude/skills/meta-harness-terminal-bench-2/SKILL.md` | 129 行 | 给提议器的先验；内容与模型无关，可移植 |
| Anthropic 缓存 | `../code/reference_examples/terminal_bench_2/anthropic_caching.py` | 62 行 | 给最近 3 条消息加 `cache_control` |
| 评测包装 | `../code/reference_examples/terminal_bench_2/scripts/run_eval.sh` | 约 100 行 | 调 `harbor run`，硬编码环境白名单与 `temperature=0.7` |
| 免 provider 测试 | `../code/reference_examples/terminal_bench_2/tests/test_meta_harness.py` | 211 行 | Agent 类校验、超时接线、循环签名 |

### 两条关键判断

1. **H0 不需要改代码就能换执行模型。** `add_anthropic_caching()` 开头即判断模型名，非
   `anthropic`/`claude` 直接原样返回（`anthropic_caching.py:22-24`），而 `_model_name`、
   `_temperature`、`_reasoning_effort` 都来自 Harbor 基类 `Terminus2`，由 `HARBOR_MODEL`
   与 `--ak` 注入。所以换 `deepseek-v4-flash` 是**配置变更**，H0 可保持与参考实现一致——
   正好满足"原始复现阶段不修改 H0"。
2. **必须改代码的是提议器。** `meta_harness.py:431-451` 的 `propose_claude()` 通过
   `claude_wrapper.run(...)` 调起 `claude` CLI（`model="opus"`、`effort="max"`，并显式
   `pop("ANTHROPIC_API_KEY")` 走订阅态）。deepseek 没有对应的 Claude Code CLI，
   这一层必须替换。提议器不属于 H0，替换不违反"不改 H0"的约束。

### 提议器的输出契约（`.claude/skills/.../SKILL.md`）

- 候选是 `agents/<snake_case_name>.py` **单文件**，类名必须是 `AgentHarness` 且继承 `Terminus2`；
  起点从 `agents/` 里现成实现复制，禁止 import 其他候选。
- 收尾写 `logs/pending_eval.json`（路径由任务提示给出），循环据此判断本轮是否有候选待评测。
- 强制约束：不得出现任何任务名或任务特定分支（"如果任务含 async 就…"属于违规）。
- **额外发现**：SKILL.md 第 92 行要求提议器"Launch 1 Agent subagent (subagent_type: general-purpose)"，
  即依赖 Claude Code 的子代理工具。这一条同样必须为 deepseek 方案改写。

### 运行产物不会被误提交

`../code/reference_examples/terminal_bench_2/.gitignore` 已忽略 `jobs/`、`logs/claude_sessions/`、
`logs/pending_eval.json`、`logs/frontier_val.json`；根 `.gitignore` 另覆盖 `logs/`、`runs/`、`traces/`。
已实测 `git status --ignored` 在该目录下无未忽略残留。

## 三、环境实测（2026-10-10 在服务器终端复核）

早前"本机无网络、无 docker、HOME 只读"的判断已过时，实测如下：

| 项 | 实测 | 结论 |
| --- | --- | --- |
| CPU / 磁盘 | 64 核；`/data1` 剩余 3.8T | 可跑本地 docker 并发，但要给 Harbor 容器留余量 |
| 网络 | `github.com`、`astral.sh` 均返回 200 | 可装 uv、可 `uv sync` |
| docker | 24.0.2，`overlay2`，data-root `/var/lib/docker`，免 sudo | **决策点 1 落定为本地 docker**，与 `configs/terminal-bench-2.0.yaml` 一致 |
| uv | 未安装 | P1 第一件事是装 uv |
| Python | 3.10.12，不满足 `>=3.12,<3.13` | 必须用 uv 自管解释器，不要用系统 python 跑测试 |
| harbor | 未安装（`import harbor` 失败） | 由 `uv sync` 装入 runner 的 venv |
| HOME | `/home/zhouMF`，可写 | uv 装到 `~/.local/bin`，venv 落在项目内 |
| 数据集 | 仓库内 vendored 快照（无 `.git`，有 `UPSTREAM_PROVENANCE.json`） | `prepare_dataset.py` 的 vendored 分支可用，无需联网下载；仍要生成 train/dev/test 三份本地目录 |

### 复核中发现的两处协议冲突（已在本分支修正）

| 冲突 | 事实 | 处理 |
| --- | --- | --- |
| smoke task 落在封存划分 | SETUP.md 推荐的 `extract-elf` 属 `test`（封存），拿它做 smoke 等于用测试题调开发 | `configs/terminal-bench-2.0.yaml` 的 `smoke_task` 改为 train 里的 `bn-fit-modify` |
| `hard` 子集跨划分 | `run_eval.sh` 的 `HARD_TASKS` 混了 train/dev/test（`cancel-async-tasks`∈test、`circuit-fibsqrt`∈dev 等） | 本地 `-p` 模式不走 `hard`，改用 `-p train 目录` + `-i <train 题>` |

## 四、分步计划

每一步都给出产出与验收标准。标注【我】= 我可在离线环境完成；【你】= 需要网络/docker/凭据。

| 步骤 | 内容 | 产出 | 验收 | 执行 |
| --- | --- | --- | --- | --- |
| P0 | 写三份配置：`configs/terminal-bench-2.0.yaml`、`configs/h0.yaml`、`configs/meta-harness.yaml` | 3 个 yaml | 字段覆盖 `configs/README.md` 要求；凭据只留变量名 | ✅ 已完成 |
| P1 | 环境打通：装 uv、`uv sync`、跑两组免 provider 单测 | `uv.lock`、单测输出 | `AgentClassValidationTests`、`TimeoutWiringTests` 全绿 | ✅ 已完成（12/12 绿，uv 0.13.0） |
| P2 | 执行模型适配：`HARBOR_MODEL=deepseek/deepseek-v4-flash` + provider 凭据，跑 smoke task `bn-fit-modify`（train；原 `extract-elf` 属封存 test，已弃用） | 1 条 trace + 分数 | 能拿到分数；记录 `temperature`、`reasoning_effort` 是否被 provider 接受 | 【你】（我出命令） |
| P3 | H0 基线评测：在 `split-v1.json` 的 train+dev 上跑 H0 | `runs/` 结果 + 逐题分数/token/费用/时延 | 与四人同条件；产出 `notes/h0-baseline.md` | 【你】（我出命令与汇总脚本） |
| P4 | 提议器接入：**保留 Claude Code**，垫本地 Anthropic 兼容网关映射到 deepseek（零 Python 改动） | 网关脚本 + 配置 + 差异说明 | `claude -p` 经网关能产出合法候选文件（`pending_eval.json` 链路闭合） | ✅ 已打通（配置），待 P5 端到端验证 |
| P5 | 优化循环冒烟：`--iterations 1 --trials 1` 在便宜子集上跑通一轮 | 1 轮迭代记录 | 提议 → 校验 → 评测 → 记录四段都留下证据 | 【你】 |
| P6 | 正式复现：`--iterations N` 默认搜索配置 | 完整结果与 trace | 满足共同协议；交叉核对条件一致 | 【你】 |
| P7 | 汇总与交叉核对：写 `notes/` 复现说明，与四人对比条件差异 | `notes/reproduction-summary.md` | 关键条件表 + 已知偏差 | 【我】起草，【你】补充运行数据 |

### 修订 2026-10-10 23:30（本轮续跑）

R3 首次基线（`jobs/h0-baseline/`）不可用：60 次 trial 里 56 次异常，全部是
`litellm.BadRequestError: DeepseekException - Insufficient Balance`，即 **DeepSeek 账户中途余额耗尽**，
与 harness、benchmark、docker 后端无关。异常集中在几分钟内，多数 trial 在 20–40s 就失败。

处理：

1. 复核账户余额已恢复（`/user/balance` 返回 `is_available: true`，`total_balance ¥99.40`），
   直连 `deepseek-v4-flash` 的 chat 与 tools 调用实测正常。
2. 重跑基线，job 名 `h0-baseline-r2`，条件与 R3 对齐（train 30 题 × 2 trials），
   并发由 4 提到 8 以缩短墙钟；并发只影响时延，不影响逐题分数。
3. 新增 `scripts/h0_baseline_watch.sh`：日志出现 `Insufficient Balance` 立即熔断并留档，
   避免再次整轮作废；job 结束后自动跑 `summarize_run.py` 追加到 `notes/run-log.md`。

另外，P4 的提议器链路已做端到端探针验证（不依赖循环）：
`claude -p --model opus --output-format stream-json --tools ...` 经 `127.0.0.1:4000` 网关
实际调用 `Write` 工具并写出文件，`total_cost_usd` 等 stream-json 字段均按 `claude_wrapper.py`
的解析口径返回。P5 现在只差循环本身的四段证据。

新增优化器侧改动 1 处：`meta_harness.py` 的 `SMOKE_TEST_TASK` 改为可用
`META_HARNESS_SMOKE_TASK` 覆盖（默认仍 `extract-elf`）。原因是上游默认冒烟题属封存 test 划分，
本地 `-p train` 模式下改为 `bn-fit-modify`。见 `notes/adaptations.md`。

## 五、决策点（阻塞后续，需先定）

1. ~~**Sandbox 后端**~~ **已定：本地 docker**。docker 24.0.2 可用，`run_eval.sh` 白名单已放开 docker 并支持 `HARBOR_TASK_PATH`。
   P1 已核实：harbor 0.18.0 的 `-e` 默认即 `docker`；`-p <目录>` 配 `-i <task_id/glob>` 正常过滤；`-p` 也接受单题目录。
2. ~~**提议器的 deepseek 落法**~~ **已定：保留 Claude Code CLI + 本地 Anthropic 兼容网关**。
   做法是 Claude Code → 本地 litellm `/v1/messages` → deepseek，提议器代码一行不改，
   与论文的提议器形态（skill、工具集、stream-json、`--effort max`）保持一致。
   实测证据与三点必须记录的偏差见 `notes/adaptations.md`。
3. **预算口径**：`step`／`tool call`／`token`／墙钟／重试的具体数值目前**全组未定**，
   我不擅自写死，配置里先按参考实现默认值给提案并标注"待五人确认"。

## 六、风险与注意事项

- 论文默认 89 题 × 2 trials × 并发 50，本地 docker 直接跑会拉爆机器；先按
  `extract-elf` → `hard` 30 题 → 全量的顺序上量（`SETUP.md` 推荐次序）。
- 封存 `test` 划分不参与提议、调参或知识检索，避免评估泄漏。
- 运行产物写 `runs/`，已在 `.gitignore` 中，不入库；`logs/`、`traces/` 同理。
- 任何与参考实现的偏差（模型、预算、后端）都要在结果里显式说明，交叉核对时才可恢复可比条件。
- 提议器替换属于优化器侧改动，不得触碰 H0 与 benchmark。

## 七、可执行 runbook（2026-10-10 复核后，按序复制即可）

先把路径固定成变量，后续命令直接用：

```bash
export REPO=/data1/users/zhouMF/knowledge-guided-harness-evolution
export BASE=$REPO/reproductions/zhouMF/meta-harness           # 基线目录（共享 code/）
export WS=$BASE/terminal-bench-2.0                            # 本 benchmark 工作区
export RD=$BASE/code/reference_examples/terminal_bench_2      # Meta-Harness runner
```

### P1 环境打通（约 10 分钟，含下载）

```bash
# 1. 装 uv（系统无 uv；Python 3.10 不满足 pyproject 的 >=3.12,<3.13）
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env"

# 2. 装依赖，由 uv 自管 3.12 解释器（会拉 harbor[modal,runloop]==0.18.0、litellm==1.84.10）
cd "$RD" && uv sync

# 3. 核实后端白名单与 -p/-i 行为（决策点 1 剩余的待验证项）
uv run harbor run --help | head -40

# 4. 两组免 provider 测试，此时应全绿
uv run python -m unittest -v tests.test_meta_harness.AgentClassValidationTests
uv run python -m unittest -v tests.test_meta_harness.TimeoutWiringTests

# 5. 一键环境报告：网络 / docker / uv / 后端 / 凭据
bash "$WS/code-adaptation/scripts/p1_env_check.sh"
```

验收：第 4 步两组测试全绿；`notes/p1-env-report.txt` 中网络与 docker 为 `PASS`。

### P1.5 生成 train/dev/test 本地任务集（只复制数据，不跑模型）

```bash
cd "$REPO"
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output /data1/users/zhouMF/benchmarks/tb2-split-v1
```

预期输出 `30 train / 19 dev / 40 test`。重复执行只核验、不覆盖。

### P2 执行模型 smoke（单题，先证明链路通）

先建凭据文件（不入库）：

```bash
cd "$RD" && cp .env.example .env && $EDITOR .env   # 填 DEEPSEEK_API_KEY / DEEPSEEK_API_BASE
```

再跑 train 里的便宜任务。注意 `extract-elf` 属封存 test，不要用：

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash "$RD/scripts/run_local_docker.sh" agents.baseline_kira:AgentHarness full 1 1 -i bn-fit-modify
```

`-p` 与 `-i` 的组合已实测有效（oracle 验证只用 `-p train` + `-i bn-fit-modify` 跑了 1 题），
无需退化成单题目录写法。

验收：拿到分数，并确认 provider 接受 `temperature=0.7` 与 `tools`。

### P3 H0 基线（train 全集）

**`-p` 生效时任务范围由本地目录决定，`hard/full` 只影响是否追加 `-i`**；
`hard` 的 30 个 id 跨 train/dev/test，因此本地模式一律用 `full`：

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash "$RD/scripts/run_local_docker.sh" agents.baseline_kira:AgentHarness full 2 4 \
  > "$WS/notes/h0-baseline.log" 2>&1
```

产出 `runs/`（已 gitignore）：逐题 task ID、分数、token、费用、时延，汇总到 `notes/h0-baseline.md`。

job 结束后把逐题指标转成可入库记录（`jobs/` 不入库，必须转写）：

```bash
python3 "$WS/code-adaptation/scripts/summarize_run.py" \
  "$RD/jobs/<job_dir>" --append-to "$WS/notes/run-log.md"
```

`notes/run-log.md` 汇总每次运行的实验条件、逐题 reward、token、费用、墙钟与异常，
字段对齐 `configs/meta-harness.yaml` 的 `records.fields`。

### P4–P6 优化循环（P4 需先写代码）

1. P4：把 `meta_harness.py` 的 `propose_claude()` 调用面换成 deepseek 提议器（决策点 2 三选一）。
2. P5：`uv run python meta_harness.py --iterations 1 --trials 1`，确认"提议 → 校验 → 评测 → 记录"四段都有产物。
3. P6：跑正式轮数，结果与 trace 落 `runs/`。

`meta_harness.py` 内部用 `$RD/scripts/run_eval.sh` + `TASK_SET=full` 做每轮评测，
只要 `HARBOR_TASK_PATH` 指向 `tb2-split-v1/train`，优化循环的评测会自动落在 train 30 题上，
不需要再改优化器代码。冒烟时建议 `--iterations 1 --trials 1 --skip-baseline`。

### 已就绪 / 未就绪一览

| 项 | 状态 |
| --- | --- |
| 三份配置 P0 | ✅ 已就绪 |
| docker 后端、runner 适配、单测 | ✅ P1 实跑通过：12/12 测试绿，`harbor run --help` 确认 `-e docker` |
| uv 与依赖、harbor | ✅ uv 0.13.0 + `uv sync` 成功（harbor 0.18.0、litellm 1.84.10） |
| train/dev/test 本地任务集 | ✅ 已生成 `/data1/users/zhouMF/benchmarks/tb2-split-v1`（30/19/40，已校验 manifest） |
| docker 端到端链路 | ✅ `oracle` agent 在 `bn-fit-modify` 上 reward=1.0，1m12s，无异常；任务镜像构建、`-p`+`-i` 过滤、判分器均正常 |
| 上游依赖可达性 | ⚠️ 需改 source URL（仓库改名），`rev` 未变；见 `notes/adaptations.md` |
| deepseek 凭据 | ❌ 待填 `.env`（仅本人填写，不入库）——**当前唯一阻塞 P2 的事项** |
| 提议器接入（Claude Code + 网关） | ✅ 已打通并实测：`claude -p` 经网关落到 deepseek，工具调用正常；提议器代码未改 |
| 预算口径（step/token/重试） | ❌ 全组未定，配置中为提案值 |

> 上表为 2026-10-10 09:5x 的快照，已被下一节取代。

### 当前状态（2026-10-10 23:3x 续跑后）

| 项 | 状态 |
| --- | --- |
| P0 配置 | ✅ 三份 yaml 就绪 |
| P1 环境 | ✅ uv 0.13.0、harbor 0.18.0、litellm 1.84.10；12/12 单测绿（含 `SMOKE_TEST_TASK` 改动后复跑） |
| P1.5 任务集 | ✅ `/data1/users/zhouMF/benchmarks/tb2-split-v1`（train 30 / dev 19 / test 40） |
| P2 执行模型 smoke | ✅ `deepseek/deepseek-v4-flash` 驱动 H0，`bn-fit-modify` reward=1.0，320s，接受 `temperature=0.7` 与 tools |
| P3 H0 基线 | ✅ 首次因账户余额耗尽作废；`h0-baseline-r2` 重跑成功（train × 2 trials，并发 8，2h19m），mean 0.6667，花费 ¥32.31。见 `notes/run-log.md` 的 R3 |
| P4 提议器 | ✅ 网关 + Claude Code CLI 打通，`claude -p` 探针实际写出文件；`run_meta_harness.sh` 一键入口就绪 |
| P5 循环冒烟 | ✅ 2026-10-11 01:50 跑通，四段证据齐全（提议 13m14s → 校验 3m48s → 评测 6m14s → 记录）；候选 `deadline_aware_delivery`，4 题冒烟集 avg=100%，真实花费 ¥1.70。见 `notes/run-log.md` 的 R4 |
| P6 正式搜索 | ✅ 2026-10-11 02:23→06:24 跑完 2 轮（3 个候选 × 30 题 × 1 trial），frontier=`enforced_final_state_audit` @ 66.7%，真实花费 ¥30.39。见 `notes/run-log.md` 的 R5 |
| P7 汇总 | ✅ 初稿 `notes/reproduction-summary.md`（条件表、逐题对比、偏差、成本、待办） |
| 预算口径 | ❌ 全组未定；`max_wall_clock_sec_per_task` 提案 900s，本地实际受 harbor 任务自带超时约束 |
