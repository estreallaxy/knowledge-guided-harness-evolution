# Exact source anchors

页码一律以 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记为准（20 页）。行号一律以 `official-code/` 中保存的文件为准（对应 `source-packet.json` 固定的上游 revision `cebdd8e4eacec1a532ce2c0041db8902217b90ba`）。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 工作记忆切分为 cross-trial memory 与 in-trial memory（working memory）；后者被现有工作忽视 | §1，PDF pp.1–2；§2.2，PDF p.3 | 提出"优化 working memory 管理"这一问题设定。不能推出 cross-trial memory 方法无效，也不能推出任意长上下文模型都能解决该问题。 |
| STANDARD 策略：把全部历史 action-observation pair 直接放进上下文 | §1 Figure 1，PDF p.1；§2.2，PDF p.3 | 定义了被对比的基线。文中未给出 STANDARD 的代码实现细节，基线行为须以代码为准。 |
| HiAgent 总体四步流程：(1) 先产出 subgoal $g_i$；(2) 生成动作完成它；(3) 判定完成后合成 summarized observation $s_i$ 并遮蔽该段的 action-observation pairs；(4) 需要时检索回来 | §3.1 Overview，PDF p.3；Figure 2，PDF p.3 | 描述机制顺序与触发时机。原文未给出摘要模型的具体提示词（正文 §3.3 的 "Appendix ??" 是出版版中的坏引用），实现细节须看 Appendix C.1 与代码。 |
| 工作记忆形式化：$m_t=(g_0,s_0,...,g_{n-1},s_{n-1},g_n,a_0^n,o_1^n,...)$，检索时 $m'_t$ 中该子目标换回原始 pair | §3.1，PDF p.3 | 给出保留"当前 subgoal 全部 pair + 历史 subgoal 摘要"这一结构。不能推出检索后是否仍保留摘要（公式写法本身不严格）。 |
| Subgoal-based 分层管理：当前 subgoal 保留全部 pair，过去 subgoal 只留摘要观察 | §3.2，PDF pp.3–4 | 明确"分层"只作用于 in-trial 记忆，不涉及外部数据库或跨任务记忆。 |
| Observation summarization 定义 $s_i=S(g_i,o_0,a_0,...,o_t)$，且须同时判断当前 subgoal 是否达成 | §3.3，PDF p.4；提示词 Appendix C.1，PDF pp.19–20 | 摘要内容以 subgoal 为条件。不能推出摘要由独立模型完成——论文实现细节说明用一个 GPT-4 同时充当 policy 与 summarizer。 |
| Trajectory retrieval：LLM 像生成动作一样生成 retrieval 函数，取回某过去 subgoal 的完整 pair | §3.4，PDF p.4；示例 Appendix B.2，PDF pp.18–19（`4 Subgoal: Examine errors...` / `Action: retrieve(3)`） | 说明检索是模型主动发起、按 subgoal 编号的。不能推出检索一定有收益、也不能推出检索的编号规则（论文示例只出现单编号 `retrieve(3)`）。 |
| 评测任务：Blocksworld、Gripper、Tyreworld、Barman、Jericho，均"typically require more than 20 steps" | §4.1 Evaluation Tasks，PDF p.4；任务动作空间与示例 Appendix A，PDF pp.13–15 | 五个任务全部来自 AgentBoard。不能推出方法在其他环境（网页、软件工程、多轮对话）同样有效。 |
| 指标：Progress Rate、Success Rate、Average Steps、Context Efficiency（in-trial 上下文平均 token 数）、Run Time | §4.1 Evaluation Metrics，PDF p.4 | 定义五个指标。Context Efficiency 在论文中以"STANDARD = 100%"的相对值报告，不是绝对 token 数。 |
| 实现细节：max step limit 30，每任务 1 个 in-context example，GPT-4（gpt-4-turbo）同时作 policy 与 summarization model，temperature 0，top_p 1 | §4.1 Implementation Details，PDF p.4 | 固定实验条件。注意与官方脚本 `evaluate_model.sh` 的 `STEP=50` 不一致，见下"配置"文档。 |
| 主结果：SR/PR/Steps/Context/Time，Overall SR 21.00 → 42.00、PR 38.61 → 62.55、Steps 26.41 → 22.61、Context -35.02%、Time -19.42% | §4.2，PDF p.5，Table 1 | 五任务均值与逐任务数值。Gripper 的 PR 下降 1.5%；不能推出所有任务都改善。 |
| 消融：w/o OS、w/o TR、w/o OS & TR（在 Tyreworld 上） | §5.1，PDF pp.5–6；Table 2，PDF p.7 | 分别支持"摘要必要""检索必要""两者结合更优"。正文数字与表格数字有两处不一致（见下"证据缺口"）。 |
| 不同步数下的 progress rate：HiAgent 每档都更高，且随步数继续增长 | §5.2，PDF p.6；Figure 3，PDF p.7 | 支持"长时域更稳"。Figure 3 的原始数据未随包提供，无法核对。 |
| 对照实验：仅做任务分解（w. TD，不遮蔽历史）SR 40.0、Context 112.8%；HiAgent SR 60.0、Context 73.6% | §5.3，PDF p.6；Table 3，PDF p.8 | 支持"收益不只来自任务分解，遮蔽历史带来上下文效率"。仅 Tyreworld 一个环境。 |
| 可执行动作比例（executability）：HiAgent 长步数下仍保持 80% 以上，STANDARD 在 blocksworld 步数 >20 时降到 10% 以下 | §5.4，PDF p.6；Figure 4，PDF p.7 | 支持"长上下文损害可执行性"。数值只来自图中读值，无原始表格。 |
| 统计显著性：Wilcoxon signed-rank，Progress Rate 统计量 144.0 / p=2.38e-5；Average Steps 统计量 112.5 / p=0.0016 | §5.5，PDF pp.6–7 | 支持两个指标上的配对差异非随机。未给出样本量与检验设置细节。 |
| 与 Tree-Planner 对比（Tyreworld）：HiAgent SR 60.0% / Context 100.0%，Tree-Planner SR 40.0% / Context 94.7% | Appendix C.2，PDF p.20，Table 4 | 支持相对该规划基线的优势。单一环境、单一对比方法。 |
| 局限：极长时域仍受记忆约束；实验只在 benchmark 上，未验证真实场景 | Limitation，PDF p.8 | 论文自述的边界。不能推出方法在真实应用、跨 trial 场景下有效。 |
| STANDARD 与 HiAgent 的完整提示示例（含 subgoal/retrieve 的对话形态） | Appendix B.1 / B.2，PDF pp.15–19 | 可用于对照代码生成的提示词。示例是人工整理的展示，不等价于代码逐字输出。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| HiAgent agent 的注册名与类 | `official-code/agentboard/agents/cme_final.py:21-23` | `@registry.register_agent("ContextEfficientAgentV2")`；论文中的 HIAGENT 即此类。注意四个 yaml 里写的是 `ContextEfficientAgent`，实际由命令行 `--agent` 覆盖。 |
| 分层记忆的数据结构：记忆是"块"的列表，每块是一串 action-observation pair | `official-code/agentboard/agents/cme_final.py:92-95`、`104` | `reset` 建首块，`update` 每次追加 `[("Action", ...), ("Observation", ...)]`。对比 STANDARD：`official-code/agentboard/agents/vanilla_agent.py:75`、`84-85` 用扁平列表，无分块。 |
| 子目标生成与入记忆：输出中不含 `Subgoal` 视为动作，否则取首行为新 subgoal 并压入记忆块 | `official-code/agentboard/agents/cme_final.py:303-314` | 触发条件是模型自己的输出格式，而不是外部规划器。`self.subgoal_idx` 在生成新 subgoal 时清空（`:312`）。 |
| 历史序列化：按 `Subgoal` 标出的边界切块，逐块替换 | `official-code/agentboard/agents/cme_final.py:114-139` | 少于等于 1 个 subgoal 时直接退化为 vanilla 序列化（`:130-132`）。 |
| 已完成子目标 → 摘要替换（Observation Summarization） | `official-code/agentboard/agents/cme_final.py:146-164` | 取 `history[index+1:obs_index+1]` 为该块轨迹，先剔除 `check valid` 动作（`:151`），再调 `TrajectorySummarizer`（`:159`）。 |
| 当前（最后一个）子目标保留全部原始 pair | `official-code/agentboard/agents/cme_final.py:166-174` | 与论文 §3.2 一致：只有"过去"的 subgoal 被摘要。 |
| 全可观测环境下关闭摘要，用块内最后一条 observation 代替（论文消融 "w/o OS" 的启发式） | `official-code/agentboard/agents/cme_final.py:115-120`、`140-145` | 由环境变量 `EVALTASK` 决定：名字里含 `gripper` 或 `blocksworld` 时 `summarization = False`。这是代码行为，论文未描述该任务级开关。 |
| Trajectory Retrieval：保留被检索子目标的原始块 | `official-code/agentboard/agents/cme_final.py:125`、`135-137` | `keep_subgoal_index_list = [_-1 for _ in self.subgoal_idx]` 把 1-based 的 subgoal 编号映射到块下标，命中则跳过摘要、原样保留。 |
| `retrieve(...)` 的解析正则与递归重跑 | `official-code/agentboard/agents/cme_final.py:14-19`、`321-326` | 正则 `retrieve\((\d+(?:, \d+)*)\)`；命中后累加编号并**递归**调用 `self.run(...)`。见下"代码行为差异"：递归返回值未被采用。 |
| 子目标协议指令（何时输出 `Subgoal:` / `Action:`、`retrieve` 用法）注入到 instruction | `official-code/agentboard/agents/cme_final.py:190-203` | 提示词层面的机制开关；文件内保留了三段被注释的旧版本措辞（`:177-189`），可用于追溯协议演化。 |
| `memory_size` 只截断末尾窗口 | `official-code/agentboard/agents/cme_final.py:222` | `history = self.memory[-self.memory_size:]`，默认 100；官方脚本再显式传 `--memory_size 100`。 |
| 上下文长度自适应截断：超长则逐块丢弃最旧的块直到放得下 | `official-code/agentboard/agents/cme_final.py:231-244` | 以 `num_tokens > context_length - max_tokens` 为条件；这是与摘要机制并存的第二道长度控制。 |
| 摘要器实现 | `official-code/agentboard/agents/summarize.py:1-31` | 用同一个 `llm_model` 生成摘要；失败时退化为"块内最后一条 Observation"（`:46-53`）。 |
| 摘要提示词的实际措辞 | `official-code/agentboard/agents/summarize.py:33-44` | 要求"1-2 句、覆盖关键动作与最终结果"，**未包含**论文 Appendix C.1 要求的"判断 subgoal 是否达成、只输出一行"。论文与代码在这一点上不一致。 |
| 驱动循环：`agent.reset → agent.run → env.step → agent.update`，逐 step 记录 action/observation/prompt/progress | `official-code/agentboard/tasks/pddl.py:114-190`（run 在 `:138`，update 在 `:159`） | 说明机制嵌在标准 agent 循环里，不改环境接口。 |
| Agent 抽象接口 | `official-code/agentboard/agents/base_agent.py:1-15` | `reset/update/run/from_config` 四个方法，是接入新 harness 时的替换点。 |
| LLM 接口：生成、token 计数、用量记账 | `official-code/agentboard/llm/openai_gpt.py:74-96`（generate）、`:97-129`（`num_tokens_from_messages`）、`:50-59`（usage）、`:130-148`（from_config） | 上下文截断依赖 `num_tokens_from_messages`；Context Efficiency 只能由外部按 usage/prompt 统计，代码里没有该指标。 |
| 评估入口与命令行覆盖 | `official-code/agentboard/eval_main.py:122-125`（`--agent`/`--memory_size` 覆盖 yaml）、`:203-209`（成功率/进度率汇总） | 说明 yaml 的 `agent.name` 不是最终生效值。 |
| 注册表 | `official-code/agentboard/common/registry.py:47-60`（`register_agent`）、`:163-164`（`get_agent_class`） | agent 类的发现机制。 |
| STANDARD 基线（对照） | `official-code/agentboard/agents/vanilla_agent.py:11`、`75`、`84-85`、`107` | 完整历史直接入 prompt，无分块、无摘要、无检索。 |
| 提示资产（instruction + 1 个 in-context example） | `official-code/agentboard/prompts/ContextAgent/pddl.json`、`pddl_wretrieval.json`、`jericho.json`、`official-code/agentboard/prompts/VanillaAgent/pddl_vanilla_prompt.json` | 各任务实际加载的 instruction/examples；`pddl_wretrieval.json` 是唯一含 `retrieve(3)` 示例的资产。 |

