# 决策论驱动的信念演化：完整详细版

## 一、完整 Method

现有 Harness 自动优化通常由通用 coding agent 根据任务 Trace、评测反馈和 Harness 代码提出修改。Trace 能揭示执行在哪个阶段失败、哪些行为发生了变化以及候选取得了怎样的结果，却不能完整给出潜在故障原因及其对应的解决机制。因此，候选修改仍主要依赖 coding agent 在当前推理中调用到的内部知识，容易遗漏尚未被模型主动想到的方法，也难以判断不同解释之间还缺少什么证据。

为扩展系统能够考虑的解释和干预，我们引入经过整理和核验的论文方法与工程经验，从中提取可能的故障机制、适用条件、干预路径和可观察结果，同时保留自主探索，以提出外部材料尚未覆盖的新解释与新方案。Trace、外部方法和自主探索分别提供当前任务的行为证据、已有机制假设与开放式候选，共同扩大 Harness 演化能够考虑的决策空间。

然而，更多候选和更多证据也会带来更复杂的不确定性。同一个失败可能源于方法本身不适用、代码接入错误、机制没有激活、评测器存在偏差或运行环境已经变化；同一个分数也可能掩盖新能力、旧能力、严重失败、成本和稳定性之间的差异。现有优化流程即使能够动态搜索候选，也常分别使用不同规则控制修改、评测、额外分析、回滚和停止，难以判断下一步究竟应该继续修改 Harness，先执行一次判别性探针，增加更可靠的评测，重新分析已有证据，还是保留当前版本。如果这些动作没有统一面向最终 Harness 选择进行比较，系统可能在结论已经稳定时继续运行，也可能在关键不确定性尚未消除时过早提交。

为同时解决优化机制不足与不确定性下动作选择分散的问题，我们将 Harness 演化建模为一个持续更新信念的序贯决策过程。外部方法提供故障、干预、机制和观察之间的候选关系，当前任务产生的证据则校准这些关系是否成立；无法被现有解释覆盖的现象继续保留为未知状态。系统在同一决策空间中比较知识引导修改、自主修改、判别性取证、额外计算、提交、回滚和停止，并依据它们对最终 Harness 选择可能产生的改善，以及相应的成本、风险和不可逆影响，选择下一步行动。每次只执行一个真实动作，再用其结果更新故障解释、方法迁移、接入状态、机制激活、候选效果和评测可靠性。由此，系统既能利用更广泛的外部机制，也能逐步学会当前证据下最值得执行什么，以及何时已经没有必要继续演化。

### 决策模型组织与检索阶段：如何组织和检索外部方法

论文提供的不只是一个可选组件，还包含对问题因果结构的隐含判断：哪些变量造成失败、干预会改变什么中介状态、哪些现象能够被观察、最终改善应体现在哪个指标上。若只保存方法摘要，就无法区分方法不适用、接入错误和评测缺失；若把论文效果直接当作当前任务概率，又会忽略模型、工具和数据条件差异，产生没有本地证据支撑的确定性。

本阶段把每个外部方法编译为决策模型片段，而不是结论性规则。片段包含潜在故障变量、可执行干预、预期中介、观测模型、效用影响、适用条件和来源强度。外部证据可以确定图中哪些关系值得考虑，却不能直接固定当前任务上的概率；所有参数都带校准状态和依赖组，使多个来自同一实验的结果不会被当作独立证据重复计算。loop 外组织只执行一次并冻结目录；loop 内检索在每代父 Harness 的 trace 形成 `DecisionNeed` 后执行，只读取冻结目录和截至本代开始已经提交的长期信念状态。

检索从 `DecisionNeed` 指定的当前决策、竞争解释和缺失边开始，先召回可能改变这些边的方法片段，再根据预期决策影响而非文本相似度排序。返回结果包括可接入的模型片段、需要补充的本地观测和仍为 unknown 的参数。下一阶段因此获得一组能够进入统一影响图的假设，并清楚知道哪些关系来自外部来源、哪些必须由当前 Harness 的 trace 校准。

来源中的潜变量、机制链、观察条件、排除条件和 persistence 关系需要语义理解，不能由字符串规则完整恢复。loop 外，`OptimizerHarness` 先固定论文段落、代码符号、配置、消融与结果锚点，再用 `SOURCE_DECISION_MODEL_COMPILATION` 请求 `OptimizerLLM` 提出片段字段、候选图边、dependency group 和 unknown 假设；程序逐字段核验来源、代码路径、图类型和证据依赖。loop 内，`TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS` 从 trace-role 事件和已提交 belief 提出竞争原因、高损失状态、未决边及所需观察；程序核验事件、代码、状态 revision 和数据角色。硬过滤、依赖闭包与来源去重完全由程序执行，`BUNDLE_DECISION_RELEVANCE_RERANK` 只能在剩余 bundle 中解释潜在终局影响和迁移缺口，不能恢复硬排除片段或写入本地概率。

原始来源首先保存为不可变包：

```text
SourcePacket = {
  source_id,
  paper_version,
  official_code_version,
  exact_source_anchors,
  algorithm_and_ablation_claims,
  configs_tests_and_reported_results,
  source_grade,
  alignment_status,
  extraction_revision
}
```

每个可迁移方法编译为：

```text
DecisionModelFragment = {
  fragment_id,
  method_id,
  source_anchors,
  target_failure_causes,
  required_regime,
  preconditions_and_exclusions,
  intervention,
  latent_state_dependencies,
  expected_trace_observations,
  expected_outcomes,
  utility_dimensions,
  safety_and_legacy_constraints,
  observation_model_claims,
  source_dependency_group,
  evidence_scope,
  unresolved_assumptions,
  status,
  revision,
  llm_call_ids,
  field_validation_status
}
```

`source_dependency_group` 标记多篇论文、代码说明或实验表是否实际复用了同一数据和同一结果，防止把重复报道当成独立证据。`observation_model_claims` 只记录“在什么条件下应看到什么”，不能直接写成当前任务上的固定似然。`unresolved_assumptions` 保留无法从论文或代码确认的条件，未知不能被默认成满足。

所有片段被编译进带版本的信念影响图：

```text
TaskRegime ───────┐
FailureCause ─────┼─> MethodTransfer ─> IntegrationCorrect
MethodEvidence ───┘                           │
                                              v
                                   MechanismActivated ─> Outcome
EvidenceAction ─> Observation ─> BeliefUpdate ─────────────┤
EvolutionAction ─> HarnessVersion ─────────────────────────┤
ComputationAction ─> EstimatorState ───────────────────────┤
EvaluatorReliability ──────────────────────────────────────┘
                                                           v
                                                     TerminalUtility
```

图中至少包含 `unknown_failure`、`unknown_transfer` 和 `observation_misspecification` 状态。否则新 trace 只能在预设解释之间重新分配概率，即使所有解释都错也会越来越自信。版本变更采用 persistence edge：只有明确不受本次修改影响的变量才从父代传给子代；例如修改检索策略后，旧的工具接口正确性可以继承，但旧的“检索结果已被采用”不能无条件继承。

检索输入不是主题关键词，而是当前决策缺口：

```text
DecisionNeed = {
  generation_id,
  parent_harness,
  generation_view_revision,
  current_belief_summary,
  competing_terminal_actions,
  high_loss_latent_states,
  unresolved_causal_edges,
  observable_trace_fields,
  hard_constraints,
  current_regime,
  forbidden_evidence_ids,
  source_call_id,
  validation_record_ids
}
```

**算法 1A：loop 外决策模型片段编译。**

1. `OptimizerHarness` 对齐论文机制、代码符号、配置、消融与评测，建立不可变来源单元；未对齐材料保留原位置和状态。
2. 对每个来源单元调用 `SOURCE_DECISION_MODEL_COMPILATION`。`OptimizerLLM` 提出潜变量、一个干预—机制—作用域片段、观察声明、排除条件、utility 维度、dependency group、unknown 假设和候选图边，并逐项引用来源与反证。
3. 程序核验来源锚点、代码路径、图类型、条件、dependency group 和 evidence scope；无法证实的参数保持 unknown，不因解释合理而通过。
4. 将经核验字段编译为最小完整片段；必须协同工作的步骤保留为组合片段。
5. 只有通过类型、来源、条件和依赖核验的关系才能建立 `CAUSES / OBSERVES / REQUIRES / EXCLUDES / PERSISTS / CONFLICTS / SHARES_EVIDENCE_WITH` 边。
6. 验证 unknown 状态完备性、persistence edge、来源可达性、依赖去重和索引可复算性，审计通过后冻结为 `DecisionModelCatalogSnapshot`。目录不包含目标 benchmark 的运行结论。

**算法 1B：loop 内价值感知检索。**

1. `TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS` 从 trace-role 成功/失败对照、父 Harness 和已提交 belief 提出多个竞争原因、最早可观测偏离、高损失潜状态、未决因果边和判别观察；程序核验 trace、实现锚点、状态 revision 与数据角色，形成 `DecisionNeed`。
2. 用硬约束和明确排除条件过滤；未知条件保留，并转成后续需要取证的变量。
3. 先按失败原因、机制、条件和可观测量分字段召回，再由程序沿依赖关系补齐并按 dependency group 去重形成 `ModelBundle`。
4. 对每个 bundle 计算终局相关性上界：若即使未知条件均取最有利值也不会改变候选、取证或停止决策，则不进入本轮上下文。
5. 对通过上述步骤的 bundle 调用 `BUNDLE_DECISION_RELEVANCE_RERANK`。`OptimizerLLM` 解释它可能改变的终局动作、关键迁移缺口和反驳观察；程序仅接收能回指 need、fragment revision 和可见 evidence 的字段。
6. 返回模型片段、来源、依赖闭包、冲突、待校准观察模型和未决假设；本阶段不生成代码补丁，也不临时联网补充来源。

```text
OFFLINE_ORGANIZE_DECISION_MODELS(source_packets, organization_protocol,
                                 llm_call_ledger):
    source_units <- FIX_DECISION_MODEL_SOURCE_UNITS(source_packets)
    compilation_requests <- BUILD_DECISION_MODEL_COMPILATION_REQUESTS(
                                source_units, organization_protocol)
    compilation_calls <- CALL_OPTIMIZER_LLM(
                             compilation_requests,
                             call_type=SOURCE_DECISION_MODEL_COMPILATION)
    compilation_proposals <- PARSE_DECISION_MODEL_COMPILATION_PROPOSALS(
                                 compilation_calls)
    verified_fields <- VERIFY_DECISION_MODEL_SOURCE_FIELDS(
                           compilation_proposals, source_units)
    fragments <- COMPILE_DECISION_MODEL_FRAGMENTS(
                     source_packets, verified_fields)
    source_graph <- BUILD_VERSIONED_INFLUENCE_GRAPH(fragments)
    return FREEZE_DECISION_MODEL_CATALOG(source_graph,
                                         organization_protocol)

BUILD_DECISION_NEED_FROM_TRACE_AND_BELIEF(generation_belief, trace_batch,
                                          parent_harness, long_term_state):
    need_request <- BUILD_TRACE_BELIEF_NEED_REQUEST(
                        generation_belief, trace_batch,
                        parent_harness, long_term_state)
    need_call <- CALL_OPTIMIZER_LLM(
                     need_request,
                     call_type=TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS)
    need_proposal <- PARSE_TRACE_BELIEF_NEED_PROPOSAL(need_call)
    return VERIFY_TRACE_CODE_BELIEF_AND_ROLE_ANCHORS(
               need_proposal, generation_belief, trace_batch,
               parent_harness)

RETRIEVE_DECISION_MODELS(catalog_snapshot, long_term_state,
                         decision_need, as_of):
    graph <- MATERIALIZE_DECISION_GRAPH(catalog_snapshot,
                                        long_term_state,
                                        as_of)
    seeds <- FIELD_AWARE_RETRIEVE(graph, decision_need)
    seeds <- HARD_FILTER_WITH_UNKNOWN_PRESERVED(seeds, decision_need)
    bundles <- DEPENDENCY_CLOSURE_AND_SOURCE_DEDUP(graph, seeds)
    bundles <- RANK_BY_TERMINAL_DECISION_RELEVANCE(bundles, decision_need)
    rerank_request <- BUILD_BUNDLE_DECISION_RERANK_REQUEST(
                          bundles, decision_need)
    rerank_call <- CALL_OPTIMIZER_LLM(
                       rerank_request,
                       call_type=BUNDLE_DECISION_RELEVANCE_RERANK)
    rerank_proposal <- PARSE_BUNDLE_DECISION_RERANK(rerank_call)
    bundles <- FUSE_DECISION_BOUNDS_AND_VERIFIED_SEMANTIC_RANKS(
                   bundles, rerank_proposal)
    return bundles, REQUIRED_LOCAL_CALIBRATIONS(bundles)
```


### 信念条件动作生成阶段：如何结合 trace、知识与自主探索生成候选

trace 是带噪观察，不会直接揭示根因；外部知识只能提出有条件的解释，也不能证明它适用于当前 Harness；自由探索可能发现知识库之外的机制，却往往缺少先验和可验证预测。更重要的是，当前最合理的下一步未必是修改代码：两个根因难以区分时应先插入 probe，预测模型不稳定时也可能值得追加一次 critic 或模拟。

这里把所有可选操作放进同一信念状态中生成。知识路径根据高后验的故障与方法区域提出受来源约束的修改，自由路径针对高不确定或未覆盖区域提出新干预，取证路径产生 probe 与评测动作，计算路径则请求额外分析。每个动作都必须声明它预期改变的潜变量、可观察后果、执行成本、风险和可逆性，因此不同类型的行动可以在后续规划器中用共同尺度比较。

每代开始时，训练调度器先用新 trace 更新故障、接入、激活和收益变量，形成权限受限的 `GenerationBeliefView`；阶段一再据此构造 `DecisionNeed` 并检索外部模型片段。本阶段接收该视图与方法束，将知识假设和自主假设合并去重，为每个假设综合代码干预或信息动作，生成预测分布和失败条件，通过硬约束后冻结动作集。未解释事件保持 unknown，不被强行归入已有类别；自由探索也保留最低概率，使信念图能够在证据不支持旧结构时增长。

这里的 trace 由真实 benchmark 运行产生。第 $g$ 代首先用冻结执行配置运行 $H^{[g]}$ 在 $D_g^{\mathrm{trace}}$ 上的全部任务；成功、失败、超时、崩溃、工具异常和评测异常都生成 `ExecutionTrace`。完整事件序列记录模型可见上下文、工具调用、记忆读写、控制转移、重试、回退、最终输出和指标，不能用事后摘要替代。该批 trace 形成只供生成路径使用的 `GenerationBeliefView`；它可以读取本代 trace 和过去已提交证据，但不能读取本代 select 任务、标签、得分、排序或其派生 critic 结论。

四类动作的语义内容由隔离调用产生。`METHOD_GUIDED_EVOLUTION_PROPOSAL` 只读取检索 bundle、合法接入孔、父代码切片与 generation belief；`FREE_BELIEF_EXPANSION_PROPOSAL` 不读取本轮知识 patch，只针对 unknown 后验区域提出新机制与 child；`DISCRIMINATIVE_EVIDENCE_ACTION_PROPOSAL` 为竞争世界提出 probe、消融和评测模板；`ESTIMATOR_COMPUTATION_ACTION_PROPOSAL` 针对解释或估计器失配提出 critic、simulation 或 refit。四类输出先解析为共同 `BeliefActionIR`。`ACTION_OUTCOME_MODEL_PROPOSAL` 可以提出结果类别、可观测预测和 unknown 分支，但预测概率必须由经校准的 `PlannerModelRevision` 拟合或保守界定，不能直接采用模型自报数字。`OptimizerHarness` 随后执行代码、接口、权限、角色、回滚、数据隔离与硬安全检查，冻结合法动作。

```text
ExecutionTrace = {
  task_id,
  split_role,
  generation_id,
  harness_version,
  model_and_tool_versions,
  seed,
  ordered_events,
  final_output,
  metric_vector,
  termination_status,
  artifact_refs
}
```

当前状态为：

```text
BeliefState_t = {
  harness_version,
  regime_id,
  posterior_particles,
  influence_graph_revision,
  planner_model_revision,
  evidence_view,
  candidate_versions,
  evaluator_calibration,
  misspecification_debt,
  llm_call_ledger_revision
}
```

每个粒子表示一个完整但不可见的世界：故障原因、方法可迁移性、接入状态、机制是否激活、各候选在完整目标协议下的多指标效果，以及观测器可靠性。真实 planner 只能看 trace 和评测结果，不能读取抽样粒子中的隐藏标签。

动作统一为：

```text
Action =
    EvolutionAction(method_guided | free_exploration)
  | EvidenceAction(probe | ablation | short_rollout | full_dev | independent_review)
  | ComputationAction(critic | simulation | estimator_refit)
  | commit | revert | stop
```

