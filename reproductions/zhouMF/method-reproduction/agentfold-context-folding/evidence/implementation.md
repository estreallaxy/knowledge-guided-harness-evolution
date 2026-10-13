# 实现依据

`code/context_folding.py` 把论文的多尺度状态做成可运行的 workspace 与折叠策略：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 任务锚点 + 长期摘要 + 最近交互 | `ContextWorkspace.render()` | 三段式渲染，规模可度量。 |
| 细粒度折叠 | `ContextWorkspace.fold_recent` | 把刚结束的一批交互折成一条记忆。 |
| 深度折叠 | `ContextWorkspace.consolidate(start, end)` | 把已完成子任务的若干摘要并成一条。 |
| 何时折叠 | `FoldingPolicy.maybe_fold` | 交互数超 `recent_budget` 触发细折；摘要数超 `summary_budget` 触发深折。 |
| 折叠指令须保留关键证据 | `keep_key_summarizer` | 含 `KEY:` 的行原样带过，其余截断。 |
| 证据存活检查 | `ContextWorkspace.missing_evidence` | 折叠后逐条核对关键证据是否仍可见。 |

**未实现（论文有、本地没有）**：训练后的 agent 自主产生 folding directive、
BrowseComp/BrowseComp-ZH 环境与判分、以及论文报告的 100 轮后约 7k token 的实测。
