# GEPA × Terminal-Bench 2.0 复现说明（赵星源）

更新时间：2026-10-14。配置见 `../configs/gepa-terminal-bench-2.0.yaml`；
本文件记录环境准备、适配说明、实跑命令、结果与成本、与论文设置的差异。

## 1. 环境与两个 venv（容易踩错，先看这里）

| venv | 位置 | 用途 |
| --- | --- | --- |
| **GEPA venv** | `../../code/.venv`（`gepa` 仓库，`uv sync --extra full`） | 跑 `gepa.optimize`、adapter、反思 LM（litellm） |
| **runner venv** | `./code/.venv`（本单元的 TB2 运行入口，`uv sync`） | §adapter 通过 subprocess 调用，跑 harbor 与 agent |

`./code/` 是本单元**自带的** TB2 运行入口（从 meta-harness 单元复制后独立 sync），
满足"四个 baseline 必须各自独立复现、不共用环境与适配代码"的要求；其中
`agents/baseline_kira.py` 与 H0 单元逐字节一致（sha256 `e06b9273…`），
`prompt-templates/terminus-kira.txt` 与 H0 单元逐字节一致（sha256 `adf2d40a…`）。

离线测试（12 项，零 LLM 零沙箱）：`cd .. && ../code/.venv/bin/python -m unittest discover -s tests -v`

## 2. 适配说明（实现级，结果须连同本声明一起引用）

1. **自写 adapter**。上游 `gepa/adapters/terminal_bench_adapter/` 面向已废弃的 `tb` CLI 与
   `terminal-bench-core` 包，对本仓库的 TB2（harbor 0.18.0 + terminal-bench 0.2.18 + 本地 Docker）
   **不可用**；`gepa_tb2_adapter.py` 是新实现，复用本仓库既有的 `scripts/run_eval.sh` 调用链。
2. **候选 = `instruction_prompt`**（唯一文本组件）。adapter 把候选写入本单元运行入口的
   `prompt-templates/terminus-kira.txt`，运行结束还原 H0 原文（备份 + sha256 校验，见
   `runs/terminus-kira.h0.txt`）。
3. **搜索集缩小**：官方每候选在完整 valset 上评估，本环境单题成本下不可行 →
   搜索只在 train 的 5 题子集上进行（选择理由见 config `search.search_set_rationale`）；
   终评仍在 **train 全 30 题 × 2 次**，与 H0 同协议可比。
4. **模型统一**：执行与优化模型均为 `deepseek/deepseek-v4-flash`（按 `docs/research-plan.md` §2.2）。
   上游示例用 GPT 系列，属协议要求的替换。
5. **成本护栏**：adapter 逐批记录真实花费到 `runs/cost-ledger.jsonl`；`CostGuardStopper` 在
   harbor + 反思 LM 合计超限时停止搜索（本轮 $4）。

## 3. 实跑命令

```bash
cd reproductions/zhaoXY/GEPA/terminal-bench-2.0

# 零成本链路自检（oracle 不调 LLM）
cd code && set -a && source .env && set +a
uv run harbor run --agent oracle -p /data1/users/zhaoXY/benchmarks/tb2-split-v1/train -e docker \
  -n 6 --n-attempts 1 --job-name gepa-oracle-preflight --jobs-dir ../runs/jobs -y \
  -i portfolio-optimization -i bn-fit-modify -i pytorch-model-cli -i mteb-retrieve \
  -i custom-memory-heap-crash -i mcmc-sampling-stan
cd ..

# 单题真实冒烟（≈$0.06）
../code/.venv/bin/python run_gepa_tb2.py --run-id gepa-tb2-smoke \
  --search-set custom-memory-heap-crash --max-metric-calls 1 --cost-limit 0.5 --concurrency 1

# 正式搜索（预算护栏 $4）
../code/.venv/bin/python run_gepa_tb2.py --run-id gepa-tb2-search-1 \
  --max-metric-calls 20 --cost-limit 4.0 --concurrency 5

# 终评（与 H0 同协议：train 30 题 × 2 次 = $9.5）
bash run_final_eval.sh runs/gepa-tb2-search-1/best_prompt.txt gepa-tb2-final-1
```

