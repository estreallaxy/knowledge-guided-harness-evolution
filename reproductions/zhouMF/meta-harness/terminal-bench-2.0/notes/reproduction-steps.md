# Meta-Harness 复现步骤与状态（周梦凡 / zhouMF）

本文件是**周梦凡个人复现任务**的权威步骤清单：按序复制命令即可重跑，每一步都标注产出、验收与当前状态。
规划背景与决策历史见 [`reproduction-plan.md`](reproduction-plan.md)，逐次运行的原始指标见 [`run-log.md`](run-log.md)，
结论与偏差见 [`reproduction-summary.md`](reproduction-summary.md)，与参考实现的代码差异见 [`adaptations.md`](adaptations.md)。

## 一、我的任务

来源：`CONTRIBUTING.md`、`docs/team-execution-plan.md` 阶段一、`reproductions/zhouMF/meta-harness/README.md`。

| 项 | 取值 |
| --- | --- |
| 任务 | 在隔离的个人工作区独立复现 Meta-Harness：维护代码、H0、配置、运行结果，并与其余四人对齐共同协议 |
| 目录 | `/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness/terminal-bench-2.0/` |
| 分支 | `zhouMF/self-evolution-branch` |
| 执行模型 / 优化模型 | `deepseek/deepseek-v4-flash`（共同协议固定） |
| H0 | `../code/reference_examples/terminal_bench_2/agents/baseline_kira.py`（= 共享参考快照，未修改） |
| 优化循环 | `../code/reference_examples/terminal_bench_2/meta_harness.py` |
| benchmark | `benchmarks/terminal-bench-2.0/`（只读）；本地任务集 `tb2-split-v1`（train 30 / dev 19 / test 40） |
| 阶段一附带的第二个交付物 | 2.1 方法知识：本人四个方向（指令与 Skill、上下文管理与压缩、规划与任务进度管理、模型选择与资源分配）各登记 2 篇论文并整理高价值方法与可用代码 |

验收口径（`docs/team-execution-plan.md` 验收一/二）：
H0 在 TB2 上有可复现的分数、trace、token、费用、时延且满足统一协议；从 H0 出发跑通初始化与至少一轮 trace 优化；
2.1 每个方向登记 2 篇论文并整理可用于迁移的方法与代码。

## 二、步骤总览

路径变量（每条新终端先执行）：

```bash
export REPO=/data1/users/zhouMF/knowledge-guided-harness-evolution
export BASE=$REPO/reproductions/zhouMF/meta-harness           # 基线目录（共享 code/）
export WS=$BASE/terminal-bench-2.0                            # 本 benchmark 工作区
export RD=$BASE/code/reference_examples/terminal_bench_2      # Meta-Harness runner
```

| 步骤 | 内容 | 状态 | 证据 |
| --- | --- | --- | --- |
| P0 | 三份个人配置 | ✅ 已完成 | `configs/{terminal-bench-2.0,h0,meta-harness}.yaml` |
| P1 | 环境打通（uv / 依赖 / 免 provider 单测） | ✅ 已完成 | `notes/p1-env-report.txt`；2026-10-12 复核 12/12 绿 |
| P1.5 | 生成 train/dev/test 本地任务集 | ✅ 已完成 | `/data1/users/zhouMF/benchmarks/tb2-split-v1`（30/19/40） |
| P2 | 执行模型 smoke（单题） | ✅ 已完成 | `run-log.md` R2：`bn-fit-modify` reward=1.0，320s |
| P3 | H0 基线（train × 2 trials） | ✅ 已完成 | `run-log.md` R3（`jobs/h0-baseline-r2`）：mean 0.6667，¥32.31 |
| P4 | 提议器接入（Claude Code → 本地网关 → deepseek） | ✅ 已完成 | `code-adaptation/scripts/claude_deepseek_gateway.sh`；提议器代码零改动 |
| P5 | 优化循环冒烟（四段证据） | ✅ 已完成 | `run-log.md` R4（`logs/p5-smoke/`），¥1.70 |
| P6 | 正式搜索（2 轮 / 3 候选 × 30 题） | ✅ 已完成 | `run-log.md` R5（`logs/p6-main/`），frontier 66.7%，¥30.39 |
| P7 | 汇总、偏差与同口径复核 | ✅ 已完成 | `notes/reproduction-summary.md` |
| P8 | 补 2 trials / 扩到 5 轮，做严格对比 | ⛔ 被余额阻塞 | DeepSeek 余额 ¥2.26（2026-10-12 实测） |
| P9 | 与其余四人交叉核对条件 | ⛔ 被访问权限阻塞 | 其余成员工作区为私有目录，且个人 notes 未推送到 `main` |