最终效果隐状态不使用单分数，而是：

$$
\theta_c=(\text{new capability},\text{legacy retention},\text{severe failure},
          \text{latency},\text{token cost},\text{stability}).
$$

评测保真度也不是一个固定编号，而是向量

$$
z=(\text{task coverage},\text{rollout horizon},\text{seed count},
   \text{judge strength},\text{environment realism}).
$$

**算法 2：训练 trace 条件下的四类动作生成。**

1. **校验 trace 信念。** 检查 `GenerationBeliefView` 中每条 trace 是否映射到影响图观察节点、是否使用正确似然 revision、是否保留不可解释事件。若真实观察在所有已知假设下都长期低概率，则增加 `unknown` 质量与 `misspecification_debt`，不能强行归给概率最高的旧原因。
2. **构造知识候选。** 对后验质量较高且已检索到可绑定 bundle 的区域调用 `METHOD_GUIDED_EVOLUTION_PROPOSAL`，提出目标潜变量、typed binding、局部代码干预、接入检查、可观测激活和 fallback；解析结果不得改变 bundle 中冻结的机制与排除条件。
3. **构造自由候选。** `FREE_BELIEF_EXPANSION_PROPOSAL` 只接收父代、trace、硬约束和知识解释覆盖不到的后验区域，不读取本轮知识候选 patch；输出新的机制边、child 修改、可观测预测和反证条件，并编译为同一 `BeliefActionIR`。
4. **构造判别性取证动作。** `DISCRIMINATIVE_EVIDENCE_ACTION_PROPOSAL` 针对会导致不同终局动作的竞争世界提出 probe、ablation、任务 strata 或 verifier 模板。模板只能声明任务条件和保真度，具体 select/anchor 实例由下一阶段绑定。
5. **构造计算动作。** 当不确定性来自已有证据的语义解释、模拟器或估计器失配时，`ESTIMATOR_COMPUTATION_ACTION_PROPOSAL` 提出 critic、反事实模拟或 estimator refit；这些动作只改变 `EstimatorState`，不能伪装成环境证据。
6. **声明动作结果模型。** `ACTION_OUTCOME_MODEL_PROPOSAL` 为每个 IR 提出结果类别、观察映射、状态转移结构和 unknown 分支；程序用历史校准、保守界或小规模 calibration action 估计数值分布。无法可靠建模时保持 `unknown_model`，不得填入模型自报的精确概率。
7. **建立父子 persistence network。** patch 生成 `H_child` 后复制父代图，只沿已声明的 persistence edge 继承状态。代码修改本身不是“对同一候选再观察一次”。
8. **执行公共确定性 gate。** 编译、接口、权限、数据隔离、回滚和硬安全检查对知识候选与自由候选完全相同；失败产生可观察的构建证据并建立新版本，不原地修补。
9. **冻结动作集。** 保存动作生成时可见的 belief revision 和来源，之后的新结果不能倒灌进当时的候选理由。

```text
GENERATE_BELIEF_CONDITIONED_ACTIONS(H, generation_belief,
                                    trace_batch, bundles, calibrations):
    belief <- EXPAND_UNKNOWN_IF_PREDICTIVE_CHECK_FAILS(generation_belief)
    method_request <- BUILD_METHOD_GUIDED_EVOLUTION_REQUEST(
                          H, bundles, belief, trace_batch)
    method_call <- CALL_OPTIMIZER_LLM(
                       method_request,
                       call_type=METHOD_GUIDED_EVOLUTION_PROPOSAL)
    method_ir <- PARSE_METHOD_GUIDED_BELIEF_ACTION_IR(method_call)

    uncovered_unknown_regions <- UNEXPLAINED_POSTERIOR_REGIONS(
                                     belief, bundles, method_ir)
    free_request <- BUILD_FREE_BELIEF_EXPANSION_REQUEST(
                        H, belief, trace_batch,
                        uncovered_unknown_regions)
    free_call <- CALL_OPTIMIZER_LLM(
                     free_request,
                     call_type=FREE_BELIEF_EXPANSION_PROPOSAL)
    free_ir <- PARSE_FREE_BELIEF_ACTION_IR(free_call)

    evidence_request <- BUILD_DISCRIMINATIVE_EVIDENCE_REQUEST(
                            belief, calibrations, method_ir, free_ir)
    evidence_call <- CALL_OPTIMIZER_LLM(
                         evidence_request,
                         call_type=DISCRIMINATIVE_EVIDENCE_ACTION_PROPOSAL)
    evidence_ir <- PARSE_EVIDENCE_ACTION_IR(evidence_call)

    computation_request <- BUILD_ESTIMATOR_COMPUTATION_REQUEST(
                               belief, calibrations)
    computation_call <- CALL_OPTIMIZER_LLM(
                            computation_request,
                            call_type=ESTIMATOR_COMPUTATION_ACTION_PROPOSAL)
    computation_ir <- PARSE_COMPUTATION_ACTION_IR(computation_call)

    action_ir <- method_ir union free_ir union evidence_ir union computation_ir
    outcome_request <- BUILD_ACTION_OUTCOME_MODEL_REQUEST(
                           action_ir, belief.planner_model_revision)
    outcome_call <- CALL_OPTIMIZER_LLM(
                        outcome_request,
                        call_type=ACTION_OUTCOME_MODEL_PROPOSAL)
    outcome_models <- PARSE_ACTION_OUTCOME_MODEL_PROPOSALS(outcome_call)
    action_ir <- FIT_OR_BOUND_AND_ATTACH_ACTION_MODELS(
                     action_ir, outcome_models, calibrations)
    action_ir <- COMMON_BELIEF_ACTION_STATIC_GATE(action_ir, H)
    return FREEZE_VALID_BELIEF_ACTIONS(action_ir)
```

若 discovery probe 暴露接口接错或观测字段缺失，且本代 select 结果尚未进入生成路径，可以在固定父代和固定三类任务池下重新检索或重新生成。任何 select 结果一旦被生成器、候选 critic 或编辑器读取，本代不再允许产生新候选；未解决信息进入下一代，避免同一确认样本既指导修改又证明修改有效。


### 单步规划与执行阶段：如何规划、测评并控制多轮 Harness 演化

开发过程持续面对同一个选择问题：继续评测旧候选、先做一个 probe、生成新子代、增加一次模型推理，还是停止并提交当前版本。便宜的观察可能偏差很大，可靠的完整评测又未必会改变最终选择。若把这些动作交给独立规则，系统可能一边认为证据已经足够，一边继续消耗任务，或在尚有高价值取证动作时过早停止。

本阶段以完整目标协议下最终选中 Harness 的效用为共同尺度。每个动作的价值等于执行后最优终局决策的期望改善，再扣除计算、延迟、风险和不可逆成本；低保真证据只有在与高保真结果完成配对校准后，才能影响相应层级的决策。规划器每次只执行一个真实动作，观察结果后重新更新信念和规划，避免长计划建立在尚未验证的预测上。

规划信念与生成信念是同一长期状态的两个权限视图。`GenerationBeliefView` 在本代候选冻结时封闭，只含 trace-role 与过去已提交证据；`PlanningBeliefView` 随真实动作更新，可以读取 discovery probes、$D_g^{\mathrm{select}}$ 的目标确认结果和 $D_g^{\mathrm{anchor}}$ 的保留结果。后者可以选择继续测评、提交、淘汰、回退或停止，却不能把本代确认结果反向交给候选生成器。只有未接触 select 结果的 discovery 证据才能触发同代重新检索或重新绑定。

实现上先由 `OptimizerLLM` 通过 `BELIEF_TREE_CONTINGENCY_PROPOSAL` 检查当前动作模型是否遗漏会改变终局选择的多步情景，例如“低保真成功但高保真回归”“修复一个模块后暴露另一故障”“观测别名导致两个潜在世界暂时不可区分”以及“回滚后仍保留外部状态”。模型只提出分支条件、可观测后果、状态转移假设、终局影响和未知分支；`OptimizerHarness` 核验动作可达性、观察 schema、状态 effect、时间顺序与数据权限，并使用 `PlannerModelRevision` 拟合或保守界定分支概率。随后从当前 belief 对可能世界做 root sampling，分别模拟评测、修改、回滚、提交和停止的后果，估计动作净价值及不确定性。若最优动作是评测，则选择最可能改变候选排序或约束判断的任务；若是演化，则执行对应干预并建立子代；若所有可行动作的保守净价值均不为正，则生成停止证书。真实结果写回后重新规划，直至提交、回滚或达到不可突破的约束边界。

真实动作完成后，原始输出不会直接被自然语言解释覆盖。`BELIEF_EVENT_INTERPRETATION` 让 `OptimizerLLM` 把 action、trace、指标和环境异常映射到预先声明的结果类别、潜变量观察、竞争解释与缺失测量；`OptimizerHarness` 核验事件、指标、代码、数据角色和 action revision，只把通过核验的观察映射交给 belief updater，原始结果独立追加保存。若动作集合仍含大量 `unknown_model`，或 stop 证书缺少可执行证据，`PLANNING_STALL_REFLECTION` 可提出新的 evidence/computation 模板、缺失 trace 字段或返回阶段一/二的理由；程序检查权限、数据披露和可执行性。`OptimizerLLM` 负责补足规划树的语义分支，不负责给分支赋概率或替 planner 作决定；root sampling、VOI、动作 argmax、置信过程、stop 证书与 `PROMOTE/RETIRE` 都不接受模型的主观分数。

在信念 $b$ 下，先按硬约束和概率约束构造可部署集合：

$$
\mathcal F(b)=\{c:\Pr(\theta_{c,k}\ \text{satisfies}\ \tau_k\mid b)
                   \ge 1-\delta_k,\ \forall k\}.
$$

$H_0$ 与当前最近确认的父版本始终作为可回退候选。当前终局价值为：

$$
D(b)=\max_{c\in\mathcal F(b)}
      \mathbb E[U(\theta_c)\mid b]-\operatorname{RiskPenalty}(c,b).
$$

对取证动作 $a$，使用决策信息价值而非单纯熵下降：

$$
\operatorname{DecisionVOI}(a)=
\mathbb E_o[D(\operatorname{Update}(b,a,o))]-D(b).
$$

修改动作会产生新的 child 和构建结果：

$$
\operatorname{InterventionVOI}(a)=
\mathbb E_r[D(\operatorname{UpdateAndExpand}(b,a,r))]-D(b).
$$

额外推理或模拟使用 computation value。所有动作最后比较：

$$
\operatorname{NetValue}(a)=\operatorname{VOI}(a)
-\lambda_t\mathbb E[T_a]-\lambda_c\mathbb E[C_a]
-\operatorname{Risk}(a)-\operatorname{MetaCost}(a).
$$

成本只用于衡量浪费与机会成本，不能把停止规则写成“预算用完”。

**多保真校准。** 每条证据保存：

```text
Evidence = {
  evidence_id, candidate, data_role, confirmation_role,
  evidence_type, task_stratum, fidelity_vector, seed,
  outcome, trace_features, execution_cost, environment,
  exposure_record_id, selection_propensity,
  action_id, trace_id, supersedes,
  interpretation_call_ids, validation_record_ids
}
```

低保真 $y(c,z)$ 到目标保真 $z^*$ 的关系通过同候选、同任务层、尽量同种子的配对锚点学习：

$$
\Delta(c,z,r)=y(c,z^*)-\operatorname{Calibrator}_z(y(c,z),x_c,r).
$$

校准器同时报告 bias、dispersion 和配对覆盖率。只有当前 regime 内覆盖率达到要求时，低保真校准后的保守界才有淘汰权；原始低保真均值永远不能永久淘汰候选。当某层剩余统计不确定性已经小于其到目标保真的校准误差底线时，继续重复这一层无意义，应升级或改换证据类型。

**算法 3：价值驱动的滚动信念规划与晋级。**

1. 从当前 belief 粒子抽取一个包含故障、迁移、候选效果和评测可靠性的完整世界，在一次模拟轨迹内固定该世界。
2. 在建树前调用 `BELIEF_TREE_CONTINGENCY_PROPOSAL`。`OptimizerLLM` 针对当前 belief、冻结动作、已知结果模型和规划 horizon，提出可能改变终局动作的多步路径、分支条件、可观察结果、状态转移假设、观测别名和必须保留的 unknown 分支；程序拒绝不可达动作、越权观察、违反时间顺序或无法映射到 action/result schema 的路径，并把通过项编译成 `VerifiedContingencySet`。模型输出的概率字段一律丢弃。
3. 采用 root-sampling tree search 比较 evidence、computation、evolution、commit、revert 和 stop；树同时使用冻结动作结果模型与 `VerifiedContingencySet`，但每条边的概率只来自 `PlannerModelRevision` 的拟合值或保守界。节点只接收模拟中可观察的 trace 与分数，禁止读取隐藏状态标签。
4. 冷启动且竞争机制尚未建立可靠效用时，用期望信息增益设计少量判别 probe；一旦存在明确候选，切换到 `DecisionVOI`；optimizer 解释不稳定时使用 `VOC`。信息熵下降不能直接决定晋级。
5. 对取证动作联合选择候选、证据类型、任务层和保真向量，并在执行前绑定数据角色：trace replay、合成 probe 与消融只能形成 `DISCOVERY`；select 任务的父子配对只更新目标效用；anchor 任务只更新旧能力、严重失败与校准约束。优先解析可能改变胜者、可行性或高损失风险的边界候选。
6. 维护目标与约束的解耦观察：目标能力已有把握但旧能力区间仍宽时，下一步只评旧能力，不重复目标分数。
7. 每轮保留配对高保真锚点，覆盖低保真预测最好、预测最差但不确定、采用新结构的候选和随机审计候选，用于发现选择偏差与校准失效。
8. 硬安全由沙箱、权限和静态规则直接阻断；可统计的旧能力、严重失败与资源约束才使用后验保守界。概率安全不能替代硬阻断。
9. 真实执行根节点价值最高的一个动作，调用 `BELIEF_EVENT_INTERPRETATION` 提出结果类别、潜变量观察和替代解释；程序核验后同时追加原始证据与解释映射，再更新 belief，并复用仍相容的搜索子树。
10. 候选仅在接入正确、机制激活、目标能力、旧能力和风险门均通过后进入 `PROMOTE`。边界未解析时返回 `CONTINUE`；确定有害返回 `RETIRE`；多种机制在现有观察下不可区分时返回 `UNRESOLVED` 并要求新增 trace 字段或 probe。
11. 自适应反复查看结果时，确认性结论使用满足条件的 confidence sequence 或 e-process；若观测不满足相应假设，只能标为探索性后验，不能借“贝叶斯”名义自动宣称校准。
12. 动作集合无可评估项或 stop 证书缺少可执行证据时，调用 `PLANNING_STALL_REFLECTION` 提出缺失 observation、evidence/computation 模板或合法前序返回；程序核验后才能加入动作集。模型不能自行宣布收敛。
13. 仅当所有可行取证、计算和修复动作的净价值上界不为正，最佳与次佳终局动作的差距稳定，高损失状态概率低于阈值，且强制接入、激活、回归和近期高保真审计全部通过时停止。EVPI 小于最便宜可行 probe 的总代价可作为停止的充分上界之一。

