# Meta-Harness 独立复现总结（周梦凡 / zhouMF）

状态：P0–P6 已完成；P7 本文档已于 2026-10-11 按 `jobs/` 逐 trial 产物复核并修订（更正第三节口径），
2026-10-13 按最新 `main` 重排工作区路径并复核。
补充：2026-10-12 环境重检通过（12/12 免 provider 单测绿、H0 与共享参考 md5 一致、网关 200、任务集 30/19/40）；
步骤清单见 [`reproduction-steps.md`](reproduction-steps.md)。剩余项（严格对比、扩轮）被 DeepSeek 余额 ¥2.26 阻塞。
工作区：`/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness/terminal-bench-2.0/`
共享 runner：`../code/reference_examples/terminal_bench_2/`（`jobs/`、`logs/` 均在该目录下）
分支：`zhouMF/self-evolution-branch`
时间：2026-10-10 08:0x → 2026-10-11 06:24（UTC）

## 一、验收一/二对照

| 验收条件 | 状态 | 证据 |
| --- | --- | --- |
| H0 在 TB2 上有可复现的分数、trace、token、费用、时延 | ✅ | `notes/run-log.md` R3（`jobs/h0-baseline-r2`）：30 题 × 2 trials，mean 0.6667，60 trials / 16 异常，312.15M in / 5.29M out tokens |
| 结果可追溯、满足统一协议 | ✅ | 逐题表落 `notes/run-log.md`；条件表见第四节 |
| `meta_harness.py` 优化循环完整跑通一轮 | ✅ | `notes/run-log.md` R4（P5 冒烟）四段证据齐全 |
| 从 H0 出发跑通初始化与至少一轮 trace 优化 | ✅ | P6：2 轮提议 + 3 个候选 + 3 次 train 30 题评测，`logs/p6-main/` |
| 2.1 每个方向 2 篇论文 + 高价值方法 | ✅ | 论文与官方代码入库 `knowledge/source-packets/`（6 篇 / 3 方向）；离线可运行 demo 入库 `../../method-reproduction/` |

## 二、复现路径（实际执行的步骤）

| 步骤 | 内容 | 结果 |
| --- | --- | --- |
| P0 | 三份配置 | `configs/{terminal-bench-2.0,h0,meta-harness}.yaml` |
| P1 | 环境打通 | uv 0.13.0、harbor 0.18.0、litellm 1.84.10；12/12 免 provider 单测绿 |
| P1.5 | 本地任务集 | `/data1/users/zhouMF/benchmarks/tb2-split-v1`（train 30 / dev 19 / test 40） |
| P2 | 执行模型 smoke | `deepseek/deepseek-v4-flash` 驱动 H0，`bn-fit-modify` reward=1.0（320s） |
| P3 | H0 基线 | 首次因账户余额耗尽作废；`h0-baseline-r2` 重跑成功，耗时 2h19m |
| P4 | 提议器接入 | Claude Code CLI 2.1.296 → 本地 litellm 网关(`127.0.0.1:4000`) → deepseek；提议器代码零改动 |
| P5 | 循环冒烟 | `logs/p5-smoke/`：提议 13m14s → 校验 3m48s → 评测 6m14s → 记录，真实花费 ¥1.70 |
| P6 | 正式搜索 | `logs/p6-main/`：2 轮提议（9m00s / 7m05s）、3 个候选、3 次 30 题评测，耗时 5h05m |
| P7 | 汇总 | 本文档 |

## 三、P6 结果

### 轮次记录（`logs/p6-main/evolution_summary.jsonl`）

| 轮 | 候选 | 机制假设 | 逐题均分（30 题为分母） | 评测耗时 |
| --- | --- | --- | --- | --- |
| 1 | `enforced_final_state_audit` | 「完成前门禁是装饰性的」：agent 宣告完成却从未在最终环境状态里验证产物，形成"声明完成但坏掉"的失败类 | **0.667** | 72m31s |
| 2 | `deadline_audited_delivery` | 上一候选的墙钟可见性 + 完成审计门禁组合 | 0.633 | 69m03s |
| 2 | `deadline_aware_delivery` | 自述为**消融对照**：仅加墙钟预算可见性，无审计门禁 | 0.600 | 66m56s |

最终 frontier：`enforced_final_state_audit` @ 66.7%。第 2 轮两个候选**均未超过** frontier。

### 与 H0 基线的逐题对比

分母口径：H0 为 30 题 × 2 trials；候选为 30 题 × 1 trial（`caffe-cifar-10`、`query-optimize` 等题在候选轮未产生计分 trial，按缺省处理）。

| 口径 | H0 基线 | iter1 `enforced_final_state_audit` | iter2 `deadline_audited_delivery` | iter2 `deadline_aware_delivery` |
| --- | --- | --- | --- | --- |
| 计分题数 | 30 | 28 | 28 | 27 |
| 均分 | 0.6667 | **0.7143** | 0.6786 | 0.6667 |

> ⚠️ 上表两侧分母不同（H0 记 30 题、候选记 28 题），因此 `+4.8pt` 被高估。按 `jobs/` 下的
> `result.json` 逐 trial 复核、只保留两边都计分的题后，iter1 的净增益实为 **+3.6pt**（见下）。

### 同口径复核（只保留两边都计分的题，2026-10-11 逐 trial 重算）

来源：`jobs/h0-baseline-r2/*/result.json`、`jobs/p6-main/evolve-*-t1/*/result.json`。

