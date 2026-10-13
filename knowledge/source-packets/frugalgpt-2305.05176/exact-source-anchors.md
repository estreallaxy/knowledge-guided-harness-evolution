# Exact source anchors

页码按 `paper/paper-v1.pdf`（13 页）计，可用 `paper/paper-v1.txt` 的 `--- PDF page N ---` 标记复核。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 降本三分类：prompt adaptation / LLM approximation / LLM cascade | Abstract 与 §1，PDF p.1；§2，PDF pp.2–3 | 论文把它作为全文的组织框架；FrugalGPT 只是其中 cascade 的一个实例。 |
| 主打结论：以最高 **98%** 的成本下降达到最佳单模型（GPT-4）的表现，或在同等成本下准确率高 4% | Abstract，PDF p.1（L19）；§1，PDF p.2（L102、L111） | 「98%」是最好情况；实际区间见 Table 3。 |
| cascade 的两个组件：生成打分函数 g(q, a) → [0,1] 与 LLM router | §3，PDF p.5 | 打分函数可用简单回归模型训练；阈值决定是否升级模型。 |
| cascade 例子：依次调用 GPT-J → J1-L → GPT-4，阈值 0.37 | §3，PDF pp.5–6；Figure 3，PDF p.8 | 单例说明，不是总体收益。 |
| 供应商与价格差异 | Table 1，PDF p.7 | 12 个商业 API / 5 家供应商，同量输入价格可差两个数量级。 |
| 评测数据集 | Table 2，PDF p.7 | HEADLINES、OVERRULING、COQA（外加 AGNEWS、SCIQ 等）。 |
| 成本节省主结果 | Table 3，PDF p.8 | 见 tests-and-reported-results.md 的转录。 |
| 理论上限（两两模型的 MPI） | Figure 4，PDF p.7 | 论文明确说这是**上界**，不一定可达。 |
| 准确率—成本权衡曲线 | Figure 5，PDF p.9 | 曲线的具体点位需按 PDF 读图，本包未转录数值。 |
| 限制：训练 cascade 需要数据 | §5，PDF p.10 | 论文自述局限，含需要标注/训练数据与价格假设。 |

## 官方代码

行号锚点按 `official-code/` 快照（revision `2b23e6acbd4b39f71912816640dcc59e45aa4b5e`）计。

| 机制或证据 | 代码位置 | 作用 |
| --- | --- | --- |
| cascade 主实现 | `src/FrugalGPT/llmcascade.py:21`（`LLMCascade`） | 按序调用模型、打分、决定是否升级。 |
| 打分器辅助 | `src/FrugalGPT/llmcascade.py:11`（`scorer_text`）、`:296`（`strategy`） | 打分文本构造与策略枚举。 |
| 打分器训练 | `src/FrugalGPT/scoring.py` | 训练/加载回归式打分器的位置。 |
| 组合优化 | `src/FrugalGPT/optimizer.py:58`（`optimize(L_mat, C_mat, d_mat, budget)`）、`:28`（`construct_data`） | 在预算约束下挑模型组合与阈值。 |
| 缓存近似 | `src/FrugalGPT/llmcache.py` | LLM approximation 中的缓存策略。 |
| 供应商与价格表 | `config/serviceinfo.json`、`config/serviceidmap.json` | 需要按当前价格重填；论文表 1 的价格已过时。 |
| 提示模板 | `config/prompt/` | prompt adaptation 用到的提示。 |