```text
PLAN_EVALUATE_AND_EVOLVE(planning_belief, actions,
                         select_pool, anchor_pool,
                         exposure_ledger, round_ledger):
    while True:
        actions <- BIND_EVIDENCE_ACTIONS_TO_DATA_ROLES(
                       actions, select_pool, anchor_pool, exposure_ledger)
        contingency_request <- BUILD_BELIEF_TREE_CONTINGENCY_REQUEST(
                                   planning_belief, actions, round_ledger)
        contingency_call <- CALL_OPTIMIZER_LLM(
                                contingency_request,
                                call_type=BELIEF_TREE_CONTINGENCY_PROPOSAL)
        contingency_proposal <- PARSE_BELIEF_TREE_CONTINGENCY_PROPOSAL(
                                    contingency_call)
        verified_contingencies <- VERIFY_AND_BOUND_TREE_CONTINGENCIES(
                                      contingency_proposal,
                                      planning_belief, actions,
                                      round_ledger)
        tree <- ROOT_SAMPLE_BELIEF_TREE(
                    planning_belief, actions, verified_contingencies)
        values <- ESTIMATE_TERMINAL_DECISION_VALUE(tree)
        if NO_DECISION_RELEVANT_ACTION(values):
            stall_request <- BUILD_PLANNING_STALL_REQUEST(
                                 planning_belief, actions, values,
                                 round_ledger)
            stall_call <- CALL_OPTIMIZER_LLM(
                              stall_request,
                              call_type=PLANNING_STALL_REFLECTION)
            stall_proposal <- PARSE_PLANNING_STALL_REFLECTION(stall_call)
            additions, return_request <- VERIFY_AND_COMPILE_STALL_RESPONSE(
                                             stall_proposal,
                                             planning_belief,
                                             round_ledger)
            if return_request is valid:
                return return_request, planning_belief, round_ledger
            if additions is empty:
                return UNRESOLVED, planning_belief, round_ledger
            actions <- actions union additions
            continue
        action <- ARGMAX_NET_VALUE(values)

        if action == stop:
            if STOP_CERTIFICATE_HOLDS(planning_belief, values):
                return DEPLOY_OR_UNRESOLVED(planning_belief), round_ledger
            actions <- DEFER_INVALID_STOP(actions, planning_belief)
            continue

        result <- EXECUTE_ONE_REAL_ACTION(action)
        interpretation_request <- BUILD_BELIEF_EVENT_INTERPRETATION_REQUEST(
                                      action, result, planning_belief)
        interpretation_call <- CALL_OPTIMIZER_LLM(
                                   interpretation_request,
                                   call_type=BELIEF_EVENT_INTERPRETATION)
        interpretation <- PARSE_BELIEF_EVENT_INTERPRETATION(
                              interpretation_call)
        verified_observation_map <- VERIFY_EVENT_METRIC_CODE_ROLE_ANCHORS(
                                        interpretation, action, result,
                                        planning_belief)
        round_ledger, event <- APPEND_IMMUTABLE_EVIDENCE(
                                   round_ledger, action, result,
                                   verified_observation_map)
        planning_belief <- VERSIONED_UPDATE_AND_CALIBRATE(
                               planning_belief, event)
        planning_belief <- KEEP_DISCOUNT_OR_SPLIT_REGIME(planning_belief)
        route <- ROUTE_AFTER_BELIEF_UPDATE(event, planning_belief,
                                           round_ledger)
        if route is RETURN_RETRIEVE or route is RETURN_REGENERATE:
            return route, planning_belief, round_ledger
        actions <- REFRESH_NON_GENERATIVE_ACTIONS(
                       planning_belief, actions, round_ledger)
```

这里的停止证书只结束第 $g$ 代的滚动规划。`PROMOTE` 指定唯一候选成为下一父 Harness，`RETIRE` 或 `UNRESOLVED` 保持当前父版本；它们都必须先进入第四阶段沉淀本代证据。整个 benchmark 训练何时结束，还需要在多代循环中检查训练任务覆盖、连续无晋级、unknown 质量、开放动作和长期状态稳定性，不能把一次局部 `stop` 当作最终测试入口。


### 信念沉淀与迁移阶段：如何持续积累并跨任务复用

演化过程会主动选择看起来更有希望的候选和任务继续测试，因此历史数据天然存在选择偏差；模型、工具、任务分布或评分器变化后，同一观察的含义也可能改变。若只保存最终 posterior，之后无法恢复它依赖哪些 trace、是否重复使用相关证据，也无法判断停止条件是否在观察结果后被改写。

长期状态从不可变事件账本开始，belief、校准曲线和迁移先验都只是可重算的派生视图。每条事件记录选择概率、保真度、环境 regime、候选谱系和来源依赖；环境变化通过显式 regime 检测产生新分层，而不是把新旧样本直接混合。跨任务共享采用层次先验和校准残差，使稳定机制能够迁移，同时为目标任务保留足够的冷启动证据来推翻历史结论。

这一阶段是 benchmark loop 内的在线沉淀，不重新收集论文或修改冻结目录。阶段三的全部事件先写入本代 `RoundLedger`；本阶段在写时复制状态中追加原始事件、重算 belief 与校准、执行 regime 更新和迁移审计，所有检查通过后再原子提交新的长期 revision。提交失败时原始 round ledger 保留供恢复，上一已提交状态不变。新论文或代码版本只能在另一场实验开始前形成新的 `DecisionModelCatalogSnapshot`。

更新流程先追加原始事件，再按选择概率校正、依赖组去重和多保真残差更新当前后验；随后检测环境断点，必要时分裂 regime，并通过留一任务审计估计迁移先验是否过强。新任务启动时只加载与目标条件相关的结构和概率区间，未知边保持 unknown。所有决策状态都能从账本重新计算，使长期积累既可利用历史证据，也能在假设或协议改变后重新解释。

这一阶段也区分语义提案与统计事实。`CALIBRATION_FAILURE_DIAGNOSIS` 从 proper score、coverage、残差、哨兵差异和缺失 trace 中提出失配机制与下一校准观察；程序重新计算指标并验证引用。`REGIME_CHANGE_HYPOTHESIS` 提出可能变化的任务、模型、工具、Harness 或 evaluator 条件以及候选断点解释；`OptimizerHarness` 用冻结变点检测、独立失配信号和状态机决定 `KEEP/DISCOUNT/SPLIT`。`TRANSFER_STRUCTURE_PROPOSAL` 提出哪些历史条件效应可共享、哪些 scope 应收紧、哪些 dependency group 或冲突需要建立；程序执行硬条件过滤、冷启动下限、proper-score 更新和留一任务/regime 审计。模型不能直接修改混合权重、删除旧事件或把自然语言相似写成迁移关系。

同一 benchmark 内，新提交 revision 成为下一代先验。跨任务复用时复制的是已提交账本、图 revision、按 regime 校准的条件效应和冷启动影子，不是上一任务的胜出 Harness；目标任务必须重新通过自身训练 split 校准迁移权重。历史正证据只影响初始检索与先验，不能替代目标任务的 select/anchor 确认，目标测试集仍保持封存。

长期状态为：

```text
BeliefLongTermState = {
  raw_evidence_ledger,
  evidence_views,
  prior_and_likelihood_revisions,
  belief_snapshots,
  decision_records,
  regime_history,
  evaluator_calibration_history,
  hierarchical_task_priors,
  cold_start_shadow_models,
  source_dependency_groups,
  llm_call_ledger_revisions,
  latest_revision
}
```

四层记录严格分开：

```text
RawEvidenceEvent --append--> EvidenceLedger
EvidenceLedger + EvidenceView + PriorRevision
                 --derive--> BeliefSnapshot
BeliefSnapshot + DecisionRuleRevision
                 --emit----> DecisionRecord
```

原始事件永久不改，纠错通过追加 correction event；`EvidenceView` 声明纳入、排除、折扣哪些事件及其 regime；`BeliefSnapshot` 可由事件、先验和似然 revision 重算；`DecisionRecord` 冻结当时可见信息与动作，未来重算不能覆盖历史决策。同一个 trace 的多个派生指标共享 event identity，只能联合建模或保守组合，不能当作独立样本重复相乘。

**算法 4：regime 校准的证据账本与跨任务迁移。**

1. **追加取样机制。** 在结果产生前写入候选池、选择策略、选择概率、probe 定义、指标、停止规则和环境版本，再追加结果与 trace。无法重建取样机制的旧实验只能形成探索先验，不能成为确认性证据。
2. **混入随机哨兵。** 主动策略大部分时间选择最高决策价值动作，同时以预声明概率运行覆盖候选空间的随机哨兵。比较主动样本与哨兵的 proper score、覆盖率和残差，审计自证循环。
3. **保留冷启动影子。** 新任务的先验使用：

   $$
   P_T(\theta)=\pi_{cold}P_{cold}(\theta)+\sum_{q\in\mathcal G_T}\pi_qP_q(\theta),
   \qquad \pi_{cold}\ge\pi_{min}.
   $$

   历史 regime 只在超参数或条件效应层共享，不复制某个胜出 Harness 的结论。来源权重根据当前任务留出的校准 probe 的严格适当得分更新并设上限；持续差于冷启动影子的来源被降权。
4. **累计失配债务。** 跟踪预测区间覆盖、proper score、标准化残差、主动样本与哨兵差异，以及迁移后验与冷启动影子的差异；`CALIBRATION_FAILURE_DIAGNOSIS` 提出失配机制和所需观察，程序核验后决定扩大区间或安排 probe，不立即用错误模型淘汰候选。
5. **执行 regime 状态机。** `REGIME_CHANGE_HYPOTHESIS` 提出变化字段、候选断点和替代解释；程序同时使用在线变点后验、预测残差和校准恶化：三者低则 `KEEP`；单一或中等持续信号则 `DISCOUNT`；高变点概率且至少一个独立失配信号确认才 `SPLIT`。旧事件永不删除。
6. **控制自适应晋级。** 对候选相对父代的最小有意义提升、旧能力和风险分别维护满足前提的 confidence sequence 或 e-process，只输出 `PROMOTE / RETIRE / CONTINUE`。regime 分裂时旧过程冻结，新过程不能无条件乘入旧证据。
7. **限制知识回流。** `TRANSFER_STRUCTURE_PROPOSAL` 提出共享机制、作用域、dependency group、冲突和候选历史分量；只有原始证据和选择机制完整、regime 内校准合格、未出现稳定负迁移、通过独立确认且作用域清晰的条件效应，才能由程序写入共享层次先验。
8. **执行留一回放。** 周期性做 leave-one-task-out 与 leave-one-regime-out 回放；若移除某来源反而改善目标任务的预测得分或终局决策效用，则降低其权重并记录冲突作用域，不改写历史结果。
9. **冻结后评估。** 方法库、先验、似然、regime 规则和停止规则全部冻结后，才在未见任务及独立测试集评价跨任务适配速度、最终质量、旧能力和校准。

```text
CONSOLIDATE_AND_TRANSFER_BELIEFS(state, round_ledger, next_regime,
                                 llm_call_ledger):
    shadow <- COPY_ON_WRITE_BELIEF_STATE(state)
    shadow.raw_evidence_ledger <- APPEND_WITH_SELECTION_METADATA(
                                      shadow.raw_evidence_ledger,
                                      round_ledger.events)
    shadow <- UPDATE_PROPER_SCORE_COVERAGE_AND_MISSPECIFICATION(shadow)
    calibration_request <- BUILD_CALIBRATION_FAILURE_REQUEST(shadow)
    calibration_call <- CALL_OPTIMIZER_LLM(
                            calibration_request,
                            call_type=CALIBRATION_FAILURE_DIAGNOSIS)
    calibration_proposal <- PARSE_CALIBRATION_FAILURE_DIAGNOSIS(
                                calibration_call)
    verified_calibration_gaps <- VERIFY_CALIBRATION_DIAGNOSIS(
                                    calibration_proposal, shadow)

    regime_request <- BUILD_REGIME_CHANGE_REQUEST(
                          shadow, verified_calibration_gaps, next_regime)
    regime_call <- CALL_OPTIMIZER_LLM(
                       regime_request,
                       call_type=REGIME_CHANGE_HYPOTHESIS)
    regime_proposal <- PARSE_REGIME_CHANGE_HYPOTHESIS(regime_call)
    verified_regime_hypotheses <- VERIFY_REGIME_CHANGE_ANCHORS(
                                      regime_proposal, shadow)
    shadow <- KEEP_DISCOUNT_OR_SPLIT_REGIME(
                  shadow, verified_regime_hypotheses)
    shadow <- UPDATE_ANYTIME_VALID_DECISION_PROCESSES(shadow)

    qualified <- QUALIFIED_REGIME_EFFECTS(shadow)
    transfer_request <- BUILD_TRANSFER_STRUCTURE_REQUEST(
                            qualified, shadow, next_regime)
    transfer_call <- CALL_OPTIMIZER_LLM(
                         transfer_request,
                         call_type=TRANSFER_STRUCTURE_PROPOSAL)
    transfer_proposal <- PARSE_TRANSFER_STRUCTURE_PROPOSAL(transfer_call)
    verified_transfer_structure <- VERIFY_TRANSFER_STRUCTURE(
                                       transfer_proposal, qualified, shadow)
    shadow.hierarchical_task_priors <- UPDATE_WITH_COLD_FLOOR(
                                            qualified,
                                            shadow.cold_start_shadow_models,
                                            verified_transfer_structure)
    shadow <- LEAVE_ONE_TASK_AND_REGIME_OUT_AUDIT(shadow)
    shadow.llm_call_ledger_revision <- CURRENT_LLM_CALL_LEDGER_REVISION(
                                           llm_call_ledger)
    commit_result <- ATOMIC_COMMIT_BELIEF_REVISION(
                         state, shadow, round_ledger)
    if commit_result.status is not COMMITTED:
        return {status: PENDING_REVIEW,
                recovery_record: commit_result.recovery_record}
    next_belief <- RECOMPUTABLE_TARGET_BELIEF(
                       commit_result.state, next_regime)
    return {status: COMMITTED,
            state: commit_result.state,
            next_belief: next_belief}
```


| 可以由设计保证 | 必须通过实验验证 |
| --- | --- |
| 方法声明、观察模型和本地信念分层保存 | 决策相关检索是否优于语义 top-k |
| 取证、计算、修改、回滚和停止使用同一终局价值接口 | 联合规划是否减少无效运行并提高最终 Harness 质量 |
| 低保真未经配对校准不能永久淘汰候选 | 多保真调度能否比固定漏斗更少浪费真实评测 |
| H0 回退、硬安全阻断和旧能力约束不会被平均分抵消 | 风险门是否能降低严重回归且不过度阻碍探索 |
| 原始证据不可变，belief 和决策可追溯重算 | regime 检测是否能在变化后及时停止错误继承 |
| 历史来源保留冷启动分量并接受目标任务校准 | 层次先验是否改善未见任务适配并避免负迁移 |
| 主动取样、随机哨兵与确认样本用途分离 | 哨兵和独立确认是否能识别自证循环 |

### 四阶段在多轮 Harness 演化中的完整流转

前面四个阶段共同产生 benchmark 训练集上的一代 Harness 更新。loop 外只执行一次来源组织，得到冻结目录 $K_0$，同时冻结 `TrainProtocol` 并封存 $D_{\mathrm{test}}$。在线 loop 从父 Harness $H^{[0]}=H_0$、不含本 benchmark 运行证据的长期状态 $M_0$ 和由冷启动分量保护的初始 belief 开始。

第 $g$ 代先冻结 trace、select 和 anchor 三类任务。执行 $H^{[g]}$ 得到 trace batch 后，仅用 trace-role 事件和过去已提交状态构造 `GenerationBeliefView`；阶段一依据它形成 `DecisionNeed` 并检索 $K_0$，阶段二生成冻结知识候选、自由候选、取证模板和计算动作。阶段三持有权限更宽的 `PlanningBeliefView`，把动作模板绑定到 select/anchor 实例，每次只执行一个动作并滚动重规划，直至 `PROMOTE/RETIRE/UNRESOLVED` 或合法的局部返回。阶段四把本代完整账本沉淀为 $M_{g+1}$。

局部返回只允许吸收未接触 select 结果的 discovery 证据。若 probe 发现缺少决策模型边，则修订 `DecisionNeed` 返回阶段一；若发现接入或生成模型错误，则返回阶段二。若本代任意 select 标签、分数、trace 或其派生排序已进入生成路径，返回门立即关闭；尚未解决的问题随账本进入下一代。`PROMOTE` 使唯一通过停止证书的候选成为 $H^{[g+1]}$，`RETIRE` 或 `UNRESOLVED` 令 $H^{[g+1]}=H^{[g]}$。下一代必须在新分配的 trace 任务上重新运行，旧候选的后验、校准区间和动作价值不能直接继承。

