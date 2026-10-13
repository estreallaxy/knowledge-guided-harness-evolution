# 主动实验驱动的假设空间演化：完整详细版

## 一、完整 Method

多数 Harness 搜索把每个候选版本视为一个孤立方案，用若干任务上的总分决定保留或淘汰。这样的测评能回答“这次谁更好”，却很难回答“哪个机制假设被支持、哪个接入条件不成立、下一次运行最应区分什么”。候选被淘汰后，其结构和失败边界往往随之丢失；相近修改又会以新名字反复出现。结果是大量运行只服务于局部排序，不能系统缩小后续搜索空间，也难以把一次任务上的经验迁移为可复用知识。

为解决这一问题，本路线把 Harness 演化提升为对结构化假设空间的主动实验过程。外部方法和自主发现的修改都被表示为具有前提、预测、typed holes 和特化关系的可执行干预假设；一般机制、参数化方案、具体绑定和已验证实例共同构成一个随证据变化的假设空间。一次运行的价值不仅取决于分数，还取决于它能否区分竞争解释、排除一片不成立的空间，或明确某种干预在何种条件下有效。

具体而言，loop 外先把论文方法编译为有限干预语法和可审计的特化图。每一轮从父 Harness 的训练 trace 构造待改变与待保持的义务，`OptimizerLLM` 在当前活跃假设空间内补全知识候选，并保留不受目录限制的自由候选；`OptimizerHarness` 负责类型、权限、状态和依赖约束。随后系统主动选择最能分裂当前假设空间的 witness experiment，根据接入、激活、效果和回归证据，对假设执行保留、排除、特化、拆分或重新抽象，形成“维护假设空间—选择判别实验—获取 witness—更新空间—生成下一代 Harness”的闭环。

外部假设目录与 benchmark 演化分属两个时间范围。实验开始前冻结来源、有限语法、特化关系、benchmark、执行环境、评测器和停止规则；在线阶段只允许训练集证据推动 H₀ → H₁ → H₂ → … 并更新独立经验层。来源事实保持只读，封存测试集只在最终版本冻结后使用。

### 干预假设组织与检索阶段：如何组织和检索外部方法

论文中的一个方法往往同时包含一般控制机制、具体实现选择和实验条件。若直接保存成摘要，检索器无法判断它是否能接入当前 Harness；若直接把代码片段当成方法，又会把同一机制的不同实现视为无关条目。本阶段把来源事实、一般机制和具体绑定分层保存，并用严格的特化偏序连接它们。它包含两个时间上分离的动作：loop 外的组织只执行一次并冻结目录快照；loop 内的检索在每一代 trace 义务形成后执行，只从冻结目录与截至该代可见的经验 revision 中构造可绑定子图。检索的目标不是找到主题相似的论文，而是在当前 Harness 的接口和 trace 义务下找到仍可执行、仍未被反证的干预假设。

来源材料中的机制步骤、生命周期 hook、可调槽、预测中介和适用条件不能仅靠静态解析恢复。离线时，`OptimizerHarness` 先固定论文段落、代码符号、配置、测试和结果锚点，再用 `SOURCE_INTERVENTION_SEMANTIC_COMPILATION` 请求 `OptimizerLLM` 提出有限语法程序、typed holes、预测链和候选特化关系；程序核验来源、控制顺序、类型、状态 effect 与执行证据。在线时，当前父 Harness 的训练 trace 通过 `TRACE_OBLIGATION_AND_NEED_DIAGNOSIS` 形成竞争故障解释、需要改变/保持的 trace 义务和 `InterventionNeed`；硬可达性过滤与依赖闭包由程序完成；`VERSION_SPACE_SEMANTIC_RERANK` 只在剩余子图中比较机制匹配、迁移缺口和反驳 witness。模型不能恢复硬不可达节点、删除必要依赖或把语义相似当作特化关系。

原始材料保存为：

```text
SourcePacket = {
  paper_version,
  official_code_version,
  exact_source_anchors,
  configs_and_examples,
  tests_and_reported_results
}
```

每个可执行方法节点表示为：

```text
InterventionHypothesis = {
  hypothesis_id,
  node_kind,
  grammar_program,
  typed_holes,
  binding_constraints,
  applicability_scope,
  predicted_activation,
  predicted_mediators,
  predicted_target_effect,
  predicted_regressions,
  fallback,
  provenance,
  support_witnesses,
  contradict_witnesses,
  unresolved_witnesses,
  status,
  revision,
  llm_call_ids,
  field_validation_status
}
```

`grammar_program` 只允许使用有限的 Harness 干预语法：

```text
Intervention := Trigger
                -> Guard
                -> ReadState*
                -> Transform+
                -> Validate*
                -> Commit
                -> Fallback?
```

每个操作都声明输入输出类型、允许读写的状态、生命周期 hook、工具权限和外部副作用。论文没有给出的绑定保持为 `typed_hole`，不能由整理过程静默补成来源事实。

**特化偏序。** 令 $\nu_i\preceq\nu_j$ 表示 $\nu_i$ 是 $\nu_j$ 的更具体假设，当且仅当：

1. $\nu_i$ 的 `grammar_program` 可以由 $\nu_j$ 填孔或添加不改变既有顺序的约束得到；
2. $\nu_i$ 的绑定域是 $\nu_j$ 允许绑定域的子集；
3. $a_i(z)\Rightarrow a_j(z)$，其中 $a(z)$ 是可检查的适用条件；
4. $\nu_i$ 的预测没有与 $\nu_j$ 的必然预测冲突；
5. 两者的来源和推导路径均可回溯。

该偏序把“具体补丁—参数化干预—一般机制”连接起来，但不表示一般节点比具体节点更正确。

当前检索请求表示为：

```text
InterventionNeed = {
  obligations,
  available_hooks,
  available_state_and_tools,
  immutable_constraints,
  forbidden_effects,
  current_regime,
  unresolved_conditions,
  source_call_id,
  validation_record_ids
}
```

**算法 1A：loop 外来源组织。**

1. `OptimizerHarness` 对齐论文段落、算法步骤、官方代码符号、配置、测试与报告结果，建立不可变来源单元；尚未对应的材料保留原位置。
2. 对每个来源单元发起 `SOURCE_INTERVENTION_SEMANTIC_COMPILATION`。`OptimizerLLM` 提出机制步骤、有限语法操作、生命周期 hook、typed holes、绑定约束、预测激活—中介—效果链、fallback、适用条件和候选关系，并逐字段引用来源与相反证据。
3. 程序核验来源锚点、代码差分、控制顺序、类型、状态 effect 和执行路径；无法对齐或无法确认的声明标记为 `paper_only`、`code_only` 或 `UNKNOWN`，不能因模型解释合理而通过。
4. 将经核验字段编译为有限语法中的最具体节点；每个未确定接口形成带类型的孔。
5. 仅对控制顺序、类型、状态效应和目标机制兼容的具体节点执行 anti-unification，产生候选父节点；模型只建议值得比较的节点组，不建立等价事实。
6. 若父节点可以重新实例化全部子节点，且公共抽象降低总描述长度，则加入偏序图；否则保留为平行节点。
7. 建立 `SPECIALIZES / REQUIRES / CONFLICTS / ALTERNATIVE_TO / DERIVED_FROM / SUPERSEDES` 关系。关系必须携带来源或运行 witness。
8. 为触发条件、生命周期 hook、状态效应、预测 trace、适用条件和来源证据分别建立索引，审计通过后冻结为 `InterventionCatalogSnapshot`。该快照不包含目标 benchmark 的运行结论。

公共抽象的描述长度收益为：

$$
G(g)=\sum_{i=1}^{m}DL_{raw}(g_i)-\left[DL_{raw}(g)+\sum_{i=1}^{m}DL_{raw}(b_i)\right],
$$

其中 $g_i$ 是具体节点，$g$ 是候选公共语法，$b_i$ 是从 $g$ 恢复 $g_i$ 的绑定。$G(g)>0$ 只表示抽象更紧凑，不表示它具有更好的任务效果。

**算法 1B：loop 内义务和可达性约束检索。**

1. `TRACE_OBLIGATION_AND_NEED_DIAGNOSIS` 从成功/失败 trace 对照、父 Harness 和既有 witness 中提出多个结构故障解释、最早事件偏离、需要改变/保持的行为及判别 witness；程序核验 trace 事件、实现锚点、状态版本和数据角色，形成义务与 need revision。
2. 用 `available_hooks`、输入输出类型、权限、状态所有权和必要依赖执行硬过滤。
3. 删除其确定性冲突关系已被当前 regime 激活的节点；未知条件保留为 `UNRESOLVED`。
4. 根据节点预测能够覆盖的 obligation 召回一般机制，再沿偏序向下展开到可绑定的具体节点。
5. 对未绑定必要依赖产生新的子查询；每读取一个来源或绑定一个孔，都使用更新后的 `InterventionNeed` 继续检索。
6. 使用词典序结构排序：硬兼容优先，其次为 obligation 覆盖、未绑定依赖更少、接入范围更小、已有 witness 更充分，最后才是文本相关度。
7. 对硬过滤和依赖闭包后的子图发起 `VERSION_SPACE_SEMANTIC_RERANK`。`OptimizerLLM` 说明机制如何覆盖义务、哪些绑定仍需迁移、哪些 witness 会反驳匹配；程序只接受可回指 need、trace 和假设 revision 的字段。
8. 返回版本空间子图、可用绑定、未决条件和能够区分候选的 witness 需求；本阶段不生成最终代码。

```text
OFFLINE_ORGANIZE(source_packets, organization_protocol, llm_call_ledger):
    source_units <- FIX_INTERVENTION_SOURCE_UNITS(source_packets)
    compilation_requests <- BUILD_SOURCE_INTERVENTION_REQUESTS(source_units)
    compilation_calls <- CALL_OPTIMIZER_LLM(
                             compilation_requests,
                             call_type=SOURCE_INTERVENTION_SEMANTIC_COMPILATION)
    compilation_proposals <- PARSE_INTERVENTION_COMPILATION_PROPOSALS(
                                 compilation_calls)
    verified_fields <- VERIFY_SOURCE_INTERVENTION_FIELDS(
                           compilation_proposals, source_units)
    leaves <- COMPILE_TO_FINITE_INTERVENTION_GRAMMAR(
                  source_packets, verified_fields)
    abstractions <- VERIFIED_ANTI_UNIFY(leaves)
    source_space <- INSERT_WITH_PARTIAL_ORDER(empty_graph,
                                              leaves,
                                              abstractions)
    return FREEZE_INTERVENTION_CATALOG(source_space,
                                       organization_protocol)

RETRIEVE_INTERVENTIONS(catalog_snapshot, empirical_space, need, as_of):
    version_space <- MATERIALIZE_VERSION_SPACE(catalog_snapshot,
                                               empirical_space,
                                               as_of)
    candidates <- HARD_REACHABILITY_FILTER(version_space, need)
    candidates <- OBLIGATION_COVERAGE_RECALL(candidates, need)
    candidates <- EXPAND_GENERAL_TO_BINDABLE_SPECIALIZATIONS(candidates)
    while EXISTS_DECISION_RELEVANT_UNBOUND_DEPENDENCY(candidates):
        need <- UPDATE_NEED_FROM_PARTIAL_BINDINGS(candidates, need)
        candidates <- RETRIEVE_NEXT_DEPENDENCY(candidates, need)
    rerank_request <- BUILD_VERSION_SPACE_RERANK_REQUEST(candidates, need)
    rerank_call <- CALL_OPTIMIZER_LLM(
                       rerank_request,
                       call_type=VERSION_SPACE_SEMANTIC_RERANK)
    rerank_proposal <- PARSE_VERSION_SPACE_SEMANTIC_RERANK(rerank_call)
    candidates <- FUSE_STRUCTURAL_AND_VERIFIED_SEMANTIC_RANKS(
                      candidates, rerank_proposal)
    return candidates, UNRESOLVED_CONDITIONS(candidates)
```

离线组织在全部来源完成对齐、语法编译、偏序校验和索引审计后停止并冻结快照。在线检索在所有必要孔已有可追踪绑定、剩余孔被证明在当前 Harness 不可达，或继续展开不能改变候选可行性与实验分区时停止；它不得通过临时联网或新增论文解除缺失依赖。

### 约束驱动候选生成阶段：如何结合 trace、知识与自主探索生成候选

完整 trace 同时包含根因、后续连锁反应和随机噪声。若直接让模型阅读整条轨迹并任意改写代码，候选很难对应一个可检验解释。本阶段先把失败与成功 trace 转换成义务，再从版本空间实例化能够覆盖义务的干预。外部知识和自主探索使用同一种假设格式，使后续实验能够根据预测区分它们，而不是根据来源标签偏爱其中一类。

这里的 trace 有确定来源。第 $g$ 代开始时，先在冻结的执行配置下用父代 $H^{[g]}$ 运行 $D_g^{\mathrm{trace}}$；每个任务无论成功、失败、超时或评测异常，都产生一条 `ExecutionTrace`。该对象记录任务与数据角色、父 Harness、模型和工具版本、种子、完整事件图、最终输出、指标向量及终止状态。事件图 $T$ 是 `ExecutionTrace.trace_graph`，不是脱离真实运行由模型总结出的解释。候选生成只能读取这些 trace、既往轮次已经持久化的 witness 和冻结目录，不能读取 $D_g^{\mathrm{select}}$ 的任务内容、标签或运行结果。

候选综合包含两条隔离通道。知识通道由 `OptimizerHarness` 提供经检索假设、合法孔域、父代码切片和义务，通过 `KNOWLEDGE_INTERVENTION_COMPLETION` 让 `OptimizerLLM` 完成绑定、adapter 与局部代码；自由通道不披露本轮检索到的具体假设，通过 `FREE_INTERVENTION_PROPOSAL` 让模型提出新的具体干预叶节点。两类输出都解析为相同 `CandidateInterventionIR`。若静态检查或 discovery witness 暴露绑定错误，`CANDIDATE_BINDING_CRITIQUE_AND_REVISION` 只能提出最小重绑、补前提、重连、控制修订或 fallback 修订；程序核验后创建新 revision，不能原地改写冻结候选。

```text
ExecutionTrace = {
  task_id,
  split_role,
  generation_id,
  harness_version,
  model_and_tool_versions,
  seed,
  trace_graph,
  final_output,
  metric_vector,
  termination_status,
  artifact_refs
}
```

trace 表示为：

$$
T=(V_T,E_D,E_C,E_S,E_A),
$$

其中 $E_D$、$E_C$、$E_S$ 和 $E_A$ 分别是数据依赖、控制依赖、状态效应依赖和实现锚点。

每个义务表示为：

```text
TraceObligation = {
  obligation_id,
  obligation_type,
  failure_or_success_signature,
  trigger,
  implicated_slice,
  implementation_anchors,
  required_trace_change,
  preserved_behavior,
  current_regime,
  reproducibility,
  uncertainty,
  weight,
  status,
  diagnosis_call_id,
  validation_record_ids
}
```

**算法 2：从训练 trace 产生可操作义务。**

1. 对输入片段、上下文块、工具可用性、配置和可重放状态等可操纵单元做重复确认。
2. 在同一失败签名下执行随机感知的 delta debugging，得到经验 1-minimal 见证；不可操纵的历史 trace 事件只用于依赖定位。
3. 沿数据、控制、状态和实现锚点将见证映射到 Harness 位置。
4. 失败轨迹产生需要改变的义务；成功轨迹产生必须保留的义务。
5. `UNRESOLVED` 观察保留为不确定条件，不能用于删除版本空间节点。

**知识候选。** 对检索到的节点 $\nu$，在有限孔域中求绑定 $b$：

$$
c=(\nu,b,\Delta H,\widehat y),
$$

其中 $\widehat y$ 是候选对激活事件、中介 trace、目标效果和回归的预测。候选必须满足类型安全、依赖闭包、冲突自由、义务覆盖和保留约束。

候选实例化使用自顶向下的有限搜索。部分绑定 $p$ 的启发式为：

$$
J(p)=\operatorname{Coverage}(p,\mathcal O_t)
-\lambda_1\overline{DL}(p)-\lambda_2U(p)-\lambda_3R(p),
$$

$\overline{DL}(p)$ 是归一化修改描述长度，$U(p)$ 是未决必要条件的加权比例，$R(p)$ 是归一化修改范围和副作用风险。该分数只决定展开顺序，不作为真实性能估计。

**自主探索候选。** 自由通道获得当前 Harness、trace obligation、硬约束、保留义务和统一输出协议，但不读取本轮检索到的具体解法。它提出的修改必须反向编译为新的具体叶节点，至少声明语法程序、绑定、适用条件、预测激活、中介变化、目标效果、潜在回归与 fallback。无法恢复这些字段的整文件改写不进入主版本空间。

**算法 3：统一候选生成。**

1. 程序对知识节点执行有限孔绑定搜索，并在每次绑定后检查类型、接口、权限、状态效应和依赖，得到带孔草图与合法绑定域。
2. `KNOWLEDGE_INTERVENTION_COMPLETION` 让 `OptimizerLLM` 在草图内补全适配代码、参数、fallback 和预期 trace；解析结果不得越过孔域或修改固定语法骨架。
3. 为没有任何知识节点覆盖的义务保留自主探索配额；`FREE_INTERVENTION_PROPOSAL` 在不读取本轮具体知识解法的视图中提出新语法程序、绑定与代码修改，并编译为具体叶节点。
4. 对解析后的共同 IR 执行类型、接口、状态、effect、权限、依赖和保留约束检查。出现绑定或机制级反例时，`CANDIDATE_BINDING_CRITIQUE_AND_REVISION` 提出目标位置、失败层、保持结构、最小修订和预期变化；程序核验后产生新 IR revision。
5. 仅对规范化 patch 完全相同或在可信 rewrite rules 下等价的候选做确定性去重。
6. 在诊断 witness 上表现相同的候选只标为 `currently_indistinguishable`，不能直接合并节点。
7. 冻结候选版本，保存父 Harness、假设节点、绑定、代码差异、预测、LLM 调用和 provenance。

```text
BUILD_OBLIGATIONS_AND_NEED(trace_batch, state):
    need_view <- BUILD_TRACE_OBLIGATION_NEED_VIEW(trace_batch, state)
    need_call <- CALL_OPTIMIZER_LLM(
                     need_view,
                     call_type=TRACE_OBLIGATION_AND_NEED_DIAGNOSIS)
    need_proposal <- PARSE_TRACE_OBLIGATION_NEED_PROPOSAL(need_call)
    return VERIFY_TRACE_CODE_STATE_AND_ROLE_ANCHORS(
               need_proposal, need_view)

GENERATE_CANDIDATES(harness, execution_traces, obligations, retrieved_subspace):
    sketches <- TOP_DOWN_BINDING_SEARCH(retrieved_subspace,
                                        harness,
                                        obligations)
    knowledge_requests <- BUILD_KNOWLEDGE_COMPLETION_REQUESTS(
                              harness, sketches, execution_traces,
                              obligations, hard_constraints)
    knowledge_calls <- CALL_OPTIMIZER_LLM(
                           knowledge_requests,
                           call_type=KNOWLEDGE_INTERVENTION_COMPLETION)
    knowledge_ir <- PARSE_KNOWLEDGE_INTERVENTION_IR(knowledge_calls)

    uncovered <- OBLIGATIONS_NOT_COVERED(sketches, obligations)
    free_request <- BUILD_FREE_INTERVENTION_REQUEST(
                        harness, execution_traces, uncovered,
                        hard_constraints)
    free_call <- CALL_OPTIMIZER_LLM(
                     free_request,
                     call_type=FREE_INTERVENTION_PROPOSAL)
    free_ir <- PARSE_FREE_INTERVENTION_IR(free_call)

    ir <- COMMON_INTERVENTION_STATIC_GATE(knowledge_ir union free_ir)
    counterexamples <- DISCOVERY_VALIDATE_BINDINGS(ir, execution_traces)
    if counterexamples is not empty:
        revision_request <- BUILD_BINDING_CRITIQUE_REQUEST(
                                ir, counterexamples, obligations)
        revision_call <- CALL_OPTIMIZER_LLM(
                             revision_request,
                             call_type=CANDIDATE_BINDING_CRITIQUE_AND_REVISION)
        revision_proposals <- PARSE_BINDING_REVISION_PROPOSALS(
                                  revision_call)
        revisions <- VERIFY_AND_COMPILE_MINIMAL_BINDING_REVISIONS(
                         revision_proposals, ir, counterexamples)
        ir <- ir union revisions

    candidates <- EXACT_OR_PROVED_REWRITE_DEDUP(ir)
    return FREEZE_VALID_CANDIDATE_REVISIONS(candidates)
```

