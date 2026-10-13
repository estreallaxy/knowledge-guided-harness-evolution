# Exact source anchors

- 论文页码一律以 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记为准；括号内的 `p.11xx` 为论文明示的会议页码（PDF p.1 = p.1160），仅作交叉核对。
- 代码行号以 `source-packet.json` 固定的 revision `c8571d7` 为准，路径相对本包根目录；上游根 README 已改名为 `official-code/README.upstream.md`。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 有状态、可多轮、可交互三条设计目标与和其他基准的差异 | §1，PDF pp.1–3（pp.1160–1162）；Table 1，PDF p.1；Figure 2，PDF p.3 | 支持"此前基准或为无状态 RESTful 单轮、或为 off-policy 轨迹"的定位，以及本工作时首个同时覆盖状态依赖、模拟用户与动态轨迹评价的说法；不能推出其他基准在任何维度上更弱（Table 1 是作者自评的分类表）。 |
| 世界状态的组成与"有状态工具"占 toolbox 的比例 | §2.1，PDF p.3（p.1162）；Figure 1，PDF p.2 | 世界状态只列出 cellular service、wifi、location service、low battery mode 四项；44% 工具为 stateful。不能推出其他类型的环境状态（文件系统、网络、账户余额等）也被覆盖。 |
| 工具间隐式依赖与嵌套依赖、需要维持调用栈并回溯 | §2.1，PDF p.3–4（pp.1162–1163）；§3 State Dependency，PDF pp.5–6（pp.1164–1165）；Figure 19，PDF p.22（p.1181） | 明确给出两层嵌套（send_message 依赖 cellular，cellular 依赖 low battery mode 关闭）与"依赖只能通过试错发现"；不能推出可迁移到任意工具集的通用依赖发现方法。 |
| 用户模拟器需要 Knowledge Boundary 与 Demonstration 两个附加组件 | §2.2，PDF p.4（p.1163）；Appendix A.4 与 Figure 7，PDF pp.14–15（pp.1173–1174） | 只给 User Goal 会同时产生幻觉与不遵循指令两类失败；加入两组件后两类错误率最低。不能推出二者对任意模拟器实现都必要，也不能推出演示样例可以被 agent 看到（论文明确 demonstration 只对 user 角色可见）。 |
| 用户模拟器提示设计的消融数值 | Table 2，PDF p.4（p.1163） | User Goal 12.4% 幻觉 / 6.20% IF；+Knowledge Boundary 7.75 / 3.88；+Demonstration 6.97 / 0.77；统计基于 1032 条人工标注轨迹（GPT-4o 模拟器 × GPT-4o agent）。不能推出该比例在其他模型组合上不变。 |
| 用户模拟器误差在 agent 之间保持稳定 | Table 3，PDF p.4（p.1163） | 4 次重复 × 1032 条轨迹，Hallucination 6.40–7.15、IF 0.92–1.38、Total 7.78–8.07，支持"agent 间精度比较不被模拟器误差系统性扭曲"；不能推出模拟器完全无误。 |
| Milestone 与 Minefield 的定义及最终分数合成 | §2.3，PDF pp.4–5（pp.1163–1164），Equation 1（PDF p.5） | `score = scoreM+ × I(scoreM− = 0)`：任一 minefield 被匹配到即整条轨迹归零；不能推出 minefield 覆盖所有"不该发生"的行为，也不能推出该乘积形式对部分完成度有良好分辨力。 |
| Milestone 是一张按时间依赖构成的 DAG，评价是"拓扑序约束下的最优映射" | §2.3，PDF p.4–5；Appendix A.7，PDF p.16（p.1175），Equation 2 | 在所有"里程碑顺序为 DAG 某个拓扑排序"的映射中取平均相似度最大者，得到 `scoreM+`；结论是最优映射，不能推出目标轨迹唯一，也不能推出所有多解轨迹都被同等接受。 |
| 相似度计算的三个粒度：列 → 行 → 快照 | Appendix A.7，PDF p.16（p.1175） | 列相似度取 [0,1]（精确匹配、ROUGE-L F、工具调用 AST 匹配等）；行相似度=各列相似度的几何均值；快照相似度=最优行分配下的几何均值。几何均值的用意是"任一列不满足即整体归零"；不能推出所有列都是硬约束（存在 ROUGE-L 这类软匹配）。 |
| 参考里程碑、guardrail 与工具信息流追踪 | Appendix A.7，PDF p.16（p.1175）；Figure 10，PDF p.17（p.1176） | `guardrail_similarity` 检查两里程碑之间某数据库是否被改动；`tool_trace_dependant_similarity` 从参考里程碑抽取工具输出并注入当前里程碑以追踪信息流；不能推出该信息流追踪覆盖全部工具参数。 |
| 中间里程碑用于定位失败原因 | §2.3，PDF pp.4–5；Figure 10，PDF p.17（p.1176） | 给出"最终里程碑失败但中间里程碑显示模型已解决状态依赖"的实例，说明中间信号可用于归因；不能推出中间里程碑与最终成败之间存在定量关系。 |
| 任务效率不由 milestone 衡量 | §2.3，PDF p.5（p.1164）；Appendix D.3，PDF pp.23–24（pp.1182–1183），Table 11 | 效率由互补的轮数（turn count）指标单独统计；Table 11 表注明确"轮数不能孤立解读，模型可能自信地做错并提前结束"；不能把低轮数当作能力强的证据。 |
| 执行环境对依赖工具的并行调用按"墨菲定律"制造竞态 | Appendix A.6，PDF p.16（p.1175）；Figure 17，PDF p.21（p.1180） | 声明竞态被检测到时一定发生，用于惩罚依赖工具的并行调用；不能推出惩罚在实现层面如何落地（消息顺序、状态是否回滚），论文只给原则。 |
| 场景类别定义与困难子集占比 | §3，PDF pp.5–6（pp.1164–1165）；Table 6，PDF p.19（p.1178） | 七类定义（Single/Multiple Tool Call、Single/Multiple User Turn、State Dependency、Canonicalization、Insufficient Information）；85% 场景至少属于一个困难类别；不能推出类别之间互斥（一个场景可多类）。 |
| Insufficient Information 用 minefield 判定"该不做的没做" | §3，PDF p.6（p.1165）；Figure 3，PDF p.5（p.1164）；Figure 20，PDF p.22（p.1181） | 有意识地抽掉必需工具，用 minefield 判断是否幻觉出工具或参数；与 BFCL 的相关性检测、ToolEval 的可解性判定相比更细粒度。不能推出该分数可与其他基准分数直接比较。 |
| 基准规模与统计 | §3，PDF p.5（p.1164）；Table 4，PDF p.5（p.1164）；Table 6/7/8，PDF p.19（p.1178） | 1032 个场景 / 34 个工具 / 11 个领域 / 平均 13.9 轮、3.80 次工具调用；Table 6 为各类别场景数，Table 7/8 为按数据库列与按工具的里程碑覆盖计数；不能推出这些数字在当前或后续上游版本仍成立。 |
| 主要模型结果 | §4，PDF pp.6–8（pp.1165–1167）；Table 5，PDF p.7（p.1166） | 13 个模型的七个类别平均相似度与工具增强列；数值见 `tests-and-reported-results.md`；不能把平均相似度读作任务成功率（论文只报相似度与轮数）。 |
| 提示工程被当作正交变量 | §4，PDF p.6（p.1165）；Appendix D.1 与 Table 9，PDF p.22（p.1181） | 所有模型使用同一最小提示（Figure 8），ReAct 带来约 0–1 分增益且不改变模型排序；不能推出提示工程在任何 harness 中都无收益。 |
| 部分模型缺少工具响应消费能力 | Appendix D.2 与 Table 10，PDF p.23（p.1182） | Gorilla、Command-R 系列无法消费工具响应，因此只会停在 Single Tool Call；不能把这类模型的低分归因于推理能力。 |
| 论文自陈的局限 | §7 Limitations，PDF p.10（p.1169） | 里程碑/矿场人工编写难以扩展；用户模拟器仍有无视忽略的幻觉与指令遵循错误；未覆盖强制确认与鉴权；未覆盖 daemon 类（定时器）工具；部分工具依赖外部 Web 服务影响可复现性。不能推出这些局限在后续版本已解决。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 世界状态与消息总线的库定义 | `official-code/tool_sandbox/common/execution_context.py:35-43`（`DatabaseNamespace`）、`137-187`（`dbs_schemas`） | SETTING / CONTACT / MESSAGING / REMINDER 四个世界状态库，加 SANDBOX 消息库（含 `sender`、`recipient`、`content`、`tool_trace`、`tool_call_exception`、`visible_to` 列）。 |
| 世界状态抽象与"按轮次保留快照"的不变量 | `official-code/tool_sandbox/common/execution_context.py:113-188` | 类文档说明 ExecutionContext 同时持有工具数据库、消息库与 `InteractiveConsole`；所有库按 `sandbox_message_index` 保存完整历史，状态变更时生成快照并与触发消息关联。对应论文 Appendix A.1。 |
| 任意轮次回读世界状态 | `official-code/tool_sandbox/common/execution_context.py:491-525`（`get_most_recent_snapshot_sandbox_message_index`）、`527-555`（`_maybe_create_snapshot`）、`557-605`（`get_database`） | 取"不晚于给定轮次的最近快照"，这是"在任意轨迹的中间状态上做评价"的底座。 |
| 工具写入世界状态的三类 API | `official-code/tool_sandbox/common/execution_context.py:607-679`（`add_to_database`）、`681-714`（`remove_from_database`）、`716-757`（`update_database`） | 分别对应里程碑相似度里的 addition / removal / update 三种目标构造方式。 |
| 全局单例执行上下文 | `official-code/tool_sandbox/common/execution_context.py:759-828`（`_create_global_execution_context` / `get_current_context` / `set_current_context` / `new_context` / `new_context_with_attribute`） | 工具与角色不通过函数参数接收世界状态，而是从全局上下文读写；对应论文 Appendix A.1"作为全局变量、禁止 LLM 直接操作"。 |
| 轨迹序列化 | `official-code/tool_sandbox/common/execution_context.py:345-410`（`to_dict` / `from_dict`）、`411-418`（`__deepcopy__`） | 完整 rollout 可落盘与复原，评价时可离线重放。 |
| 工具调用轨迹记录 | `official-code/tool_sandbox/common/utils.py:257-307`（`add_tool_trace`） | 每次工具调用把 `{tool_name, arguments, result}` 以 JSON 追加进当前 SANDBOX 快照的 `tool_trace` 列，是"trajectory 记录"的实现；文档注明工具抛异常时不产生 trace。 |
| 工具注册、角色可见性与 trace 包装 | `official-code/tool_sandbox/common/utils.py:310-355`（`register_as_tool`） | 装饰器给函数打上 `is_tool` / `visible_to` / `backend` 标记，并在调用前后包一层 trace 记录；嵌套调用内层不再重复记录（`339`）。 |
| 消息可见性（Message Bus 的分角色子视图） | `official-code/tool_sandbox/common/message_conversion.py:27-49`（`Message`，`visible_to` 默认取 sender+recipient）；`official-code/tool_sandbox/roles/base_role.py:96-110`（`filter_messages`） | 每个角色只读到 `visible_to` 包含自己的消息，支撑"demonstration 只对 user 可见"与论文 Figure 4。 |
| 场景类别枚举（与论文正文有差） | `official-code/tool_sandbox/common/execution_context.py:54-98`（`ScenarioCategories`） | 除论文 §3 的七类外，枚举还定义了 `COREFERENCE`、`DISAMBIGUATION`、`ARG_NAME_SCRAMBLED`；经全仓检索，`COREFERENCE` 与 `DISAMBIGUATION` 在 `official-code/` 内无任何引用，属未启用的占位取值。 |
| Milestone / Minefield / 快照约束的数据结构 | `official-code/tool_sandbox/common/evaluation.py:702-734`（`SnapshotConstraint`，含 `reference_milestone_node_index`）、`737-774`（`Milestone`，含 guardrail 库清单）、`777-786`（`Minefield`） | 里程标记的 schema；`Minefield` 是 `Milestone` 的子类，语义差异在最终合成时体现。 |
| 列级相似度度量 | `official-code/tool_sandbox/common/evaluation.py:49-74`（精确匹配）、`76-115`（带 `atol` 的数值接近）、`117-134`（恒为 1）、`137-159`（子串包含）、`162-223`（工具调用匹配）、`225-262`（ROUGE-L） | 对应论文 Appendix A.7 所述"每条列各自定义相似度函数"。 |
| 快照级相似度度量 | `official-code/tool_sandbox/common/evaluation.py:283-344`（`snapshot_similarity`）、`346-394`（`addition_similarity`）、`396-429`（`removal_similarity`）、`431-479`（`update_similarity`）、`481-623`（`tool_trace_dependant_similarity`）、`625-700`（`guardrail_similarity`） | 对应论文 Appendix A.7 的六种快照约束；`tool_trace_dependant_similarity` 依赖 `tool_sandbox/common/tool_trace_extractors.py` 从参考里程碑的工具输出中抽值。 |
| 相似度缓存 | `official-code/tool_sandbox/common/evaluation.py:789-913`（`CachedSimilarityCalculator`） | 按"每个数据库的快照桶"缓存相似度，避免对同一组（当前快照，参考快照）重复计算。 |
| 里程碑 DAG 与 guardrail 自动注入 | `official-code/tool_sandbox/common/evaluation.py:985-1054`（`MilestoneMatcher.__attrs_post_init__`、`_add_guardrail_constraints`） | 未给 `edge_list` 时按链表连边；自动为每个里程碑相对其参考节点与前驱补上 guardrail 约束（除非该库已被显式约束）。 |
| 拓扑序约束下的最优映射求解 | `official-code/tool_sandbox/common/evaluation.py:1056-1163`（`_dfs`）、`1165-1214`（`compute_mapping_and_similarity`） | DFS + 最大堆 + 上界剪枝，最大化里程碑平均相似度，约束是匹配到的里程碑顺序必须是 DAG 的一个拓扑序（Equation 2）。 |
| 最终分数合成与有效轮数 | `official-code/tool_sandbox/common/evaluation.py:960-982`（`EvaluationResult`，`similarity = int(minefield_similarity == 0) * milestone_similarity`）、`917-957`（`get_effective_turn_count`） | 实现 Equation 1；轮数统计排除系统消息、User↔ExecutionEnvironment 消息与用户模拟器 few-shot 消息。 |
| 评价总入口 | `official-code/tool_sandbox/common/evaluation.py:1216-1279`（`Evaluation.evaluate`） | 分别算里程碑与矿场映射，合成相似度并给出轮数；无里程碑时里程碑相似度默认 1，无矿场时默认 0。 |
| 场景播放、评价与轨迹落盘 | `official-code/tool_sandbox/common/scenario.py:60-111`（`play`）、`113-213`（`play_and_evaluate`） | 按"最近接收者发言"推进多轮；把 `pretty_print.txt`、`execution_context.json`、`conversation.json` 写到 `trajectories/<scenario_name>/`，异常时仍先落盘再抛。 |
| 场景扩展与初始世界状态注入 | `official-code/tool_sandbox/common/scenario.py:216-269`（`ScenarioExtension`） | 在基础场景上追加初始消息、工具白/黑名单、里程碑与矿场边表——论文 §3 所述"场景 = 初始世界状态 + 初始消息 + 可用工具 + 里程碑/矿场"的代码形态。 |
| 基础场景（设备初始状态） | `official-code/tool_sandbox/scenarios/base_scenarios.py:31-252` | 构造 base 场景：Import 语句、agent 系统提示、用户模拟器 few-shot，以及 CONTACT / MESSAGING / REMINDER / SETTING 的初始行。 |
| 场景聚合与工具增强变体 | `official-code/tool_sandbox/scenarios/__init__.py:25-131` | 汇总四类场景，并为每个场景派生出 0/3/10/all 干扰工具与四种 schema 打乱变体（对应 Table 5 的增强列）。 |
| 用户模拟器提示的 Demonstration 部分 | `official-code/tool_sandbox/scenarios/user_simulator_few_shot_examples.py:13-43`（`USER_INSTRUCTION`）、`53-414`（示例） | few-shot 对话逐条标注 `visible_to: [RoleType.USER]`，只有用户角色能读到；对应论文 Appendix A.4 与 Figure 7。 |
| 用户模拟器角色与 `end_conversation` | `official-code/tool_sandbox/roles/openai_api_user.py:28-120` | 模拟用户唯一可用的工具是 `end_conversation`；当最近一条消息来自 agent 时才向模型暴露工具，用于主动结束会话。 |
| 有状态工具的嵌套依赖（PermissionError） | `official-code/tool_sandbox/tools/setting.py:61-82`（low battery 开启时联动关闭 cellular/wifi/location）、`95-112`、`125-144`、`187-204`（`get_current_location` 依赖 location_service） | 论文 §2.1 与 Figure 19 所述嵌套状态依赖的可执行来源；依赖不满足时抛 `PermissionError`。 |
| 有状态工具的隐性依赖（ConnectionError） | `official-code/tool_sandbox/tools/messaging.py:36-58`（cellular 关闭时 `send_message_with_phone_number` 抛 `ConnectionError`）、`official-code/tool_sandbox/tools/rapid_api_search_tools.py:63-78`（wifi 关闭时 RapidAPI 请求抛 `ConnectionError`） | 对应论文 Appendix A.2"工具在条件不满足时抛出信息量充足的异常，让 agent 靠试错反推依赖"。 |
| 执行环境：REPL 执行、异常回流与并行调用惩罚 | `official-code/tool_sandbox/roles/execution_environment.py:27-112`（单条消息编译执行，SyntaxError/异常写入 `tool_call_exception` 与 content）、`115-137`、`140-228`（并行调用枚举全部排列，任一排列失败即判该并行调用无效并返回该排列的响应）、`252-330`（角色 `respond`，含把排列顺序的 tool trace 重排回原始顺序） | 论文 Appendix A.6"按墨菲定律保证竞态发生"的实现；注意返回值语义为"检测到失败即返回当前排列的响应"，不是回滚状态。 |
| CLI 入口与结果汇总 | `official-code/tool_sandbox/cli/__init__.py:91-196`（`run_sandbox`）、`197-271`（`main`）；`official-code/tool_sandbox/cli/utils.py:45-103`（角色与模型映射表）、`113-149`（`resolve_scenarios`）、`150-213`（`run_scenario`） | 官方唯一命令入口 `tool_sandbox`；结果写 `result_summary.json`，并记录 git SHA 与是否有本地改动。 |
| 工具 schema 增强 | `official-code/tool_sandbox/common/tool_conversion.py:81-208`（类型提示/工具描述/参数描述/参数名的打乱与还原）、`350-405`（Python 函数转 OpenAI tool schema） | 论文 Appendix A.2.1 四类打乱的实现。 |
