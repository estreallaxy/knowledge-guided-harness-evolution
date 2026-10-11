# Result summary

**状态：尚未跑通（未运行）。** Meta-Harness 优化循环截至 2026-10-11 未执行，本表在运行后填写；
原因与计划见 `../notes/stage1-summary.md` 第 6 节（DeepSeek 账户余额约 ¥28，不足以支撑一轮 30 题 × 候选的
搜索，等待团队预算确认）。H0 对照线的已有结果在
`reproductions/wangY/H0/terminal-bench-2.0/results/summary.md`（pass@2 = 0.70），**不属于本线结果**。

| Field | Value |
| --- | --- |
| Baseline | meta-harness（H0 起点：`agents.baseline_kira:AgentHarness`） |
| Benchmark | terminal-bench@2.0（commit `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`） |
| Code revision | 未运行 |
| H0 revision | `baseline_kira.py` sha256 `e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889` |
| Dataset split | train（30 题，`split-v1.json`，seed `kghe-tb2-v1-2026-09-27`） |
| Model and provider | 执行 `deepseek/deepseek-flash`；优化器 deepseek-v4-flash 经 Claude Code CLI（目标配置，未验证） |
| Random seed | 未运行 |
| Score | 未运行 |
| Successful / failed / ungraded | 未运行 |
| Tokens / calls / cost / elapsed time | 未运行 |
| Config path | `../configs/meta-harness.yaml`、`../configs/terminal-bench-2.0.yaml` |
| Trace path | 运行后：本地 `../runs/`、`../traces/`（不入库） |
| Notes | 优化器成本须单独记录，不混入执行预算；config_hash 变更后两条线一起重跑 |
