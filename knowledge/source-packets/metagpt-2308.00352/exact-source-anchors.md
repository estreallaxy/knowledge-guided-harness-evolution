# Exact source anchors

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| SOP 角色流水线（五角色顺序与职责） | §3.1，PDF p.4–5（Fig.1 p.2、Fig.3 p.5） | 支持：五个角色 Product Manager、Architect、Project Manager、Engineer、QA Engineer（p.4）；"all agents to work in a sequential manner"（p.5）；PM 产出 PRD → Architect 转 File Lists/Data Structures/Interface Definitions → Project Manager 分发 → Engineer 实现 → QA 写测试。 |
| 结构化产物作为消息传递 | §3.1 p.5、§3.2 p.5–6；附录 B.2 p.18–22（Fig.7–9） | 支持：角色间 "communicate through documents and diagrams (structured outputs) rather than dialogue"（p.6）；附录给出 PRD/系统设计/任务/代码/单测的 Markdown/JSON 产物。 |
| 发布-订阅消息池 | §3.2 "Publish-Subscribe Mechanism" p.6；Fig.2 左 p.4 | 支持：shared message pool 发布结构化消息，角色按 role profile 订阅选择信息（p.6）。 |
| 可执行反馈循环 | §3.3 p.6（ln290–306）；Fig.2 右 p.4 | 支持：Engineer 写并运行单测→收到结果→不通过则调试，"maximum of 3 retries"（p.6）。 |
| 评测：HumanEval / MBPP Pass@1 | §1 p.2、§4.2 p.7；Fig.4 p.7 | 支持：MetaGPT+GPT-4 "85.9% and 87.7% in Pass@1"。注意：无对应数值表，数字只出现在 Fig.4 柱图与正文；Table 7（p.25）是 GPT-4/3.5 变体实验，非此数字出处。 |
| 评测：SoftwareDev 主结果 Table 1 | Table 1 p.8；数据集 §4.1 p.6–7、附录 C.1 p.23 | 支持：Executability 3.75 vs ChatDev 2.25；Tokens 31,255 vs 19,292；Productivity 124.3 vs 248.9；Human Revision Cost 0.83 vs 2.5；Time 三列 762/503/541 s（ChatDev/w-o-FB/MetaGPT）。 |
| 消融：可执行反馈（Fig.4 + Table 9） | §4.4 p.9；Fig.4 p.7；Table 9 p.29 | 支持："+4.2% and +5.4% in Pass@1"；Fig.4 末两对柱（w/o 反馈 → 全量）85.9/87.7；executability 3.67→3.75；revision 2.25→0.83。 |
| 消融：角色数 Table 3 | §4.4 p.9；Table 3 p.9 | 支持：Engineer 单独（1 agent）：Executability 1.0、Revisions 10、$0.915 → 全 4 角色：4.0、2.5、$1.385；#Lines 83→191。 |
| 限制 | 附录 D.1 p.25；§A.1 p.15 | 支持："cannot fully cater to specific scenarios, such as UI and front-end"；用户难以 "interrupt the running process"；summary-based optimizations 只改约束不改结构化通信接口。 |

备注：论文没有"去掉 SOP / 改自由流程"的受控消融——§4.4 仅有角色数与可执行反馈两个消融；Table 1/4 的跨框架比较中基线保留各自流程，不构成 SOP 去除对照（`w/o SOP`、`without SOP`、`ablation.*SOP`、`free-flow` 多关键词零命中）。

## 官方代码

（同节内后续路径省略 `official-code/metagpt/` 前缀。）

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 团队装配与运行入口 | `official-code/metagpt/software_company.py:50-62`；`team.py:80-82, 89-93, 99-107, 122-138` | hire 三角色 → Engineer（n_borg=5）→ QaEngineer（仅 run_tests=True）；invest→run_project 发布需求；run 循环 env.run()。 |
| 五角色订阅链（流水线顺序） | `roles/product_manager.py:37-40`；`roles/architect.py:37-40`；`roles/project_manager.py:37-38`；`roles/engineer.py:91-92`；`roles/qa_engineer.py:44-45` | 各自 set_actions/_watch：PM watch [UserRequirement, PrepareDocuments]；Architect {WritePRD}；PMgr [WriteDesign]；Engineer [WriteTasks, SummarizeCode…]；QA [SummarizeCode, WriteTest, RunCode, DebugError]。 |
| 结构化产物动作（PRD/设计/任务） | `actions/write_prd.py:61, 68-110`；`actions/design_api.py:39, 48-96`；`actions/project_management.py:32, 36-67` | WritePRD→docs.prd；WriteDesign→docs.system_design + Mermaid；WriteTasks→docs.task 文档交接。 |
| 发布-订阅：环境分发 + 角色过滤 | `environment/base_env.py:175-195`（publish_message）、`164-173`（add_roles）、`197-208`（run）；`roles/role.py:305-309`（_watch）、`421-444`（_observe，过滤 433-434）、`446-459`（publish） | env 按 send_to 投递进角色 msg_buffer；角色按 `cause_by in watch` 过滤 news。 |
| 结构化消息 schema | `schema.py:188-197`（Message 字段）、`199-238`（校验/serializer） | content/instruct_content/cause_by/sent_from/send_to，作为消息池与订阅的载荷定义。 |
| 可执行反馈：QA 写测→跑测→调试 | `roles/qa_engineer.py:48-93`（_write_test）、`95-127`（_run_code）、`129-142`（_debug_error）、`144-177`（_act）；`actions/run_code.py:92-118`（subprocess, timeout=10s）、`120-146`；`actions/debug_error.py:48-74` | 运行 `python tests/…`、解析 PASS/FAIL、失败时 LLM 重写代码并循环（论文 §3.3 机制的实现）。 |
| Engineer 写码→SummarizeCode→交 QA | `roles/engineer.py:140-153`、`155-163`、`165-204`（send_to="Edward" :197）、`234-239`（_is_pass） | WriteCode→SummarizeCode 判定通过后把控制流发给 QaEngineer。 |
| CLI 与配置入口 | `software_company.py:81-113`（typer）、`131-157`（--init-config）；`startup.py:9-10`（已废弃转发） | `metagpt "..."` CLI；默认配置搜索路径见 `config2.py:98-112`。 |

行号以 `source-packet.json` 固定的官方代码 revision 为准。