本阶段在有限绑定队列为空、当前保留的 top-$B$ 候选已支配所有剩余分支上界，或新自由候选持续编译为已有节点时停止。该停止只相对于当前干预语法和候选生成协议成立。若后续实验暴露接入错误，可以在不披露独立选择标签的前提下回到本阶段重新绑定；一旦本代 $D_g^{\mathrm{select}}$ 的结果已向生成器披露，该结果只能沉淀到下一代，不能用于同代重写候选后再重复充当独立提交证据。

### 版本空间消歧与演化控制阶段：如何规划、测评并控制多轮 Harness 演化

两个候选可能获得相近总分，却对失败原因给出不同解释；也可能使用同一方法名称，但一个绑定真正激活，另一个只是偶然在简单任务上得分更高。固定验证集只能排序候选，不能主动暴露这些差异。本阶段把下一次运行定义为 candidate–witness 实验，优先选择能够最大程度拆分当前版本空间的任务、probe 或干预。实验结果首先改变假设结构，然后才决定是否把候选提交为下一代 Harness。

实验的数据角色决定它能支持什么结论。由 $D_g^{\mathrm{trace}}$ 重放、局部 probe、消融与扰动产生的 `DISCOVERY` witness 可以删除无效绑定、标记未激活机制、拆分节点或生成新的未决条件，但不能单独证明任务收益。$D_g^{\mathrm{select}}$ 上父子严格配对的 `CONFIRMATION` witness 用于目标收益下界；$D_g^{\mathrm{anchor}}$ 上的配对 witness 用于旧能力与关键机制保留。确认任务在候选冻结之前不向候选生成器披露，且每个任务的暴露历史随实验写入账本。这样，主动消歧可以利用训练数据，又不会让被候选适配过的同一案例再次伪装成独立证据。

本阶段让 `OptimizerLLM` 参与难以规则化的 witness 设计与结果解释，但不把实验选择、结构写入或晋级交给模型。`WITNESS_EXPERIMENT_PROPOSAL` 针对竞争假设提出能够产生不同可观测预测的 probe、扰动或消融；程序核验可执行性、数据角色、风险和 predicted partition，并与规则枚举实验合并。结果返回后，`WITNESS_STRUCTURE_INTERPRETATION` 提出哪些预测得到支持、反驳或仍未知，以及可能触发的结构操作；只有满足操作表中确定触发条件的解释才能进入影子版本空间。`NEXT_VERSION_SPACE_ACTION_PROPOSAL` 在合法实验与流程返回中提出下一步，停滞时 `VERSION_SPACE_STALL_REFLECTION` 检查遗漏 witness、错误适用条件或缺失干预原语。`OptimizerHarness` 计算 Split、成本、风险与 confidence sequence，并作出最终选择和提交决定。

实验表示为：

```text
CandidateWitnessExperiment = {
  experiment_id,
  candidate_id,
  witness_id,
  witness_type,
  matched_parent,
  task_and_seed,
  data_role,
  perturbation_or_ablation,
  predicted_partition,
  execution_cost,
  regression_risk,
  confirmation_role,
  exposure_record_id,
  proposal_call_ids,
  validation_record_ids
}
```

`witness_type` 可以是静态契约、激活 probe、失败 replay、关键步骤 perturbation、目标任务配对运行、保留任务配对运行或 fresh confirmation。

对实验 $e$ 及可能结果 $o$，令 $\mathcal V_{e,o}$ 为结果 $o$ 出现后仍未被排除或仍未拆分完成的假设集合。节点权重只用于表示来源可靠性、已有 witness 数量和当前活跃范围，不解释为校准后验。定义：

$$
W(A)=\sum_{h\in A\cap F_t}\omega_t(h),
$$

$$
\operatorname{Split}(e)=1-
\sum_{o\in\mathcal Y_e}
\left(\frac{W(\mathcal V_{e,o})}{W(\mathcal V_t)}\right)^2.
$$

选择规则为：

$$
e_t=\arg\max_e
\left[
\operatorname{Split}(e)
-\lambda_c\widetilde C(e)
-\lambda_r\widetilde R(e)
\right],
$$

其中 $\widetilde C(e)$ 与 $\widetilde R(e)$ 是归一化执行成本和回归风险。`Split` 衡量实验预期把版本空间分得多均衡；它不需要把 LLM 的主观概率当成真实后验。

**结构更新操作。** 每个观察只允许触发以下操作：

| 操作 | 触发条件 | 结果 |
| --- | --- | --- |
| `DELETE_BINDING` | 编译、类型、接口、权限或 hook 可达性确定性失败 | 删除具体绑定，保留一般方法节点 |
| `MARK_INERT` | 重复 probe 显示修改未激活 | 当前节点与绑定失活，不否定来源机制 |
| `SPECIALIZE_SCOPE` | 可检查谓词能稳定区分正负 witness | 将适用条件与该谓词合取 |
| `SPLIT_NODE` | 一个节点在两个 regime 中产生稳定且不可由单一条件解释的相反预测 | 建立两个特化子节点，父节点标记为不可直接实例化 |
| `ADD_REQUIRES` | 方法单独不激活或无效，与另一干预组合后重复生效 | 增加有 witness 的依赖边 |
| `ADD_CONFLICT` | 两个干预单独有效，组合后重复产生相同回归 | 增加有作用域的冲突边 |
| `MERGE_NODES` | 类型化共同抽象可恢复子节点，区分 witness 无法分开，且压缩与跨 regime 检查通过 | 建立公共父节点；不删除具体节点 |
| `KEEP_UNRESOLVED` | 证据不足或结果不复现 | 不改变结构，只追加观察 |

`ADD_REQUIRES` 和 `ADD_CONFLICT` 需要单独与组合的最小对照，不能由 `OptimizerLLM` 的解释直接写入。

**算法 4：主动消歧与结构修订。**

1. 程序在本代冻结的 $D_g^{\mathrm{trace}}$、$D_g^{\mathrm{select}}$、$D_g^{\mathrm{anchor}}$ 及安全 probe 集上枚举契约、重放、消融、扰动和父子配对实验；每个实验预先声明数据角色和允许支持的结论。
2. `WITNESS_EXPERIMENT_PROPOSAL` 针对仍竞争假设提出语义判别实验、预期分区、应保持条件和停止规则。程序只编译可执行、风险合格且不会越权披露的数据视图。
3. 先运行确定性契约和激活 probe，再按冻结的 `Split(e)-cost-risk` 规则从合法实验中选择唯一下一实验；模型建议不直接进入分数。
4. 将结果追加到本代 `RoundLedger`，并通过 `WITNESS_STRUCTURE_INTERPRETATION` 提出支持/反驳/未知预测、竞争解释和结构操作意图；程序核验 witness、假设、绑定与操作触发条件后，在写时复制的影子版本空间执行更新。
5. 结构变化后重新计算可绑定节点和候选分区；旧实验计划全部失效并重规划。
6. `NEXT_VERSION_SPACE_ACTION_PROPOSAL` 只可在程序枚举的 `CONTINUE_EXPERIMENT/RETURN_RETRIEVE/RETURN_REBIND` 中排序或补全参数；提交、拒绝和回退仍由预注册置信序列与 hard gate 唯一决定。无合法动作但仍有决策不确定性时，`VERSION_SPACE_STALL_REFLECTION` 只能产生待核验的新 witness、适用条件修订或缺失原语需求，不能直接宣布收敛。
7. 当一个候选完成机制验证后，再使用目标与保留任务决定是否提交。

候选相对父 Harness 的配对差值为：

$$
D_i(c)=R_i(H_t\oplus c)-R_i(H_t).
$$

分别对目标收益和每类旧能力回归维护预先分配错误率的 anytime confidence sequence。候选提交需要：

$$
L_n^{target}(c)>\epsilon_{gain},
$$

$$
L_n^{preserve,j}(c)>-\epsilon_{reg,j},\quad\forall j,
$$

同时满足激活确认、fresh confirmation 和全部硬约束。若目标收益上界不超过 $\epsilon_{gain}$，或任一旧能力上界仍低于允许边界，则拒绝。区间跨越边界时继续取证。

接受后：

$$
H_{t+1}=H_t\oplus c_t.
$$

所有未执行候选必须针对 $H_{t+1}$ 重新检查绑定，不能沿用旧 Harness 上的可行性结论。延迟回归触发事务式回退，并生成新的作用域 witness。

```text
PLAN_TEST_AND_EVOLVE(state, candidates, select_pool, anchor_pool,
                     exposure_ledger, accumulated_round_ledger):
    loop:
        program_experiments <- BUILD_CANDIDATE_WITNESS_EXPERIMENTS(
                                   state, candidates, select_pool,
                                   anchor_pool, exposure_ledger)
        witness_request <- BUILD_WITNESS_EXPERIMENT_REQUEST(
                               state, candidates, program_experiments,
                               accumulated_round_ledger)
        witness_call <- CALL_OPTIMIZER_LLM(
                            witness_request,
                            call_type=WITNESS_EXPERIMENT_PROPOSAL)
        witness_proposals <- PARSE_WITNESS_EXPERIMENT_PROPOSALS(
                                 witness_call)
        semantic_experiments <- VERIFY_AND_COMPILE_WITNESS_EXPERIMENTS(
                                    witness_proposals, state, candidates,
                                    exposure_ledger)
        experiments <- program_experiments union semantic_experiments
        experiments <- KEEP_DECISION_OR_STRUCTURE_CHANGING_TESTS(experiments)
        if experiments is empty:
            reflection_request <- BUILD_VERSION_SPACE_STALL_REQUEST(
                                      state, candidates,
                                      accumulated_round_ledger)
            reflection_call <- CALL_OPTIMIZER_LLM(
                                   reflection_request,
                                   call_type=VERSION_SPACE_STALL_REFLECTION)
            reflection <- PARSE_VERSION_SPACE_STALL_REFLECTION(
                              reflection_call)
            return_request <- VERIFY_AND_COMPILE_STALL_RETURN(
                                  reflection, state,
                                  accumulated_round_ledger)
            if return_request is valid:
                return return_request, state, accumulated_round_ledger
            return unresolved, state, accumulated_round_ledger

        e <- ARGMAX_VERSION_SPACE_SPLIT_MINUS_COST_RISK(experiments)
        observation <- EXECUTE_ISOLATED(e)
        accumulated_round_ledger.witnesses <- APPEND(
                                                  accumulated_round_ledger.witnesses,
                                                  observation)
        interpretation_request <- BUILD_WITNESS_STRUCTURE_REQUEST(
                                      state, candidates, e, observation)
        interpretation_call <- CALL_OPTIMIZER_LLM(
                                   interpretation_request,
                                   call_type=WITNESS_STRUCTURE_INTERPRETATION)
        interpretation <- PARSE_WITNESS_STRUCTURE_INTERPRETATION(
                              interpretation_call)
        verified_update <- VERIFY_WITNESS_ANCHORS_AND_UPDATE_TRIGGER(
                               interpretation, e, observation, state)
        state.version_space <- APPLY_STRUCTURAL_UPDATE(
                                   state.version_space, observation,
                                   verified_update)
        candidates <- REBIND_AND_REPARTITION(candidates, state)

        program_actions <- ENUMERATE_LEGAL_VERSION_SPACE_ACTIONS(
                               observation, state, candidates,
                               accumulated_round_ledger)
        action_request <- BUILD_NEXT_VERSION_SPACE_ACTION_REQUEST(
                              program_actions, state, candidates,
                              accumulated_round_ledger)
        action_call <- CALL_OPTIMIZER_LLM(
                           action_request,
                           call_type=NEXT_VERSION_SPACE_ACTION_PROPOSAL)
        action_proposals <- PARSE_VERSION_SPACE_ACTION_PROPOSALS(action_call)
        actions <- program_actions union VERIFY_AND_COMPILE_VERSION_SPACE_ACTIONS(
                                           action_proposals, state,
                                           accumulated_round_ledger)
        route <- SELECT_DECISION_RELEVANT_VERSION_SPACE_ACTION(
                     actions, state, candidates)
        if route is return_retrieve or route is return_rebind:
            return route, state, accumulated_round_ledger

        decision <- ANYTIME_TARGET_AND_PRESERVATION_DECISION(candidates)
        if decision is commit:
            return commit(decision.candidate), state, accumulated_round_ledger
        elif decision is reject:
            candidates <- REMOVE_CANDIDATE_KEEP_EVIDENCE(candidates, decision)
        elif decision is rollback:
            state.harness <- RESTORE_CONFIRMED_PARENT(state.harness)
            return rollback, state, accumulated_round_ledger

        if NO_ACTIVE_HYPOTHESIS_CAN_CHANGE_HARNESS(state):
            return stop_unresolved, state, accumulated_round_ledger
```

阶段内控制器在候选仍可被区分或统计边界仍可能改变时继续取证；结构 witness 触发重新分区，提交 witness 只更新确认区间。若结果只暴露接口或机制问题且没有使用选择集标签，可以带着新 revision 返回候选生成；若结果来自选择集，则该结果被封存到本代账本，本代不再据此生成候选。外层多代何时停止由文末完整流转统一定义，资源耗尽始终单独记录为 `RESOURCE_STOP`。

### 结构学习与跨任务复用阶段：如何持续积累并跨任务复用

完整 Harness 可以直接迁移，但很难解释其中哪一部分适合新任务。自然语言经验容易丢失接口和失败条件，静态组件库又不会根据反例改变。本阶段继续更新同一个干预版本空间：具体成功实例成为叶节点，负 witness 限制适用范围，多个独立任务上的可复现实例产生公共父节点。下一轮检索的是带绑定规则、适用条件和反例边界的方法，而不是上一轮的最高分 Harness。

这一阶段是 loop 内的在线积累，不重新执行来源收集。它只消费本代已经产生的 `ExecutionTrace`、`EmpiricalWitness`、候选 revision、提交/拒绝/回退记录和暴露记录，在写时复制的经验层中学习范围与关系；阶段三的影子结构与 `RoundLedger` 在这里一起校验并原子提交。原始 witness 追加保存，派生结构通过新 revision 表达；提交失败时保留原始 round ledger 供恢复，但已提交长期状态保持不变。新论文或新官方代码只能在另一场实验开始前生成新的目录快照，不能插入正在运行的 benchmark loop。

同一 benchmark 内，提交后的经验 revision 直接成为下一代检索输入。跨任务复用时，只复制已经提交的版本空间、witness 与 revision 账本作为新实验的初始经验状态，再针对目标 Harness 的 hook、权限、工具和目标 regime 重新执行硬过滤与绑定；来源任务上的正 witness 只提高检索优先级，不自动成为新任务的效果证据。新任务仍须从自己的训练 split 产生 trace、select 与 anchor witness，测试 split 保持封存。

重新抽象同样把语义提案与结构事实分开。`SEMANTIC_INTERVENTION_ABSTRACTION` 让 `OptimizerLLM` 从多个具体干预及其正反 witness 中提出公共机制骨架、开放孔、不可参数化部分和边界反例；程序执行类型化 anti-unification、可恢复性与 leave-one-regime-out 检查。`APPLICABILITY_SCOPE_PROPOSAL` 提出可检查的任务、接口、失败与 runtime 谓词，程序在冻结谓词语言内求解并验证正负 witness。`VERSION_SPACE_RELATION_REVISION` 提出 `SPECIALIZES/REQUIRES/CONFLICTS/ALTERNATIVE_TO/SUPERSEDES` 关系或节点分裂，但只有相应的最小对照、结构和作用域证据才能写入 revision。模型不能把自然语言相似、单次成功或自身置信度当作跨任务关系证据。

长期 witness 表示为：

```text
EmpiricalWitness = {
  witness_id,
  experiment_id,
  task_and_regime,
  data_role,
  harness_version,
  hypothesis_revision,
  binding,
  intervention_or_probe,
  activation_observation,
  mediator_observation,
  target_outcome,
  preservation_outcomes,
  repetitions_and_seeds,
  environment,
  selection_metadata,
  exposure_record_id,
  confidence_status,
  outcome_class,
  supersedes,
  interpretation_call_ids,
  validation_record_ids
}
```

**适用条件学习。** 每个节点的适用条件限制为可检查谓词语言：

$$
a_\nu(z)=a_{task}(z)\land a_{interface}(z)\land
a_{failure}(z)\land a_{runtime}(z).
$$

从候选谓词类 $\mathcal A$ 中选择：

$$
a_\nu^*=\arg\min_{a\in\mathcal A}
\left[
DL_{raw}(a)+\lambda_+FN(a;W^+)+\lambda_-FP(a;W^-)
\right].
$$

$FN$ 是被条件错误排除的正 witness 数，$FP$ 是被条件错误接纳的负 witness 数。若没有稳定谓词能区分相反结果，则执行 `SPLIT_NODE`，而不是写入含糊的自然语言例外。

**算法 5：正反 witness 驱动的重新抽象。**

1. 按机制结构、输入输出类型、状态效应和预测中介对具体叶节点分组。
2. `SEMANTIC_INTERVENTION_ABSTRACTION` 提出公共机制、开放孔、宿主绑定、不可参数化部分和边界反例；程序只对锚点完整、类型/effect 兼容的组执行 anti-unification。
3. 检查父节点能否通过绑定恢复每个子节点，以及描述长度是否下降。
4. 使用 leave-one-regime-out witness 检查父节点的激活和条件效果；任一被留出的 regime 出现无法由适用条件解释的稳定反例时拒绝合并。
5. `APPLICABILITY_SCOPE_PROPOSAL` 提出候选谓词和区分正负 witness 的字段，程序在有限可检查谓词类中学习适用条件。
6. `VERSION_SPACE_RELATION_REVISION` 对父子、平行节点和新反例提出关系修订或分裂意图；程序核验最小对照、作用域与关系触发条件后才写入影子 revision。
7. 对通过的父节点把正负 witness 分别连接到节点 revision。自主探索叶节点只有在多个独立条件下复现，才允许进入共享检索层。
8. 本代结构更新在影子 revision 上完成审计后原子提交；若以后离线目录升级，新 `SourcePacket` 与旧来源通过 `SUPERSEDES` 连接，但不改变既有实验的目录快照。

```text
CONSOLIDATE_AND_TRANSFER(state, round_ledger, next_need, llm_call_ledger):
    shadow <- COPY_ON_WRITE_EMPIRICAL_STATE(state)
    shadow.witness_ledger <- APPEND(shadow.witness_ledger,
                                    round_ledger.witnesses)
    groups <- GROUP_COMPATIBLE_CONCRETE_INTERVENTIONS(shadow.version_space)
    for group in groups:
        abstraction_request <- BUILD_INTERVENTION_ABSTRACTION_REQUEST(
                                   group, shadow.witness_ledger)
        abstraction_call <- CALL_OPTIMIZER_LLM(
                                abstraction_request,
                                call_type=SEMANTIC_INTERVENTION_ABSTRACTION)
        abstraction_proposal <- PARSE_INTERVENTION_ABSTRACTION_PROPOSAL(
                                    abstraction_call)
        parent <- VERIFY_AND_TYPED_ANTI_UNIFY(
                      group, abstraction_proposal)
        if DESCRIPTION_GAIN(parent, group) <= 0:
            continue
        if not LEAVE_ONE_REGIME_OUT_ACTIVATION_AND_EFFECT_CHECK(parent, group):
            continue
        scope_request <- BUILD_APPLICABILITY_SCOPE_REQUEST(
                             parent, group, shadow.witness_ledger)
        scope_call <- CALL_OPTIMIZER_LLM(
                          scope_request,
                          call_type=APPLICABILITY_SCOPE_PROPOSAL)
        scope_proposal <- PARSE_APPLICABILITY_SCOPE_PROPOSAL(scope_call)
        scope <- LEARN_AND_VERIFY_CHECKABLE_APPLICABILITY_SCOPE(
                     parent.witnesses, scope_proposal)

        relation_request <- BUILD_VERSION_SPACE_RELATION_REQUEST(
                                parent, scope, group, shadow.version_space)
        relation_call <- CALL_OPTIMIZER_LLM(
                             relation_request,
                             call_type=VERSION_SPACE_RELATION_REVISION)
        relation_proposal <- PARSE_VERSION_SPACE_RELATION_PROPOSAL(
                                 relation_call)
        relation <- VERIFY_VERSION_SPACE_RELATION_TRIGGER(
                        relation_proposal, parent, scope, group,
                        shadow.witness_ledger)
        shadow.version_space <- INSERT_PARENT_WITH_SCOPE_AND_RELATION(
                                    parent, scope, relation, group)

    shadow.version_space <- SPLIT_VERIFIED_HETEROGENEOUS_NODES(
                                shadow.version_space,
                                shadow.witness_ledger)
    shadow.revision_log.llm_call_ledger_revision <- CURRENT_LEDGER_REVISION(
                                                        llm_call_ledger)
    commit_result <- ATOMIC_COMMIT_EMPIRICAL_REVISION(
                         state, shadow, round_ledger)
    if commit_result.status is not COMMITTED:
        return {status: PENDING_REVIEW,
                recovery_record: commit_result.recovery_record}
    subspace <- HARD_FILTER_AND_RETRIEVE(
                    commit_result.state.version_space, next_need)
    return {status: COMMITTED,
            state: commit_result.state,
            next_view: subspace}
```

