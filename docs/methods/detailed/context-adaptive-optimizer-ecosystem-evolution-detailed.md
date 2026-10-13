# 情境自适应的优化生态演化：完整详细版

## 一、完整 Method

现有 Harness 优化常采用单一优化器或固定流程，默认同一套分析、生成和修复策略能够覆盖所有任务与演化阶段。但不同任务对工具、记忆、上下文和容错的需求不同，同一任务在“发现缺失机制”“修复接入错误”和“降低成本”等阶段也需要不同能力。即使已经收集多个方法或优化策略，如果只按主题相似度选择，或只按最终分数给整条链路记功，系统仍然无法回答：哪种策略在当前情境下适用、多个策略应如何互补、失败究竟发生在生成、接入、激活还是效果层。

为解决这一问题，本路线把优化过程建模为一个能够随任务情境自适应重组的优化生态。外部论文与历史演化被整理为带前提、干预、适配过程、结果分布和失败边界的条件案例；不同优化方式被表示为具有能力边界、资源需求和组合接口的优化器程序。系统不追求一个全局最优优化器，而是根据当前 Harness、失败区域和证据缺口选择互补成员，形成一次面向当前情境的策略组合。

具体而言，loop 外先冻结条件案例目录和优化器契约。每一轮由父 Harness 的训练 trace 形成 `CaseNeed`，`OptimizerLLM` 诊断多个竞争性需求，解释候选案例的迁移条件，并设计知识引导与自由探索的优化器程序；`OptimizerHarness` 负责硬前提过滤、组合合法性检查、候选去重和统一执行。所有策略共享候选身份和评测账本，运行证据分别更新案例迁移边界、各优化器在不同情境下的能力画像，以及生成、接入、激活和最终效果各层的信用，从而形成“情境识别—生态组队—协同生成—共享测评—分层归因—生态更新”的闭环。

案例准备与 benchmark 演化分属两个时间范围。实验开始前冻结来源、案例目录、优化器接口、benchmark、执行环境、评测器、随机种子、晋级规则和停止规则；在线阶段只允许训练集证据推动 H₀ → H₁ → H₂ → … 并更新当前实验的长期状态。新论文和案例目录修订不能在同一次演化中途加入，封存测试集只用于最终版本的正式测评。

### 案例组织与检索阶段：如何组织和检索外部方法

方法能否迁移取决于干预发生时的完整条件，而不只是任务描述是否相似。两个任务可能共享领域词汇，却使用不同模型、工具权限、上下文压力和 Harness 生命周期；反过来，表面不同的任务也可能具有相同失败机制。若检索只返回“最相似的成功案例”，模型容易照搬在来源环境成立、在目标环境失效的做法，并且看不到曾经失败的边界。

本阶段把外部论文方法和历史实验统一编译为条件化干预案例。每个案例同时记录干预前状态、具体修改、预期机制、中介事件、结果分布、环境条件以及负面或不确定证据。相似性只承担初始召回，真正的迁移判断通过条件差异、机制不变量和可适配字段完成；成功案例、失败边界和拒绝路线一同返回，使后续优化器知道哪些内容可以复用、哪些必须重新验证。

本阶段包含时间位置不同的两个动作。**离线组织**发生在 benchmark 演化 loop 之前：从固定外部来源恢复条件化干预案例、行为 probe schema、迁移边界与多视图索引，并冻结为目录快照。**在线检索**发生在每一轮 loop 内：从 $H_t$ 在 $D_t^{\mathrm{trace}}$ 上的真实响应构造 `CaseNeed`，联合查询固定目录与 `LongTermState` 中当前 regime 可见的案例 revision，估计来源到目标的 transport map，并区分可直接迁移、需要适配、需要目标证据和应拒绝四类。随后形成 `CaseProposal`，明确要复用的干预、需要修改的条件、校准证据和停止条件；本阶段不改动 Harness。

离线组织中的实验单元拆分、论文步骤与代码修改对齐、机制/构造过程分离及未知条件识别需要语义判断。`OptimizerHarness` 先固定论文、代码、配置、测试和结果表锚点，再以 `SOURCE_CASE_SEMANTIC_EXTRACTION` 请求 `OptimizerLLM` 提出条件案例字段与逐字段依据；程序核验锚点、实验单元一致性、代码差分和结果归属。在线时，`TARGET_CASE_NEED_DIAGNOSIS` 让 `OptimizerLLM` 从父代成功/失败 trace、响应签名和历史边界提出竞争故障解释；硬召回和前提过滤由程序完成；`CASE_TRANSFER_AND_ADAPTATION_PROPOSAL` 只对过滤后的案例提出迁移解释、逐步骤适配计划、风险和反驳 probe。模型不能恢复被硬前提拒绝的案例，也不能把来源效果直接当作目标收益。

原始材料仍先保存为不可变来源包：

```text
SourcePacket = {
  source_packet_id,
  paper_version,
  official_code_version,
  exact_source_anchors,
  configs_and_examples,
  tests_and_reported_results
}
```

`SourcePacket` 只负责保存来源。全部外部来源在进入 benchmark loop 前编译为固定 `CaseCatalogSnapshot`；新增论文、改变官方代码 revision、probe schema 或案例编译规则都产生新的目录快照和实验条件，不能在线覆盖。第一轮 `CaseNeed` 来自 $H_0$ 的训练 trace 与行为 probe，后续轮次来自 $H_t$ 的新 trace、上一轮失败迁移条件、优化器覆盖缺口与 regime 证据。

一篇论文中的不同任务、模型、Harness、消融或配置分别形成案例：

```text
ConditionalInterventionCase = {
  case_id,
  source_context: {
    task_response_signature,
    harness_state,
    model_tool_environment,
    evaluation_protocol
  },
  diagnosed_need,
  method_intervention: {
    mechanism,
    required_capabilities,
    hard_preconditions,
    configurable_slots,
    known_interactions
  },
  construction_process,
  observations: {
    mechanism_activation,
    paired_effects,
    regressions,
    variance,
    measured_cost
  },
  failed_conditions,
  changed_environment_slots,
  evidence_regime,
  source_anchors,
  unknown_fields,
  semantic_extraction_call_ids,
  field_validation_status
}
```

`method_intervention` 与 `construction_process` 必须分开：前者表示论文究竟加入了什么机制，后者表示作者怎样得到这份实现。论文没有报告优化过程时保存为 `UNKNOWN`，不能推断成某个优化器的成功案例。作者报告、本地复现和本项目演化也使用不同 `evidence_regime`。

任务不能只用自然语言主题表示。系统使用固定版本的 $H_0$ 或诊断 probe 在小型任务面板上取得行为响应：失败族分布、工具序列、上下文压力、验证覆盖、恢复路径以及模块敏感性。由此形成 `task_response_signature`，作为当前 Harness 的经验行为表征。

**算法 1：条件干预案例编译。**

1. **固定来源单元。** `OptimizerHarness` 按论文段落、算法步骤、代码符号与差分、配置、测试和结果表建立不可变来源单元，先保留原始边界，不由模型改写来源事实。
2. **提出并核验条件案例字段。** `OptimizerLLM` 通过 `SOURCE_CASE_SEMANTIC_EXTRACTION` 提出实验单元划分、机制步骤、构造过程、环境条件、结果归属、可调槽和未知项，并逐字段引用来源锚点。程序按任务、数据划分、模型、Harness、工具环境、配置和评测协议核验；每个消融条件单独保存。
3. **对齐机制、实现与结果。** 将通过核验的论文步骤、代码修改、配置和结果表对应起来。若多项改动同时发生且没有消融，标记为组合干预，不向单个组件分配效果。
4. **计算行为签名。** 对可运行来源使用固定 probe；不能运行时只保存论文报告的特征，并把运行签名标为缺失。
5. **提取适配模式。** 记录机制依赖的能力、必须保留的顺序、可替换接口、可调槽位和已知交互。该模式描述“怎样可能迁移”，不绑定当前 Harness。
6. **定位环境变化。** 比较论文实验环境和其他案例，将模型、工具、权限、反馈、数据分布、资源与 Harness 状态结构等差异保存为显式槽位。
7. **构造正例、反例与边界例。** 机制激活且有效形成正例；明确退化形成反例；仅改变少量条件便使结果翻转的案例形成边界对。未报告项保持 `UNKNOWN`。
8. **建立多视图索引。** 分别索引行为签名、需求与机制、前置条件、环境槽位、适配操作、结果和反例，不能把全部字段拼成一个文本向量。

当前任务的查询为：

```text
CaseNeed = {
  need_id,
  target_response_signature,
  current_harness_state,
  model_tool_environment,
  diagnosed_need,
  immutable_constraints,
  observable_target_evidence,
  unknown_conditions,
  source_call_id
}
```

**算法 2：可适配性优先的条件案例检索。**

1. 使用相同 probe 构造目标响应签名；`OptimizerLLM` 通过 `TARGET_CASE_NEED_DIAGNOSIS` 提出多个竞争故障解释、最早行为偏离、目标能力与判别观察，`OptimizerHarness` 只接受能回指 trace、响应特征和父代代码的字段。
2. 以非对称距离做高召回粗检索。来源案例在更多任务上验证过可以提高其 `generality`，但不能因结构复杂便自动获得通用性。
3. 对每个粗召回案例执行硬覆盖检查：若目标的必要需求没有被案例机制覆盖、硬前置条件明确冲突或所需权限不可获得，则直接排除；未知条件进入待核验集合。
4. 对剩余案例发起 `CASE_TRANSFER_AND_ADAPTATION_PROPOSAL`。`OptimizerLLM` 逐步骤提出保留、参数化、替换、删除或补前提操作，说明迁移机制、交互风险、相反证据、所需目标 probe 与停止条件；程序核验来源步骤、目标代码锚点、动作合法性和权限边界，形成 `AdaptPlan`。
5. 构造经验变化图，标记来源与目标间可能变化的环境槽位。候选被划分为：
   - `DIRECT`：声明的有效路径不经过未核验变化槽位；
   - `CALIBRATE`：受变化槽位影响，但能通过目标 probe 重新估计；
   - `REJECT`：依赖不可观测、明确冲突或已有反例的变化机制。
6. 对 `DIRECT/CALIBRATE` 案例运行少量目标 probe。在确有标签或可验证结果时，可用 LEEP 式条件映射估计轻量迁移分数；没有目标监督证据时保持高不确定性，不虚构分数。
7. 以适配后价值而非文本相似度排序：

   $$
   S(c,q)=w_rR_{response}+w_pE_{probe}+w_gG_{generality}
   -w_aC_{adapt}-w_iR_{interaction}-w_uU_{transfer}.
   $$

   硬约束与 `REJECT` 优先于连续分数。
8. 返回若干机制不同的 `CaseProposal`，同时包含最相近成功案例、失败边界与被拒绝路线。案例组织与检索阶段不直接修改当前 Harness。

```text
CaseProposal = {
  proposal_id,
  need_id,
  retrieved_case,
  adaptation_plan,
  transfer_decision,
  required_target_evidence,
  predicted_gain,
  predicted_adaptation_cost,
  interaction_risk,
  uncertainty,
  rejection_reason,
  llm_call_ids
}

OFFLINE_COMPILE_CASE_CATALOG(source_packets):
    source_units <- FIX_CASE_SOURCE_UNITS(source_packets)
    extraction_requests <- BUILD_SOURCE_CASE_EXTRACTION_REQUESTS(source_units)
    extraction_calls <- CALL_OPTIMIZER_LLM(
                            extraction_requests,
                            call_type=SOURCE_CASE_SEMANTIC_EXTRACTION)
    extraction_proposals <- PARSE_SOURCE_CASE_PROPOSALS(extraction_calls)
    verified_fields <- VERIFY_SOURCE_CASE_FIELDS(
                           extraction_proposals, source_units)
    cases <- SPLIT_ALIGN_AND_COMPILE_INTERVENTION_CASES(
                 source_packets, verified_fields)
    cases <- ADD_FIXED_PROBE_SIGNATURES_AND_CHANGE_SLOTS(cases)
    indexes <- BUILD_CASE_MULTIVIEW_INDEXES(cases)
    return FREEZE_CASE_CATALOG(source_packets, cases, indexes)

BUILD_CASE_NEED(parent, trace_batch, state, train_protocol):
    need_view <- BUILD_TARGET_CASE_NEED_VIEW(
                     parent, trace_batch,
                     VISIBLE_CASE_BOUNDARIES(state), train_protocol)
    need_call <- CALL_OPTIMIZER_LLM(
                     need_view, call_type=TARGET_CASE_NEED_DIAGNOSIS)
    need_proposal <- PARSE_TARGET_CASE_NEED_PROPOSAL(need_call)
    return VERIFY_CASE_NEED_TRACE_CODE_AND_REGIME_ANCHORS(
               need_proposal, need_view)

ONLINE_RETRIEVE_CONDITIONAL_CASES(catalog_snapshot, case_view, need):
    indexes <- MERGE_CASE_RETRIEVAL_VIEWS(
                   catalog_snapshot.indexes, case_view)
    recalled <- ASYMMETRIC_RESPONSE_RECALL(indexes, need)
    eligible <- HARD_COVERAGE_AND_PRECONDITION_FILTER(recalled, need)
    adaptation_request <- BUILD_CASE_TRANSFER_ADAPTATION_REQUEST(
                              eligible, need)
    adaptation_call <- CALL_OPTIMIZER_LLM(
                           adaptation_request,
                           call_type=CASE_TRANSFER_AND_ADAPTATION_PROPOSAL)
    adaptation_proposals <- PARSE_CASE_TRANSFER_ADAPTATION_PROPOSALS(
                                adaptation_call)
    plans <- VERIFY_AND_COMPILE_ADAPTATION_PLANS(
                 adaptation_proposals, eligible, need)
    licensed <- EMPIRICAL_TRANSFER_GATE(plans, need)
    calibrated <- TARGET_PROBE_CALIBRATION(licensed, need)
    return ADAPTATION_VALUE_RERANK(calibrated, need)
```


### 优化器程序生成阶段：如何结合 trace、知识与自主探索生成候选

案例只描述在某些条件下何种干预曾经有效，并不规定面对当前 trace 时应先诊断、接入还是探索。单个固定策略容易把所有失败压缩成同一种修改风格；彼此无契约的多次模型调用又会产生重复候选、相互冲突的 patch 和无法归因的结果。需要被组合的是具有明确输入、输出、触发条件和边际作用的调用策略。

本阶段将每个优化器表示为从演化上下文到候选分布的受约束程序。诊断器、知识适配器、局部修复器、自由探索器和批评器可以形成条件分支与串行依赖；选择器决定哪些策略在当前状态下启动，生成器提出候选，接受器执行契约和安全过滤。程序化组合保留了多策略的互补性，同时让每个中间产物和决策都可以记录、复现和分配信用。

实现时先从 trace、案例提案、父代代码和历史账户构成 `EvolutionContext`，预测各优化器在当前条件下产生合法、激活且有效候选的概率。随后以边际覆盖为目标挑选优化器组合，按依赖关系执行并对语义等价 patch 去重；自由探索获得独立的最低概率，不会因知识库偏好而消失。所有候选在冻结前记录生成路径、共享祖先、预期机制和所需评测，为后续竞赛提供清晰的信用图。

组合中的 optimizer revision 不是独立 agent，而是 `OptimizerHarness` 内的一份调用策略：它规定 call type、输入视图、提示模板、工具权限、私有状态、编辑范围、输出 schema 与 fallback。`PORTFOLIO_PROGRAM_DESIGN` 让 `OptimizerLLM` 提出哪些策略应串联、它们交换什么中间产物以及哪些证据触发转移，程序只从契约兼容且满足边际覆盖约束的边中构造无环程序。执行程序时，案例适配、外部方法组合和自由探索分别发起 `CASE_GUIDED_CANDIDATE_PROPOSAL`、`METHOD_GUIDED_CANDIDATE_PROPOSAL` 与 `FREE_CANDIDATE_PROPOSAL`；批评节点通过 `CANDIDATE_CRITIQUE_AND_REVISION` 指出接入错误、遗漏条件或最小修订。所有输出先解析为共同候选 IR，再由程序执行静态 gate 和精确去重。若所有路径最终为空，`EMPTY_PORTFOLIO_DIAGNOSIS` 负责跨路径解释空集形成机制，程序只核验事件并把合格解释编译为可路由缺口，避免用固定错误码代替对组合失败的语义判断。

**trace 的来源。** 第 $t$ 轮固定 $H_t$、模型与采样配置、工具与容器、评测器和种子后，在 $D_t^{\mathrm{trace}}$ 上实际运行。第一轮运行 $H_0$，后续运行上一轮确定的 $H_t$。每次执行生成：

```text
ExecutionTrace = {
  run_id,
  task_id,
  split_role,
  harness_version,
  model_tool_environment_versions,
  seed,
  ordered_events,
  optimizer_visible_context,
  final_output,
  metric_vector,
  failure_signature,
  replay_artifacts
}
```

`ordered_events` 记录模型调用及可见上下文、工具调用与结果、状态和记忆读写、控制流、重试、fallback、异常和终止；`optimizer_visible_context` 明确候选冻结前由 `OptimizerHarness` 向 `OptimizerLLM` 披露的事件与字段。成功与失败 trace 必须来自同一协议，前者用于构造对照响应，后者用于形成失败切片。只有最终得分而没有事件链的运行，不能用于 `task_response_signature`、失败定位或策略条件信用。候选生成只能读取 $D_t^{\mathrm{trace}}$，不能读取测试集或本轮 $D_t^{\mathrm{select}}$ 的运行。

