# Exact source anchors

页码一律以 `paper/paper-v1.txt` 中的 `===== PDF p.N =====` 标记为准；该标记与论文印刷页码的对应关系是「印刷页 = 4981 + N」（PDF p.1 = p.4982，PDF p.22 = p.5003）。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 「开放接地规划」的两个维度：Grounded Planning（只能用可执行动作集内的动作）与 Open Planning（开放领域、庞大动作集） | §1，PDF p.2 | 给出两个维度的定性定义；不能推出动作集规模阈值、也不能推出跨领域动作集是否必须共享同一套嵌入。 |
| Open Grounded Planning 的任务定义与形式化 | §3.1，PDF p.3 | 给定目标 G 与约束 C，产出 P = (s1, …, sn \| G, C)，且每个 si 必须属于开放动作集 S。原文写作 `s_i ∈ S, 0 ≤ i ≤ n`，下标从 0 起属于笔误。不能推出 S 在推理时如何被截断/检索、也不能推出动作是否带参数。 |
| 任务实例的输入形态（task / method / candidate action set / golden steps 四元组） | §3.1 与 Table 1，PDF p.3 | Table 1 以「How to Activate the Dark Theme on YouTube」给出候选动作集里混杂无关动作的样例；不能推出候选集在每个数据集中的实际大小（见 Table 2）。 |
| Benchmark 的收集范围：daily life、tool use、robot 三个领域；每个类别最多保留 500 条作为评测集；原任务涉及的全部动作保留进动作库 | §3.2，PDF p.3 | 说明评测集与动作库的构造口径；不能推出动作库是否去重、是否为各数据集独立。 |
| Benchmark 规模统计（19 个 wikiHow 类别各 500 条评测样本、full-set 规模与动作数；Tools 的 APIBank 263 / GPT4Tools 500 / ToolAlpaca 201；Robot 的 SayCan 164 / VirtualHome 500） | §3.2，Table 2，PDF p.4 | 给出每个子集的评测集大小、全集大小与动作库大小；不能推出训练集规模（训练集口径见 §5.1）。 |
| wikiHow 作为 in-domain：19 个类别、全集 76,000+ 任务、各类别动作库平均规模超过 20,000 | §3.2.1，PDF p.4 | 说明 in-domain 动作库极大约 2 万条量级、任务量极大；不能推出单条任务的候选动作数（表 2 的 Actions 列是「全集动作数」而非每次给模型的候选数）。 |
| Tools 与 Robot 作为 out-of-domain；Tools 只保留 API 名称与描述、丢弃参数；Robot 只做规划生成、不含视觉处理与动作执行 | §3.2.2，PDF p.4 | 明确本 benchmark 的边界是「计划生成」，不覆盖完整机器人管线；不能推出真实执行器行为。 |
| SayCan 原始数据存在任务与计划不匹配，作者手工补齐 | §3.2.2 脚注 2，PDF p.4；Appendix A，PDF p.12 | 说明 SayCan 子集被人工修正过；不能推出修正覆盖率。 |
| 计划质量的三维评判标准：Completeness / Feasibility / Relevance to the Task | §3.3.1，PDF pp.4–5 | 给出三维度的语义定义；不能推出各维度的量化阈值（prompt 里每维满分 10，但最终只用「哪个计划更好」的成对选择，见 Figure 16）。 |
| 用 ChatGPT 做评判器，并用「交换两份计划顺序后取平均」消除位置偏差、对冗余步骤扣分以抑制长度偏好，并用人工抽样验证 | §3.3.1，PDF p.5；Appendix C，PDF p.12 | 说明评判流程与已采取的纠偏手段；不能推出偏差已被完全消除（Limitation 自述偏差与幻觉仍存在）。 |
| 三个指标定义：Executability = #executable cases / #all cases；Quality = #win cases / #executable cases；Pass Rate = Executability × Quality | §3.3.2，PDF p.5 | 给出指标公式，Pass Rate 为最终指标；不能推出「可执行」是否要求顺序正确（只要求动作全部存在于动作库）。 |
| Task-Retrieve：用任务名检索动作，再让 LLM 选择与排序 | §4，PDF p.5 | 定义 A′ = retrieve(T, A)，P = select&sort(T, A′)。 |
| Plan-Retrieve：先生成初始计划 P0，用 P0 检索动作，再把 P0 作为参考生成最终计划 | §4，PDF p.5 | A′ = retrieve(P0, A)，P = select&sort′(T, A′, P0)。 |
| Step-wise Select：类 ReAct 的逐步选择；三个终止条件（LLM 输出 None / 拒绝从候选列表中选择 / 达到最大迭代数） | §4，PDF pp.5–6 | 给出单步生成—检索—选择的循环与终止条件；不能推出单步失败后的回退行为（该行为定义在 DFS）。 |
| DFS：在 Step-wise Select 上扩展，允许 LLM 放弃当前步的候选并回溯 | §4，PDF p.6 | 定义「无合适候选 → 回溯」这一个搜索操作；不能推出回溯深度、节点扩展数等上限（见 Appendix B）。 |
| Retrieve and Rewrite 框架：先基于参考步生成初始计划 P0（P0 不必由 A0 中的精确步骤组成），再迭代地把不在动作集内的步骤替换为动作集内的动作；迭代停止条件是「全部动作都在动作集内」或达到最大迭代数 | §4 与 Figure 2，PDF p.6 | 定义循环的输入、状态与两个终止条件，并列出改写操作（replace / insert / remove / new-add）。不能推出每轮改写的步数上限与召回数量（见 Appendix B 与代码）。 |
| 被评估的模型：GPT-3.5（gpt-3.5-turbo-1106）、Vicuna-7B-v1.5-16k、以及用少量领域数据微调的 LLaMA-2-7B(SFT) | §5.1，PDF pp.6–7 | 固定被评估模型与其版本；不能推出微调数据的完整配方（只说明每子类抽 200 条、用 GPT-3.5 推理并挑选高质量样本、与 Alpaca 混合、训练 3 epoch）。 |
| 全部动作的向量由 OpenAI text-embedding-ada-002 生成 | §5.1，PDF p.7；Appendix B，PDF p.12 | 说明检索所用嵌入模型；不能推出索引类型与相似度度量（代码中是内积 FAISS 索引，见代码锚点）。 |
| 主结果：in-domain（wikiHow 全类别平均）与 5 个 out-of-domain 数据集上的 Executability / Quality / Pass Rate | §5.2–5.3，Table 3，PDF p.7 | 给出 3 个模型 × 5 个方法的完整指标；不能推出单类别 wikiHow 的分解结果（论文只报全类别平均）。 |
| 结论：SFT 模型在所有方法上最好；不同方法偏重不同（Plan-Retrieve 质量优于 Task-Retrieve、DFS 可执行率更高）；Rewrite 在合理性与完整性上超过 Select 与 DFS | §5.2，PDF p.7 | 给出 in-domain 的比较结论；不能推出该结论对每个 wikiHow 类别都成立。 |
| OOD 结论：除 DFS 外 LLaMA-2-SFT 在多数数据集上超过 GPT-3.5；GPT-3.5 在 tools 数据集上倾向生成自然语言完整步骤而非给定 API 名；SFT 模型在 tools 上使用 DFS 平均计划长度不足 1 | §5.3，PDF p.7 | 给出 OOD 的行为差异与失败归因（训练数据中拒绝比例高导致模型信心不足）；属于作者解释，不能推出该归因已被消融验证。 |
| 错误分析：Rewrite 的不可执行计划中 11.84% 是格式解析错误；DFS 生成的计划中 19.32% 出现两次及以上重复步骤；Table 4 给出 Plan-Retrieve / DFS / Rewrite 与 golden plan 的对照案例 | §5.4 与 Table 4，PDF p.8 | 给出两种方法的失败模式与量级；不能推出其余方法（Task-Retrieve、Plan-Retrieve 之外的检索法）的格式错误率。 |
| 检索数量的影响：Task-Retrieve 中 Pass Rate 随召回数先升后降，GPT-3.5 在召回 20 条时最好；召回 5 条时仍会出现不可执行步骤 | §5.5 与 Figure 3，PDF pp.8–9 | 只在 wikiHow-Computers and Electronics、且只检查输出格式的设置下成立；不能外推到全部数据集或全部方法。 |
| Plan-Retrieve 与 Step-wise Select 的召回数量影响 | Appendix D 与 Figure 4，PDF pp.12–13 | Plan-Retrieve 召回越多可执行率下降；Select 上 Vicuna 与 GPT-3.5 趋势相反。 |
| 实现细节：FastChat 训练、生成 temperature = 1.0、每次生成最多 5 次重试以规避格式错误、对输出做规则审查；各方法的召回数（Plan-Retrieve 每步 2 条、Task-Retrieve 20 条、Step-wise Select 与 DFS 5 条、Rewrite 每轮至多取前三个未替换步骤且每步召回约 10 条）；先对召回步骤去重再交给 LLM；迭代上限 Step-wise Select 20 / DFS 30 / Rewrite 20 | Appendix B，PDF p.12 | 这是复现实验最关键的参数表；不能推出「达到迭代上限」时论文如何处理不完整计划（原文只说仍按可执行计但当质量受损）。**注意：Rewrite 的「每步召回约 10 条」与代码实际做法不完全一致，见下方代码锚点。** |
| 人工评估一致性：随机抽 200 例对 3 模型 × 5 方法做人工评估，与自动评估的 Spearman 相关系数为 80.76% | Appendix C，PDF p.12 | 说明自动评判与人工评判的一致性量级；不能推出该相关系数在每个数据集上都成立（原文未分数据集报告）。 |
| 五个 OOD 数据集的详细 Executability / Quality / Pass Rate | Appendix E，Table 5–9，PDF pp.13–14 | 给出 APIBank / GPT4Tools / ToolAlpaca / VirtualHome / SayCan 的分解结果；不能推出工具数据集的参数级正确性（本 benchmark 不含参数）。 |
| 全部方法的提示词（task-retrieve、plan-retrieve、step-wise select、DFS、rewrite、evaluation） | Appendix F，Figure 5–16，PDF pp.14–22 | 给出各方法的 system instruction 与 few-shot 范例，与代码中的 instruction 字符串逐条对应；不能推出 GPT-3.5 之外的模型如何拼接 system message（Appendix F 开头说明 Vicuna/SFT 把 instruction 放在 user 输入开头）。 |
| 局限：当前实现是「检索 + 生成」两阶段；数据集只做「把任务接地到给定动作集」，不含每个动作的参数；用 ChatGPT 评判仍带来偏差与幻觉 | Limitation，PDF p.9 | 明确作者自认的边界；不能把该方法当作参数化工具调用的通用解法。 |