过时实现只降低当前绑定的可用性，不删除论文来源和历史 witness。节点仅在长期无可绑定实现、被更简单节点严格支配且全部 witness 可由替代节点解释时退出活跃检索；其证据仍保留在账本中。

### 四阶段在多轮 Harness 演化中的完整流转

前面四个阶段共同实现 benchmark 训练集上的一代更新，而不是只执行一次的线性流程。loop 外先运行 `OFFLINE_ORGANIZE` 得到冻结目录 $K_0$，冻结 `TrainProtocol` 并封存 $D_{\mathrm{test}}$。在线 loop 从 $S_0=(H_0,\mathcal V_0,\varnothing,\mathcal W_0,\mathcal R_0)$ 开始；其中 $H^{[0]}=H_0$，经验空间尚未包含本次 benchmark 的运行结论，$\mathcal V_0$ 的来源节点来自 $K_0$，$\mathcal W_0$ 与 $\mathcal R_0$ 只含初始化记录。

第 $g$ 代先由调度器冻结三个数据角色。执行器用 $H^{[g]}$ 跑完 $D_g^{\mathrm{trace}}$，将每次运行写成 `ExecutionTrace`，再从成功/失败对照中形成 $\mathcal O_g$ 与 `InterventionNeed`。阶段一在线检索把该 need 应用于 $K_0$ 与截至本代开始可见的经验空间；阶段二只使用这些 trace、检索子图和既有 witness 生成冻结候选；阶段三在 discovery、select 和 anchor 三种证据流上逐次选择 candidate–witness 实验，收缩版本空间并给出候选决定；阶段四把本代原始证据和结构修订原子持久化。

一代内部允许局部返回，但返回边界由数据独立性决定。静态检查、激活 probe 或 trace replay 若证明绑定不可达、机制未激活或 mediator 定位错误，控制器先更新版本空间：依赖缺失返回阶段一重新检索，绑定问题返回阶段二重新实例化。此时父 Harness 与 $D_g^{\mathrm{select}}$ 仍冻结不变。若选择集结果已经披露给生成路径，则禁止同代返回生成；该结果只进入阶段四，并在第 $g+1$ 代作为历史 witness 使用。这样局部闭环修复机制解释，外层闭环负责产生新的 Harness 代际。

本代候选满足提交条件时，唯一胜者原子成为 $H^{[g+1]}$；全部候选拒绝、不可区分或没有安全信息实验时，$H^{[g+1]}=H^{[g]}$。无论 Harness 是否改变，阶段四都产生新的经验 revision，调度器也更新任务暴露、任务族覆盖、未决义务和 anchor。因此下一代必须重新分配数据角色，用 $H^{[g+1]}$ 重新执行 $D_{g+1}^{\mathrm{trace}}$，不能沿用上一代候选的绑定、激活结论或提交区间。

```text
EVOLVE_INTERVENTION_SPACE(H0, source_packets, D_train, D_test, train_protocol):
    llm_call_ledger <- INIT_LLM_CALL_LEDGER(train_protocol)
    catalog <- OFFLINE_ORGANIZE(source_packets,
                                train_protocol.organization_protocol,
                                llm_call_ledger)
    scheduler <- INIT_TRAIN_SCHEDULER(D_train, train_protocol)
    state <- INIT_ONLINE_STATE(H0, catalog)
    g <- 0

    loop:
        trace_pool, select_pool, anchor_pool <- ASSIGN_TRAIN_ROLES(
                                                    scheduler, state, g)
        trace_batch <- RUN_HARNESS(state.harness,
                                   trace_pool,
                                   train_protocol.execution_config)
        obligations, need <- BUILD_OBLIGATIONS_AND_NEED(trace_batch,
                                                        state)
        round_ledger <- INIT_ROUND_LEDGER(
                            g, state.harness, trace_batch,
                            llm_call_ledger, scheduler.exposure_ledger)

        loop current_generation:
            retrieved, unresolved <- RETRIEVE_INTERVENTIONS(
                                          catalog,
                                          state.version_space,
                                          need,
                                          as_of=state.revision_log.latest_committed_revision)
            candidates <- GENERATE_CANDIDATES(state.harness,
                                              trace_batch,
                                              obligations,
                                              retrieved)
            control, state, round_ledger <- PLAN_TEST_AND_EVOLVE(
                                                  state,
                                                  candidates,
                                                  select_pool,
                                                  anchor_pool,
                                                  scheduler.exposure_ledger,
                                                  round_ledger)
            UPDATE_EXPOSURE_FROM_LLM_CALLS(
                scheduler, llm_call_ledger, candidates,
                trace_pool union select_pool union anchor_pool)

            if control is RETURN_RETRIEVE and NO_SELECT_RESULT_DISCLOSED(round_ledger):
                select_pool, anchor_pool <- REFRESH_INDEPENDENT_DEVELOPMENT_POOLS(
                                               scheduler, candidates,
                                               select_pool, anchor_pool)
                need <- REVISE_NEED_FROM_WITNESS(need, round_ledger)
                continue current_generation
            if control is RETURN_REBIND and NO_SELECT_RESULT_DISCLOSED(round_ledger):
                select_pool, anchor_pool <- REFRESH_INDEPENDENT_DEVELOPMENT_POOLS(
                                               scheduler, candidates,
                                               select_pool, anchor_pool)
                continue current_generation
            break current_generation

        H_next <- APPLY_GENERATION_DECISION(state.harness, control)
        next_need <- CARRY_UNRESOLVED_TO_NEXT_NEED(need,
                                                   unresolved,
                                                   round_ledger)
        consolidation <- CONSOLIDATE_AND_TRANSFER(state,
                                                  round_ledger,
                                                  next_need,
                                                  llm_call_ledger)
        if consolidation.status is not COMMITTED:
            return {status: PENDING_REVIEW,
                    recovery_record: consolidation.recovery_record,
                    state: state,
                    round_ledger: round_ledger}
        state <- consolidation.state
        next_view <- consolidation.next_view
        UPDATE_EXPOSURE_FROM_LLM_CALLS(
            scheduler, llm_call_ledger,
            EMPIRICAL_REVISIONS_CREATED(round_ledger, state),
            trace_pool union select_pool union anchor_pool)
        scheduler <- UPDATE_TRAIN_SCHEDULER(scheduler,
                                            trace_pool,
                                            select_pool,
                                            anchor_pool,
                                            round_ledger)

        if TRAIN_FIXED_POINT(state.harness, H_next, state,
                             scheduler, train_protocol.stop_rule):
            frozen <- FREEZE_FOR_FINAL_TEST(H_next, state, catalog,
                                            train_protocol)
            break

        state.harness <- H_next
        INVALIDATE_OLD_BINDINGS_CANDIDATES_AND_INTERVALS(state)
        g <- g + 1

    return RUN_FINAL_TEST_ONCE(frozen, D_test)
```

`TRAIN_FIXED_POINT` 只有在预注册的训练集完整轮换完成、连续规定代数没有 Harness 晋级、没有可执行的开放义务、重新检索与自由探索都未产生新合法叶节点、版本空间没有待执行的结构更新，并且当前 Harness 通过 fresh confirmation 与全部 anchors 时才为真。资源或时间耗尽返回 `RESOURCE_STOP`，不能写成固定点。stop 后同时冻结 Harness、目录、经验 revision、模型、工具、评测器和种子，只在 $D_{\mathrm{test}}$ 上运行一次正式比较；测试 trace 仅用于报告，不得更新 Harness、版本空间、检索器、停止决定或任何超参数。

| 可以由设计保证 | 必须通过实验验证 |
| --- | --- |
| 每个活跃方法节点具有有限语法、来源、绑定和可检验预测 | 干预语法是否覆盖足够多的有效 Harness 修改 |
| 确定性违规只删除具体绑定，不篡改论文来源 | 结构更新是否减少重复无效修改并提高最终 Harness 质量 |
| `split/specialize/merge` 均保存触发 witness 和旧 revision | candidate–witness 主动选择是否优于固定验证或随机取证 |
| 普通随机失败不会被伪装成形式反例 | 经验 witness 能否可靠学到方法的适用范围 |
| 完整 Harness 提交和方法空间更新是两个独立决定 | 跨任务重新抽象是否提高新任务的演化效率与最终效果 |
| 测试集不参与版本空间更新、适用条件学习或候选选择 | 学到的版本空间是否能在未见任务保持收益和旧能力 |

## 二、字段、公式与参数完整定义

本节给出第一部分全部对象的可实现定义。未在这里声明的字段不得在实现中静默推断；缺失信息必须显式记为 `UNKNOWN`、`UNBOUND` 或 `UNRESOLVED`。

### 记号、取值与统一状态

| 记号 | 类型与取值 | 完整定义 |
| --- | --- | --- |
| $g\in\mathbb N_0$ | 非负整数 | Harness 外层演化代际。第 $g$ 代从父版本 $H^{[g]}$ 和新分配的训练任务角色开始，以提交/不提交决定、在线沉淀和调度状态更新结束。方括号上标只用于区别结构修订下标。 |
| $t\in\mathbb N_0$ | 非负整数 | 版本空间的结构修订时刻。每吸收一个合法 witness 并完成 `UpdateStructure` 后加一；同一 Harness 代内可有多个 $t$。 |
| $H_t$ | `HarnessVersion` | 结构修订时刻 $t$ 的当前已确认 Harness。多个相邻 $t$ 可指向同一版本；只有提交或回退改变它。正文的 $H^{[g]}$ 是第 $g$ 代边界处的同一对象。 |
| $\mathcal V_t=(N_t,E_t,F_t)$ | 有向带类型图 | 干预版本空间。$N_t$ 是节点集合，$E_t$ 是关系边集合，$F_t$ 是当前可直接实例化、可参与实验分区的活跃前沿。 |
| $\mathcal O_t$ | `TraceObligation[]` | 当前开发任务产生的改变义务与保留义务。义务被解决后保留历史状态，但不再进入候选覆盖率计算。 |
| $\mathcal O_g$ | `TraceObligation[]` | 第 $g$ 代父 Harness 在 $D_g^{\mathrm{trace}}$ 上生成的初始义务集合；进入阶段内结构修订后，对应当前 $\mathcal O_t$ revision。 |
| $\mathcal W_t$ | append-only ledger | 来源、静态检查、probe、配对执行、回归测试与跨任务复现形成的原始 witness 账本。原始记录不可修改；纠错通过追加 superseding record 完成。 |
| $\mathcal R_t$ | append-only revision log | 节点、边、绑定、候选、Harness 提交与回退的修订记录。每条记录必须指向触发它的 witness。 |
| $S_t$ | 五元组 | $S_t=(H_t,\mathcal V_t,\mathcal O_t,\mathcal W_t,\mathcal R_t)$，是四个方法阶段共享的内容状态。训练角色、暴露与本代事务由独立的 `SchedulerState` 和 `RoundLedger` 管理，不能静默写入 $S_t$。 |
| $\nu$ | `InterventionHypothesis` | 一个一般、参数化或具体的干预假设节点。 |
| $b$ | `Binding` | 将 $\nu$ 的全部必填孔映射到 $H_t$ 中具体 hook、状态、工具、参数和实现锚点的类型安全赋值。 |
| $c$ | `FrozenCandidate` | 在固定父 Harness、节点 revision 和绑定 revision 上生成的不可变候选。 |
| $e$ | `CandidateWitnessExperiment` | 对某个候选实施一次 probe、消融、扰动、任务执行或组合对照的完整实验计划。 |
| $w$ | `EmpiricalWitness` | 一次实验产生的原始观察、评测结果、环境信息与统计状态。 |
| $z$ | `Regime` | 决定一次观察适用边界的任务、数据、模型、工具、Harness、评测器和运行环境组合。 |
| $K_0$ | `InterventionCatalogSnapshot` | loop 外由固定 `SourcePacket[]` 编译并审计后冻结的来源方法目录；下标 0 表示本次实验中不随代际变化。 |

状态更新严格定义为

$$
S_{t+1}=\operatorname{UpdateStructure}(S_t,w_t;\Theta_{struct}),
$$

其中 $w_t$ 是本轮新增 witness，$\Theta_{struct}$ 是实验开始前冻结的结构更新配置，包含允许操作、阈值、谓词语言、最小重复数和冲突优先级。该函数不得读取封存测试集。

全文数学记号遵循以下约定：

| 记号 | 唯一含义 |
| --- | --- |
| $\mathbf 1[P]$ | 指示函数；命题 $P$ 为真取 1，否则取 0；`UNKNOWN` 不算真。 |
| $\mathbb E[X]$ | 在明确声明的开发任务分布、种子分布与运行随机性下对 $X$ 取期望。 |
| $\arg\max/\arg\min$ | 先按目标值选择；并列时使用相应小节给出的确定性 tie-break，不返回任意元素。 |
| $\log$、$\exp$ | 自然对数和自然指数。 |
| $\land$、$\Rightarrow$ | 三值谓词上的合取与蕴含；含 `UNKNOWN` 且无法由另一项决定时结果仍为 `UNKNOWN`。硬 gate 只接受 `TRUE`。 |
| $\lvert A\rvert$ | 有限集合 $A$ 的元素数；多重集计重复，普通集合不计重复。 |
| $A\subseteq B$ | 包含相等的子集关系；严格子集写 $A\subset B$。 |
| 空和、空积 | 空和为 0，空积为 1；任何分母为空或为 0 的特殊处理必须由对应公式单独声明。 |
| 分数方向 | 进入差值、均值或置信序列前统一转换为“越大越好”，原始方向仍保存在 endpoint 元数据中。 |

### Benchmark 数据角色与实验协议

| 符号 | 来源与用途 | 隔离约束 |
| --- | --- | --- |
| $D_{\mathrm{train}}$ | benchmark 官方训练集，是在线演化唯一允许使用的任务全集。 | 不含测试实例；官方没有训练集时必须在实验前声明公开开发集，不能从测试集回填。 |
| $D_g^{\mathrm{trace}}$ | 第 $g$ 代父 Harness 的故障发现与成功对照任务，用于产生 `ExecutionTrace`、义务和检索需求。 | 本代与 select、anchor 两组不相交；其结果可参与生成，不能再为同一候选提供独立提交证据。 |
| $D_g^{\mathrm{select}}$ | 候选冻结后才运行的目标收益确认任务。 | 在生成期间隐藏任务内容、标签和结果；父子使用同任务、种子、环境与评测器配对。 |
| $D_g^{\mathrm{anchor}}$ | 已确认旧能力、严重失败和关键机制的回放任务。 | 只判断保留约束与回归，不替代目标收益证据。 |
| $D_{dev}^{(g)}$ | $D_g^{\mathrm{select}}\cup D_g^{\mathrm{anchor}}$，本代允许用于候选提交判断的开发池。 | 不含 $D_g^{\mathrm{trace}}$ 和测试集。 |
| $D_{\mathrm{test}}$ | benchmark 官方封存测试集。 | stop 前完全不可见；只对最终冻结状态运行一次，不产生在线结构更新。 |

`TrainProtocol` 在实验开始前冻结，字段如下。

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `benchmark_revision` | version id | benchmark 的精确发布版本及数据校验信息。 |
| `split_revision` | version id | 官方 train/test 划分与训练集内部角色分配规则版本。 |
| `organization_protocol` | config snapshot | 来源对齐、语法编译、anti-unification、描述长度编码和目录审计规则。 |
| `task_strata` | stratification rule | 保证任务族、难度、工具需求和 trace 长度覆盖的预注册分层。 |
| `role_assignment_rule` | deterministic rule/seeded sampler | 根据分层、暴露历史、未决义务和 anchors 产生三组互不重叠任务。 |
| `execution_config` | config snapshot | 执行模型、provider、推理参数、工具、容器、超时、并发及 trace instrumentation。 |
| `optimizer_config_revision` | config snapshot | `OptimizerLLMConfig`、`OptimizerHarness` 代码、parser、核验器、提示模板和调用账本 schema 的冻结 revision。 |
| `evaluator_revision` | version id | 指标实现、聚合、方向和异常处理规则。 |
| `seeds` | seed plan | 任务抽样、模型、工具、环境和父子配对所用种子及复用规则。 |
| `promotion_rule` | decision config | $\epsilon_{gain}$、$\epsilon_{reg,j}$、错误率分配、fresh confirmation 和 hard gate。 |
| `stop_rule` | fixed-point config | 完整轮换、连续无晋级代数、开放义务、结构更新与 anchor 通过条件。 |

#### `OptimizationAgent`

本方法中的 `OptimizationAgent` 定义为：

$$
\text{OptimizationAgent}=\text{OptimizerLLM}+\text{OptimizerHarness}.
$$

公式中的加号表示二者共同组成一个可运行系统，不表示数值相加。`OptimizerLLM` 是来源干预语义编译、trace 义务解释、版本空间语义比较、知识与自由候选设计、witness 实验构思、实验结果解释、下一动作规划和跨任务重新抽象的认知主体。`OptimizerHarness` 固定来源与数据角色，维护有限语法和版本空间，构造最小权限输入，解析并核验模型输出，执行硬可达性过滤、代码检查、真实实验、结构更新、置信序列、披露追踪和原子提交。

| `OptimizerHarness` 组件 | 职责 | 发起的 `OptimizerLLM` 调用 |
| --- | --- | --- |
| `intervention_catalog_compiler_and_retriever` | 固定来源锚点，编译有限语法，核验特化关系，构造 trace 义务与 need，执行硬过滤、依赖展开和排序融合。 | `SOURCE_INTERVENTION_SEMANTIC_COMPILATION`、`TRACE_OBLIGATION_AND_NEED_DIAGNOSIS`、`VERSION_SPACE_SEMANTIC_RERANK`。 |
| `candidate_synthesizer` | 构造知识与自由通道视图，解析共同候选 IR，核验绑定修订并冻结候选。 | `KNOWLEDGE_INTERVENTION_COMPLETION`、`FREE_INTERVENTION_PROPOSAL`、`CANDIDATE_BINDING_CRITIQUE_AND_REVISION`。 |
| `witness_planner_and_structure_controller` | 枚举合法实验，核验语义 probe，执行真实 witness，验证结构操作触发条件并依据冻结统计规则决策。 | `WITNESS_EXPERIMENT_PROPOSAL`、`WITNESS_STRUCTURE_INTERPRETATION`、`NEXT_VERSION_SPACE_ACTION_PROPOSAL`、`VERSION_SPACE_STALL_REFLECTION`。 |
| `empirical_abstraction_manager` | 核验公共机制、适用条件与版本空间关系，执行留一 regime 检查和经验 revision 提交。 | `SEMANTIC_INTERVENTION_ABSTRACTION`、`APPLICABILITY_SCOPE_PROPOSAL`、`VERSION_SPACE_RELATION_REVISION`。 |
| `llm_call_ledger` | 追加保存全部输入视图、原始响应、解析/核验状态、工具会话和资源消耗。 | 不发起调用，只记录调用。 |

被优化的执行 agent 由执行模型和当前 Harness $H^{[g]}$ 组成，负责在 benchmark 任务上产生 `ExecutionTrace`。即使执行模型与 `OptimizerLLM` 采用同一基础模型，也必须隔离会话、上下文、工具权限、采样配置和调用账本。

#### `OptimizerLLMConfig`

| 字段 | 精确定义 |
| --- | --- |
| `provider_model_revision` | provider、模型名称和不可变 revision 或可审计快照。 |
| `call_types` | 只允许 `SOURCE_INTERVENTION_SEMANTIC_COMPILATION`、`TRACE_OBLIGATION_AND_NEED_DIAGNOSIS`、`VERSION_SPACE_SEMANTIC_RERANK`、`KNOWLEDGE_INTERVENTION_COMPLETION`、`FREE_INTERVENTION_PROPOSAL`、`CANDIDATE_BINDING_CRITIQUE_AND_REVISION`、`WITNESS_EXPERIMENT_PROPOSAL`、`WITNESS_STRUCTURE_INTERPRETATION`、`NEXT_VERSION_SPACE_ACTION_PROPOSAL`、`VERSION_SPACE_STALL_REFLECTION`、`SEMANTIC_INTERVENTION_ABSTRACTION`、`APPLICABILITY_SCOPE_PROPOSAL`、`VERSION_SPACE_RELATION_REVISION`。 |
| `decoding_by_call_type` | 每类调用的 temperature、top-p、最大输出、停止条件、推理强度、种子策略和候选数量。 |
| `prompt_template_revisions` | 每类调用的系统指令、输入序列化、输出 schema 与示例 revision。 |
| `context_policies` | 每类调用允许披露的来源、父代码、trace、hypothesis、candidate、witness 和 relation 字段；未列字段默认禁止。 |
| `tool_policy` | 允许读取和编辑的代码范围及分析/测试工具；禁止访问测试集、直接改已提交空间或绕过检查器。 |
| `retry_policy` | 超时、格式错误与工具失败的重试和退避规则；每次重试新建 call ID。 |
| `parser_revision` | 每类输出的固定解析器；只能提取或拒绝字段，不能补写模型未输出语义。 |
| `validator_revisions` | 每类调用对应的来源、代码、trace、角色、实验、统计与结构触发核验器 revision；模型自身判断不能充当验证器。 |
| `resource_accounting` | 逐调用 token、费用、时延、工具执行和失败重试的记录规则；只用于预算/报告和实验选择中的实际成本，不改变证据有效性。 |