每个优化器必须注册统一契约：

```text
OptimizerContract = {
  optimizer_id,
  optimizer_type: STATELESS_ADVISER | STATEFUL_OPTIMIZER,
  llm_call_policy,
  applicability,
  observation_requirements,
  private_state_schema,
  action_space,
  editable_scope,
  method_forms_supported,
  proposal_distribution_interface,
  expected_trace_effects,
  deterministic_validator,
  fallback,
  provenance,
  design_call_ids
}
```

策略 revision 可以实现知识案例适配、方法组件组合、反例修复、局部 patch、拓扑编辑、参数配置或自由代码探索。名称不是身份；只有契约、模型调用配置、内部状态和行动空间相同的实现才视为同一 revision。

当前演化上下文为：

```text
EvolutionContext = {
  frozen_parent_harness,
  task_and_environment,
  trace_batch,
  case_need,
  diagnosed_failure_slices,
  retrieved_case_proposals,
  retrieved_external_methods,
  attempted_edits,
  preservation_requirements,
  optimizer_history,
  regime_id
}
```

**输入。** 冻结父代 $H_t$、由 $D_t^{\mathrm{trace}}$ 产生的 `ExecutionTrace[]`、当前 `CaseNeed` 与 `CaseProposal[]`、允许披露的外部方法、已尝试修改、保护约束、分 regime 优化器账户及注册表。

**输出。** 冻结且去重的 `CandidateVersion[]`、本轮 `OptimizerProgram` 和完整 `GenerationLedger`。若所有优化器均被硬前提拒绝或只能产生无效候选，`EMPTY_PORTFOLIO_DIAGNOSIS` 先让 `OptimizerLLM` 综合各路径的中间产物、等待原因、拒绝报告和重复修改，区分案例覆盖不足、策略契约不匹配、迁移或接入失败、缺少观察、输出 schema 失败与真正无合法路线；`OptimizerHarness` 核验这些解释对应的路径和 gate 事件后，才输出显式 `PortfolioCoverageGap`。该对象供竞赛阶段返回案例检索或长期阶段生成 specialist，不能把空候选解释为父代最优。

优化器程序不是固定角色列表，而是带触发条件的有向图：

```text
OptimizerProgram = {
  program_revision,
  entry_optimizers,
  transition_edges: (optimizer_i, evidence_condition,
                     routing_probability, optimizer_j),
  backup_edges,
  disclosure_policy,
  re_gate_triggers,
  stop_conditions,
  design_call_id
}
```

**算法 3：trace 条件化的互补优化器程序与共享候选生成。**

1. **重建当前状态。** 将成功/失败 trace 对齐到父 Harness 的代码位置、状态变化与能力结果，得到失败切片、未知机制和已尝试修改。只把 trace 支持的字段写入上下文。
2. **激活安全优化器。** 根据契约的输入需求、可编辑范围、权限和硬约束过滤优化器；缺少证据但可补足的优化器进入等待集，不等同于不适用。
3. **预测条件增量。** 使用案例组织与检索阶段的案例与本地历史，估计优化器在当前状态下产生“可执行、机制激活、有效且不回归”候选的分层分布，而不是预测一个混合总分。
4. **按残差构造互补集合。** 设当前优化器程序集为 $P$，按尚未解决的任务残差计算新优化器的价值：

   $$
   J(o;P)=\sum_x w_x\max(0,V(P\oplus o,x)-V(P,x))
   -\lambda C(o)-\rho R(o).
   $$

   $x$ 是当前组合仍失败或高不确定的案例区域。新成员必须补足残差，不能只重复当前组合已解决的案例。
5. **提出并核验程序结构。** `OptimizerLLM` 通过 `PORTFOLIO_PROGRAM_DESIGN` 提出入口策略、串行依赖、竞争分支、预期中间产物和转移判据；程序核验策略契约、输入输出 schema、披露权限和无环性，并只保留能增加残差覆盖的边。除一阶适配 $o_j\mid x$ 外，同时使用历史中的 $o_j\mid o_i,x$，但历史信用不能绕过契约检查。
6. **执行三条候选通道。** 案例策略通过 `CASE_GUIDED_CANDIDATE_PROPOSAL` 读取 `CaseProposal`；方法策略通过 `METHOD_GUIDED_CANDIDATE_PROPOSAL` 读取允许披露的外部机制；自由策略通过 `FREE_CANDIDATE_PROPOSAL` 只读取父代、trace、硬约束和未解决需求，不读取本轮具体案例解法。三类输出使用相同 Candidate IR。
7. **批评并产生新 revision。** 若程序包含批评节点，`CANDIDATE_CRITIQUE_AND_REVISION` 必须指出候选的具体代码/trace 锚点、失败层级、保持不变部分、最小修订与预期观察。程序核验后才能产生新 IR revision；批评文本不能原地修改候选。
8. **记录提案分布。** 每个策略路径返回 top-$k$ 候选及其内部相对概率、预期机制和未决条件；无法提供校准概率时明确标为 `UNAVAILABLE`，后续不得伪造 propensity 校正。
9. **规范化候选。** 将 patch、配置和方法组件引用编译为统一 `CandidateVersion`。只有代码编辑、配置、父代和前置条件完全相同的候选才能合并；结构近似的候选只能共享先验，不能共享实测 reward。
10. **合并来源而不复制收益。** 完全相同候选保存全部来源策略、LLM 调用和提案概率，但只进入一次评测队列。多编辑候选先按整体归因，组件信用等待消融或跨候选证据。
11. **执行共同静态检查并冻结。** 编译、接口、状态、权限、禁止访问封存测试、fallback 和修改范围检查通过后冻结版本。失败记录为具体生成或接入失败，不能直接判定论文方法无效。

```text
CandidateVersion = {
  candidate_id,
  ir_ids,
  parent_id,
  normalized_change,
  method_sources,
  source_optimizers,
  optimizer_path,
  proposal_probabilities,
  expected_trace_effects,
  unresolved_conditions,
  hard_gate_status,
  frozen_at,
  llm_call_ids
}

GENERATE_WITH_CONDITIONAL_OPTIMIZER_PROGRAM(context, registry):
    x <- TRACE_CONDITIONED_EVOLUTION_STATE(context)
    active, waiting, rejected <- CONTRACT_AND_SAFETY_FILTER(registry, x)
    outcome_models <- ESTIMATE_LAYERED_OPTIMIZER_OUTCOMES(active, x)
    program_request <- BUILD_PORTFOLIO_PROGRAM_REQUEST(
                           x, active, waiting, outcome_models,
                           transition_credit)
    program_call <- CALL_OPTIMIZER_LLM(
                        program_request,
                        call_type=PORTFOLIO_PROGRAM_DESIGN)
    program_proposal <- PARSE_PORTFOLIO_PROGRAM_PROPOSAL(program_call)
    program <- VERIFY_AND_BUILD_RESIDUAL_COMPLEMENTARY_PROGRAM(
                   active, outcome_models, transition_credit,
                   program_proposal)

    proposals <- empty
    for optimizer in EXECUTABLE_FRONTIER(program):
        view <- APPLY_DISCLOSURE_POLICY(optimizer, x)
        call_type <- CANDIDATE_CALL_TYPE(optimizer)
        proposal_call <- CALL_OPTIMIZER_LLM(view, call_type=call_type)
        path_proposals <- PARSE_CANDIDATE_PROPOSALS(
                              proposal_call, optimizer.output_schema)
        proposals <- proposals union path_proposals

        if program routes path_proposals to a critique optimizer:
            critique_view <- BUILD_CANDIDATE_CRITIQUE_VIEW(
                                 path_proposals, optimizer, x)
            critique_call <- CALL_OPTIMIZER_LLM(
                                 critique_view,
                                 call_type=CANDIDATE_CRITIQUE_AND_REVISION)
            revisions <- PARSE_AND_VERIFY_CANDIDATE_REVISIONS(
                             critique_call, path_proposals, x)
            proposals <- proposals union revisions

    candidates <- NORMALIZE_TO_SHARED_CANDIDATE_IR(proposals)
    candidates <- EXACT_DEDUP_AND_ATTACH_ALL_SOURCES(candidates)
    candidates <- COMMON_DETERMINISTIC_GATE(candidates)
    ledger <- GENERATION_LEDGER(proposals)
    if candidates is empty:
        gap_request <- BUILD_EMPTY_PORTFOLIO_DIAGNOSIS_REQUEST(
                           x, program, active, waiting, rejected, ledger)
        gap_call <- CALL_OPTIMIZER_LLM(
                        gap_request,
                        call_type=EMPTY_PORTFOLIO_DIAGNOSIS)
        gap_diagnosis <- PARSE_EMPTY_PORTFOLIO_DIAGNOSIS(gap_call)
        verified_gap_diagnosis <- VERIFY_EMPTY_PORTFOLIO_DIAGNOSIS(
                                      gap_diagnosis, x, program,
                                      active, waiting, rejected, ledger)
        gap <- BUILD_PORTFOLIO_COVERAGE_GAP(
                   x, active, waiting, rejected, ledger,
                   verified_gap_diagnosis)
        return empty, program, ledger, gap
    return FREEZE(candidates), program, ledger, NONE
```


### 竞赛与信用分配阶段：如何规划、测评并控制多轮 Harness 演化

最终分数同时混合了生成合法性、接入正确性、机制激活和任务收益。把同一个总分回传给整条优化器链，会奖励只参与了早期步骤但没有产生边际贡献的策略，也会把适配器错误归咎于外部方法。多个优化器还可能独立生成同一个 patch；若重复运行并分别记功，组合选择会被重复证据系统性扭曲。

这里把候选实体与优化器账户分开。语义等价的 patch 共享一个候选及其运行证据，生成路径则保留为有向信用图；合法性、接入、激活、收益和回归分别形成局部反馈，只传给真正控制相应决定的优化器。评测采用父子配对和可追加样本，在结果足以改变晋级或账户排序时停止继续投入，使资源集中到尚有决策价值的候选上。

算法先通过契约、安全和机制 probe 过滤候选，再根据不确定性、潜在收益和优化器覆盖分配开发任务。每次成对运行更新候选后验和各账户的条件信用，采用反事实边际贡献或责任权重处理协作链。控制器据此选择晋级、继续取证、退役或触发新的优化器组合，并完整记录选择概率与保真度，保证长期统计能够校正主动选择带来的偏差。

本阶段让 `OptimizerLLM` 解释“真实证据支持了哪一层”和“下一次动作应区分什么”，但不让模型决定晋级或直接写信用。`PORTFOLIO_EVIDENCE_ATTRIBUTION` 将静态 gate、机制事件、父子配对和回归证据解释为生成、接入、激活、效果或转移层的支持/反对/未知，并提出竞争解释；`NEXT_RACE_ACTION_PROPOSAL` 在程序列出的合法动作上提出排序或参数完整的新动作；没有动作却仍存在决策不确定性时，`PORTFOLIO_STALL_REFLECTION` 检查遗漏策略、错误迁移假设、缺失 probe 或 regime 失配。`OptimizerHarness` 核验所有 trace、候选、策略路径和账户锚点，执行真实评测，并只按冻结规则更新信用与作出决定。

本阶段区分机制取证与收益取证。绑定修复、激活 probe 和 trace mutant 可以使用 $D_t^{\mathrm{trace}}$ 或预先定义的合成 probe；候选相对父代的新收益只能来自候选冻结前不可见的 $D_t^{\mathrm{select}}$；旧能力回归只由 $D_t^{\mathrm{anchor}}$ 检查。候选与父代在相同 task、seed、模型、工具和环境下成对运行，所有执行都生成与上一阶段相同 schema 的 `ExecutionTrace` 并写入 `OptimizationRoundLedger`。同一运行不能同时作为生成当前候选的证据和该候选的独立收益证据。

轮内返回还有一个额外限制：`ReturnOptimizerGeneration` 与 `ReturnCaseRetrieval` 只能依据 `trace`、`synthetic-probe` 或 `anchor` 角色的证据触发，这些证据本来就不承担新收益估计。一旦任何 $D_t^{\mathrm{select}}$ 结果向控制器披露，当前轮次禁止再生成候选或修改案例需求；系统必须用现有冻结候选完成 `Promote/Reject/Tie`，将 select 证据提交到长期状态，再由下一轮重新分配 withheld 任务。这样，优化器能够在下一轮吸收新失败，却不能重复使用已经暴露的选择任务证明自己的修改有效。

**输入。** 父代 $H_t$、冻结候选、`OptimizerProgram`、`GenerationLedger`、$D_t^{\mathrm{trace}}$、$D_t^{\mathrm{select}}$、$D_t^{\mathrm{anchor}}$、当前 regime、优化器账户和此前本轮证据。

**输出。** `Promote / Reject / Tie / ReturnOptimizerGeneration / ReturnCaseRetrieval / Continue / Unresolved` 之一，以及更新后的账户、regime 与 `OptimizationRoundLedger`。两个 return 动作仍停留在第 $t$ 轮：前者重门控或改写优化器程序，后者修订 `CaseNeed` 后重新在线检索；只有前三种终止决定允许进入长期积累并结束本轮。外部执行中断或证据缺失返回 `Unresolved`，不能伪装成 `Tie`。

系统维护三个互不替代的状态：

```text
OptimizerAccount = {
  optimizer_revision,
  regime_id,
  registration_status,
  exposure_count,
  feedback_count,
  feedback_debt,
  proposal_history,
  generation_credit,
  activation_credit,
  effect_credit,
  transition_credit,
  credit_call_ids
}

CanonicalCandidate = {
  normalized_change,
  parent_id,
  source_optimizers,
  proposal_probabilities,
  evidence_ledger,
  status,
  llm_call_ids
}

EvidenceObservation = {
  candidate_id,
  parent_id,
  execution_trace_id,
  task_instance,
  split_role,
  seed_and_environment,
  fidelity,
  selection_probability,
  mechanism_events,
  outcomes,
  hard_failures,
  measured_cost
}
```

**算法 4：混合调度、配对竞赛与分层信用控制。**

1. **匹配证据 regime。** 根据任务族、父 Harness 主版本、模型、工具、评测协议和主要失败构成匹配 `regime_id`。旧 regime 只提供先验，不能直接共享统计量。
2. **形成混合调度分布。** 对近似无状态、每轮给出提案分布的 adviser，使用 EXP4 式专家聚合；对依赖私有历史成长的 stateful optimizer，维护最小曝光和反馈债务，避免早期暂时落后的优化器永久饿死。两类优化器最终在共享候选层合流。
3. **合并优化器路径的候选概率。** 对完全相同候选，若路径选择与提案概率可用，则其行为概率为：

   $$
   q(c\mid x)=\sum_{g\in\mathcal G(x)}p(g\mid x)\,\pi_g(c\mid x).
   $$

   $g$ 是实际可执行的优化器路径；长度为 1 的路径对应单个 adviser。一次候选执行可向所有给该候选分配概率质量的路径提供共享信息，但路径内部各优化器的局部信用还要依据中间产物和失败层级分配。概率缺失时只做保守的实际使用归因。
4. **执行硬门。** 编译、接口、权限、接入可达性、机制 probe 和关键旧能力 smoke test 依次运行。硬失败候选退出当前竞争，但保留 trace 和失败层级；其他候选与本轮父代不受影响。
5. **启动多路径配对竞赛。** 主 bracket 在少量覆盖主要失败簇的共同任务、seed、模型和环境上比较候选与父代；保守 bracket 让少量结构新颖或长程候选直接进入较高保真度，避免低保真排序错误造成永久淘汰。
6. **只追加决策相关证据。** 下一次评测必须至少完成一项：解除晋级不确定性、区分仍竞争的候选、填补能力覆盖缺口或检查 regime 漂移。任务数少本身不是目标，停止无信息运行才是目标。
7. **解释证据层级。** `OptimizerLLM` 通过 `PORTFOLIO_EVIDENCE_ATTRIBUTION` 提出每项观察应归入生成、接入、激活、效果还是转移信用，指出共享候选中各路径实际控制的中间产物及替代解释。程序只接受能回指真实事件、路径 propensity 和候选 revision 的归因，并依据确定性规则更新账户。
8. **在预定检查点进行 race。** 复用已有逐实例结果，报告配对效应、区间、硬失败率与能力回归。只有明确且实质更差的候选退出；不可区分时保留幸存集，不强制产生唯一赢家。F-Race/irace 的重复检验在这里仅作搜索控制，不能宣称整体显著性受控。
9. **分层回传信用。**
   - 候选层首先写入真实观测，不区分来源；
   - 优化器层只根据其实际提案概率和候选所处失败层更新；极端重要性权重需截断并报告有效样本量；
   - 方法适用性只在接入正确、机制已激活后更新；
   - 组件层只有在配对消融、单编辑变体或多候选重复证据下才更新；
   - 相邻优化器的转移信用只在其前后中间状态被记录时更新。
10. **选择下一动作。** 程序先枚举 `request-proposal / switch-optimizer / repair-binding / evaluate / add-discriminating-task / promote / retire / rollback / reopen-retrieval` 中的合法动作；`NEXT_RACE_ACTION_PROPOSAL` 可排序这些动作或补全一个合法动作的参数与预期观察。`OptimizerHarness` 选择最可能改变当前决定且满足数据角色的唯一动作。出现新失败解释、停滞、低置信或阶段变化时才重新门控策略程序。
11. **反思停滞。** 若合法动作为空但证据仍不足，`PORTFOLIO_STALL_REFLECTION` 提出遗漏策略能力、迁移假设修订、判别 probe 或 regime 重匹配；核验后返回第一/二阶段或继续取证，模型不能直接宣布 `Tie`。
12. **晋级父代。** 候选只有在机制证据完整、相对父代的配对收益得到支持、关键旧能力未越界后才形成 $H_{t+1}$。没有合法候选时，若仍存在可补的案例或组合覆盖缺口，则返回前序阶段；只有硬约束已经证明不存在合法路线时才形成 `Reject`。现有动作均不能改变决定且证据充分时可以 `Tie`，不以任意固定评测预算代替结论。