```text
EVOLVE_DECISION_THEORETICALLY(H0, source_packets,
                              D_train, D_test, train_protocol):
    llm_call_ledger <- INIT_LLM_CALL_LEDGER(train_protocol)
    catalog <- OFFLINE_ORGANIZE_DECISION_MODELS(
                   source_packets, train_protocol.organization_protocol,
                   llm_call_ledger)
    scheduler <- INIT_TRAIN_SCHEDULER(D_train, train_protocol)
    long_state <- INIT_BELIEF_LONG_TERM_STATE(catalog, train_protocol)
    H <- H0
    g <- 0

    loop:
        trace_pool, select_pool, anchor_pool <- ASSIGN_TRAIN_ROLES(
                                                    scheduler, long_state, g)
        trace_batch <- RUN_HARNESS(
                           H, trace_pool, train_protocol.execution_config)
        round_ledger <- INIT_ROUND_LEDGER(
                            g, H, trace_batch,
                            llm_call_ledger, scheduler.exposure_ledger)
        generation_belief <- BUILD_GENERATION_BELIEF_VIEW(
                                  long_state, H, trace_batch)

        loop current_generation:
            need <- BUILD_DECISION_NEED_FROM_TRACE_AND_BELIEF(
                        generation_belief, trace_batch, H, long_state)
            bundles, calibrations <- RETRIEVE_DECISION_MODELS(
                                          catalog,
                                          long_state,
                                          need,
                                          as_of=long_state.latest_revision)
            actions <- GENERATE_BELIEF_CONDITIONED_ACTIONS(
                           H, generation_belief, trace_batch,
                           bundles, calibrations)
            control, planning_belief, round_ledger <- PLAN_EVALUATE_AND_EVOLVE(
                           generation_belief, actions,
                           select_pool, anchor_pool,
                           scheduler.exposure_ledger, round_ledger)
            UPDATE_EXPOSURE_FROM_LLM_CALLS(
                scheduler, llm_call_ledger,
                {actions, planning_belief, round_ledger.events},
                trace_pool union select_pool union anchor_pool)

            if control is RETURN_RETRIEVE and NO_SELECT_RESULT_DISCLOSED(round_ledger):
                select_pool, anchor_pool <- REFRESH_INDEPENDENT_PLANNING_POOLS(
                                               scheduler, actions,
                                               select_pool, anchor_pool)
                generation_belief <- REFRESH_GENERATION_VIEW_FROM_DISCOVERY(
                                         generation_belief, round_ledger)
                continue current_generation
            if control is RETURN_REGENERATE and NO_SELECT_RESULT_DISCLOSED(round_ledger):
                select_pool, anchor_pool <- REFRESH_INDEPENDENT_PLANNING_POOLS(
                                               scheduler, actions,
                                               select_pool, anchor_pool)
                generation_belief <- REFRESH_GENERATION_VIEW_FROM_DISCOVERY(
                                         generation_belief, round_ledger)
                continue current_generation
            break current_generation

        H_next <- APPLY_TERMINAL_CONTROL(H, control, planning_belief)
        next_regime <- PREDICT_NEXT_REGIME(scheduler, round_ledger, H_next)
        consolidation <- CONSOLIDATE_AND_TRANSFER_BELIEFS(
                             long_state, round_ledger, next_regime,
                             llm_call_ledger)
        if consolidation.status is not COMMITTED:
            return {status: PENDING_REVIEW,
                    recovery_record: consolidation.recovery_record,
                    long_state: long_state,
                    round_ledger: round_ledger}
        long_state <- consolidation.state
        next_belief <- consolidation.next_belief
        UPDATE_EXPOSURE_FROM_LLM_CALLS(
            scheduler, llm_call_ledger,
            BELIEF_REVISIONS_CREATED(round_ledger, long_state),
            trace_pool union select_pool union anchor_pool)
        scheduler <- UPDATE_TRAIN_SCHEDULER(
                         scheduler, trace_pool, select_pool, anchor_pool,
                         round_ledger)

        if TRAIN_FIXED_POINT(H, H_next, long_state, scheduler,
                             train_protocol.stop_rule):
            frozen <- FREEZE_FOR_FINAL_TEST(
                          H_next, long_state, catalog, train_protocol)
            break

        H <- H_next
        INVALIDATE_CHILD_BELIEFS_ACTIONS_AND_INTERVALS(long_state, H)
        g <- g + 1

    return RUN_FINAL_TEST_ONCE(frozen, D_test)
```

`TRAIN_FIXED_POINT` 必须同时验证：训练 strata 已完成预注册轮换；连续规定代数没有 Harness 晋级；不存在具有正保守净价值的可执行演化、取证或计算动作；unknown 与 misspecification debt 已低于阈值或被安全父版本控制；长期 regime、校准器和层次先验没有待提交修订；当前 Harness 通过近期高保真 select 与全部 anchors。资源或时间耗尽返回 `RESOURCE_STOP`，不能当作固定点。stop 后冻结 Harness、目录、长期 revision、模型、工具、评测器、效用函数与种子，只在 $D_{\mathrm{test}}$ 上运行一次正式评测；测试 trace 只用于报告，不更新 belief、校准、目录、停止证书或 Harness。

## 二、字段、公式与参数完整定义

### 基本约定

| 概念 | 规范 |
| --- | --- |
| 信念 | 对故障原因、方法可迁移性、接入正确性、机制激活、候选效用和评测器可靠性的联合分布。 |
| unknown | 模型当前未覆盖的原因、迁移状态或观测模型；必须保留概率质量，不能分摊给已知假设。 |
| 动作 | 演化、取证、计算、提交、回退或停止；一次循环只执行一个真实动作后重新规划。 |
| 终局决策 | `PROMOTE`、`RETIRE`、`UNRESOLVED` 或保持父版本；中间动作不等同于最终部署。 |
| 效用 | 新能力、旧能力、严重失败、时延、token、稳定性等多维结果经预先声明的效用函数映射。 |
| 安全 | 硬安全和旧能力约束先定义可行集，期望效用不能补偿不可行候选。 |

外层 Harness 代际记为 $g\in\mathbb N_0$，第 $g$ 代父版本记为 $H^{[g]}$；规划器真实执行动作后的信念 revision 记为 $t\in\mathbb N_0$。一代内部可以经历多个 $t$，但最多提交一个新父版本。$K_0$ 表示本次实验冻结的 `DecisionModelCatalogSnapshot`，下标 0 表示它不随在线代际改变；$M_g$ 表示第 $g$ 代开始时已经提交的 `BeliefLongTermState`。

### Benchmark 数据角色与实验协议

| 符号 | 来源与用途 | 隔离约束 |
| --- | --- | --- |
| $D_{\mathrm{train}}$ | benchmark 官方训练集，是在线 belief 更新与 Harness 演化唯一允许使用的任务全集。 | 不含测试实例；官方没有训练集时必须预先声明公开开发集。 |
| $D_g^{\mathrm{trace}}$ | 用 $H^{[g]}$ 产生成功/失败 trace、故障信念和生成视图。 | 本代与 select、anchor 不相交；不能为由它生成的候选提供独立确认。 |
| $D_g^{\mathrm{select}}$ | 候选冻结后用于确认目标效用的任务。 | 生成路径不可见；父子使用同任务、种子、环境和评测器配对。 |
| $D_g^{\mathrm{anchor}}$ | 旧能力、严重失败、评测校准及历史关键行为回放。 | 只更新相应约束与校准，不替代目标收益证据。 |
| $D_{dev}^{(g)}$ | $D_g^{\mathrm{select}}\cup D_g^{\mathrm{anchor}}$。 | 不含本代 trace 任务和测试集。 |
| $D_{\mathrm{test}}$ | 官方封存测试集。 | 训练固定点前不可见；最终冻结状态只运行一次。 |

`TrainProtocol` 字段如下。

| 字段 | 精确定义 |
| --- | --- |
| `benchmark_revision` | benchmark 发布版本及数据校验信息。 |
| `split_revision` | 官方 train/test 划分及训练集内部角色分配规则版本。 |
| `organization_protocol` | 来源对齐、片段粒度、图类型、dependency group、persistence edge、索引和目录审计规则。 |
| `task_strata` | 任务族、难度、工具、故障类型和轨迹长度的预注册分层。 |
| `role_assignment_rule` | 根据分层、暴露、未决信念与 anchors 产生三组互不重叠任务的确定规则或带种子抽样器。 |
| `execution_config` | 模型、provider、推理参数、工具、容器、权限、超时、并发与 trace instrumentation。 |
| `optimizer_config_revision` | `OptimizerLLMConfig`、`OptimizerHarness` 代码、prompt、parser、validator、调用账本和 belief/action schema 的冻结 revision。 |
| `evaluator_revision` | 指标、judge、聚合、方向、缺失和异常处理版本。 |
| `utility_and_risk_config` | $U$、硬阈值、$\delta_k$、CVaR、成本换算、净价值和模型失配参数。 |
| `seeds` | 任务抽样、模型、环境、父子配对和 planner 模拟种子。 |
| `promotion_rule` | 接入、激活、目标、旧能力、风险和近期高保真审计要求。 |
| `stop_rule` | 完整轮换、连续无晋级代数、unknown、开放动作、长期状态和 anchor 的固定点条件。 |

#### `OptimizationAgent`

本方法中的 `OptimizationAgent` 定义为：

$$
\text{OptimizationAgent}=\text{OptimizerLLM}+\text{OptimizerHarness}.
$$

加号表示两者共同构成一个可运行系统。`OptimizerLLM` 是来源因果结构解释、trace 竞争诊断、知识与自由 child 设计、判别证据和计算动作设计、结果模型与多步规划情景构思、事件解释、失配诊断、regime 假设与迁移结构抽象的认知主体。`OptimizerHarness` 维护权限视图、来源图、belief 与动作账本，解析并验证模型输出，拟合或保守界定数值概率，运行代码和真实动作，计算 VOI、风险、置信过程与停止证书，并执行原子提交。

| `OptimizerHarness` 组件 | 确定职责 | 发起的 `OptimizerLLM` 调用 |
| --- | --- | --- |
| `decision_model_compiler_and_retriever` | 固定来源锚点，核验片段和图边，构造 need，执行硬过滤、依赖闭包、来源去重与排序融合。 | `SOURCE_DECISION_MODEL_COMPILATION`、`TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS`、`BUNDLE_DECISION_RELEVANCE_RERANK`。 |
| `belief_conditioned_action_synthesizer` | 构造知识/自由/取证/计算隔离视图，解析共同 IR，拟合结果模型并执行全部静态 gate。 | `METHOD_GUIDED_EVOLUTION_PROPOSAL`、`FREE_BELIEF_EXPANSION_PROPOSAL`、`DISCRIMINATIVE_EVIDENCE_ACTION_PROPOSAL`、`ESTIMATOR_COMPUTATION_ACTION_PROPOSAL`、`ACTION_OUTCOME_MODEL_PROPOSAL`。 |
| `sequential_decision_controller` | 核验多步情景和事件解释，更新 belief，执行 root sampling、VOI、动作选择、置信过程和 stop 证书。 | `BELIEF_TREE_CONTINGENCY_PROPOSAL`、`BELIEF_EVENT_INTERPRETATION`、`PLANNING_STALL_REFLECTION`。 |
| `belief_consolidation_and_transfer_manager` | 重算校准统计，验证 regime 和迁移结构，执行冷启动下限、留一审计与原子提交。 | `CALIBRATION_FAILURE_DIAGNOSIS`、`REGIME_CHANGE_HYPOTHESIS`、`TRANSFER_STRUCTURE_PROPOSAL`。 |
| `llm_call_ledger` | 追加保存全部输入视图、原始输出、解析/核验记录、工具会话和资源消耗。 | 不发起调用。 |

被优化的执行 agent 由执行模型和当前 Harness $H^{[g]}$ 构成，负责在 benchmark 任务上产生 `ExecutionTrace`。即使执行模型与 `OptimizerLLM` 使用同一基础模型，也必须隔离会话、上下文、工具权限、解码配置和调用账本。

#### `OptimizerLLMConfig`

| 字段 | 精确定义 |
| --- | --- |
| `provider_model_revision` | provider、模型名称和不可变 revision 或可审计快照。 |
| `call_types` | 只允许 `SOURCE_DECISION_MODEL_COMPILATION`、`TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS`、`BUNDLE_DECISION_RELEVANCE_RERANK`、`METHOD_GUIDED_EVOLUTION_PROPOSAL`、`FREE_BELIEF_EXPANSION_PROPOSAL`、`DISCRIMINATIVE_EVIDENCE_ACTION_PROPOSAL`、`ESTIMATOR_COMPUTATION_ACTION_PROPOSAL`、`ACTION_OUTCOME_MODEL_PROPOSAL`、`BELIEF_TREE_CONTINGENCY_PROPOSAL`、`BELIEF_EVENT_INTERPRETATION`、`PLANNING_STALL_REFLECTION`、`CALIBRATION_FAILURE_DIAGNOSIS`、`REGIME_CHANGE_HYPOTHESIS`、`TRANSFER_STRUCTURE_PROPOSAL`。 |
| `decoding_by_call_type` | 各调用的 temperature、top-p、最大输出、推理强度、种子、候选数与停止条件。 |
| `prompt_template_revisions` | 各调用的系统指令、输入序列化、输出 schema 与示例 revision。 |
| `context_policies` | 各调用允许披露的来源、代码、trace、belief、bundle、action、result 和 ledger 字段；未列字段默认禁止。 |
| `tool_policy` | 允许访问的代码、分析器和测试工具；禁止读取测试集、隐藏 select 信息或写入已提交 belief。 |
| `retry_policy` | 超时、格式错误和工具失败的重试/退避规则；每次重试创建新 call ID。 |
| `parser_revisions` | 各输出的固定 parser；只能提取或拒绝字段，不能补写模型未输出语义。 |
| `validator_revisions` | 来源、代码、trace、角色、action、event、calibration、regime 与 transfer validator 的 revision。 |
| `resource_accounting` | token、费用、时延、工具运行和失败重试的逐调用记录方式。 |

#### `LLMCallRecord` 与 `OptimizerProposal`

| `LLMCallRecord` 字段 | 精确定义 |
| --- | --- |
| `call_id` | 一次请求的唯一 ID；重试创建新 ID。 |
| `generation_id` | 在线取 $g$；离线使用预分配的 `OFFLINE:<catalog_build_id>`。 |
| `belief_revision` | 调用时可见的 belief revision；离线编译为 `NOT_APPLICABLE`。 |
| `call_type` | `OptimizerLLMConfig.call_types` 中的一种，决定视图、schema 和 validator。 |
| `model_revision` | 实际响应请求的 provider/model revision。 |
| `prompt_template_revision` | 本次系统指令、输入序列化和输出 schema revision。 |
| `input_view_revision` | `OptimizerHarness` 构造的不可变最小权限视图。 |
| `disclosed_object_ids` | 实际披露的来源、代码、trace、belief、bundle、action、result 或 ledger ID。 |
| `forbidden_object_check` | `PASS/FAIL`；检查测试集、隐藏 select、未来 revision 和越权文件，`FAIL` 时不得调用。 |
| `tool_session_id` | 隔离工具会话 ID 或 `NONE`。 |
| `seed` | 实际生成种子或 `UNCONTROLLED`。 |
| `raw_output_ref` | 原始响应的不可变存储引用。 |
| `parsed_output_ids` | 解析产生的 proposal 或 `BeliefActionIR` ID；失败时为空。 |
| `validation_status` | `PENDING/PARSE_FAILED/ANCHOR_REJECTED/GATE_REJECTED/RULE_REJECTED/EVIDENCE_REJECTED/ACCEPTED_AS_PROPOSAL`。 |
| `validation_record_ids` | 对解析对象执行的全部 `ValidationRecord`。 |
| `parent_call_id` | 格式修复或受控重试引用的前一调用；首次为 `NONE`。 |
| `usage` | 输入/输出 token、费用、时延与工具次数，只进入成本和复现统计。 |

除四类动作设计调用直接解析为 `BeliefActionIR` 外，其余响应进入：

| `OptimizerProposal` 字段 | 精确定义 |
| --- | --- |
| `proposal_id` | 不可变提案 ID；同一调用多项响应分别编号。 |
| `call_id` | 产生提案的 `LLMCallRecord`。 |
| `proposal_type` | 必须与 call type 一致。 |
| `target_ids` | 被编译、诊断、解释或修订的来源、fragment、belief、action、event 或 transfer 对象。 |
| `payload` | 下表规定的 call-specific 必填字段。 |
| `evidence_anchors` | 每个关键主张引用的来源、代码、trace、metric、belief revision 或 evidence。 |
| `counterevidence` | 与提案冲突或限制其范围的已知锚点；无时为空。 |
| `uncertainties` | 当前视图不能判断的前提、替代解释和所需观察。 |
| `expected_observations` | 提案正确或错误时应出现的可执行观察。 |
| `validation_status` | `PENDING/ACCEPTED/REJECTED/PARTIALLY_ACCEPTED`，只由 `OptimizerHarness` 写入。 |

| call type | `payload` 必填字段 |
| --- | --- |
| `SOURCE_DECISION_MODEL_COMPILATION` | `{latent_variables,intervention,mechanism_chain,observation_claims,outcome_claims,scope,exclusions,utility_dimensions,dependency_group,unknown_assumptions,edge_candidates}`。 |
| `TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS` | `{competing_causes,earliest_divergences,high_loss_states,unresolved_edges,required_observations,implementation_anchors,unknown_conditions}`。 |
| `BUNDLE_DECISION_RELEVANCE_RERANK` | `{bundle_order,terminal_actions_changed,migration_gaps,refuting_evidence,required_calibrations}`。 |
| `ACTION_OUTCOME_MODEL_PROPOSAL` | `{action_ir_id,result_categories,observable_mapping,state_transition_structure,unknown_branches,calibration_requirements}`；不得直接提供可采用的本地概率。 |
| `BELIEF_TREE_CONTINGENCY_PROPOSAL` | `{action_paths,branch_conditions,observable_outcomes,state_transition_hypotheses,observation_aliases,terminal_decision_changes,unknown_branches}`；只描述可能遗漏的多步语义分支，不得提供可采用的分支概率、VOI 或动作排序。 |
| `BELIEF_EVENT_INTERPRETATION` | `{action_id,result_ids,matched_result_categories,latent_observations,alternative_explanations,missing_measurements,update_targets}`。 |
| `PLANNING_STALL_REFLECTION` | `{stagnation_cause,missing_observation,evidence_or_computation_templates,missing_trace_fields,return_destination}`。 |
| `CALIBRATION_FAILURE_DIAGNOSIS` | `{failed_strata,score_or_coverage_anomalies,candidate_failure_mechanisms,required_checks,next_calibration_observations}`。 |
| `REGIME_CHANGE_HYPOTHESIS` | `{changed_fields,candidate_changepoints,affected_likelihoods,alternative_explanations,required_independent_signals}`。 |
| `TRANSFER_STRUCTURE_PROPOSAL` | `{shareable_effects,scope_predicates,dependency_groups,conflicts,source_components,cold_start_failures,required_audits}`。 |