## 官方代码

行号以 `source-packet.json` 固定的 upstream revision `c9d3cd5` 为准（本地 22/22 文件与该 commit 的 blob 哈希逐一相同）。核心目录为 `official-code/generate/`（计划生成循环）、`official-code/evaluate/`（自动评价）、`official-code/generate/dataset_settings/`（数据集适配与配置）。

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 五个方法的顶层分发 | `official-code/generate/generate_loop.py:82-91`（record 骨架）、`:92`（plan_retrieve）、`:146`（task_retrieve）、`:190`（select）、`:280`（dfs）、`:411`（rewrite）、`:526-527`（未支持方法抛错） | 一个 `process_item` 函数内以 `method` 字符串分支实现全部方法，是所有执行循环的入口。 |
| 运行入口与参数 | `official-code/generate/generate_loop.py:554-562` | CLI：`--model`（默认 chatgpt）、`--dataset`（默认 `wikihow-Computers and Electronics`）、`--method`（默认 plan_retrieve）、`--version`、`--max_workers`（默认 8）；并在启动时 `set_seed(42)`。 |
| 作者机器上的硬编码路径 | `official-code/generate/generate_loop.py:23`、`:563-564` | `sys.path.append("/mnt/ceph_home/guoshiguang2021/code/ogp")` 与 `source_path` / `predict_path` 均为绝对路径，接入前必须修改。 |
| 数据集装配 | `official-code/generate/generate_loop.py:37-74` | 从 `generate/dataset_path_dict.py` 取目录，读入 `actions.txt`、`actions_emb.npy`、`tasks.json`，按数据集名选择适配类。 |
| 断点续跑（跳过已完成任务） | `official-code/generate/generate_loop.py:50-52` | 若 `predict_path` 下已存在同名 `.json` 则从任务列表中剔除，用于重跑与增量执行。 |
| 并发执行与结果落盘 | `official-code/generate/generate_loop.py:584-589`、`:543-551`、`:594-602` | `ThreadPoolExecutor(max_workers=8)` 并发跑任务，每个任务写一份 `json.dumps(record)`，失败项汇总进 `error.json`（全部成功时删除该文件）。 |
| Plan-Retrieve 循环 | `official-code/generate/generate_loop.py:92-145` | 先生成初始计划，再对初始计划中每一步用 `faiss` 内积索引检索 top-2（`:103`），去重后拼进 prompt，最多 5 次重试（`:123-142`）。 |
| Task-Retrieve 循环 | `official-code/generate/generate_loop.py:146-189` | 用任务名嵌入检索 top-20（`:150`），去重、拼 prompt、5 次重试。 |
| Step-wise Select 循环 | `official-code/generate/generate_loop.py:190-279` | `max_select_loops = 20`（`:191`）；每轮生成可能的下一个自然语言步骤 → 检索 top-5（`:233`）→ 让 LLM 从候选中选一个（`:244-264`）；终止条件见 `:227-231` 与 `:277-279`。 |
| Step-wise Select 的拒绝分支行为 | `official-code/generate/generate_loop.py:266-271` | 当 LLM 返回 “None of these” 时只写 `record["status"] = "reject all candidates"`，**不跳出循环**，随后仍把该拒绝标记 append 进 `current_plan` 并继续迭代。这是与 DFS 回滚不同的处理方式，属于代码行为而非论文描述。 |
| DFS 的节点生成与栈式回溯 | `official-code/generate/generate_loop.py:281-310`（`next_node` 生成 3 个候选并以逆序入栈）、`:313`（`max_dfs_loops = 30`）、`:337-345`（弹栈）、`:394-395` 与 `:398-399`（rollback）、`:402-406`（expand） | 用显式栈实现回溯，`[None]` 表示完成；候选步检索同样为 top-5（`:358`）。 |
| Rewrite 的初始计划与在库/待替换标记 | `official-code/generate/generate_loop.py:412-443` | 先用任务名检索 top-20 作为 `<References>`（`:412`、`:532-540`）生成初始计划，再按「是否出现在参考步中」把每一步标为 `{<IN LIB> ...}` 或 `{<TO BE REPLACED> ...}`（`:439-443`）。 |
| Rewrite 主循环与迭代上限 | `official-code/generate/generate_loop.py:436`、`:444-521` | `max_rewrite_loops = 20`；当 `rewrite_ans` 全部以 `{<IN LIB>` 开头时提前退出（`:520-521`），否则继续改写。 |
| Rewrite 每轮只取前三个未替换步骤 | `official-code/generate/generate_loop.py:468` | `not_in_lib_steps = [... <TO BE REPLACED> ...][:3]`，即每轮最多处理前 3 个待替换步骤。 |
| Rewrite 的召回数量策略（与论文表述有差异） | `official-code/generate/generate_loop.py:77-79`、`:470-473` | 每步先检索 100 条，再用 `return_number_based_on_length` 截断：1 个待替换步→10 条、2→5、3→4、4→3、5→2、6→2、7→2、其他→1。论文 Appendix B 只说「每步召回约 10 条」，代码实际是 10/5/4 三档。 |
| Rewrite 的去重与两例 few-shot | `official-code/generate/generate_loop.py:478-479`（小写去重）、`:486-492`（把 `refined_2_shot_examples` 作为 prompt 前缀） | 去重按 `lower()` 比较（其余方法按原串比较）；few-shot 样例定义在 `base_dataset.py:112-116`。 |
| Rewrite 中被注释禁用的自反馈机制 | `official-code/generate/generate_loop.py:451-466` | 一段检测「连续两轮改写结果相同」并调用 `dataset.feedback(...)` 的代码被整块注释掉；`TaskDataset.feedback` 本身是 `raise NotImplementedError`（`base_dataset.py:117-118`）。说明该机制在快照中**未启用、也未实现**。 |
| 数据集名称到目录的映射（24 项：19 wikiHow + 3 Tools + 2 Robot） | `official-code/generate/dataset_path_dict.py:10-35` | 生成与评测两侧共用同一套 `--dataset` / 目录名口径。 |
| 任务与动作库的数据结构 | `official-code/generate/dataset_settings/base_dataset.py:12-24`（`DataItem`）、`:27-34`（`TaskDataset`，用 `faiss.IndexFlatIP` 建内积索引） | 任务字段为 `title / method / steps / file_name / cate_hierarchy`；动作嵌入以 `.npy` 载入后加入 FAISS。 |
| 全部方法指令字符串的唯一定义处 | `official-code/generate/dataset_settings/base_dataset.py:35-110` | 与论文 Appendix F Figure 5–16 一一对应；各方法的 system instruction 都在这里。 |
| 输出格式检查与动作抽取 | `official-code/generate/dataset_settings/base_dataset.py:120-133`（`check_init_plan`）、`:135-152`（`extract_action`，剥掉 `{...}`、序号前缀与 `<IN LIB>`/`<TO BE REPLACED>` 标记）、`:157-171`（`check_list_ans`）、`:173-192`（`check_select_ans`）、`:194-210`（`check_dfs_candidates_ans`）、`:212-235`（`check_refine_ans`） | 这些检查函数就是论文「规则审查 + 5 次重试」的实现位置；返回 `None` 即触发重试。 |
| 初始计划生成是抽象方法 | `official-code/generate/dataset_settings/base_dataset.py:154-155` | `get_no_constraints_actions` 在基类 `raise NotImplementedError`，由 7 个适配类各自实现。 |
| 各数据集的初始计划 few-shot 范式 | `official-code/generate/dataset_settings/wikihow.py:18-39`、`apibank.py:16-32`、`gpt4tools.py:16-32`、`toolalpaca.py:24-42`、`saycan.py:19-39`、`virtualhome.py:17-37` | 每个子集用自己的 few-shot 例子与（工具类特有的）`init_plan_instruction` 覆盖；wikiHow / SayCan / VirtualHome 在 `max_rewrite_loop_times = 10` 后抛 `ValueError`。 |
| 检索接口 | `official-code/utils/embedding.py:13-16`（OpenAI 客户端，密钥与 base_url 为空）、`:20-30`（`text-embedding-ada-002`） | 嵌入是外部服务调用；代码不包含预计算嵌入文件。 |
| 生成/评判共用的 LLM 接口与重试 | `official-code/utils/chat.py:97-121`（`get_ans`，tenacity 指数退避、最多 5 次）、`:113-120`（`save_path` 逐次追加原始 request/response 的 JSONL） | 会话日志按任务落盘到 `<predict_path>_chat/`；`:90` 把 chatgpt 分支的模型名硬编码为 `gpt-3.5-turbo-1106`。 |
| 模型分支与评测侧所用模型名不匹配 | `official-code/utils/chat.py:103-110` 对比 `official-code/evaluate/eval_utils.py:194,196` | `get_ans` 只接受 `"vicuna"`、`"sft"` 或包含 `"chatgpt"` 的字符串，否则 `raise ValueError("model name error")`；而评测侧以 `model="1106"` 调用并且异常会被 `:191-202` 捕获后重试、最终返回空串，外层 `score_tool_wrapper`（`:172-185`）会无限重试。按当前快照原样运行，评分阶段无法通过。 |
| 可执行率（Executability）的计算 | `official-code/evaluate/eval_utils.py:93-105` | `success_rate = 合规计划数 / case_count`，其中「合规」= `count_hallu_baseline` 为 0。 |
| 幻觉步计数 | `official-code/evaluate/eval_utils.py:245-254` | 计划中每个动作若不在本轮检索到的步骤字符串里、且不含 `TO BE REPLACED`，计为一次幻觉。 |
| 质量（win rate）的位置交换实现 | `official-code/evaluate/eval_utils.py:134-160`（跑两遍打分，正序与逆序）、`:188-203`（`auto_score_kit`，`temperature=0.0`，最多 3 次）、`:206-242`（正则取 `<Better Plan>` 并判定胜负） | 对应论文 §3.3.1 的「交换顺序后取平均」；`:224` 把两遍结果相加后除以 2。 |
| 评分提示词 | `official-code/evaluate/eval_prompts.py:1-27` | 与论文 Figure 16 完全一致的完整评判 prompt（三维度 + `<Better Plan>` 输出格式）。 |
| 评测规模与快评开关 | `official-code/evaluate/eval_utils.py:265-268`、`official-code/evaluate/eval_set_size.json` | `eval_fast == "True"` 只取前 100 例，否则最多 500 例；分母用 `eval_set_size.json` 的固定规模（wikiHow 各类 500、APIBank 263、GPT4Tools 500、ToolAlpaca 201、VirtualHome 500、saycan 164）。 |
| 评测侧答案归一化 | `official-code/evaluate/eval_utils.py:278-335` | 去掉序号前缀、`DESCRIPTION` 之后内容、`<IN LIB>` 标记；tools 数据集（GPT4Tools 除外）进一步只取第一个 token（`:329-331`）。 |
| 评测入口与配置位置 | `official-code/evaluate/evaluate.py:17`（`eval_records_dir` 留空，需自行填写）、`:20-25`（四个 CLI 参数）；`official-code/evaluate/eval.sh:2-7` | 评测只读「生成结果目录」，与实际生成过程解耦。 |
| 结果汇总 | `official-code/evaluate/get_score_result.py:5-27`、`:31-47` | 遍历若干 `final_score.json`，按 `win_count / case_count`（可执行且胜出率）、`valid_case_count / case_count`（可执行率）、`win_count / valid_case_count`（质量）打印三列，对应论文的 Pass Rate / Executability / Quality。 |
| 结果文件的字段含义 | `official-code/evaluate/eval_utils.py:118-131` | `final_score.json` 记录 `category_name / case_count / not_none_case_count / valid_case_count / success_rate / total_hallu_count / avg_hallu_count / win_count / win_rate`。 |
