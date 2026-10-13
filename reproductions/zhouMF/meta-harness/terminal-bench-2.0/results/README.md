# Result summary

| Field | Value |
| --- | --- |
| Baseline | meta-harness |
| Benchmark | Terminal-Bench 2.0 |
| Code revision | 上游 `8123ccabe2b19fa1123090b2e5f1bacc20963ce8`（见 `../../code/UPSTREAM.md`）；本地适配见 `../code-adaptation/upstream-adaptation.diff` |
| H0 revision | 共享参考快照 `agents/baseline_kira.py`（未修改） |
| Dataset split | `tb2-split-v1` train（30 题）；dev 19 / test 40 未运行 |
| Model and provider | `deepseek/deepseek-v4-flash`（执行与优化共用，deepseek） |
| Random seed | 无固定种子；`--ak temperature=0.7` |
| Score | H0：计分均分 **0.6909**（38/55）、全 trial 均分 **0.6333**（38/60，未评分按 0）、30 题 macro 任务均分 **0.6667**（20.0/30）。前沿候选 `enforced_final_state_audit`：计分均分 0.7143（20/28）、全 trial 均分 0.6667（20/30） |
| Score basis | 计分均分 = successes / scored_trials；全 trial 均分 = successes / total_trials；macro 任务均分 = 任务内先取均值再对任务取平均。三者互不替代，引用必须写明口径；重算脚本 `../code-adaptation/scripts/compute_scores.py` |
| Successful / failed / ungraded | H0：38 成功 / 17 零分 / 5 未计分（30 题 × 2 trials = 60） |
| Tokens / calls / cost / elapsed time | H0：312.15M in / 5.29M out tokens；8359.9s（2h19m）；`cost_usd_from_agent_result` 9.29（非真实计费） |
| Config path | `../configs/h0.yaml`、`../configs/meta-harness.yaml`、`../configs/terminal-bench-2.0.yaml` |
| Trace path | `../../code/reference_examples/terminal_bench_2/jobs/`（本地，已 gitignore） |
| Notes | `../notes/reproduction-summary.md`、`../notes/run-log.md`；机读汇总见 `summary.json` |

同口径复核后，iter1 相对 H0 的净增益为 **+3.6pt**，落在单题噪声范围内，不能定性为提升；
详见 `../notes/reproduction-summary.md` 第三节与 `summary.json` 的 `same_basis_vs_h0`。

Keep large raw artifacts local under `runs/` or `traces/`; commit the summary and the evidence needed to audit it.
