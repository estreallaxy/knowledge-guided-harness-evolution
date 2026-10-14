# AutoSaddler × Terminal-Bench 2.0 —— 接入设计与现状（赵星源）

更新时间：2026-10-14。本单元目标是**在 TB2 上复现 AutoSaddler 基线**（阶段二 12 格中的第 3 格）。
本轮（Round 1）只做**零成本的接入准备**：摸清 V2 契约、定下实现方案、写明阻塞项；
付费运行留到下一轮（最小 2 迭代 ≈ $5–10，本轮预算已分配给 GEPA）。

## 1. 上游现状（实测，2026-10-14）

- 官方源码 `../code/`（`microsoft/AutoSaddler` @ `e841543c…`），当前实现是 **V2**
  （`src/autosaddler/v2/`；V1 为遗留，其状态与 worktree 不能被 V2 恢复或导入）。
- 入口：`python -m autosaddler.v2.cli --config <cfg.yaml> --run-id <id>`；引擎可断点续跑
  （`events.jsonl` 为事实源，逐 attempt 去重）。
- **官方只提供两个 scenario 插件**：`fake`（确定性模板）与 `meta_are`（GAIA2）。
  **没有 Terminal-Bench 2.0 / Terminus-2 集成**（README 写 "coming"）→ 必须自写。
- **优化器 provider 只有 `claude`（Anthropic 线）、`codex`（CLI）、`copilot`（BYOK）**，
  没有通用 OpenAI/litellm 通道；`copilot` 的 BYOK 对非 `api.openai.com` 主机不附带 key
  （`registry.py:_copilot_provider_mapping`）。要满足"优化模型 = deepseek-flash"需自写传输层。
- 离线可验证：`uv run python -m autosaddler.v2.cli --config configs/v2/local_template.yaml --run-id local-template`
  （credential-free）+ `uv run --extra dev python -m pytest tests/`（约 200 项，全部离线）。

## 2. TB2 场景插件设计（下轮施工图）

一个 V2 插件必须提供 `ScenarioComponents`（`src/autosaddler/v2/core/ports.py`）：
`harness_space` / `evaluator` / `evidence_builder` / `prompt_pack` / `train_cases` /
`development_cases` / `required_capabilities` / `evaluation_repetitions` / `resolved_entities`。
注册方式二选一：改 `default_registry()`（动 vendored 代码）或走 entry point
`[project.entry-points."autosaddler.scenarios"] tb2 = "…:PLUGIN"`（**推荐**，保持 `../code/` 原样）。

### 2.1 HarnessSpace：不套 git worktree，用目录拷贝

上游 `GitHarnessSpace` 走 git 工作树，要求被优化的 harness 是一个独立 git 仓库且每个候选一个
worktree。我们的候选树只有 ~1.4MB（agents/ + prompt-templates/ + scripts/ + meta_harness.py），
逐候选 `shutil.copytree` 更简单、更快，也不需要在个人工作区里额外造一个 git 仓库 →
自写 `CopyHarnessSpace`，语义与上游一致：
- `seed()`：把 H0 运行入口（`reproductions/zhaoXY/GEPA/terminal-bench-2.0/code` 的同源副本，
  或本单元自带的 `harness-template/`）打成内容寻址的候选；
- `begin_mutation()/apply_mutation()/finalize()`：把候选树复制进会话工作区，交给 provider 编辑；
- **写白名单**：`prompt-templates/`（含 `terminus-kira.txt`）与 `agents/` 下**新增**文件；
  `agents/baseline_kira.py`、`agents/baseline_terminus2.py`（即 H0 本体）与 `scripts/`、`meta_harness.py` 只读；
- `diff()`：逐文件 sha256 比较 → `ChangeSummary`；
- `compose()`：本轮先不支持多父合成（返回显式错误），避免过度实现。

### 2.2 关键设计：候选如何真正生效（materialize）

harbor 以 `--agent agents.baseline_kira:AgentHarness` 导入 agent；`baseline_kira.py:306`
的 `_get_prompt_template_path()` 用 `Path(__file__).parent.parent/"prompt-templates"/"terminus-kira.txt"`
**相对自身文件位置**解析。因此让 harbor 导入**候选树里的** `agents/`，候选的 prompt 与新增 agent
文件即自动生效，无需改 harbor、无需复制 `.venv`（venv 不随候选走，评测统一用固定的 runner venv）。