```text
PLAN_TEST_AND_CREDIT(parent, candidates, program, generation_ledger,
                     coverage_gap,
                     trace_pool, select_pool, anchor_pool,
                     accounts, prior_round_ledger, regimes):
    eval_ledger <- empty
    r <- MATCH_OR_OPEN_REGIME(parent, prior_round_ledger, regimes)
    if candidates is empty:
        gap_event <- ROUTE_PORTFOLIO_COVERAGE_GAP(
                         coverage_gap, program, generation_ledger)
        APPEND(eval_ledger, gap_event)
        return gap_event.decision, accounts, eval_ledger, regimes
    schedule <- HYBRID_ADVISER_STATEFUL_MASTER(candidates, accounts[r])

    loop:
        for candidate with incomplete deterministic/mechanism gates:
            e <- RUN_COMMON_GATES(candidate, trace_pool)
            APPEND(eval_ledger, e)
            attribution_request <- BUILD_PORTFOLIO_EVIDENCE_REQUEST(
                                       candidate, program, e,
                                       generation_ledger, accounts[r])
            attribution_call <- CALL_OPTIMIZER_LLM(
                                    attribution_request,
                                    call_type=PORTFOLIO_EVIDENCE_ATTRIBUTION)
            attribution <- PARSE_PORTFOLIO_EVIDENCE_ATTRIBUTION(
                               attribution_call)
            attribution <- VERIFY_EVIDENCE_PATH_AND_PROPENSITY_ANCHORS(
                               attribution, candidate, program, e)
            LAYERED_CREDIT_UPDATE(
                candidate, e, attribution, accounts[r])

        evidence <- prior_round_ledger union eval_ledger
        decision <- PAIRED_PROMOTION_DECISION(parent, candidates, evidence)
        if decision is promote/reject/tie-with-sufficient-evidence:
            return decision, accounts, eval_ledger, regimes

        program_actions <- ENUMERATE_LEGAL_RACE_ACTIONS(
                               parent, candidates, schedule, evidence)
        action_request <- BUILD_NEXT_RACE_ACTION_REQUEST(
                              parent, candidates, program_actions,
                              evidence, accounts[r])
        action_call <- CALL_OPTIMIZER_LLM(
                           action_request,
                           call_type=NEXT_RACE_ACTION_PROPOSAL)
        action_proposals <- PARSE_NEXT_RACE_ACTION_PROPOSALS(action_call)
        actions <- program_actions union VERIFY_AND_COMPILE_RACE_ACTIONS(
                                           action_proposals, evidence)
        action <- SELECT_DECISION_RELEVANT_RACE_ACTION(actions, evidence)
        if action requests a new optimizer path or
           action exposes missing or invalid transfer evidence:
            if RETURN_EVIDENCE_IS_GENERATION_SAFE(action, evidence):
                if action requests a new optimizer path:
                    return RETURN_TO_OPTIMIZER_GENERATION(action), accounts, eval_ledger, regimes
                return RETURN_TO_CASE_RETRIEVAL(action), accounts, eval_ledger, regimes
            action <- SELECT_DECISION_RELEVANT_RACE_ACTION(
                          FILTER_OUT_GENERATION_RETURNS(actions), evidence)
        if action is none:
            reflection_request <- BUILD_PORTFOLIO_STALL_REFLECTION_REQUEST(
                                      candidates, program, evidence,
                                      coverage_gap, accounts[r])
            reflection_call <- CALL_OPTIMIZER_LLM(
                                   reflection_request,
                                   call_type=PORTFOLIO_STALL_REFLECTION)
            reflection <- PARSE_PORTFOLIO_STALL_REFLECTION(reflection_call)
            return_request <- VERIFY_AND_COMPILE_PORTFOLIO_RETURN(
                                  reflection, evidence)
            if return_request is valid and
               RETURN_EVIDENCE_IS_GENERATION_SAFE(return_request, evidence):
                return return_request, accounts, eval_ledger, regimes
            action <- COMPLETE_FROZEN_DEVELOPMENT_PANEL_ACTION(
                          parent, candidates, select_pool, anchor_pool,
                          evidence)
        if action is none:
            return unresolved, accounts, eval_ledger, regimes

        e <- EXECUTE_MATCHED_EVALUATION(
                 action, parent, select_pool, anchor_pool)
        APPEND(eval_ledger, e)
        result_attribution_request <- BUILD_PORTFOLIO_EVIDENCE_REQUEST(
                                          TARGET_CANDIDATES(action), program,
                                          e, generation_ledger, accounts[r])
        result_attribution_call <- CALL_OPTIMIZER_LLM(
                                       result_attribution_request,
                                       call_type=PORTFOLIO_EVIDENCE_ATTRIBUTION)
        result_attribution <- PARSE_PORTFOLIO_EVIDENCE_ATTRIBUTION(
                                  result_attribution_call)
        result_attribution <- VERIFY_EVIDENCE_PATH_AND_PROPENSITY_ANCHORS(
                                  result_attribution,
                                  TARGET_CANDIDATES(action), program, e)
        LAYERED_CREDIT_UPDATE(
            action, e, result_attribution, accounts[r])

        if MULTISCALE_REPLAY_DETECTS_SHIFT(
               prior_round_ledger union eval_ledger, r):
            r <- MARK_REGIME_SHIFT_SUSPECTED_AND_FREEZE_LOCAL_CREDIT(r)
```


### 案例与组合积累阶段：如何持续积累并跨任务复用

随着实验增加，案例库会快速积累大量只在种子、提示或微小配置上不同的记录。若全部进入活动索引，检索会被高频近重复成功淹没；若只保留最佳案例，又无法识别优化器在哪些边界上稳定失败。模型版本、工具和评分协议变化还会使旧信用失效，但旧 trace 与来源事实仍可能对新的判断有价值。

长期状态因此分为不可变运行账本、条件案例 revision、优化器信用账户和 evidence regime。原始事件永远保留，案例按条件与机制合并，信用只在明确的环境层级内统计；当环境发生变化时创建新 regime，而不是覆盖旧结果。进入活动检索层的案例由未来决策价值决定，少见但能区分迁移边界的失败案例可以比大量重复成功拥有更高保留优先级。

更新流程先校正选择概率与重复候选，计算各案例对条件边界和优化器排序的增量信息，再执行合并、分裂、降级或归档。系统周期性聚类所有优化器共同失败或无人覆盖的残差，形成新策略需求，并以冷启动账户验证新增优化器。跨任务启动时，目标条件先匹配 regime，再加载相关案例和组合先验，同时保留探索配额以检验历史组合是否仍然成立。

长期沉淀中的“两个案例为何相同或相反”“共同失败究竟缺少什么策略能力”“一次变化是否构成新 regime”也需要语义判断。`CASE_RELATION_AND_REVISION_PROPOSAL` 让 `OptimizerLLM` 提出支持、边界、冲突、冗余或条件分裂关系；`RESIDUAL_SPECIALIST_DESIGN` 把经程序确认的 coverage gap 转成新的策略契约草案；`REGIME_SHIFT_INTERPRETATION` 为多尺度统计变化提出模型、工具、接口、任务分布或评测器层的竞争解释。`OptimizerHarness` 负责来源与运行锚点核验、选择偏差检查、契约和权限检查、冷启动验证、regime 阈值判断及原子提交；模型输出不能覆盖原始证据或直接激活新 specialist。

这一阶段位于 benchmark 训练 loop 内，在每轮形成终止决定后执行。它只吸收 $H_t$ 的故障发现 trace、案例检索和迁移许可、优化器程序、候选归并、机制 gate、父子配对、anchor 回放及选择 propensity，不在线接收新论文。外部来源只能在 loop 外产生新的 `CaseCatalogSnapshot`；当前实验产生的 `EvolutionCase`、优化器账户和 regime revision 则写入 $K_{t+1}$，在下一轮 `CaseNeed` 形成后通过有条件的 `CaseMemoryView` 参与检索和组合。

**输入。** 旧长期状态 $K_t$、本轮 `OptimizationRoundLedger`、`GenerationLedger`、案例检索日志、优化器程序、终止决定和完整 `ExecutionTrace` 指针。

**输出。** 原子提交的新长期状态 $K_{t+1}$、供下一轮按需查询的案例/优化器索引，以及未能完成的案例关系、coverage gap 或 regime 审核项。原始运行先只追加提交；即使案例派生、信用结算、specialist 冷启动或索引重建失败，也不能丢失原始证据。

长期状态由四部分组成：

```text
LongTermState = {
  state_revision,
  immutable_run_ledger,
  conditional_case_memory,
  optimizer_registry_and_accounts,
  regime_history,
  llm_call_ledger_revision
}

EvolutionCase = {
  case_revision,
  context_and_response_signature,
  retrieved_case_proposals,
  optimizer_program,
  canonical_candidates,
  selected_actions_and_propensities,
  mechanism_activation,
  paired_effects,
  regressions,
  failed_transfer_conditions,
  source_run_pointers,
  evidence_regime,
  llm_call_ids
}
```

**算法 5：能力覆盖驱动的案例维护与优化器续造。**

1. **先提交完整运行。** 将查询、案例检索、适配许可、优化器选择、候选合并、逐实例评测和最终决定写成不可变记录；派生案例只能引用该记录，不能覆盖原证据。
2. **提出并核验案例关系。** `OptimizerLLM` 通过 `CASE_RELATION_AND_REVISION_PROPOSAL` 区分新证据是在支持旧案例、揭示适配边界、形成冲突、要求条件分裂，还是仅重复已有结论，并引用具体运行、条件差和机制事件。程序核验锚点、数据角色、regime 与选择 propensity 后才创建关系或 revision。
3. **维护 prototype 与 boundary。** 条件、适配计划和结果相近的案例形成导航 prototype；使结果翻转的差异保留为 boundary/exception link。检索必须能够下钻到具体运行，prototype 不替代证据。
4. **按能力覆盖维护案例库。** 评价案例是否覆盖新的任务—失败—环境区域，是否为已有区域提供更低适配成本，或是否保护关键反例。冗余判断不能只看文本相似。
5. **计算未来决策价值。** 活动索引的保留分数为：

   $$
   V_{retain}(c)=\alpha G_{coverage}+\beta I_{boundary}
   +\gamma I_{decision}+\eta E_{independent}
   -\rho R_{redundancy}-\xi U_{unresolved}.
   $$

   低任务得分的案例若能阻止错误迁移或错误选择，仍可具有高价值。
6. **按失败残差设计新策略。** 周期性收集当前策略程序共同失败、持续低置信或无人覆盖的案例簇。`RESIDUAL_SPECIALIST_DESIGN` 让 `OptimizerLLM` 提出目标残差、所需输入、调用类型、提示/工具策略、行动空间、预期中间产物、fallback 与反驳条件；程序把合格输出编译为 `OptimizerContract` 草案。新策略先通过接口和安全 gate，再进入冷启动探索池。
7. **验证新优化器的局部边际价值。** 在其声明覆盖的案例簇上，与当前优化器程序集从同一父 Harness、同一环境起点做成对比较。观察到独立边际价值后才进入活动门控；持续无增益则休眠，但保留 revision。
8. **更新选择器而不泄漏。** 只有记录了实际选择概率、候选合并关系和失败层级的运行才能训练信用模型。选择器调参与跨任务评价使用嵌套任务划分；冻结案例库、优化器池和选择器后再评估未见任务，避免 meta-overfitting。
9. **检测并分裂 regime。** 短窗口 replay 发现突然接口变化，长窗口 replay 发现策略排序、历史精英优势或方差缓慢漂移。检测器触发后，`REGIME_SHIFT_INTERPRETATION` 提出变化层级和竞争解释；只有统计阈值、版本差异和回放锚点共同通过核验才开启新 regime，冻结或折扣旧条件信用。外部来源、候选、trace 和旧 regime 不删除。
10. **让下一任务重新使用。** 新任务同时检索具体近邻、prototype、边界例、适配计划以及相应 regime 下的优化器一阶与转移信用。相似性只负责召回，迁移 gate 和目标证据仍须重新执行。

```text
RETAIN_CASES_AND_EXTEND_OPTIMIZERS(state, run_ledger, llm_call_ledger):
    raw_state, immutable_run <- APPEND_COMPLETE_RUN(state, run_ledger)
    shadow <- COPY_ON_WRITE(raw_state)
    new_case <- DERIVE_CONDITIONAL_EVOLUTION_CASE(immutable_run)
    relation_request <- BUILD_CASE_RELATION_REVISION_REQUEST(
                            new_case, shadow.conditional_case_memory,
                            immutable_run)
    relation_call <- CALL_OPTIMIZER_LLM(
                         relation_request,
                         call_type=CASE_RELATION_AND_REVISION_PROPOSAL)
    relation_proposals <- PARSE_CASE_RELATION_REVISION_PROPOSALS(
                              relation_call)
    relations <- VERIFY_CASE_RELATIONS_AND_REVISIONS(
                     relation_proposals, new_case,
                     shadow.conditional_case_memory, immutable_run)

    shadow.conditional_case_memory <- VERSIONED_REVISE_WITHOUT_OVERWRITE(
        shadow.conditional_case_memory, new_case, relations)
    shadow.conditional_case_memory <- UPDATE_PROTOTYPE_BOUNDARY_COMPETENCE(
        shadow.conditional_case_memory)

    residual_regions <- FIND_PORTFOLIO_COVERAGE_GAPS(
        shadow.optimizer_registry_and_accounts,
        shadow.conditional_case_memory)
    specialist_request <- BUILD_RESIDUAL_SPECIALIST_REQUEST(
                              residual_regions,
                              shadow.optimizer_registry_and_accounts)
    specialist_call <- CALL_OPTIMIZER_LLM(
                           specialist_request,
                           call_type=RESIDUAL_SPECIALIST_DESIGN)
    specialist_proposals <- PARSE_RESIDUAL_SPECIALIST_PROPOSALS(
                                specialist_call)
    new_optimizers <- VERIFY_AND_COMPILE_SPECIALIST_CONTRACTS(
                          specialist_proposals, residual_regions)
    shadow.optimizer_registry_and_accounts <- COLD_START_AND_VALIDATE(
        new_optimizers, shadow.optimizer_registry_and_accounts,
        shadow.conditional_case_memory, immutable_run)

    shift_signal <- MULTISCALE_REPLAY_DETECTS_SHIFT(shadow)
    if shift_signal is positive:
        shift_request <- BUILD_REGIME_SHIFT_INTERPRETATION_REQUEST(
                             shift_signal, shadow.regime_history,
                             immutable_run)
        shift_call <- CALL_OPTIMIZER_LLM(
                          shift_request,
                          call_type=REGIME_SHIFT_INTERPRETATION)
        shift_proposal <- PARSE_REGIME_SHIFT_INTERPRETATION(shift_call)
        verified_shift <- VERIFY_REGIME_SHIFT_INTERPRETATION(
                              shift_proposal, shift_signal,
                              immutable_run)
        if verified_shift is confirmed:
            shadow.regime_history <- OPEN_NEW_REGIME(
                                         shadow.regime_history,
                                         verified_shift)

    shadow.llm_call_ledger_revision <- CURRENT_LEDGER_REVISION(
                                           llm_call_ledger)
    if not LONG_TERM_INVARIANTS_HOLD(shadow):
        return raw_state, pending_review
    K_next <- ATOMIC_COMMIT_LONG_TERM_STATE(shadow)
    indexes <- REBUILD_CASE_AND_OPTIMIZER_INDEXES(K_next)
    return K_next, indexes
```

该阶段形成两种不同的学习：案例记忆学习“什么条件下可以迁移以及怎样适配”，优化器组合学习“在当前状态下应让哪一种生成过程先做什么”。两者共享不可变运行证据，但不能互相代替。

| 可以由设计保证 | 必须通过实验验证 |
| --- | --- |
| 方法、优化器和候选具有独立身份与来源链 | 行为签名能否预测 Harness 方法迁移价值 |
| 完全相同候选只执行一次，近似候选不复制 reward | 共享候选和信用估计是否减少无效评测 |
| 生成、接入、激活和效果失败分层记录 | 分层归因是否改善优化器选择与方法边界判断 |
| regime 变化产生新条件统计而不覆盖旧证据 | replay 能否及时发现模型、工具和任务漂移 |
| 只有记录选择概率的运行才用于 propensity 校正 | 混合调度是否优于单优化器、并行均分和静态路由 |
| 固定案例库、优化器池和选择器后再做未见任务评估 | 累积案例和顺序信用能否产生跨任务收益 |

### 四阶段在多轮 Harness 演化中的完整流转

四个阶段共同完成训练集上的一次 Harness 更新。实验开始前只执行一次离线案例编译并冻结 `CaseCatalogSnapshot`，同时封存 benchmark 测试集。在线 loop 从 $(H_0,K_0)$ 开始：$H_0$ 是未经本方法优化的父 Harness；$K_0$ 保存进入当前实验前已经可用的案例 revision、优化器注册表、分 regime 账户和历史运行，但不包含当前 benchmark 测试证据。每轮必须先运行当前父代并形成新的行为响应与 `CaseNeed`，不能直接拿上一轮的案例提案生成下一代。