`LLMCallLedger={ledger_id,schema_revision,optimizer_config_revision,records,latest_revision,storage_ref}` 是实验级只追加账本。`CALL_OPTIMIZER_LLM` 在请求前建立 call ID，并把请求、响应、解析、核验和拒绝事件全部写入该账本。离线调用归入 catalog build；在线调用自动登记到当前 `RoundLedger.llm_call_ids`。任何模型产生的 fragment、need、action IR、规划情景、事件解释、regime 或 transfer revision 都必须回指 call ID 与独立 `ValidationRecord`。

`ExposureRecord={task_id,generation_id,split_role,disclosed_to,disclosed_fields,disclosed_to_call_ids,harness_versions,candidate_ids,action_ids,belief_revision_ids,evidence_ids,independence_status}`。`disclosed_to` 区分生成路径、planner、评测器与长期抽象；`disclosed_to_call_ids` 记录接收字段的具体 LLM 调用。任一任务字段直接或经派生对象影响候选、动作或 belief revision 后，该任务对该对象及其后代永久为 `EXPOSED`，不能通过换标签或跨代轮换恢复独立性。

`DecisionModelCatalogSnapshot={catalog_id,source_packet_revisions,source_graph_revision,index_revisions,organization_protocol_revision,semantic_compilation_call_ids,created_at,frozen}`。`source_graph_revision` 是带来源的节点、边、unknown 状态和 persistence edge；`index_revisions` 覆盖故障、机制、条件、可观测量和依赖索引；`semantic_compilation_call_ids` 含全部成功、失败和拒绝的离线编译调用。`frozen=true` 后任何变化都必须建立新快照和新实验身份。

### 数据字段规范

#### `SourcePacket`

| 字段 | 定义 |
| --- | --- |
| `source_id` | 来源包的稳定标识，只用于引用，不编码质量判断。 |
| `paper_version` | 固定论文版本、元数据和本地原文。 |
| `official_code_version` | 固定官方代码 revision、范围和许可证。 |
| `exact_source_anchors` | 机制、算法、实验和限制的精确定位。 |
| `algorithm_and_ablation_claims` | 原子化算法步骤、消融比较和对应条件；主张与来源一一绑定。 |
| `configs_tests_and_reported_results` | 配置、测试、指标、结果、方差、失败条件和复核状态。 |
| `source_grade` | `A_OFFICIAL_REPRODUCIBLE/B_OFFICIAL_PARTIAL/C_PAPER_ONLY/D_SECONDARY`，只影响检索优先级。 |
| `alignment_status` | 每条 claim 的 `ALIGNED/PAPER_ONLY/CODE_ONLY/UNRESOLVED` 状态。 |
| `extraction_revision` | 结构化提取 revision；修订递增且旧版本保留。 |

#### `DecisionModelFragment`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `fragment_id` | 稳定 ID | 一个干预、机制链和作用域片段的逻辑身份。 |
| `method_id` | 稳定 ID | 该片段描述的方法机制。 |
| `source_anchors` | 锚点列表 | 每条边、条件和结果声明的来源。 |
| `target_failure_causes` | latent state 列表 | 方法直接处理的故障原因，不包含仅相关但不受干预影响的症状。 |
| `required_regime` | regime 谓词 | 模型、工具、任务、Harness 和评测环境必须满足的条件。 |
| `preconditions_and_exclusions` | 谓词对象 | 必要条件与排除条件分别保存，未知条件不视为满足。 |
| `intervention` | 有序程序 | 对 Harness 的具体操作、参数、hook、状态和回退。 |
| `latent_state_dependencies` | 有向边列表 | 干预效果依赖的不可直接观测变量及方向。 |
| `expected_trace_observations` | 观测模型片段 | 在各 latent state 下 trace 事件的预测分布。 |
| `expected_outcomes` | 条件化结果分布 | 新能力、保留、失败、成本和稳定性的预测。 |
| `utility_dimensions` | 维度列表 | 该方法可能影响的效用维度和方向。 |
| `safety_and_legacy_constraints` | 硬谓词列表 | 不可由效用权衡覆盖的安全和旧能力要求。 |
| `observation_model_claims` | 似然声明 | $P(\text{observation}\mid\text{latent state},\text{action},\text{regime})$ 的来源、参数和误差。 |
| `source_dependency_group` | 组 ID | 共享数据、实现或评测器的来源归为一组，防止被当作独立证据重复计算。 |
| `evidence_scope` | 条件范围 | 声明已获支持的任务、Harness、模型、工具和 regime。 |
| `unresolved_assumptions` | 未知列表 | 尚无法校准的边、参数和前提及其取证动作。 |
| `status` | enum | `ACTIVE/UNKNOWN/DEPRECATED/INCOMPATIBLE`；后两项仍保留来源和历史证据。 |
| `revision` | object | 当前 revision、父 revision、结构/参数差分、触发证据与创建时间。 |
| `llm_call_ids` | call id[] | 产生或修订当前语义字段的全部来源编译与迁移调用；纯程序初始化为空。 |
| `field_validation_status` | map | 每个模型提出字段对应的 `SOURCE_VERIFIED/CODE_VERIFIED/TRACE_VERIFIED/EMPIRICALLY_VERIFIED/REJECTED/UNKNOWN` 及验证记录。 |

#### 影响图节点和边

| 节点 | 状态空间 | 定义 |
| --- | --- | --- |
| `TaskRegime` | regime ID/unknown | 当前任务和环境生成机制。 |
| `FailureCause` | 原因枚举 + `unknown_failure` | 产生失败 trace 的潜在原因。 |
| `MethodTransfer` | `VALID/INVALID/UNKNOWN` | 来源方法能否在当前 regime 保持机制。 |
| `IntegrationCorrect` | `TRUE/FALSE/UNKNOWN` | 适配代码是否正确实现机制。 |
| `MechanismActivated` | `TRUE/FALSE/UNKNOWN` | 机制在运行时是否触发。 |
| `Outcome` | 多维随机变量 | 候选的能力、退化、风险和成本。 |
| `EvaluatorReliability` | 校准参数 | 评测器偏差、方差和错误相关性。 |
| `EstimatorState` | 版本化对象 | critic、模拟器或代理模型的参数和校准。 |
| `TerminalUtility` | 实数 | 在硬约束内对 Outcome 的效用。 |

边类型为 `CAUSES`、`OBSERVES`、`REQUIRES`、`EXCLUDES`、`PERSISTS`、`CONFLICTS` 和 `SHARES_EVIDENCE_WITH`。每条边包含方向、条件、regime、参数、来源和状态 `SUPPORTED/OPPOSED/UNKNOWN`。

#### `DecisionNeed`

| 字段 | 精确定义 |
| --- | --- |
| `current_belief_summary` | 当前高概率假设、unknown 质量、后验区间和校准版本。 |
| `generation_id` | 当前 Harness 外层代际 $g$。 |
| `parent_harness` | 本代冻结父版本 $H^{[g]}$。 |
| `generation_view_revision` | 产生查询的 `GenerationBeliefView` revision。 |
| `competing_terminal_actions` | 当前可能成为最优的终局动作集合。 |
| `high_loss_latent_states` | 即使概率不高也会造成大损失的 latent states。 |
| `unresolved_causal_edges` | 对终局决策敏感但状态未知的影响图边。 |
| `observable_trace_fields` | 当前 Harness 实际能产出的字段、类型和时序。 |
| `hard_constraints` | 安全、接口、数据和旧能力硬门。 |
| `current_regime` | 当前环境 ID 和变更证据。 |
| `forbidden_evidence_ids` | 本代 select/anchor 与测试证据，以及其他不得进入生成路径的事件 ID。 |
| `source_call_id` | 产生该 revision 的 `TRACE_BELIEF_AND_DECISION_NEED_DIAGNOSIS`；纯人工预注册 need 为 `NONE`。 |
| `validation_record_ids` | trace、代码、状态、belief revision 和数据角色核验记录；缺失时不得检索。 |

#### `ExecutionTrace`

| 字段 | 精确定义 |
| --- | --- |
| `task_id` | benchmark 任务实例的稳定标识，可连接到唯一暴露记录。 |
| `split_role` | `TRACE/SELECT/ANCHOR/FINAL_TEST`；决定该运行可进入哪种 belief view。 |
| `generation_id` | 产生运行的外层代际 $g$。 |
| `harness_version` | 实际执行的父 Harness 或候选沙箱 revision，并记录候选的父版本。 |
| `model_and_tool_versions` | 模型、provider、推理配置、工具协议、容器与依赖版本。 |
| `seed` | 模型、环境、任务与工具随机性的种子；不可控随机源显式列出。 |
| `ordered_events` | 按真实时间排序的模型调用及可见上下文、工具输入输出、记忆读写、控制转移、重试、回退、异常和终止事件。 |
| `final_output` | 最终产物引用；未产生时为 `null` 并由终止状态解释。 |
| `metric_vector` | 各预注册端点的原始值、方向、评测 revision 与缺失状态。 |
| `termination_status` | `SUCCESS/TASK_FAIL/TIMEOUT/CRASH/TOOL_FAIL/EVALUATOR_FAIL/CANCELLED`。 |
| `artifact_refs` | 上下文快照、状态差分、日志和评测产物的不可变引用。 |

#### `BeliefState_t`

| 字段 | 精确定义 |
| --- | --- |
| `harness_version` | 当前父 Harness 的冻结版本。 |
| `regime_id` | 当前证据 regime。 |
| `posterior_particles` | 粒子状态、权重、生成来源和有效样本量；必须包含 unknown 粒子。 |
| `influence_graph_revision` | 当前使用的图结构和参数版本。 |
| `planner_model_revision` | 当前 prior、likelihood、evaluator 与 estimator 的联合 `PlannerModelRevision`。 |
| `evidence_view` | 从原始账本按时间、regime 和依赖组投影出的可重算视图。 |
| `candidate_versions` | 冻结候选及父关系。 |
| `evaluator_calibration` | judge/指标的偏差、方差、相关性和适用 strata。 |
| `misspecification_debt` | 无法由当前模型解释的预测残差、失败次数和严重度。 |
| `llm_call_ledger_revision` | 该 belief revision 可追溯的最近调用账本 revision；只记录语义来源，不作为后验权重。 |

`GenerationBeliefView={generation_id,parent_harness,as_of_revision,allowed_evidence_ids,excluded_evidence_ids,posterior_revision,influence_graph_revision,unknown_mass,misspecification_debt}`。`allowed_evidence_ids` 只含本代 trace-role 事件和此前已提交事件；`excluded_evidence_ids` 必须显式列出本代 select/anchor 结果及测试证据。`PlanningBeliefView` 使用相同字段，并额外含 `{round_event_ids,select_confirmation_ids,anchor_confirmation_ids}`；它只服务于动作选择与终局判断，不得作为候选生成输入。

#### `Action`

四类模型设计调用统一解析为：

`BeliefActionIR={ir_id,source_call_id,source_channel,parent_harness,generation_view_revision,target_latents,action_family,executable_spec,predicted_observations,predicted_outcomes,unknown_outcome,required_data_role,allowed_effects,cost_factors,risk_factors,reversibility,fallback,unresolved_conditions,ancestor_ir_ids,llm_call_ids,validation_status}`。

| `BeliefActionIR` 字段 | 精确定义 |
| --- | --- |
| `ir_id` | 不可变 IR revision ID；任一字段变化创建新 ID。 |
| `source_call_id` | 直接产生该 IR 的四类动作设计调用之一。 |
| `source_channel` | `METHOD_GUIDED/FREE_BELIEF_EXPANSION/EVIDENCE_DESIGN/COMPUTATION_DESIGN`，只表示输入隔离通道。 |
| `parent_harness` | 动作附着的确切父 Harness revision。 |
| `generation_view_revision` | 生成时可见的权限受限 belief view。 |
| `target_latents` | 动作预期改变或观察的潜变量及 revision。 |
| `action_family` | 演化、取证或计算动作的具体子类型。 |
| `executable_spec` | 演化动作的 typed patch、取证动作的 probe/strata/fidelity 模板，或计算动作的 estimator 操作。 |
| `predicted_observations` | 每个结果类别下应出现的 trace/metric/构建观察。 |
| `predicted_outcomes` | 对终局效用维度的方向、范围和观察窗口，不是可直接采用的概率。 |
| `unknown_outcome` | 现有模型无法解释或测量失败时的显式分支；必填。 |
| `required_data_role` | 可绑定的 `TRACE/SELECT/ANCHOR/SYNTHETIC_PROBE/COMPUTATION` 角色。 |
| `allowed_effects` | 可更新 generation belief、planning belief、Harness 或 estimator 的范围。 |
| `cost_factors` | token、费用、时延、工具、硬件和人工成本要素。 |
| `risk_factors` | 权限、不可逆、严重失败、模型失配和旧能力风险。 |
| `reversibility` | 逆操作、恢复点、可恢复范围与验证条件。 |
| `fallback` | 构建、执行、评测或回归失败时的可执行处理。 |
| `unresolved_conditions` | 必须通过 calibration/evidence 回答后才能执行或晋级的问题。 |
| `ancestor_ir_ids` | 受控修订所依赖的直接父 IR；首次提案为空。 |
| `llm_call_ids` | 对当前 IR 有语义贡献的完整调用谱系。 |
| `validation_status` | 接口、权限、角色、回滚、隔离、硬安全和结果模型校准的逐项 `PASS/FAIL/UNKNOWN`。 |

任何硬项非 `PASS` 的 IR 都不能冻结。

每个冻结动作具有共同 envelope：`{action_id,action_type,parent_harness,belief_revision,generator_view_revision,ir_ids,parameters,predicted_result_distribution,state_transition,cost_distribution,risk,reversibility,required_data_role,allowed_effects,status,provenance,llm_call_ids,hard_gate_status,frozen_at}`。`predicted_result_distribution` 必须包含 `unknown_model`，数值来自 `PlannerModelRevision` 的拟合或保守界而非模型自报；`required_data_role` 规定允许绑定的任务角色；`allowed_effects` 区分可更新生成信念、规划信念、Harness 或 estimator 的范围；任一共同字段变化都生成新 `action_id`。

| 动作 | 参数 | 精确定义 |
| --- | --- | --- |
| `EvolutionAction(method_guided)` | 方法束、候选编辑、父版本 | 使用决策模型片段实例化干预。 |
| `EvolutionAction(free_exploration)` | 编辑范围、生成策略、父版本 | 针对 unknown 后验质量提出不受方法模板限制的候选，仍服从硬约束。 |
| `EvidenceAction(probe)` | probe、候选、任务 strata | 运行局部机制或诊断观测。 |
| `EvidenceAction(ablation)` | mask、对照、配对设置 | 隔离机制贡献。 |
| `EvidenceAction(short_rollout)` | 任务、步数、重复 | 低覆盖运行，结果必须经过保真校准。 |
| `EvidenceAction(full_dev)` | 完整开发协议 | 获得目标保真证据。 |
| `EvidenceAction(independent_review)` | 审核对象、盲化信息 | 由独立评测器或人工复核高风险结论。 |
| `ComputationAction(critic)` | 输入视图、模型 | 增加诊断或候选评分，不产生真实环境证据。 |
| `ComputationAction(simulation)` | 生成模型、rollout 数 | 估计动作后果；输出受模型失配惩罚。 |
| `ComputationAction(estimator_refit)` | 数据视图、模型 revision | 更新似然、代理或校准器。 |
| `commit` | 候选 ID | 将候选作为下一父版本；需停止证书。 |
| `revert` | 祖先版本 ID | 回到已验证版本并关闭失败分支。 |
| `stop` | 终局动作 | 结束当前谱系并输出 `PROMOTE/RETIRE/UNRESOLVED`。 |

#### `Evidence`