**2026-10-14 实测（关键坑）**：只把候选树放到 `PYTHONPATH` **不生效** —— 以 runner 目录为 cwd 时，
`sys.path[0]`（cwd）先于 `PYTHONPATH` 命中 runner 自己的 `agents/`。有效的两种做法：
- **D（推荐）**：`cwd = 候选树`，用固定 runner venv 的 python 启动（`sys.path[0]` 即候选树）；
- C：cwd 为中立目录 + `PYTHONPATH=<候选树>`。
两种都实测确认：模块文件与 prompt 路径都落在候选树内。评测器必须显式设置 cwd（不要沿用 runner 目录）。

### 2.3 Evaluator

`async evaluate(candidate, cases, context)`：
1. `harness_space.materialize(candidate, "evaluate")`；
2. 起一个 harbor job：`-p <tb2-split-v1/train> -i <case_id>…`、`-e docker`、
   `-m deepseek/deepseek-v4-flash`、`--n-attempts 1`、`-n <min(len(cases),10)>`、
   环境变量 `PYTHONPATH=<candidate>/agents:<runner>`、`HARBOR_MODEL/HARBOR_ENVIRONMENT/HARBOR_DATASET_PATH`；
3. 逐 trial 解析 `result.json` / `verifier/test-stdout.txt` / `agent/trajectory.json`
   → `Observation`（score = reward；异常/超时记 `task_failure` 且 score 0）；
4. **必须遵守 `context.attempt_sink`**（`completed()` 命中即复用、`start/complete/fail` 逐 attempt 落账），
   否则断点续跑会重复计费。

### 2.4 EvidenceBuilder / PromptPack

- Evidence：只允许来自 train 评测；产出 JSON artifact（逐题 disposition/score + 轨迹摘要），
  形状对齐 `fake` 与 `meta_are` 的写法即可。
- PromptPack：`evolve` / `diagnose_patch` / `reflect` 三类会话，各带 JSON Schema 输出契约
  （引擎按 schema 校验 provider 输出）。TB2 版的 patch 分类学应从上游 `prompting/assets` 出发，
  按 TB2 的失败类型（超时、验证失败、残留文件、未读题）改写；这一块决定复现的忠实度，
  下轮需单独花时间，并在 notes 里声明改写范围。

### 2.5 用例划分

`ScenarioComponents.__post_init__` 强制：train 与 development 用例**不相交**且非空，test 保持 opaque。
TB2 冻结划分是 train 30 / dev 19 / test 40 —— **正好可以直接用**：
`train_cases` = train 30 题（或其中的搜索子集），`development_cases` = dev 19 题，test 40 题不打开。
这比 GEPA 那条线（只能在同一 train 内自造搜索集）更干净，但要注意与 GEPA/meta-harness 线的
"报 train"口径不同 → 终评仍需在 **train 30 题 × 2** 上与 H0 可比，dev 只作发展集。

## 3. 优化器 provider（决策点）

| 方案 | 代价 | 风险 |
| --- | --- | --- |
| A. 自写 litellm `AgentTransport`（复用 `meta-harness/.../litellm_proposer.py` 的进程内工具循环） | ~200–300 行 + 单测 | 需要精确实现 V2 的会话能力契约（read_workspace/edit_workspace/load_skills）与 JSON 契约校验 |
| B. 走 `copilot` 的 BYOK 自定义 provider 指向 DeepSeek | 配置即可（`wire_api: chat_completions`、`model_id: deepseek-flash`） | 上游仅在 host 为 `api.openai.com` 时附加 key；非 OpenAI 主机**不带鉴权头**，未验证能否工作 |

**建议 A**（可控、可测、符合"优化模型 = deepseek-flash"的硬要求）；B 只作快速试错。

## 4. 成本与规模（供预算决策）

引擎每次迭代：`2 × batch_size` 次 train 观测 + 若候选被接受则 development 全量评估。
按 TB2 实测单价（单题单次 $0.03–0.8，train 30 题全量 ×2 = $9.5）：
**最小可行运行（max_iterations=2、batch_size=6、dev=19 题）≈ $5–10**；
paper-scale（`meta_are_full.yaml` 量级：30000 rollouts / 2000 iterations）在本环境不可行，
需在 notes 中声明偏差。**待你确认预算后开跑。**

## 5. 本轮（2026-10-14）已实现并离线验证 ✅

