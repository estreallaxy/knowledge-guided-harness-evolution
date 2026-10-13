# Tests and reported results

论文报告值，**不是本仓库复跑结果**。

> 数值来自 `paper/paper-v1.txt` 的文本提取，表格串列风险存在；引用前请对照
> `paper/paper-v1.pdf` 核对。指标含义：**CPT(x%)** = 强模型调用比例控制在 x% 时的评测质量；
> **APGR** = 相对随机路由「恢复的质量差距」比例，越高越好。

## 主打主张（Abstract，PDF p.1；上游 README）

| 主张 | 数值 | 说明 |
| --- | --- | --- |
| 成本下降 | **>2×（README 表述为 up to 85% 成本下降）** | 同时保持 **95% GPT-4 表现**（MT Bench） |
| 相对商业路由服务 | 同等表现下 **>40% 更便宜** | 论文附录 E |
| 跨模型对泛化 | 训练未见过的模型对仍可路由 | 见 Table 4 |

## Table 1（PDF p.7）MT Bench，Msgpt-4-1106-preview / MwMixtral-8x7B

| 训练数据 | 路由器 | CPT(50%) | CPT(80%) | APGR | 相对随机 |
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 49.03(±4)% | 78.08(±3)% | 0.500(±0.02) | +0% |
| Darena | BERT | 78.09% | 87.64% | 0.391 | −21.8% |
| Darena | Causal LLM | 28.82% | 77.53% | 0.573 | +14.6% |
| Darena | Matrix Factorization | 25.32% | 74.26% | 0.580 | +16% |
| Darena | SW Ranking | 37.85% | 58.99% | 0.610 | +22.1% |
| Darena+Djudge | BERT | 19.58% | 34.02% | 0.751 | +50.2% |
| Darena+Djudge | Causal LLM | 31.50% | 48.75% | 0.679 | +35.8% |
| Darena+Djudge | Matrix Factorization | 13.40% | 31.31% | **0.802** | +60.4% |
| Darena+Djudge | SW Ranking | 23.21% | 36.04% | 0.759 | +51.8% |

表注：CPT(50%) 处的 MT Bench 分数 8.8 约为 GPT-4（9.3）的 **95%**。

读法提醒：**CPT(50%) 与 CPT(80%) 是「成本」列，越低越省**；BERT 在 MT Bench 上
CPT(50%) 高达 78%（省不下来），即在同质量下反而更贵——不能只引用 APGR。

## Table 2（PDF p.7）5-shot MMLU

| 训练数据 | 路由器 | CPT(50%) | CPT(80%) | APGR | 相对随机 |
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 50.07(±0)% | 79.93(±0)% | 0.500(±0) | +0% |
| Darena | Matrix Factorization | 45.00% | 76.86% | 0.524 | +4.9% |
| Darena | SW Ranking | 55.82% | 80.25% | 0.473 | −5.4% |
| Darena+Dgold | BERT | 41.30% | 72.20% | 0.572 | +14.4% |
| Darena+Dgold | Causal LLM | 35.49% | 70.31% | 0.600 | +19.9% |
| Darena+Dgold | Matrix Factorization | 35.46% | 71.40% | 0.597 | +19.5% |
| Darena+Dgold | SW Ranking | 35.40% | 71.55% | **0.603** | +20.7% |

表注：CPT(50%) 处 MMLU 分数 75 约为 GPT-4（81）的 **92%**。论文说明：只用 Darena 训练时
MMLU 多为分布外样本、路由器接近随机；加入约 1500 条 golden 标注（<2% 训练数据）后显著改善。

## Table 3（PDF p.8）8-shot GSM8K

| 训练数据 | 路由器 | CPT(50%) | CPT(80%) | APGR | 相对随机 |
| --- | --- | ---: | ---: | ---: | ---: |
| — | Random (95% CI) | 50.00(±2)% | 80.08(±1)% | 0.497(±0.01) | +0% |
| Darena | BERT | 58.78% | 83.84% | 0.438 | −11.8% |
| Darena | Matrix Factorization | 53.59% | 85.24% | 0.475 | −4.5% |
| Darena+Djudge | Causal LLM | 33.64% | 63.26% | 0.622 | +25.3% |
| Darena+Djudge | Matrix Factorization | 38.82% | 72.62% | 0.565 | +13.8% |
| Darena+Djudge | SW Ranking | 41.21% | 72.20% | 0.568 | +14.3% |

表注：CPT(50%) 处 GSM8K 分数 75 约为 GPT-4（86）的 **87%**。

## Table 4（PDF p.8）跨模型对迁移（不做任何重训）

| 模型对（强 / 弱） | 路由器 | CPT(50%) | APGR | 相对随机 |
| --- | --- | ---: | ---: | ---: |
| Claude 3 Opus / Claude 3 Sonnet | Random | 49.89% | 0.493 | +0% |
| Claude 3 Opus / Claude 3 Sonnet | SW Ranking | 23.27% | **0.772** | +56.6% |
| Llama 3.1 70B / Llama 3.1 8B | Random | 47.52% | 0.512 | +0% |
| Llama 3.1 70B / Llama 3.1 8B | SW Ranking | 21.18% | **0.767** | +49.8% |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，16 页，提取到 `paper/paper-v1.txt`（含分页标记） |
| Abstract / §2–§5 与 Table 1–4 | 已按本地文本核对 |
| 关键提醒 | 三张表的「CPT」是成本列、越低越省；Darena-only 训练在 MMLU/GSM8K 上接近或低于随机 |
| 路由器权重 | **未纳入**（HuggingFace `routellm/*`） |
| 官方端到端复跑 | **未执行**：需强弱模型凭据与 Arena 偏好数据 |
| 官方单元测试 | **未知**：上游无 tests 目录 |
| 迁移到本 harness 的收益 | **未验证**；且需共同协议放开单一执行模型 |