| 字段 | 精确定义 |
| --- | --- |
| `evidence_id` | 不可复用的稳定标识；纠错通过新事件的 `supersedes` 字段完成。 |
| `candidate` | 候选或父版本 ID。 |
| `data_role` | `TRACE/SELECT/ANCHOR/SYNTHETIC_PROBE/COMPUTATION/EXTERNAL_SOURCE`。 |
| `confirmation_role` | `DISCOVERY/CONFIRMATION/ESTIMATOR_ONLY`；只有合格 `CONFIRMATION` 能决定晋级，计算动作固定为 `ESTIMATOR_ONLY`。 |
| `evidence_type` | 静态、probe、消融、短 rollout、完整开发或独立复核。 |
| `task_stratum` | 任务族、难度、故障类型和数据 split。 |
| `fidelity_vector` | 见“保真度向量”公式定义的五维保真度。 |
| `seed` | 随机种子及模型采样配置。 |
| `outcome` | 多维原始指标和硬门状态。 |
| `trace_features` | 用于更新 observation model 的事件特征。 |
| `execution_cost` | token、费用、时延、工具和人工成本。 |
| `environment` | 模型、工具、容器、权限、评测器和时间版本。 |
| `exposure_record_id` | 对应任务及披露历史；纯计算和外部来源可为 `null`。 |
| `selection_propensity` | 在结果产生前，该动作和任务被当前策略选择的概率及策略 revision。确定性选择记为 1。 |
| `action_id` | 生成该证据的冻结动作。 |
| `trace_id` | 真实环境动作产生的 `ExecutionTrace`；静态或纯计算动作可为 `null`。 |
| `supersedes` | 被纠正事件 ID；无纠错时为 `null`。 |
| `interpretation_call_ids` | 对原始 action result 提出潜变量观察与替代解释的 `BELIEF_EVENT_INTERPRETATION` 调用；原始 outcome 不依赖这些解释。 |
| `validation_record_ids` | 将解释映射到 action、trace、指标、代码和数据角色的核验记录；未通过字段不进入 belief update。 |

角色映射固定为：`TRACE` 与 `SYNTHETIC_PROBE` 只能是 `DISCOVERY`；`SELECT` 只能在候选冻结后成为目标端点的 `CONFIRMATION`；`ANCHOR` 的 `CONFIRMATION` 只进入对应旧能力、风险或校准端点；`COMPUTATION` 只能是 `ESTIMATOR_ONLY`，其输出不能作为环境结果。违反映射的事件不得进入 belief 更新。一个任务一旦影响某候选的生成，即使后续改标 `SELECT` 也不能恢复对该候选的确认独立性。

#### `BeliefLongTermState`

| 字段 | 精确定义 |
| --- | --- |
| `raw_evidence_ledger` | 追加写的原始证据、选择概率和环境元数据。 |
| `evidence_views` | 不同时间/regime/任务投影；可从原始账本重算。 |
| `prior_and_likelihood_revisions` | 先验和观测模型的全部版本、训练数据指针和原因。 |
| `belief_snapshots` | 每次真实动作前后的 `BeliefState_t`。 |
| `decision_records` | 候选动作、预测价值、实际动作、结果和终局决定。 |
| `regime_history` | 变化点、拆分、折扣、合并和复查记录。 |
| `evaluator_calibration_history` | 评测器按 strata 的校准版本。 |
| `hierarchical_task_priors` | 全局、任务族和任务级条件效应分布。 |
| `cold_start_shadow_models` | 不使用历史迁移证据的对照先验和决策。 |
| `source_dependency_groups` | 共享来源、数据或评测器的证据组。 |
| `llm_call_ledger_revisions` | 每次已提交长期 revision 所引用的调用账本 revision；调用记录只提供语义谱系，不作为独立 Evidence。 |
| `latest_revision` | 最近一次通过审计并原子提交的长期状态 revision；影子更新不计入。 |

`BeliefSnapshot` 是给定原始证据视图、先验 revision、似然 revision 和图 revision 后可重算的后验；`DecisionRecord` 保存当时全部可选动作及价值，防止只记录最终动作造成选择偏差。

### 公式逐项定义

#### 候选效用状态

$$
\theta_c=(\text{new capability},\text{legacy retention},\text{severe failure},\text{latency},\text{token cost},\text{stability}).
$$

`c` 是候选。`new capability` 是目标新能力指标；`legacy retention` 是旧任务/接口保持量；`severe failure` 是安全、数据或不可恢复失败的概率与严重度；`latency` 是端到端墙钟分布；`token cost` 分开记录执行与优化 token；`stability` 是跨种子、任务和重复的方差/复现率。每一维保留分布，不提前合成。

#### 保真度向量

$$
z=(\text{task coverage},\text{rollout horizon},\text{seed count},\text{judge strength},\text{environment realism}).
$$

`task coverage` 是开发任务 strata 覆盖；`rollout horizon` 是最大步数/时间；`seed count` 是独立重复数；`judge strength` 是评测器版本、校准和独立性等级；`environment realism` 是相对部署环境的容器、工具、网络和权限一致性。保真度是偏序向量，不允许默认将五维压成单一等级。

#### 可行候选集

$$
\mathcal F(b)=\{c:\Pr(\theta_{c,k}\ \text{satisfies}\ \tau_k\mid b)\ge 1-\delta_k,\ \forall k\}.
$$

`b` 是当前信念；`c` 是候选；`k` 遍历每个硬安全或旧能力维度；`θ_{c,k}` 是候选在维度 `k` 的真实值；`τ_k` 是该维度阈值；`δ_k` 是允许的后验违规概率；`F(b)` 是满足所有概率约束的候选集。若集合为空，终局只能保持父版本或 `UNRESOLVED`。

#### 当前最优终局价值

$$
D(b)=\max_{c\in\mathcal F(b)}\mathbb E[U(\theta_c)\mid b]-\operatorname{RiskPenalty}(c,b).
$$

`U(θ_c)` 是预先声明的多目标效用；`RiskPenalty` 只惩罚硬门之外的尾部风险、模型失配和不可逆性；`D(b)` 是在当前信念下立即终止可获得的最佳净价值。父版本始终作为可选 `c`，保证有安全基线。

#### 取证动作的决策价值

$$
\operatorname{DecisionVOI}(a)=\mathbb E_o[D(\operatorname{Update}(b,a,o))]-D(b).
$$

$a$ 是取证或计算动作；$o$ 是可能结果；`Update` 按动作、结果和 regime 更新信念；外层期望使用 $P(o\mid b,a)$；`DecisionVOI` 只度量信息导致终局选择改善的价值，不包含执行成本。

#### 演化动作价值

$$
\operatorname{InterventionVOI}(a)=\mathbb E_r[D(\operatorname{UpdateAndExpand}(b,a,r))]-D(b).
$$

`a` 是演化动作；`r` 是代码生成、静态 gate 和初步机制结果；`UpdateAndExpand` 同时增加新候选节点并更新故障/迁移信念；该值允许新候选扩大终局动作集。生成失败或硬门失败也属于 `r`。

#### 动作净价值

$$
\operatorname{NetValue}(a)=\operatorname{VOI}(a)-\lambda_t\mathbb E[T_a]-\lambda_c\mathbb E[C_a]-\operatorname{Risk}(a)-\operatorname{MetaCost}(a).
$$

`VOI(a)` 对取证/计算动作使用 `DecisionVOI`，对演化动作使用 `InterventionVOI`；`T_a` 是墙钟；`C_a` 是货币或 token 成本；`λ_t,λ_c≥0` 是单位转换系数；`Risk(a)` 是不可逆、权限、严重失败和模型失配风险；`MetaCost(a)` 是 optimizer 推理、模拟和调度开销。硬约束失败动作不参与 argmax。

#### 多保真校准残差

$$
\Delta(c,z,r)=y(c,z^*)-\operatorname{Calibrator}_z(y(c,z),x_c,r).
$$

$c$ 是候选；$z$ 是低保真向量；$z^*$ 是目标保真协议；$r$ 是 regime；$y(c,z)$ 是低保真观测；$x_c$ 是候选结构、任务和 trace 特征；$\operatorname{Calibrator}_z$ 把低保真结果映射为目标保真预测；$\Delta$ 是真实目标结果与预测之差。校准器按候选选择过程和任务 strata 训练，残差区间过宽时低保真证据不得淘汰候选。

#### 带冷启动下限的迁移先验

$$
P_T(\theta)=\pi_{cold}P_{cold}(\theta)+\sum_{q\in\mathcal G_T}\pi_qP_q(\theta),\qquad \pi_{cold}\ge\pi_{min}.
$$

`T` 是目标任务；$\mathcal G_T$ 是经硬条件过滤后与目标任务相关的历史任务族/regime 集合；$q$ 是其中一个历史分量，不是外层 Harness 代际；$P_{cold}$ 是完全不使用历史任务的先验；$P_q$ 是分量 $q$ 的条件效应分布；$\pi_{cold}$ 和全部 $\pi_q$ 非负且满足 $\pi_{cold}+\sum_{q\in\mathcal G_T}\pi_q=1$；$\pi_{min}>0$ 保证冷启动模型不会被历史先验完全压制。目标证据到达后按预测表现更新混合权重，负迁移时增加 $\pi_{cold}$ 或拆分 regime。

### 停止证书

执行 `stop` 必须同时满足：

1. 当前最优终局动作相对次优动作的后验决策优势超过预设阈值；
2. 所有硬约束的满足概率达到各自 `1-δ_k`；
3. unknown 后验质量低于阈值，或其最坏损失已被安全动作控制；
4. 所有未执行动作的 `NetValue` 保守上界不为正，或剩余动作违反硬安全、数据隔离或不可逆风险约束；
5. 评测器校准和多保真残差在当前 task strata 与 regime 内有效；
6. 决策记录包含全部候选动作、价值估计、数据版本和模型 revision。

任何一项不满足，输出 `UNRESOLVED` 或继续取证，不能用最高均分替代停止证书。

外层 Harness 代际转移为

$$
H^{[g+1]}=
\begin{cases}
c_g^*, & \text{若控制信号为 }\mathtt{PROMOTE}\text{ 且 }c_g^*\text{ 通过全部门},\\
H^{[g]}, & \text{若控制信号为 }\mathtt{RETIRE}\text{ 或 }\mathtt{UNRESOLVED}.
\end{cases}
$$

$g$ 是外层代际，$H^{[g]}$ 是本代父 Harness，$c_g^*$ 是停止证书指定的唯一冻结候选。回退动作先恢复经过确认的祖先，再把该版本作为代际末的父 Harness。单次 $H^{[g+1]}=H^{[g]}$ 不是训练固定点；还必须满足 `TrainProtocol.stop_rule` 中的完整训练轮换、连续无晋级、无正保守净价值动作、unknown/失配受控、长期状态稳定和 anchors 通过。

### 四阶段接口

| 阶段 | 输入 | `OptimizerLLM` 的语义工作 | `OptimizerHarness` 的确定工作与输出 | 完成条件 |
| --- | --- | --- | --- | --- |
| loop 外决策模型组织 | `SourcePacket[]`、组织协议 | 提出潜变量、干预—机制—观察片段、unknown 假设和候选图边。 | 核验来源/代码/图类型/dependency group，编译并审计冻结 $K_0$。 | 每条边有状态、条件、来源和 dependency group，目录审计通过。 |
| loop 内 need 与决策模型检索 | trace-role evidence、$K_0$、$M_g$、`as_of` | 提出竞争原因、高损失状态、未决边，并比较可达 bundle 的终局影响。 | 核验 trace/代码/状态/角色，执行硬过滤、依赖闭包、去重和排序融合，输出 need、bundle 与待校准边。 | 关键决策缺口有可绑定 bundle 或显式不可达/unknown 结论。 |
| 信念条件动作生成 | $H^{[g]}$、`GenerationBeliefView`、trace batch、bundle | 设计知识/自由 child、判别 evidence、computation 及结果结构。 | 统一解析为 IR，拟合/界定概率，执行代码、接口、角色、隔离、回滚和硬安全 gate，输出冻结动作。 | unknown 保留；每个动作有可校准结果模型、成本、风险、可逆性与数据角色。 |
| 单步规划与执行 | `PlanningBeliefView`、冻结动作、select/anchor 池、暴露账本 | 补足会改变终局选择的多步语义分支，解释真实事件；停滞时提出可核验 evidence/computation 或合法前序返回。 | 核验并界定情景分支，更新 belief，执行 root sampling、VOI、argmax、置信过程与 stop 证书，输出控制信号和 `RoundLedger`。 | 每执行一步重新规划；选择数据不能回流生成，晋级只由证书决定。 |
| 信念沉淀与迁移 | $M_g$、完整 `RoundLedger`、下一 regime | 提出失配机制、regime 变化和可共享迁移结构。 | 重算 calibration/change-point/冷启动权重，执行留一审计与原子提交，输出 $M_{g+1}$ 和下一代 belief。 | 选择元数据完整，冷启动下限、regime 与留一审计通过。 |
| stop 后正式测评 | 冻结 Harness、目录、长期 revision、协议、$D_{\mathrm{test}}$ | 不调用。 | 只读运行一次最终测试，输出指标与审计 trace。 | 不更新任何训练状态。 |

### 复合类型、状态与数学约定

| 对象 | 完整定义 |
| --- | --- |
| `EvidenceView` | `{as_of,regime_filter,task_filter,dependency_groups,event_ids,selection_propensities,view_revision}`；它是账本投影，不复制或改写事件。 |
| `ValidationRecord` | `{validation_id,validator_revision,target_id,field_or_operation,input_revision,result,evidence_refs,reason,created_at}`；`result` 取 `PASS/FAIL/UNKNOWN`，不能由被核验的同一次模型调用自证。 |
| `HarnessVersion` | `{harness_id,revision,parent_revision,source_tree,config,dependency_lock,model_interface,tool_interfaces,lifecycle_hooks,observability_schema,fallback_entry,commit_record}`；源码、配置和依赖锁共同决定可重放版本。 |
| `CandidateVersion` | `{candidate_id,parent_harness,origin,source_action_id,ir_ids,patch,config_delta,dependency_delta,predicted_latents,predicted_observations,predicted_outcomes,fallback,status,provenance,llm_call_ids,hard_gate_status,frozen_at}`；`origin` 为 `METHOD_GUIDED/FREE_EXPLORATION`，全部硬项必须 `PASS`，父版本或任一差分改变都创建新 ID。 |
| `Regime` | `{task_family,dataset_split,instance_stratum,executor_model,model_config,tool_versions,harness_revision,evaluator_revision,environment_id,time_window}`；字段变化产生新 regime，显式投影才可合并。 |
| `ModelBundle` | `{bundle_id,fragment_ids,graph_revision,dependency_closure,conflicts,unresolved_assumptions,required_local_calibrations,source_dependency_groups,terminal_relevance_upper_bound,provenance}`；它是一次检索返回的可接入片段闭包，不携带未声明的本地概率。 |
| `PlannerModelRevision` | `{graph_revision,prior_revision,likelihood_revision,evaluator_revision,estimator_revision,training_event_ids,calibration_report}`；它唯一确定 planner 使用的生成模型与校准状态。 |
| `VerifiedContingencySet` | `{set_id,belief_revision,planner_model_revision,planning_horizon,path_revisions,validation_record_ids,llm_call_ids,created_at}`；`planning_horizon` 是训练协议冻结的正整数，表示一次规划模拟最多包含的动作步数；`path_revisions` 中每条路径为 `{path_id,ordered_action_types,branch_conditions,observable_outcomes,state_transitions,observation_aliases,terminal_decision_changes,unknown_branches,probability_source,bounds,status}`。`ordered_action_types` 只能引用当前合法动作类型且长度不超过 `planning_horizon`；`branch_conditions` 是进入该分支前可检查的 belief 或 observation 条件；`observable_outcomes` 必须映射到已声明结果 schema；`state_transitions` 只能修改动作 `allowed_effects` 允许的状态；`observation_aliases` 列出不同潜在状态产生相同观察的情况；`terminal_decision_changes` 说明该路径可能改变哪个终局动作；`unknown_branches` 显式保留未建模后果；`probability_source` 只能引用 `PlannerModelRevision` 的拟合器、保守界或 `UNMODELED`，不得引用模型自报概率；`bounds` 是程序计算的概率区间，`UNMODELED` 时为 `[0,1]`；`status` 由程序写为 `VERIFIED/REJECTED/UNKNOWN`。 |
| `BeliefSnapshot` | `{snapshot_id,as_of,evidence_view_revision,planner_model_revision,particle_state,unknown_mass,misspecification_debt,llm_call_ledger_revision,created_by_action}`；全部概率和派生量必须可由 evidence 与 revisions 重算，调用账本仅说明语义解释来源。 |
| `DecisionRecord` | `{decision_id,generation_id,belief_snapshot_id,available_action_ids,predicted_value_distributions,selected_action_id,selection_propensity,result_event_id,terminal_control,rule_revision,llm_call_ids}`；未选择动作也必须记录，`llm_call_ids` 记录参与 action、规划情景与 event 语义构造的调用，不能把调用本身计作环境证据。 |
| influence edge | `{edge_id,source,target,type,condition,regime,parameters,source_anchors,dependency_group,status,revision,llm_call_ids,validation_record_ids}`；类型只取 `CAUSES/OBSERVES/REQUIRES/EXCLUDES/PERSISTS/CONFLICTS/SHARES_EVIDENCE_WITH`；LLM 只能提议，状态由来源/经验验证决定。 |
| posterior particle | `{latent_assignment,weight,source_component,unknown_flags,regime,revision}`；权重非负且总和为 1。 |
| action status | `KEEP` 表示仍可执行，`DISCOUNT` 表示证据陈旧但保留，`SPLIT` 表示新建 regime，`CONTINUE` 表示尚无终局证书。 |
| terminal status | `PROMOTE`、`RETIRE` 或 `UNRESOLVED`；`CONTINUE` 不是终局状态。 |
| unknown state | `unknown_model` 表示观测模型无法解释事件；`unknown_transfer` 表示迁移合法性未知；`observation_misspecification` 表示似然校准失败。三者保留独立概率质量。 |
| `OrganizationProtocol` | `{fragment_granularity,graph_type_schema,source_alignment_rules,semantic_compilation_prompt_revision,semantic_compilation_parser_revision,semantic_field_verifier_revision,dependency_group_rules,persistence_rules,index_schema,audit_checks}`；全部在目录构建前冻结，审计至少覆盖来源可达、unknown 完备、非法边、依赖去重和索引可复算。 |
| `SchedulerState` | `{protocol_revision,generation_id,strata_state,exposure_ledger,coverage_state,open_decision_needs,anchor_registry}`；记录训练角色分配、案例披露、完整轮换进度和 anchor 最近通过代际。 |
| `RoundLedger` | `{generation_id,parent_harness,trace_ids,events,action_ids,llm_call_ids,llm_call_ledger_revision,exposure_record_ids,belief_revisions,terminal_control,select_disclosure_status,resource_status}`；`events` 是有序 `Evidence[]`，成功、失败和拒绝调用全部追加；`select_disclosure_status` 为 `HIDDEN` 或 `DISCLOSED_TO_GENERATION_PATH`。 |
| `FrozenTestPackage` | `{experiment_id,harness_version,catalog_id,long_term_revision,train_protocol_revision,optimizer_config_revision,llm_call_ledger_revision,model_and_tool_versions,evaluator_revision,utility_revision,seeds,frozen_at}`；任一字段改变都产生新实验身份；终局测试不调用 `OptimizerLLM`。 |