第一阶段的在线检索将当前 `CaseNeed` 同时作用于固定目录和 $K_t$ 的 `CaseMemoryView`，返回迁移许可与校准要求。第二阶段根据当前 trace、案例提案和账户状态构造优化器程序，并将多来源提案归并成冻结候选。第三阶段在本轮内部滚动取证：若尚未披露 select 结果，且 trace、合成 probe 或 anchor 证据表明案例迁移失效，可以修订需求并返回第一阶段；同类证据要求新的优化器路径、修复绑定或改变披露顺序时，可以返回第二阶段。任何 select 结果一旦披露，本轮便不再返回生成阶段，而是对现有冻结候选作出终止决定，将新证据留给下一轮。所有合法返回仍沿用同一父代和数据角色，旧候选也保持不可变。

只有第三阶段得到 `Promote`、`Reject` 或证据充分的 `Tie`，第四阶段才将完整运行写入 $K_t$，派生案例边界、结算分层信用、识别组合覆盖缺口并处理 regime 变化。`Promote` 令获胜候选成为 $H_{t+1}$；`Reject` 或 `Tie` 令 $H_{t+1}=H_t$。提交 $K_{t+1}$ 后，训练调度器更新任务曝光历史、失败区域覆盖、anchors、反馈债务和未决迁移证据；第 $t+1$ 轮必须用新父代重新产生 trace，不能继承旧候选的效果统计。

```text
EVOLVE_WITH_CONDITIONAL_PORTFOLIO_ON_TRAIN(
    H0, K0, catalog_snapshot, D_train, train_protocol):

    scheduler <- INIT_TRAIN_SCHEDULER(D_train, train_protocol)
    llm_call_ledger <- INIT_LLM_CALL_LEDGER(train_protocol)
    H <- H0
    K <- K0
    t <- 0

    loop:
        trace_pool, select_pool, anchor_pool <-
            ASSIGN_TRAIN_ROLES(scheduler, H, K)

        trace_batch <- RUN_HARNESS(H, trace_pool, train_protocol)
        need <- BUILD_CASE_NEED(H, trace_batch, K, train_protocol)
        case_view <- RETRIEVE_CASE_MEMORY_VIEW(K, need, train_protocol)
        case_proposals <- ONLINE_RETRIEVE_CONDITIONAL_CASES(
                              catalog_snapshot, case_view, need)

        context <- BUILD_EVOLUTION_CONTEXT(
                       H, trace_batch, need, case_proposals, K)
        accounts, regimes <- PORTFOLIO_STATE(K)
        round_ledger <- INIT_OPTIMIZATION_ROUND_LEDGER(
                            t, H, trace_batch, need, case_proposals)

        repeat:
            candidates, program, generation_ledger, coverage_gap <-
                GENERATE_WITH_CONDITIONAL_OPTIMIZER_PROGRAM(
                    context, K.optimizer_registry_and_accounts)
            APPEND(round_ledger, generation_ledger)

            decision, accounts, eval_ledger, regimes <-
                PLAN_TEST_AND_CREDIT(
                    H, candidates, program, generation_ledger,
                    coverage_gap, trace_pool, select_pool, anchor_pool,
                    accounts, round_ledger, regimes)
            APPEND(round_ledger, eval_ledger)
            UPDATE_EXPOSURE_FROM_LLM_CALLS(
                scheduler, llm_call_ledger, candidates,
                trace_pool union select_pool union anchor_pool)

            if decision is Unresolved:
                return PAUSE_INCOMPLETE_EVOLUTION(
                           H, K, round_ledger, scheduler)

            if decision is ReturnOptimizerGeneration:
                select_pool, anchor_pool <-
                    REFRESH_INDEPENDENT_DEVELOPMENT_POOLS(
                        scheduler, candidates,
                        select_pool, anchor_pool)
                context <- REVISE_CONTEXT_FROM_PORTFOLIO_RETURN(
                               context, eval_ledger, accounts)
                continue

            if decision is ReturnCaseRetrieval:
                select_pool, anchor_pool <-
                    REFRESH_INDEPENDENT_DEVELOPMENT_POOLS(
                        scheduler, candidates,
                        select_pool, anchor_pool)
                need <- REVISE_CASE_NEED(need, eval_ledger)
                case_view <- RETRIEVE_CASE_MEMORY_VIEW(
                                 K, need, train_protocol)
                case_proposals <- ONLINE_RETRIEVE_CONDITIONAL_CASES(
                                      catalog_snapshot, case_view, need)
                context <- BUILD_EVOLUTION_CONTEXT(
                               H, trace_batch, need, case_proposals, K,
                               eval_ledger)
                continue
        until decision is Promote, Reject, or Tie

        round_ledger <- FINALIZE_OPTIMIZATION_ROUND_LEDGER(
                            round_ledger, decision, accounts, regimes)
        K_next, indexes <- RETAIN_CASES_AND_EXTEND_OPTIMIZERS(
                               K, round_ledger, llm_call_ledger)
        if indexes is PENDING_REVIEW:
            return PAUSE_INCOMPLETE_EVOLUTION(
                       H, K_next, round_ledger, scheduler)
        UPDATE_EXPOSURE_FROM_LLM_CALLS(
            scheduler, llm_call_ledger,
            LONG_TERM_REVISIONS_CREATED(K, K_next),
            trace_pool union select_pool union anchor_pool)
        H_next <- ACCEPT_IF_PROMOTED(H, candidates, decision)

        UPDATE_TRAIN_SCHEDULER(
            scheduler, trace_pool, select_pool, anchor_pool,
            decision, round_ledger, H_next, K_next)

        if CONDITIONAL_PORTFOLIO_FIXED_POINT(
               scheduler, H, H_next, K, K_next, round_ledger):
            break

        H <- H_next
        K <- K_next
        t <- t + 1

    return FREEZE_CONDITIONAL_PORTFOLIO_FOR_FINAL_TEST(
               H_next, K_next, catalog_snapshot, train_protocol)
```

`CONDITIONAL_PORTFOLIO_FIXED_POINT` 只在训练调度器完成一个覆盖全部预定任务族、失败区域和关键 anchors 的轮换后检查。stop 必须同时满足：本轮换没有候选达到 `Promote`；所有候选已被 `Reject` 或形成证据充分的 `Tie`；没有新的迁移边界、coverage gap、优化器 revision、反馈债务结算或 regime 变化会改变下一轮案例检索与优化器程序；不存在仍能改变父子选择或账户排序的合法运行。外部服务失败、执行中断、应记录而未记录的 propensity、`INCOMPLETE_RUN`、`pending_review` 或未解决迁移条件都不是 stop。

stop 后冻结最终 Harness、`LongTermState`、目录快照、优化器池与选择器、模型和工具环境、评测器及随机协议，随后才在 $D_{\mathrm{test}}$ 上按照 benchmark 官方协议运行。测试阶段不再调用优化器程序，不更新案例、账户或 regime，不产生新候选，也不把测试 trace 写回长期状态；测试结果只用于最终报告和与 baseline 比较。

## 二、字段、公式与参数完整定义

### 基本约定

| 概念 | 规范 |
| --- | --- |
| 案例 | 一次“条件—诊断—干预—构造过程—观测结果”的完整记录，不等同于任务文本或最终 patch。 |
| optimizer revision | `OptimizerHarness` 内从 `EvolutionContext` 到一类 `OptimizerLLM` 调用和候选分布的版本化策略；它不是独立 agent。策略负责构造候选，接受器负责晋级，两者不得混合。 |
| regime | 模型、工具、Harness 接口、任务分布和评测器生成机制近似稳定的版本区间。 |
| 候选归并 | 对同一父版本产生语义等价 `normalized_change` 的提案只评测一次，但保留所有来源优化器及提案概率。 |
| 未知 | 转移条件、适配条件或结果未知时保留 `UNKNOWN`，不得按失败或成功计入信用。 |

### 数据字段规范

#### Benchmark 数据角色与轮次边界

| 符号 | 类型 | 精确定义 |
| --- | --- | --- |
| $D_{\mathrm{train}}$ | 固定任务集合 | benchmark 官方训练集，是在线案例检索、候选生成、信用更新和 stop 判断唯一允许访问的 benchmark 任务全集。官方无训练集时必须事先公开定义开发集，不能从测试集回填。 |
| $D_{\mathrm{test}}$ | 封闭任务集合 | 只在训练 loop stop 且系统冻结后运行；其输入、标签、trace 和结果不得进入案例、优化器账户、regime 或调度器。 |
| $D_t^{\mathrm{trace}}$ | 训练子集 | 第 $t$ 轮运行父代并产生行为签名、成功/失败 trace、迁移校准和候选生成证据。 |
| $D_t^{\mathrm{select}}$ | 训练子集 | 候选冻结前不向 `OptimizerLLM` 披露且不进入生成视图的父子收益判定集合。 |
| $D_t^{\mathrm{anchor}}$ | 训练子集 | 已确认能力、接口、安全和严重失败的回放集合。 |
| $D_{dev}^{(t)}$ | 派生集合 | $D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}$，仅用于候选选择与回归判断。 |

同一轮要求三类基础集合两两不相交。跨轮可以轮换角色，但每次暴露必须写入 `ExposureRecord`；曾向当前候选生成过程披露的任务不能在同一候选 revision 上重新声明为独立选择证据。

#### `TrainProtocol`

| 字段 | 精确定义 |
| --- | --- |
| `benchmark_revision` | benchmark 名称、任务 revision 和官方评测协议。 |
| `split_revision` | 训练/测试任务 ID 及其来源，冻结后不可迁移任务。 |
| `task_strata` | 用于完整轮换的任务族、失败族、能力、长度、工具和环境分层。 |
| `role_assignment_rule` | trace/select/anchor 的分配、轮换、冷却和重复规则。 |
| `execution_config` | 模型、采样、上下文、工具、容器、网络、资源与超时。 |
| `optimizer_config_revision` | `OptimizerLLMConfig`、`OptimizerHarness` 代码、策略 registry、parser、核验器和调用账本 schema 的冻结 revision。 |
| `probe_suite_revision` | 构造 `ResponseSignature` 的固定 probe、特征 schema 和归一化 revision。 |
| `evaluator_revision` | grader、指标方向、失败编码、聚合和并列规则。 |
| `seeds` | 父子配对、probe、重复运行和调度随机性允许使用的种子集合。 |
| `promotion_rule` | `Promote/Reject/Tie` 所需的激活、收益、回归和证据充分性条件。 |
| `stop_rule` | 完整训练轮换、案例边界、组合覆盖、账户/regime 变化与可执行实验共同决定的固定点规则。 |

#### `OptimizationAgent`

本方法中的 `OptimizationAgent` 定义为：

$$
\text{OptimizationAgent}=\text{OptimizerLLM}+\text{OptimizerHarness}.
$$

公式中的加号表示二者共同组成一个可运行系统，不表示数值相加。`OptimizerLLM` 是来源案例语义抽取、目标故障诊断、迁移与适配推理、策略程序设计、候选代码生成、空组合失败综合、证据分层归因、竞赛动作规划、案例关系修订、specialist 设计和 regime 变化解释的认知主体。`OptimizerHarness` 固定数据角色，构造每类调用的最小权限视图，解析并核验输出，执行检索、硬过滤、代码检查、真实评测、信用更新、长期状态提交和测试隔离。组合中的 optimizer revision 是 `OptimizerHarness` 内部的一种调用策略，不是另一个完整 agent。

| `OptimizerHarness` 组件 | 职责 | 发起的 `OptimizerLLM` 调用 |
| --- | --- | --- |
| `case_catalog_compiler_and_retriever` | 固定来源锚点，核验条件案例字段，构造 `CaseNeed`，执行多视图召回、硬过滤、迁移校准和排序。 | `SOURCE_CASE_SEMANTIC_EXTRACTION`、`TARGET_CASE_NEED_DIAGNOSIS`、`CASE_TRANSFER_AND_ADAPTATION_PROPOSAL`。 |
| `portfolio_program_builder` | 管理策略契约、结果模型、残差覆盖、路径依赖与披露策略，核验无环程序。 | `PORTFOLIO_PROGRAM_DESIGN`。 |
| `candidate_context_builder_and_parser` | 按策略 revision 构造知识、方法或自由探索视图，将模型输出解析为共同候选 IR；全部路径为空时核验跨路径失败解释并编译 coverage gap。 | `CASE_GUIDED_CANDIDATE_PROPOSAL`、`METHOD_GUIDED_CANDIDATE_PROPOSAL`、`FREE_CANDIDATE_PROPOSAL`、`CANDIDATE_CRITIQUE_AND_REVISION`、`EMPTY_PORTFOLIO_DIAGNOSIS`。 |
| `race_planner_and_credit_engine` | 执行 gate、父子配对与 anchor 回放，核验证据归因和动作提案，按冻结规则更新信用和作出决定。 | `PORTFOLIO_EVIDENCE_ATTRIBUTION`、`NEXT_RACE_ACTION_PROPOSAL`、`PORTFOLIO_STALL_REFLECTION`。 |
| `long_term_case_and_portfolio_manager` | 核验案例关系、覆盖残差、specialist 契约与 regime 变化，原子提交 $K_{t+1}$。 | `CASE_RELATION_AND_REVISION_PROPOSAL`、`RESIDUAL_SPECIALIST_DESIGN`、`REGIME_SHIFT_INTERPRETATION`。 |
| `llm_call_ledger` | 追加保存实际输入视图、原始输出、解析/核验状态、工具会话和费用。 | 不产生调用，只记录调用。 |

被优化的执行 agent 由执行模型和当前 Harness $H_t$ 组成，在 benchmark 任务上产生 `ExecutionTrace`。即使执行模型与 `OptimizerLLM` 使用同一基础模型，也必须隔离会话、上下文、工具权限、随机配置和调用账本。

#### `OptimizerLLMConfig`

| 字段 | 精确定义 |
| --- | --- |
| `provider_model_revision` | provider、模型名称和不可变 revision 或可审计快照。 |
| `call_types` | 只允许 `SOURCE_CASE_SEMANTIC_EXTRACTION`、`TARGET_CASE_NEED_DIAGNOSIS`、`CASE_TRANSFER_AND_ADAPTATION_PROPOSAL`、`PORTFOLIO_PROGRAM_DESIGN`、`CASE_GUIDED_CANDIDATE_PROPOSAL`、`METHOD_GUIDED_CANDIDATE_PROPOSAL`、`FREE_CANDIDATE_PROPOSAL`、`CANDIDATE_CRITIQUE_AND_REVISION`、`EMPTY_PORTFOLIO_DIAGNOSIS`、`PORTFOLIO_EVIDENCE_ATTRIBUTION`、`NEXT_RACE_ACTION_PROPOSAL`、`PORTFOLIO_STALL_REFLECTION`、`CASE_RELATION_AND_REVISION_PROPOSAL`、`RESIDUAL_SPECIALIST_DESIGN`、`REGIME_SHIFT_INTERPRETATION`。 |
| `decoding_by_call_type` | 每类调用的 temperature、top-p、最大输出、停止条件、推理强度、种子策略和候选数量。 |
| `prompt_template_revisions` | 每类调用的系统指令、输入序列化、输出 schema 和示例 revision。 |
| `context_policies` | 每类调用允许披露的来源、代码、trace、案例、账户和证据字段；未列字段默认禁止。 |
| `tool_policy` | 可读写代码范围、允许的静态分析和测试工具；禁止读取测试集、绕过 gate 或直接写长期状态。 |
| `retry_policy` | 超时、格式错误和工具失败的最大重试及退避；每次重试创建新 call ID。 |
| `parser_revision` | 每类输出的固定解析器；只能提取或拒绝模型给出的字段，不能补写未输出语义。 |

#### `LLMCallRecord`

| 字段 | 精确定义 |
| --- | --- |
| `call_id` | 一次 `OptimizerLLM` 请求的唯一 ID；重试使用新 ID。 |
| `round_id` | 在线调用所属外层轮次；离线来源抽取使用 `OFFLINE:<catalog_revision>`。 |
| `call_type` | `OptimizerLLMConfig.call_types` 中的一种，决定披露策略、输出 schema 和核验器。 |
| `strategy_revision` | 触发调用的 optimizer revision；非策略调用为 `SYSTEM_CASE_PIPELINE`。 |
| `model_revision` | 实际响应请求的模型 revision。 |
| `prompt_template_revision` | 本次使用的模板和 schema revision。 |
| `input_view_revision` | `OptimizerHarness` 构造的不可变最小权限视图。 |
| `disclosed_object_ids` | 实际披露的来源单元、父代码、trace、案例、候选、证据或账户 ID。 |
| `forbidden_object_check` | `PASS/FAIL`；检查测试数据、未来 revision、隐藏标签和越权文件，`FAIL` 时不得调用。 |
| `tool_session_id` | 隔离工具会话 ID 或 `NONE`，记录实际读写和执行权限。 |
| `seed` | 实际生成种子或 `UNCONTROLLED`。 |
| `raw_output_ref` | 原始响应的不可变存储位置。 |
| `parsed_output_ids` | 解析产生的提案、候选 IR、关系或契约草案 ID；失败时为空。 |
| `validation_status` | `PENDING/PARSE_FAILED/ANCHOR_REJECTED/GATE_REJECTED/RULE_REJECTED/EVIDENCE_REJECTED/ACCEPTED_AS_PROPOSAL`。 |
| `parent_call_id` | 格式修复或受控重试所引用的前一调用；首次为 `NONE`。 |
| `usage` | 输入/输出 token、费用、时延和工具调用数，只用于复现与成本统计。 |