## 4. 结果

<!-- RESULTS:BEGIN -->
**本轮无终评分数**：搜索未产出候选（最佳候选 = 种子，逐字节相同），按事前决策门不执行 $9.5 终评。
完整结论与依据见 `../results/README.md`；下方是搜索阶段的实测记录。
<!-- RESULTS:END -->

### 4.1 搜索阶段实测（2026-10-14，`gepa-tb2-search-1`）

- 种子（H0 prompt）在 5 题搜索集上的 val 分数 = **0.8（4/5）**；
- 迭代 1–6 全部命中 `All subsample scores perfect for parent 0. Skipping.`
  → **未提出任何候选**（`skip_perfect_score=True` 的设计行为）；
- 逐条实测的 minibatch 抽样（每批次单题）：pytorch-model-cli $0.084、bn-fit-modify $0.043、
  portfolio-optimization $0.040、mteb-retrieve $0.126 —— **全部 1.0**，与 H0 的"两次只过一次"
  不同，说明单次尝试（temp 0.7、无 seed）下这些题的通过率是抛硬币，且本轮偏向通过。

**结构性结论（下轮设计依据）**：本环境里"便宜且对 H0 有梯度"的题集合 ≈ 空集——
便宜的题（$0.03–0.2 / 3–12 分钟）在单次尝试下大多被种子解出；种子稳定失败的题
（`sam-cell-seg`/`make-mips-interpreter`/`schemelike-metacircular-eval` 等）单次 $\ge$ 0.57、
耗时 ≥25 分钟，且多为超时类。因此**小预算下的 GEPA 反思循环拿不到可靠信号**。
下轮若要真正跑 GEPA：搜索集应选"种子稳定失败且非超时"的题（按 2 次尝试的 0/2 结果挑），
并按 `minibatch ≥ 2`、每候选 ≥$0.6–1.0 估预算（即搜索预算需 $20–30 量级）。

## 5. 成本台账

| 项 | 金额 |
| --- | --- |
| oracle 预检（不调 LLM） | $0 |
| 单题冒烟 `gepa-tb2-smoke` | $0.0619 |
| 搜索 `gepa-tb2-search-1`（11 次 metric call，71 分钟，优雅停止） | **$0.9053**（harbor；反思 LM $0 —— 从未提出候选） |
| 终评 `gepa-tb2-final-1` | **未执行**（无候选；按决策门保留 $9.5 预算） |
| 本轮合计 | **$0.9672** |

明细（逐批复核用）：`runs/cost-ledger.jsonl`（每次 harbor 批次的题目、分数、花费、耗时）。

## 6. 过程中发现（对全组有意义）

1. **`mcmc-sampling-stan` 的 oracle 预检 = 0.0**（2026-10-14，本单元实测）：该题在本地 Docker +
   冻结快照下，连官方 `solution/solve.sh` 都拿不到分（验证器不可满足）。任何把它放进搜索集或
   评测集的线都会得到系统性低估，建议全组核对。它已从本单元搜索集剔除。
2. **H0 的 prompt 就是种子**：GEPA 的结果与 H0 的唯一差异是
   `prompt-templates/terminus-kira.txt` 的文本，逐题 diff 会随结果一起入库。
3. 上游 GEPA 的 `terminal_bench_adapter` 不可用一事对其他成员同样成立（他们也要复现 GEPA）。

## 7. 待办

- [x] ~~回填 §4 与 §5~~ ✅ 2026-10-14：本轮无候选，已按此如实记录（`../results/README.md`）。
- [ ] **下一轮**：按 §4.1 的建议重配搜索（稳定失败集 + minibatch ≥2 + $20–30 搜索预算），
      跑出候选后执行 `run_final_eval.sh` 与 `compare_with_h0.py`；届时 `results/` 换成正式分数摘要。
- [ ] H0 对照口径（0.6333 vs meta-harness Phase 0 的 0.6667）待团队统一，见 config `open_items`。
- [ ] 本轮"搜索集饱和"的结构性结论建议同步给其他成员（他们复现 GEPA 时会撞到同一堵墙）。
