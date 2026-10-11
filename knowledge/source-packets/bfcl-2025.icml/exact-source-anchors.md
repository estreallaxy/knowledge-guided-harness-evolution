# Exact source anchors

页码一律取自 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记，与 PDF 实际页码一致（全文 22 页）。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| BFCL 的四部分结构与总规模 | §1，PDF p.1；§3，PDF p.3 | 单轮、众包、多轮、agentic 四部分；5 551 条 question-function-answer 对，覆盖 Python、Java、JavaScript、REST、SQL。不能推出各分类的条目数与计分权重。 |
| AST 子串匹配替代真实执行 | §1，PDF p.2；§4.1，PDF p.5 | 用 Python `ast` 提取函数名与参数，参数取值落在预定义合法集合即判对，以此规避大规模执行。不能推出类型规则细节（在 Appendix H）。 |
| 单轮五类场景的形式化定义 | §3.1，PDF p.3；Appendix C.1–C.2，PDF pp.14–15 | Simple/Multiple/Parallel/Parallel Multiple 由候选函数数 \|F\| 与期望调用数 \|f̂(P)\| 定义；Relevance 至少一次调用，Irrelevance 期望零调用。不能推出各分类用例数量。 |
| 众包数据的规模与来源 | §3.2，PDF p.3；Appendix E.2，PDF pp.16–17 | 2024-02-26 至 2024-04-01 收集 64 517 条真实单轮查询，ROUGE-L 与 embedding 去重、剔除公开测试集、人工最小编辑后入库；摘要称 2 251 条入选。不能推出众包条目在总榜中的权重。 |
| 多轮数据四类与"每轮双检查" | §3.3、§4.4，PDF pp.4–5；Appendix D.1–D.2，PDF p.15 | Base/Missing Parameters/Missing Functions/Long Context；一条条目只有在所有轮次同时通过 state-based 与 response-based 检查才算正确。不能推出检查失败时的错误码或重试策略。 |
| Agentic 三类数据 | §3.4，PDF p.4 | Web Search（DuckDuckGo 检索 + 网页抓取两个工具）、Memory（五个领域、每段对话后记录快照，评测时以空历史 + 快照提问）、SQL（以 JSON schema 表达 SELECT/INSERT/UPDATE/DELETE 并允许组合调用）。不能推出三类的条目数。 |
| 执行响应匹配的三种比较方式 | §4.2，PDF p.5 | 确定性输出用精确匹配；时间敏感输出同时执行真值调用与模型调用再比较；嵌套 list/dict 只比长度与键是否存在。不能推出这些类别在当前代码版本中仍参与打分（见下方代码行为）。 |
| AST 与执行评测的一致性 | §4.3，PDF p.5，Figure 3 | 报告 AST summary 与 Exec summary 在单轮数据集上强相关。原文未给出相关系数、回归斜率或置信区间。 |
| Agentic 的精确匹配评测 | §4.5，PDF p.5；Appendix J，PDF p.22 | 只评测专门的 answer 字段，归一化（转小写、去标点）后两者相同才算对；附录给出 `{'answer': ..., 'context': ...}` 的格式指令。不能推出代码实现是对 answer 字段做严格相等（实现差异见代码表）。 |
| 总榜结果 | §5.1，Table 1，PDF p.6 | 71 行模型的 Overall Acc 与 21 个分类列。不能推出当前 leaderboard 的实时状态（论文是快照）。 |
| FC 模式与 prompting 模式的差异 | §5.1，PDF pp.5–6 | prompting 模型解码问题约为 FC 模型的 3 倍（412.93 vs 182.5，共 4 251 条）；已成功解码的 multiple 类目中 FC 模型函数调用个数错误更多（77.5 vs 21），parallel multiple 类似。不能推出该趋势适用于全部模型，也不能推出 FC 模式普遍更差（原文称更强模型常在 prompting 模式更好）。 |
| 并行调用能力的回退 | §5.3，PDF p.7 | 观察到 o1-2024-12-17-FC 与 claude-3-5-sonnet-20241022-FC 的并行调用能力"回退甚至移除"。原文只是假设原因（链式调用下逐次调用可能更准），不能推出因果结论。 |
| 多轮确定性错误分类 | §5.4.1，PDF p.7，Figure 4 | 五类错误：Empty Turn Response、Instance State Mismatch、Execution Response Mismatch、Force Termination、API Error；图 4 标注该数据集共 800 条。不能推出各类错误在全部模型上的具体分布数值。 |
| 多轮 LLM-as-judge 错误分析 | §5.4.2，PDF pp.7–8，Figure 5；Appendix F，PDF pp.18–19 | 用 GPT-4o-08-06 作 judge，把失败归为三类根因（环境状态/用户请求/函数文档理解），并给出完整 judge 提示模板。不能推出 judge 与人工标注的一致率或偏差幅度。 |
| 数据污染检测 | §5.5，PDF pp.8–9，Tables 2–3，Figures 6–7 | 用 PPL 与 char-NLL 对比 single-turn 与 crowd-sourced：多数模型在 crowd-sourced 上更低，Salesforce xLAM-7B 反向上升（PPL 3.67→5.09）。不能推出所有模型都被判定为污染，也不能推出单一指标即可定案。 |
| 记忆管理失败模式 | §5.6，PDF p.9 | 记忆类目最好成绩是 o1-2024-12-17 (FC) 的 12%；失败模式包括键粒度不一致、跳过 `list keys` 直接猜键、单次失败即放弃。不能推出该结论在论文之后的新版本仍成立。 |
| 数据生成与校验流程 | Appendix E.1–E.3，PDF pp.16–17；Appendix B，PDF pp.13–14 | 收集/预处理/生成/变换/校验五阶段；五种增强（并行、多函数、多并行、参数删除、函数删除）；多轮自建 API 覆盖 Vehicle Control、Trading Bot、Travel Booking、File System、Messaging、Twitter、Ticket Booking、Math 八个领域，用 Persona Hub 生成多样化提问。不能推出各领域的条目数。 |
| 系统提示与步数上限 | Appendix A，PDF p.13 | 给出 prompting 模型使用的统一系统提示全文。不能推出 FC 模式的工具定义注入方式（在代码中）。 |
| AST 匹配细则 | Appendix H，PDF pp.20–21 | 并行调用顺序无关、任一预测可匹配任一真值、只要有真值未被匹配则整条失败；int/float 跨语言规则；字符串大小写与标点归一化；list/tuple 顺序敏感；dict 键序无关、list of dict 顺序敏感。不能推出嵌套的深度上限或浮点容差。 |
| 跨语言转换 | Appendix H，PDF p.22 | Java/JavaScript 的代码字符串先用 Tree-Sitter 转成 Python 等价物再评测（例如 Java long 必须以 `L` 结尾）。不能推出固定的 tree-sitter 站点包版本（该约束在 pyproject.toml 中）。 |
| 函数调用能力随时间的变化 | Appendix G，PDF p.20，Figure 8 | 2023 与 2024 初的模型在规模化函数调用上不可靠，随模型规模与后训练目标引入而改善。不能推出严格单调改进或无平台期。 |

