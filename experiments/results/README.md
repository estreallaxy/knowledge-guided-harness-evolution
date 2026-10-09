# 结果字段约定

本目录保存两条实验线（H0 与 Meta-Harness）的运行结果。字段按[三阶段任务计划](../../docs/team-execution-plan.md)统一：task ID、配置、trace、分数、token、费用、时延、异常和候选 harness 版本；优化器侧成本（优化模型、搜索轮数、候选数、优化成本）单独记录，不混入执行预算。

## 目录约定

每次运行一个目录：

```text
experiments/results/<benchmark>/<run_id>/
├── per-task.jsonl   # 每行一个任务的结果记录
├── summary.json     # 本次运行的汇总与配置引用
└── traces/          # 原始 trace（默认不入库，见 .gitignore）
```

- `run_id` 格式：`<harness版本>-<方法>-<日期>-<序号>`，如 `h0-terminal-bench-2.0-20261005-1`。
- 同一次运行的所有字段写入同一目录，不跨目录拼接。
- 原始 `per-task.jsonl` 与 `traces/` 只作本地留存；汇总表按需引用路径。结果字段文档（本文件）入库，运行产物不入库。

## 逐题记录（`per-task.jsonl`）

每行一个任务（JSON Object）：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `task_id` | string | 与 `benchmarks/terminal-bench-2.0/split-v1.json` 一致的任务 ID |
| `split` | string | `train` / `dev` / `test`，标明来源划分 |
| `status` | string | `success` / `failed` / `error` / `timeout` |
| `score` | number | 0–1，判分器原始输出（二值成功记 1 或 0） |
| `steps` | integer | 实际执行的 step 数 |
| `tool_calls` | integer | 实际工具调用次数 |
| `tokens_in` / `tokens_out` | integer | 执行模型输入 / 输出 token |
| `cost` | number | 费用（美元），按执行模型的计费口径 |
| `wall_time_s` | number | 墙上时间（秒） |
| `error` | string \| null | 异常信息；无异常为 `null` |
| `trace_path` | string | 相对 `experiments/results/` 的 trace 路径 |
| `harness_version` | string | 候选 harness 版本标识（H0 或某轮候选） |
| `config_hash` | string | 公共配置 + 方法配置的内容哈希 |
| `run_id` | string | 与所在目录一致，防止跨目录拼接错行 |

## 汇总记录（`summary.json`）

运行级字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `run_id` / `created_at` | string | 运行标识 / 完成时间 |
| `benchmark` / `split` | string | 基准与划分 |
| `harness_version` / `config_hash` | string | 与逐题记录一致 |
| `task_count` / `success_count` | integer | 任务数与成功数 |
| `success_rate` / `avg_score` | number | 总体两项汇总 |
| `total_tokens_in` / `total_tokens_out` | integer | 执行模型 token 合计 |
| `total_cost` | number | 执行费用合计 |
| `total_wall_time_s` | number | 墙上时间合计 |
| `optimizer` | object \| null | 优化器侧记录；无优化器（如 H0）为 `null` |

优化器侧单独块（Meta-Harness 等），不与执行预算混记：

| 字段 | 说明 |
| --- | --- |
| `optimizer.model` | 优化模型 |
| `optimizer.search_rounds` | 搜索轮数 |
| `optimizer.candidates` | 候选 harness 版本列表（版本标识及各候选的开发集分数） |
| `optimizer.tokens` / `optimizer.cost` | 优化器 token 与费用，单独列示 |

## 缺失记录检查

汇总前按此清单核对；缺失字段用显式 `null`（不删键），无法解释的缺失写入汇总说明：

1. 每条逐题记录必须同时有 `score` 与 `trace_path`；`status` 为 `error` / `timeout` 时必须有 `error` 文本。
2. `run_id`、`harness_version`、`config_hash` 在同一 run 内必须完全一致。
3. 两条实验线的任务 ID 集合与 `split` 划分必须一致；缺题逐项列出，不静默丢弃。
4. H0 运行的 `optimizer` 必须为 `null`；Meta-Harness 运行不得把优化器 token / 费用计入 `tokens_*` 与 `cost`。
5. `config_hash` 变化后两条实验线一起重跑，不混合不同配置的结果。

## 分工

- 周梦凡（H0）与赵星源（Meta-Harness）按本约定产出各自运行的 `per-task.jsonl` 与 `summary.json`。
- 王懿按确定后的配置汇总两条实验线，更新 [`../README.md`](../README.md) 的结果列，并执行上述缺失记录检查。