`CALL_OPTIMIZER_LLM` 在请求开始前建立 `call_id`，并把请求、响应、解析与核验状态以追加事件写入实验级 `LLMCallLedger`。调用失败和被拒绝输出同样保留。任何案例字段、迁移计划、候选、证据归因、竞赛动作、specialist 或 regime 解释都必须通过 `call_id` 回指产生它的调用。

#### `OptimizerProposal`

除三类候选生成调用直接解析为 `CandidateProposalIR` 外，其余模型输出先进入统一提案外壳：

| 字段 | 精确定义 |
| --- | --- |
| `proposal_id` | 一项不可变提案的唯一 ID；同一调用返回多项时分别编号。 |
| `call_id` | 产生提案的 `LLMCallRecord`。 |
| `proposal_type` | 与对应 `call_type` 一致；不一致时解析失败。 |
| `target_ids` | 被解释、迁移、规划、归因、修订或抽象的来源、案例、策略、候选、证据或 regime 对象。 |
| `payload` | 下表规定的 call-specific 字段；缺少必填字段时不得核验。 |
| `evidence_anchors` | 每个关键结论引用的来源位置、代码符号、trace 事件、运行、候选、路径或账户事件。 |
| `counterevidence` | 与提案冲突或限制适用性的锚点；没有时为空列表。 |
| `uncertainties` | 当前视图无法判断的前提、替代解释和所需观察。 |
| `expected_observations` | 提案正确或错误时应出现的可执行谓词；纯来源抽取可为 `NOT_APPLICABLE`。 |
| `validation_status` | `PENDING/ACCEPTED/REJECTED/PARTIALLY_ACCEPTED`，只由 `OptimizerHarness` 写入。 |

| call type | `payload` 必填字段 | 含义 |
| --- | --- | --- |
| `SOURCE_CASE_SEMANTIC_EXTRACTION` | `{experiment_units,mechanism_steps,construction_steps,context_fields,outcome_attribution,configurable_slots,unknown_fields}` | 提出实验单元、机制与构造过程、条件、结果归属、可调槽和未知项。 |
| `TARGET_CASE_NEED_DIAGNOSIS` | `{competing_failure_hypotheses,earliest_divergences,target_capability,immutable_constraints,observable_evidence,unknown_conditions}` | 从父代 trace 和代码形成可反驳的当前需求。 |
| `CASE_TRANSFER_AND_ADAPTATION_PROPOSAL` | `{source_case,mechanism_mapping,step_actions,slot_bindings,interaction_risks,required_probes,stop_conditions}` | 对过滤后案例提出逐步骤迁移与适配计划。 |
| `PORTFOLIO_PROGRAM_DESIGN` | `{entry_strategies,transition_candidates,intermediate_schemas,guards,backup_paths,residual_coverage}` | 提出策略程序结构和各边的中间产物契约。 |
| `CANDIDATE_CRITIQUE_AND_REVISION` | `{candidate_id,failure_layer,target_locations,preserved_parts,minimal_revision,expected_trace_change,required_rechecks}` | 对候选提出带锚点的最小新 revision。 |
| `EMPTY_PORTFOLIO_DIAGNOSIS` | `{failed_path_ids,failure_hypotheses,failure_layers,cross_path_commonalities,distinguishing_events,missing_observations,proposed_remedies,uncertainties}` | 综合全部策略路径为何没有产生合法候选，并提出可由已有事件核验的缺口解释；不得宣称父代最优或直接决定路由。 |
| `PORTFOLIO_EVIDENCE_ATTRIBUTION` | `{observation_ids,supported_layers,refuted_layers,unknown_layers,responsible_path_segments,alternative_explanations,next_observations}` | 把真实证据映射到生成、接入、激活、效果或转移层。 |
| `NEXT_RACE_ACTION_PROPOSAL` | `{action_kind,target_ids,executable_parameters,expected_decision_change,stop_condition}` | 排序合法动作或提出参数完整且可核验的新动作。 |
| `PORTFOLIO_STALL_REFLECTION` | `{stagnation_cause,missing_strategy_capability,transfer_revision,discriminating_probe,regime_rematch}` | 对停滞提出可返回前序阶段的具体修订。 |
| `CASE_RELATION_AND_REVISION_PROPOSAL` | `{left_case,right_case,relation,distinguishing_conditions,revision_operation,scope}` | 提出支持、边界、冲突、冗余或条件分裂关系。 |
| `RESIDUAL_SPECIALIST_DESIGN` | `{target_gap,input_requirements,call_policy,action_space,intermediate_schema,fallback,refutation_conditions}` | 把确认的覆盖缺口转成待核验策略契约。 |
| `REGIME_SHIFT_INTERPRETATION` | `{change_level,competing_causes,affected_accounts,carryover_safe_fields,reset_fields,confirming_replays}` | 解释统计变化并限定可继承与须重置状态。 |

`CASE_GUIDED_CANDIDATE_PROPOSAL`、`METHOD_GUIDED_CANDIDATE_PROPOSAL` 与 `FREE_CANDIDATE_PROPOSAL` 直接解析为共同 `CandidateProposalIR`；三者只允许输入视图不同，输出字段和后续 gate 完全相同。

#### `ExposureRecord`

| 字段 | 精确定义 |
| --- | --- |
| `task_id` | 训练任务稳定 ID。 |
| `round_id` | 所属外层演化轮次。 |
| `split_role` | `trace/select/anchor` 之一。 |
| `visible_to_optimizer_before_freeze` | 候选冻结前是否进入 `OptimizerHarness` 构造的生成视图或向 `OptimizerLLM` 披露任务、标签或 trace。 |
| `disclosed_fields` | 实际披露的输入、标签、trace、指标、代码和账户字段。 |
| `disclosed_to_call_ids` | 接收上述字段的全部 `LLMCallRecord`。 |
| `affected_candidate_ids` | 使用相应调用输出生成、修订或规划的候选及后代。 |
| `affected_long_term_revision_ids` | 使用相应调用输出形成的案例、策略、账户或 regime revision。 |
| `independence_status` | 对每个受影响对象取 `INDEPENDENT/EXPOSED/NOT_APPLICABLE`；披露一旦影响对象形成便不能恢复为独立。 |
| `harness_versions` | 该角色下运行的父代或候选 revisions。 |
| `run_ids` | 对应 `ExecutionTrace.run_id` 列表。 |
| `evidence_uses` | `response-signature/diagnosis/calibration/generation/gate/selection/regression/credit` 中实际用途。 |

#### `ExecutionTrace`

| 字段 | 精确定义 |
| --- | --- |
| `run_id` | 一次不可变真实执行的唯一 ID。 |
| `task_id` | 输入任务 ID，必须连接到 `ExposureRecord`。 |
| `split_role` | 本次执行的数据角色。 |
| `harness_version` | 执行的冻结 Harness revision。 |
| `model_tool_environment_versions` | 模型、采样、工具 schema、容器、依赖、外部服务和评测器版本。 |
| `seed` | 模型、环境与调度随机性的实际种子；不可控来源标为 `UNCONTROLLED`。 |
| `ordered_events` | 真实时序的模型、工具、状态、控制、异常、回退与终止事件，含输入输出指针和父事件。 |
| `optimizer_visible_context` | 候选冻结前允许优化器读取的事件与字段集合。 |
| `final_output` | 最终可评分输出或终止状态。 |
| `metric_vector` | grader 返回的全部原始指标和方向。 |
| `failure_signature` | 失败阶段、异常类别、未满足条件和最早偏离；成功为 `NONE`。 |
| `replay_artifacts` | 输入、配置、环境与允许缓存的工具响应；不能重放时说明原因。 |

#### `CaseCatalogSnapshot`

| 字段 | 精确定义 |
| --- | --- |
| `catalog_revision` | 本次实验固定引用的案例目录 revision。 |
| `source_packet_ids` | 离线组织使用的全部来源包 ID。 |
| `external_case_revisions` | 从论文和工程来源恢复的 `ConditionalInterventionCase` revisions。 |
| `probe_suite_revision` | 目录案例响应签名使用的 probe 与特征 schema。 |
| `transport_and_boundary_relations` | 案例间已核验的适配、反例、边界和环境变化关系。 |
| `indexes` | 可由权威案例重建的响应、条件、机制、代码、证据和反例索引。 |
| `compiler_config` | 案例拆分、字段抽取、`SOURCE_CASE_SEMANTIC_EXTRACTION` 提示/parser/核验器、变化槽定位和索引配置；任一改变产生新 revision。 |
| `semantic_extraction_call_ids` | 离线 `SOURCE_CASE_SEMANTIC_EXTRACTION` 调用，包括解析或核验失败记录。 |
| `frozen_at` | 快照冻结时间，仅用于审计。 |

#### `CaseMemoryView`

| 字段 | 精确定义 |
| --- | --- |
| `query_need_id` | 产生视图的当前 `CaseNeed.need_id`。 |
| `case_revisions` | 从 $K_t$ 中按 scope、regime、时间和权限过滤的在线案例。 |
| `prototypes_and_boundaries` | 与当前需求相关的原型、边界例和拒绝路线。 |
| `optimizer_priors` | 当前 regime 下可用于组合但尚未当作目标真值的一阶与转移信用。 |
| `failed_transfer_conditions` | 与当前目标条件匹配的迁移反例。 |
| `as_of` | 查询允许访问的证据截止时间，防止读取未来 revision。 |

#### `SourcePacket`

| 字段 | 定义 |
| --- | --- |
| `source_packet_id` | 固定论文—代码来源包的稳定 ID；内容或来源 revision 变化时创建新 ID。 |
| `paper_version` | 固定论文版本及本地原文。 |
| `official_code_version` | 固定官方代码 revision、范围和许可证。 |
| `exact_source_anchors` | 机制、实验条件、代码和限制的精确定位。 |
| `configs_and_examples` | 配置、命令、输入输出和运行前提。 |
| `tests_and_reported_results` | 测试协议、对照、结果、消融、失败条件和复核状态。 |

#### `ConditionalInterventionCase`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `case_id` | 稳定 ID | 案例身份；内容修订使用 revision。 |
| `source_context` | 复合对象 | 干预发生前的任务响应、Harness、模型/工具环境和评测协议；四个子字段必须来自同一实验单元。 |
| `source_context.task_response_signature` | 数值/类别向量 | 固定 probe 下的失败族、工具路径、上下文压力、恢复路径、验证覆盖和模块敏感性。 |
| `source_context.harness_state` | 版本化结构对象 | Harness 代码版本、模块图、已启用机制和关键配置。 |
| `source_context.model_tool_environment` | 环境对象 | 模型/provider/推理参数、工具协议、容器、权限和外部服务版本。 |
| `source_context.evaluation_protocol` | 协议对象 | 数据 split、任务集、重复、种子、预算、指标和评测器。 |
| `diagnosed_need` | 结构化诊断 | 要修复的失败原因、证据、严重度和仍竞争的解释。 |
| `method_intervention` | 复合对象 | 实际加入的机制、宿主能力要求、硬前提、可调槽和已知交互；不包含生成该实现的优化过程。 |
| `method_intervention.mechanism` | 有序步骤 | 实际接入的机制程序。 |
| `method_intervention.required_capabilities` | 能力列表 | 宿主必须已有的接口和行为能力。 |
| `method_intervention.hard_preconditions` | 谓词列表 | 迁移前必须满足的条件。 |
| `method_intervention.configurable_slots` | 参数映射 | 可适配的 hook、阈值、adapter、顺序和回退；每项有类型与范围。 |
| `method_intervention.known_interactions` | 关系列表 | 与其他机制的依赖、协同、替代和冲突。 |
| `construction_process` | 有序事件列表 | 从来源方法到具体 patch 的选择、适配、实现、修订和验证步骤。 |
| `observations` | 复合对象 | 在固定评测协议下记录的激活、配对效果、回归、方差和实测成本；不同协议不得合并。 |
| `observations.mechanism_activation` | 三值与证据 | 机制是否真实触发及对应 trace。 |
| `observations.paired_effects` | 指标差分分布 | 同任务同环境父子配对的收益。 |
| `observations.regressions` | 指标差分分布 | 旧能力、安全、成本和稳定性退化。 |
| `observations.variance` | 方差对象 | 任务间、种子间、运行间和评测器间方差。 |
| `observations.measured_cost` | 成本向量 | token、墙钟、模型费用、工具调用和人工时间。 |
| `failed_conditions` | 条件列表 | 已观察到无法迁移、无法激活或产生退化的条件。 |
| `changed_environment_slots` | 差异映射 | 相对来源环境发生变化的模型、工具、接口、任务和评测字段。 |
| `evidence_regime` | regime ID | 案例证据所属稳定环境区间。 |
| `source_anchors` | 锚点列表 | 所有外部事实与原始运行的定位。 |
| `unknown_fields` | 字段路径列表 | 当前仍未知的字段以及获取它们的动作。 |
| `semantic_extraction_call_ids` | 调用 ID 列表 | 提出当前语义字段的来源抽取调用；程序提取字段可为空。 |
| `field_validation_status` | 字段到状态映射 | 每个语义字段取 `ANCHORED/STATICALLY_VERIFIED/EXECUTION_VERIFIED/UNKNOWN/REJECTED`。 |

#### `CaseNeed`

| 字段 | 精确定义 |
| --- | --- |
| `need_id` | 当前父 Harness、外层轮次和 revision 绑定的需求 ID；返回检索修订时产生新 revision。 |
| `target_response_signature` | 目标任务在同一固定 probe 下的行为签名；与来源签名使用同一 schema 和归一化。 |
| `current_harness_state` | 当前父 Harness 的版本化结构和配置。 |
| `model_tool_environment` | 当前模型、工具、权限和运行环境。 |
| `diagnosed_need` | 当前 trace 支持的失败原因与目标能力。 |
| `immutable_constraints` | 任何候选都不得修改的接口、安全、数据和预算条件。 |
| `observable_target_evidence` | 当前可运行的 probe、任务、静态检查和指标。 |
| `unknown_conditions` | 会影响迁移但尚未观测的条件。 |
| `source_call_id` | 产生当前 revision 的 `TARGET_CASE_NEED_DIAGNOSIS` 调用。 |

#### `CaseProposal`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `proposal_id` | 唯一 ID | 当前 need、来源案例 revision、适配计划 revision 和校准结果共同确定的提案身份。 |
| `need_id` | `CaseNeed` ID | 该提案回答的需求 revision；需求改变时不得静默复用旧提案。 |
| `retrieved_case` | case revision | 被召回的完整案例。 |
| `adaptation_plan` | `AdaptPlan` | 对每个机制步骤和接口标记 `KEEP/PARAMETERIZE/REPLACE/DELETE/ADD_PREREQ`，并给出代码位置。 |
| `transfer_decision` | 枚举 | `DIRECT`、`CALIBRATE`、`REJECT` 或 `UNKNOWN`。 |
| `required_target_evidence` | 动作列表 | 执行迁移前后必须取得的目标证据。 |
| `predicted_gain` | 分布 | 在目标条件下的收益预测，包含均值、区间和模型版本。 |
| `predicted_adaptation_cost` | 成本分布 | 代码修改、运行、token、时延和人工复核成本。 |
| `interaction_risk` | `[0,1]` 与原因 | 与现有模块、状态、权限和其他方法发生冲突的概率或上界。 |
| `uncertainty` | 分解对象 | 数据不足、环境变化、模型失配和结果噪声分别量化。 |
| `rejection_reason` | 枚举与证据 | 只有 `REJECT` 时必填，例如硬前提失败或风险超限。 |
| `llm_call_ids` | 调用 ID 列表 | 产生目标需求解释、迁移映射和适配计划的调用。 |

#### `OptimizerContract`

| 字段 | 精确定义 |
| --- | --- |
| `optimizer_id` | 优化器家族与 revision 的唯一标识。 |
| `optimizer_type` | `STATELESS_ADVISER` 每轮只依赖公开上下文；`STATEFUL_OPTIMIZER` 还依赖不可与其他优化器混用的私有历史。 |
| `llm_call_policy` | 该策略允许发起的 call type、提示 revision、输入视图、输出 schema、工具权限、采样参数和最大调用数。 |
| `applicability` | 优化器可处理的任务、故障、代码范围和 regime 谓词。 |
| `observation_requirements` | 运行前必须提供的 trace、代码、方法、指标和历史字段。 |
| `private_state_schema` | stateful optimizer 私有状态的类型、更新和清理规则；stateless 时为 `NOT_APPLICABLE`。 |
| `action_space` | 可产生的诊断、检索、编辑、绑定、取证或回退动作。 |
| `editable_scope` | 允许修改的文件、模块、配置和接口。 |
| `method_forms_supported` | 可消费的方法表示，例如草图、案例、图 motif 或原语。 |
| `proposal_distribution_interface` | 输入上下文后返回候选及 `π_o(c \mid x)` 的接口；无法给出精确概率时返回可审计近似和归一化方法。 |
| `expected_trace_effects` | 优化器候选若正确应改变的 trace 特征。 |
| `deterministic_validator` | 无模型随机性的语法、接口、安全和不变量检查。 |
| `fallback` | 优化器失败、超时或无候选时的下一优化器或返回路径。 |
| `provenance` | 实现、配置、版本和生成来源。 |
| `design_call_ids` | 若契约由 `RESIDUAL_SPECIALIST_DESIGN` 产生，保存全部设计调用；人工注册时为空。 |

#### `EvolutionContext`