| 候选 | 共同计分题数 | 候选均分 | H0 同题均分（2 trials 平均） | 净差 | 单题升 / 降 |
| --- | --- | --- | --- | --- | --- |
| `enforced_final_state_audit` | 28 | 0.7143 | 0.6786 | **+3.6pt** | 3 / 2 |
| `deadline_audited_delivery` | 28 | 0.6786 | 0.6786 | +0.0pt | 4 / 4 |
| `deadline_aware_delivery` | 27 | 0.6667 | 0.7037 | **−3.7pt** | 2 / 4 |

H0 逐 trial 明细：30 题共 60 trial，其中 **55 个计分、5 个无分**（`compile-compcert`、`git-multibranch`、
`query-optimize`、`torch-pipeline-parallelism`、`caffe-cifar-10` 各 1，均为超时/运行异常）；
`dna-assembly`、`make-mips-interpreter` 两题两次 trial 分数不同，是 H0 侧唯一的试次噪声来源。

单题变动（相对 H0）：

| 变动 | 题目 |
| --- | --- |
| iter1 由 0→1 | `compile-compcert`、`portfolio-optimization` |
| iter1 由 0.5→1 | `dna-assembly` |
| iter1 由 1→0 | `pytorch-model-cli`、`make-mips-interpreter`(0.5→0) |
| iter2 新增回退 | `mailman`(1→0)、`mteb-retrieve`(1→0，仅 `deadline_aware_delivery`) |

结论：同口径复核后，`enforced_final_state_audit` 的净增益为 **+3.6pt（28 题里净多对 1 题，3 升 2 降）**，
`deadline_audited_delivery` 为 0，`deadline_aware_delivery` 为 −3.7pt。三者都只有 1 个 trial，
题数级噪声即可吞掉这点差异，**不能判定为真实增益**；要定性必须把候选补到 2 trials（见第七节）。

## 四、关键实验条件（交叉核对用）

| 项 | 取值 | 与共同协议 |
| --- | --- | --- |
| 执行模型 | `deepseek/deepseek-v4-flash`，`temperature=0.7` | 一致 |
| 优化模型 | `deepseek/deepseek-v4-flash` | 一致 |
| H0 | `agents.baseline_kira:AgentHarness`，未修改 | 一致 |
| 任务划分 | `tb2-split-v1` 的 train（30 题）；dev/test 未参与 | 一致（封存 test 未触碰） |
| 后端 | 本地 docker 24.0.2 | 差异，已记录 |
| 并发 | 基线 8 / P5 4 / P6 8（参考实现 50） | 差异，已记录 |
| trials | 基线 2；P6 评测 1 | 差异，已记录 |
| 搜索规模 | 2 轮 × 1–2 候选（论文默认 5 轮） | 差异，已记录 |
| 提议器 | Claude Code CLI + 本地 Anthropic 兼容网关；**提议器代码未改** | 差异（模型为 deepseek 而非 Opus） |
| 预算口径 | step/tool/token/重试全组未定；本地受 harbor 任务自带超时约束 | 未定 |

## 五、已知偏差（必须随结果一并说明）

1. **提议器模型**：论文用 Opus + `--effort max`，本工作区经网关落到 `deepseek-v4-flash`。机制（skill 先验、
   工具集、stream-json、单文件候选契约）一致，**提议质量不可与论文直接比**。
2. **中间层**：Claude Code 与 Anthropic 之间多一层 litellm 网关，`drop_params: true` 会静默丢弃上游参数
   （如 `cache_control`）。
3. **成本口径**：`claude_wrapper` 记的 `total_cost_usd` 是 Anthropic 列表价，对 deepseek 无意义；
   真实花费须用 DeepSeek 余额差（本工作区做法）。
4. **后端与并发**：runloop/50 并发 → 本地 docker/4–8 并发，墙钟时间不可直接比。
5. **评测 trials 不一致**：候选评测为 1 trial，H0 基线为 2 trials，噪声不同。若要严格对比，
   需把候选重跑成 2 trials，或把基线重跑成 1 trial。
6. **`N_EVAL_TASKS=89` 未改**：代码里的打印与提示词仍写 89 题，实际由 `HARBOR_TASK_PATH` 决定为 30 题。
   这是显示层不一致，不影响评测；已在 `notes/adaptations.md` 与本表说明。

## 六、成本

| 阶段 | 真实花费（DeepSeek 余额差） |
| --- | --- |
| P2 smoke | < ¥0.2 |
| P3 H0 基线（60 trials） | ¥32.31 |
| P5 循环冒烟（4 题） | ¥1.70 |
| P6 正式搜索（3 候选 × 30 题 + 2 轮提议） | ¥30.39 |
| **合计** | **¥64.4**（¥99.40 → ¥16.87） |

⚠️ 2026-10-11 复核时余额为 **¥16.54**（`/user/balance`，granted=0），仍不足以再跑一轮 30 题评测
（单候选 1 trial 约 ¥10、2 trials 约 ¥20）。继续 P6 扩轮前需先充值。

## 七、待办

- [x] 用现有 `jobs/` 产物做了同口径复核（第三节，iter1 净增益更正为 +3.6pt）。
- [ ] 严格对比仍需把候选补到 2 trials **或**把基线降到 1 trial；两项都需余额，当前 ¥16.54 不足，暂缓。
- [ ] 提高搜索规模到论文默认（5 轮），并固定 budget 字段（需全组确认）。
- [x] 2.1 论文收集线（每方向 2 篇）已登记到 `knowledge/source-packets/`；离线可运行 demo 迁到 `reproductions/zhouMF/method-reproduction/`。
- [ ] `notes/reproduction-plan.md` 中的 runbook 已按实际执行更新，可与其余四人交叉核对。
- [x] 候选文件已入库为 `code-adaptation/agents/*.py`（`pending_eval.json` 等运行态产物仍不入库）。
