# 赵星源 · Meta-Harness 复现说明

本文件是**供审阅与复核的**复现说明。逐日的工作细节、证据与未提交改动清单在服务器上的个人日志里（仓库外，不提交）：

- `/data1/users/zhaoXY/progress-log.md`（做到哪了、下一步）
- `/data1/users/zhaoXY/personal-notes.md`（未解决的阻塞项）
- `/data1/users/zhaoXY/adaptation-record.md`（对参考实现的每处改动及理由）

---

## 一、当前状态（2026-10-11）

| 项 | 状态 |
| --- | --- |
| H0 在 train 划分上的 baseline | ✅ **已完成**，见第三节 |
| Meta-Harness 首轮 + 定向复验 | ✅ **已完成**（候选 65.0%，判无显著差异），见第四节 |
| 独立复现（阶段一验收项） | TB2 复现侧完成，待审阅复核；知识收集已按 SourcePacket 范式入库（6 个来源包，见 `knowledge/README.md`） |
| 沙箱后端 | 本地 Docker（已打通，89 个任务镜像本机全量缓存） |
| 配置 | `terminal-bench-2.0/configs/` 三份已就位 |

## 二、相对参考实现的改动

共 14 处，全部记录在 `adaptation-record.md`，按影响面分三类：

| 类别 | 改动 | 说明 |
| --- | --- | --- |
| **运行条件适配** | 依赖源修复、执行位补齐、模型改由 `HARBOR_MODEL` 指定、数据集改由 `HARBOR_DATASET_PATH` 指定、沙箱白名单放行 `docker`、冒烟题改按挂载划分解析 | 为把参考实现接到本线的冻结运行条件所必需，不是实现选择 |
| **优化器重写** | `propose_claude()`（绑死 Claude Code CLI）→ `litellm_proposer.py`（进程内 litellm 直调） | 要求的优化模型是 `deepseek-v4-flash`，CLI 路径无法指向任意 provider |
| **工程便利** | `RUNS_DIR` 改为环境变量可覆盖；冒烟题可用环境变量显式覆盖 | `RUNS_DIR` 未设置时行为不变 |

**未改动**：`agents/baseline_kira.py`（H0）、`agents/baseline_terminus2.py`、`prompt-templates/terminus-kira.txt`、`claude_wrapper.py` —— 均与上游 HEAD 逐字节一致（sha256 核对过）。`tests/test_meta_harness.py` 只在末尾新增 `SmokeTaskResolutionTests`（7 项，覆盖冒烟题解析），原有测试未改。

## 三、H0 baseline 结果（train 划分）

| 项 | 值 |
| --- | --- |
| 规模 | 30 题 × 2 次 = 60 trial |
| **通过率** | **40/60 = 66.7%** |
| 逐题 | 18 题两次全过 / 4 题部分 / 8 题两次全败 |
| 墙钟 / 费用 | 113 分钟 / **$10.13** |
| tokens | 281.8M in / 6.04M out |

失败构成（20 个 trial）：`AgentTimeoutError` 10、**真答错** 7、`VerifierTimeoutError` 3。

> ⚠️ **复核的两个前提**
>
> 1. **`VerifierTimeoutError`（3 个）不是 agent 能力失败**——是验证器跑满 900s 被切断，属评测侧开销。直接计入通过率会低估 H0；本线的登记口径见 `results/README.md`，与其他线路比较前须先确认口径一致。
> 2. **本次并发用 10，低于配置默认的 50**。原因是运行时宿主 load average 达 82（64 核，另有他人 49 个容器在跑）。10 个 `AgentTimeoutError` 中有多少是负载导致的假失败，需在低负载下复跑才能定量。**在这一点澄清前，本分数不宜与其他线路直接比较。**

## 四、Meta-Harness 首轮 + 定向复验（2026-10-09 / 10-11）

| 项 | 值 |
| --- | --- |
| 首轮 run（`evolve-1`） | 优化器（`deepseek-v4-flash`，`litellm_proposer.py`）产出候选 `kira_context_budget`：超 120k token 时压缩最老终端观测，未超预算逐字节不变 |
| 首轮通过率 | **65.0%**（同批 H0 66.7%、terminus2 61.7%；相对「两基线逐题最优」68.3% 为 −3.3pp）；候选评估 $11.36 + 优化器 $0.17 |
| 定向复验（`confirm5`） | 4 题 × 5 次 × 两臂：gcode 0/5 vs 0/5、make-mips 0/5 vs 0/4、mcmc 4/5 vs 5/5、raman 1/5 vs 0/5；合计 $12.01（10-11 低负载补跑收尾） |
| **结论** | 按 `runs/confirm5/run.sh` 事前写定的标准判定：**该机制对本环境无影响，首轮 −3.3pp 是 n=2 噪声**；gcode / raman 的超时是任务固有（低负载下依旧） |
| 产物 | `runs/jobs/evolve-1/`、`runs/jobs/confirm5-*/`、`runs/confirm5/{run.sh,resume-candidate.sh,summarize.py,load-trace.log}` |

