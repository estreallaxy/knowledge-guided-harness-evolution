# 赵星源 · Meta-Harness 复现说明

本文件是**给四人交叉核对看的**复现说明。逐日的工作细节、证据与未提交改动清单在服务器上的个人日志里（仓库外，不提交）：

- `/data1/users/zhaoXY/progress-log.md`（做到哪了、下一步）
- `/data1/users/zhaoXY/personal-notes.md`（未解决的阻塞项）
- `/data1/users/zhaoXY/adaptation-record.md`（对参考实现的每处改动及理由）

---

## 一、当前状态（2026-10-11）

| 项 | 状态 |
| --- | --- |
| H0 在 train 划分上的 baseline | ✅ **已完成**，见第三节 |
| Meta-Harness 首轮 + 定向复验 | ✅ **已完成**（候选 65.0%，判无显著差异），见第四节 |
| 独立复现（阶段一验收项） | TB2 复现侧完成，尚需四人交叉核对；知识收集需按主分支新 SourcePacket 范式重建（方向由 4 变 3，权限/审批与运行隔离已转李嘉旺） |
| 沙箱后端 | 本地 Docker（已打通，89 个任务镜像本机全量缓存） |
| 配置 | `terminal-bench-2.0/configs/` 三份已就位 |

## 二、相对参考实现的改动

共 13 处，全部记录在 `adaptation-record.md`，按影响面分三类：

| 类别 | 改动 | 说明 |
| --- | --- | --- |
| **协议适配**（四人须一致） | 依赖 URL 修复、执行位补齐、模型改由 `HARBOR_MODEL` 指定、数据集改由 `HARBOR_DATASET_PATH` 指定、沙箱白名单放行 `docker` | 这些是"迁移到共同协议"的必要改动，不是实现选择 |
| **优化器重写** | `propose_claude()`（绑死 Claude Code CLI）→ `litellm_proposer.py`（进程内 litellm 直调） | 协议要求优化模型为 `deepseek-v4-flash`，CLI 路径无法指向任意 provider |
| **工程便利**（不影响可比性） | `SMOKE_TEST_TASK`、`RUNS_DIR` 改为环境变量可覆盖 | 默认值与上游一致；未设置时行为不变 |

**未改动**：`agents/baseline_kira.py`（H0）、`agents/baseline_terminus2.py`、`prompt-templates/terminus-kira.txt`、`tests/test_meta_harness.py`、`claude_wrapper.py` —— 均与 HEAD 逐字节一致（sha256 核对过）。

## 三、H0 baseline 结果（train 划分）

| 项 | 值 |
| --- | --- |
| 规模 | 30 题 × 2 次 = 60 trial |
| **通过率** | **40/60 = 66.7%** |
| 逐题 | 18 题两次全过 / 4 题部分 / 8 题两次全败 |
| 墙钟 / 费用 | 113 分钟 / **$10.13** |
| tokens | 281.8M in / 6.04M out |

失败构成（20 个 trial）：`AgentTimeoutError` 10、**真答错** 7、`VerifierTimeoutError` 3。

> ⚠️ **交叉核对的两个前提**
>
> 1. **`VerifierTimeoutError`（3 个）不是 agent 能力失败**——是验证器跑满 900s 被切断，属评测侧开销。直接计入通过率会低估 H0。四人需先统一这类 trial 的计分口径，再比较分数。
> 2. **本次并发用 10，偏离协议默认的 50**。原因是运行时宿主 load average 达 82（64 核，另有他人 49 个容器在跑）。10 个 `AgentTimeoutError` 中有多少是负载导致的假失败，需在低负载下复跑才能定量。**在这一点澄清前，本分数不宜与另外三人直接比较。**

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
export SMOKE_TEST_TASK=fix-code-vulnerability

# H0 baseline（本次实跑的命令）
bash scripts/run_eval.sh agents.baseline_kira:AgentHarness full 2 10 \
  --job-name h0-train-baseline --jobs-dir "$RUNS_DIR/jobs" -y

# 免 API 回归测试（应 44 项全过）
uv run python -m unittest tests.test_meta_harness tests.test_litellm_proposer

# 最便宜的链路自检（不调 LLM）
uv run harbor run --agent oracle -p "$HARBOR_DATASET_PATH" -i fix-code-vulnerability \
  -e docker -n 1 --n-attempts 1 --job-name oracle-check --jobs-dir "$RUNS_DIR/jobs" -y
```

**注意**：`run_eval.sh` 直跑时不会自己读 `RUNS_DIR`，必须显式传 `--jobs-dir`；只有经 `meta_harness.py` 调用时才会自动带上。

## 六、待四人商定的事项

1. **沙箱后端统一**：本地 Docker 已验证可用；Runloop / Modal 需各自账号与配额。
2. **并发数**：本机负载下 50 并发不可行（会因超时产生假失败），建议四人在启动前确认宿主负载再定。
3. **`SMOKE_TEST_TASK`**：上游默认的 `extract-elf` 在本仓库 `split-v1.json` 中属 **test 集**，与"test 到最终评估才运行"冲突。提案改用 `fix-code-vulnerability`（train 集，实测两次尝试均 1.0、1.1/1.3 分钟）。**四个副本都是同一份硬编码，必须统一。**
4. **`VerifierTimeoutError` 计分口径**（见第三节）。
5. **依赖 URL 修复与执行位缺陷**：同一问题在仓库里有 5 处副本（1 处共享 H0 + 4 份个人副本），须四人改成同一份，否则不可比。详见 `personal-notes.md` 第 3、4 条。

## 七、产物位置

| 内容 | 路径 | 是否提交 |
| --- | --- | --- |
| 原始运行产物 | `runs/jobs/<job>/`、`runs/logs/` | ❌ 本地（`.gitignore` 已挡） |
| 机器可读摘要 | `runs/h0-train-baseline-summary.json` | ❌ 本地 |
| 配置 | `terminal-bench-2.0/configs/*.yaml` | ✅ |
| 本说明 | `terminal-bench-2.0/notes/README.md` | ✅ |
| 结果摘要（交叉核对入口） | `terminal-bench-2.0/results/README.md` | ✅ |
