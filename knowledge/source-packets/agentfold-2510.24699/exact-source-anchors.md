# Exact source anchors

页码按 `paper/paper-v1.pdf`（26 页）计，可用 `paper/paper-v1.txt` 的 `--- PDF page N ---` 标记复核。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 取舍问题：ReAct 累积原始历史导致饱和，固定全量摘要会不可逆丢细节 | Abstract，PDF p.1 | 论文把这两种失败模式并列为动机；未给量化对比。 |
| 核心机制：每一步同时输出**折叠指令**与**工具调用** | §2，PDF p.2 | 折叠指令有「双尺度」；不能推出任何 agent 都能零样本使用。 |
| 多尺度状态摘要 + 最近一次交互保真 | §2–§3，PDF pp.2–4 | 记忆结构由 folded blocks 与 latest interaction 组成。 |
| 细粒度合并（Granular Condensation） | §3，PDF p.7；§2，PDF p.4 | 允许保留单点细节；与「整段压成结论」是同一指令的两个尺度。 |
| 用 SFT 实现（无 continual pre-training、无 RL） | Abstract，PDF p.1；§3，PDF p.3、p.6 | 训练目标是把折叠行为蒸馏进开源模型；训练数据与脚本未随仓库发布。 |
| 主结果 | Table 1，PDF p.8 | AgentFold-30B-A3B 与开源/闭源 agent 的横向对比。 |
| 上下文长度增长曲线 | §5，PDF p.9；Figure 1，PDF p.1 | 100 轮内约 3.5k → 7k token，次线性增长。 |
| 扩展到 500 轮 | §5，PDF p.10 | 论文报告的长期扩展观察。 |
| 案例研究 | Table 2/3，PDF pp.15–20 | 折叠前后的轨迹对照；样本为个案，不能外推。 |

## 官方代码

行号锚点按 `official-code/` 快照（revision `f72f75d8c3eb842f2bbbab096a12206ff66e270f`）计。

| 机制或证据 | 代码位置 | 作用 |
| --- | --- | --- |
| 推理主入口 | `AgentFold/infer.py` | 加载提示、调模型、执行工具、维护步骤列表的循环。 |
| 折叠的落点 | `AgentFold/infer.py:170`（`update_and_sort_steps`） | 按模型给出的压缩信息重排/替换历史步骤，是「折叠」在代码里的实际位置。 |
| 折叠指令解析 | `AgentFold/infer.py:90`（`extract_tags`）、`:147`（`format_previous_steps`） | 从模型输出里取折叠标签并重排历史。 |
| 工具调用 | `AgentFold/infer.py:117`（`execute_tool`）、`:200`（`call_llm_with_tool`） | 与折叠指令同一步输出的工具调用。 |
| 通用 ReAct 基座 | `inference/react_agent.py:47`（`MultiTurnReactAgent`） | 仓库提供的多轮 ReAct agent 基类。 |
| 搜索/访问工具 | `inference/tool_search.py`、`inference/tool_visit.py` | `infer.py` 依赖的检索与访问工具。 |
| 服务脚本 | `AgentFold/serve.sh` | 用 vLLM 起 8000-8005（目标模型）与 8006（gpt-oss-120b）；`MODEL_PATH` 留空。 |
