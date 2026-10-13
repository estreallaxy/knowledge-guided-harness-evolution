# Exact source anchors

页码按 `paper/paper-v3.pdf`（57 页，含附录）计，可用 `paper/paper-v3.txt` 的 `--- PDF page N ---` 标记复核。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 两个瓶颈：无界增长带来推理显存成本 + 无关信息导致推理退化 | Abstract，PDF p.1 | 论文把二者并列为长程 agentic 任务的关键瓶颈；未给形式化定义。 |
| 统一压缩**观察**与**历史** | Abstract，PDF p.1；§3，PDF p.3 | ACON 的框架定位；「统一」是相对只压其一的既有方法的差异点。 |
| 在**自然语言空间**优化压缩指南，不需要更新被测模型参数 | Abstract，PDF p.1；§2，PDF p.2 | 模型无关（model-agnostic）可直接套用；不能推出对所有模型都有效。 |
| 指南优化依据 agent 的**失败分析**迭代 | Abstract，PDF p.1；§3.3，PDF p.5 | 这是与静态启发式压缩的关键差异；论文未证明失败归因总是正确。 |
| 把优化后的压缩器**蒸馏**进小模型 | §3.4，PDF p.5；Table 13，PDF p.25 | 蒸馏后由 student 在推理时替代 teacher。 |
| 三项主张：峰值 token 降 26–54%、成功率优于压缩基线、小模型最高 +46% | §1，PDF p.2；§3.2，PDF p.3 | 「26–54%」是跨 benchmark/设置的区间；「+46%」针对小模型作为长程 agent 的场景。 |
| 评测对象：AppWorld、OfficeBench、8-objective QA | §1，PDF p.2；§4，PDF p.6 | 三个 benchmark 的难度分层与指标定义见 Table 1/2 表注。 |
| 统一 agent 骨架为 ReAct | §4，PDF p.6 | 所有实验沿用 ReAct 风格 agent；换 agent 后的行为未报告。 |
| 主结果：AppWorld 各压缩方案对照 | Table 1，PDF p.6 | 表注说明各列是 accuracy / steps / peak input tokens(10³) / dependency(10⁶)。 |
| 主结果：OfficeBench 与 8-objective QA | Table 2，PDF p.7 | 同时给 acc/EM/F1 与 steps/peak/dependency。 |
| 消融：优化器模型与对比式反馈（task contrastive feedback） | Table 3，PDF p.9 | 默认 o3 + 对比式反馈最优。 |
| 实际效率：API 成本与单题时延 | Table 4，PDF p.9 | 成本用 gpt-4.1 agent + Qwen3-14B compressor 估计；时延为单 A100 上中位数。 |
| 蒸馏后的效果 | Table 13，PDF p.25 | 优化后的指南在小模型上仍带来提升。 |
| 限制 | §5 之后的 Limitations，PDF p.9；详细讨论 PDF p.16 | 明确承认仍存在局限，未主张普适。 |

## 官方代码

行号锚点按 `official-code/` 快照（revision `d63f9ae18959dc7215ff62899c94c5e8c56847ae`）计。

| 机制或证据 | 代码位置 | 作用 |
| --- | --- | --- |
| 压缩器基类 | `src/productive_agents/ctxopt/base.py:17`（`BaseContextOptimizer`） | 观察/历史压缩器的共同接口。 |
| 历史压缩 | `src/productive_agents/ctxopt/history_optimizer.py:19`（`HistoryOptimizer`） | 历史摘要压缩主实现；`:135` 判断是否需要重新摘要。 |
| 历史压缩的变体 | `src/productive_agents/ctxopt/history_optimizer.py:216`（`HistoryOptimizerV2`）、`src/productive_agents/ctxopt/history_optimizer.py:335`（`HistoryRetriever`） | 与论文「统一压缩」和 retrieval 基线对应。 |
| 观察压缩 | `src/productive_agents/ctxopt/obs_optimizer.py:20`（`ObservationOptimizer`）、`src/productive_agents/ctxopt/obs_optimizer.py:188`（`ObservationOptimizerV2`） | 观察压缩主实现与变体。 |
| 统一 agent | `src/productive_agents/agents/unified_agent.py` | 把压缩器挂到 agent 循环上的位置。 |
| 指南优化提示 | `experiments/prompt_optimizer/unified_compress_update_history_prompt.py`、`unified_compress_update_observation_prompt.py` | 自然语言空间里更新压缩指南的提示模板。 |
| 端到端流水线 | `experiments/appworld/run_ctxopt_pipeline.py:87`（`main`）、`experiments/appworld/run_all.py` | 复现指南优化与评测的入口。 |
| 凭据占位 | `configs/private_config_dummy.yaml` | 上游只给占位键，运行前需自建 `configs/private_config.yaml`。 |