| 字段 | 精确定义 |
| --- | --- |
| `frozen_parent_harness` | 不可修改的父版本快照。 |
| `task_and_environment` | 当前任务、split、模型、工具、权限、预算和 regime。 |
| `trace_batch` | 仅来自当前 $D_t^{\mathrm{trace}}$ 的同协议 `ExecutionTrace[]`。 |
| `case_need` | 由当前父代 trace、响应签名和已有失败边界形成的 `CaseNeed`。 |
| `diagnosed_failure_slices` | 可复现失败的最小 trace/代码切片及竞争解释。 |
| `retrieved_case_proposals` | 已迁移规划和校准的 `CaseProposal[]`。 |
| `retrieved_external_methods` | 案例不足时补充的外部方法束。 |
| `attempted_edits` | 当前谱系已尝试的规范化修改及结果，防止无意义重复。 |
| `preservation_requirements` | 必须保持的旧能力和安全谓词。 |
| `optimizer_history` | 各优化器曝光、反馈、信用、失败和转移记录。 |
| `regime_id` | 当前证据环境 ID。 |

#### `OptimizerProgram`

| 字段 | 精确定义 |
| --- | --- |
| `program_revision` | 当前父 Harness、EvolutionContext revision、registry revision 和路由策略共同确定的冻结程序 ID。 |
| `entry_optimizers` | 首轮可执行的优化器集合及初始概率。 |
| `transition_edges` | 四元组 `(optimizer_i,evidence_condition,routing_probability,optimizer_j)`；条件只依赖已观测证据，概率是在 guard 可选后选择该边的条件 propensity。 |
| `backup_edges` | 主优化器失败、超时或空提案时使用的确定性后备边。 |
| `disclosure_policy` | 每个优化器可读取的 trace、知识、历史和私有状态字段。 |
| `re_gate_triggers` | 需要重新执行契约/安全过滤的事件，例如 regime 变化或父版本改变。 |
| `stop_conditions` | 无剩余合法优化器、确定性风险不可接受或决策证据充分等程序终止谓词；外部资源中断返回 `Unresolved`，不能伪装成科学结论。 |
| `design_call_id` | 产生本程序语义结构的 `PORTFOLIO_PROGRAM_DESIGN` 调用；纯确定性 fallback 程序为 `NONE`。 |

#### `CandidateProposalIR`

三条候选生成通道和批评修订都进入相同的待核验表示：

| 字段 | 精确定义 |
| --- | --- |
| `ir_id` | 一次成功解析得到的不可变 ID；解析失败不创建。 |
| `source_call_id` | 直接生成该 IR 的 `LLMCallRecord`。 |
| `source_channel` | `CASE_GUIDED/METHOD_GUIDED/FREE/CRITIQUE_REVISION`。 |
| `strategy_revision` | 构造输入视图并触发调用的 optimizer revision。 |
| `parent_id` | 补丁必须应用的冻结父 Harness。 |
| `normalized_change` | 文件、配置、组件与控制关系的规范化语义编辑。 |
| `code_patch` | 可重放的精确代码和配置差异。 |
| `method_sources` | 使用的案例、方法和来源 revision；自由通道没有来源时为空。 |
| `expected_trace_effects` | 正确接入、激活、旁路和失败时预期出现的事件谓词。 |
| `preservation_requirements` | 必须保持的旧能力、接口、安全和终止条件。 |
| `unresolved_conditions` | 尚未确认的绑定、迁移、交互或激活条件及取证动作。 |
| `proposal_probability` | 当前策略路径内对该 IR 的条件概率或 `UNAVAILABLE`。 |
| `ancestor_ir_ids` | 批评修订所依赖的旧 IR；初次提案为空。 |
| `llm_call_ids` | 产生和修订该 IR 的全部调用。 |

#### `CandidateVersion`

| 字段 | 精确定义 |
| --- | --- |
| `candidate_id` | 冻结候选 ID。 |
| `ir_ids` | 归并到该候选的全部 `CandidateProposalIR`；至少一个。 |
| `parent_id` | 直接父 Harness ID。 |
| `normalized_change` | 与格式和无关重构解耦后的语义编辑 IR。 |
| `method_sources` | 使用的案例、方法和来源 revision。 |
| `source_optimizers` | 提出语义等价候选的全部优化器 revision。 |
| `optimizer_path` | 产生候选的 optimizer revisions、转移边、触发证据、中间产物和每步 routing propensity。 |
| `proposal_probabilities` | 每条来源优化器路径的选择 propensity、路径内局部选择概率和最终候选条件概率；无法取得时标为 `UNAVAILABLE`。 |
| `expected_trace_effects` | 候选预期改变的事件和方向。 |
| `unresolved_conditions` | 尚未验证的绑定、迁移和交互条件。 |
| `hard_gate_status` | 编译、接口、状态、权限、数据隔离、fallback、修改范围和父代不变量各自的 `PASS/FAIL/UNKNOWN`。 |
| `frozen_at` | 候选进入机制或收益评测前的冻结时间；之后修改必须创建新 ID。 |
| `llm_call_ids` | 产生、批评或修订该候选语义内容的全部调用。 |

#### `PortfolioCoverageGap`

| 字段 | 精确定义 |
| --- | --- |
| `gap_id` | 与父 Harness、CaseNeed revision 和本轮 program 绑定的唯一 ID。 |
| `uncovered_regions` | 没有优化器能合法覆盖的任务—失败—环境区域。 |
| `missing_observations` | 只因缺少可取得证据而仍在 waiting 的优化器输入。 |
| `hard_rejections` | 被接口、权限、安全、可编辑范围或方法形式硬拒绝的优化器及理由。 |
| `duplicate_only_paths` | 只能重复已尝试且无新条件的修改路径。 |
| `failure_hypotheses` | 经核验的跨路径失败解释；每项为 `{hypothesis_id,failure_layer,affected_path_ids,event_anchors,alternative_explanations,status}`。`failure_layer` 取 `CASE_COVERAGE/CONTRACT/TRANSFER/BINDING/SCHEMA/OBSERVATION/NO_LEGAL_ROUTE`；`affected_path_ids` 指向实际执行或等待路径；`event_anchors` 必须来自生成账本、gate 或策略状态；`alternative_explanations` 保留仍相容的解释；`status` 只由程序写为 `VERIFIED/REJECTED/UNKNOWN`。 |
| `cross_path_commonalities` | 多条失败路径共同缺少的输入、能力、接口、观察或适配条件；每项必须回指至少两条不同路径及相应事件。 |
| `uncertainties` | 现有事件无法区分的失败解释及可取得的判别观察；不得被折叠为硬拒绝。 |
| `candidate_remedies` | `RETRIEVE_CASE/REVEAL_OBSERVATION/RECONFIGURE_OPTIMIZER/CREATE_SPECIALIST/PROVE_NO_LEGAL_ROUTE`。 |
| `evidence_ids` | 形成缺口判断的 trace、CaseProposal、过滤和生成事件。 |
| `diagnosis_call_ids` | 产生跨路径语义解释的 `EMPTY_PORTFOLIO_DIAGNOSIS` 调用；空候选时至少包含一次已入账调用，调用失败时 gap 保持 `UNKNOWN`。 |

#### `GenerationLedger`

| 字段 | 精确定义 |
| --- | --- |
| `round_id` | 当前外层演化轮次。 |
| `program_revision` | 本次执行的冻结 `OptimizerProgram`。 |
| `optimizer_exposures` | 每个 optimizer revision 被调度的上下文、入口/转移概率、输入披露、中间状态和时间。 |
| `raw_proposals` | 未规范化提案、内部相对概率、预期机制和未决条件。 |
| `normalization_events` | 原提案到 `normalized_change` 的映射或失败原因。 |
| `dedup_groups` | 归并到同一 canonical candidate 的全部来源与概率。 |
| `deterministic_gate_events` | 语法、接口、安全、权限和修改范围检查。 |
| `coverage_gap` | 无合法候选时的 `PortfolioCoverageGap`，否则为 `NONE`。 |
| `llm_call_ids` | 程序设计、候选生成、批评修订和空组合诊断调用，包括失败与拒绝。 |

#### `OptimizationRoundLedger`

| 字段 | 精确定义 |
| --- | --- |
| `round_id` | 当前外层轮次。 |
| `parent_id` | 本轮唯一父 Harness。 |
| `trace_batch_ids` | 用于形成 CaseNeed 和候选的父代 trace IDs。 |
| `case_need_revisions` | 本轮初始及所有返回修订后的 CaseNeed。 |
| `case_retrieval_events` | 召回、过滤、迁移许可、校准和拒绝记录。 |
| `generation_ledgers` | 本轮每次优化器程序执行的 `GenerationLedger`。 |
| `candidate_ids` | 全部冻结 canonical candidate revisions。 |
| `evaluation_observations` | gate、父子配对、anchor 与其他取证事件。 |
| `account_updates` | 按 optimizer revision、regime 和信用层记录的更新及有效样本量。 |
| `regime_events` | regime 匹配、漂移怀疑、开启与冻结事件。 |
| `llm_call_ids` | round ledger 冻结前的需求、迁移、程序设计、候选生成、批评、空组合诊断、证据归因、动作与反思调用；第四阶段调用记录在实验级账本及其产生的长期 revision。 |
| `decision` | 当前决定及其证据；修订只能追加。 |

#### 测评与信用对象

##### `OptimizerAccount`

| 字段 | 精确定义 |
| --- | --- |
| `optimizer_revision` | 被计账的精确优化器版本。 |
| `regime_id` | 信用所属环境区间。 |
| `registration_status` | `PENDING/ACTIVE/DORMANT/RETIRED`；新 specialist 先为 `PENDING`，只有独立训练证据确认边际价值后才能 `ACTIVE`。 |
| `exposure_count` | 优化器获得生成机会的次数。 |
| `feedback_count` | 已收到可归因结果的次数。 |
| `feedback_debt` | `exposure_count-feedback_count` 经候选归并和延迟反馈修正后的待反馈量。 |
| `proposal_history` | 上下文、propensity、候选和时间的追加日志。 |
| `generation_credit` | 候选通过静态 gate 的信用。 |
| `activation_credit` | 候选成功激活目标机制的信用。 |
| `effect_credit` | 候选在配对评测中产生净收益的信用。 |
| `transition_credit` | 该优化器作为前序或后序步骤对整个路径的条件贡献。 |
| `credit_call_ids` | 对账户更新提出证据分层解释的调用；实际数值仍由程序规则写入。 |

##### `CanonicalCandidate`

| 字段 | 精确定义 |
| --- | --- |
| `normalized_change` | 去重键。 |
| `parent_id` | 去重只在同一父版本内进行。 |
| `source_optimizers` | 全部提案来源。 |
| `proposal_probabilities` | 各来源优化器路径及路径内步骤的 propensity，用于反事实或重要性修正。 |
| `evidence_ledger` | 该候选全部 gate 和运行证据。 |
| `status` | `FROZEN/ACTIVE/PROMOTED/REJECTED/RETIRED/UNRESOLVED`。 |
| `llm_call_ids` | 产生、批评、修订或解释该 canonical candidate 的全部调用。 |

##### `EvidenceObservation`

| 字段 | 精确定义 |
| --- | --- |
| `candidate_id`、`parent_id` | 子候选和配对父版本。 |
| `execution_trace_id` | 产生该观测的不可变 `ExecutionTrace.run_id`；纯静态 gate 时为 `NOT_APPLICABLE` 并保存 gate event ID。 |
| `task_instance` | 任务 ID、split 和输入特征。 |
| `split_role` | `trace/select/anchor/synthetic-probe`，决定该观测允许用于诊断、选择还是回归。 |
| `seed_and_environment` | 随机种子、容器、模型、工具和时间版本。 |
| `fidelity` | 任务覆盖、步数、重复、评测器和环境真实性向量。 |
| `selection_probability` | 本次候选—任务—保真度组合被调度的概率。 |
| `mechanism_events` | 激活、旁路、回退和失败事件。 |
| `outcomes` | 新能力、旧能力、失败、成本和稳定性原始指标。 |
| `hard_failures` | 任何安全、接口或数据隔离违规。 |
| `measured_cost` | token、费用、时延、工具和人工成本。 |

#### 长期对象

##### `LongTermState`

在外层 loop 中记为 $K_t$；$t$ 表示已经完成并提交的训练轮次数，而不是墙钟时间。

| 字段 | 定义 |
| --- | --- |
| `state_revision` | 长期状态 ID、唯一父 revision、提交轮次和提交状态。 |
| `immutable_run_ledger` | 不可变原始运行与选择 propensity。 |
| `conditional_case_memory` | 版本化条件案例及其关系。 |
| `optimizer_registry_and_accounts` | 优化器契约、实现、状态和分 regime 账户。 |
| `regime_history` | regime 创建、合并、拆分、怀疑和关闭记录。 |
| `llm_call_ledger_revision` | 当前状态可达的实验级调用账本 revision；所有派生对象的 call ID 必须存在于该账本。 |

##### `EvolutionCase`

| 字段 | 定义 |
| --- | --- |
| `case_revision` | 案例 ID 和修订号。 |
| `context_and_response_signature` | 任务、Harness、环境和固定 probe 响应。 |
| `retrieved_case_proposals` | 本轮使用和拒绝的迁移建议。 |
| `optimizer_program` | 实际执行的优化器图。 |
| `canonical_candidates` | 去重后的全部候选。 |
| `selected_actions_and_propensities` | 每次生成/测评动作及被选择概率。 |
| `mechanism_activation` | 候选机制激活证据。 |
| `paired_effects` | 父子配对效果。 |
| `regressions` | 旧能力和风险变化。 |
| `failed_transfer_conditions` | 击穿迁移许可的条件。 |
| `source_run_pointers` | 原始 trace、配置和结果定位。 |
| `evidence_regime` | 证据所属 regime。 |
| `llm_call_ids` | 形成该案例 revision 的来源、需求、迁移、候选、归因和关系修订调用。 |

### 公式逐项定义

#### 训练集轮次划分

$$
D_t^{\mathrm{trace}},D_t^{\mathrm{select}},D_t^{\mathrm{anchor}}
\subseteq D_{\mathrm{train}},
$$

$$
D_t^{\mathrm{trace}}\cap D_t^{\mathrm{select}}
=D_t^{\mathrm{trace}}\cap D_t^{\mathrm{anchor}}
=D_t^{\mathrm{select}}\cap D_t^{\mathrm{anchor}}
=\varnothing,
\qquad
D_{dev}^{(t)}=D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}.
$$

$t\in\{0,1,2,\ldots\}$ 是外层 Harness 演化轮次。三类角色由 `TrainProtocol.role_assignment_rule` 在看到本轮候选之前冻结。每轮可以只覆盖训练集的一部分，但固定点检查前必须完成 `task_strata` 规定的完整轮换。

#### 长期状态

$$
K_t=(\mathcal E_t,\mathcal C_t,\mathcal O_t,\mathcal G_t).
$$

$\mathcal E_t$ 是 `immutable_run_ledger`，$\mathcal C_t$ 是 `conditional_case_memory`，$\mathcal O_t$ 是 `optimizer_registry_and_accounts`，$\mathcal G_t$ 是 `regime_history`。$K_t$ 只在第四阶段原子提交；第三阶段产生的临时账户和 regime 更新在提交前属于本轮 ledger，不能被下一轮读取。

#### 案例检索与迁移分数

$$
S(c,q)=w_rR_{response}+w_pE_{probe}+w_gG_{generality}-w_aC_{adapt}-w_iR_{interaction}-w_uU_{transfer}.
$$

`c` 是来源案例，`q` 是当前 `CaseNeed`。`R_response` 是固定 probe 响应相似度；`E_probe` 是来源案例关键条件在目标 probe 中得到确认的比例；`G_generality` 是来源机制跨任务/环境有效的证据覆盖；`C_adapt` 是 `AdaptPlan` 的局部修改量和验证成本；`R_interaction` 是与现有机制冲突风险；`U_transfer` 是关键迁移条件未知比例。各项范围 `[0,1]`。权重非负；硬前提失败在评分前执行 `REJECT`。

#### 组合中新增优化器的残差价值

$$
J(o;P)=\sum_x w_x\max(0,V(P\oplus o,x)-V(P,x))-\lambda C(o)-\rho R(o).
$$

`o` 是待加入优化器；`P` 是现有优化器程序；`P⊕o` 是加入 `o` 后的程序；`x` 是开发任务—故障—环境区域；`w_x` 是该区域目标权重，和为 1；`V(P,x)` 是程序在区域 `x` 的期望终局效用；`C(o)` 是运行与集成成本；`R(o)` 是退化、冲突和不稳定风险；`λ,ρ≥0`。`max(0,·)` 只奖励填补残差，不让新优化器用已覆盖区域的退化抵消其他区域收益。

#### 多优化器路径的候选生成分布

$$
q(c\mid x)=\sum_{g\in\mathcal G(x)}p(g\mid x)\pi_g(c\mid x).
$$

`x` 是 `EvolutionContext` 的可观测摘要；$\mathcal G(x)$ 是当前 `OptimizerProgram` 中契约合法且 guard 可满足的全部终止路径，包括以 `NO_PROPOSAL`、fallback 失败或正常候选结束的路径；$p(g\mid x)$ 是调度器和条件转移共同选择路径 $g$ 的概率；$\pi_g(c\mid x)$ 是沿该路径执行后产生规范化候选 $c$ 的条件概率，其中 $c$ 的取值空间显式包含 `NO_PROPOSAL`；$q(c\mid x)$ 是候选的总体提案概率。多个路径提出同一候选时概率相加，候选只评测一次，信用仍按路径 propensity、中间状态和后续分层事件更新。

