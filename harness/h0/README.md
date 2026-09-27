# 共同 H0：Meta-Harness 原始 Terminus-KIRA

本目录原样保存 [Meta-Harness TB2 参考实现](https://github.com/stanford-iris-lab/meta-harness/tree/44b9942127847f7421db70d8c7e48407f09a3c70/reference_examples/terminal_bench_2) 中的初始 `agents/baseline_kira.py`、提示词、缓存辅助文件和 `pyproject.toml`，上游提交为 `44b9942127847f7421db70d8c7e48407f09a3c70`。代码遵循随附的 [`LICENSE.upstream`](LICENSE.upstream)（MIT）。

运行导入路径是 `agents.baseline_kira:AgentHarness`，须把本目录放在 `PYTHONPATH` 上；上游实现的提示词路径是相对于 `agents/` 的 `../prompt-templates/terminus-kira.txt`。不要就地修改 H0；每个方法从此目录复制候选，并记录差异。正式运行需先按 [`phase1-decisions.md`](../../docs/phase1-decisions.md) 核对本地 TB2 checkout、依赖锁、Docker 和 API。

`baseline_kira.py` 的 Git blob SHA-256：`e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889`；已与上游相同提交的 Git blob 比对一致。Windows 工作区可能用 CRLF，工作区文件哈希会不同。这里没有 Meta-Harness 搜索后发布的高分 agent。
