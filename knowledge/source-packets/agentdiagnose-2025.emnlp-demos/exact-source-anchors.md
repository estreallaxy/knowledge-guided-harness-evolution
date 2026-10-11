# Exact source anchors

页码以 `paper/paper-v1.txt` 的 `===== PDF p.N =====` 标记为准。行号以 `source-packet.json` 固定的官方代码 revision（`6ac7bedd`）为准。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 工具要解决的问题：现有流程只看最终成败，决策过程不透明 | 摘要、§1，PDF p.1 | 论文把 AgentXRay、AgentOps、AgentEval 等归为“只回放”或“只给整体分”；不能推出论文对这些工具做过实测复现或对照实验。 |
| 两个模块：评估模块 + 可视化模块 | 摘要、§1，PDF p.1；§3，PDF p.3 | 支持“评估给数值分、可视化给难以量化的性质”；不能推出两者在实现上解耦（代码里 dashboard 直接复用评估产物）。 |
| 五个能力维度清单 | 摘要、§1，PDF pp.1–2；§3 Key Trajectory Metrics，PDF p.3，Figure 2 | 维度为 backtracking & exploration、task decomposition、observation reading、self-verification、objective quality；不能推出这五项覆盖了 agent 失败的全部成因，或可跨领域直接沿用。 |
| 评估不依赖参考轨迹 | §1，PDF p.1；§3，PDF p.3 | 明确写 “without requiring reference trajectories”“without needing a predetermined correct sequence”；不能推出它可替代有 gold 的轨迹匹配评测。 |
| 评估器可扩展 | §3，PDF p.3 | 原文 “supports adding customized evaluators to access any property of interest”；仓库内置只有三个 scorer，不能推出“任意属性”都已实现。 |
| Backtracking & Exploration 的评分口径 | §3，PDF p.3；附录 A，PDF p.9 | 1–4 分档，另设 N/A 分支（agent 全程走对、无需回溯时不计分）；不能推出代码对 N/A 的处理与标注者口径一致。 |
| Task Decomposition 的评分口径 | §3，PDF p.3；附录 A，PDF p.9 | 1–4 分档；论文称分解多发生在第一步但“revisiting and updating plans”能进一步提升；不能推出评分器会区分“首次分解”与“后续更新”。 |
| Self-verification 的评分口径 | §3，PDF pp.3–4；附录 A，PDF p.9 | 强调“beyond checking if the final answer is satisfying”，要看每步推理对总目标的意识；不能推出它与 objective quality 的边界在标注中无重叠。 |
| Observation Reading 的评分口径 | §3，PDF p.4；附录 A，PDF p.9 | 评 agent 是否正确理解 observation 并抓住关键信息；不能推出它衡量的是页面渲染或工具输出质量。 |
| Objective Quality 的评分口径 | §3，PDF p.4；附录 A，PDF p.9 | 评“任务目标本身”的清晰度与可执行性，不评 agent 表现；不能推出低分目标必然导致任务失败。 |
| 可视化三视图：t-SNE 嵌入、词云、状态转移时间线 | §3 Key Property Visualizer，PDF p.4；§4.2，PDF p.5，Figure 1/Figure 5 | 支持三类视图的存在与用途；不能从截图推出交互细节、缩放或筛选行为。 |
| 动作词抽取的六个内置选项 | §3，PDF p.4 | root verbs / root nouns / root verb-noun pairs / all verbs / all nouns / all verb-noun pairs；不能推出这些选项在论文中被逐一评测过。 |
| 词性抽取与嵌入模型 | §3，PDF p.4 | 用 Berkeley Neural Parser (benepar) 从 reasoning 抽动词名词，默认嵌入模型 Qwen3-Embedding-0.6B；不能推出换用其他嵌入模型的效果。 |
| 终端单命令调用评估器 | §4.1，PDF p.5，Listing 1 | 给出 `python evaluate_trajectories.py --input ./input.json --scorers reasoning_quality objective_quality navigation_path --output-json output.json`；与代码一致，但论文未给出依赖安装与 API key 配置。 |
| 结果立即本地保存，可生成交互条形图 | §4.1，PDF p.4 | 支持“运行后结果落盘、可在 dashboard 分 tab 展示分数分布”；不能推出多机或增量并发下的行为。 |
| 用评估分数筛选高质量训练数据 | §4.1–§4.2，PDF pp.4–5，Figure 3、Figure 4 | Figure 3 给 backtrack & explore 分布与探索行为样例，Figure 4 给 objective quality 分布与对应目标文本；论文只给“top 6k”一档阈值，不能推出其他阈值的效果。 |
| 人评相关性 | §5.1，PDF p.6，Table 1 | 30 条人工标注轨迹，Pearson/Spearman/Kendall 三系数；不能推出该相关性可迁移到其他领域、模型或标注者群体。 |
| 数据筛选的下游收益 | §5.2，PDF p.6，Figure 6 | WebArena + NNetNav 设定 + BrowserGym + Llama-3.1-8B；top-6k 比 46k 全集高 0.98 个绝对百分点、只用 13% 数据；不能推出对其他基座模型或非 web 领域成立。 |
| 导航图定位失败的实例 | §4.2，PDF p.5，Figure 5 | openweb_351 在 login 与 search 页之间死循环，据此推测错误在 login 处理；这是单例说明，不是统计结论。 |
| 已知局限 | §7，PDF p.6 | 主要面向 web navigation；coding 与多模态场景未验证；评估依赖 LLM judge，可靠性有待专用评估器替换。 |
| 人评与伦理 | §8，PDF p.7 | 30 条轨迹、学生志愿者标注、未收集人口属性、任务无敏感信息。 |
| 公开地址 | §1 脚注 1–2，PDF p.1 | 项目页 `https://AgentDiagnose.live/`、代码库 `https://github.com/oootttyyy/AgentDiagnose`。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| 动作与轨迹的数据模型 | `official-code/evaluator/trajectory.py:30-70`、`:73-78`、`:171-206` | `Action` 字段含 reasoning/observation/action_type/url/label_line/label_pos/nth_step 及动词-名词标注字段；`Trajectory` 为 objective + actions + task_website + reward；`to_json`/`from_json` 定义官方轨迹 JSON 形态。 |
| 多来源轨迹解析（本文档接入点） | `official-code/evaluator/trajectory.py:80-169`（browsergym pickle）、`:208-338`（CUGA）、`:340-460`（Synatra）、`:462-637`（AgentTrek） | 四种解析器把不同 harness 产物归一化为同一 `Action` 序列，是接入新 harness 时最直接的扩展位置。 |
| 动作词/动词-名词对抽取 | `official-code/evaluator/trajectory.py:18-27`、`:639-649`、`:661-719` | 加载 spaCy `en_core_web_md` + benepar；按 VERB→dobj NOUN 依存取对，首个对作为 root verb/noun。 |
| 评分器注册表 | `official-code/evaluator/scorers/__init__.py:7-24` | 三个内置名（navigation_path / objective_quality / reasoning_quality）到类的映射。 |
| 评分结果结构与基类 | `official-code/evaluator/scorers/base.py:12-25`、`:28-54` | `ScorerResult` 含 score/description/details/confidence/weight，`weighted_score` 供加权聚合。 |
| LLM 评分器与 dry-run | `official-code/evaluator/scorers/base.py:57-100` | `generate_prompt`/`parse_response` 抽象；`dry_run` 用 tiktoken `cl100k_base` 只数 token 不发请求。 |
| 评分细则提示词 | `official-code/evaluator/scorers/prompts/prompt.py:1-50`、`:52-61`、`:63-80`、`:82-88` | 把论文附录 A 的 1–4 分档写进 system prompt，并要求返回固定 JSON 结构；objective 有独立 prompt。 |
| 推理质量四维评分与聚合 | `official-code/evaluator/scorers/reasoning_quality.py:17-29`、`:43-70`、`:72-146`、`:148-175` | 一次调用同时产出 backtrack/task decomposition/observation reading/self-verification；backtrack 为 N/A 时按三维平均；保留原始分与 justification。 |
| 目标质量评分与重试 | `official-code/evaluator/scorers/objective_quality.py:38-46`、`:48-89`、`:91-146` | 单独评 objective；最多重试 2 次，并记录 token usage。 |
| 导航路径指标 | `official-code/evaluator/scorers/navigation_path_scorer.py:27-58`、`:60-133`、`:135-149` | 统计 overall_length、backtrack_count、domain_transitions、unique_urls_visited、actions_per_url_segment。**注意 `score` 恒为 `0.0`，该 scorer 只产出 details**，与论文 Figure 5 的导航图用途一致，但不进入加权总分。 |
| 批量评估编排 | `official-code/evaluate_trajectories.py:74-270` | 默认三评分器与各自模型映射、断点续跑、每 50 条中间落盘、`ThreadPoolExecutor` 并发。 |
| 从已有输出恢复（省 API 调用） | `official-code/evaluate_trajectories.py:100-119`、`:134-161` | 读取 `--output-json` 中已评过的 trajectory，只评剩下的；写盘用临时文件 + rename。 |
| 结果汇总 | `official-code/evaluate_trajectories.py:279-303` | 按各 scorer 的 weight 求 `overall_score`，输出为 pandas DataFrame。 |
| CLI 参数面 | `official-code/evaluate_trajectories.py:331-349`、`:352-386` | `--input`/`--output-json`/`--scorers`/`--temperature`/`--dry-run`/`--no-parallel`/`--max-workers`/`--limit`/`--web-dashboard`/`--dashboard-port`/`--dashboard-host`/`--enable-tunnel`/`--tunnel-token`；`--web-dashboard` 直接拉起 dashboard。 |
| Judge 聚合与配置化装配 | `official-code/evaluator/evaluator.py:11-44`、`:47-99`、`:101-115`、`:126-147` | `EvaluationResult`；聚合方式支持 weighted_average/min/max；`from_config` 按 `module` + `class` 动态导入 scorer。 |
| Dashboard HTTP 接口面 | `official-code/dashboard/backend/main.py:79-531` | `/api/results`、`/api/trajectories`、动作与截图、图表、过滤器、嵌入、tagcloud 全部路由集中在 `_setup_routes`。 |
| 轨迹列表分页与瘦身 | `official-code/dashboard/backend/main.py:87-165` | `summary_only` 时丢弃 observation/image_encoding/reasoning，仅留动作数与首步预览。 |
| 轨迹详情、动作与截图 | `official-code/dashboard/backend/main.py:208-291` | 详情、动作列表、单动作、单步截图分端点按需返回。 |
| 结果与轨迹预处理 | `official-code/dashboard/backend/main.py:544-606`、`:607-639` | 把 `ScorerResult` 转成前端可用的分数结构；抽取轨迹摘要。 |
| 图表数据生成 | `official-code/dashboard/backend/main.py:640-681`（overview）、`:682-847`（reasoning quality）、`:876-972`（objective quality） | 服务端生成 plotly 图数据；分数区间与轨迹 id 绑定，供点选筛选。 |
| 过滤器状态机 | `official-code/dashboard/backend/main.py:318-373`、`:848-875`、`:973-984` | 增/删/清空过滤器；按过滤器求交集得到当前轨迹 id 集合。 |
| 嵌入视点到轨迹的反查 | `official-code/dashboard/backend/main.py:375-521`、`:1196-1251`、`:1252-1394` | 从 t-SNE 选点经 metadata 反查 `trajectory_file`，含精确匹配与模糊回退，再注册为过滤器。 |
| 词云数据读取 | `official-code/dashboard/backend/main.py:523-531`、`:985-1195` | 读取预生成 tag cloud JSON，不在请求内重算。 |
| Dashboard 进程编排 | `official-code/dashboard/web_dashboard.py:43-74`、`:325-341`、`:343-402`、`:425-532` | `npm install` 检查、pickle 传递结果并 spawn uvicorn 子进程、静态服务 + `/api` 反代；前端端口 N，后端端口 N+1000。 |
| 公网隧道 | `official-code/dashboard/web_dashboard.py:76-312`、`:579-589` | cloudflared（quick/named）或 localhost.run SSH 反隧道；`create_web_dashboard` 是评估脚本调用入口。 |
| 嵌入生成（Qwen3 + FAISS） | `official-code/generate_embeddings.py:18-46`、`:80-122`、`:144-194`、`:196-232`、`:279-337` | 动词/名词/动词-名词对三套 `Qwen/Qwen3-Embedding-0.6B` 嵌入与 FAISS 索引，落盘 pkl+npy+faiss。 |
| 动词-名词标注流程 | `official-code/generate_verb_nouns.py:16-69`、`:72-127` | 批量为轨迹写入 root verb/noun 与 pairs，输出 `*_labeled` 目录与统计 JSON。 |
| 词云生成入口 | `official-code/generate_tag_cloud.py:89-160`、`:163-269` | 两种来源（reasoning n-gram / action phrases）与 `--all-ngrams` 批量模式。 |
| 推理 n-gram 词云与 TF-IDF | `official-code/visualization/reasoning_tag_cloud.py:11-42`、`:108-141`、`:144-240`、`:296-309` | 停用词表、`min_frequency`/`max_frequency_rate` 阈值、TF-IDF 权重，并保留每个 tag 的 `trajectories_using` 供反查。 |
| 动作短语词云 | `official-code/visualization/action_phrases_tag_cloud.py:11-21`、`:22-59`、`:100-154`、`:209-221` | verbs / nouns / pairs 三型短语词云。 |
| 一键端到端流程 | `official-code/launch_dashboard.sh:1-25` | 依次跑标注 → 两种词云 → 嵌入 → 评估 → 起 dashboard（host 0.0.0.0，port 8080）。 |
| 前端页面与后端契约 | `official-code/dashboard/src/routes/+page.svelte:4-10`、`:18-21`、`:48-51` | 页面只通过 `/api` 相对路径取数；但 **`src/lib/components/` 下 7 个被 import 的组件在快照中不存在**，前端无法直接构建。 |
| 前端运行时配置 | `official-code/dashboard/static/runtime-config.js:1-4` | 内含一个硬编码 ngrok 后端地址，属于作者演示环境的残留，接入时需替换。 |