## 三、逐步命令

### P0 三份个人配置

产出：`configs/terminal-bench-2.0.yaml`、`configs/h0.yaml`、`configs/meta-harness.yaml`。
验收：字段覆盖 `configs/README.md` 的要求；凭据只写变量名，不写取值。**已就绪，无需重跑。**

### P1 环境打通

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh      # 系统 Python 3.10 不满足 >=3.12,<3.13，用 uv 自管解释器
source "$HOME/.local/bin/env"
cd "$RD" && uv sync                                  # harbor[modal,runloop]==0.18.0、litellm==1.84.10
uv run harbor run --help | head -40                  # 确认后端白名单与 -p/-i 行为
uv run --with pytest --no-sync pytest tests/ -q      # 免 provider 测试，应 12/12 绿
bash "$WS/code-adaptation/scripts/p1_env_check.sh"   # 一键环境报告 → notes/p1-env-report.txt
```

验收：单测全绿；`notes/p1-env-report.txt` 中网络与 docker 为 `PASS`。

### P1.5 生成本地任务集（只复制数据，不跑模型）

```bash
cd "$REPO"
python3 benchmarks/terminal-bench-2.0/prepare_dataset.py \
  --source benchmarks/terminal-bench-2.0/dataset \
  --output /data1/users/zhouMF/benchmarks/tb2-split-v1
```

预期 `30 train / 19 dev / 40 test`。重复执行只核验、不覆盖。封存 `test` 不参与提议、调参或知识检索。

### P2 执行模型 smoke（单题）

```bash
cd "$RD" && cp .env.example .env && $EDITOR .env      # 填 DEEPSEEK_API_KEY / DEEPSEEK_API_BASE，不入库
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash "$RD/scripts/run_local_docker.sh" agents.baseline_kira:AgentHarness full 1 1 -i bn-fit-modify
```

验收：拿到分数，并确认 provider 接受 `temperature=0.7` 与原生 `tools`。

### P3 H0 基线（train 全集，2 trials）

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
  bash "$RD/scripts/run_local_docker.sh" agents.baseline_kira:AgentHarness full 2 4 \
  > "$WS/notes/h0-baseline.log" 2>&1
python3 "$WS/code-adaptation/scripts/summarize_run.py" "$RD/jobs/<job_dir>" --append-to "$WS/notes/run-log.md"
```

验收：`runs/`（已 gitignore）与 `notes/run-log.md` 含逐题 task ID、reward、token、费用、时延、异常。
注：`-p` 生效时任务范围由本地目录决定，`hard/full` 只影响是否追加 `-i`，因此本地一律用 `full`。
另用 `scripts/h0_baseline_watch.sh` 在日志出现 `Insufficient Balance` 时立即熔断留档。

### P4 提议器接入（优化器侧，不改 H0）

```bash
bash "$WS/code-adaptation/scripts/claude_deepseek_gateway.sh" start   # litellm: Anthropic /v1/messages → deepseek
bash "$WS/code-adaptation/scripts/claude_deepseek_gateway.sh" status  # 期望：运行中 http://127.0.0.1:4000
```

做法：Claude Code CLI → 本地 Anthropic 兼容网关 → `deepseek-v4-flash`，`claude_wrapper.py` 与
`propose_claude()` 代码路径一行不改，只把提议模型从 Opus 换成 deepseek（偏差已登记）。

### P5 优化循环冒烟

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-smoke-v1 \
  bash "$WS/code-adaptation/scripts/run_meta_harness.sh" p5-smoke \
    --iterations 1 --trials 1 --skip-baseline --concurrent 4
```

验收：提议 → 校验 → 评测 → 记录四段都留证据（`agents/<候选>.py`、`logs/<run>/pending_eval.json`、
`jobs/<run>/smoke-*`、`jobs/<run>/evolve-*`、`logs/<run>/evolution_summary.jsonl`）。

### P6 正式搜索

```bash
HARBOR_TASK_PATH=/data1/users/zhouMF/benchmarks/tb2-split-v1/train \
HARBOR_TIMEOUT_SECONDS=10800 \
  bash "$WS/code-adaptation/scripts/run_meta_harness.sh" p6-main \
    --iterations 2 --trials 1 --skip-baseline --concurrent 8