$\mathbf1[P]$ 是指示函数；`UNKNOWN` 不算真。所有期望都相对于公式明确给出的预测分布；所有 `argmax` 并列依次选择硬风险更低、可逆性更强、预计成本更低和稳定 action ID 更小者。概率归一化分母为零时必须扩展 unknown 组件，不能改成均匀分布。

### 公式参数的完整计算规则

候选状态每一维记为随机变量 $\theta_{c,d}$，并保存 `{support,distribution,mean,quantiles,source_model,updated_at}`。效用固定为

$$
U(\theta_c)=\sum_{d\in D_{soft}}u_d\,\bar\theta_{c,d}-
u_f\,\operatorname{CVaR}_{\alpha_f}(L_{severe}(\theta_c)),
$$

其中 $D_{soft}$ 是新能力、保留、时延、token 和稳定性中的软目标维度，$\bar\theta_{c,d}\in[0,1]$ 均已转成越大越好，$u_d,u_f\ge0$ 且总和为 1；$L_{severe}\in[0,1]$ 是严重失败损失，$\alpha_f\in(0,1)$ 是冻结的尾部水平。硬安全维度只进入 $\mathcal F(b)$，不进入加权补偿。

保真向量 $z=(z_1,\ldots,z_5)$ 的每个分量都在 `[0,1]`：任务覆盖按已覆盖 strata 权重计算，rollout horizon 按目标步数截断归一化，seed count 按目标独立重复数截断归一化，judge strength 来自当前 strata 的校准等级，environment realism 是部署接口/工具/权限匹配的加权比例。偏序 $z\preceq z'$ 当且仅当五维逐项不大于。

可行集中的 $k$ 只遍历硬约束，$\tau_k$ 包含方向和值；“满足”事件按方向写为 $\theta_{c,k}\ge\tau_k$ 或 $\theta_{c,k}\le\tau_k$。$\delta_k\in(0,1)$ 在查看证据前分配，并满足 $\sum_k\delta_k\le\delta_{hard}$。后验概率使用当前 `BeliefState_t` 的加权粒子或解析分布计算；unknown 粒子按最坏硬门结果计入。

$$
\operatorname{RiskPenalty}(c,b)=
\rho_t\operatorname{CVaR}_{\alpha_t}(L_c\mid b)+
\rho_m M_c(b)+\rho_i I_c,
$$

$L_c$ 是硬门之外的尾部损失，$M_c(b)\in[0,1]$ 是由 misspecification debt 归一化得到的模型失配，$I_c\in[0,1]$ 是不可逆度；$\rho_t,\rho_m,\rho_i\ge0$。$D(b)$ 的最大化集合始终含父版本；若除父版本外为空，$D(b)$ 等于父版本净价值。

`DecisionVOI` 中 $o\sim P(o\mid b,a)$，`InterventionVOI` 中 $r\sim P(r\mid b,a)$；两种预测分布均由当前 `ModelBundle` 产生并保留 `unknown_model` 结果。`Update` 只更新既有状态，`UpdateAndExpand` 还加入新候选与迁移状态。计算动作的 VOI 必须扣除估计器自身校准误差，不能把模型输出当环境证据。

动作成本统一为

$$
\operatorname{NetValue}(a)=VOI(a)-\lambda_t\mathbb E[T_a]
-\lambda_c\mathbb E[C_a]-\rho_aR_a-\mu_aM_a,
$$

$T_a$ 用小时，$C_a$ 用协议货币单位；$\lambda_t,\lambda_c$ 是效用/单位换算系数。$R_a\in[0,1]$ 是权限、不可逆和严重失败软风险，$M_a\in[0,1]$ 是优化器推理、模拟与调度开销归一值，$\rho_a,\mu_a\ge0$。硬违规动作在计算前移除。仅当最大 `NetValue` 大于停止阈值 $\epsilon_{act}\ge0$ 或硬门要求取证时才执行。

校准残差中 $y(c,z)$ 必须声明指标和方向，$x_c$ 只含选择时可见特征；`Calibrator_z` 保存训练 strata、选择 propensity、损失、区间覆盖和 revision。残差上界超过 $\epsilon_{cal}$ 时，该低保真层只能生成后续取证动作。迁移混合中 $\pi_{cold}+\sum_{q\in\mathcal G_T}\pi_q=1$、$\pi_{cold}\ge\pi_{min}>0$；同一 dependency group 的多个 $P_q$ 先组内合并，不能作为独立分量重复增权。

### 伪代码算子契约

| 组织检索算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `OFFLINE_ORGANIZE_DECISION_MODELS` | 来源包、组织协议、`LLMCallLedger` → 冻结 `DecisionModelCatalogSnapshot`；只在 benchmark loop 外执行。 |
| `FREEZE_DECISION_MODEL_CATALOG` | 来源影响图、组织协议 → 不可变 `DecisionModelCatalogSnapshot`；审计失败不生成快照。 |
| `MATERIALIZE_DECISION_GRAPH` | $K_0$、已提交长期状态、`as_of` → 截至指定 revision 可见的组合影响图；来源层只读，未来证据不可见。 |
| `RETRIEVE_DECISION_MODELS` | $K_0$、$M_g$、need、`as_of` → 方法束与本地校准项；不联网补来源，未找到与不可达分开返回。 |
| `FIX_DECISION_MODEL_SOURCE_UNITS` | 来源包、对齐规则 → 有论文/代码/配置/消融/结果锚点的不可变单元；不能定位者保持未对齐。 |
| `BUILD_DECISION_MODEL_COMPILATION_REQUESTS` | 来源单元、组织协议 → 最小权限语义编译请求；目标 benchmark 数据不可见。 |
| `CALL_OPTIMIZER_LLM` | 经禁止对象检查的输入视图、call type、配置 → 原始响应与追加的 `LLMCallRecord`；失败与拒绝仍入账。 |
| `PARSE_DECISION_MODEL_COMPILATION_PROPOSALS` | 来源编译调用 → `OptimizerProposal[]`；parser 不补写缺失语义。 |
| `VERIFY_DECISION_MODEL_SOURCE_FIELDS` | 编译提案、来源单元 → 逐字段值、锚点和验证状态；模型解释不能替代来源或代码证据。 |
| `COMPILE_DECISION_MODEL_FRAGMENTS` | 来源包、经核验字段 → 有来源的节点、边和观测模型片段；未知参数显式保留。 |
| `BUILD_VERSIONED_INFLUENCE_GRAPH` | fragments → 无非法类型边的 revision 图；环仅在允许反馈边中存在。 |
| `BUILD_DECISION_NEED_FROM_TRACE_AND_BELIEF` | generation view、trace、父 Harness、长期状态 → 经 LLM 提议和程序核验的 `DecisionNeed`；select/anchor/test 禁止进入。 |
| `BUILD_TRACE_BELIEF_NEED_REQUEST` | 同上最小切片 → 诊断视图；只含允许 evidence、代码锚点和已提交 belief。 |
| `PARSE_TRACE_BELIEF_NEED_PROPOSAL` | 诊断调用 → 竞争原因、高损失状态、未决边和 required observations 草案。 |
| `VERIFY_TRACE_CODE_BELIEF_AND_ROLE_ANCHORS` | 诊断草案、trace、代码、belief、暴露账本 → 合法 need revision；无锚点项保持 unknown。 |
| `FIELD_AWARE_RETRIEVE` | 图、need → 字段级 seeds；不以整段文本替代字段匹配。 |
| `HARD_FILTER_WITH_UNKNOWN_PRESERVED` | seeds、硬门 → eligible/unknown/rejected；unknown 不误删。 |
| `DEPENDENCY_CLOSURE_AND_SOURCE_DEDUP` | seeds、图 → 依赖闭包 bundles；同 dependency group 不重复计证据。 |
| `RANK_BY_TERMINAL_DECISION_RELEVANCE` | bundles、belief → 对当前终局选择影响的确定排序。 |
| `BUILD_BUNDLE_DECISION_RERANK_REQUEST` | 已硬过滤 bundle、need → 仅允许比较剩余项的语义视图。 |
| `PARSE_BUNDLE_DECISION_RERANK` | rerank 调用 → 终局动作影响、迁移缺口、反驳 evidence 与校准需求。 |
| `FUSE_DECISION_BOUNDS_AND_VERIFIED_SEMANTIC_RANKS` | 终局价值上界排序、经核验语义排序 → 唯一检索顺序；语义排序不能覆盖 hard filter 或上界淘汰。 |
| `REQUIRED_LOCAL_CALIBRATIONS` | bundles → 待校准边、参数及可执行动作。 |

| 动作生成算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `GENERATE_BELIEF_CONDITIONED_ACTIONS` | Harness、`GenerationBeliefView`、trace batch、bundles、待校准边 → 通过 hard gate 的冻结动作；不得读取本代 select/anchor 结果。 |
| `UPDATE_FROM_VERSIONED_TRACE` | belief、trace → 新 belief revision；原 trace 不覆盖。 |
| `EXPAND_UNKNOWN_IF_PREDICTIVE_CHECK_FAILS` | belief、预测检查 → 新 unknown 粒子；禁止把零似然重归一化。 |
| `DECISION_NEEDS_FROM_POSTERIOR_MASS` | belief → 高损失或决策敏感的程序 pre-need；必须再经 trace-belief 诊断与锚点核验才成为 `DecisionNeed`。 |
| `BUILD_METHOD_GUIDED_EVOLUTION_REQUEST` | Harness、bundle、belief、trace → 合法孔域、代码切片、机制和义务视图；固定来源机制不可改写。 |
| `PARSE_METHOD_GUIDED_BELIEF_ACTION_IR` | method-guided 调用 → `BeliefActionIR[]`；越出孔域或缺少激活/fallback 时拒绝。 |
| `UNEXPLAINED_POSTERIOR_REGIONS` | belief、bundle、知识 IR → 未被可执行知识解释覆盖的 unknown/high-loss 区域；按决策影响而非熵排序。 |
| `BUILD_FREE_BELIEF_EXPANSION_REQUEST` | Harness、belief、trace、未覆盖区域 → 不含本轮知识 patch 的自由视图。 |
| `PARSE_FREE_BELIEF_ACTION_IR` | free 调用 → 新机制边与 child 的共同 IR；无法声明可观测预测和反证条件时拒绝。 |
| `BUILD_DISCRIMINATIVE_EVIDENCE_REQUEST` | belief、校准缺口、候选 IR → 竞争世界和允许 evidence primitives 的视图。 |
| `PARSE_EVIDENCE_ACTION_IR` | evidence-design 调用 → probe/ablation/task-strata/fidelity 模板 IR；不在此绑定 select/anchor 实例。 |
| `BUILD_ESTIMATOR_COMPUTATION_REQUEST` | belief、校准/失配状态 → 仅允许 estimator effect 的视图。 |
| `PARSE_COMPUTATION_ACTION_IR` | computation-design 调用 → critic/simulation/refit IR；`allowed_effects` 必须为 estimator/planning only。 |
| `BUILD_ACTION_OUTCOME_MODEL_REQUEST` | action IR、planner model revision → 结果类别、可观察映射和 unknown 分支视图。 |
| `PARSE_ACTION_OUTCOME_MODEL_PROPOSALS` | outcome-model 调用 → 结构化结果模型草案；模型自报概率字段被丢弃。 |
| `FIT_OR_BOUND_AND_ATTACH_ACTION_MODELS` | IR、结果模型草案、校准数据 → 带拟合分布或保守界的 IR；数据不足时保留 `unknown_model`。 |
| `COMMON_BELIEF_ACTION_STATIC_GATE` | IR、Harness、协议 → 接口、权限、角色、隔离、回滚和硬安全逐项状态；任一硬项非 `PASS` 不得冻结。 |
| `FREEZE_VALID_BELIEF_ACTIONS` | 全部硬项通过的 IR → 不可变 `Action[]` 与 child versions；字段变化创建新 ID。 |

| 规划执行算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `PLAN_EVALUATE_AND_EVOLVE` | planning belief、actions、select/anchor 池、暴露账本、round ledger → 控制信号、更新 belief 与累计账本；每次只执行一个真实动作。 |
| `BIND_EVIDENCE_ACTIONS_TO_DATA_ROLES` | 动作模板、select/anchor 池、暴露账本 → 绑定任务、保真度和角色的可执行动作；独立性不满足则拒绝绑定。 |
| `BUILD_BELIEF_TREE_CONTINGENCY_REQUEST` | planning belief、冻结动作、round ledger 与 planning horizon → 只披露已提交 belief、动作 schema、已知结果结构和历史可见事件的多步情景视图；隐藏状态标签和测试信息不可见。 |
| `PARSE_BELIEF_TREE_CONTINGENCY_PROPOSAL` | contingency 调用 → action paths、分支条件、可观测结果、状态转移假设、观测别名、终局影响和 unknown 分支草案；概率、VOI 与动作排序字段一律丢弃。 |
| `VERIFY_AND_BOUND_TREE_CONTINGENCIES` | 情景草案、belief、冻结动作、round ledger、`PlannerModelRevision` → `VerifiedContingencySet`；逐路径检查动作可达性、时间顺序、观察 schema、状态 effect、权限与数据角色，并由程序拟合概率或给出保守界。任何未建模质量保留在 `unknown_branches`。 |
| `ROOT_SAMPLE_BELIEF_TREE` | belief、actions、`VerifiedContingencySet`、规划 horizon → 带 unknown 的 root-sampled tree；只从程序界定的分布采样，LLM 提案仅扩充结构支持集。 |
| `ESTIMATE_TERMINAL_DECISION_VALUE` | tree → 每个根动作的价值分布和误差。 |
| `NO_DECISION_RELEVANT_ACTION` | 根动作价值、模型误差与 hard obligations → bool；无可评估动作但仍有硬缺口时为真，不能伪造 stop。 |
| `BUILD_PLANNING_STALL_REQUEST` | planning belief、动作、价值、round ledger → 停滞原因和允许动作 schema 的最小视图。 |
| `PARSE_PLANNING_STALL_REFLECTION` | stall 调用 → evidence/computation 模板、缺失 trace 字段或合法前序返回草案；收敛声明无效。 |
| `VERIFY_AND_COMPILE_STALL_RESPONSE` | stall 草案、belief、账本 → 经过共同 `BeliefActionIR` schema、结果模型界定和全部 hard gate 的动作 additions 与/或合法返回；select 已披露时禁止返回生成。 |
| `ARGMAX_NET_VALUE` | values → 按净价值及固定 tie-break 的唯一动作。 |
| `STOP_CERTIFICATE_HOLDS` | belief、values、阈值 → bool 与逐项证据。 |
| `DEFER_INVALID_STOP` | 动作集、belief → 暂时移除无证书 stop 的动作集；生成缺失证书对应的取证动作，不能执行伪 stop。 |
| `DEPLOY_OR_UNRESOLVED` | belief、证书 → `PROMOTE/RETIRE/UNRESOLVED`。 |
| `EXECUTE_ONE_REAL_ACTION` | 冻结 action、隔离环境 → 原始 result；故障同样返回事件。 |
| `BUILD_BELIEF_EVENT_INTERPRETATION_REQUEST` | action、原始 result、planning belief → 固定观察与声明结果类别的解释视图；不得改变原始指标。 |
| `PARSE_BELIEF_EVENT_INTERPRETATION` | event-interpretation 调用 → 潜变量观察、结果类别、替代解释和缺失测量草案。 |
| `VERIFY_EVENT_METRIC_CODE_ROLE_ANCHORS` | 解释草案、action、result、belief → 经核验 observation map；未锚定字段不进入后验。 |
| `APPEND_IMMUTABLE_EVIDENCE` | round ledger、action、原始 result、经核验 observation map → 新 ledger revision 与带选择元数据的 `Evidence`；旧 ledger 不覆盖。 |
| `VERSIONED_UPDATE_AND_CALIBRATE` | belief、event → 后验、评测器和残差 revision。 |
| `KEEP_DISCOUNT_OR_SPLIT_REGIME` | 新旧预测残差、变化证据、经核验 regime hypothesis 或 `NONE` → `KEEP/DISCOUNT/SPLIT`；状态由冻结变点与独立失配规则决定。 |
| `ROUTE_AFTER_BELIEF_UPDATE` | 最新 event、planning belief、round ledger → `STAY/RETURN_RETRIEVE/RETURN_REGENERATE`；select 已披露时只允许 `STAY`。 |
| `REFRESH_NON_GENERATIVE_ACTIONS` | planning belief、旧动作、round ledger → 新的取证、计算、提交、回退和停止动作；不得生成新 child。 |
| `CURRENT_HARNESS` | belief → 当前已提交 Harness；未提交候选不可返回。 |