#### `LLMCallRecord`

| 字段 | 精确定义 |
| --- | --- |
| `call_id` | 一次 `OptimizerLLM` 请求的唯一 ID；重试使用新 ID。 |
| `generation_id` | 在线调用所属 Harness 代际；离线来源编译使用预先分配的 `OFFLINE:<catalog_build_id>`，目录冻结后由快照反向引用该 build。 |
| `structure_revision` | 调用发生时可见的版本空间 revision。 |
| `call_type` | `OptimizerLLMConfig.call_types` 中的一种，决定披露策略、输出 schema 和核验器。 |
| `model_revision` | 实际响应请求的模型 revision。 |
| `prompt_template_revision` | 本次模板与 schema revision。 |
| `input_view_revision` | `OptimizerHarness` 构造的不可变最小权限视图。 |
| `disclosed_object_ids` | 实际披露的来源、代码、trace、义务、hypothesis、candidate、experiment 或 witness ID。 |
| `forbidden_object_check` | `PASS/FAIL`；检查测试数据、隐藏 select 标签、未来 revision 和越权文件，`FAIL` 时不得调用。 |
| `tool_session_id` | 隔离工具会话 ID 或 `NONE`，记录实际读写和执行权限。 |
| `seed` | 实际生成种子或 `UNCONTROLLED`。 |
| `raw_output_ref` | 原始响应的不可变存储位置。 |
| `parsed_output_ids` | 解析产生的提案、候选 IR、实验、关系或 scope 草案 ID；失败时为空。 |
| `validation_status` | `PENDING/PARSE_FAILED/ANCHOR_REJECTED/GATE_REJECTED/RULE_REJECTED/EVIDENCE_REJECTED/ACCEPTED_AS_PROPOSAL`。 |
| `validation_record_ids` | 对解析产物执行的全部 `ValidationRecord`；`ACCEPTED_AS_PROPOSAL` 仅表示可进入下一确定步骤，不表示经验结论成立。 |
| `parent_call_id` | 格式修复或受控重试引用的前一调用；首次为 `NONE`。 |
| `usage` | 输入/输出 token、费用、时延和工具调用数，仅用于复现与成本统计。 |

`CALL_OPTIMIZER_LLM` 在请求开始前建立 `call_id`，并把请求、响应、解析与核验状态以追加事件写入实验级 `LLMCallLedger`。失败和拒绝输出同样保存。任何 hypothesis、need、候选、witness 解释、结构动作或经验 revision 都必须通过 `call_id` 回指产生它的调用。

`LLMCallLedger` 由 `OptimizerHarness` 作为实验级依赖注入全部调用算子，因此伪代码不在每次调用中重复传参。离线调用归入 `catalog_build_id`；在线调用按 `generation_id` 自动登记到当前 `RoundLedger.llm_call_ids`。义务诊断发生在 round ledger 实体创建之前时，`INIT_ROUND_LEDGER` 必须从实验账本收集本代已存在的诊断 call ID，不能遗漏或事后重建。

#### `OptimizerProposal`

除知识与自由候选调用直接解析为 `CandidateInterventionIR` 外，其余模型输出先进入统一提案外壳：

| 字段 | 精确定义 |
| --- | --- |
| `proposal_id` | 不可变提案 ID；同一调用返回多项时分别编号。 |
| `call_id` | 产生提案的 `LLMCallRecord`。 |
| `proposal_type` | 与对应 call type 一致；不一致时解析失败。 |
| `target_ids` | 被编译、解释、比较、修订或抽象的来源、义务、节点、候选、实验、witness 或关系对象。 |
| `payload` | 下表规定的 call-specific 必填字段。 |
| `evidence_anchors` | 每项关键主张引用的来源位置、代码符号、trace 事件、节点 revision、实验或 witness。 |
| `counterevidence` | 与提案冲突或限制其范围的锚点；没有时为空列表。 |
| `uncertainties` | 当前视图无法判断的前提、替代解释和取证动作。 |
| `expected_observations` | 提案正确或错误时应出现的可执行观察；纯来源字段可为 `NOT_APPLICABLE`。 |
| `validation_status` | `PENDING/ACCEPTED/REJECTED/PARTIALLY_ACCEPTED`，只由 `OptimizerHarness` 写入。 |

| call type | `payload` 必填字段 | 含义 |
| --- | --- | --- |
| `SOURCE_INTERVENTION_SEMANTIC_COMPILATION` | `{mechanism_steps,grammar_operations,hooks,typed_holes,binding_constraints,prediction_chain,fallback,applicability,relation_candidates}` | 将来源方法映射到有限干预语法和候选关系。 |
| `TRACE_OBLIGATION_AND_NEED_DIAGNOSIS` | `{competing_failure_hypotheses,earliest_divergences,change_obligations,preservation_obligations,implementation_anchors,required_witnesses,unknown_conditions}` | 从父代 trace 构造可反驳义务与检索需求。 |
| `VERSION_SPACE_SEMANTIC_RERANK` | `{node_order,mechanism_matches,migration_gaps,dependency_complements,refuting_witnesses}` | 仅重排硬过滤后的可达子图。 |
| `CANDIDATE_BINDING_CRITIQUE_AND_REVISION` | `{candidate_ir,failure_layer,target_locations,repair_kind,preserved_program,expected_trace_change,required_rechecks}` | 对确认反例提出最小绑定或控制 revision。 |
| `WITNESS_EXPERIMENT_PROPOSAL` | `{target_hypotheses,experiment_kind,input_or_perturbation,preserved_conditions,predicted_partition,expected_observations,stop_rule}` | 提出能够区分竞争假设的可执行 witness。 |
| `WITNESS_STRUCTURE_INTERPRETATION` | `{observation_ids,supported_predictions,refuted_predictions,unknown_predictions,alternative_explanations,structural_operation_intents}` | 把真实 witness 映射到预测与结构操作意图。 |
| `NEXT_VERSION_SPACE_ACTION_PROPOSAL` | `{action_kind,target_ids,executable_parameters,expected_structure_or_decision_change,stop_condition}` | 排序合法实验/返回/终止动作或补全合法动作参数。 |
| `VERSION_SPACE_STALL_REFLECTION` | `{stagnation_cause,missing_witness,scope_revision,missing_primitive,return_destination}` | 为停滞分支提出可核验的新证据或前序返回。 |
| `SEMANTIC_INTERVENTION_ABSTRACTION` | `{fixed_mechanism,open_holes,host_bindings,nonparameterizable_parts,boundary_counterexamples}` | 从具体干预提出公共父机制边界。 |
| `APPLICABILITY_SCOPE_PROPOSAL` | `{candidate_predicates,positive_separators,negative_separators,unknown_regions,required_replays}` | 提出有限可检查的适用条件候选。 |
| `VERSION_SPACE_RELATION_REVISION` | `{left_revision,right_revision,relation_type,guard,supporting_witnesses,contradicting_witnesses,revision_operation}` | 提出关系建立、收紧、分裂或废弃意图。 |

`KNOWLEDGE_INTERVENTION_COMPLETION` 与 `FREE_INTERVENTION_PROPOSAL` 直接解析为共同 `CandidateInterventionIR`；二者只允许披露视图不同，输出字段和后续检查完全相同。

#### `ExposureRecord`

| 字段 | 精确定义 |
| --- | --- |
| `task_id` | 训练任务稳定 ID。 |
| `generation_id` | 披露所属外层 Harness 代际。 |
| `split_role` | `trace/select/anchor/synthetic-probe`；合成 probe 没有 benchmark task 时使用独立 probe ID。 |
| `disclosed_fields` | 实际进入 `OptimizerHarness` 生成/规划视图或向 `OptimizerLLM` 披露的输入、标签、trace、指标、代码和 witness 字段。 |
| `disclosed_to_call_ids` | 接收上述字段的全部 `LLMCallRecord`。 |
| `harness_versions` | 该角色下运行的父代或候选 revisions。 |
| `candidate_ids` | 披露内容直接或间接影响的候选及后代。 |
| `empirical_revision_ids` | 披露内容影响的 hypothesis、relation、scope 或经验 revision。 |
| `witness_ids` | 该任务产生的静态、discovery、confirmation 或 anchor witness。 |
| `independence_status` | 针对每个候选或经验 revision 取 `INDEPENDENT/EXPOSED/NOT_APPLICABLE`；影响形成后不能恢复为独立。 |

角色可跨代轮换；只要披露字段影响过候选，就不得将同一任务对该候选标为独立 `CONFIRMATION`。

`InterventionCatalogSnapshot={catalog_id,source_packet_revisions,source_space_revision,index_revisions,organization_protocol_revision,semantic_compilation_call_ids,created_at,frozen}`。`source_space_revision` 指冻结的一般/具体来源节点和偏序；`index_revisions` 指字段、hook、状态效应、预测与来源索引版本；`semantic_compilation_call_ids` 包含全部离线语义编译调用及其拒绝记录；`frozen=true` 后任何字段变化都必须创建新快照和新实验，不能原地更新。

### 来源、干预与版本空间字段

#### `SourcePacket`

| 字段 | 类型 | 必填 | 定义与约束 |
| --- | --- | --- | --- |
| `source_id` | string | 是 | 来源包的稳定标识；只用于引用，不编码质量结论。 |
| `paper_version` | object | 是 | 论文标题、作者、公开地址、版本号、发布日期和获取日期。若有正式出版版与预印本，两者分别记录。 |
| `official_code_version` | object/null | 是 | 官方仓库地址、commit、release、license 和获取日期；无官方代码时为 `null`，不能用非官方实现冒充。 |
| `exact_source_anchors` | `SourceAnchor[]` | 是 | 支撑每个机制陈述的精确页码、章节、公式、图表、代码文件和行号。每个派生节点至少关联一个 anchor。 |
| `configs_and_examples` | `ArtifactRef[]` | 是 | 官方配置、命令、样例输入输出及其版本；不存在时保存空数组和缺失原因。 |
| `tests_and_reported_results` | `EvidenceRecord[]` | 是 | 官方测试、数据集、指标、对照、均值/方差/重复数和已报告限制。该字段保存原始事实，不外推到新任务。 |
| `source_grade` | enum | 是 | `A_OFFICIAL_REPRODUCIBLE`、`B_OFFICIAL_PARTIAL`、`C_PAPER_ONLY` 或 `D_SECONDARY`；只影响检索优先级，不代表方法必然有效。 |
| `alignment_status` | map | 是 | 每条声明与实现的对齐状态：`ALIGNED`、`PAPER_ONLY`、`CODE_ONLY` 或 `UNRESOLVED`。 |
| `extraction_revision` | integer | 是 | 结构化提取版本；修订时递增，旧版本保留。 |

`SourceAnchor={artifact_id, locator, quoted_or_paraphrased_claim, claim_type}`。`locator` 必须能定位到确定片段；`claim_type` 取 `MECHANISM`、`CONDITION`、`IMPLEMENTATION`、`RESULT` 或 `LIMITATION`。

#### 有限干预语法

$$
\texttt{Intervention}:=\texttt{Trigger}\to\texttt{Guard}\to
\texttt{ReadState}^{*}\to\texttt{Transform}^{+}\to
\texttt{Validate}^{*}\to\texttt{Commit}\to\texttt{Fallback}^{?}.
$$

| 语法项 | 基数 | 输入 | 输出与语义 |
| --- | --- | --- | --- |
| `Trigger` | 恰好 1 | 生命周期事件 | 指定何时启动干预，例如工具返回、上下文超限、计划停滞或任务结束。 |
| `Guard` | 恰好 1 | regime、当前状态、事件 | 返回布尔值；为假时不得产生写操作。空条件用常真谓词表示。 |
| `ReadState` | 0 个或多个 | 声明的只读状态 | 读取上下文、记忆、trace、工具 schema 或预算；每次读取均声明类型与权限。 |
| `Transform` | 1 个或多个 | 已读取状态和绑定参数 | 产生候选状态差分；至少一个变换保证该节点不是空操作。 |
| `Validate` | 0 个或多个 | 差分、接口和约束 | 执行静态检查、单元检查、schema 检查或机制 probe；失败时禁止提交。 |
| `Commit` | 恰好 1 | 已验证差分 | 以原子方式写入候选 Harness 沙箱，不直接覆盖 $H_t$。 |
| `Fallback` | 0 或 1 | 失败类型与原状态 | 回滚、降级或转入人工复核；无 fallback 时必须证明沙箱能完整隔离副作用。 |

每个语法操作统一具有 `{op_id,input_types,output_types,read_set,write_set,hook,tool_permissions,side_effect_class}`。`side_effect_class` 取 `NONE`、`REVERSIBLE_LOCAL`、`REVERSIBLE_EXTERNAL` 或 `IRREVERSIBLE`；`IRREVERSIBLE` 操作不得进入自动实验集合。

#### `TypedHole`、`Binding` 与约束

| 对象/字段 | 类型 | 定义 |
| --- | --- | --- |
| `TypedHole.hole_id` | string | 节点内唯一的孔标识。 |
| `TypedHole.value_type` | type | 允许绑定的静态类型，如 `LifecycleHook`、`StateStore`、`ToolRef`、`Threshold`。 |
| `TypedHole.required` | bool | 必填孔为真时，未绑定候选不能执行。 |
| `TypedHole.domain` | finite set/predicate | 合法取值集合或可检查谓词。 |
| `TypedHole.source_status` | enum | `SOURCE_SPECIFIED`、`DERIVED` 或 `OPEN`，区分来源事实、可逆推导和待探索选择。 |
| `Binding.assignments` | map | 从 `hole_id` 到具体值的全函数；只覆盖必填孔时才称完整绑定。 |
| `Binding.anchor_map` | map | 每个 hook、状态或代码差分对应的 $H_t$ 文件与符号位置。 |
| `Binding.constraint_results` | list | 每条绑定约束的 `PASS/FAIL/UNKNOWN` 及证据。`UNKNOWN` 不得按 `PASS` 处理。 |
| `Binding.revision` | integer | 父 Harness 或绑定改变时递增。 |
| `Binding.status` | enum | `PARTIAL`、`VALID`、`INVALID`、`STALE`。Harness 提交后旧绑定全部转为 `STALE`。 |

`binding_constraints` 是有限约束集合，至少包括类型兼容、hook 可达、读写权限、依赖存在、顺序可满足和禁止副作用。完整绑定当且仅当所有必填孔有值且所有硬约束为 `PASS`。

#### `InterventionHypothesis`

| 字段 | 类型 | 定义 |
| --- | --- | --- |
| `hypothesis_id` | string | 跨 revision 不变的逻辑身份。 |
| `node_kind` | enum | `GENERAL`、`PARAMETERIZED`、`CONCRETE` 或 `FREE_DERIVED`。 |
| `grammar_program` | AST | 由有限语法构成的有类型程序；保存操作顺序和数据依赖。 |
| `typed_holes` | `TypedHole[]` | 尚需绑定的 hook、状态、工具、参数或实现策略。 |
| `binding_constraints` | predicate[] | 对孔之间及孔与目标 Harness 之间的硬约束。 |
| `applicability_scope` | predicate | 对 regime $z$ 的可执行布尔谓词；默认不等于“所有任务”。 |
| `predicted_activation` | observable predicate | 干预被触发和执行时必须出现的可观测事件。 |
| `predicted_mediators` | ordered predicate[] | 从激活到任务效果之间应出现的中间 trace 变化；次序必须与因果链一致。 |
| `predicted_target_effect` | endpoint specification | 目标能力端点、方向、最小有意义效应与测量窗口。 |
| `predicted_regressions` | endpoint specification[] | 可能受损的能力族、方向与容忍界限；空数组表示来源未报告，而非不存在风险。 |
| `fallback` | executable policy | 验证失败、运行异常或回归触发时的恢复动作。 |
| `provenance` | reference[] | `SourcePacket` anchor、自主生成记录或上游节点 revision。 |
| `support_witnesses` | witness id[] | 与当前 revision 一致的正证据索引。 |
| `contradict_witnesses` | witness id[] | 与当前 revision 的激活、机制、效果或范围预测冲突的证据索引。 |
| `unresolved_witnesses` | witness id[] | 观测不足、测量失败或多重解释无法区分的证据索引。 |
| `status` | enum | `ACTIVE`、`NONINSTANTIABLE_PARENT`、`INERT`、`DEPRECATED` 或 `UNRESOLVED`。 |
| `revision` | `NodeRevision` | 当前节点修订号、父 revision、变更差分、触发 witness 和时间。 |
| `llm_call_ids` | call id[] | 产生或修订当前节点语义字段的全部 `LLMCallRecord`；纯程序构造的初始化节点为空数组。 |
| `field_validation_status` | map | 从每个模型提出字段映射到 `SOURCE_VERIFIED/CODE_VERIFIED/TRACE_VERIFIED/EMPIRICALLY_VERIFIED/REJECTED/UNKNOWN` 及核验依据；节点可见不表示所有字段均已验证。 |

`predicted_activation`、每个 mediator 和每个 endpoint 都必须给出 `{measurement, expected_direction, observation_window, missing_policy}`。`missing_policy` 只能取 `FAIL`、`UNRESOLVED` 或 `NOT_APPLICABLE`，不得把缺失测量计为成功。

#### 关系边与修订记录

`RelationEdge={edge_id,source,target,relation_type,guard,support_witnesses,contradict_witnesses,status,revision,llm_call_ids}`。`llm_call_ids` 只记录提出或解释该关系的调用；关系是否成立仍由对应来源、结构证明或最小经验对照决定。

| `relation_type` | 方向与含义 |
| --- | --- |
| `SPECIALIZES` | `source` 比 `target` 更具体，即 $source\preceq target$。 |
| `REQUIRES` | 执行 `source` 前必须已满足 `target` 或指定 guard。 |
| `CONFLICTS` | `source` 与 `target` 在 guard 成立时不能同时启用；该关系对称存储。 |
| `ALTERNATIVE_TO` | 两节点解决同一义务，但机制或资源路径不同。 |
| `DERIVED_FROM` | 自主候选或抽象节点由一个或多个既有节点推导。 |
| `SUPERSEDES` | 新 revision 取代旧 revision 的可直接实例化地位，但不删除旧记录。 |

`RevisionRecord={revision_id,object_type,object_id,before_revision,after_revision,operation,witness_ids,llm_call_ids,validation_record_ids,reversible,inverse_operation,timestamp}`。经验结构变更没有 `witness_ids` 时非法；来源目录的离线 revision 必须改由来源锚点和 `validation_record_ids` 支撑。`llm_call_ids` 可以为空，但不能替代 witness 或验证记录。

#### 辅助复合类型