逐题对照与成本明细见 `terminal-bench-2.0/results/README.md`。

## 五、可复现的运行方式

环境变量从 shell 传入，**不要写进 `.env`**（`.env` 只放 key，见 `personal-notes.md` 第 2 条）。

```bash
export PATH="$HOME/.local/bin:$PATH"
cd /data1/users/zhaoXY/knowledge-guided-harness-evolution/reproductions/zhaoXY/meta-harness/code/reference_examples/terminal_bench_2

export HARBOR_MODEL="deepseek/deepseek-v4-flash"
export HARBOR_ENVIRONMENT=docker
export HARBOR_DATASET_PATH=/data1/users/zhaoXY/benchmarks/tb2-split-v1/train
export RUNS_DIR=/data1/users/zhaoXY/knowledge-guided-harness-evolution/reproductions/zhaoXY/meta-harness/runs
export SMOKE_TEST_TASK=fix-code-vulnerability   # 可省略：未设置时按挂载划分自动解析（默认即此题）

# H0 baseline（本次实跑的命令）
bash scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 10 \
  --job-name h0-train-baseline --jobs-dir "$RUNS_DIR/jobs" -y

# 免 API 回归测试（应 51 项全过）
uv run python -m unittest tests.test_meta_harness tests.test_litellm_proposer

# 最便宜的链路自检（不调 LLM）
uv run harbor run --agent oracle -p "$HARBOR_DATASET_PATH" -i fix-code-vulnerability \
  -e docker -n 1 --n-attempts 1 --job-name oracle-check --jobs-dir "$RUNS_DIR/jobs" -y
```

**注意**：`run_eval.sh` 直跑时不会自己读 `RUNS_DIR`，必须显式传 `--jobs-dir`；只有经 `meta_harness.py` 调用时才会自动带上。

## 六、副本现状与本副本差异（2026-10-13 实测，供复核）

**副本清点**：TB2 复现副本现为 **5 份**（`reproductions/{zhouMF,zhaoXY,wangY,liYK,liJW}/meta-harness/code/reference_examples/terminal_bench_2/`）；原共享 H0（仓库根 `harness/h0/terminus-kira`）已随 2026-10-11 重组移除，H0 改为每人的 `reproductions/<成员>/H0/terminal-bench-2.0/code/terminus-kira/`。

**起点同源已复核 ✅**：五份 H0 `baseline_kira.py` 的 sha256 **全为 `e06b9273…`**，逐字节一致（2026-10-13 复测）。

阶段二起五条线路独立复现，副本之间的适配差异属预期（各线路自行选择修法）。下表是本副本与另外四份副本的实测差异（共 5 份），供复核时定位：

| 项 | 本副本 | 另外四份副本（2026-10-13 实测） |
| --- | --- | --- |
| 依赖安装 | `laude-institute`（同 rev `1a6ffa96`） | zhouMF / liYK / liJW 仍指向 `harbor-framework`（该远端已无此 ref，`uv sync` 直接失败）；wangY 改走 PyPI pin `terminal-bench==0.2.18` |
| `run_eval.sh` 执行位 | 755 | zhouMF / liYK / liJW 为 644 |
| 执行模型 | 读 `HARBOR_MODEL` | zhouMF / liYK / liJW 仍硬编码 `anthropic/claude-opus-4-6`；wangY 亦读 `HARBOR_MODEL` |
| 沙箱白名单 | 放行 `docker` | zhouMF / liYK / liJW 仅 `runloop\|modal`；wangY 亦放行 `docker` |
| 冒烟题 | 按挂载划分自动解析（首选 train 集 `fix-code-vulnerability`） | zhouMF / liYK / liJW 仍硬编码 `extract-elf`（test 集任务）；wangY 同为本副本做法 |

**跨线比较前须确认的两个口径**：`VerifierTimeoutError` 的计分方式、并发取值在高负载下的可执行性——两条目前都无仓库文档规定；本副本的实际取值与偏差见第三节。

**后端选型**：本线路已实测收敛为本地 Docker（89 个任务镜像全量缓存），不依赖云沙箱账号。

## 七、产物位置

| 内容 | 路径 | 是否提交 |
| --- | --- | --- |
| 原始运行产物 | `runs/jobs/<job>/`、`runs/logs/` | ❌ 本地（`.gitignore` 已挡） |
| 机器可读摘要 | `runs/h0-train-baseline-summary.json` | ❌ 本地 |
| 配置 | `terminal-bench-2.0/configs/*.yaml` | ✅ |
| 本说明 | `terminal-bench-2.0/notes/README.md` | ✅ |
| 结果摘要（交叉核对入口） | `terminal-bench-2.0/results/README.md` | ✅ |