```

说明：`--skip-baseline` 因为 Phase 0 会对 2 个基线各跑 30 题（约多花 ¥26），基线已在 P3 单独跑过。
每轮评测走 `scripts/run_eval.sh` + `TASK_SET=full`，任务范围由 `HARBOR_TASK_PATH` 决定。

### P7 汇总与复核

产出：`notes/run-log.md`（逐次运行）、`notes/reproduction-summary.md`（条件表、逐题对比、偏差、成本、待办）。
同口径复核用 `jobs/` 下每 trial 的 `result.json` 重算，只保留两边都计分的题。

## 四、一次性环境重检（2026-10-12）

| 检查 | 命令 | 结果 |
| --- | --- | --- |
| 免 provider 单测 | `uv run --with pytest --no-sync pytest tests/ -q` | ✅ 12 passed |
| H0 与共享参考一致 | `md5sum harness/h0/terminus-kira/agents/baseline_kira.py <我的副本>` | ✅ 同为 `2a6d57f5782037da70ffb279adab024e` |
| H0 无本地改动 | `git diff --stat HEAD -- .../agents/baseline_kira.py` | ✅ 无 diff |
| harbor / uv | `.venv/bin/python -c "import harbor"`、`uv --version` | ✅ harbor 0.18.0、uv 0.13.0 |
| docker | `docker version --format '{{.Server.Version}}'` | ✅ 24.0.2 |
| 提议器网关 | `curl -s -o /dev/null -w '%{http_code}' 127.0.0.1:4000/health/liveliness` | ✅ 200 |
| 任务集 | `ls .../tb2-split-v1/{train,dev,test}` | ✅ 30 / 19 / 40 |
| DeepSeek 余额 | `curl api.deepseek.com/user/balance` | ⚠️ ¥2.26（不足以再跑 30 题评测） |

## 五、未完成项与阻塞

| 事项 | 为什么重要 | 阻塞条件 | 解除后怎么做 |
| --- | --- | --- | --- |
| 严格对比：候选补 2 trials，或基线降到 1 trial | 现在两侧 trials 不一致（候选 1 / 基线 2），单题噪声即可吞掉 +3.6pt 的净增益，不能定性 | 余额 ¥2.26；单候选 1 trial 约 ¥10、2 trials 约 ¥20 | 充值后重跑 `p6` 的同一批候选到 2 trials，或把 `h0-baseline-r2` 降到 1 trial，再按同口径重算 |
| 搜索规模扩到论文默认 5 轮 | 2 轮无法判断搜索是否收敛 | 同上，且预算口径（step/token/重试）全组未定 | 固定预算字段后 `--iterations 5` |
| 与四人交叉核对条件 | 验收一要求"满足统一协议" | 其余成员工作区为 `0700` 私有目录，个人 notes 未推 `main`；他人结果不可读 | 各人把条件表/结果摘要推送到 `main` 或提供只读汇总后逐项比对 |
| 2.1 方法知识"可用代码" | 验收一要求"整理高价值方法与可用代码" | 无阻塞（离线可做） | 论文与官方代码已整理进 `knowledge/source-packets/`；离线可运行 demo 迁到 `reproductions/zhouMF/method-reproduction/`，见该目录 `README.md` |

## 六、产物索引

| 路径 | 内容 | 入库 |
| --- | --- | --- |
| `configs/*.yaml` | 三份个人配置 | 是 |
| `../code/` | Meta-Harness 上游副本；保持与参考实现一致，改动以补丁保存在 `code-adaptation/upstream-adaptation.diff` | 是 |
| `code-adaptation/` | 上游适配补丁、运行脚本、候选 harness 与提示模板 | 是 |
| `notes/` | 计划、步骤、运行记录、偏差、总结 | 是 |
| `results/` | 可审计的汇总（`summary.json`），逐题原始产物不入库 | 是（汇总）/ 否（原始） |
| `runs/`、`code/.../jobs/`、`code/.../logs/` | 原始日志、trace、逐题 result.json | 否（`.gitignore`） |
