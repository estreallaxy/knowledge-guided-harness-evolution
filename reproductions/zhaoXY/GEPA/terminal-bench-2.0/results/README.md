# Result summary — GEPA × Terminal-Bench 2.0（赵星源）

**结论（2026-10-14）：本单元已完成 GEPA 在 TB2 上的完整接入并在预算内跑完一次真实搜索，
但搜索未产出任何候选改进；按事前约定的决策门，未进入终评。**
本格目前**没有可与其他 baseline 比较的 GEPA 分数**，原因与依据如下（全部可回到本地产物）。

## 1. 本轮运行

| Field | Value |
| --- | --- |
| Baseline | GEPA（`gepa-ai/gepa` @ `462e437a…`，`gepa.optimize` + 本单元自写 harbor adapter） |
| H0（种子，未改动） | `terminus-kira`，prompt sha256 `adf2d40a…`；搜索结束时已校验还原 |
| Benchmark | Terminal-Bench 2.0（仓库冻结快照，本地 Docker） |
| Dataset split | train 子集 5 题（搜索集；test 40 题从未打开） |
| Model and provider | 执行与优化模型均 `deepseek/deepseek-v4-flash`（API 实际标识 `deepseek-flash`） |
| Random seed | `seed=0`（GEPA RNG）；任务侧无 seed，temperature 0.7 |
| **Score** | **无终评分数**（无候选）；种子在搜索集上 val = **0.8（4/5）**，最佳候选 = 种子（`best_changed_from_seed: false`） |
| Successful / failed / ungraded | 搜索期 11 次 metric call（5 题种子全量 + 6 次单题 minibatch），全部判分 |
| Tokens / calls / cost / elapsed | **$0.9053**（全部为 harbor 执行成本；反思 LM $0，因为从未提出候选）；71 分钟 |
| Config path | `configs/gepa-terminal-bench-2.0.yaml` |
| Trace path | 本地不入库：`runs/gepa-tb2-search-1/`（`run_log.txt`、`gepa_state.bin`、逐批 `runs/cost-ledger.jsonl`）、`runs/jobs/<job>/` |
| Notes | `notes/README.md` §4.1 记录了结构性原因与下轮设计建议 |

## 2. 为什么没有产出候选（实测证据）

`runs/gepa-tb2-search-1/run_log.txt` 显示：迭代 1–6 **全部**为

```
All subsample scores perfect for parent 0. Skipping.
Reflective mutation did not propose a new candidate
```

即 GEPA 每次抽到的 minibatch 样本都被种子拿到 1.0（`skip_perfect_score=True` 时不反思、不提候选）。
逐条 minibatch 实测：pytorch-model-cli 1.0 / bn-fit-modify 1.0 / portfolio-optimization 1.0 /
mteb-retrieve 1.0 —— 这些题在 H0（两次尝试）里是"只过一次"，但单次尝试下本轮全部通过。

**结构性结论**：本环境中"便宜（$0.03–0.2、3–12 分钟）且有稳定梯度"的 TB2 题集合 ≈ 空集：
便宜题在单次尝试下大多被种子解出；种子稳定失败的题（`sam-cell-seg`、`make-mips-interpreter`、
`schemelike-metacircular-eval` 等）单次 ≥$0.57、耗时 ≥25 分钟，且多为超时类。
小预算下 GEPA 的反思循环因此拿不到可靠信号 —— 这是**预算规模问题**，不是 adapter 问题
（adapter 本身已通过 12 项离线测试、oracle 预检、单题真实冒烟与整轮真实搜索验证）。

## 3. 决策门与预算

- 事前约定（用户 2026-10-14 批准）：搜索集上最佳候选 ≥ 种子时才花 $9.5 跑 train 30×2 终评。
  本次最佳候选 = 种子（逐字节相同），终评只会把 H0 重测一遍 → **不执行**，$9.5 保留。
- 本轮 GEPA 相关实际支出：oracle 预检 $0 + 单题冒烟 $0.0619 + 搜索 $0.9053 ≈ **$0.97**。

## 4. 下轮建议（若要真正跑出 GEPA 分数）

| 项 | 建议 |
| --- | --- |
| 搜索集 | 按"种子在 2 次尝试下稳定失败 **且非纯超时**"筛选（本轮证据：`sam-cell-seg` 等），3–6 题 |
| minibatch | ≥2（降低"全满分跳过"的概率） |
| 预算 | 每候选评估 $0.6–1.0；搜索 $20–30 量级，另加终评 $9.5 |
| 现状 | adapter/驱动/终评脚本/对照脚本均已就绪，改配置即可开跑（`configs/` + `run_gepa_tb2.py --search-set …`） |