| 长期沉淀算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `CONSOLIDATE_AND_TRANSFER_BELIEFS` | 长期状态、完整 round ledger、下一 regime、调用账本 → `COMMITTED` 的新状态/next belief 或 `PENDING_REVIEW`。 |
| `COPY_ON_WRITE_BELIEF_STATE` | 已提交长期状态 → 隔离影子状态；不复制或修改只读目录。 |
| `APPEND_WITH_SELECTION_METADATA` | ledger、事件、候选集/propensity → 新不可变 ledger revision。 |
| `UPDATE_PROPER_SCORE_COVERAGE_AND_MISSPECIFICATION` | 预测与结果 → proper score、coverage、misspecification debt。 |
| `BUILD_CALIBRATION_FAILURE_REQUEST` | 重算后的校准/残差/哨兵状态 → 失配诊断视图。 |
| `PARSE_CALIBRATION_FAILURE_DIAGNOSIS` | calibration 调用 → 失败 strata、候选机制、required checks 与观察草案。 |
| `VERIFY_CALIBRATION_DIAGNOSIS` | 诊断草案、影子状态 → 经指标和 evidence 锚定的校准缺口；未核验原因保持 unknown。 |
| `BUILD_REGIME_CHANGE_REQUEST` | 状态、校准缺口、预测下一 regime → 候选变化字段和断点视图。 |
| `PARSE_REGIME_CHANGE_HYPOTHESIS` | regime 调用 → changed fields、断点、受影响 likelihood 与替代解释草案。 |
| `VERIFY_REGIME_CHANGE_ANCHORS` | regime 草案、状态 → 经环境版本、变点统计与独立信号锚定的假设。 |
| `UPDATE_ANYTIME_VALID_DECISION_PROCESSES` | 新事件、错误率账本 → 可持续查看的决策区间。 |
| `QUALIFIED_REGIME_EFFECTS` | ledger、regime 条件 → 通过激活、配对、校准要求的效应。 |
| `BUILD_TRANSFER_STRUCTURE_REQUEST` | qualified effects、状态、目标 regime → 共享结构与负迁移边界视图。 |
| `PARSE_TRANSFER_STRUCTURE_PROPOSAL` | transfer 调用 → scope、dependency group、冲突和来源分量草案。 |
| `VERIFY_TRANSFER_STRUCTURE` | transfer 草案、qualified effects、状态 → 经独立确认、作用域、依赖和负迁移核验的结构。 |
| `UPDATE_WITH_COLD_FLOOR` | qualified effects、shadow models、经核验 transfer structure → 满足 $\pi_{cold}\ge\pi_{min}$ 的先验；数值权重由程序更新。 |
| `LEAVE_ONE_TASK_AND_REGIME_OUT_AUDIT` | 状态 → 留一预测与失败报告；失败时收紧 scope。 |
| `RECOMPUTABLE_TARGET_BELIEF` | 状态、目标任务 → 可由指定 revisions 重算的 posterior。 |
| `ATOMIC_COMMIT_BELIEF_REVISION` | 旧状态、影子状态、round ledger → 新长期 revision；来源、选择元数据、校准与审计任一失败时保持旧状态。 |
| `CURRENT_LLM_CALL_LEDGER_REVISION` | 调用账本 → 已完整落盘的当前 revision；有 pending 调用时拒绝长期提交。 |

| 外层训练与封闭测试算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `EVOLVE_DECISION_THEORETICALLY` | $H_0$、来源、训练集、测试集、协议 → 固定点后的冻结状态与最终结果；测试集只传给最终算子。 |
| `INIT_LLM_CALL_LEDGER` | optimizer config revision → 空实验级 `LLMCallLedger`；schema 或存储不可用时不得启动。 |
| `INIT_TRAIN_SCHEDULER` | $D_{\mathrm{train}}$、协议 → `SchedulerState`；无法满足分层与隔离时返回配置错误。 |
| `INIT_BELIEF_LONG_TERM_STATE` | $K_0$、协议 → 不含目标 benchmark 运行证据的 $M_0$；外部报告不写成本地似然。 |
| `ASSIGN_TRAIN_ROLES` | scheduler、长期状态、$g$ → 三个两两不相交任务集合；不足时不借用测试集。 |
| `RUN_HARNESS` | 冻结 Harness、任务、执行配置 → 每次运行一条 `ExecutionTrace`；失败、超时和异常不得丢弃。 |
| `INIT_ROUND_LEDGER` | $g$、父 Harness、trace batch、调用/暴露账本 → 含 trace evidence、已有诊断调用和初始暴露的 `RoundLedger`；一代只初始化一次。 |
| `BUILD_GENERATION_BELIEF_VIEW` | $M_g$、父 Harness、trace batch → 权限受限的生成信念；明确排除本代 select/anchor 与测试证据。 |
| `NO_SELECT_RESULT_DISCLOSED` | round ledger、暴露账本 → bool；任一 select 内容或派生结论进入生成路径即为假。 |
| `UPDATE_EXPOSURE_FROM_LLM_CALLS` | scheduler、调用账本、受影响对象、任务集合 → 对象级披露和独立性 revision；影响对象及后代后永久 `EXPOSED`。 |
| `REFRESH_INDEPENDENT_PLANNING_POOLS` | scheduler、动作、select/anchor 池 → 满足对象级独立性的替换池；无可用任务时结束同代返回。 |
| `REFRESH_GENERATION_VIEW_FROM_DISCOVERY` | 旧生成视图、round ledger → 仅吸收合格 discovery 事件的新视图；select/anchor 事件始终排除。 |
| `APPLY_TERMINAL_CONTROL` | 父 Harness、`PROMOTE/RETIRE/UNRESOLVED`、planning belief → $H^{[g+1]}$ 候选值；仅 PROMOTE 原子选择唯一 child。 |
| `PREDICT_NEXT_REGIME` | scheduler、本代账本、下一 Harness → 下一代待校验 regime 描述；预测不视为已确认事实。 |
| `BELIEF_REVISIONS_CREATED` | 提交前后长期状态、round ledger → 本代已原子提交的 belief/regime/transfer revision IDs；pending 对象不返回。 |
| `UPDATE_TRAIN_SCHEDULER` | scheduler、三类任务、round ledger → 新暴露、coverage、未决信念和 anchor 状态；历史只追加。 |
| `TRAIN_FIXED_POINT` | 当前/下一 Harness、长期状态、scheduler、stop rule → bool；`UNKNOWN`、pending 和资源耗尽均为假。 |
| `FREEZE_FOR_FINAL_TEST` | 最终 Harness、长期状态、$K_0$、协议 → `FrozenTestPackage`；任一对象变化都创建新实验。 |
| `RUN_FINAL_TEST_ONCE` | 冻结测试包、$D_{\mathrm{test}}$ → 最终指标与只读 trace；不调用 `OptimizerLLM`，不更新训练状态。 |
| `INVALIDATE_CHILD_BELIEFS_ACTIONS_AND_INTERVALS` | 新父 Harness、长期状态 → 标为 stale 的旧 child belief、动作价值和确认区间；原始事件保留。 |

#### 伪代码局部变量

| 变量 | 唯一含义 |
| --- | --- |
| `llm_call_ledger` | 实验级只追加调用账本，包含离线和在线全部成功、失败、重试与拒绝调用。 |
| `source_units/compilation_requests/compilation_calls/compilation_proposals` | 固定来源单元、来源编译输入、调用记录与解析提案，通过 call ID 连接。 |
| `verified_fields/fragments/source_graph` | 经来源/代码逐字段核验的语义字段、决策模型片段和只含来源事实的影响图。 |
| `need_request/need_call/need_proposal/need` | trace-belief 诊断视图、调用、解析草案和经锚点核验的 `DecisionNeed`。 |
| `graph/seeds/bundles/calibrations` | 在线物化影响图、字段初召回、依赖闭包方法束和仍需本地校准的边。 |
| `rerank_request/rerank_call/rerank_proposal` | 对硬过滤 bundle 的语义重排视图、调用和经解析提案。 |
| `method_request/method_call/method_ir` | 方法引导演化输入、调用和共同 `BeliefActionIR`。 |
| `uncovered_unknown_regions` | 没有可执行知识 IR 覆盖且会影响终局决策的 unknown/high-loss 后验区域。 |
| `free_request/free_call/free_ir` | 与本轮知识 patch 隔离的自由扩展输入、调用和共同 IR。 |
| `evidence_request/evidence_call/evidence_ir` | 判别性取证设计视图、调用和 evidence-action 模板 IR。 |
| `computation_request/computation_call/computation_ir` | estimator computation 设计视图、调用和 computation-action IR。 |
| `outcome_request/outcome_call/outcome_models` | action 结果结构视图、调用和不含可直接采用本地概率的结果模型草案。 |
| `action_ir/actions` | 经结果模型拟合/界定与公共 hard gate 的 IR，以及最终冻结动作集合。 |
| `planning_belief/generation_belief` | 可读取本代确认结果的规划视图与禁止读取这些结果的生成视图。 |
| `contingency_request/contingency_call/contingency_proposal` | 多步规划情景视图、调用和不含可采用概率的语义分支草案。 |
| `verified_contingencies` | 经动作、观察、状态、权限、时间和数据角色核验，并由程序界定概率的 `VerifiedContingencySet`。 |
| `tree/values/action/result/event` | 使用 `verified_contingencies` 构造的 root-sampling 树、根动作价值分布、唯一真实动作、原始结果和规范化 `Evidence`。 |
| `stall_request/stall_call/stall_proposal` | 无决策相关动作时的停滞视图、调用和 evidence/computation/返回草案。 |
| `additions/return_request` | 经权限、披露和可执行性核验后可加入的动作及合法前序返回。 |
| `interpretation_request/interpretation_call/interpretation` | 对固定 action result 的事件解释视图、调用和潜变量观察草案。 |
| `verified_observation_map` | 经 trace、指标、代码、角色和 action revision 核验后允许进入 belief updater 的观察映射。 |
| `route/control` | 阶段内返回方向与代际末 `PROMOTE/RETIRE/UNRESOLVED` 控制信号。 |
| `shadow/qualified` | 写时复制长期状态与满足 regime、激活、配对和校准要求的效应集合。 |
| `calibration_request/call/proposal/verified_calibration_gaps` | 失配诊断视图、调用、草案和经指标/evidence 核验的缺口。 |
| `regime_request/call/proposal/verified_regime_hypotheses` | regime 变化视图、调用、草案和经环境/变点/独立信号核验的假设。 |
| `transfer_request/call/proposal/verified_transfer_structure` | 跨任务共享结构视图、调用、草案和经作用域、依赖、确认及负迁移核验的结构。 |
| `commit_result` | `ATOMIC_COMMIT_BELIEF_REVISION` 的事务结果，包含 `COMMITTED/PENDING_REVIEW`、新状态或恢复记录。 |
| `consolidation` | 阶段四原子提交结果，状态为 `COMMITTED` 或 `PENDING_REVIEW`。 |
| `catalog/long_state` | 冻结 $K_0$ 与当前已提交 $M_g$。 |
| `scheduler` | 训练分层、角色暴露、coverage、未决 need 和 anchors 的调度状态。 |
| `trace_pool/select_pool/anchor_pool` | 第 $g$ 代三类训练任务集合。 |
| `trace_batch` | $H^{[g]}$ 在 trace pool 上产生的完整 `ExecutionTrace[]`。 |
| `round_ledger` | 本代 trace、真实动作、证据、披露和控制信号的累计事务账本。 |
| `H/H_next` | 当前父 Harness 与按代际转移规则得到的下一父版本。 |
| `next_regime/next_belief` | 根据本代变化提出、并在下一代 trace 上重新校验的 regime 与先验 belief。 |
| `frozen` | stop 后包含 Harness、目录、长期 revision 与完整评测协议的只读测试包。 |

兼容记号固定如下：`FailureCause × MethodTransfer` 是两个潜变量的联合状态；$P(\text{result}\mid\text{belief},\text{action})$ 是当前 `PlannerModelRevision` 产生的动作结果分布；`H_child` 是冻结父版本应用一个候选差分后的新子版本；`VOC` 是 computation action 的 value of computation，按 `DecisionVOI` 计算但只更新 `EstimatorState`；`PROMOTE / RETIRE / UNRESOLVED` 是本代终局控制，`CONTINUE` 只表示继续取证。`CAUSES / OBSERVES / REQUIRES / EXCLUDES / PERSISTS / CONFLICTS / SHARES_EVIDENCE_WITH` 是七种 edge type 的并列写法。

### 不变量

1. 原始证据账本不可覆盖；belief 必须能从指定 revisions 重算。
2. 计算动作只改变估计器状态，不能伪装成环境证据。
3. 低保真结果未校准时只能排序取证，不能直接晋级或淘汰。
4. 共享来源依赖的证据不得按独立样本重复累计。
5. 任何动作选择都记录当时完整候选集，避免幸存者偏差。
6. 测试集不进入 belief 更新、校准器、动作价值或停止证书。
7. 外部来源组织只在 loop 外执行；在线 belief revision 不得改写 $K_0$ 的来源图与索引。
8. 本代候选生成只读取 `GenerationBeliefView`；select/anchor 结果只能进入 `PlanningBeliefView` 和长期账本。
9. 每代结束后，无论 Harness 是否晋级，都更新暴露账本并重新运行下一代 trace；旧 child 后验、动作价值与确认区间不得跨父版本直接继承。
10. 局部停止证书只终止本代规划；只有 `TRAIN_FIXED_POINT` 才能进入封存测试。
11. stop 后测试执行只读，测试结果不得反馈到 belief、校准器、目录、效用函数或 Harness。
12. 每次 `OptimizerLLM` 调用都先通过最小权限和禁止对象检查；任何派生 fragment、need、action、event interpretation 或 transfer revision 可见前必须完成固定 schema 解析与对应 validator。
13. `OptimizerLLM` 不得直接设置 posterior weight、本地 likelihood、动作概率、VOI、risk、置信边界、迁移权重或 stop 结果；这些数值只由冻结模型、真实 evidence 与程序计算。
14. 模型提出的结果类别和因果解释必须保留 `unknown_model` 与替代解释；无锚点字段不得通过重归一化进入已知状态。
15. 任一任务字段一旦通过调用、程序视图或派生对象影响候选、动作或 belief revision，该任务对该对象及后代永久失去独立性。
16. 所有模型产生对象必须回指完整 `LLMCallRecord` 与 `ValidationRecord`；调用失败、解析失败和被拒提案同样保留在只追加账本中。
17. `BELIEF_TREE_CONTINGENCY_PROPOSAL` 只能扩充规划树的结构支持集；路径概率、净价值、动作选择和停止结论必须由 `PlannerModelRevision`、真实 evidence 与冻结规则计算。
