# Exact source anchors

页码按 `paper/paper-v1.pdf`（16 页）计，可用 `paper/paper-v1.txt` 的 `--- PDF page N ---` 标记复核。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 问题设定：推理时在强/弱模型之间二选一 | Abstract 与 §1，PDF p.1 | 路由器在请求级决策；不做多模型级联。 |
| 主打主张：成本降到 **1/2 以下**且不牺牲质量 | Abstract，PDF p.1 | 论文用「>2×」表述；具体随模型对与阈值变化。 |
| 用**人类偏好数据**训练路由器 + 数据增强 | Abstract，PDF p.1；§2–§3，PDF p.2 | 偏好数据来源为 Chatbot Arena 对战。 |
| 四类路由器 | §4（PDF pp.4–6） | 相似度加权、矩阵分解、BERT 分类器、因果语言模型；超参见原文。 |
| 阈值/缩放参数 | §4，PDF p.5 | 论文称指数缩放效果最好并取 γ = 10。 |
| 实验设置：强 `gpt-4-1106-preview`、弱 `Mixtral 8x7B`，随机路由为对照 | §5.1，PDF p.7 | CPT(50%)/CPT(80%) 与 APGR 三个指标的定义见该节。 |
| MT Bench 主结果 | Table 1，PDF p.7 | 表注说明 CPT(50%) 处 MT Bench 8.8 ≈ GPT-4 的 95%。 |
| MMLU 结果 | Table 2，PDF p.7 | 表注说明 CPT(50%) 处 75 ≈ GPT-4 的 92%。 |
| GSM8K 结果 | Table 3，PDF p.8 | 表注说明 CPT(50%) 处 75 ≈ GPT-4 的 87%。 |
| 迁移：路由到训练中未出现的模型对 | Table 4，PDF p.8 | 论文主张路由器有较强泛化；表中给出跨模型对结果。 |
| 成本估计 | §5，PDF p.9 | 论文用 GPT-4 与 Mixtral 8x7B 的每百万 token 价格估算。 |

## 官方代码

行号锚点按 `official-code/` 快照（revision `0b64fdafe049e596a3f5657c219329f24af24198`）计。

| 机制或证据 | 代码位置 | 作用 |
| --- | --- | --- |
| 路由控制器 | `routellm/controller.py:41`（`Controller`） | 对外接口：按 `router-<name>-<threshold>` 形式的模型名路由。 |
| 模型对定义 | `routellm/controller.py:36`（`ModelPair`）、`:31`（`RoutingError`） | 强/弱模型对与路由异常。 |
| 阈值校准 | `routellm/calibrate_threshold.py` | 命令行校准：给定强模型调用比例求阈值。 |
| 路由器实现 | `routellm/routers/similarity_weighted/`、`matrix_factorization/`、`causal_llm/`、`routers.py` | 论文四类路由器中开源实现的三类 + 统一接口。 |
| OpenAI 兼容服务 | `routellm/openai_server.py` | 起本地 OpenAI 兼容端点，便于无侵入替换客户端。 |
| checkpoint 配置 | `config.example.yaml` | 指向 HuggingFace 上的 `routellm/*` 权重。 |
| 评测脚本 | `routellm/evals/benchmarks.py`、`evaluate.py` | 评测入口（本快照未纳入其数据目录）。 |