#### 案例保留价值

$$
V_{retain}(c)=\alpha G_{coverage}+\beta I_{boundary}+\gamma I_{decision}+\eta E_{independent}-\rho R_{redundancy}-\xi U_{unresolved}.
$$

`G_coverage` 是案例覆盖新区域或降低该区域适配成本的增益；`I_boundary` 是案例对成功/失败边界的收紧量；`I_decision` 是加入案例后优化器选择改变或决策损失下降；`E_independent` 是独立复核强度；`R_redundancy` 是相对现有案例的条件与证据冗余；`U_unresolved` 是关键未知比例。所有项归一到 `[0,1]`，权重非负。保护性反例即使均分低，只要 `I_boundary` 高也可保留。

### 信用更新规则

候选生成伪代码中的中间变量具有固定含义：`x` 是由 `EvolutionContext` 编译的可观测状态；`active` 是通过契约和安全过滤且当前可执行的优化器；`waiting` 是仅因缺少可取得观测而暂不可执行的优化器；`outcome_models` 是按生成、激活、效果和成本分层的条件结果模型；`program` 是本轮冻结的 `OptimizerProgram`；`proposals` 是尚未规范化的优化器原始提案；`candidates` 是去重并通过共同确定性 gate 的 `CandidateVersion[]`；`gap_request/gap_call/gap_diagnosis` 分别是空组合诊断视图、对应调用和未经核验的跨路径失败解释；`verified_gap_diagnosis` 是逐项绑定路径、事件和 gate 后的解释集合，只允许 `VERIFIED` 字段决定 `PortfolioCoverageGap.candidate_remedies`。`waiting` 中存在硬前提失败的优化器时应移入 rejected 集，而不是无限等待。

1. 候选未通过静态 gate，只更新 `generation_credit`。
2. 机制未激活，不更新 `effect_credit`，并记录适配或观测缺口。
3. 候选由多个优化器提出时，每个来源获得生成信用；效果信用使用 propensity 和候选归并关系分配。
4. stateful optimizer 的私有历史只在自身 revision 内更新；不能把 adviser 的共享反馈直接写入私有状态。
5. 延迟结果先增加 `feedback_debt`，结果到达后再结算；无结果不能按失败处理。
6. regime 改变时新建账户；旧账户只作为带折扣先验。

### 四阶段接口

| 阶段 | 输入 | 输出 | 硬要求 |
| --- | --- | --- | --- |
| loop 外离线案例组织 | `SourcePacket[]`、probe 与编译配置 | 来源抽取调用记录和固定 `CaseCatalogSnapshot` | 每个语义字段有来源/代码/执行锚点或显式未知，目录冻结。 |
| loop 内案例检索 | 当前父代 trace、`CaseNeed`、目录快照、`CaseMemoryView` | 需求诊断与迁移调用记录、`CaseProposal[]` | 硬拒绝不能被模型恢复；每个 proposal 有经核验适配计划和目标证据。 |
| 优化器程序生成 | `EvolutionContext`、registry | 程序设计/候选/批评调用记录；空候选时的跨路径失败综合；冻结候选、`GenerationLedger`、coverage gap | 所有策略先过契约与披露检查；等价候选只保留一份执行体；coverage gap 只接受有路径与事件锚点的解释。 |
| 竞赛与信用分配 | 父子候选、程序、账户、三类任务池 | 证据归因/动作/反思调用记录、决策、临时账户/regime 更新和 round ledger | 模型不直接写信用或晋级；选择概率、角色和保真度完整记录。 |
| 案例与组合积累 | 完整 round ledger、$K_t$ | 关系/specialist/regime 调用记录、$K_{t+1}$、索引和 pending 项 | 原始运行先提交；所有语义修订经锚点和独立证据核验。 |
| 外层训练 loop | $H_t$、$K_t$、训练调度器 | $H_{t+1}$、$K_{t+1}$ 或冻结系统 | 只有完整训练轮换达到固定点才 stop；测试集始终封闭。 |

### 复合字段、枚举与数值约定

| 对象 | 完整定义 |
| --- | --- |
| `AdaptPlan` | `{step_actions,slot_bindings,added_prerequisites,deleted_optional_steps,code_anchors,validation_actions,fallback,revision}`；`step_actions` 的值仅为 `KEEP/PARAMETERIZE/REPLACE/DELETE/ADD_PREREQ`，删除必需步骤非法。 |
| `ResponseSignature` | `{probe_suite_version,feature_schema,numeric_features,categorical_features,missing_mask,normalization_revision}`；两个签名只有 probe 与 schema revision 相同才可直接比较。 |
| `CreditLayer` | `{eligible_count,success_weight,total_weight,estimate,confidence_interval,last_updated}`；`generation/activation/effect/transition_credit` 均使用该结构，不是单个累计分。 |
| `RegimeRecord` | `{regime_id,parent_regime,valid_from,valid_to,change_evidence,model_versions,tool_versions,harness_interface,evaluator_version,task_distribution}`。 |
| `Fidelity` | `{task_fraction,step_limit,repetitions,evaluator_level,environment_level}`，各维归一到 `[0,1]`，不能先压成单一等级。 |
| `transfer_decision` | `DIRECT` 表示无需改机制步骤但仍需目标激活验证；`CALIBRATE` 表示必须先完成 `required_target_evidence`；`REJECT` 表示硬条件失败；`UNKNOWN` 表示可取得证据尚缺失。 |
| race action | `request-proposal`、`switch-optimizer`、`repair-binding`、`evaluate`、`add-discriminating-task`、`promote`、`retire`、`rollback` 或 `reopen-retrieval`；每次只执行一种真实动作。 |
| round decision | `Promote/Reject/Tie/ReturnOptimizerGeneration/ReturnCaseRetrieval/Continue/Unresolved`；前三者结束本轮，两个 return 回到本轮前序阶段，`Continue` 留在竞赛内部，`Unresolved` 要求补证或恢复运行。 |
| fixed point | 完整训练轮换上无晋级、无会改变检索或程序的案例/组合/regime 更新、无未结反馈债务、无能改变决定的合法实验；任一关键项未知时不成立。 |
| missing value | `UNAVAILABLE` 表示来源明确不存在该制品，`UNKNOWN` 表示尚未确认，`NOT_APPLICABLE` 表示字段对该对象无意义；三者不得互换。 |

所有指标在进入公式前统一为越大越好；指示函数把 `UNKNOWN` 视为未确认而不是 0；空分母使该项返回 `UNDEFINED`，候选转入校准，不以零填充。

### 公式各项的可计算定义

案例检索分数中的六项定义为

$$
R_{response}=\frac{\sum_f a_f m_f\,sim_f(s_c,s_q)}{\sum_f a_f m_f},\qquad
E_{probe}=\frac{\sum_j b_j\mathbf1[probe_j=PASS]}{\sum_j b_j},
$$

$$
G_{generality}=\min\left(1,\frac{\sum_{r\in Reg(c)}\zeta_r}{Z_{ref}}\right),\quad
C_{adapt}=\sum_k d_k\min(1,c_k/B_k),
$$

$$
R_{interaction}=\sum_h e_h r_h,\qquad
U_{transfer}=\frac{\sum_u g_u\mathbf1[u=UNKNOWN]}{\sum_u g_u}.
$$

这里 $s_c,s_q$ 是来源与目标 `ResponseSignature`；$m_f$ 表示两侧第 $f$ 个特征都已观测；$sim_f\in[0,1]$ 是数值特征的一减归一化距离或类别精确匹配；$a_f,b_j,\zeta_r,d_k,e_h,g_u\ge0$。$Reg(c)$ 是独立验证过案例机制的 regime 集，$Z_{ref}>0$ 是协议规定的饱和覆盖量。$c_k$ 与 $B_k>0$ 分别是适配代码量、运行量、人工量等成本及参考尺度，$\sum_kd_k=1$。$r_h$ 是状态写冲突、顺序冲突、资源冲突和语义冲突风险，$\sum_he_h=1$。检索权重 $w_r,w_p,w_g,w_a,w_i,w_u\ge0$，并固定 $w_r+w_p+w_g+w_a+w_i+w_u=1$；同分依次选择硬未知更少、适配成本更低、独立证据更多和稳定 ID 更小的案例。

残差价值公式中，$x\in\mathcal X_{dev}$ 是预先划分的开发任务—故障—环境区域，$w_x\ge0$ 且 $\sum_xw_x=1$；$V(P,x)=\mathbb E[U(Y)\mid P,x]$，$U(Y)\in[0,1]$ 是冻结的终局效用；$P\oplus o$ 只在契约兼容且转移图无环时有定义。$C(o),R(o)\in[0,1]$，$\lambda,\rho\ge0$。只有 $J(o;P)>\epsilon_J$ 才加入优化器，其中 $\epsilon_J\ge0$ 预先固定；并列选择风险、成本、反馈债务和稳定 ID 依次更小者。

候选混合分布实际作用于当前可执行优化器路径集合 $\mathcal G(x)$。若路径 $g=(o_1,\ldots,o_m)$，中间可观测状态依次为 $z_1,\ldots,z_{m-1}$，则：

$$
p(g\mid x)=p(o_1\mid x)
\prod_{j=2}^{m}p(o_j\mid x,o_{<j},z_{<j}),
$$

$$
q(c\mid x)=\sum_{g\in\mathcal G(x)}p(g\mid x)\pi_g(c\mid x),\quad
\sum_{g\in\mathcal G(x)}p(g\mid x)=1,\quad
\sum_c\pi_g(c\mid x)=1.
$$

$o_j$ 是路径第 $j$ 个 optimizer revision；$o_{<j}$ 是此前优化器序列；$z_{<j}$ 是此前诊断、草图、patch、批评或 gate 等实际中间证据。$p(o_1\mid x)$ 是入口优化器选择概率，$p(o_j\mid x,o_{<j},z_{<j})$ 是满足转移 guard 后选择下一优化器的条件概率；备份边、停止事件和空提案路径也必须计入路径概率，因此 $\mathcal G(x)$ 覆盖全部终止质量。$\pi_g(c\mid x)$ 是整条路径在包含 `NO_PROPOSAL` 的规范化候选空间上的最终提案概率。确定性路径对唯一输出赋值 1，不能事后丢弃无输出质量再重归一化。若任一步概率为 `UNAVAILABLE`，该路径只能做实际使用归因，不能参与无偏 propensity 校正。

案例保留式中六个特征均在 `[0,1]`：$G_{coverage}$ 是加入案例后新覆盖区域的目标质量；$I_{boundary}$ 是正负边界经验风险下降；$I_{decision}$ 是保留该案例导致的决策损失下降；$E_{independent}$ 是独立 regime 复核覆盖；$R_{redundancy}$ 是相对已有案例的最大条件—机制—证据重合；$U_{unresolved}$ 是关键未知权重比例。$\alpha,\beta,\gamma,\eta,\rho,\xi\ge0$ 且和为 1；保留阈值 $\epsilon_{retain}$、保护性反例阈值 $\epsilon_{boundary}$ 和并列规则在沉淀前冻结。

### 伪代码算子契约

| 组织与检索算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `OFFLINE_COMPILE_CASE_CATALOG` | 固定来源包 → `CaseCatalogSnapshot`；来源、probe schema 或编译配置改变均产生新快照。 |
| `ONLINE_RETRIEVE_CONDITIONAL_CASES` | 固定目录、当前 `CaseMemoryView`、`CaseNeed` → 带许可的 `CaseProposal[]`；不修改 Harness。 |
| `FIX_CASE_SOURCE_UNITS` / `BUILD_SOURCE_CASE_EXTRACTION_REQUESTS` | 来源包 → 不可变论文、代码、配置、测试与结果单元 → `SOURCE_CASE_SEMANTIC_EXTRACTION` 最小视图。 |
| `PARSE_SOURCE_CASE_PROPOSALS` / `VERIFY_SOURCE_CASE_FIELDS` | 模型输出、来源单元 → 待核验语义字段 → 锚点、实验单元、代码差分与结果归属合格字段；失败字段保持未知。 |
| `SPLIT_ALIGN_AND_COMPILE_INTERVENTION_CASES` | 来源包、经核验语义字段 → 原子条件案例；论文—代码无法对齐字段保留 `paper_only/code_only`。 |
| `ADD_FIXED_PROBE_SIGNATURES_AND_CHANGE_SLOTS` | 案例、固定 probe schema → 响应签名与环境变化槽；不可测特征写 `UNKNOWN`。 |
| `BUILD_CASE_MULTIVIEW_INDEXES` | 案例 revisions → 响应、条件、机制、代码、证据索引；索引可由权威案例重建。 |
| `FREEZE_CASE_CATALOG` | 来源、外部案例、索引 → 只读目录快照；字段不完整时阻止进入在线 loop。 |
| `MERGE_CASE_RETRIEVAL_VIEWS` | 目录索引、按需长期视图 → 当前查询的逻辑联合索引；不改写两侧权威对象。 |
| `ASYMMETRIC_RESPONSE_RECALL` | 索引、目标 need → 高召回案例；目标未知特征不当作失配。 |
| `HARD_COVERAGE_AND_PRECONDITION_FILTER` | 召回集、need → 满足硬覆盖与前提者；`FALSE` 删除、`UNKNOWN` 转校准。 |
| `BUILD_TARGET_CASE_NEED_VIEW` / `PARSE_TARGET_CASE_NEED_PROPOSAL` | 父代、trace、可见边界与协议 → `TARGET_CASE_NEED_DIAGNOSIS` 视图 → 竞争故障解释和目标需求。 |
| `VERIFY_CASE_NEED_TRACE_CODE_AND_REGIME_ANCHORS` | 需求提案与输入视图 → trace、代码、响应特征和 regime 均可回溯的 `CaseNeed`。 |
| `BUILD_CASE_TRANSFER_ADAPTATION_REQUEST` / `PARSE_CASE_TRANSFER_ADAPTATION_PROPOSALS` | 硬过滤案例、need → `CASE_TRANSFER_AND_ADAPTATION_PROPOSAL` 视图 → 逐步骤迁移与适配提案。 |
| `VERIFY_AND_COMPILE_ADAPTATION_PLANS` | 适配提案、来源案例和目标 need → 锚点、动作、权限和机制顺序合格的 `AdaptPlan[]`。 |
| `EMPIRICAL_TRANSFER_GATE` | 适配计划、来源/目标证据 → `DIRECT/CALIBRATE/REJECT/UNKNOWN`；不得由文本相似度授权。 |
| `TARGET_PROBE_CALIBRATION` | 待校准提案、仅来自 trace 角色或合成输入的目标 probes → 更新许可与预测；缺测保留未知，不读取 select/test。 |
| `ADAPTATION_VALUE_RERANK` | 校准提案、$S(c,q)$ → 确定排序；硬拒绝项不参与打分。 |

| 候选生成算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `GENERATE_WITH_CONDITIONAL_OPTIMIZER_PROGRAM` | `EvolutionContext`、registry → 冻结候选、程序、`GenerationLedger` 与可选 coverage gap。 |
| `TRACE_CONDITIONED_EVOLUTION_STATE` | context → 只含可观测字段的状态 $x$；不得含测试答案。 |
| `CONTRACT_AND_SAFETY_FILTER` | registry、$x$ → `active,waiting,rejected`；未知可取得时 waiting，硬失败 rejected。 |
| `ESTIMATE_LAYERED_OPTIMIZER_OUTCOMES` | active、历史账户 → 生成/激活/效果/成本条件模型及不确定度。 |
| `BUILD_PORTFOLIO_PROGRAM_REQUEST` / `PARSE_PORTFOLIO_PROGRAM_PROPOSAL` | 当前状态、active/waiting、结果模型与转移信用 → `PORTFOLIO_PROGRAM_DESIGN` 视图 → 入口、转移、guard、中间 schema 与 fallback 提案。 |
| `VERIFY_AND_BUILD_RESIDUAL_COMPLEMENTARY_PROGRAM` | 程序提案、契约、结果模型与转移信用 → 带 propensity 的无环 `OptimizerProgram`；只保留 schema/权限兼容且增加残差覆盖的边。 |
| `EXECUTABLE_FRONTIER` | 程序、已观测证据 → 当前 guard 为真的优化器集合。 |
| `APPLY_DISCLOSURE_POLICY` | 优化器、$x$ → 允许读取的不可变 view；私有状态不串用。 |
| `CANDIDATE_CALL_TYPE` | optimizer revision → `CASE_GUIDED_CANDIDATE_PROPOSAL/METHOD_GUIDED_CANDIDATE_PROPOSAL/FREE_CANDIDATE_PROPOSAL`；契约未注册对应类型则拒绝执行。 |
| `CALL_OPTIMIZER_LLM` | 最小权限视图、call type 与冻结配置 → 原始响应及 `LLMCallRecord`；请求、失败、解析和核验状态追加到 `LLMCallLedger`。 |
| `PARSE_CANDIDATE_PROPOSALS` | 原始响应、策略输出 schema → `CandidateProposalIR[]` 或解析失败；解析器不得补写模型未输出的编辑。 |
| `BUILD_CANDIDATE_CRITIQUE_VIEW` / `PARSE_AND_VERIFY_CANDIDATE_REVISIONS` | IR、触发策略和状态 → `CANDIDATE_CRITIQUE_AND_REVISION` 视图 → 锚点、最小编辑和保持条件合格的新 IR revision。 |
| `NORMALIZE_TO_SHARED_CANDIDATE_IR` | 原始提案 → `normalized_change`；无法规范化者拒绝。 |
| `EXACT_DEDUP_AND_ATTACH_ALL_SOURCES` | IR 候选 → canonical candidates；同父版本等价项只执行一次。 |
| `COMMON_DETERMINISTIC_GATE` | canonical candidates → 通过语法、接口、安全和不变量者。 |
| `FREEZE` | 候选及父版本 → 不可变 `CandidateVersion[]`；字段改变生成新 ID。 |
| `GENERATION_LEDGER` | 全部原始提案与 gate → 带 propensity 的追加日志。 |
| `BUILD_EMPTY_PORTFOLIO_DIAGNOSIS_REQUEST` | 当前状态、程序、active/waiting/rejected 策略和完整生成日志 → 只披露实际路径、中间产物、等待原因、拒绝事件与重复修改的空组合诊断视图。 |
| `PARSE_EMPTY_PORTFOLIO_DIAGNOSIS` | 诊断调用 → 路径失败假设、失败层级、共同缺口、判别事件、缺失观察、补救方向和未知项草案；路由决定和“父代最优”声明被丢弃。 |
| `VERIFY_EMPTY_PORTFOLIO_DIAGNOSIS` | 诊断草案、当前状态、程序、策略集合和生成日志 → 逐项带 `VERIFIED/REJECTED/UNKNOWN` 的失败解释；检查路径、事件、gate、时间和数据披露锚点。 |
| `BUILD_PORTFOLIO_COVERAGE_GAP` | 当前状态、active/waiting/rejected 策略、生成日志和经核验空组合诊断 → 区分缺观察、硬拒绝、重复路径及跨路径语义缺口的 `PortfolioCoverageGap`；补救路由只从经核验字段和固定规则编译。 |