| 类型 | 完整字段 | 约束 |
| --- | --- | --- |
| `HarnessVersion` | `{harness_id,revision,parent_revision,source_tree,config,dependency_lock,model_interface,tool_interfaces,lifecycle_hooks,state_schema,observability_schema,fallback_entry,commit_record}` | `source_tree`、配置和依赖锁共同决定可重放版本；缺一项不得作为配对父版本。 |
| `ArtifactRef` | `{artifact_id,artifact_type,uri,version,locator,license,retrieved_at}` | `uri` 可指本地已保存对象；`version` 不得使用浮动分支名代替 commit。 |
| `EvidenceRecord` | `{claim_id,dataset,split,metric,baseline,reported_value,uncertainty,repetitions,conditions,anchor}` | 没有报告的方差、重复数或条件显式记为 `UNKNOWN`。 |
| `ValidationRecord` | `{validation_id,validator_revision,target_id,field_or_operation,input_revision,result,evidence_refs,reason,created_at}` | `result` 取 `PASS/FAIL/UNKNOWN`；记录程序检查或人工复核，不允许由被核验的同一次模型调用自证。 |
| `LLMCallLedger` | `{ledger_id,schema_revision,optimizer_config_revision,records,latest_revision,storage_ref}` | `records` 是按开始、响应、解析、核验事件追加的 `LLMCallRecord[]`；失败与拒绝调用不得删除，revision 只能单调增加。 |
| `EndpointSpec` | `{endpoint_id,metric,direction,score_lower,score_upper,minimum_effect,observation_window,aggregation,missing_policy}` | `direction` 统一转换为“越大越好”；`score_lower<score_upper` 给出单次分数硬边界；`aggregation` 在运行前冻结。 |
| `NodeRevision` | `{revision_id,parent_revision,program_delta,scope_delta,prediction_delta,relation_delta,trigger_witnesses,llm_call_ids,validation_record_ids,created_at}` | 任一 delta 为空时保存空值；在线经验修订不能省略触发 witness，离线来源修订必须保留来源验证记录。 |
| `HookDescriptor` | `{hook_id,lifecycle_phase,signature,predecessors,successors,readable_state,writable_state}` | hook 必须能映射到 `HarnessVersion.source_tree` 中的确定锚点。 |
| `Capability` | `{capability_id,kind,input_type,output_type,permissions,availability_guard,version}` | `kind` 为状态读写、工具、模型能力或验证器；权限按最小授权计算。 |
| `UnresolvedCondition` | `{condition_id,question,decision_relevance,required_observation,next_probe,status}` | `status` 为 `OPEN`、`RESOLVED` 或 `UNREACHABLE`；只有会改变可行性、结构或决策的问题进入检索循环。 |
| `OrganizationProtocol` | `{finite_grammar_revision,type_system_revision,alignment_rules,semantic_compilation_prompt_revision,semantic_compilation_parser_revision,semantic_field_verifier_revision,anti_unification_rules,description_length_config,index_schema,audit_checks}` | 全部字段在目录构建前冻结；`alignment_rules` 决定论文/代码声明如何对齐，三个 semantic compilation revision 固定 LLM 输入、解析和逐字段核验，`audit_checks` 必须覆盖来源可达、节点可重构、偏序无环和索引可复算。 |
| `SchedulerState` | `{protocol_revision,generation_id,strata_state,exposure_ledger,coverage_state,open_obligations,anchor_registry}` | `strata_state` 保存各层剩余任务，`coverage_state` 保存训练轮换进度，`anchor_registry` 保存每个 anchor 的来源、最后通过代际与严重度。 |
| `RoundLedger` | `{generation_id,parent_harness,trace_ids,experiment_ids,witnesses,llm_call_ids,llm_call_ledger_revision,exposure_record_ids,structural_operations,candidate_decisions,select_disclosure_status,resource_status}` | `witnesses` 是按产生顺序保存的完整 `EmpiricalWitness[]`；`llm_call_ids` 保存本代所有成功、失败和被拒调用；其余字段只追加。`select_disclosure_status` 为 `HIDDEN` 或 `DISCLOSED_TO_GENERATION_PATH`，控制同代是否允许返回生成。 |
| `FrozenTestPackage` | `{experiment_id,harness_version,catalog_id,empirical_revision,train_protocol_revision,optimizer_config_revision,llm_call_ledger_revision,model_and_tool_versions,evaluator_revision,seeds,frozen_at}` | 任一字段改变都创建新的 `experiment_id`；包内对象全部只读。终局测试不再发起任何 `OptimizerLLM` 调用。 |

文中简写 `endpoint specification`、`hook descriptor`、`capability` 和 `question` 分别指上表的 `EndpointSpec`、`HookDescriptor`、`Capability` 和 `UnresolvedCondition`，不允许各模块另造不兼容结构。

兼容名称只有一组确定映射：`paper_only`=`PAPER_ONLY`，`code_only`=`CODE_ONLY`，`currently_indistinguishable`=`CURRENTLY_INDISTINGUISHABLE`；`SPECIALIZES / REQUIRES / CONFLICTS / ALTERNATIVE_TO / DERIVED_FROM / SUPERSEDES` 是六种独立关系类型的并列简写；`Split(e)` 是 $\operatorname{Split}(e)$ 的代码名称；`split/specialize/merge` 分别指 `SPLIT_NODE`、`SPECIALIZE_SCOPE` 和 `MERGE_NODES`，不引入额外操作。

### 需求、trace、候选、实验与 witness 字段

#### `Regime` 与 `InterventionNeed`

`Regime={task_family,dataset_split,instance_id,executor_model,model_config,tool_versions,harness_version,evaluator_version,environment_id,time_window}`。任一字段变化都生成新的 regime 身份；可通过显式投影忽略不相关字段，但不能静默合并。

| `InterventionNeed` 字段 | 类型 | 定义 |
| --- | --- | --- |
| `obligations` | obligation id[] | 当前必须改变和必须保留的行为集合。 |
| `available_hooks` | hook descriptor[] | $H_t$ 可插入干预的生命周期位置、调用签名与先后关系。 |
| `available_state_and_tools` | capability[] | 可读取/写入状态、可调用工具及权限边界。 |
| `immutable_constraints` | predicate[] | 模型、接口、评测协议、数据隔离和安全方面不能被候选改变的条件。 |
| `forbidden_effects` | predicate[] | 即使提高目标得分也不允许发生的副作用。 |
| `current_regime` | `Regime` | 该检索请求适用的完整运行条件。 |
| `unresolved_conditions` | question[] | 仅靠当前信息无法判断的依赖；每项应可转化为 probe 或显式不可达结论。 |
| `source_call_id` | call id | 产生该 need revision 的 `TRACE_OBLIGATION_AND_NEED_DIAGNOSIS`；纯人工预注册 need 使用 `NONE`。 |
| `validation_record_ids` | validation id[] | trace、代码、状态版本和数据角色核验记录；缺失时 need 不得进入检索。 |

#### trace 图与 `TraceObligation`

| `ExecutionTrace` 字段 | 类型 | 定义 |
| --- | --- | --- |
| `task_id` | string | benchmark 任务实例的稳定标识，并可连接到唯一 `ExposureRecord`。 |
| `split_role` | enum | `TRACE`、`SELECT`、`ANCHOR` 或 `FINAL_TEST`；决定该运行可支持的结论。 |
| `generation_id` | integer | 产生该运行的 Harness 外层代际 $g$；最终测试为冻结后的终局代际。 |
| `harness_version` | version id | 实际运行的父 Harness 或候选沙箱版本；候选运行还必须记录 `parent_harness`。 |
| `model_and_tool_versions` | map | 模型、provider、采样参数、工具协议、容器和依赖的精确版本。 |
| `seed` | object | 模型、环境、任务和工具随机性的种子；不可控随机源显式列出。 |
| `trace_graph` | graph | 下式 $T=(V_T,E_D,E_C,E_S,E_A)$ 的完整事件图。 |
| `final_output` | artifact ref/null | 执行 agent 的最终产物或输出；异常终止时可为 `null`。 |
| `metric_vector` | map | 各预注册端点的原始值、方向、评测 revision 与缺失状态。 |
| `termination_status` | enum | `SUCCESS`、`TASK_FAIL`、`TIMEOUT`、`CRASH`、`TOOL_FAIL`、`EVALUATOR_FAIL` 或 `CANCELLED`。 |
| `artifact_refs` | ref[] | 上下文快照、工具输入输出、日志、状态差分与评测产物的不可变引用。 |

一次执行 trace 表示为

$$
T=(V_T,E_D,E_C,E_S,E_A).
$$

| 项 | 定义 |
| --- | --- |
| $V_T$ | 事件节点集合；节点为 `{event_id,event_type,start,end,input_ref,output_ref,status,actor,hook}`。 |
| $E_D$ | 数据依赖边：目标事件读取了源事件产生的数据。 |
| $E_C$ | 控制依赖边：源事件决定目标事件是否或何时执行。 |
| $E_S$ | 状态读写边：两个事件通过同一状态槽发生依赖。 |
| $E_A$ | 实现锚点边：trace 事件指向产生它的 Harness 文件、符号、配置项或生命周期 hook；无法可靠定位时保持为空并记录不确定性。 |

`event_type` 至少覆盖 `MODEL_CALL`、`TOOL_CALL`、`MEMORY_READ`、`MEMORY_WRITE`、`CONTEXT_EDIT`、`PLAN_UPDATE`、`VALIDATION`、`RETRY`、`COMMIT` 和 `EVALUATION`。原始 payload 通过内容地址引用保存，结构算法只读取声明过的字段。

| `TraceObligation` 字段 | 定义 |
| --- | --- |
| `obligation_id` | 稳定标识。 |
| `obligation_type` | `CHANGE` 或 `PRESERVE`。 |
| `failure_or_success_signature` | 可复算的事件模式；失败产生改变义务，成功产生保留义务。 |
| `trigger` | 该模式首次成立的事件与条件。 |
| `implicated_slice` | 从图中抽出的最小相关节点、边和状态槽。 |
| `implementation_anchors` | 当前 Harness 中可能改变该切片的文件、符号和 hook。 |
| `required_trace_change` | 期望新增、删除、重排或数值改变的可观测 trace 条件。 |
| `preserved_behavior` | 候选实施后仍必须成立的 trace/任务端点。 |
| `current_regime` | 产生义务的 regime。 |
| `reproducibility` | 相同配置下复现次数、总次数和复现率。 |
| `uncertainty` | 缺失日志、竞争解释与评测噪声列表。 |
| `weight` | 非负义务重要度；在实验前冻结，用于覆盖率。 |
| `status` | `OPEN`、`COVERED`、`RESOLVED`、`DEFERRED` 或 `UNREACHABLE`。 |
| `diagnosis_call_id` | 产生该义务的 `TRACE_OBLIGATION_AND_NEED_DIAGNOSIS`；程序从预注册规则直接产生时为 `NONE`。 |
| `validation_record_ids` | trace 事件、实现锚点、状态 revision、数据角色和复现检查的记录 ID。 |

#### `CandidateInterventionIR` 与 `FrozenCandidate`

`OptimizerLLM` 的知识补全、自由探索和反例修订都先进入同一中间表示，不能直接写入候选代码库。

| `CandidateInterventionIR` 字段 | 定义 |
| --- | --- |
| `ir_id` | 不可变 IR revision ID；任何语义或代码字段变化都创建新 ID。 |
| `source_call_id` | 直接产生该 revision 的 `KNOWLEDGE_INTERVENTION_COMPLETION`、`FREE_INTERVENTION_PROPOSAL` 或 `CANDIDATE_BINDING_CRITIQUE_AND_REVISION` 调用。 |
| `source_channel` | `KNOWLEDGE/FREE/CRITIQUE_REVISION`；只表示输入隔离通道，不影响后续 gate。 |
| `parent_harness` | IR 所依附的确切父 Harness revision。 |
| `hypothesis_revision` | 知识通道绑定的节点 revision，或自由通道待编译的 `FREE_DERIVED` 节点 revision。 |
| `grammar_program` | 有限干预语法程序；知识补全不得修改草图中冻结的操作与顺序。 |
| `binding` | 完整或待核验的 typed-hole 赋值及代码锚点。 |
| `code_patch` | 相对 `parent_harness` 的规范化代码与配置差分。 |
| `predicted_activation` | 修改真正触发时应出现的可测量事件。 |
| `predicted_mediators` | 从激活到目标结果之间有序且可测量的中介链。 |
| `predicted_target_effect` | 目标端点、方向、最小效应与观察窗口。 |
| `predicted_regressions` | 可能受损端点、方向与容忍界限。 |
| `preservation_requirements` | 从 `PRESERVE` 义务继承的 trace 与任务行为约束。 |
| `fallback` | 静态失败、运行失败和回归分别触发的可执行恢复策略。 |
| `unresolved_conditions` | 尚需 discovery witness 或依赖检索回答的问题。 |
| `ancestor_ir_ids` | 该 revision 的全部直接父 IR；首次生成为空。 |
| `llm_call_ids` | 对当前 IR 有语义贡献的完整调用谱系。 |
| `validation_status` | 每一硬 gate 的 `PASS/FAIL/UNKNOWN`；只有全部硬项 `PASS` 才能冻结。 |

候选记为

$$
c=(\nu,b,\Delta H,\hat y).
$$

| 分量/字段 | 定义 |
| --- | --- |
| $\nu$ | 候选引用的确切 `hypothesis_id@revision`。 |
| $b$ | 对该 revision 的完整且有效绑定。 |
| $\Delta H$ | 相对父 Harness 的可应用代码与配置差分；必须通过静态接口检查。 |
| $\hat y$ | 对激活、mediator、目标效果和各回归端点的预注册预测。 |
| `candidate_id` | 由父 Harness revision、节点 revision、绑定 revision 和差分内容确定的稳定标识。 |
| `parent_harness` | 候选必须附着的 $H_t$ revision；父版本变化后候选自动失效。 |
| `covered_obligations` | 候选声明能够处理的义务及逐项理由。 |
| `fallback_plan` | 运行时失败和实验失败分别采用的恢复动作。 |
| `origin` | `KNOWLEDGE_BOUND` 或 `FREE_DERIVED`；两类候选使用相同验证协议。 |
| `provenance` | 来源节点、SourcePacket anchor、自由探索运行和生成提示的完整引用链。 |
| `ir_ids` | 形成该候选的全部 `CandidateInterventionIR` revision，末项是通过 gate 的直接来源。 |
| `hard_gate_status` | 类型、接口、权限、状态效应、依赖、保留、fallback 与隔离检查的逐项结果；必须全部为 `PASS`。 |
| `llm_call_ids` | 从语义编译、诊断、候选生成到受控修订的调用谱系；只用于复现和审计。 |
| `frozen_at` | 候选冻结时间与冻结协议 revision；之后任何变化必须创建新 candidate ID。 |
| `equivalence_status` | `UNIQUE`、`EXACT_DUPLICATE`、`PROVED_REWRITE_EQUIVALENT` 或 `CURRENTLY_INDISTINGUISHABLE`；最后一项只表示现有 witness 未能区分，禁止据此合并节点。 |
| `status` | `FROZEN`、`RUNNING`、`ACCEPTED`、`REJECTED`、`STALE` 或 `UNRESOLVED`。 |

#### `CandidateWitnessExperiment`

| 字段 | 类型 | 定义 |
| --- | --- | --- |
| `experiment_id` | string | 实验计划的稳定标识。 |
| `candidate_id` | string | 唯一待检候选。组合实验另列全部组件，但仍生成一个组合候选。 |
| `witness_id` | string | 计划产生的 witness 标识；运行失败也必须写入。 |
| `witness_type` | enum | `STATIC_CHECK`、`ACTIVATION_PROBE`、`FAILURE_REPLAY`、`MEDIATOR_PERTURBATION`、`MEDIATOR_ABLATION`、`PAIRED_TARGET`、`PAIRED_PRESERVATION`、`FRESH_CONFIRMATION`、`FACTORIAL_COMBINATION` 或 `CROSS_TASK_REPLICATION`。 |
| `matched_parent` | Harness revision | 配对对照所用父 Harness，必须与候选父版本一致。 |
| `task_and_seed` | object | 任务实例、采样来源、随机种子及选择概率。 |
| `data_role` | enum | `TRACE`、`SELECT`、`ANCHOR` 或 `SYNTHETIC_PROBE`；必须与 `confirmation_role` 相容。 |
| `perturbation_or_ablation` | object/null | 对输入、状态、组件或机制链实施的唯一受控变化。 |
| `predicted_partition` | map | 活跃前沿中每个假设对本实验的唯一预期结果类别。 |
| `execution_cost` | vector | 模型 token、工具调用、GPU/CPU、墙钟和人工审核的预计量。 |
| `regression_risk` | object | 风险端点、影响范围、隔离方式和恢复能力。 |
| `confirmation_role` | enum | `DISCOVERY` 或 `CONFIRMATION`；只有后者可用于 Harness 提交。 |
| `exposure_record_id` | string | 本实验所用任务的暴露记录；合成 probe 指向其构造所依赖的来源任务记录。 |
| `proposal_call_ids` | call id[] | 提出或补全该实验的 `WITNESS_EXPERIMENT_PROPOSAL`；纯程序枚举实验为空数组。 |
| `validation_record_ids` | validation id[] | 可执行性、数据角色、风险、predicted partition 与隔离检查记录；缺失时不得执行。 |

实验结果类别固定为：`HARD_FAIL`、`INERT`、`ACTIVATED_NO_MEDIATOR`、`MEDIATOR_NO_GAIN`、`GAIN_WITHOUT_REGRESSION`、`GAIN_WITH_REGRESSION`、`UNRESOLVED`。每个前沿假设对一个实验必须映射到其中恰好一类；没有可检验预测时映射为 `UNRESOLVED`，以保证分区互斥且完备。

角色兼容规则固定为：`TRACE` 与 `SYNTHETIC_PROBE` 只能标为 `DISCOVERY`；`SELECT` 只能在候选冻结后标为 `CONFIRMATION` 并用于 target 端点；`ANCHOR` 可标为 `CONFIRMATION`，但只进入对应 preserve 端点。违反该映射的实验计划在执行前即为 `HARD_FAIL`。同一任务一旦以 `TRACE` 或其他可见方式影响该候选，后续即使改标 `SELECT` 也不能恢复独立性。

#### `EmpiricalWitness`

| 字段 | 定义 |
| --- | --- |
| `witness_id` | 不可复用的稳定标识。 |
| `experiment_id` | 生成该记录的实验计划；外部来源 witness 指向来源提取任务。 |
| `task_and_regime` | 完整任务实例和 regime。 |
| `data_role` | 产生该 witness 的 `TRACE/SELECT/ANCHOR/SYNTHETIC_PROBE/EXTERNAL_SOURCE` 角色。 |
| `harness_version` | 实际执行的父 Harness 与候选差分版本。 |
| `hypothesis_revision` | 被检节点的确切 revision。 |
| `binding` | 实际绑定及其 revision。 |
| `intervention_or_probe` | 执行的代码差分、probe、消融或扰动。 |
| `activation_observation` | 激活谓词的原始测量和 `PASS/FAIL/MISSING`。 |
| `mediator_observation` | 每个 mediator 的原始测量、顺序与状态。 |
| `target_outcome` | 目标端点原始值、评测版本及与父 Harness 的配对差。 |
| `preservation_outcomes` | 各旧能力端点原始值及配对差。 |
| `repetitions_and_seeds` | 重复次数、全部种子及独立性分组。 |
| `environment` | 依赖锁、容器/系统、硬件和外部服务版本。 |
| `selection_metadata` | 实验为何被选中、候选集合、选择分数与抽样概率。 |
| `exposure_record_id` | 对应任务披露历史；外部来源 witness 为 `null`。 |
| `confidence_status` | `NOT_USED`、`ACCUMULATING`、`ACCEPT_BOUND`、`REJECT_BOUND` 或 `INCONCLUSIVE`。 |
| `outcome_class` | 七类实验结果之一。 |
| `supersedes` | 若本记录纠正旧记录，指向旧 witness；否则为 `null`。 |
| `interpretation_call_ids` | 对该原始 observation 提出语义解释的 `WITNESS_STRUCTURE_INTERPRETATION` 调用；原始测量本身不依赖这些解释。 |
| `validation_record_ids` | 将模型解释映射到预测、节点、绑定和合法结构操作触发条件的核验记录。 |

### 组织、检索与候选生成公式

#### 特化偏序

定义 $\nu_i\preceq\nu_j$ 表示 $\nu_i$ 比 $\nu_j$ 更具体，当且仅当以下五个条件同时成立：

1. $\nu_i$ 的语法程序可由 $\nu_j$ 填孔或增加不改变原有先后关系的 guard/validation 得到；
2. $D_b(\nu_i)\subseteq D_b(\nu_j)$，其中 $D_b$ 是合法绑定集合；
3. $A(\nu_i)\Rightarrow A(\nu_j)$，其中 $A$ 是适用谓词；
4. $P(\nu_i)\supseteq P(\nu_j)$，其中 $P$ 是可检验预测集合，即具体节点不得删除父节点预测；
5. 两节点的副作用类别和 fallback 兼容。

在规范化 AST、规范化谓词和类型等价关系下，$\preceq$ 满足自反、反对称和传递。无法证明任一条件时两节点保持不可比，不能凭语义相似度添加偏序边。

#### 抽象的描述长度收益

对拟合并的具体节点 $g_1,\ldots,g_m$，公共抽象 $g$ 及恢复各子节点的绑定 $b_1,\ldots,b_m$，定义

$$
G(g)=\sum_{i=1}^{m}DL_{raw}(g_i)-\left[DL_{raw}(g)+\sum_{i=1}^{m}DL_{raw}(b_i)\right].
$$

| 符号 | 定义 |
| --- | --- |
| $m\ge2$ | 参与本次抽象的具体节点数。 |
| $DL_{raw}(x)$ | 按冻结编码表计算的原始描述长度，单位为 bit；AST 操作、类型、谓词、常量和边分别有固定编码成本。 |
| $g_i$ | 第 $i$ 个原始具体节点，包含程序、条件和预测。 |
| $g$ | 由有类型 anti-unification 得到的候选公共父节点。 |
| $b_i$ | 从 $g$ 恢复 $g_i$ 的孔赋值和附加约束。 |
| $G(g)$ | 使用公共父节点后的净压缩收益；越大表示共享结构越多。 |

统一原始描述长度由冻结编码配置 $\Theta_{DL}$ 计算：

