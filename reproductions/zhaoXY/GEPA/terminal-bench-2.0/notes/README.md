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
（搜索进行中，终评完成后回填：种子分数轨迹、最佳候选 prompt 的 diff、train 30×2 的 pass@2 与
trial-level micro、与 H0 0.6333 / 0.5500 的逐题对照、实际花费。）
<!-- RESULTS:END -->

## 5. 成本台账

| 项 | 金额 |
| --- | --- |
| oracle 预检（不调 LLM） | $0 |
| 单题冒烟 `gepa-tb2-smoke` | $0.0619 |
| 搜索 `gepa-tb2-search-1` | 见 `runs/gepa-tb2-search-1/gepa_summary.json` 的 `cost` 字段 |
| 终评 `gepa-tb2-final-1` | 见 `../results/summary.json` 的 `cost_usd` |

明细（逐批复核用）：`runs/cost-ledger.jsonl`（每次 harbor 批次的题目、分数、花费、耗时）。

## 6. 过程中发现（对全组有意义）

1. **`mcmc-sampling-stan` 的 oracle 预检 = 0.0**（2026-10-14，本单元实测）：该题在本地 Docker +
   冻结快照下，连官方 `solution/solve.sh` 都拿不到分（验证器不可满足）。任何把它放进搜索集或
   评测集的线都会得到系统性低估，建议全组核对。它已从本单元搜索集剔除。
2. **H0 的 prompt 就是种子**：GEPA 的结果与 H0 的唯一差异是
   `prompt-templates/terminus-kira.txt` 的文本，逐题 diff 会随结果一起入库。
3. 上游 GEPA 的 `terminal_bench_adapter` 不可用一事对其他成员同样成立（他们也要复现 GEPA）。

## 7. 待办

- [ ] 终评完成后回填 §4 与 §5，并生成 `results/summary.{md,json}`。
- [ ] 若搜索未产生改进：如实报告"本轮预算内无增益"，不追加搜索预算（等团队决定是否加码）。
- [ ] H0 对照口径（0.6333 vs meta-harness Phase 0 的 0.6667）待团队统一，见 config `open_items`。
