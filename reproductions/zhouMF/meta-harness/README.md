# 周梦凡的 Meta-Harness 复现工作区

本目录仅由 **周梦凡**（`zhouMF`）维护。代码、配置、日志和结果不得引用其他成员的个人工作区。

| 内容 | 独立路径 |
| --- | --- |
| Meta-Harness 代码 | `code/` |
| H0 实现 | `code/reference_examples/terminal_bench_2/agents/baseline_kira.py` |
| 优化循环 | `code/reference_examples/terminal_bench_2/meta_harness.py` |
| 个人配置 | `configs/terminal-bench-2.0.yaml`、`configs/h0.yaml`、`configs/meta-harness.yaml` |
| 原始运行产物 | `runs/`（本地生成，不提交 Git） |
| 复现说明 | `notes/` |
| 服务器工作区 | `/data1/users/zhouMF/knowledge-guided-harness-evolution/reproductions/zhouMF/meta-harness/` |

`code/` 是从官方 Meta-Harness 仓库完整克隆后移除上游 `.git` 的个人副本，后续提交进入本仓库的个人分支。Benchmark 只从仓库根目录 `benchmarks/terminal-bench-2.0/` 读取，不在个人目录复制或修改。执行模型与优化模型均使用 `deepseek-v4-flash`；原始代码中与 Claude/Anthropic 绑定的入口需要在本人的 `code/` 内适配并记录。
