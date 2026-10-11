# Tests and reported results

## 论文报告结果

以下数值为论文结果，不是本仓库复跑结果。页码为 PDF 实际页。

| 实验 | 设置 | 结果（论文） | 位置 |
| --- | --- | --- | --- |
| MATH 定性对照 | 每题测 3 次 | AutoGen T1 3/3、T2 2/3；AutoGPT 0/3、LangChain ReAct 0/3 等 | Table 2, p.19 |
| MATH 全量 | 5000 题，GPT-4 后端 | AutoGen 69.48% vs GPT-4 55.18% | p.7、p.20 |
| MATH level-5 | 120 题 | 仅图内有数（正文未逐方法列出） | Figure 4a, p.7 |
| NQ | 前 500 题 | 无交互检索版 F1 23.40/Recall 62.60；19.4% 问题触发 Update Context | p.23 |
| NQ（图值） | 图 4b | AutoGen 25.88/66.65、W/O 22.79/62.59、DPR 15.12/58.56（F1/Recall，%） | Figure 4b, p.7 |
| ALFWorld | 134 unseen 任务 | ReAct 54/66、ALFChat-2 54/63、ALFChat-3 69/77（avg/best-of-3，%） | Table 3, p.25 |
| OptiGuide | 100 题（安全/不安全各半） | 识别不安全代码 F1 +8%（GPT-4）/ +35%（GPT-3.5）；交互节省 3.03x–4.88x | p.8、Table 4 p.27 |
| A5 动态群聊 | 12 个手工任务 | GPT-4 成功率 11/12（群聊）；GPT-3.5 9/12 | Table 5, p.28 |
| MiniWob++ | 49 任务 | MiniWobChat 52.8%，比 RCI 低 3.6% | p.32、Figure 18 p.33 |

NQ 图值与正文存在口径差（正文注明"前 500 题"）；引用时注明来源位置。

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| MATH 提示与判分 | `official-code/autogen/math_utils.py:4-23` |
| MATH 专用代理（含 Wolfram 变体） | `official-code/autogen/agentchat/contrib/math_user_proxy_agent.py:126-352` |
| 检索方案（A2）建库/查询 | `official-code/autogen/retrieve_utils.py:239/278`、`official-code/autogen/agentchat/contrib/retrieve_user_proxy_agent.py` |
| 代码执行行为 | `official-code/autogen/code_utils.py:216-393` |

快照内无 `test/` 目录与 pytest 配置（find 实测）；README 引用的 `test/twoagent.py` 不在快照内。数据集本体（MATH/NQ/ALFWorld/MiniWob++/OptiGuide）均未纳入来源包。

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，43 页。 |
| 论文锚点与本地全文核对 | 已通过（含 Figure 4a–d 图内数值的坐标交叉验证，正文未列出的 level-5 数据仅作参考）。 |
| 官方代码版本与核心文件 | 已固定并保存。 |
| 大型数据与完整 benchmark 环境 | 未纳入来源包。 |
| 官方端到端实验复跑 | 尚未执行（快照无测试入口）。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