$$
DL_{raw}(x)=\ell_{head}(\operatorname{type}(x))
+\sum_{u\in Ops(x)}\ell_{op}(u)
+\sum_{v\in Types(x)}\ell_{type}(v)
+\sum_{r\in Pred(x)}\ell_{pred}(r)
+\sum_{q\in Const(x)}\ell_{const}(q)
+\sum_{d\in Edges(x)}\ell_{edge}(d).
$$

$Ops(x)$、$Types(x)$、$Pred(x)$、$Const(x)$ 和 $Edges(x)$ 分别是规范化对象中的操作、类型、谓词、常量和关系边多重集；$\ell_{head}$ 是对象头编码长度；其余 $\ell_*$ 是 $\Theta_{DL}$ 中各 token 的前缀码长度，均为非负 bit 且满足 Kraft 条件。未知 token 使用固定 escape code 加其字节长度，不允许取零成本。$DL_{max}>0$ 是单个部分绑定允许的最大原始长度，由候选搜索配置给出。

只有 $G(g)>\epsilon_{DL}$、每个 $g_i$ 可由 $(g,b_i)$ 无损重构、留一 regime 检查通过且未发现稳定区分条件时才执行 `MERGE_NODES`。$\epsilon_{DL}\ge0$ 在实验前固定，用于抵消微小编码差异。

#### 部分绑定搜索分数

$$
J(p)=\operatorname{Coverage}(p,\mathcal O_t)
-\lambda_1\overline{DL}(p)-\lambda_2U(p)-\lambda_3R(p).
$$

| 项 | 定义与范围 |
| --- | --- |
| $p$ | 一个部分绑定；允许仍有未填孔，但不得违反已可检查的硬约束。 |
| $\operatorname{Coverage}(p,\mathcal O_t)$ | 被 $p$ 的可达操作与预测覆盖的开放义务权重之和除以全部开放义务权重，范围 $[0,1]$。 |
| $\overline{DL}(p)$ | 已选择操作、孔赋值和新增约束的归一化描述长度，等于 $\min(1,DL_{raw}(p)/DL_{max})$，范围 $[0,1]$。 |
| $U(p)$ | 必填孔、依赖和预测中仍未决项的加权比例，范围 $[0,1]$。 |
| $R(p)$ | 禁止效应邻近度、不可逆副作用、回归端点暴露和 fallback 缺失组成的归一化风险，范围 $[0,1]$。 |
| $\lambda_1,\lambda_2,\lambda_3\ge0$ | 复杂度、未决性和风险惩罚；在一次候选生成批次开始前冻结。 |

$J$ 中三个数据项按以下公式计算：

$$
\operatorname{Coverage}(p,\mathcal O_t)=
\frac{\sum_{o\in\mathcal O_t^{open}}\kappa_o\,\mathbf 1[p\rightsquigarrow o]}
{\sum_{o\in\mathcal O_t^{open}}\kappa_o},
$$

$$
U(p)=\frac{\sum_{u\in Dep(p)}\eta_u\,\mathbf 1[status_p(u)\in\{UNBOUND,UNKNOWN\}]}
{\sum_{u\in Dep(p)}\eta_u},
$$

$$
R(p)=\rho_s r_{scope}(p)+\rho_x r_{external}(p)+
\rho_b r_{rollback}(p)+\rho_p r_{preserve}(p).
$$

$\mathcal O_t^{open}$ 是状态为 `OPEN` 的义务集合，$\kappa_o>0$ 是义务字段 `weight`，$p\rightsquigarrow o$ 表示部分绑定的剩余合法扩展中至少存在一个能实现义务 $o$ 的完整绑定。$Dep(p)$ 是必填孔、硬依赖与必要预测的集合，$\eta_u>0$ 是依赖重要度，$status_p(u)$ 是当前解析状态。分母为空时对应的 `Coverage` 或 $U$ 定义为 0。风险分量和 $\rho_*$ 与“实验成本、风险与选择”小节完全相同，只是作用对象由实验换为部分绑定；禁止维护第二套含义不同的风险配置。

$J$ 只用于 beam/branch-and-bound 的扩展顺序。任何硬约束失败都会立即剪枝；高 $J$ 不能覆盖硬失败，也不能作为提交证据。并列时依次选择更低风险、更短描述和稳定标识更小的部分绑定。$B\in\mathbb N^+$ 是每一搜索深度保留的最大部分绑定数；仅当未保留分支的可证明 $J$ 上界不超过第 $B$ 项时，top-$B$ 剪枝才可作为搜索停止依据。没有开放义务时 `Coverage` 定义为 0，并跳过候选生成而非依赖除零结果。

确定性去重所用 rewrite rule 必须属于冻结集合 $\mathcal Q$。每条规则包含匹配 AST、替换 AST、类型侧条件和语义保持证明或穷举验证域；不在 $\mathcal Q$ 中的“看起来等价”只能标为 `CURRENTLY_INDISTINGUISHABLE`。

### 主动实验、任务效果与提交公式

#### 活跃前沿及权重

活跃前沿 $F_t$ 由状态为 `ACTIVE`、具有至少一个有效完整绑定、未被同内容候选去重且不是仅供组织的父节点组成。为避免父子重复计数，`NONINSTANTIABLE_PARENT` 不进入 $F_t$。

对 $h=(\nu,b)\in F_t$ 定义非概率优先级原始质量

$$
\widetilde\omega_t(h)=q_{src}(h)
\frac{1+\log(1+n^+_{ind}(h))}{1+n^?_{ind}(h)}
\exp[-\gamma\,\Delta t(h)],
$$

其中 $q_{src}(h)=\max_{s\in Src(h)}q_{grade(s)}$，且 $q_{grade(A)}=q_A$、$q_{grade(B)}=q_B$、$q_{grade(C)}=q_C$、$q_{grade(D)}=q_D$；当 $Src(h)=\varnothing$ 时取 $q_{src}(h)=q_{free}$。`Src(h)` 只包含候选实际采用并可追踪到 anchor 的来源，检索后未采用的来源不计入。

并归一化为

$$
\omega_t(h)=\frac{\widetilde\omega_t(h)}{\sum_{h'\in F_t}\widetilde\omega_t(h')},
\qquad
W(A)=\sum_{h\in A\cap F_t}\omega_t(h).
$$

| 参数 | 定义 |
| --- | --- |
| $q_{src}(h)\in[q_{min},1]$ | 由 `source_grade` 映射的来源完整度：$q_A\ge q_B\ge q_C\ge q_D\ge q_{min}>0$；具体数值在实验配置中冻结。有多个独立来源时取其中最高等级，不相加，避免重复来源放大质量。纯自主候选取 $q_{free}\in[q_{min},1]$；混合候选按其被实际采用的节点来源计算。 |
| $n^+_{ind}(h)$ | 支持该 revision 的独立 witness 组数；同一任务、种子族和环境的重复只计一组。 |
| $n^?_{ind}(h)$ | 尚未解决且测量充分的独立 witness 组数；纯日志缺失不重复惩罚。 |
| $\Delta t(h)$ | 距最近一次支持或修订的结构轮次数。 |
| $\gamma\ge0$ | 新鲜度衰减率；$\gamma=0$ 表示不衰减。 |
| $q_{min}>0$ | 防止尚无强来源的自主候选永远无法被选择的最小质量。 |

矛盾 witness 不直接通过减小权重“软处理”，而应触发删除绑定、收紧范围、拆分节点或保持未决。$\omega_t$ 只服务于实验分区，不是节点正确概率，也不能决定提交；$w_t$ 始终只表示第 $t$ 轮新增的 witness。

若 $F_t=\varnothing$，$\omega_t$ 与 `Split` 均不计算，规划器返回 `NO_ACTIVE_HYPOTHESIS` 并转入重新检索或自由探索；不得用空分母构造均匀权重。

#### 分裂分数

$$
\operatorname{Split}(e)=1-
\sum_{o\in\mathcal Y_e}
\left(\frac{W(\mathcal V_{e,o})}{W(\mathcal V_t)}\right)^2.
$$

| 符号 | 定义 |
| --- | --- |
| $\mathcal Y_e$ | 前述七类实验结果中，本实验可观测的有限类别集合，必须包含 `UNRESOLVED`。 |
| $\mathcal V_{e,o}$ | 活跃前沿中预测实验 $e$ 会得到唯一结果 $o$ 的假设—绑定单元集合。 |
| $W(\mathcal V_t)$ | 记号上作用于整个版本空间，计算时等于 $W(F_t)=1$；非活跃祖先和无效绑定质量为零。 |
| $W(\mathcal V_{e,o})$ | 结果分区内归一化权重之和。各分区互斥且并集为 $F_t$。 |

该式等于预测结果分布的 Gini impurity，范围为 $[0,1-1/|\mathcal Y_e|]$。若所有假设预测同一结果，分数为零；分区越均衡，分数越高。

#### 实验成本、风险与选择

令可执行实验集合为 $\mathcal E_t^{safe}$：静态接口、安全、隔离、回退和数据泄漏检查全部通过的实验。选择规则为

$$
e_t=\arg\max_{e\in\mathcal E_t^{safe}}
\left[\operatorname{Split}(e)-\lambda_c\widetilde C(e)-\lambda_r\widetilde R(e)\right].
$$

其中

$$
\widetilde C(e)=\sum_k\omega_k
\min\left(1,\frac{C_k(e)}{B_k}\right),\qquad \sum_k\omega_k=1,
$$

$C_k(e)$ 是 token、工具调用、计算时间、墙钟或人工审核中的第 $k$ 类预计消耗，$B_k>0$ 是协议预先声明的对应参考单位，不能依据本实验的观测结果回调；$\omega_k\ge0$ 是成本维度权重。若某类成本不纳入比较，令其 $\omega_k=0$ 而不是删除字段。风险定义为

$$
\widetilde R(e)=
\rho_s r_{scope}(e)+
\rho_x r_{external}(e)+
\rho_b r_{rollback}(e)+
\rho_p r_{preserve}(e),
\qquad
\rho_s+\rho_x+\rho_b+\rho_p=1.
$$

$r_{scope}$ 是候选可写状态和可触达任务的归一化比例，$r_{external}$ 是可逆外部副作用等级，$r_{rollback}$ 是回滚后无法恢复状态的比例，$r_{preserve}$ 是受影响保留端点的加权比例；四者均在 $[0,1]$。$\rho_s,\rho_x,\rho_b,\rho_p\ge0$ 是实验前冻结的风险维度权重。不可逆外部副作用直接从 $\mathcal E_t^{safe}$ 移除，不依赖该软风险分数。

$\lambda_c,\lambda_r\ge0$ 控制消歧收益与消耗/风险的取舍，不是总预算限制。并列时依次选择风险更低、可区分节点更多、成本更低和稳定标识更小的实验。

若 $\mathcal E_t^{safe}=\varnothing$，返回 `NO_SAFE_EXPERIMENT`；若最高目标值不大于预设最小信息阈值 $\epsilon_{info}$，返回 `NO_INFORMATIVE_EXPERIMENT`。这两种返回均不是方法收敛证明。

#### 配对任务差值

对候选 $c$ 和第 $i$ 个匹配任务—种子单元，定义

$$
D_i^{(k)}(c)=R_i^{(k)}(H_t\oplus c)-R_i^{(k)}(H_t),
$$

| 符号 | 定义 |
| --- | --- |
| $i$ | 同一任务实例、数据版本、种子、模型配置、工具版本和评测器组成的匹配单元。 |
| $k$ | 端点索引；`target` 表示目标能力，$j$ 表示第 $j$ 个保留能力族。 |
| $R_i^{(k)}(H)$ | Harness $H$ 在匹配单元 $i$ 上的预注册标量得分；方向统一为越大越好。 |
| $H_t\oplus c$ | 在隔离环境中把 $c$ 的差分原子应用于父 Harness；不表示已经提交。 |
| $D_i^{(k)}(c)$ | 候选相对父 Harness 的配对改变量。若原指标越小越好，先乘以 $-1$ 再计算。 |

发现流可用于结构学习，但提交统计只使用 `confirmation_role=CONFIRMATION` 的新鲜匹配单元。若确认任务自适应抽样，必须记录抽样概率并使用与该策略相容的 anytime-valid 估计；否则改用预先固定的确认队列。

#### 置信序列与四种决策

对每个候选和端点 $k$，使用在全部查看时间上同时有效的区间

$$
[L_n^{(k)}(c),U_n^{(k)}(c)]
$$

覆盖 $\mu^{(k)}(c)=\mathbb E[D_i^{(k)}(c)]$。具体构造可采用有界差值或 sub-$\psi$ 置信序列，但必须在运行前声明边界/尺度假设、错误率分配和缺失值策略。

默认实现使用固定确认队列和有界差值的逐时 union-bound 置信序列。设端点单次分数范围为 $[A_k,B_k]$，则配对差 $D_i^{(k)}\in[a_k,b_k]=[A_k-B_k,B_k-A_k]$。定义

$$
\bar D_n^{(k)}(c)=\frac1n\sum_{i=1}^{n}D_i^{(k)}(c),
\qquad
\delta_{c,k,n}=\frac{\alpha_{c,k}}{n(n+1)},
$$

$$
r_{c,k,n}=(b_k-a_k)
\sqrt{\frac{\log(2/\delta_{c,k,n})}{2n}},
$$

$$
L_n^{(k)}(c)=\max\{a_k,\bar D_n^{(k)}(c)-r_{c,k,n}\},
\qquad
U_n^{(k)}(c)=\min\{b_k,\bar D_n^{(k)}(c)+r_{c,k,n}\}.
$$

$A_k$、$B_k$ 来自 `EndpointSpec.score_lower/score_upper`；$a_k$、$b_k$ 是由它们推导的配对差边界；$\bar D_n^{(k)}$ 是前 $n$ 个独立确认单元的样本均值；$\delta_{c,k,n}$ 是第 $n$ 次查看分配的错误率，且 $\sum_{n\ge1}\delta_{c,k,n}=\alpha_{c,k}$；$r_{c,k,n}$ 是 Hoeffding 半径。该默认式要求确认单元相互独立并来自冻结目标分布。若使用自适应确认采样，必须在配置中以完整的 martingale/sub-$\psi$ 区间替换上述四式，并同时保存 propensity、尺度过程和边界公式；不能只改采样器而沿用默认区间。

接受条件为

$$
L_n^{(target)}(c)>\epsilon_{gain}
\quad\land\quad
\forall j,\;L_n^{(preserve,j)}(c)>-\epsilon_{reg,j}.
$$

拒绝条件为

$$
U_n^{(target)}(c)\le\epsilon_{gain}
\quad\lor\quad
\exists j,\;U_n^{(preserve,j)}(c)<-\epsilon_{reg,j}.
$$

| 参数 | 定义 |
| --- | --- |
| $\epsilon_{gain}\ge0$ | 相对父 Harness 具有实践意义的最小目标提升。 |
| $\epsilon_{reg,j}\ge0$ | 保留能力族 $j$ 可接受的最大平均退化。 |
| $\alpha_{total}\in(0,1)$ | 整个开发实验的总错误率上限。 |
| $\alpha_{c,k}$ | 分给候选 $c$、端点 $k$ 的错误率，满足 $\sum_{c,k}\alpha_{c,k}\le\alpha_{total}$；必须在查看结果前分配。 |
| $n$ | 当前候选进入确认流的独立匹配单元数。 |

接受条件成立返回 `COMMIT`；拒绝条件成立返回 `REJECT`；两者均未成立且仍有安全信息实验时返回 `CONTINUE`; 已提交候选后来在有效回归流中满足拒绝条件时返回 `ROLLBACK`。置信序列只判断任务端点证据，不证明 trace 归因、节点等价或机制因果关系。

提交时

$$
H_{t+1}=H_t\oplus c_t,
$$

其中 $c_t$ 是本轮唯一满足接受条件并通过全部硬检查的候选；若多个候选同时满足，则先按更高目标下界、最差保留端点下界、更低风险和稳定标识依次决胜。$\oplus$ 表示在干净父版本上原子应用 $\Delta H$、锁定依赖并生成新的 `HarnessVersion`；任一步失败则 $H_{t+1}=H_t$ 并写入 `HARD_FAIL` witness。该式不允许把多个未经组合验证的候选同时提交。

### 适用范围学习

节点 $\nu$ 对 regime $z$ 的适用谓词为

$$
a_\nu(z)=a_{task}(z)\land a_{interface}(z)\land
a_{failure}(z)\land a_{runtime}(z).
$$

| 分量 | 可使用的特征 |
| --- | --- |
| $a_{task}$ | 任务族、输入/输出形态、交互长度、允许工具和评测目标。 |
| $a_{interface}$ | hook、状态 schema、工具协议、模型能力和可观测性。 |
| $a_{failure}$ | trace signature、义务类型、复现率和已确认 mediator 缺口。 |
| $a_{runtime}$ | 上下文窗口、延迟级别、并发模式、环境和依赖版本。 |

不得使用封存测试标签、任务答案或执行后才能获得的未来特征。候选谓词语言 $\mathcal A$ 由上述原子条件、有限阈值和 `AND/OR/NOT` 组成，最大深度及阈值网格在学习前冻结。

$$
a_\nu^*=\arg\min_{a\in\mathcal A}
\left[DL_{raw}(a)+\lambda_+FN(a;W^+)+\lambda_-FP(a;W^-)\right].
$$

其中

$$
FN(a;W^+)=\sum_{w\in W^+}\rho_w\mathbf 1[a(z_w)=0],
\qquad
FP(a;W^-)=\sum_{w\in W^-}\rho_w\mathbf 1[a(z_w)=1].
$$

| 符号 | 定义 |
| --- | --- |
| $W^+$ | 机制激活、mediator 成立且满足目标/保留标准的独立正 witness 组。 |
| $W^-$ | 接口可执行但机制或效果预测被充分反证的独立负 witness 组。硬接口失败不进入该集合。 |
| $z_w$ | witness $w$ 对应的 regime。 |
| $\rho_w>0$ | 独立组权重；同一 regime 的重复总权重上限为 1，避免重复运行支配范围。 |
| $DL_{raw}(a)$ | 按冻结谓词编码表计算的原始描述长度，单位为 bit。 |
| $\lambda_+,\lambda_->0$ | 排除有效条件与接纳无效条件的代价。高风险方法通常设 $\lambda_->\lambda_+$。 |

按 regime 分组划分结构学习集与范围验证集；$a_\nu^*$ 必须在范围验证集上不劣于旧范围才可替换。目标相同则选择描述更短、覆盖更窄且稳定标识更小的谓词。

### 结构更新操作与执行顺序

结构配置 $\Theta_{struct}$ 至少包含下列参数。它们可随实验协议设定，但同一比较批次内不得根据已见结果回调。

| 参数 | 类型 | 作用 |
| --- | --- | --- |
| $r_{det}\in\mathbb N^+$ | 正整数 | 确定性接口失败的独立复查次数；全部同向失败才可删除绑定。 |
| $r_{act}\in\mathbb N^+$ | 正整数 | 激活机会成立时判定 `INERT` 所需的最小重复数。 |
| $r_{rel}\in\mathbb N^+$ | 正整数 | 添加 `REQUIRES` 或 `CONFLICTS` 关系所需的最小独立析因重复数。 |
| $k_{regime}\ge2$ | 正整数 | 自主节点进入共享层或公共抽象被接受所需的最小独立 regime 数。 |
| $\epsilon_{DL}\ge0$ | bit | 接受公共抽象所需的最小描述长度收益。 |
| $\epsilon_{info}\ge0$ | 实数 | 继续主动消歧所需的最小“分裂收益减成本风险”值。 |
| $d_{scope}\in\mathbb N$ | 非负整数 | 适用谓词 AST 的最大深度。 |
| $\mathcal G_{threshold}$ | finite set | 适用谓词可选择的数值阈值网格。 |
| $\mathcal Q$ | finite rewrite rules | 被允许用于确定性候选等价判定的规则集合。 |
| `operation_priority` | ordered list | 结构操作冲突时的固定优先顺序，默认采用本节给出的顺序。 |