实施时把方案 2.1 的 `CopyHarnessSpace` 换成了**上游自带的 `ComponentMapHarnessSpace`**
（文本组件空间，非 git）：候选 = `{"instruction_prompt": <prompt 文本>}`，身份/增量/校验全部复用上游代码；
"候选如何变成可运行的 harness" 交由 evaluator 负责（逐候选复制 runner 树 + 写入候选 prompt）。
这样少写约 400 行自定义空间代码，风险更低，且写白名单语义仍成立（组件只有 prompt）。

| 文件 | 作用 | 离线测试 |
| --- | --- | --- |
| `plugin/tb2_scenario.py` | 场景插件：设置解析（含 H0 prompt/agent 的 sha256 校验）、evaluator（harbor + `attempt_sink` 断点语义）、证据构建（仅 train）、prompt pack（evolve/diagnose_patch/reflect） | 11 项 |
| `plugin/litellm_transport.py` | litellm 工具循环（read/write/list/grep/bash/finish），工作区路径牢笼、剥离 API key、结构化输出落盘 | 7 项 |
| `plugin/litellm_provider.py` | V2 provider 工厂（settings 精确校验） | 随驱动验证 |
| `plugin/pyproject.toml` | entry point `autosaddler.scenarios:tb2`；`uv pip install --no-deps -e .` 进 `../../code/.venv` | — |
| `run_autosaddler_tb2.py` | 驱动：私有 registry 注入 `litellm` provider + 官方 `build_runtime`（vendored 代码零改动） | — |
| `configs/tb2_terminus_deepseek.yaml` | 运行配置（train 6 题 / dev 6 题 / 预算 40 rollouts / 2 迭代） | — |
| `runner/` | 本单元自带的 TB2 运行入口（独立 .venv；H0 agent 与 prompt 的 sha256 与 H0 单元一致） | — |

**实测证据**：`--check-only` 驱动跑通 → 未改动的 V2 引擎经官方 entry point 装配出
`scenario=tb2` + `provider=litellm`（`scenarios` 列表含 `tb2`，registration source = entry_point）。
全套离线测试 **18/18 通过**（`../code/.venv/bin/python -m unittest discover -s tests -v`）。

### 5.1 oracle 预检（2026-10-14，零成本，全部通过）

| 集合 | 结果 |
| --- | --- |
| train_cases 6 题（portfolio-optimization / bn-fit-modify / pytorch-model-cli / mteb-retrieve / custom-memory-heap-crash / sanitize-git-repo） | **6/6 reward = 1.0**（4 分 15 秒） |
| development_cases 6 题（fix-git / openssl-selfsigned-cert / git-leak-recovery / circuit-fibsqrt / db-wal-recovery / modernize-scientific-stack） | **6/6 reward = 1.0**（modernize 35 秒，其余一次通过） |

- 原定 dev 题 `filter-js-from-html` **已剔除**：oracle 在本环境跑 25 分钟仍未结束（harbor 反复
  "Collecting main service artifacts"），且时限属 dev 集最重一档（agent 900s / verifier 1800s）。
  换成 `modernize-scientific-stack`（600s/600s，oracle 35 秒）。
- 与 GEPA 线一致：**金标准也过不了的题不进任何集合**（GEPA 线已剔除 `mcmc-sampling-stan`）。

## 6. 下一轮待办

1. **付费最小运行**（需预算确认）：先跑 oracle 预检（免费）→
   `../code/.venv/bin/python run_autosaddler_tb2.py --config configs/tb2_terminus_deepseek.yaml --run-id tb2-run-1`
   估算 $4–7（种子 dev 6 + 2 迭代 × 8 train + 被接受的 dev 全量）；dev 6 题的 agent 成本未实测，先用 `--max-iterations 1` 试水也行。
2. 结果与 H0（0.6333）/ GEPA 同协议对照，回填 `results/summary.{md,json}`。
3. 若要做**全 harness 优化**（prompt+工具+中间件，论文原范围）：需补自定义文件级 HarnessSpace
   （见 §2.1 原方案）并在 notes 声明；本轮先交付 prompt 组件范围。

## 6. 已知阻塞 / 需决策

- **预算**：付费运行不在本轮 ¥100 额度内（已分配给 GEPA 搜索 + 终评）。
- **忠实度声明**：TB2 插件、patch 分类学改写、litellm 传输都是实现级适配，结果必须标注
  （与 meta-harness 线、GEPA 线同一处理方式）。
- **是否改 vendored 代码**：建议走 entry point 注册，`../code/` 保持逐字节原样；若必须改
  （例如 provider 注册），改动要进 `adaptation-record.md`。