| 测评与信用算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `PLAN_TEST_AND_CREDIT` | 父版本、候选、程序、生成日志、coverage gap、三类任务池、账户、只读既有 ledger、regimes → 决策、增量 eval ledger 及临时更新。 |
| `ROUTE_PORTFOLIO_COVERAGE_GAP` | coverage gap、程序、生成日志 → `ReturnOptimizerGeneration/ReturnCaseRetrieval/Reject/Unresolved`。 |
| `MATCH_OR_OPEN_REGIME` | 当前环境、历史 → 匹配 regime 或新建记录；疑似漂移不强行复用信用。 |
| `HYBRID_ADVISER_STATEFUL_MASTER` | 候选、当前账户 → race schedule；共享 adviser 与私有 stateful 状态隔离。 |
| `RUN_COMMON_GATES` | 候选、trace pool 或合成 probe → 确定性及机制激活 `EvidenceObservation`；不得产生独立收益结论。 |
| `BUILD_PORTFOLIO_EVIDENCE_REQUEST` / `PARSE_PORTFOLIO_EVIDENCE_ATTRIBUTION` | 候选、程序、真实观察、生成账本与账户 → `PORTFOLIO_EVIDENCE_ATTRIBUTION` 视图 → 分层支持/反对/未知及责任路径提案。 |
| `VERIFY_EVIDENCE_PATH_AND_PROPENSITY_ANCHORS` | 归因提案、候选、程序和观察 → 事件、路径、中间产物及 propensity 可回溯的归因。 |
| `APPEND` | ledger、事件 → 新 revision；重复 ID 拒绝，纠错以 supersede 追加。 |
| `LAYERED_CREDIT_UPDATE` | 候选/动作、证据、经核验归因和账户 → 由程序规则更新分层信用；未激活不得更新效果信用。 |
| `PAIRED_PROMOTION_DECISION` | 父子配对证据、保留约束 → promote/reject/tie/continue。 |
| `ENUMERATE_LEGAL_RACE_ACTIONS` | 父代、候选、schedule 与 ledger → 满足权限、数据角色和冻结规则的程序动作。 |
| `BUILD_NEXT_RACE_ACTION_REQUEST` / `PARSE_NEXT_RACE_ACTION_PROPOSALS` | 候选、程序动作、证据和账户 → `NEXT_RACE_ACTION_PROPOSAL` 视图 → 动作排序或参数完整的新动作。 |
| `VERIFY_AND_COMPILE_RACE_ACTIONS` / `SELECT_DECISION_RELEVANT_RACE_ACTION` | 动作提案和证据 → 合法动作集 → 能改变当前决定的唯一动作并记录选择概率。 |
| `BUILD_PORTFOLIO_STALL_REFLECTION_REQUEST` / `PARSE_PORTFOLIO_STALL_REFLECTION` | 停滞候选、程序、证据、coverage gap 与账户 → `PORTFOLIO_STALL_REFLECTION` 视图 → 策略/迁移/probe/regime 修订提案。 |
| `VERIFY_AND_COMPILE_PORTFOLIO_RETURN` | 停滞反思、证据 → 合法的前序阶段 return 或无效；不能直接产生 `Tie`。 |
| `COMPLETE_FROZEN_DEVELOPMENT_PANEL_ACTION` | 父代、候选、未暴露 select/anchor 与证据 → 尚未执行且能改变决定的冻结评测动作，或 `NONE`。 |
| `RETURN_EVIDENCE_IS_GENERATION_SAFE` | 拟返回动作、当前证据 → bool；仅当支撑返回的证据不含已披露 select 结果时为 true。 |
| `RETURN_TO_CASE_RETRIEVAL` | 缺失迁移证据 → 重新组织检索请求；仅为流程返回，不是成功。 |
| `RETURN_TO_OPTIMIZER_GENERATION` | 新优化器路径请求 → 新候选生成上下文；旧候选保持冻结。 |
| `EXECUTE_MATCHED_EVALUATION` | action、父版本、冻结 select/anchor pools → 同任务同种子配对 observation；失败也入账。 |
| `MULTISCALE_REPLAY_DETECTS_SHIFT` | 多窗口 replay 统计、regime → bool 与变化证据；阈值预注册。 |
| `MARK_REGIME_SHIFT_SUSPECTED_AND_FREEZE_LOCAL_CREDIT` | 当前 regime 与变化信号 → 本轮临时 `SHIFT_SUSPECTED` 状态并冻结局部信用更新；是否创建新 regime 留给第四阶段核验。 |

| 沉淀算子 | 输入 → 输出；失败语义 |
| --- | --- |
| `RETAIN_CASES_AND_EXTEND_OPTIMIZERS` | 长期状态、完整 run ledger 与实验级 `LLMCallLedger` → 带调用账本 revision 的新状态与索引。 |
| `CURRENT_LEDGER_REVISION` | 当前追加写调用账本 → 覆盖截至本次提交全部成功、失败和拒绝调用的不可变 revision ID。 |
| `APPEND_COMPLETE_RUN` | 旧长期状态、临时 round ledger → 已追加原始证据的状态与不可变运行；字段缺失返回 `INCOMPLETE_RUN`。 |
| `COPY_ON_WRITE` | 已追加原始证据的状态 → 供派生修订使用的影子状态；失败不影响原始运行。 |
| `DERIVE_CONDITIONAL_EVOLUTION_CASE` | 完整运行 → `EvolutionCase`；推导项保留原始指针。 |
| `BUILD_CASE_RELATION_REVISION_REQUEST` / `PARSE_CASE_RELATION_REVISION_PROPOSALS` | 新案例、案例 memory 与完整运行 → `CASE_RELATION_AND_REVISION_PROPOSAL` 视图 → 支持、边界、冲突、冗余或分裂提案。 |
| `VERIFY_CASE_RELATIONS_AND_REVISIONS` | 关系提案、新旧案例和完整运行 → 来源、条件、机制、regime、propensity 与运行证据合格的关系。 |
| `VERSIONED_REVISE_WITHOUT_OVERWRITE` | memory、新案例、关系 → 新 revision；旧案例不覆盖。 |
| `UPDATE_PROTOTYPE_BOUNDARY_COMPETENCE` | 案例 memory → 原型、边界和覆盖统计；均可重建。 |
| `FIND_PORTFOLIO_COVERAGE_GAPS` | registry/accounts、案例分布 → 未覆盖区域及目标质量。 |
| `BUILD_RESIDUAL_SPECIALIST_REQUEST` / `PARSE_RESIDUAL_SPECIALIST_PROPOSALS` | coverage gaps 与 registry → `RESIDUAL_SPECIALIST_DESIGN` 视图 → 新策略契约提案。 |
| `VERIFY_AND_COMPILE_SPECIALIST_CONTRACTS` | specialist 提案、确认缺口 → 调用策略、工具权限、行动空间、fallback 与反驳条件完整的 `OptimizerContract` 草案。 |
| `COLD_START_AND_VALIDATE` | 新 specialist、registry、案例 memory、当前完整运行 → 隔离的 `PENDING` 账户与验证计划；当前残差证据只允许做接口/gate 检查，边际效果必须在后续未暴露训练任务上确认后才转为 active。 |
| `BUILD_REGIME_SHIFT_INTERPRETATION_REQUEST` / `PARSE_REGIME_SHIFT_INTERPRETATION` | 多尺度变化信号、历史和完整运行 → `REGIME_SHIFT_INTERPRETATION` 视图 → 变化层级、原因、继承/重置字段与确认回放提案。 |
| `VERIFY_REGIME_SHIFT_INTERPRETATION` / `OPEN_NEW_REGIME` | 解释提案、统计信号和版本/回放证据 → 经核验变化或未知 → 新 regime record；模型解释不能单独触发分裂。 |
| `LONG_TERM_INVARIANTS_HOLD` | 影子状态 → bool 或 pending；检查来源可达、账户隔离、propensity、regime 与无测试泄漏。 |
| `ATOMIC_COMMIT_LONG_TERM_STATE` | 通过不变量的影子状态 → 新 $K_{t+1}$；失败不发布派生 revision。 |
| `REBUILD_CASE_AND_OPTIMIZER_INDEXES` | 权威长期对象 → 派生索引；不把索引当证据源。 |
| `EVOLVE_WITH_CONDITIONAL_PORTFOLIO_ON_TRAIN` | 初始 Harness、长期状态、固定目录、训练集、协议 → stop 后冻结的系统。 |
| `INIT_TRAIN_SCHEDULER` / `ASSIGN_TRAIN_ROLES` | 训练集与协议 → 可审计调度器 → 本轮 trace/select/anchor pools。 |
| `INIT_LLM_CALL_LEDGER` / `UPDATE_EXPOSURE_FROM_LLM_CALLS` | 冻结协议 → 追加写调用账本；调用账本、候选或长期 revisions 与任务池 → 实际披露字段、受影响对象及独立性状态。 |
| `LONG_TERM_REVISIONS_CREATED` | 前后 $K_t$ → 本轮新建或修订的案例、策略、账户和 regime ID；pending/失败派生保留其审核记录 ID。 |
| `REFRESH_INDEPENDENT_DEVELOPMENT_POOLS` | 调用披露历史、受影响候选和旧 select/anchor pools → 删除已影响候选修订的任务并按冻结分层规则补入未披露训练任务；无法补足时返回 `Unresolved`。 |
| `RUN_HARNESS` | 冻结 Harness、任务池、协议 → `ExecutionTrace[]`；失败运行同样产生终止事件。 |
| `BUILD_CASE_NEED` / `REVISE_CASE_NEED` | 当前父代、trace、长期边界或 generation-safe 返回证据 → 经 `TARGET_CASE_NEED_DIAGNOSIS` 提议并由 trace/代码/regime 锚点核验的 `CaseNeed` revision。 |
| `RETRIEVE_CASE_MEMORY_VIEW` | $K_t$、need、协议时间边界 → `CaseMemoryView`。 |
| `BUILD_EVOLUTION_CONTEXT` | 父代、trace、need、proposals、长期状态和可选返回证据 → 字段可见性受控的 `EvolutionContext`。 |
| `PORTFOLIO_STATE` | $K_t$ → 当前 optimizer accounts 与 regime history 的只读工作副本。 |
| `INIT_OPTIMIZATION_ROUND_LEDGER` | 轮次、父代、trace、need、proposals → 本轮只追加 ledger。 |
| `REVISE_CONTEXT_FROM_PORTFOLIO_RETURN` | 旧 context、generation-safe 竞赛证据、账户 → 新 context revision；不读取 select 结果，不修改旧候选。 |
| `FINALIZE_OPTIMIZATION_ROUND_LEDGER` | 本轮 ledger、终止决定、账户、regimes → 可提交的完整运行或 `INCOMPLETE_RUN`。 |
| `PAUSE_INCOMPLETE_EVOLUTION` | 当前 Harness、长期状态、本轮 ledger、调度器 → 可恢复检查点；不运行测试、不产生 stop 结论。 |
| `ACCEPT_IF_PROMOTED` | 父代、冻结候选、决定 → 获胜候选或原父代。 |
| `UPDATE_TRAIN_SCHEDULER` | 本轮角色、决定、ledger、新状态 → exposure、覆盖、anchors、反馈债务和未决证据。 |
| `CONDITIONAL_PORTFOLIO_FIXED_POINT` | 调度器、前后 Harness、前后长期状态、ledger → stop bool 或 `UNKNOWN`。 |
| `FREEZE_CONDITIONAL_PORTFOLIO_FOR_FINAL_TEST` | 最终 Harness、长期状态、目录与协议 → 不再可写的测试输入快照。 |

局部变量 `source_units/extraction_requests/extraction_calls/extraction_proposals/verified_fields/cases/indexes` 依次表示不可变来源单元、来源案例抽取请求及调用、未核验语义字段、经核验字段、编译案例和派生索引。`need_view/need_call/need_proposal/need/recalled/eligible/adaptation_request/adaptation_call/adaptation_proposals/plans/licensed/calibrated` 是目标需求视图及调用、需求提案与经核验 revision、初召回、硬过滤结果、迁移适配调用链、合法适配计划、迁移许可和目标校准结果。

`active/waiting/rejected/outcome_models/program_request/program_call/program_proposal/program/proposals/candidates/coverage_gap` 是可执行、等待或硬拒绝策略、分层结果模型、程序设计调用链、经核验程序、原始提案、共享候选和组合覆盖缺口。`proposal_call/path_proposals/critique_view/critique_call/revisions` 是某一策略的候选调用、解析 IR、批评视图及调用和经核验新 revisions；`gap_request/gap_call/gap_diagnosis/verified_gap_diagnosis` 是空组合诊断视图、调用、原始解释及经路径和事件核验的解释。任一模型输出在对应核验器通过前均不是程序、候选、缺口或证据事实。

`r/schedule/e/attribution_request/attribution_call/attribution/program_actions/action_request/action_call/action_proposals/actions/action/reflection_request/reflection_call/reflection/return_request` 依次表示当前 regime、竞赛日程、真实证据、证据归因调用链、程序动作、下一动作调用链、合法动作集与唯一动作、停滞反思调用链和经核验前序返回。`result_attribution_*` 对动作执行结果执行同一归因协议。

`raw_state/shadow/immutable_run/new_case/relation_request/relation_call/relation_proposals/relations/residual_regions/specialist_request/specialist_call/specialist_proposals/new_optimizers/shift_signal/shift_request/shift_call/shift_proposal/verified_shift` 是已追加原始证据的状态、派生影子状态、冻结运行、派生案例、案例关系调用链、组合缺口、specialist 调用链、待验证策略、变化信号与 regime 解释调用链。`scheduler/llm_call_ledger/trace_pool/select_pool/anchor_pool/trace_batch/case_view/context/round_ledger` 是训练调度器、实验级调用账本、三类任务角色、父代 trace、按需案例视图、生成上下文和本轮总账。

兼容枚举 `request-proposal / switch-optimizer / repair-binding / evaluate / add-discriminating-task / promote / retire / rollback / reopen-retrieval` 与前述 race action 九个值一一对应，不产生额外动作类型。

### 不变量

1. 案例检索不能只用任务文本相似度。
2. `DIRECT` 仍需目标机制激活证据；只有适配步骤可以省略。
3. 选择器、生成器、验证器和接受器保持独立接口。
4. 多来源等价候选只运行一次，但所有来源和概率永久保留。
5. 测试集不参与优化器信用、case scope 或 regime 判断。
6. 任何信用均带 optimizer revision 和 regime，禁止跨版本无条件累加。
7. 同一运行不能同时用于生成当前候选和估计该候选的独立收益。
8. 外部案例目录在一次 benchmark 演化中只读；在线案例与优化器状态只能写入版本化 $K_t$。
9. 缺少 propensity 的运行可以保留原始证据，但不能伪装成可做无偏重要性校正的样本。
10. 未结反馈债务、未解决迁移条件、`INCOMPLETE_RUN` 或能改变决定的合法动作存在时，外层 loop 不得 stop。
11. stop 后测试 trace 永不回写案例、账户、regime、选择器或训练调度器。
12. 任一 select 结果披露后，本轮不得返回案例检索或优化器生成；该结果只能在下一轮成为生成证据。
13. 任一 `OptimizerLLM` 输出进入目录、需求、适配计划、策略程序、候选、信用归因、竞赛动作或长期状态前，必须通过对应 parser、来源/代码/trace 锚点、权限和规则核验。
14. `OptimizerLLM` 的语言置信度不得直接写入检索分数、路径 propensity、信用估计、父子收益、晋级统计或 regime 变化阈值。
15. 空候选集合必须经过跨路径诊断；`OptimizerLLM` 只能提出失败解释和补救方向，不能据此宣称父代最优、直接选择路由或跳过后续固定规则。
15. 任一 select/anchor 任务一旦通过模型调用影响候选修订或策略程序返回，便对相应候选及后代失去独立选择资格；影响长期案例、策略或 regime revision 的任务也必须记录对应披露关系。