| 操作 | 触发条件 | 状态变化 | 不变量与可逆性 |
| --- | --- | --- | --- |
| `DELETE_BINDING` | 类型、hook、权限、依赖或顺序确定性失败，且复查得到同一结果 | 将具体绑定标为 `INVALID`，移出前沿 | 不删除一般节点、来源和其他绑定；可由新 Harness revision 上的重新绑定逆转。 |
| `MARK_INERT` | 触发机会存在、观测链正常，但预注册激活事件在最小重复数内始终未出现 | 将该节点—绑定在对应 regime 标为 `INERT` | 只否定该绑定/范围；不能据此否定一般机制。 |
| `SPECIALIZE_SCOPE` | 正负 witness 可由谓词语言中的稳定条件分开，且范围验证通过 | 用 $a_{new}\Rightarrow a_{old}$ 替换作用域，记录被排除 witness | 旧 revision 保留；新范围不得扩大。扩大范围必须新建 revision 并重新验证。 |
| `SPLIT_NODE` | 同一节点存在至少两个可复现、机制或条件不同的 witness 簇，单一范围无法稳定描述 | 创建互斥或显式重叠的子节点，父节点变为 `NONINSTANTIABLE_PARENT` | witness 分配规则可复算；父节点和原始 witness 不删除。 |
| `ADD_REQUIRES` | 2×2 对照表明 A 单独无效、B 单独不足而 A+B 重复有效 | 添加 `A REQUIRES B` 条件边 | 必须排除纯执行顺序错误；关系带 guard，可被后续反例撤销。 |
| `ADD_CONFLICT` | A、B 单独满足接受标准，而 A+B 重复产生机制破坏或回归 | 添加带 guard 的对称冲突边 | 组合失败必须非偶然且可复现；不否定 A、B 单独适用。 |
| `MERGE_NODES` | 类型兼容、可无损恢复、$G(g)>\epsilon_{DL}$ 且留一 regime 验证通过 | 新建公共父节点与 `SPECIALIZES` 边 | 具体节点继续保留；行为不可区分不声明程序等价。 |
| `KEEP_UNRESOLVED` | 测量缺失、结果冲突、样本不足或多解释尚不可区分 | 仅追加 witness 与未决问题 | 不改变活跃结构和 Harness；必须生成下一可检验条件或不可达原因。 |

`UpdateStructure` 按以下确定顺序执行：

1. 验证 witness schema、环境与父版本，追加到 $\mathcal W_t$；
2. 先处理确定性失败：`DELETE_BINDING`；
3. 再处理激活链：`MARK_INERT`，或把失败定位到具体 mediator；
4. 再处理条件异质性：`SPECIALIZE_SCOPE` 或 `SPLIT_NODE`；
5. 有成对/析因证据时处理 `ADD_REQUIRES`、`ADD_CONFLICT`；
6. 跨节点证据充足时尝试 `MERGE_NODES`；
7. 条件不足时执行 `KEEP_UNRESOLVED`；
8. 重算 $F_{t+1}$，追加 $\mathcal R_{t+1}$；若发生 Harness 提交，使全部旧候选与绑定变为 `STALE` 并重新绑定。

同一 witness 可触发多个相容操作，但后一步必须读取前一步生成的 revision。相互冲突的操作按“确定性接口事实优先于机制解释，具体绑定修订优先于一般节点修订，保守未决优先于不可逆合并”解决。

### 停止条件与四阶段接口

| 阶段 | 输入 | `OptimizerLLM` 的语义工作 | `OptimizerHarness` 的确定工作与输出 | 算法完成条件 |
| --- | --- | --- | --- | --- |
| loop 外来源组织 | `SourcePacket[]`、`organization_protocol` | 从锚定材料提出语法程序、typed holes、预测链和候选关系。 | 逐字段核验、编译、anti-unification、偏序/关系证明、索引审计，输出冻结 $K_0$。 | 全部来源完成对齐、编译、偏序与索引审计；此后同一实验不再改变。 |
| loop 内义务构造与干预检索 | 父代 trace、$K_0$、当前经验空间、`as_of` | 提出竞争故障解释、改变/保留义务并对可达子图作语义比较。 | 核验 trace/代码/状态/角色锚点，执行 hard filter、依赖闭包和排序融合，输出 need、可绑定子图及未决条件。 | 所有开放义务均有至少一个可绑定路径，或缺失依赖被证明不可达；继续展开不再产生新合法路径。 |
| 约束驱动候选生成 | $H^{[g]}$、trace-role trace、子图、$\mathcal O_g$ | 在知识孔域内完成适配、从隔离自由视图提出新机制、针对反例提出最小修订。 | 统一解析为 IR，执行类型/接口/effect/权限/依赖/保留 gate、discovery 检查、去重和冻结，输出知识与自由候选。 | beam 中所有保留项均完整绑定、可执行、有预测和 fallback；继续扩展不能提高覆盖且只增加支配候选。 |
| 版本空间消歧与演化控制 | 候选、$F_t$、select/anchor 池、安全 probes 与暴露账本 | 提出语义判别实验、解释 witness、在合法流程动作间规划，停滞时提出可核验缺口。 | 核验实验与解释，计算 Split/cost/risk 和置信序列，执行结构操作并输出 `COMMIT/REJECT/CONTINUE/ROLLBACK/RETURN_RETRIEVE/RETURN_REBIND/STOP_UNRESOLVED`。 | 全部候选已决，或返回 `NO_SAFE_EXPERIMENT/NO_INFORMATIVE_EXPERIMENT`；已披露选择结果时禁止回流生成。 |
| 结构学习与跨任务复用 | 完整 round ledger、旧经验 revision、下一轮未决 need | 提出公共机制、可检查 scope 和关系修订。 | 执行 typed anti-unification、范围求解、留一 regime、最小对照、图审计和原子提交，输出新经验 revision 与目标子图。 | 一轮合并、拆分、范围与关系学习均无合法更新，即达到本代结构固定点。 |
| stop 后正式测评 | 冻结 Harness、目录、经验 revision、执行协议、$D_{\mathrm{test}}$ | 不调用。 | 在只读包中执行一次测试，输出最终指标与审计 trace。 | 测试集恰好按协议执行且结果落盘；不触发任何在线更新。 |

外部资源耗尽、人工暂停或运行故障统一返回 `RESOURCE_STOP`，必须与上述算法完成条件分开记录；它们不能被报告为收敛。

外层 Harness 转移定义为

$$
H^{[g+1]}=
\begin{cases}
H^{[g]}\oplus c_g^*, & \text{若唯一候选 }c_g^*\text{ 返回 `COMMIT`},\\
H^{[g]}, & \text{若本代以 `REJECT`、未决或无安全信息实验结束}.
\end{cases}
$$

$g$ 是外层代际，$H^{[g]}$ 是本代父 Harness，$c_g^*$ 是通过激活、目标收益、全部保留端点与 hard gate 的唯一候选，$\oplus$ 是前文定义的原子差分应用。`ROLLBACK` 先恢复最近确认父版本，再把恢复结果作为 $H^{[g+1]}$。固定点不是简单的 $H^{[g+1]}=H^{[g]}$：还必须同时满足训练集完整轮换、连续规定代数无提交、无可执行开放义务、无待执行结构更新、检索与自由探索均无新叶节点以及 fresh confirmation/anchor 全部通过；任一条件为 `UNKNOWN` 时固定点为假。

### 伪代码算子与中间变量

第一部分伪代码中的大写名称均为确定接口，而非自然语言占位符。除明确标注为 LLM 生成的算子外，相同输入版本和配置必须产生相同输出。

#### 组织与检索算子

| 算子 | 输入 | 输出 | 失败或未知处理 |
| --- | --- | --- | --- |
| `OFFLINE_ORGANIZE` | `SourcePacket[]`、`organization_protocol`、`LLMCallLedger` | 冻结 `InterventionCatalogSnapshot` | 只在 loop 外执行；输入 schema 不合法返回 `INVALID_SOURCE_PACKET`，不隐式修复；全部离线调用写入同一实验账本。 |
| `FIX_INTERVENTION_SOURCE_UNITS` | `SourcePacket[]`、对齐规则 | 带不可变锚点的论文段落、代码符号、配置、测试和结果单元 | 不能定位到精确来源的内容保留为未对齐材料，禁止送入语义编译。 |
| `BUILD_SOURCE_INTERVENTION_REQUESTS` | 来源单元、语法/type/schema revision | 最小权限的来源语义编译请求 | 每项机制主张必须能引用输入锚点；禁止披露目标 benchmark 数据。 |
| `CALL_OPTIMIZER_LLM` | 已核验输入视图、call type、`OptimizerLLMConfig` | 原始响应与追加写入的 `LLMCallRecord` | 越权检查、调用、超时、重试和格式失败全部入账；失败输出不能进入后续对象。 |
| `PARSE_INTERVENTION_COMPILATION_PROPOSALS` | 来源编译调用 | `OptimizerProposal[]` | 固定 parser 只提取 schema 中已有字段；缺字段标记 `PARSE_FAILED/UNKNOWN`，不自动补写。 |
| `VERIFY_SOURCE_INTERVENTION_FIELDS` | 编译提案、来源单元、代码/配置/测试 | 逐字段值、锚点和验证状态 | 未被来源、代码或可重放测试支持的字段不得标为事实；关系候选仍需单独证明。 |
| `FREEZE_INTERVENTION_CATALOG` | 来源版本空间、组织协议与索引 | 不可变 `InterventionCatalogSnapshot` | 审计失败不生成快照；冻结后禁止原地修改。 |
| `MATERIALIZE_VERSION_SPACE` | $K_0$、经验空间、`as_of` | 截至指定 revision 可见的组合版本空间 | 来源层只读；未来 witness 和未提交 revision 不可见。 |
| `RETRIEVE_INTERVENTIONS` | $K_0$、经验空间、`InterventionNeed`、`as_of` | 可绑定子图和未决条件 | 不联网补来源；不可达与未找到严格区分。 |
| `COMPILE_TO_FINITE_INTERVENTION_GRAMMAR` | 来源包、经核验语义字段、语法配置 | 最具体叶节点和逐字段 provenance | 无法表达的步骤生成 `OPEN` typed hole；核心动作无法表达则返回 `UNCOMPILABLE_METHOD`。 |
| `VERIFIED_ANTI_UNIFY` | 类型兼容叶节点集合、$\Theta_{DL}$ | 可无损恢复的候选父节点及绑定 | 任一子节点不能重构或 $G\le\epsilon_{DL}$ 时不输出父节点。 |
| `INSERT_WITH_PARTIAL_ORDER` | 版本空间、叶节点、父节点 | 新 revision 的有向无环偏序图 | 无法证明偏序条件的节点保持不可比；发现环则拒绝本次边插入。 |
| `HARD_REACHABILITY_FILTER` | 版本空间、`InterventionNeed` | 未违反类型、权限、hook、依赖和禁止效应的节点 | `FALSE` 过滤，`UNKNOWN` 保留并生成未决条件。 |
| `OBLIGATION_COVERAGE_RECALL` | 已过滤节点、开放义务 | 至少覆盖一个改变义务且不违反保留义务的节点 | 没有覆盖节点时返回空集和 coverage gap。 |
| `EXPAND_GENERAL_TO_BINDABLE_SPECIALIZATIONS` | 一般节点、偏序图、目标 Harness | 可实例化具体节点和初始部分绑定 | 只遍历 `SPECIALIZES` 边；组织父节点本身不直接执行。 |
| `EXISTS_DECISION_RELEVANT_UNBOUND_DEPENDENCY` | 当前部分绑定集合 | bool | 仅当缺失依赖可能改变可行性、分区或提交决定时为真。 |
| `UPDATE_NEED_FROM_PARTIAL_BINDINGS` | 当前 need、部分绑定 | 新 `InterventionNeed` revision | 新增依赖、冲突、hook 和 probe 问题；旧 need 保留。 |
| `RETRIEVE_NEXT_DEPENDENCY` | 部分绑定、更新后的 need、索引 | 补充节点、能力或 `UNREACHABLE` 证明 | 检索不到不等于不存在；必须记录已查索引与停止依据。 |
| `BUILD_TRACE_OBLIGATION_NEED_VIEW` | trace-role trace、父 Harness、既有 witness | 限定到失败/成功切片、代码锚点和允许历史的诊断视图 | select/test 与未来 revision 不得进入视图；无法建立角色记录则拒绝调用。 |
| `PARSE_TRACE_OBLIGATION_NEED_PROPOSAL` | 诊断调用 | 竞争解释、obligation 与 need 草案 | 模型陈述只作为待核验提案；缺失竞争解释时保留 `UNKNOWN`。 |
| `VERIFY_TRACE_CODE_STATE_AND_ROLE_ANCHORS` | 诊断草案、trace、代码、状态 revision、暴露账本 | `TraceObligation[]` 与 `InterventionNeed` revision | 事件、锚点、状态或角色不一致的字段拒绝；只有 endpoint 的记录不能伪造因果切片。 |
| `BUILD_VERSION_SPACE_RERANK_REQUEST` | 硬过滤且依赖闭包后的节点、need、可见 witness | 只允许比较剩余节点的语义排序视图 | 不披露已过滤节点，防止模型恢复硬失败项。 |
| `PARSE_VERSION_SPACE_SEMANTIC_RERANK` | rerank 调用 | 带锚点的节点次序、迁移缺口和反驳 witness | 未指向现有 need、节点 revision 或 witness 的条目被拒绝。 |
| `FUSE_STRUCTURAL_AND_VERIFIED_SEMANTIC_RANKS` | 结构词典序、经核验语义排序 | 确定的检索次序 | 语义排序只能打破结构层级内的并列，不能覆盖 hard filter、依赖或冲突。 |
| `UNRESOLVED_CONDITIONS` | 节点与部分绑定 | 去重后的 `UnresolvedCondition[]` | 相同问题合并来源引用，不合并不同 regime。 |

#### 候选生成算子

| 算子 | 输入 | 输出 | 失败或未知处理 |
| --- | --- | --- | --- |
| `GENERATE_CANDIDATES` | $H^{[g]}$、$D_g^{\mathrm{trace}}$ 的 `ExecutionTrace[]`、$\mathcal O_g$、检索子图、搜索配置 | 冻结候选集合 | 不读取 select 任务或标签，不修改父 Harness；无合法候选时返回 coverage gap。 |
| `TOP_DOWN_BINDING_SEARCH` | 子图、Harness schema、义务、$B$、$\lambda_{1:3}$ | 完整知识绑定及搜索 ledger | 使用 $J(p)$ 排序；硬失败剪枝，未知依赖进入队列。 |
| `OBLIGATIONS_NOT_COVERED` | 候选、开放义务 | 尚无合法候选覆盖的 obligation id[] | 只计算 `OPEN` 义务；`PRESERVE` 义务作为约束而非待修复目标。 |
| `BUILD_KNOWLEDGE_COMPLETION_REQUESTS` | 父 Harness、知识草图、trace-role trace、义务、硬约束 | 每个草图的最小代码切片、合法孔域和预测要求 | 固定语法骨架与禁止修改区域显式标记；不能披露 select/test。 |
| `PARSE_KNOWLEDGE_INTERVENTION_IR` | 知识补全调用 | `CandidateInterventionIR[]` | 越出孔域、改变冻结骨架或缺少预测/fallback 的输出解析为拒绝。 |
| `BUILD_FREE_INTERVENTION_REQUEST` | 父 Harness、trace-role trace、未覆盖义务、硬约束 | 不含本轮具体知识解法的自由探索视图 | 可以披露统一语法和约束，不披露检索节点、知识候选代码或其排序。 |
| `PARSE_FREE_INTERVENTION_IR` | 自由提案调用 | 待编译 `FREE_DERIVED CandidateInterventionIR[]` | 无法表达为有限语法、绑定、预测和 fallback 的修改被拒绝。 |
| `COMMON_INTERVENTION_STATIC_GATE` | 两通道 IR、Harness schema、硬约束 | 逐项 gate 后仍合法的 IR revisions | 类型、接口、权限、状态 effect、依赖、保留、fallback 或隔离任一非 `PASS` 都不能冻结。 |
| `DISCOVERY_VALIDATE_BINDINGS` | 合法 IR、trace-role replay 与安全 probes | 绑定、激活和机制反例 | 仅产生 discovery evidence，不能作为目标收益提交证据。 |
| `BUILD_BINDING_CRITIQUE_REQUEST` | IR、确认反例、义务、允许修订类型 | 最小受控修订视图 | 只披露目标位置、失败层和须保持结构，禁止整文件重写。 |
| `PARSE_BINDING_REVISION_PROPOSALS` | critique 调用 | 带父 IR 和预期变化的修订提案 | 缺少父 revision、目标位置或 required rechecks 时拒绝。 |
| `VERIFY_AND_COMPILE_MINIMAL_BINDING_REVISIONS` | 修订提案、父 IR、反例 | 新 `CandidateInterventionIR` revisions | 必须解释对应反例且不改变无关结构；所有硬检查重新执行。 |
| `EXACT_OR_PROVED_REWRITE_DEDUP` | 通过 gate 的候选、$\mathcal Q$ | 规范候选及等价来源集合 | 只合并完全相同或由 $\mathcal Q$ 证明等价的 patch。 |
| `FREEZE_VALID_CANDIDATE_REVISIONS` | 通过全部 gate 且去重的 IR | `FrozenCandidate[]` | 固定父版本、节点/绑定/IR revision、预测、fallback 和调用谱系；任何字段变化都创建新 ID。 |

#### 规划、测评与演化算子

| 算子 | 输入 | 输出 | 失败或未知处理 |
| --- | --- | --- | --- |
| `PLAN_TEST_AND_EVOLVE` | $S_t$、冻结候选、select/anchor 池、暴露账本、累计 round ledger、实验配置 | 更新状态、同一累计 ledger 和七种控制信号之一 | 每轮只执行一个真实实验，再依据新 revision 重规划；一个外层代际最多提交一个候选；选择结果一旦披露便锁住同代生成路径。 |
| `BUILD_CANDIDATE_WITNESS_EXPERIMENTS` | 候选、$F_t$、select/anchor 池、暴露账本、可用 probes | 具有角色、互斥完备预测分区的实验集合 | 已影响候选生成的任务不能生成独立确认实验；无唯一预测的前沿单元进入 `UNRESOLVED` 分区。 |
| `BUILD_WITNESS_EXPERIMENT_REQUEST` | 状态、候选、程序实验、累计账本 | 竞争假设、可用任务/探针和安全边界的最小视图 | 隐藏 select 标签/结果；只提供允许提出的实验原语。 |
| `PARSE_WITNESS_EXPERIMENT_PROPOSALS` | witness 设计调用 | 语义 probe、扰动、消融与预期分区草案 | 没有互斥完备预测、保持条件或 stop rule 时拒绝。 |
| `VERIFY_AND_COMPILE_WITNESS_EXPERIMENTS` | 实验草案、状态、候选、暴露账本 | 合法 `CandidateWitnessExperiment[]` | 核验执行接口、角色独立性、风险、恢复和 predicted partition；模型建议不改变数据角色。 |
| `KEEP_DECISION_OR_STRUCTURE_CHANGING_TESTS` | 实验集合、当前结构与区间 | 可能改变结构操作或决策边界的安全实验 | 仅重复已知结论且不收紧区间的实验被删除。 |
| `ARGMAX_VERSION_SPACE_SPLIT_MINUS_COST_RISK` | $\mathcal E_t^{safe}$、权重和 $\lambda_c,\lambda_r$ | 依“实验成本、风险与选择”小节规则唯一选出的 $e_t$ | 空集合和低信息分别返回两个显式停止码。 |
| `EXECUTE_ISOLATED` | 完整实验计划、冻结环境 | 原始运行记录或运行失败记录 | 超时、崩溃和工具异常均生成 witness，不丢弃。 |
| `APPEND` | append-only ledger、新记录 | 新 ledger revision | 重复 ID 拒绝；纠错通过 `supersedes` 追加。 |
| `BUILD_WITNESS_STRUCTURE_REQUEST` | 状态、候选、实验、原始 observation | 绑定到确定节点/预测/实验的解释视图 | 不允许修改原始测量或添加不存在的观察。 |
| `PARSE_WITNESS_STRUCTURE_INTERPRETATION` | witness 解释调用 | 支持/反驳/未知预测、替代解释和操作意图 | 输出只是 `OptimizerProposal`，不能直接写版本空间。 |
| `VERIFY_WITNESS_ANCHORS_AND_UPDATE_TRIGGER` | 解释提案、实验、原始 observation、状态 | 经核验预测映射与合法结构操作 | 每个操作逐项匹配冻结触发表；缺失最小对照或锚点时降为 `KEEP_UNRESOLVED`。 |
| `APPLY_STRUCTURAL_UPDATE` | 版本空间、原始 witness、经核验更新、$\Theta_{struct}$ | 新版本空间 revision 和操作日志 | 严格采用“结构更新操作与执行顺序”小节；模型置信度和未核验解释均不得进入状态。 |
| `REBIND_AND_REPARTITION` | 候选、新版本空间、当前父 Harness | 仍有效候选、新绑定和预测分区 | 节点或绑定 revision 改变即生成新候选；旧候选标为 `STALE`。 |
| `ENUMERATE_LEGAL_VERSION_SPACE_ACTIONS` | 最新 witness、更新状态、候选、累计账本 | `CONTINUE_EXPERIMENT/RETURN_RETRIEVE/RETURN_REBIND` 的可执行实例 | select 结果已披露时删除两个返回动作；提交/拒绝/回退不在该集合。 |
| `BUILD_NEXT_VERSION_SPACE_ACTION_REQUEST` | 合法动作、状态、候选、累计账本 | 只允许排序或补全合法动作参数的视图 | 不向模型提供越权动作 schema。 |
| `PARSE_VERSION_SPACE_ACTION_PROPOSALS` | 动作规划调用 | 带目标、参数和停止条件的动作提案 | 非枚举动作或目标 revision 失效时拒绝。 |
| `VERIFY_AND_COMPILE_VERSION_SPACE_ACTIONS` | 动作提案、状态、累计账本 | 可执行合法动作 | 核验数据披露、前置条件和参数；不能编译出提交/拒绝/回退。 |
| `SELECT_DECISION_RELEVANT_VERSION_SPACE_ACTION` | 程序动作、经核验模型动作、状态、候选 | 唯一流程动作 | 优先能改变结构/决策且成本风险可接受的动作；并列按预注册 tie-break。 |
| `BUILD_VERSION_SPACE_STALL_REQUEST` | 状态、候选、累计账本 | 停滞原因、缺失信息和允许返回边界 | 已披露 select 后禁止请求同代生成修订。 |
| `PARSE_VERSION_SPACE_STALL_REFLECTION` | 停滞反思调用 | 新 witness、scope revision、missing primitive 或前序返回草案 | “已经收敛”不是可接受 payload。 |
| `VERIFY_AND_COMPILE_STALL_RETURN` | 停滞草案、状态、累计账本 | 合法实验/返回请求或 `INVALID` | 必须能转化为可执行 probe、明确缺失依赖或合法返回；否则维持 unresolved。 |
| `ANYTIME_TARGET_AND_PRESERVATION_DECISION` | 确认 witness、端点配置、错误率账本 | `COMMIT/REJECT/CONTINUE/ROLLBACK` | 只使用确认流；缺失端点返回 `CONTINUE` 或 `UNRESOLVED`。 |
| `COMMIT_NEW_VERSION` | 唯一接受候选、干净父版本 | 新 `HarnessVersion` | 原子应用失败保持父版本并产生 `HARD_FAIL`。 |
| `REBIND_ALL_TO_NEW_HARNESS` | 全部活跃节点、新 Harness | 新绑定搜索任务 | 旧父版本上的可行性、预测和成本结论不直接继承。 |
| `REMOVE_CANDIDATE_KEEP_EVIDENCE` | 被拒候选、决策 witness | 移出活跃集的候选状态 | 候选、节点、来源和 witness 都不物理删除。 |
| `RESTORE_CONFIRMED_PARENT` | 当前 Harness、提交链和回退入口 | 最近一个完整确认的父版本 | 回退本身生成 revision 和回归 witness。 |
| `NO_ACTIVE_HYPOTHESIS_CAN_CHANGE_HARNESS` | 义务、候选、实验和决策状态 | bool | 只有“停止条件与四阶段接口”小节的算法完成条件满足时为真；资源耗尽不使其为真。 |