## 官方代码

行号以 `source-packet.json` 固定的 revision `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8` 为准。文件为逐字节复制，行号与上游一致。

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| AST 匹配主入口与分类分派 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:33-61` | 类别名含 `parallel` 走无序并行匹配器，含 `multiple` 走多函数匹配器，否则要求恰好一个调用并走单函数匹配器。 |
| 并行调用的无序匹配（全有或全无） | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:554-620` | 逐条真值调用在模型输出中寻找任意未被占用的匹配项；只要有一条真值找不到匹配即整条失败，对齐 Appendix H 的 Parallel Tool Calls 规则。 |
| 保序并行匹配器（当前未被调用） | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:518-551` | 函数已定义但 `ast_checker` 不调用它；当前所有 parallel 类别都按无序匹配处理。 |
| 单函数检查：函数名、必需参数、类型与取值 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:333-515` | 先比对函数名，再检查必需参数缺失、非法参数名，随后按声明类型分派到各类型检查器。 |
| 字符串归一化 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:174-182` | 去掉空格与 `,./-_*^` 并转小写、单引号转双引号；对应 Appendix H 的 STRING 规则。 |
| list/tuple 顺序敏感、dict 键序无关、list of dict 顺序敏感 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:204-235`、`238-298`、`301-330` | 三个类型检查器分别实现 Appendix H 的 LIST AND TUPLE、DICTIONARY、LIST OF DICTIONARIES 规则。 |
| Python 允许 int→float 自动转换 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:442-448` | 仅在 `Language.PYTHON` 且期望 `float` 且值为 `int` 时转换，其余语言按字面类型判定。 |
| Java/JS 参数先转成 Python 等价物 | `official-code/bfcl_eval/eval_checker/ast_eval/ast_checker.py:387-425`；`.../type_convertor/java_type_converter.py`、`js_type_converter.py` | 对应 Appendix H 的 Cross-Language Notes；`java_type_converter` 内含 `"3.14f"→3.14`、`"123L"→123` 等自测断言。 |
| 多轮主检查：逐轮 state + response | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:9-129` | 每一轮分别执行模型调用与真值调用（各自持有独立实例），先比状态再比响应，任一失败即整条失败。 |
| 状态比较的具体口径 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:162-194`、`259-279` | 逐实例逐属性比较，跳过以下划线开头的私有属性。 |
| 响应比较：真值执行结果是模型执行结果的乱序子序列 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:197-220`、`282-300`；`multi_turn_utils.py:103-108` | 对齐 §4.4 的 response-based evaluation；空响应判定由 `is_empty_execute_response` 承担。 |
| 空真值轮不在此处判失败 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:94-98` | miss_func/miss_param 轮（真值为空）直接 `continue`，模型在该轮输出多余调用不会被这条路径捕获。 |
| 多轮无关检查器：已定义、已 import、未被调用 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:132-159`；`official-code/bfcl_eval/eval_checker/eval_runner.py:13` | `multi_turn_irrelevance_checker` 只在 eval_runner 的 import 列表中出现，没有任何调用点；当前评估不会用它判定"应无调用却输出了调用"。 |
| 方法调用顺序检查器：调用点被注释 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_checker.py:122-127`、`223-253` | 定义存在，但 `multi_turn_checker` 中的调用被注释掉，当前不生效。 |
| 函数调用执行与后端状态加载 | `official-code/bfcl_eval/eval_checker/multi_turn_eval/multi_turn_utils.py:13-101` | 按 `CLASS_FILE_PATH_MAPPING` 动态 import 后端类、深拷贝 `initial_config` 调 `_load_scenario`、执行调用串并返回实例状态。 |
| 多轮后端类清单与状态处理规则 | `official-code/bfcl_eval/constants/executable_backend_config.py:1-47` | 12 个后端类到模块与函数文档文件的映射；`MathAPI` 无状态，Memory 三类与 WebSearch 的状态不写入推理日志。 |
| Agentic 精确匹配的实现 | `official-code/bfcl_eval/eval_checker/agentic_eval/agentic_checker.py:6-36`（主函数）、`41-49`（归一化辅助函数） | 归一化后用词边界正则 `\b...\b` 在模型回复中搜索任一候选答案。这与论文 §4.5 所述"只取 answer 字段做严格相等"不同：实现是整条回复的包含式匹配。 |
| Agentic 条目评估：只取最后一条非函数调用消息 | `official-code/bfcl_eval/eval_checker/eval_runner.py:72-163` | 中间的函数调用步骤不参与打分；找不到"最后一条无法解码为函数调用的消息"即整条判失败。 |
| 评估总入口与类别分派 | `official-code/bfcl_eval/eval_checker/eval_runner.py:668-756` | relevance/irrelevance、format_sensitivity、multi_turn、agentic 各有 runner，其余单轮类别走 `ast_file_runner`。 |
| 当前跳过 executable/rest/sql/chatable 类别 | `official-code/bfcl_eval/eval_checker/eval_runner.py:792-800`；`official-code/bfcl_eval/constants/category_mapping.py:11-25` | 这些类别在 `runner()` 中被显式 `continue`，且在 category_mapping 中被注释；论文 §4.2 的执行响应匹配在当前版本不参与计分。 |
| 总榜权重 | `official-code/bfcl_eval/eval_checker/eval_runner_helper.py:509-519` | `calculate_percentage_weighted_accuracy(..., [10, 10, 10, 30, 40])`，对应 Live / Non-Live / Irrelevance / Multi-Turn / Agentic。 |\n| 权重变更的官方记录（V3 每段 33% → V4） | `official-code/CHANGELOG.md:10-23` | 2025-07-17 的 BFCL V4 条目给出新旧权重表：Live/Non-Live/Multi-Turn 各 33 → 10/10/30，Irrelevance 与 Agentic 从 0 → 10/40；同条目还说明 `Non-Live Acc`、`Live Acc` 不再计入 Irrelevance/Relevance。 |
| 加权与不加权准确率、缺失类别按 0 计 | `official-code/bfcl_eval/eval_checker/eval_runner_helper.py:15-35`、`38-62` | 未被评估的类别在总分计算中按 0 处理（判定阈值 `display_accuracy == "N/A"`）。 |
| CLI 子命令 | `official-code/bfcl_eval/__main__.py:60-311` | `version`、`test-categories`、`models`、`generate`、`results`、`evaluate`、`scores`。 |
| 推理生成入口 | `official-code/bfcl_eval/_llm_response_generation.py:28-94`（`get_args`、`build_handler`）、`223-`（`generate_results`）、`359`（`main`）；`official-code/openfunctions_evaluation.py:1-11` | 旧结构兼容入口，等价于 `python -m bfcl_eval.openfunctions_evaluation`。 |
| 模型接口（抽象） | `official-code/bfcl_eval/model_handler/base_handler.py:31-92`、`756-766` | `inference()` 按 FC/prompting × 单轮/多轮四路分派；`decode_ast`、`decode_execute` 是子类必须实现的抽象接口（评测器只依赖这两个方法）。 |
| 输出格式解析器 | `official-code/bfcl_eval/model_handler/parser/{json,java,js,xml}_parser.py` | 把模型原始输出解析成 `[{func_name: params}]`；`json_parser` 先用正则截取 JSON 数组再 `json.loads`。 |
| 语言与返回格式枚举 | `official-code/bfcl_eval/constants/enums.py:1-36` | `Language` 决定 AST 类型检查分支；`ReturnFormat` 决定 `decode_ast` 的解析路径。 |
| 提示模板与步数上限 | `official-code/bfcl_eval/constants/default_prompts.py:1-60` | `MAXIMUM_STEP_LIMIT = 20`；默认系统提示格式 `ret_fmt=python&tool_call_tag=False&func_doc_fmt=json&prompt_fmt=plaintext&style=classic`。 |
| 目录与项目根解析 | `official-code/bfcl_eval/constants/eval_config.py:1-45` | `BFCL_PROJECT_ROOT`、`result/`、`score/`、`.env`、`data/` 数据集路径（本包未纳入 data/）。 |
| 类别清单与类别组 | `official-code/bfcl_eval/constants/category_mapping.py:1-88` | 计分/非计分类别与 `all`、`multi_turn`、`live`、`agentic` 等组的映射。 |
| 函数文档格式校验脚本 | `official-code/bfcl_eval/scripts/check_func_doc_format.py:1-25` 起 | 校验 function doc 的三字段结构与参数类型枚举，直接打印出问题的条目 ID。 |
| 多轮函数文档编译 | `official-code/bfcl_eval/scripts/compile_multi_turn_func_doc.py`、`_compile_helper.py` | 从后端类方法签名生成 `multi_turn_func_doc/*.json`，是理解多轮函数文档来源的入口。 |