## 代码行为差异（读码所得，未在本地运行验证）

| 现象 | 位置 | 说明 |
| --- | --- | --- |
| `retrieve(...)` 的递归调用没有 return | `official-code/agentboard/agents/cme_final.py:321-326`、`331` | 递归帧里模型新生成的动作被丢弃，外层仍把字面量 `retrieve(n)` 作为 action 返回给 `tasks/pddl.py:138` 并交给 `env.step`。快照中没有任何环境或任务代码拦截 `retrieve(`（Python 代码里仅 `cme_final.py:321` 命中；另一次出现是提示资产 `prompts/ContextAgent/pddl_wretrieval.json` 的演示示例）。与论文 Appendix B.2（PDF pp.18–19）中 `retrieve(3)` 后直接接 `Action: check valid actions` 的呈现不一致。 |
| yaml 内的 agent 名是旧名 | `official-code/eval_configs/hiagent/*.yaml:11` | 四个配置均写 `name: ContextEfficientAgent`，而注册表中只有 `ContextEfficientAgentV2`；`evaluate_model.sh` 用 `--agent ContextEfficientAgentV2` 覆盖后才可运行。 |
| `EVALTASK` 环境变量是隐藏开关 | `official-code/agentboard/agents/cme_final.py:115-120`；`official-code/evaluate_model.sh:7` | 是否启用摘要取决于 shell 里 `export EVALTASK=...` 的取值，yaml 中不存在该字段；脚本里硬编码为 `blocksworld`。 |
| 官方脚本步数与论文不符 | `official-code/evaluate_model.sh:5`（`export STEP=50`）、`official-code/eval_configs/hiagent/blocksworld.yaml:2`（`max_num_steps: 30`） | 命令行优先（`eval_main.py:73`），因此脚本实际跑 50 步，论文 §4.1 写 30 步。复现论文数值时需自行比对。 |
| 快照内 `tasks/__init__.py` 引用了缺失模块 | `official-code/agentboard/tasks/__init__.py:10-11` | `pddl_structured`、`babyai_train` 在快照中不存在，`eval_main.py` 无法直接 import 成功；这是官方仓库的既有状态，不是本包裁剪造成。 |

## 证据缺口

| 项目 | 说明 |
| --- | --- |
| 正文与表格数字不一致 | §5.1（PDF p.6）称 w/o TR 的 average steps "increased by 1.2"，Table 2（PDF p.7）为 `+2.2`；称 w/o OS & TR 的 success rate "decreasing by 20%"，Table 2 为 `-30.0`。 |
| 引用错位 | Appendix C.2（PDF p.20）把任务分解对照写成"As shown in Table 2"，该对照实际在 Table 3（PDF p.8）。§3.3（PDF p.4）的 "Appendix ??" 是坏引用。 |
| 无原始数据 | Figure 3、Figure 4 的逐步曲线只以图像给出，未随论文或仓库提供数据表；本包不含 assets 图片。 |
| 无检索次数统计 | 论文未报告 `retrieve(...)` 的实际调用频率与命中率；代码中该路径的递归返回值问题也未被讨论。 |
| Context Efficiency 不可由本包直接复算 | 指标定义在论文 §4.1，但计算脚本不在仓库快照中（快照只逐 step 记录 prompt 与 usage）。 |