#### 结构学习与迁移算子

| 算子 | 输入 | 输出 | 失败或未知处理 |
| --- | --- | --- | --- |
| `CONSOLIDATE_AND_TRANSFER` | 长期状态、本代 round ledger、下一轮未决 need、`LLMCallLedger`、结构配置 | 更新版本空间和目标子图，或 `PENDING_REVIEW` | 只消费在线运行证据，不导入新论文；测试集不可见；原子提交失败时保持旧状态。 |
| `COPY_ON_WRITE_EMPIRICAL_STATE` | 已提交在线状态 | 隔离的影子 witness/版本空间/revision 状态 | 不复制或修改只读 $K_0$；失败丢弃影子，不影响已提交状态。 |
| `GROUP_COMPATIBLE_CONCRETE_INTERVENTIONS` | 具体节点、类型和机制签名 | 待抽象节点组 | 只按结构、类型、状态效应和 mediator 兼容性分组，不按标题相似度。 |
| `BUILD_INTERVENTION_ABSTRACTION_REQUEST` | 兼容节点组、正反 witness | 固定具体结构并突出开放抽象槽的视图 | 不披露测试数据，不把标题相似度作为机制证据。 |
| `PARSE_INTERVENTION_ABSTRACTION_PROPOSAL` | abstraction 调用 | 公共机制、开放孔、宿主绑定、不可参数化部分和边界反例草案 | 缺少逐子节点映射或边界反例时保持未决。 |
| `VERIFY_AND_TYPED_ANTI_UNIFY` | 节点组、抽象草案 | 公共 AST 与逐子节点恢复绑定 | 程序验证类型最小上界、effect、控制顺序和可重构性；失败返回 `NO_COMMON_PARENT`。 |
| `DESCRIPTION_GAIN` | 公共父节点、子节点、$\Theta_{DL}$ | $G(g)$ | 严格使用“抽象的描述长度收益”小节的 raw bit 编码。 |
| `LEAVE_ONE_REGIME_OUT_ACTIVATION_AND_EFFECT_CHECK` | 父节点、分 regime witness | bool 及逐折证据 | 任一留出 regime 出现稳定且不可由范围解释的反例即失败。 |
| `BUILD_APPLICABILITY_SCOPE_REQUEST` | 父节点、子节点组、正负 witness、有限谓词字段 | 只允许提出可测谓词的 scope 视图 | 自由自然语言例外不进入候选谓词类。 |
| `PARSE_APPLICABILITY_SCOPE_PROPOSAL` | scope 调用 | 候选谓词、正负分隔、未知区和 required replay | 谓词无法编译或引用不可见字段时拒绝。 |
| `LEARN_AND_VERIFY_CHECKABLE_APPLICABILITY_SCOPE` | 正负 witness、scope 草案、$\mathcal A$ | $a_\nu^*$、目标值和逐 witness 验证 | 程序在冻结谓词类中求解；没有稳定谓词时返回 `NO_STABLE_SCOPE`。 |
| `BUILD_VERSION_SPACE_RELATION_REQUEST` | 父节点、scope、节点组、当前图、最小对照 | 允许关系类型和可见证据的视图 | 禁止仅凭文本相似提出等价或依赖事实。 |
| `PARSE_VERSION_SPACE_RELATION_PROPOSAL` | relation 调用 | 建边、收紧、分裂或废弃草案 | 缺失 guard、支持/冲突 witness 或目标 revision 时拒绝。 |
| `VERIFY_VERSION_SPACE_RELATION_TRIGGER` | 关系草案、父节点、scope、节点组、witness | 经核验关系或 `UNRESOLVED` | 按关系类型检查结构证明、最小对照、作用域和反证。 |
| `INSERT_PARENT_WITH_SCOPE_AND_RELATION` | 父节点、scope、经核验关系、子节点 | 新父 revision 和有证据边 | 子节点和原始 witness 保留；父节点默认不可直接实例化。 |
| `SPLIT_VERIFIED_HETEROGENEOUS_NODES` | 版本空间、冲突 witness、谓词语言 | 经验证特化子节点及 witness 分配 | 只有稳定异质性与可复算边界才分裂；否则保持 `UNRESOLVED`。 |
| `HARD_FILTER_AND_RETRIEVE` | 更新后的版本空间、目标 `InterventionNeed` | 目标可绑定子图 | 与组织检索阶段使用相同硬过滤和未知值语义。 |
| `ATOMIC_COMMIT_EMPIRICAL_REVISION` | 旧状态、影子状态、round ledger | 新已提交状态 revision | 先审计来源可达、无环、witness 完整和暴露一致性；任一失败保持旧状态并返回恢复记录。 |
| `CURRENT_LEDGER_REVISION` | `LLMCallLedger` | 当前只追加账本 revision | 账本不完整或有未落盘调用时返回 `PENDING`，禁止经验提交。 |

#### 外层训练与封闭测试算子

| 算子 | 输入 | 输出 | 失败或未知处理 |
| --- | --- | --- | --- |
| `EVOLVE_INTERVENTION_SPACE` | $H_0$、来源包、$D_{\mathrm{train}}$、$D_{\mathrm{test}}$、`TrainProtocol` | 固定点后的冻结实验状态与最终测试结果 | 测试集只传给最终算子；资源停止显式返回，不伪装成固定点。 |
| `INIT_TRAIN_SCHEDULER` | $D_{\mathrm{train}}$、协议 | 任务分层、暴露账本、coverage 与 anchor 初态 | 无法满足划分要求时返回配置错误，不借用测试集。 |
| `INIT_LLM_CALL_LEDGER` | `TrainProtocol.optimizer_config_revision` | 空的只追加 `LLMCallLedger` | 配置、schema 或存储不可用时实验不得启动。 |
| `INIT_ONLINE_STATE` | $H_0$、$K_0$ | 初始 $S_0$ 与只读来源层 | 不把论文报告结果写成目标 benchmark witness。 |
| `ASSIGN_TRAIN_ROLES` | scheduler、当前状态、$g$ | 三个两两不相交任务集合 | 服从分层、暴露与独立性约束；不足时返回未完成状态。 |
| `RUN_HARNESS` | 冻结 Harness、任务集合、执行配置 | 每次运行一条 `ExecutionTrace` | 成功、失败、超时、崩溃和评测异常均保留，禁止只筛失败轨迹。 |
| `BUILD_OBLIGATIONS_AND_NEED` | trace-role `ExecutionTrace[]`、当前状态 | 经 LLM 提议并由程序核验的 $\mathcal O_g$ 与 `InterventionNeed` | 内部固定调用诊断、解析和锚点核验三步；只有得分没有事件链的运行可形成端点事实，但不能定位结构义务。 |
| `INIT_ROUND_LEDGER` | $g$、父 Harness、trace batch、实验级调用/暴露账本 | 已包含父代 trace、义务诊断调用与初始暴露的 `RoundLedger` | 同一代只能初始化一次；局部返回继续追加原 ledger。 |
| `UPDATE_EXPOSURE_FROM_LLM_CALLS` | scheduler、调用账本、受影响对象、候选任务集合 | 追加后的对象级披露与独立性状态 | 只要任务字段直接或间接影响对象及后代，其独立性永久变为 `EXPOSED`。 |
| `REFRESH_INDEPENDENT_DEVELOPMENT_POOLS` | scheduler、当前候选、select/anchor 池 | 满足对象级独立性的替换池 | 无可用独立任务时结束同代返回，不允许把已暴露任务重新标记为独立。 |
| `NO_SELECT_RESULT_DISCLOSED` | round ledger、暴露账本 | bool | 任一 select 标签、分数、trace 或派生排序进入生成上下文即为假。 |
| `REVISE_NEED_FROM_WITNESS` | 当前 need、合法 discovery witness | 保留谱系的新 need revision | 不得读取 select/test 结果；证据不足追加未决条件。 |
| `CARRY_UNRESOLVED_TO_NEXT_NEED` | 当前 need、检索未决条件、round ledger | 下一代待重新判断的 `InterventionNeed` revision | 已解决项关闭，仍开放项保留来源与所需 probe；不提前绑定下一代 Harness。 |
| `EMPIRICAL_REVISIONS_CREATED` | 提交前后状态、round ledger | 本代新增 hypothesis/relation/scope revision IDs | 只返回已原子提交对象；pending 或回滚对象不进入后代暴露传播。 |
| `APPLY_GENERATION_DECISION` | 当前父 Harness、终局决定 | $H^{[g+1]}$ 候选值 | 仅 `COMMIT` 应用唯一候选；失败保持父版本并生成 witness。 |
| `UPDATE_TRAIN_SCHEDULER` | 旧 scheduler、三类任务、round ledger | 新暴露、coverage、未决义务与 anchors | 追加历史，不覆盖旧角色记录。 |
| `TRAIN_FIXED_POINT` | 当前/下一 Harness、状态、scheduler、stop rule | bool | 所有条件合取；`UNKNOWN`、pending、资源耗尽均返回假。 |
| `FREEZE_FOR_FINAL_TEST` | 最终 Harness、经验状态、$K_0$、协议 | 只读 `FrozenTestPackage` | 任一对象继续变化就产生新实验身份。 |
| `RUN_FINAL_TEST_ONCE` | `FrozenTestPackage`、$D_{\mathrm{test}}$ | 最终指标和只读测试 trace | 不调用 `OptimizerLLM`，不写入在线经验层。 |
| `INVALIDATE_OLD_BINDINGS_CANDIDATES_AND_INTERVALS` | 下一父 Harness、旧在线状态 | 标为 `STALE` 的旧绑定、候选和确认区间 | 原始证据保留；下一代必须重新绑定并重新确认。 |

#### 伪代码局部变量

| 变量 | 唯一含义 |
| --- | --- |
| `llm_call_ledger` | 实验级只追加 `LLMCallLedger`；记录离线和在线全部成功、失败、重试与拒绝调用，revision 被 round ledger 和最终冻结包引用。 |
| `source_units` | 从 `SourcePacket[]` 固定的最小来源单元；每个单元有论文/代码/配置/测试锚点及对齐状态。 |
| `compilation_requests/calls/proposals` | 来源语义编译的输入视图、调用记录和统一提案；三者通过 call ID 一一关联。 |
| `verified_fields` | 经来源、代码、配置或测试逐字段核验后的语义字段及状态，只有这些字段可被编译为来源节点。 |
| `leaves` | 从来源或自由修改编译出的最具体干预节点。 |
| `abstractions` | 已通过重构和描述长度检查的候选公共父节点。 |
| `version_space` | 当前函数内的 $\mathcal V$ revision；赋值产生新 revision，不原地覆盖历史。 |
| `rerank_request/call/proposal` | 硬过滤与依赖闭包后才构造的语义重排请求、调用和解析提案；不能恢复已过滤节点。 |
| `need_view/need_call/need_proposal` | 从 trace、父代码、状态和可见 witness 构造的诊断视图、调用与义务/need 草案。 |
| `sketches` | 对检索节点作有限孔绑定搜索得到的知识草图、合法孔域和固定语法骨架。 |
| `knowledge_requests/knowledge_calls/knowledge_ir` | 知识通道输入、调用和共同候选 IR；只能补全草图允许的孔。 |
| `free_request/free_call/free_ir` | 不披露本轮具体知识解法的自由通道输入、调用和共同候选 IR。 |
| `ir` | 通过共同静态 gate 的 `CandidateInterventionIR` revision 集合。 |
| `counterexamples` | discovery 检查产生的绑定、激活或机制反例，不包含用于提交的独立 select 证据。 |
| `revision_request/revision_call/revision_proposals/revisions` | 对确认反例构造的受控修订视图、调用、解析提案及经核验的新 IR revision。 |
| `candidates` | 当前仍可执行或待决的冻结候选集合。 |
| `uncovered` | 尚无知识候选覆盖的开放改变义务。 |
| `program_experiments` | 由冻结规则枚举的基础契约、probe、replay、配对和 anchor 实验。 |
| `witness_request/witness_call/witness_proposals` | 针对竞争假设的语义实验设计视图、调用和解析草案。 |
| `semantic_experiments` | 通过执行、角色、风险、隔离和 predicted-partition 核验的模型提出实验。 |
| `experiments` | 当前结构 revision 下仍有效的安全 candidate–witness 实验。 |
| `e` | 本轮唯一被选择并执行的实验。 |
| `observation` | `e` 的完整原始结果，写入后成为 `EmpiricalWitness`。 |
| `interpretation_request/call/interpretation` | 绑定到确定 observation、experiment、candidate 和节点 revision 的 witness 解释视图、调用及提案。 |
| `verified_update` | 把模型解释逐项映射到原始观察和结构操作触发表后得到的合法更新；可能仅为 `KEEP_UNRESOLVED`。 |
| `program_actions/action_request/action_call/action_proposals/actions` | 程序合法流程动作、受限规划视图、调用、解析提案和核验后的动作并集。 |
| `reflection_request/reflection_call/reflection/return_request` | 无信息实验时的停滞视图、调用、提案及经核验的 probe/返回请求。 |
| `decision` | anytime 接受器返回的四种状态之一及触发边界。 |
| `control` | `PLAN_TEST_AND_EVOLVE` 返回给外层 loop 的七种控制信号之一；它可以封装 `decision`，也可以要求局部返回或以未决状态结束。 |
| `route` | 最新结构 witness 决定的阶段内控制方向：留在测评、返回检索或返回重新绑定。 |
| `accumulated_round_ledger` | 从本代第一次实验开始累计的 `RoundLedger`；局部返回后继续追加，不得用新局部账本覆盖。 |
| `groups` | 可尝试共同抽象的具体节点组。 |
| `shadow` | 阶段四写时复制的经验状态；审计通过前不对后续代际可见。 |
| `abstraction_request/call/proposal` | 针对兼容具体节点组的语义抽象视图、调用和公共机制草案。 |
| `parent` | 类型化 anti-unification 得到的候选公共父节点。 |
| `scope_request/call/proposal` | 有限谓词语言中的适用范围视图、调用和候选谓词草案。 |
| `scope` | 从正负 witness 学得并通过验证的 $a_\nu^*$。 |
| `relation_request/call/proposal/relation` | 版本空间关系视图、调用、关系草案和经最小对照/结构/作用域核验的关系。 |
| `subspace` | 针对目标 need 硬过滤和展开后的版本空间子图。 |
| `state.harness` | `S_t.H`；只有提交或回退算子可以改变。 |
| `state.version_space` | `S_t.\mathcal V`。 |
| `state.witness_ledger` | `S_t.\mathcal W`，只允许追加。 |
| `state.revision_log` | `S_t.\mathcal R`；`latest_committed_revision` 是本代开始时已原子提交的最大 revision，不包含阶段三影子修订。 |
| `catalog` | 本次实验冻结的 $K_0$；在线 loop 内始终只读。 |
| `scheduler` | 训练任务分层、角色暴露、coverage、未决义务和 anchor 状态。 |
| `trace_pool/select_pool/anchor_pool` | 第 $g$ 代的 $D_g^{\mathrm{trace}}/D_g^{\mathrm{select}}/D_g^{\mathrm{anchor}}$。 |
| `trace_batch` | 父 Harness 在 trace pool 上产生的完整 `ExecutionTrace[]`。 |
| `obligations/need` | 从 `trace_batch` 得到的 $\mathcal O_g$ 与 `InterventionNeed` revision。 |
| `retrieved/unresolved` | 当前 need 对应的可绑定版本空间子图与尚未解决的可执行条件。 |
| `next_need` | 汇总本代未决条件和 witness 后形成的下一代需求 revision；下一代 trace 到来后还需重新校验。 |
| `round_ledger` | 本代全部 trace、实验计划、witness、暴露、结构操作和决策的追加账本。 |
| `H_next` | 按代际转移式得到的下一父 Harness；不提交时等于当前父版本。 |
| `next_view` | 阶段四提交后针对 `next_need` 构造的可重建检索子图；不含测试证据。 |
| `frozen` | stop 后冻结的 Harness、目录、经验 revision、模型/工具/评测协议和种子包。 |

### 全局不变量

1. 原始来源与原始 witness 只追加，不被摘要、结构结论或后续修订覆盖。
2. 来源事实、算法推导、自主假设和经验结论分别标记；缺失信息不静默补全。
3. 确定性接口失败、机制未激活、mediator 未成立、任务无收益和能力回归分别更新不同对象。
4. 版本空间权重仅用于选择实验，不解释为校准概率，也不能直接决定 Harness 提交。
5. 节点合并不删除具体实例；有限实验中的行为不可区分不等于程序等价。
6. 每次 Harness 提交后，所有候选和绑定失效并针对新父版本重新生成。
7. 发现流可以改变版本空间；只有新鲜确认流和预注册保留端点可以决定提交。
8. 所有结构操作、实验选择和提交决定必须可由记录的配置、版本、种子和 witness 重放。
9. 封存测试集不参与检索、候选生成、结构学习、范围学习、实验选择、停止或超参数调整。
10. 任一字段、公式输入或测量缺失时显式进入 `UNRESOLVED`；不得以默认成功值继续。
11. 来源组织只在 loop 外执行；在线经验可以新增 revision，但不能改写 $K_0$ 的来源事实和目录索引。
12. 候选生成只读取本代 trace-role 数据；已经影响候选的任务不得再为该候选提供独立 select 证据。
13. 每一代结束后，无论 Harness 是否晋级，都更新暴露账本并重新运行下一代 trace；旧绑定、候选与置信区间不得跨父版本直接继承。
14. stop 后的 $D_{\mathrm{test}}$ 运行是只读终局测评，测试结果不得反馈到任何演化状态。
15. 每次 `OptimizerLLM` 调用都必须先通过最小权限与禁止对象检查，并在任何派生对象可见前完成固定 schema 解析和对应锚点/规则核验。
16. `OptimizerLLM` 输出的置信度、排序或自然语言解释不得进入 hard filter、$\operatorname{Split}(e)$、置信序列或提交边界；模型只产生语义提案，统计量和最终决定由冻结程序计算。
17. 任一 task 字段一旦通过 LLM 调用、程序视图或派生对象影响候选或经验 revision，该任务对该对象及其后代永久失去独立性；更换标签或跨代轮换不能恢复。
18. hypothesis、need、候选 IR、模型提出实验、witness 解释、scope 和关系 revision 必须能回指完整 `LLMCallRecord` 与 `ValidationRecord`；缺少任一链路时保持 `PENDING/UNRESOLVED`。

