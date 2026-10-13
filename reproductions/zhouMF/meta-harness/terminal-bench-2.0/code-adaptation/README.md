# code-adaptation（周梦凡 / zhouMF，Terminal-Bench 2.0）

本目录保存**本地适配与本次复现产生的代码**，与共享的上游副本 `../../code/` 分开：
`../../code/` 保持与参考实现一致，只做上游快照；所有本地改动以补丁形式记录在这里，
便于五人交叉核对时还原可比条件（详见 [`../notes/adaptations.md`](../notes/adaptations.md)）。

```text
code-adaptation/
├── upstream-adaptation.diff   # 对 runner 的本地改动（补丁，不直接改 code/）
├── scripts/                   # 本地运行脚本与汇总工具
├── agents/                    # P6 优化循环产出的候选 harness
└── prompt-templates/          # 候选 harness 使用的提示模板
```

| 路径 | 内容 | 来源 |
| --- | --- | --- |
| `upstream-adaptation.diff` | 对 `meta_harness.py`、`pyproject.toml`、`scripts/run_eval.sh`、`tests/test_meta_harness.py` 的 4 处本地改动 | 本人适配 |
| `scripts/run_local_docker.sh` | 本地 docker 后端一键入口（显式设置后端/模型/任务集） | 本人适配 |
| `scripts/run_meta_harness.sh` | 优化循环入口（Claude Code CLI → 本地网关 → deepseek） | 本人适配 |
| `scripts/claude_deepseek_gateway.sh` | Anthropic `/v1/messages` → deepseek 的本地 litellm 网关 | 本人工具 |
| `scripts/p1_env_check.sh` | P1 环境检查，输出 `../notes/p1-env-report.txt` | 本人工具 |
| `scripts/h0_baseline_watch.sh` | H0 重跑看护：余额耗尽即熔断 | 本人工具 |
| `scripts/summarize_run.py` | 把 Harbor job 目录汇总成 `../notes/run-log.md` 记录 | 本人工具 |
| `scripts/export_results.py` | 把 Harbor job 目录导出成 `../results/summary.json` 等可入库摘要 | 本人工具 |
| `agents/enforced_final_state_audit.py` | P6 iter1 候选（前沿）：完成前强制核对最终环境状态 | 优化循环产出 |
| `agents/deadline_audited_delivery.py` | P6 iter2 候选：交付前做截止时间审计 | 优化循环产出 |
| `agents/deadline_aware_delivery.py` | P6 iter2 候选：在观测中注入 `[budget]` 提示 | 优化循环产出 |
| `prompt-templates/*.txt` | 上述两个 iter2 候选的提示模板 | 优化循环产出 |

## 应用上游适配

```bash
BASE=/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness
cd "$BASE/code/reference_examples/terminal_bench_2"
patch --dry-run -p1 < "$BASE/terminal-bench-2.0/code-adaptation/upstream-adaptation.diff"
patch -p1 < "$BASE/terminal-bench-2.0/code-adaptation/upstream-adaptation.diff"   # 对干净上游副本执行一次
```

上游 revision 见 `../../code/UPSTREAM.md`。补丁只改适配点，不改 H0 harness
（`agents/baseline_kira.py` 与共享参考快照一致）。

## 候选的定位

`agents/` 里的三个候选由 P6 优化循环产出，评测口径与结论见
[`../notes/reproduction-summary.md`](../notes/reproduction-summary.md) 与
[`../results/summary.json`](../results/summary.json)：前沿为 `enforced_final_state_audit`
（同口径 +3.6pt），但落在单题噪声范围内，**不能定性为提升**。

## 不入库的内容

`.env`（凭据）、`jobs/`、`logs/`、`runs/`、`uv.lock` 等运行态产物均在 `.gitignore` 内，
原始 trace 保留在本地工作区。
