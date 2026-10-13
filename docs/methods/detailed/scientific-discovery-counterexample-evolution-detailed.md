# 科学发现驱动的反例演化：完整详细版

## 一、完整 Method

现有 Harness 优化通常把 trace 当作一份故障说明，把论文方法当作一组可选技巧，再交给 LLM 直接提出下一版代码。问题在于，trace 只记录已经发生的现象，并不自动给出失败原因；论文中的有效性依赖原始任务、模型、接口和评测条件；LLM 对原因与改法的判断也只是尚未验证的解释。缺少统一的可证伪表示后，一次成功很难说明究竟哪个机制起了作用，一次失败也难以沉淀为后续搜索可以利用的边界，多轮演化因而容易重复猜测和试错。

为解决这一问题，本路线把 Harness 演化提升为一个持续进行的科学发现过程。当前 Harness 是被研究的系统，故障解释、方法迁移、代码接入和效果预测都是待检验假设；论文与工程经验提供带条件的机制先验，训练 trace、配对运行和针对性 probe 提供观测，真实反例负责推翻或收紧解释。外部知识不直接充当答案，`OptimizerLLM` 的提案也不直接成为事实，只有能够回到来源锚点或目标任务执行证据的结论，才能进入下一轮。

具体而言，loop 外先把论文、代码、配置和结果冻结为可审计的方法目录。每一轮从当前父 Harness 在 benchmark 训练任务上的真实 trace 出发，由 `OptimizerLLM` 提出多个竞争性故障解释，检索与之匹配且满足结构约束的方法机制，并同时生成知识引导候选与自由探索候选；`OptimizerHarness` 将这些提案编译为可执行修改，安排能够反驳关键假设的测评。成功证据扩大经过验证的适用范围，反例则修正故障解释、接入方案和检索方向，最终形成“提出假设—实施干预—寻找反例—修订知识—进入下一代 Harness”的闭环。

外部方法准备与目标 benchmark 上的演化属于两个时间范围。实验开始前同时冻结方法目录、benchmark 版本、数据划分、模型与工具环境、任务分层、随机种子、晋级规则和停止规则；进入实验后只允许训练集证据推动 H₀ → H₁ → H₂ → … 并更新实验内的长期状态。新论文不能在同一次演化中途加入，封存测试集也不能进入检索、生成、选择或记忆更新。

### 证据组织与检索阶段：如何组织和检索外部方法

论文与工程实现中的有效方法通常不是一个可以直接复制的完整组件。机制定义可能在正文，适用前提藏在实验设置中，失败边界只出现在消融或附录里，真正可执行的接口又位于代码与配置文件中。若只保存摘要，检索会返回听起来相关但缺少接入条件的方法；若只保存代码，后续的 `OptimizerLLM` 又无法判断实现对应哪项主张、在哪些环境下得到过验证。外部知识因此必须先恢复为可以审计的完整证据链，才能参与后续演化。

这里采用“来源事实与方法解释分离”的结构。原始论文、代码版本、配置和结果作为不可改写的来源包保存；从来源中抽取的机制、前置条件、依赖、冲突和失败边界则形成可修订的方法对象。这样既允许后续根据新证据调整对方法的理解，又不会反向改写原始材料。检索也不只比较文本相似度，而是同时检查任务能力缺口、Harness 生命周期位置、必要依赖、禁止条件与证据强度，避免把语义相近但结构上无法接入的方法交给候选生成器。

本阶段包含两个时间位置不同的动作。**离线组织**发生在 benchmark 演化 loop 之前：把固定版本的论文、官方代码、配置、测试与结果编译为方法对象、关系图和字段索引，并冻结目录版本。**在线检索**发生在每一轮 loop 内：先把本轮 trace 暴露出的 Harness 缺口写成 `MethodNeed`，再用该需求从 $M_t$ 构造 `CrossTaskEvidenceView`，并与冻结目录联合召回方法，以字段过滤排除硬性不兼容项，以图扩展补齐依赖和互补方法，最后返回方法束及仍未解决的假设。每个结果都携带可回溯的来源锚点、适用范围和待验证条件。

本阶段由 `OptimizerLLM` 完成难以规则化的语义理解，由 `OptimizerHarness` 保持来源事实、检索边界和结构约束。离线组织时，`OptimizerHarness` 先固定论文段落、代码符号、配置、测试和结果锚点，再以 `SOURCE_CLAIM_EXTRACTION` 请求让 `OptimizerLLM` 提出机制单元、前置条件、失败边界、接口和关系候选；任何没有精确锚点的内容只能成为待核验提案。在线检索时，`OptimizerHarness` 从本轮允许使用的 trace 构造受控视图，`OptimizerLLM` 通过 `TRACE_TO_METHOD_NEED` 提出竞争性故障解释、能力缺口和查询计划；程序完成稀疏/稠密召回、硬过滤、分数融合、依赖闭包和冲突打包后，再由 `OptimizerLLM` 通过 `SEMANTIC_BUNDLE_RERANK` 比较方法束与当前失败机制的匹配关系。`OptimizerHarness` 最终核验锚点、字段、依赖和禁止条件，未确认内容保留为 `UNKNOWN`，不把模型判断写成来源事实。

第一阶段首先保留不可变的原始来源包，论文方法的所有派生表示都必须能够回到这里：

```text
SourcePacket = {
  paper_version,
  official_code_version,
  exact_source_anchors,
  configs_and_examples,
  tests_and_reported_results
}
```

`SourcePacket` 只负责保存来源，不直接参与候选生成。全部 `SourcePacket` 在进入 benchmark loop 前被离线编译并冻结；若后来加入新论文或更换代码版本，必须生成新的目录版本并作为新的实验条件重新开始，不能在同一次多轮演化中途改变。$H_0$ 的第一轮 `MethodNeed` 来自它在训练集故障发现批次上的运行 trace，而不是只靠静态说明猜测；后续轮次则由 $H_t$ 的新 trace 和上一轮反例共同形成新的需求。

**组织对象。** 每个方法被编译为：

```text
EvidenceBoundMethod = {
  method_id,
  source_anchors,
  problem_signatures,
  target_capability,
  preconditions,
  forbidden_conditions,
  ordered_mechanism,
  generic_interface_requirements,
  expected_observations,
  reported_successes,
  counterexamples_and_limitations,
  dependencies,
  conflicts,
  evidence_grade,
  extraction_call_ids,
  field_validation_status
}
```

`generic_interface_requirements` 只描述方法通常需要什么输入、状态或调用能力，不记录它在当前 Harness 中接到哪里。每一条机制、条件和效果声明都必须指向论文段落、表格、代码符号或测试；作者报告、代码可验证结果和本地复现结果分开保存。

**离线组织算法。**

1. `OptimizerHarness` 从 `SourcePacket` 中对齐论文算法步骤、代码符号、配置和测试，形成只含原文、代码和执行证据的最小来源视图；无法对齐的内容标为 `paper_only` 或 `code_only`。
2. 对每个来源视图发起 `SOURCE_CLAIM_EXTRACTION`。`OptimizerLLM` 按机制完整性提出方法切分、原子声明、前置条件、禁止条件、失败边界、接口契约和关系候选，并为每一项返回精确来源锚点与不确定性。
3. `OptimizerHarness` 逐字段检查锚点是否真实存在、引用内容是否支持该字段、代码符号和配置是否对应固定 revision。缺失或越界项变为 `UNKNOWN` 或 `unverified_relation`，不能因表述合理而通过。
4. 只有通过锚点检查的声明才能形成 `EvidenceBoundMethod`；若若干步骤必须按顺序共同工作，则保留为一个单元。关系候选必须再次经过类型、effect、时间与来源规则核验，才能写入 `REQUIRES / CONFLICTS / ALTERNATIVE_TO / REFINES / SUPPORTED_BY / REFUTED_BY` 图。
5. 为问题、机制、前置条件、预期现象、限制和证据分别建立稀疏与稠密索引；不把全部字段拼成单一文本。原始 `OptimizerLLM` 输出和被拒字段进入调用账本，不进入权威目录。

**在线检索算法。** 每轮输入为冻结的方法目录、上一轮长期证据视图和：

```text
MethodNeed = {
  need_id,
  source_call_id,
  competing_hypotheses,
  desired_capability,
  problem_description,
  known_constraints,
  forbidden_properties,
  acceptable_evidence,
  unresolved_questions,
  query_plan
}
```

1. `OptimizerHarness` 对本轮成功/失败 trace、最小事件切片、父 Harness 摘要、历史反例和允许访问的长期证据构造最小诊断视图；`OptimizerLLM` 通过 `TRACE_TO_METHOD_NEED` 同时提出多个故障假设、相应能力缺口、已知约束、禁止属性和需要取证的问题。程序核验每项解释引用的 trace 事件和代码位置，并把未被事件支持的内容标为 hypothesis，而不是事实。
2. 将经核验的需求分解为问题、机制、条件、证据和反例五类子查询，先用明确的 `forbidden_properties` 和前置条件做硬过滤；未知条件保留为 `UNKNOWN`，不能当作已满足。
3. 各字段分别执行稀疏与稠密召回，再融合字段得分：

   $$
   s(m)=\sum_f w_f\,s_f(m)+\lambda C_{condition}(m)+\eta C_{evidence}(m)-\mu U(m).
   $$

4. 从高分种子沿 `REQUIRES` 反向扩展，补齐依赖；遇到 `CONFLICTS` 时不能同时进入结果集。
5. 以“需求覆盖、证据完整、条件匹配、未知项少”为目标形成若干方法束，而不是返回单篇论文 top-$k$。
6. `OptimizerHarness` 为通过硬约束的方法束构造 `SEMANTIC_BUNDLE_RERANK` 视图；`OptimizerLLM` 逐束说明其机制如何对应当前故障假设、迁移时可能缺少什么、哪些方法互补，以及什么观察会反驳该选择。语义排序只能在硬过滤后的集合内调整次序，不能恢复已排除项或删除依赖。
7. 融合程序分数与经规则核验的语义排序，返回结构多样的方法束、来源、依赖闭包、反例和未决假设。到此停止，不生成当前 Harness 的绑定方案。

```text
OFFLINE_ORGANIZE(source_packets):
    units <- ALIGN_AND_SEGMENT(source_packets)
    extraction_requests <- BUILD_SOURCE_CLAIM_REQUESTS(units)
    extraction_calls <- CALL_OPTIMIZER_LLM(extraction_requests)
    claim_proposals <- PARSE_SOURCE_CLAIM_PROPOSALS(extraction_calls)
    claims <- ANCHOR_SCHEMA_AND_RELATION_CHECK(claim_proposals, units)
    graph, field_indexes <- BUILD_EVIDENCE_GRAPH_AND_INDEXES(claims)
    return FREEZE_METHOD_CATALOG(source_packets, claims, graph, field_indexes)

BUILD_METHOD_NEED(H, trace_batch, evidence_view, old_counterexamples):
    diagnostic_view <- BUILD_TRACE_NEED_VIEW(
                           H, trace_batch, evidence_view,
                           old_counterexamples)
    need_call <- CALL_OPTIMIZER_LLM(diagnostic_view,
                                    call_type=TRACE_TO_METHOD_NEED)
    need_proposal <- PARSE_METHOD_NEED_PROPOSAL(need_call)
    return TRACE_ANCHOR_AND_CONSTRAINT_CHECK(need_proposal,
                                             diagnostic_view)

ONLINE_RETRIEVE(catalog_snapshot, evidence_view, need, trace_view):
    queries <- DECOMPOSE_NEED(need)
    indexes <- MERGE_RETRIEVAL_VIEWS(catalog_snapshot.field_indexes,
                                     evidence_view)
    seeds <- FIELD_AWARE_HYBRID_RETRIEVE(indexes, queries)
    seeds <- HARD_CONDITION_FILTER(seeds, need)
    bundles <- DEPENDENCY_CLOSURE_AND_CONFLICT_PACK(
                   catalog_snapshot.graph, seeds)
    rerank_request <- BUILD_SEMANTIC_BUNDLE_RERANK_REQUEST(
                          bundles, need, trace_view)
    rerank_call <- CALL_OPTIMIZER_LLM(rerank_request)
    rerank_proposal <- PARSE_BUNDLE_RERANK_PROPOSAL(rerank_call)
    bundles <- FUSE_PROGRAM_SCORE_AND_VERIFIED_SEMANTIC_RANK(
                   bundles, rerank_proposal)
    return bundles, UNRESOLVED_ASSUMPTIONS(bundles, need)
```


### 证据约束候选生成阶段：如何结合 trace、知识与自主探索生成候选

检索命中只说明某个机制可能相关，并没有回答当前 Harness 的哪段代码导致了失败，也没有说明论文中的抽象机制应接入哪个生命周期位置。真实 trace 还会混入模型随机性、工具噪声和后续连锁错误；若直接让 `OptimizerLLM` 阅读整条轨迹并自由改写代码，很容易同时改变多个因素，最终既无法归因，也无法把失败转化为有用反例。

本阶段把候选生成限制为“最小化、因果诊断、定位、编译、补全、反思修订”六个连续动作。`OptimizerHarness` 先把失败压缩成可稳定复现的最小 trace 条件并映射到代码位置，再构造 `TRACE_CAUSAL_DIAGNOSIS` 视图；`OptimizerLLM` 必须提出多个竞争性因果链，逐项引用事件、状态转移和代码位置，并说明能够区分这些解释的观测。`OptimizerHarness` 只保留锚点存在且不违反依赖事实的诊断，再把检索方法编译成带类型、接口和行为约束的代码草图。知识通道要求 `OptimizerLLM` 补全 `MethodSketch` 中仍需语义实现的 `predicate/adapter/fallback` 等孔位；自由通道使用独立上下文，不披露本轮方法束及知识候选补丁，由 `OptimizerLLM` 提出新的局部机制。两类原始输出都由 `OptimizerHarness` 解析为共同 Candidate IR 并经过相同 gate；被拒候选可通过 `GATE_FAILURE_REFLECTION` 解释语义性接入错误，第三阶段返回的确认反例则通过 `COUNTEREXAMPLE_GUIDED_REVISION` 形成新的修订意图，但任何反思都不能绕过原 gate。

算法先维护父代、反例、可疑位置、证据子图、修复模式以及硬约束和经验约束构成的候选状态。随后对 trace 做最小化和分层定位，为每个候选选择单机制、互补组合或自由探索模板，生成带明确孔位的 patch，并通过静态检查、接口检查和旧能力保护检查冻结版本。冻结后的候选同时记录来源方法、预期激活事件和失败时应返回的反例类型，使测评结果能够定向改变下一轮生成，而不是只留下一个总分。

**trace 的来源。** 为使候选生成与候选测评不混用，第 $t$ 轮开始前，训练调度器从 benchmark 官方训练集 $D_{\mathrm{train}}$ 中冻结三种数据角色。$D_t^{\mathrm{trace}}$ 用于运行父 Harness $H_t$ 并产生候选生成所依据的成功与失败 trace；$D_t^{\mathrm{select}}$ 在候选冻结前不可进入 `OptimizerLLM` 的生成上下文，用于判断候选相对父代的新收益；$D_t^{\mathrm{anchor}}$ 回放此前已经确认的能力和严重失败，用于检查回归。本轮测评池为 $D_{dev}^{(t)}=D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}$，三组任务在同一轮中两两不相交。

第 $t$ 轮固定父 Harness $H_t$、模型版本、工具环境、评测器和随机种子后，在 $D_t^{\mathrm{trace}}$ 上实际执行任务。第一轮运行 $H_0$，以后每轮运行上一轮确定的 $H_t$。每次执行不仅保存最终分数，还保存：

```text
ExecutionTrace = {
  task_id,
  split_role,
  harness_version,
  model_and_tool_versions,
  seed,
  ordered_events,
  final_output,
  metric_vector,
  failure_signature,
  replay_artifacts
}
```

`ordered_events` 按真实发生顺序记录模型调用及其可见上下文、工具调用与结果、记忆读写、控制流转移、重试、回退、异常和终止原因。成功 trace 用于建立失败/成功对照，失败 trace 用于形成故障假设和最小切片；只有最终得分而没有事件链的运行不能进入候选定位。当前轮用于生成候选的 trace 只能来自 $D_t^{\mathrm{trace}}$，不能来自 benchmark 测试集，也不能偷看本轮预留的候选判定面板。

**输入。** 父代 $H_t$、由 $D_t^{\mathrm{trace}}$ 运行得到的 `ExecutionTrace` 集合、故障假设集合 $\Phi_t$ 及其权重分布 $Z_t$、在线检索得到的证据包 $B_t$，以及此前确认的硬反例 $C_t^{hard}$ 与经验反例 $C_t^{emp}$。

**输出。** 一组已冻结的 `CandidateVersion`。每个候选包含具体代码修改、来源方法、预期激活事件、待验证机制、保留旧能力的检查项，以及生成它的 `LLMCallRecord` ID。解析失败或未通过确定性 gate 的 `OptimizerLLM` 输出不进入候选集，但调用记录仍保留。

本阶段维护状态：

$$
C_t=(H_t,Z_t,L_t,G_t,P_t,C_t^{hard},C_t^{emp},Q_t),
$$

其中 $L_t$ 是代码位置可疑度，$G_t$ 是已经检索并编译的方法草图集合，$P_t$ 是知识通道与自由通道产生的冻结候选集合，$C_t^{hard}$ 与 $C_t^{emp}$ 分别保存确定性反例和带作用域的经验反例，$Q_t$ 保存仍需取证的前提、冲突与观测缺口。分层修复模式是生成 $G_t$ 和 $P_t$ 的中间结构，不再与 $P_t$ 共用符号。

**算法 2：最小切片、分层模式与双通道综合。**

1. **只最小化可操纵单元。** 构造集合 $U$，元素可以是输入步骤、上下文块、工具响应、配置项和可可靠重放的状态。普通 trace 事件只是观察，除非存在确定性 replay，否则不能假装可以删除。
2. **执行随机版 ddmin。** 对子集 $u\subseteq U$ 重复运行，记录目标失败签名是否出现。使用顺序证据判断 `FAIL / PASS / UNRESOLVED`：失败率下界高于阈值才判 `FAIL`，上界低于阈值才判 `PASS`，证据不足返回 `UNRESOLVED`。ddmin 仅删除被稳定判定仍可复现失败的部分，最终得到的是“经验 1-minimal”切片，而不是全局最小反例。
3. **把切片映射到代码位置。** 根据控制依赖、数据依赖和状态读写把切片映射到 Harness 位置，并计算：

   $$
   \operatorname{loc}(\ell)=w_1\,\text{slice-overlap}
   +w_2\,\text{failed/success contrast}
   +w_3\,\text{dependency proximity}
   +w_4\,\text{historical repair success}.
   $$

   仅用该分数排序 top-$k$ 位置，不把低分位置永久删除，避免故障定位噪声提前截断正确修复。
4. **提出并核验竞争性因果解释。** `OptimizerHarness` 把最小 trace、匹配成功 trace、top-$k$ 位置、状态差分和已有假设组成 `TRACE_CAUSAL_DIAGNOSIS` 请求。`OptimizerLLM` 输出若干因果链，每条包括最早偏离、传播路径、可能根因、相反证据和判别 probe。程序检查引用事件、时间顺序、数据/控制依赖和可执行 probe；未通过检查的链不能进入 $Φ_t$。
5. **吸收已有反例。** 若输入包含第三阶段确认的反例，`OptimizerHarness` 构造 `COUNTEREXAMPLE_GUIDED_REVISION` 请求。`OptimizerLLM` 判断应收紧条件、重新绑定、替换适配器、换用相邻方法还是开启自由分支，并返回具体修订意图；程序把意图转成允许的最小编辑或新的检索需求。
6. **建立修复模式层级。** 对检索到的实现和历史 patch 做 AST edit anti-unification，形成“具体修改 → 参数化修改 → 一般控制模式”的树。合并两个模式时，要求生命周期 hook 相同、状态与工具映射可保持、前置条件和 fallback 不丢失，并优先选择孔位更少的共同父模式。
7. **编译带类型代码草图。** 每个方法转成：

   ```text
   MethodSketch = FixedMechanism
                + TypedHoles{hook, location, predicate, adapter,
                             parameter, ordering, fallback}
                + HardConstraints
                + ExpectedTraceEvents
   ```

   固定部分保存论文方法的核心控制机制；孔位只负责与宿主 Harness 的接入。若适配必须改变机制本身，则产生一个新的派生草图，不能静默改写原方法。
8. **并行生成两类候选。** 知识通道读取草图、证据包、切片和经核验因果解释，填充类型孔位；自由通道只读取同一父代、切片、候选位置、经核验诊断和硬约束，自行提出未被知识库覆盖的修改。二者都编译成相同 Candidate IR，进入相同 gate，评测时隐藏来源标签，避免规划器偏爱“论文候选”或“自由候选”。
9. **确定性预筛与一次受控反思。** 依次检查能否编译、接口与工具 schema、状态读写权限、hook 可达性、测试集隔离、fallback 和修改范围。对于包含语义性绑定或实现错误的拒绝报告，`OptimizerHarness` 可发起一次 `GATE_FAILURE_REFLECTION`；`OptimizerLLM` 只能在原草图、原位置和原硬约束内提出最小修订，修订后重新经过完整 gate。确定性权限或数据隔离违规不进入反思，直接拒绝。
10. **冻结候选版本。** 候选一旦开始评测便不可原地修改；任何修复都生成新 ID，并记录父版本、诊断调用、草图、孔位绑定、代码差异和预期 trace 事件。

```text
SYNTHESIZE(H, trace_batch, hypotheses, bundles, old_counterexamples,
           historical_patches, hard_constraints):
    failing_case <- SELECT_DIAGNOSTIC_CASE(trace_batch, hypotheses)
    target_failure_signature <- failing_case.failure_signature
    atoms <- MANIPULABLE_ATOMS(H, failing_case)
    slice <- STOCHASTIC_DDMIN(atoms, target_failure_signature)
    successful_traces <- MATCHED_SUCCESS_TRACES(trace_batch, failing_case)
    locations <- LOCALIZE(slice, H, successful_traces)
    diagnosis_request <- BUILD_TRACE_CAUSAL_DIAGNOSIS_REQUEST(
                             H, slice, successful_traces,
                             locations, hypotheses)
    diagnosis_call <- CALL_OPTIMIZER_LLM(diagnosis_request)
    diagnosis_proposals <- PARSE_CAUSAL_DIAGNOSES(diagnosis_call)
    diagnoses <- VERIFY_CAUSAL_TRACE_ANCHORS_AND_DEPENDENCIES(
                     diagnosis_proposals, trace_batch, H)

    revision_intents <- empty
    if old_counterexamples is not empty:
        revision_request <- BUILD_COUNTEREXAMPLE_REVISION_REQUEST(
                                H, diagnoses, old_counterexamples)
        revision_call <- CALL_OPTIMIZER_LLM(revision_request)
        revision_intents <- PARSE_COUNTEREXAMPLE_REVISIONS(revision_call)
        revision_intents <- VERIFY_ALLOWED_REVISION_INTENTS(
                                revision_intents, old_counterexamples)

    hierarchy <- ANTI_UNIFY_EDITS(bundles.code, historical_patches)
    sketches <- COMPILE_TYPED_SKETCHES(
                    hierarchy, bundles.constraints,
                    diagnoses, revision_intents)

    knowledge_requests <- BUILD_KNOWLEDGE_LLM_REQUESTS(
                              H, sketches, locations, slice,
                              diagnoses, hard_constraints)
    knowledge_calls <- CALL_OPTIMIZER_LLM(knowledge_requests)
    knowledge_candidates <- PARSE_KNOWLEDGE_COMPLETIONS(
                                knowledge_calls, sketches)

    free_request <- BUILD_FREE_LLM_REQUEST(
                        H, locations, slice, diagnoses,
                        hard_constraints)
    free_call <- CALL_OPTIMIZER_LLM(free_request)
    free_candidates <- PARSE_FREE_PROPOSALS(free_call)
    candidates <- NORMALIZE_TO_COMMON_IR(knowledge_candidates, free_candidates)
    candidates <- DEDUP_BY_BEHAVIOR_AND_PATCH(candidates)
    accepted, rejected <- DETERMINISTIC_FILTER(candidates)
    semantic_rejections <- ELIGIBLE_SEMANTIC_GATE_FAILURES(rejected)
    if semantic_rejections is not empty:
        reflection_request <- BUILD_GATE_FAILURE_REFLECTION_REQUEST(
                                  H, semantic_rejections,
                                  sketches, hard_constraints)
        reflection_call <- CALL_OPTIMIZER_LLM(reflection_request)
        revisions <- PARSE_MINIMAL_GATE_REVISIONS(reflection_call)
        revised <- APPLY_VERIFIED_MINIMAL_REVISIONS(
                       revisions, semantic_rejections)
        accepted <- accepted union DETERMINISTIC_FILTER(revised).accepted
    return FREEZE_NEW_VERSIONS(accepted)
```

反例规划与测评阶段返回反例后，`OptimizerHarness` 先按硬约束违反、机制未激活、机制已激活但任务失败、旧能力回归或 `UNRESOLVED` 分类，再通过 `COUNTEREXAMPLE_GUIDED_REVISION` 让 `OptimizerLLM` 解释反例对当前因果链、方法条件和接入方案意味着什么。硬约束违反仍直接禁止相应绑定；其余输出只有在引用反例字段、保持来源机制并落入允许编辑集合时才进入下一版草图。`UNRESOLVED` 不得用于剪枝。


### 反例规划与测评阶段：如何规划、测评并控制多轮 Harness 演化

候选得分变化不能直接解释修改是否有效。分数没有提升，可能是方法不适用、接入位置错误、机制从未被触发，或测试任务没有覆盖目标故障；分数提升也可能来自随机波动、数据选择偏差或对旧能力的牺牲。若所有候选一次性跑满任务，运行会大量消耗在结论已经明确的版本上；若根据少量结果过早淘汰，又会错过只在长轨迹或特定任务族中显现的改进。

这里把机制验证和任务收益放进同一套滚动决策。候选首先通过接入、激活和旧能力保护门，只有方法确实进入执行链并产生预期中介行为后，最终任务结果才用于更新“方法适用性”。随后控制器根据当前信念选择最能区分候选、故障解释或风险来源的下一项实验。评测因此不是固定流水线，而是围绕尚未解决的决策边界逐步取证；低成本 probe 可以提前排除接入错误，却不能替代对最终任务效用的验证。

实现上使用一组加权粒子联合表示根因、方法适用性、适配器正确性、机制激活和任务族收益。真实执行结果到来后，`OptimizerHarness` 先计算可直接观测的 gate、指标和配对差，再以 `EVIDENCE_INTERPRETATION` 请求让 `OptimizerLLM` 解释这些观察分别支持或反驳哪些假设、哪些结论仍不可识别；模型输出作为带来源的语义 observation，不能直接充当概率。出现违规时，`COUNTEREXAMPLE_ATTRIBUTION` 区分方法不适用、adapter 错误、机制未激活、任务 regime 变化和其他模块干扰。需要继续取证时，`NEXT_ACTION_PROPOSAL` 在合法动作与未决问题上提出 probe、任务、检索或修订方向；搜索停滞时，`SEARCH_BRANCH_REFLECTION` 检查是否遗漏假设、方法邻域或自由分支。`OptimizerHarness` 负责校验提案、更新粒子、计算风险、执行实验并依据冻结规则作出最终决定。

**训练/开发任务池的来源。** 阶段三使用的数据仍然来自 $D_{\mathrm{train}}$，但不与候选生成共用同一角色。第 $t$ 轮在产生任何候选之前，训练调度器冻结三组任务：

$$
D_{dev}^{(t)}=D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}},
\qquad
D_t^{\mathrm{trace}}\cap D_t^{\mathrm{select}}=
D_t^{\mathrm{trace}}\cap D_t^{\mathrm{anchor}}=
D_t^{\mathrm{select}}\cap D_t^{\mathrm{anchor}}=\varnothing.
$$

$D_t^{\mathrm{select}}$ 是本轮候选判定池，只包含未向候选生成器暴露 trace、标签和评测结果的训练任务，用于估计候选相对父代的新收益；$D_t^{\mathrm{anchor}}$ 是旧能力回放池，用于检查回归。第 0 轮的 anchors 由预注册任务分层中 $H_0$ 已正确完成的代表案例和必须保留的关键行为构成；后续轮次再加入此前确认的能力、严重失败和晋级边界。anchor 可以是已经暴露过的训练任务，因此只承担能力保留检查，不能作为未见任务泛化证据。主动收益选题只在 $D_t^{\mathrm{select}}$ 内进行，anchors 则由回归风险和能力族覆盖单独调度；两类结果进入不同统计量。二者都不能临时扩展到 benchmark 测试集。

**输入。** 父代 $H_t$、冻结候选集合 $P_t$、故障假设 $\Phi_t$ 及其权重 $Z_t$、本轮训练/开发任务池 $D_{dev}^{(t)}$ 及其案例暴露记录。

**输出。** `promote / reject / return-counterexample / continue / tie` 之一，以及完整的新证据。父代、候选、probe 和配对评测的每次真实执行都产生同一格式的 `ExecutionTrace`，写入 `EvaluationLedger`；这些 trace 可以在下一轮作为历史证据或 anchor 来源，但若其任务已参与当前候选生成，就不能再被计作该候选的独立收益证据。封闭测试集不参与该阶段。

为避免把“接入错误”误判成“论文方法无效”，维护 $L$ 个加权粒子。粒子 $\omega_l$ 保存：根因 $z_l$、方法在当前条件下是否适用 $a_l[m]$、候选适配器是否正确 $c_l[i]$、目标机制是否激活 $g_l[i]$、候选在任务族 $d$ 上相对父代的收益 $\mu_l[i,d]$，以及各变形关系的可靠性 $\rho_l[r]$。新证据 $e$ 到来后：

$$
w_l'\propto w_l\,P(e\mid \omega_l,a),
$$

归一化后在有效样本量过低时重采样。关键归因规则是：只有 `adapter_ok` 和 `mechanism_on` 已有正证据时，最终任务失败才主要削弱“方法适用”；否则先更新接入错误或机制未激活的概率。

**算法 3：反例约束的信念滚动控制。**

1. **冻结版本。** 代码、模型、工具环境或指标任一改变都产生新 candidate/evidence regime，旧统计不能继续累计到新版本。
2. **先做机制 gate。** 每个候选依次执行：
   - 静态契约检查：编译、接口、状态读写、工具 schema、终止条件；
   - 激活 probe：构造能触发该方法前提的最小输入，要求出现预声明 activation event 和 mediator change；
   - 因果对照：在同一 probe 上临时 bypass 新组件。若启用与禁用无法观察到预期差异，则标记为 `inert`；
   - 变形检查：仅在前置条件成立时，对 source case 和语义保持变换后的 follow-up case 检查关系。随机输出使用成对差的顺序容差判断，不能用单次结果判定。
3. **解释证据并归因反例。** 每批新 gate 或任务证据先由 `OptimizerHarness` 提取事实字段，再通过 `EVIDENCE_INTERPRETATION` 让 `OptimizerLLM` 返回支持、反对、替代解释和未知项。若观察违反声明，再调用 `COUNTEREXAMPLE_ATTRIBUTION` 比较方法、接入、激活、regime 和旁路干扰等解释。程序检查每项依据并把失败最小化为 `{violated_claim, precondition, minimal_input, transform, seeds, minimal_trace_slice, reproducibility}`。gate 通过只表示机制已接入并产生预期中介行为，不表示总体效果更好。
4. **联合枚举并扩展动作。** 程序动作集合包括 `ActivationProbe`、`MetamorphicPair`、`PairedRun`、`DevPanel`、`RefineAdapter`、`TightenScope`、`RetrieveNeighbor`、`FreeBranch`、`Promote`、`Reject`、`Rollback` 和 `Stop`。`NEXT_ACTION_PROPOSAL` 可以在这些动作上给出排序，也可以提出带目标假设、预期观察和停止条件的新 probe；`OptimizerHarness` 只有在动作可执行、数据角色合法且可能改变决定或形成反例时才加入动作集。未通过 gate 的候选不能执行效能评测。
5. **用决策价值选择下一步。** `OptimizerLLM` 的置信表达不直接作为粒子概率。观测似然来自重复运行、已校准错误模型或明确的区间假设；无法校准的语义解释进入 `unknown_model` 分支。令当前 belief 下的最小决策损失为：

   $$
   \mathcal R(b)=\min_{d\in\{promote,reject,return,continue\}}
   \mathbb E_b[L(d,\theta)].
   $$

   一个取证动作的期望价值为：

   $$
   \operatorname{EVI}(a)=\mathcal R(b)-
   \mathbb E_{o\sim p(o\mid b,a)}\mathcal R(\operatorname{update}(b,a,o)).
   $$

   对“生成新候选”动作，短 rollout 模拟“生成—gate—任务测评—决策”。控制器比较深度 2～3 的若干短计划，只执行第一步，得到真实观察后丢弃旧计划并重规划。动作成本只在决策价值接近时破同分；若小 probe 不可能改变决定，则直接运行完整开发面板，避免连续执行便宜但无用的测试。
6. **主动选择判别任务。** 对 $D_t^{\mathrm{select}}$ 中每个任务 $x$，用 belief 粒子预测结果和更新后的决策风险，得到 $VOI(x)$。从混合分布抽样：

   $$
   q_t(x)=(1-\varepsilon)\operatorname{softmax}(VOI_t(x)/\tau)
          +\varepsilon p_{target}(x),\qquad \varepsilon>0.
   $$

   记录抽样前的 $q_t(x)$，并对候选与父代执行 matched task、matched seed 的成对运行。$D_t^{\mathrm{anchor}}$ 不进入该收益抽样分布，而是按回归后验上界和能力族覆盖运行。若采用确定性 argmax 选题，结果只能用于区分候选，不能用于声称目标开发分布上的无偏平均收益。
7. **在停滞时反思搜索分支。** 当合法动作为空、连续证据不能改变 belief，或多个候选反复产生同类反例时，`OptimizerHarness` 构造 `SEARCH_BRANCH_REFLECTION` 请求。`OptimizerLLM` 可以提出遗漏根因、相邻方法需求、自由探索方向或更具判别力的观测，但不能直接宣布收敛。提案通过锚点、权限和可执行性检查后返回第一或第二阶段；没有合法提案时才进入完整开发面板或固定点检查。
8. **随时判断晋级或淘汰。** 设成对得分差 $d_t\in[-1,1]$，对主动抽样任务使用重要性加权观测 $X_t=p_{target}(x_t)d_t/q_t(x_t)$，在满足相应条件时维护 anytime confidence sequence。候选满足以下规则：
   - `Promote`：总体收益下界超过实践阈值，所有旧能力族的回归下界高于允许边界，且机制 gate 全部通过；
   - `Reject`：总体收益上界仍低于最小改进，关键旧能力明确退化，或出现确定性安全/机制反例；
   - `Continue`：区间跨越决策边界，且仍存在能改变决定的任务或重复；
   - `Tie`：完整允许证据下差异仍小于实践阈值，记录为不可区分，不强行选优。

```text
PLAN_AND_TEST(parent, candidates, hypotheses, dev_pool, prior_evidence):
    freeze all candidate versions
    method_scopes <- EXTRACT_METHOD_SCOPES(candidates)
    belief <- INIT_PARTICLES(hypotheses, method_scopes, prior_evidence)
    ledger <- empty

    loop:
        for c in candidates with unknown gate:
            event <- RUN_NEXT_GATE(c)  # contract -> activation -> bypass -> MR
            APPEND(ledger, event)

            interpretation_request <- BUILD_EVIDENCE_INTERPRETATION_REQUEST(
                                          c, event, belief)
            interpretation_call <- CALL_OPTIMIZER_LLM(
                                       interpretation_request)
            interpretation <- PARSE_EVIDENCE_INTERPRETATION(
                                  interpretation_call)
            interpretation <- VERIFY_INTERPRETATION_ANCHORS(
                                  interpretation, event)
            belief <- UPDATE_WITH_OBSERVATION_MODEL(
                          belief, event, interpretation)

            if event violates a claim:
                cex <- MINIMIZE_AND_CONFIRM(event)
                attribution_request <- BUILD_COUNTEREXAMPLE_ATTRIBUTION_REQUEST(
                                           c, cex, interpretation, belief)
                attribution_call <- CALL_OPTIMIZER_LLM(attribution_request)
                attribution <- PARSE_COUNTEREXAMPLE_ATTRIBUTION(
                                   attribution_call)
                attribution <- VERIFY_ATTRIBUTION_EVIDENCE(
                                   attribution, cex, event)
                return RETURN_TO_CANDIDATE_SYNTHESIS(
                           cex, attribution), ledger, belief

        decision <- ANYTIME_DECISION(candidates, belief, ledger)
        if decision is promote/reject/tie:
            return decision, ledger, belief

        actions <- ENUMERATE_EVOLVE_AND_EVALUATE_ACTIONS(belief)
        action_request <- BUILD_NEXT_ACTION_PROPOSAL_REQUEST(
                              belief, ledger, actions, dev_pool)
        action_call <- CALL_OPTIMIZER_LLM(action_request)
        action_proposals <- PARSE_NEXT_ACTION_PROPOSALS(action_call)
        actions <- actions union COMPILE_VALID_ACTION_PROPOSALS(
                                   action_proposals, belief, dev_pool)
        actions <- KEEP_ACTIONS_THAT_CAN_CHANGE_DECISION_OR_FORM_CEX(actions)

        if actions is empty and important uncertainty remains:
            reflection_request <- BUILD_SEARCH_BRANCH_REFLECTION_REQUEST(
                                      parent, candidates, belief, ledger)
            reflection_call <- CALL_OPTIMIZER_LLM(reflection_request)
            reflection <- PARSE_SEARCH_BRANCH_REFLECTION(reflection_call)
            return_request <- VERIFY_AND_COMPILE_BRANCH_RETURN(reflection)
            if return_request is valid:
                return return_request, ledger, belief
            actions <- FULL_DEV_PANEL(unresolved candidates)
        if actions is empty:
            return tie, ledger, belief

        plan <- SAMPLED_POSTERIOR_ROLLOUT(actions, depth=2..3)
        result <- EXECUTE_FIRST_ACTION(plan)
        APPEND(ledger, result)

        result_interpretation_request <- BUILD_EVIDENCE_INTERPRETATION_REQUEST(
                                             TARGETS(plan), result, belief)
        result_interpretation_call <- CALL_OPTIMIZER_LLM(
                                          result_interpretation_request)
        result_interpretation <- PARSE_EVIDENCE_INTERPRETATION(
                                     result_interpretation_call)
        result_interpretation <- VERIFY_INTERPRETATION_ANCHORS(
                                     result_interpretation, result)
        belief <- UPDATE_WITH_OBSERVATION_MODEL(
                      belief, result, result_interpretation)
        # 下一轮基于真实观察重新规划
```

第三阶段中，`OptimizerLLM` 负责解释证据、归因反例、提出下一动作和反思停滞分支；`OptimizerHarness` 保留动作合法性、统计更新、任务调度、真实执行和最终决策权。若某个 select case 的输入、trace、标签或结果被披露给 `OptimizerLLM`，并进一步影响候选修订，该 case 对所有受影响后代立即失去独立选择资格；训练调度器必须将其记录为已暴露，并从尚未披露的训练任务中补充新的 select case。`OptimizerLLM` 的解释不能直接触发 `Promote/Reject/Tie`，也不能把 select 或 test 信息带入未经重新划分数据角色的候选生成。


### 证据积累与复用阶段：如何持续积累并跨任务复用

单次成功只能证明某个候选在特定任务、模型、工具和评测条件下取得了结果，不能自动上升为通用规律；单次失败也可能由接入错误、机制未触发或环境变化造成，不能直接判定外部方法无效。若长期记忆只保存最佳 Harness 和总分，系统会遗失适用条件与失败原因；若把每条 trace 平铺保存，重复事件又会淹没少量关键边界。

长期状态因此区分不可变事实、可修订结论、因果归因和使用记录。原始运行与选择过程只追加保存，方法主张以版本化形式维护，成功和反例分别约束其适用范围，方法是否被检索、采用、激活以及是否对结果产生独立贡献也分开记录。跨任务迁移使用带条件的证据视图，而不是把历史均值当作新任务真值；当任务或运行环境进入新 regime 时，旧经验只作为需要重新校准的先验。

每轮结束先原子写入评测与使用账本，再对重复证据聚类、对冲突结论分裂条件、对过时 regime 降权，并通过方法消融与谱系信息估计独立贡献。只有获得跨种子、跨任务或跨环境支持的主张才逐级扩大作用域，稳定反例则收紧条件或标记争议。更新后的索引直接服务下一轮需求检索，使积累结果能够改变候选空间，同时保留从任一结论回溯到原始运行的路径。

这一阶段位于 benchmark 演化 loop 内并在每轮在线执行。它吸收的是 $H_t$ 在故障发现批次上的运行、候选 gate、父子配对评测、旧能力回放以及方法使用链产生的证据；它不负责接收和重新整理新论文。新外部来源只能通过 loop 外的离线组织生成新的方法目录版本，在线积累只修订目标 Harness 上观察到的适用范围、反例、归因和跨任务证据。

**输入。** 反例规划与测评阶段的 `EvaluationLedger`、本轮 `UsageLedger` 与旧快照 $M_t$。前者包含候选谱系、成对运行、机制 probe 和晋级/淘汰决定；后者记录每条知识是否被检索、披露、采用和实际激活。

**输出。** 原子提交的新快照 $M_{t+1}$。下一轮只有在新的 trace 已经形成 `MethodNeed` 后，才以该需求查询 $M_{t+1}$ 并构造 `CrossTaskEvidenceView`；不存在脱离查询预先生成的通用视图。证据持久化与派生知识提交是两次操作：即使知识修订失败，原始证据也不能丢失。

本阶段由 `OptimizerLLM` 把异构运行证据综合为可检验的知识提案，由 `OptimizerHarness` 决定哪些提案能够进入长期状态。`EVIDENCE_TO_CLAIM` 从 trace、gate、配对运行、消融和使用链中提出最小声明；`REGIME_DISCOVERY` 寻找成功与失败证据可能由模型、工具、任务或宿主条件分开的边界；`CLAIM_RELATION_PROPOSAL` 比较新旧声明的重复、细化、冲突和替代关系；`SCOPE_SEPARATOR_PROPOSAL` 为稳定反例提出最小可检查区分谓词；`REUSABLE_LESSON_SYNTHESIS` 把已经通过证据门的结论整理为后续检索可消费的机制、适配规则与反例；`RETRIEVAL_FAILURE_REFLECTION` 分析“检索到但未采用、采用但未激活、激活但无效果”的断点并提出检索策略修订。所有输出都只是带锚点的提案，不能直接修改 $M_t$；原始证据追加、规则核验、效果后验、scope 升降、稳定性—可塑性检查与原子提交仍由 `OptimizerHarness` 完成。

记忆状态为：

$$
M_t=(E_t,C_t,J_t,U_t,R_t,\Pi_t,I_t),
$$

| 分量 | 保存内容 |
| --- | --- |
| $E_t$ | 只追加的原始证据事件 |
| $C_t$ | 可修订的方法声明、适配声明和经验声明 |
| $J_t$ | 声明—前提—证据的依赖图 |
| $U_t$ | 从检索到结果的使用账本 |
| $R_t$ | 由模型、工具、数据与宿主版本划分的 evidence regime |
| $\Pi_t$ | 声明写入、关系判定、scope 升降、归档和检索的版本化策略状态 |
| $I_t$ | 供证据组织与检索阶段使用的检索索引 |

证据、总结、当前信念与效用不能塞进同一条记录。最小 schema 为：

```text
EvidenceEvent = {
  event_id, kind, source_pointer,
  valid_from, valid_to, learned_at,
  task_descriptor, harness_version, model_version, tool_version,
  candidate_id, method_ids, trace_slice, metric_vector,
  repetitions, paired_run_id, reproducibility_status
}

ClaimRevision = {
  claim_id, revision, mechanism, preconditions, expected_effect,
  interface_contract, scope, regime_id, status,
  minimal_support_sets, oppose_ids,
  effect_posterior, regression_posterior, derived_from
}

UsageEvent = {
  usage_id, query_id, claim_id,
  retrieved, disclosed, adopted, activated,
  affected_result, candidate_id, paired_run_id
}
```

`valid_from/valid_to` 表示声明适用于现实中的哪个版本区间，`learned_at` 表示系统何时获知它；历史重放必须同时使用两条时间轴。`minimal_support_sets` 保存足以支持声明的最小证据与前提集合。确定性前提失效时沿 $J_t$ 撤回依赖声明，但随机任务失败只能形成经验反证，不能直接写成逻辑矛盾。

**算法 4：来源保持的事务式巩固。**

1. **追加原始事件。** 本轮父代与候选的完整 trace、候选代码差异、机制 gate、配对评测、案例角色和方法使用记录先写入 $E_t$；撤回只增加撤回事件，不覆盖旧记录。离线 `SourcePacket` 通过来源指针被引用，不在此处重新解析或改写。
2. **生成并核验原子声明。** `OptimizerHarness` 把新事件、对应 trace 切片、候选差分、激活状态和配对结果组成 `EVIDENCE_TO_CLAIM` 视图。`OptimizerLLM` 提出“某机制在条件 $c$ 下被激活”“某 adapter 在宿主 $h$ 上失败”“候选在任务族 $d$ 上产生收益或回归”等最小声明，并逐字段引用事件。程序核验 `derived_from`、时间、数据角色和可识别性；不支持的效果主张降为 `observational_association`。
3. **发现可能的 evidence regime。** 当相同机制在不同模型、工具、任务或宿主条件下出现稳定异质性时，`REGIME_DISCOVERY` 提出候选分界和判别实验。`OptimizerHarness` 只接受由已观测字段定义、能在留出训练案例上复核且不会引用测试标签的 regime；否则保持为未决假设。
4. **执行三层去重并判定关系。** 事件层按同一 source/run/revision 去重；声明层规范化 `mechanism + preconditions + interface + scope + regime` 后比较；机制层先用结构字段寻找候选匹配，再通过 `CLAIM_RELATION_PROPOSAL` 让 `OptimizerLLM` 提出重复、细化、冲突或替代关系。规则重新核对来源、条件交集、有效时间、regime 和依赖；不确定项进入 `pending-review`。只有条件有交集、有效时间重叠且 regime 相同时，结论相反才是真冲突。按下表在 copy-on-write 影子快照中处理：

   | 关系 | 操作 |
   | --- | --- |
   | 相同结论、相同来源 | `duplicate`：不新建声明，只补事件引用 |
   | 相同结论、独立来源或独立运行 | `merge-support`：增加独立支持边 |
   | 新声明条件更窄 | `refine`：建立父子条件 revision |
   | 模型、工具、数据或宿主版本不同 | `coexist-by-regime`：分 regime 共存 |
   | 同一来源的新版本明确替代旧版本 | `supersede`：关闭旧有效区间，保留审计视图 |
   | 同 regime、同条件下结论相反 | `split-condition`；无法找到区分条件则标为 `contested` 并向反例规划与测评阶段请求实验 |
   | 违反确定性接口、权限或状态不变量 | 写入 hard conflict，并沿依赖图撤回 |

   `OptimizerLLM` 给出的关系标签只是一条待核对提案，不能直接决定哪一方获胜。
5. **在 scope 偏序格上升降。** scope 不是单个标签，而是多维条件：

   ```text
   scope = (task/task-family/domain,
            harness-version/harness-family,
            model-version/model-family,
            tool-version,
            evidence-regime)
   ```

   新经验从 exact run 开始，每次只尝试移动到一个 immediate parent scope。对边界 $s\rightarrow parent(s)$，从新增覆盖区域选择未参与当前声明形成的 transfer cases，并运行旧能力 anchors。只有机制 probe 已确认激活、存在策略要求的独立任务与环境支持、配对效果后验下界高于采用阈值、回归概率上界低于阈值、无未决冲突且来源/历史/时间 fidelity 检查通过时，才提升一级。门槛数量和阈值都是实验超参数，不写成论文事实。
6. **用反例回缩或分裂 scope。** 出现可复现反例时，`OptimizerHarness` 构造成功/失败对照视图，`OptimizerLLM` 通过 `SCOPE_SEPARATOR_PROPOSAL` 提出最小可检查区分谓词 $g$、其字段来源和反例。程序拒绝不可观测、引用未来信息或只复述任务 ID 的谓词。若 $g$ 在新 case 上复核通过，则拆成 `scope∧g` 和 `scope∧¬g` 两个 revision；否则回缩到最近仍有独立支持且无反例的子 scope。一次成功不能提升，一次随机失败也不能永久删除。
7. **只给已激活知识分配效果信用。** 记录 `retrieved → disclosed → adopted → activated → affected-result` 五个事件。对已激活方法 $m$，在相同 task、seed 和 environment 上比较完整候选与 mask 掉 $m$ 的候选：

   $$
   d_m=\operatorname{metric}(H_{full})-
       \operatorname{metric}(H_{mask(m)}).
   $$

   用配对差更新当前 scope/regime 下的 `effect_posterior`。无法消融时只更新 `observational_association`。多方法组合先做 leave-one-out；若组合差异不能由单项差异解释，则新建 bundle claim，以组合而非单项作为归因对象。
8. **执行稳定性—可塑性门。** 每次提升、合并或替代前，分别运行应吸收合法更新的 $U$ 组 probe 和应保留旧知识的 $P$ 组 probe，计算 Plasticity、Stability 与二者的调和量，同时检查 previous-value、source/conflict-status 和 temporal fidelity。任一关键检查不满足策略阈值时，回滚派生快照，但保留失败事件。
9. **形成可复用经验并反思检索失败。** 对已经通过关系、scope、归因和稳定性门的声明，`REUSABLE_LESSON_SYNTHESIS` 生成面向后续查询的机制摘要、适用条件、adapter 经验、触发事件、反例和代码入口；程序逐项链接到已提交 claim 与证据。对本轮使用链中的断点，`RETRIEVAL_FAILURE_REFLECTION` 提出字段权重、查询分解或重排策略修订，`OptimizerHarness` 只在离线回放或后续训练轮验证后更新 $\Pi_t$，不能用当前 select 结果直接追调同轮检索器。
10. **准备下一轮可查询状态。** 新索引随影子快照一起接受审计，但此时不假设下一轮查询。下一轮 `MethodNeed` 形成后，`RETRIEVE_VIEW(M, query, as_of, scope_ceiling)` 再对已提交状态做权限、scope、双时态和 regime 硬过滤；取回相关声明后执行依赖闭包，把支持、反证、前置条件、效用区间、代码入口和失败案例组成有界证据子图。
11. **达到固定点后原子提交。** 当所有 proposal 已归类或显式标记 pending、依赖传播达到固定点、没有可立即执行的 scope 移动、稳定性—可塑性检查完成且策略不变量成立时，提交新快照。检查项包括来源可达、无静默覆盖、无跨 regime 混算和无越级 scope 提升。

```text
CONSOLIDATE(M, eval_ledger, usage_ledger):
    # A. 原始证据先追加；语义综合只产生提案
    normalized_events <- NORMALIZE_EVENTS(eval_ledger, usage_ledger)
    E1 <- APPEND_ONLY(M.E, normalized_events)
    claim_request <- BUILD_EVIDENCE_TO_CLAIM_REQUEST(E1.new_events)
    claim_call <- CALL_OPTIMIZER_LLM(claim_request)
    claim_proposals <- PARSE_ATOMIC_CLAIM_PROPOSALS(claim_call)
    proposals <- VERIFY_CLAIM_EVENT_ANCHORS_AND_IDENTIFIABILITY(
                     claim_proposals, E1.new_events)
    shadow <- COPY_ON_WRITE(M with E=E1)

    # B. 候选 regime、声明关系和依赖传播
    regime_request <- BUILD_REGIME_DISCOVERY_REQUEST(
                          proposals, E1.new_events, shadow.R)
    regime_call <- CALL_OPTIMIZER_LLM(regime_request)
    regime_proposals <- PARSE_REGIME_PROPOSALS(regime_call)
    verified_regimes <- VALIDATE_REGIME_PREDICATES_AND_HOLDOUTS(
                            regime_proposals, E1.new_events)
    APPLY_VERIFIED_REGIME_REVISIONS(verified_regimes, shadow)

    for c in proposals:
        matches <- FIND_BY_NORMALIZED_KEY_AND_OVERLAPPING_SCOPE(c, shadow)
        relation_request <- BUILD_CLAIM_RELATION_REQUEST(c, matches)
        relation_call <- CALL_OPTIMIZER_LLM(relation_request)
        relation_proposal <- PARSE_RELATION_PROPOSAL(relation_call)
        relation <- RULE_CHECK(relation_proposal)
        action <- SELECT_TRANSACTIONAL_ACTION(relation)
        APPLY(action, c, shadow)
    PROPAGATE_WITHDRAWALS_TO_FIXED_POINT(shadow.J)

    # C. 使用与结果分开记账
    UPDATE_USAGE_STAGES(shadow.U, usage_ledger)
    for m in ACTIVATED_METHODS(usage_ledger):
        if HAS_MATCHED_MASK_ABLATION(m):
            UPDATE_EFFECT_POSTERIOR(m, PAIRED_DIFFERENCES(m))
        else:
            UPDATE_OBSERVATIONAL_ASSOCIATION_ONLY(m)
    CREATE_BUNDLE_CLAIMS_FOR_DETECTED_INTERACTIONS(shadow)

    # D. scope 一次只移动一条偏序边
    repeat:
        changed <- false
        for c in CHANGED_CLAIMS(shadow):
            if CONFIRMED_COUNTEREXAMPLE(c):
                separator_request <- BUILD_SCOPE_SEPARATOR_REQUEST(
                                         c, successes(c), failures(c))
                separator_call <- CALL_OPTIMIZER_LLM(separator_request)
                separator_proposal <- PARSE_SCOPE_SEPARATOR_PROPOSAL(
                                          separator_call)
                g <- VALIDATE_CHECKABLE_SEPARATOR(separator_proposal)
                if g is valid and VALIDATE_SEPARATOR(g): SPLIT_SCOPE(c, g)
                else DEMOTE_TO_LARGEST_SUPPORTED_SUBSCOPE(c)
                changed <- true
            else:
                s_next <- IMMEDIATE_PARENT(c.scope)
                if PROMOTION_EVIDENCE_PASSES(c, s_next) and
                   STABILITY_PLASTICITY_PROBES_PASS(c, s_next):
                    PROMOTE_ONE_LEVEL(c, s_next)
                    changed <- true
    until not changed

    # E. 形成复用经验并提出检索策略修订
    lesson_request <- BUILD_REUSABLE_LESSON_REQUEST(
                          CHANGED_CLAIMS(shadow), shadow.U, E1.new_events)
    lesson_call <- CALL_OPTIMIZER_LLM(lesson_request)
    lesson_proposals <- PARSE_REUSABLE_LESSONS(lesson_call)
    ATTACH_VERIFIED_LESSONS_TO_CLAIMS(lesson_proposals, shadow)

    failures <- RETRIEVAL_USAGE_FAILURE_CHAINS(shadow.U, usage_ledger)
    if failures is not empty:
        retrieval_request <- BUILD_RETRIEVAL_FAILURE_REFLECTION_REQUEST(
                                 failures, shadow.Pi)
        retrieval_call <- CALL_OPTIMIZER_LLM(retrieval_request)
        policy_proposals <- PARSE_RETRIEVAL_POLICY_PROPOSALS(retrieval_call)
        QUEUE_POLICY_REVISIONS_FOR_OFFLINE_REPLAY(policy_proposals, shadow)

    # F. 派生知识失败时仍返回已追加的证据
    if not POLICY_INVARIANTS_HOLD(shadow):
        return M.with(E=E1), pending_review
    if not REPLAY_NEW_AND_OLD_ANCHORS(shadow):
        return M.with(E=E1), failed_consolidation

    M1 <- ATOMIC_COMMIT(shadow)
    return M1
```

### 四阶段在多轮 Harness 演化中的完整流转

前面四个阶段共同组成训练集上的一轮 Harness 更新，而不是只执行一次的线性流水线。实验开始前只执行一次离线组织：`OptimizerLLM` 从固定来源提出带锚点的方法声明，`OptimizerHarness` 核验并冻结目录；同时封存 benchmark 测试集。在线 loop 从 $(H_0,M_0)$ 开始，其中 $H_0$ 是未经本方法优化的父 Harness，$M_0$ 是尚未写入目标 benchmark 运行证据的长期状态。每轮首先按前文规则冻结 $D_t^{\mathrm{trace}}$、$D_t^{\mathrm{select}}$ 和 $D_t^{\mathrm{anchor}}$，再运行 $H_t$ 产生 trace。随后 `OptimizerLLM` 依次参与需求解释、语义重排、因果诊断、候选生成、证据解释、动作提议与知识综合；每次输出都由 `OptimizerHarness` 依据当前阶段的来源、权限、数据角色和执行规则核验。

阶段三产生 `return-counterexample` 时仍停留在第 $t$ 轮。若反例指向 hook、adapter、位置或接口绑定，就带着经核验的归因和更新后的约束返回阶段二生成新候选；若反例暴露方法、依赖或适用条件缺口，就由 `OptimizerLLM` 提出 `MethodNeed` 修订并返回阶段一在线检索。凡是已经向 `OptimizerLLM` 披露并影响修订的 select case，都从受影响后代的独立判定池中移除并补充新案例。只有得到 `Promote`、`Reject` 或 `Tie`，并把本轮 `EvaluationLedger` 与 `UsageLedger` 交给阶段四完成一次可审计的持久化后，本轮才结束。

进入下一轮需要同时准备 Harness 状态、知识状态和数据状态。`Promote` 令获胜候选成为 $H_{t+1}$，`Reject` 或 `Tie` 令 $H_{t+1}=H_t$；阶段四产生 $M_{t+1}$；训练调度器更新每个案例曾承担的角色、已经覆盖的任务族、待复核反例和旧能力 anchors。第 $t+1$ 轮不能沿用第 $t$ 轮候选的统计量：它必须用 $H_{t+1}$ 在新分配的 $D_{t+1}^{\mathrm{trace}}$ 上重新运行，生成新的 trace 和 `MethodNeed`，然后才从 $M_{t+1}$ 构造该需求对应的 `CrossTaskEvidenceView`。

```text
EVOLVE_ON_BENCHMARK_TRAIN(H0, M0, catalog_snapshot,
                          D_train, train_protocol):
    scheduler <- INIT_TRAIN_SCHEDULER(D_train, train_protocol)
    llm_call_ledger <- INIT_LLM_CALL_LEDGER(train_protocol)
    H <- H0
    M <- M0
    t <- 0
    confirmed_counterexamples <- empty

    loop:
        trace_pool, select_pool, anchor_pool <-
            ASSIGN_TRAIN_ROLES(scheduler, H, M)
        as_of, allowed_scope <- RESOLVE_REUSE_BOUNDARY(train_protocol, t)

        trace_batch <- RUN_HARNESS(H, trace_pool, train_protocol)
        diagnostic_evidence_view <- RETRIEVE_DIAGNOSTIC_CONTEXT(
                                        M, H, trace_batch, as_of)
        need <- BUILD_METHOD_NEED(H, trace_batch,
                                 diagnostic_evidence_view,
                                 confirmed_counterexamples)
        hypotheses <- need.competing_hypotheses
        evidence_view <- RETRIEVE_VIEW(M, need, as_of, allowed_scope)
        bundles, unresolved <-
            ONLINE_RETRIEVE(catalog_snapshot, evidence_view,
                            need, TRACE_VIEW(trace_batch))
        historical_patches <- RETRIEVE_PATCH_HISTORY(
                                  M, need, as_of, allowed_scope)
        hard_constraints <- COMPILE_ROUND_HARD_CONSTRAINTS(
                                H, train_protocol, need, bundles)

        round_eval_ledger <- LEDGER_FROM_TRACE_BATCH(trace_batch)
        round_usage_ledger <- empty
        RECORD_RETRIEVAL(round_usage_ledger, bundles)
        repeat:
            candidates <- SYNTHESIZE(
                              H, trace_batch, hypotheses, bundles,
                              confirmed_counterexamples,
                              historical_patches, hard_constraints)
            RECORD_CANDIDATE_USAGE(round_usage_ledger, candidates)
            prior_evidence <- RETRIEVE_PLANNING_PRIORS(
                                  M, candidates, hypotheses,
                                  as_of, allowed_scope)
            decision, new_eval_ledger, belief <-
                PLAN_AND_TEST(H, candidates, hypotheses,
                              select_pool union anchor_pool,
                              prior_evidence)
            APPEND(round_eval_ledger, new_eval_ledger)
            UPDATE_EXPOSURE_FROM_LLM_CALLS(
                scheduler, llm_call_ledger, candidates, select_pool)

            if decision is return-counterexample:
                cex <- CONFIRMED_COUNTEREXAMPLE(new_eval_ledger)
                select_pool <- REFRESH_INDEPENDENT_SELECT_POOL(
                                   scheduler, candidates, select_pool)
                if cex concerns hook, adapter, location, or interface:
                    confirmed_counterexamples <-
                        confirmed_counterexamples union {cex}
                    continue
                need <- REVISE_METHOD_NEED_WITH_COUNTEREXAMPLE(
                            H, trace_batch, need, cex,
                            diagnostic_evidence_view)
                evidence_view <- RETRIEVE_VIEW(
                                     M, need, as_of, allowed_scope)
                bundles, unresolved <-
                    ONLINE_RETRIEVE(catalog_snapshot, evidence_view,
                                    need, TRACE_VIEW(trace_batch))
                historical_patches <- RETRIEVE_PATCH_HISTORY(
                                          M, need, as_of, allowed_scope)
                hard_constraints <- COMPILE_ROUND_HARD_CONSTRAINTS(
                                        H, train_protocol, need, bundles)
                RECORD_RETRIEVAL(round_usage_ledger, bundles)
                continue
        until decision is Promote, Reject, or Tie

        usage_ledger <- COMPLETE_USAGE_LEDGER(round_usage_ledger,
                                              round_eval_ledger)
        M_next <- CONSOLIDATE(M, round_eval_ledger, usage_ledger)
        H_next <- ACCEPT_IF_PROMOTED(H, candidates, decision)
        UPDATE_TRAIN_SCHEDULER(scheduler, trace_pool, select_pool,
                               anchor_pool, decision, round_eval_ledger)

        if TRAIN_SPLIT_FIXED_POINT(scheduler, H, H_next,
                                   M, M_next, belief):
            break

        H <- H_next
        M <- M_next
        t <- t + 1

    return FREEZE_FOR_FINAL_TEST(H_next, M_next, catalog_snapshot,
                                 train_protocol)
```

`TRAIN_SPLIT_FIXED_POINT` 只在完成一个覆盖全部预定任务族的训练集轮换后检查。停止必须同时满足：该轮换中没有候选达到 `Promote`；全部剩余候选已经得到 `Reject` 或具有充分证据的 `Tie`，不存在仍可能改变决定的合法实验；最近一次 `SEARCH_BRANCH_REFLECTION` 没有产生通过核验的新故障假设、检索需求、自由分支或判别动作；没有新确认反例、claim revision、regime、scope 或待回放检索策略会改变下一轮候选空间。外部服务失败、运行中断、证据缺失、`pending-review`、`failed_consolidation` 或尚未回放的高影响策略提案都表示 loop 尚未完成，不能伪装成 stop。

stop 后冻结最终 Harness、方法目录版本、检索策略、模型与工具配置、评测器和随机协议。随后才在 $D_{\mathrm{test}}$ 上按照 benchmark 官方协议运行最终 Harness。测试阶段不再运行 `OptimizerHarness` 或调用 `OptimizerLLM`，不生成候选，不把测试 trace 写回 $M_t$，也不依据测试结果修改 Harness；测试 trace 只作为最终结果的审计材料保存。该阶段得到的测试指标才用于与 baseline 比较。

## 二、字段、公式与参数完整定义

### 统一约定

| 项目 | 约定 |
| --- | --- |
| 标识符 | 所有 `*_id` 在所属账本内唯一且写入后不可复用；版本对象使用新 ID 或递增 `revision`，禁止原地覆盖。 |
| 未知值 | 未观测、不可观测和不适用分别写成 `UNKNOWN`、`UNOBSERVABLE`、`NOT_APPLICABLE`；不得用 `0`、空字符串或空列表代替未知。 |
| 分数方向 | 除公式明确使用惩罚项外，所有 `score/gain/effect` 均为越大越好；进入加权和前缩放到 `[0,1]`。 |
| 概率 | 取值范围为 `[0,1]`。后验必须同时保存分布族或粒子集、样本量和更新时间。 |
| 时间 | `valid_from/valid_to` 描述事实适用的事件时间；`learned_at` 描述系统获知该事实的时间，统一使用带时区的 ISO 8601。 |
| 版本 | Harness、模型、工具、论文和代码均使用可精确定位的版本；“latest”不是合法值。 |
| 证据 | 论文报告、本地复现、目标任务实验和 `OptimizerLLM` 提案分别标注；模型提案不是经验事实，不与前三类合并成同一证据等级。 |

### 端到端输入与输出

系统级输入是 benchmark 训练集、初始父版本 Harness、初始长期状态、共享 `SourcePacket` 和硬约束。外层循环将训练集轮换为故障发现批次、候选判定面板和旧能力回放集合；内层循环接收固定父版本、故障发现 trace、当前证据视图和本轮判定数据，依次执行组织与检索、候选综合、规划与测评、长期沉淀。

每个内层轮次输出冻结候选的决策、父子配对证据、反例、方法主张修订和使用账本；每个外层轮次输出下一父 Harness 与下一长期状态。最终输出是在完整训练集轮换达到固定点后冻结的 Method、检索策略和 Harness。benchmark 测试集不属于任何演化输入。任何阶段发现缺失前提时，都返回显式未解决项，不擅自补成事实。

### 字段规范

#### Benchmark 数据角色与轮次边界

| 符号 | 来源与用途 | 隔离约束 |
| --- | --- | --- |
| $D_{\mathrm{train}}$ | benchmark 官方训练集，是整个在线演化唯一允许访问的任务全集。 | 不包含测试实例；官方没有训练集时必须事先定义可公开使用的开发集，不能从测试集回填。 |
| $D_t^{\mathrm{trace}}$ | 第 $t$ 轮故障发现批次；运行 $H_t$ 产生候选生成所需的成功/失败 trace。 | 当前轮不得再作为 $D_t^{\mathrm{select}}$ 的独立收益证据。 |
| $D_t^{\mathrm{select}}$ | 第 $t$ 轮候选判定池；父代和候选在相同任务、种子、环境下配对运行。 | 候选冻结前不得向 `OptimizerLLM` 披露其 trace、标签或评测结果。 |
| $D_t^{\mathrm{anchor}}$ | 第 $t$ 轮旧能力回放池；来自此前已确认能力、严重失败和晋级边界。 | 只判断能力保留与回归；已暴露案例不声称未见泛化。 |
| $D_{dev}^{(t)}$ | $D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}$，是阶段三在第 $t$ 轮可调度的完整任务域。 | 不得包含 $D_{\mathrm{test}}$；收益估计和回归检查分别标识来源角色。 |
| $D_{\mathrm{test}}$ | benchmark 官方封存测试集，只用于 stop 后的最终比较。 | 不参与 trace 生成、检索、候选生成、动作选择、阈值设定、记忆更新或 stop 判断。 |

案例暴露记录至少保存 `task_id`、出现过的轮次、每轮角色、向 `OptimizerLLM` 披露过的字段、运行过的 Harness/候选版本和产生的证据 ID。角色可以跨轮轮换，但一旦案例内容影响过某个候选的生成或修订，它就不能再为该候选提供独立收益证据。

#### `TrainProtocol`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `benchmark_revision` | 版本 ID | benchmark 的固定发布版本。 |
| `split_revision` | 版本 ID | 官方 train/test 划分及训练集内部角色划分规则的版本。 |
| `task_strata` | 分层规则 | 用于保证任务族、难度、工具类型和轨迹长度覆盖的预注册分层。 |
| `role_assignment_rule` | 确定性规则或带种子抽样器 | 根据分层、暴露历史和未决故障产生每轮三组两两不相交的数据角色。 |
| `reuse_policy` | 双时态与作用域配置 | 规定每轮 `as_of` 的取值、允许复用的最大 `scope_ceiling`、可接受的 regime 与陈旧度；用于构造长期证据视图、历史 patch 和规划先验，实验中不可追随结果改写。 |
| `execution_config` | 配置快照 | 模型、provider、推理参数、工具、容器、超时、并发和 trace instrumentation。 |
| `optimizer_harness_revision` | 版本 ID | 上述反例构造、检索、草图编译、双通道请求构造、候选 gate、信念控制和证据巩固组件的联合代码与配置版本。 |
| `optimizer_llm_config` | `OptimizerLLMConfig` | `OptimizerLLM` 在知识抽取、需求解释、检索重排、因果诊断、候选生成、证据解释、动作规划和知识巩固中的运行配置；任一字段改变都产生新的实验条件。 |
| `evaluator_revision` | 版本 ID | 评分器、解析器、错误分类器和指标方向的固定版本。 |
| `seeds` | 种子计划 | 父子配对、重复运行、任务抽样和环境随机性的种子及复用规则。 |
| `promotion_rule` | 决策配置 | 实践阈值、回归边界、置信序列和 hard gate 条件。 |
| `stop_rule` | 固定点配置 | 训练集完整轮换的定义、无晋级条件、未决动作条件和知识状态稳定条件。 |

#### `OptimizationAgent`

本方法中的 `OptimizationAgent` 定义为：

$$
\text{OptimizationAgent}=\text{OptimizerLLM}+\text{OptimizerHarness}.
$$

公式中的加号表示二者共同组成一个可运行系统，不表示数值相加。`OptimizerLLM` 是贯穿知识理解、需求解释、trace 因果诊断、候选设计、证据解释、搜索规划和经验抽象的认知核心；`OptimizerHarness` 是围绕 `OptimizerLLM` 固定来源与数据角色、构造最小输入视图、核验锚点与权限、执行检索和程序分析、运行候选与统计评测、维护账本并提交长期状态的外部程序。`OptimizerLLM` 产生的始终是可核验提案，`OptimizerHarness` 不能用规则替代语义推理，也不能把未经真实证据验证的模型判断升级为事实。

`OptimizerHarness` 在本方法中由以下相互衔接的组件构成：

| 组件 | 本方法中的唯一职责 | 是否调用 `OptimizerLLM` |
| --- | --- | --- |
| `method_catalog_and_retriever` | 对齐固定来源、核验声明锚点、冻结目录；构造 `MethodNeed` 视图，执行字段召回、硬过滤、依赖闭包、冲突打包和排序融合。 | 发起 `SOURCE_CLAIM_EXTRACTION`、`TRACE_TO_METHOD_NEED`、`SEMANTIC_BUNDLE_RERANK`。 |
| `counterexample_constructor` | 从 $D_t^{\mathrm{trace}}$ 的成功/失败运行中选择诊断案例，执行随机感知 ddmin，形成最小 trace 切片，并核验语义归因引用。 | 发起 `TRACE_CAUSAL_DIAGNOSIS`、`COUNTEREXAMPLE_GUIDED_REVISION`。 |
| `localizer_and_sketch_compiler` | 把切片映射到 Harness 代码位置，将经核验诊断和检索方法编译为带 `FixedMechanism`、`TypedHoles`、硬约束和预期事件的 `MethodSketch`。 | 不直接调用；消费已核验的诊断与修订提案。 |
| `knowledge_synthesis_channel` | 为每个草图构造只含来源机制、待填孔位、宿主代码切片和约束的请求，解析知识约束补全结果。 | 是，发起 `KNOWLEDGE_COMPLETION`。 |
| `free_exploration_channel` | 构造不含本轮方法束和知识候选补丁的独立请求，解析知识库之外的局部修改。 | 是，发起 `FREE_EXPLORATION`。 |
| `candidate_normalizer_and_gate` | 将两条通道输出转成共同 Candidate IR，去重并检查编译、接口、权限、hook、fallback、数据隔离和修改范围；只允许一次受控语义修订。 | 对符合条件的语义性拒绝发起 `GATE_FAILURE_REFLECTION`。 |
| `counterexample_belief_controller` | 维护根因、适用性、接入、激活和收益粒子，运行 gate 与任务，核验解释和动作提案，并依据冻结规则决定 `Promote/Reject/Continue/Tie`。 | 发起 `EVIDENCE_INTERPRETATION`、`COUNTEREXAMPLE_ATTRIBUTION`、`NEXT_ACTION_PROPOSAL`、`SEARCH_BRANCH_REFLECTION`。 |
| `evidence_consolidator` | 追加证据与使用账本，核验并组织 claim、regime、关系、scope、复用经验和检索策略提案，执行效果归因、稳定性—可塑性检查和原子提交。 | 发起 `EVIDENCE_TO_CLAIM`、`REGIME_DISCOVERY`、`CLAIM_RELATION_PROPOSAL`、`SCOPE_SEPARATOR_PROPOSAL`、`REUSABLE_LESSON_SYNTHESIS`、`RETRIEVAL_FAILURE_REFLECTION`。 |
| `llm_call_ledger` | 追加保存全部 `OptimizerLLM` 调用的实际输入视图、原始输出、解析结果、验证状态和资源消耗。 | 不产生调用，只记录调用。 |

被优化的执行 agent 由当前执行模型与 $H_t$ 组成，负责在 benchmark 任务上产生 `ExecutionTrace`。`OptimizerHarness` 按当前 call type 的披露规则构造最小视图，`OptimizerLLM` 负责对该视图进行语义推理并返回结构化提案，随后仍由 `OptimizerHarness` 解析、核验、执行和记录。即使 `OptimizerLLM` 与执行模型相同，也必须使用不同会话、上下文、工具权限和调用账本。

#### `OptimizerLLMConfig`

`OptimizerLLMConfig` 固定上述 `OptimizerLLM` 在本方法全部认知步骤中的运行方式，不描述执行 agent 使用的任务模型。

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `model_revision` | 版本 ID | 模型、provider 与不可变模型版本；别名必须解析到实际版本。 |
| `inference_config` | 配置对象 | temperature、top-p、最大输出、推理强度、停止条件和种子策略。 |
| `call_types` | 枚举集合 | 只允许：`SOURCE_CLAIM_EXTRACTION`、`TRACE_TO_METHOD_NEED`、`SEMANTIC_BUNDLE_RERANK`、`TRACE_CAUSAL_DIAGNOSIS`、`COUNTEREXAMPLE_GUIDED_REVISION`、`KNOWLEDGE_COMPLETION`、`FREE_EXPLORATION`、`GATE_FAILURE_REFLECTION`、`EVIDENCE_INTERPRETATION`、`COUNTEREXAMPLE_ATTRIBUTION`、`NEXT_ACTION_PROPOSAL`、`SEARCH_BRANCH_REFLECTION`、`EVIDENCE_TO_CLAIM`、`REGIME_DISCOVERY`、`CLAIM_RELATION_PROPOSAL`、`SCOPE_SEPARATOR_PROPOSAL`、`REUSABLE_LESSON_SYNTHESIS`、`RETRIEVAL_FAILURE_REFLECTION`。 |
| `prompt_template_revisions` | 映射 | 每种 call type 使用的系统指令、输入序列化和输出 schema 版本。 |
| `context_policies` | 映射 | 每种 call type 允许披露的对象和字段；未列字段默认禁止。 |
| `tool_policy` | 权限对象 | `OptimizerLLM` 可调用的代码读取、编辑沙箱、静态分析和测试工具；禁止读取 select/test 数据及直接写入父 Harness 或账本。 |
| `retry_policy` | 规则对象 | 超时、格式错误和工具失败的最大重试数及退避规则；每次重试单独记账。 |
| `parser_revision` | 版本映射 | 每种 call type 对应的输出 schema 与固定解析器 revision；解析器只能拒绝或提取字段，不能补写模型未输出的语义内容。 |

#### `LLMCallRecord`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `call_id` | 唯一 ID | 一次 `OptimizerLLM` 请求；重试创建新的 ID 并用 `parent_call_id` 连接。 |
| `round_id` | 非负整数或离线 revision | 在线调用所属 Harness 演化轮次；`SOURCE_CLAIM_EXTRACTION` 使用 `OFFLINE:<catalog_revision>`。 |
| `call_type` | 枚举 | `OptimizerLLMConfig.call_types` 中的一种，决定允许披露的对象、输出 schema 和核验器。 |
| `model_revision` | 版本 ID | 实际处理该请求的 `OptimizerLLM` 版本，必须与 `OptimizerLLMConfig` 一致。 |
| `prompt_template_revision` | 版本 ID | 本次请求使用的系统指令、序列化模板和输出约束版本。 |
| `input_view_revision` | 版本 ID | Harness 为本次调用构造的最小权限视图；它不是完整内部状态。 |
| `disclosed_artifact_ids` | ID 列表 | 实际披露的代码切片、trace 切片、草图、硬约束、声明或反例；顺序与输入一致。 |
| `forbidden_artifact_check` | `PASS/FAIL` | 调用前对 select/test、隐藏标签和越权路径执行的检查结果；`FAIL` 时不得发起请求。 |
| `tool_session_id` | ID 或 `NONE` | 本次调用使用的隔离工具会话，保存权限、命令、读写路径与退出状态。 |
| `seed` | 整数或 `UNCONTROLLED` | 实际生成种子；provider 不支持固定种子时显式标记。 |
| `raw_output_ref` | 不可变定位 | `OptimizerLLM` 原始输出的存储位置，不能只保存解析结果。 |
| `parsed_output_ids` | ID 列表 | 解析得到的 `OptimizerProposal`、Candidate IR 或 `RelationProposal` ID；解析失败为空。 |
| `validation_status` | 枚举 | `PENDING`、`PARSE_FAILED`、`ANCHOR_REJECTED`、`GATE_REJECTED`、`RULE_REJECTED`、`EVIDENCE_REJECTED` 或 `ACCEPTED_AS_PROPOSAL`；不表示提案已经成为事实、候选已经晋级或状态已经提交。 |
| `parent_call_id` | ID 或 `NONE` | 格式修复或受控重试所基于的前一次调用。 |
| `usage` | 资源向量 | 输入/输出 token、费用、时延和工具调用数，只用于成本与复现记录。 |

全部 `LLMCallRecord` 按调用开始顺序追加到实验级 `LLMCallLedger`。该账本只保存 `OptimizerLLM` 的推理 provenance，不把 `OptimizerLLM` 自述当成方法证据；方法声明、诊断、需求、候选、动作提案和长期知识都通过 `call_id` 或 `llm_call_ids` 回指来源调用。调用失败、解析失败和核验拒绝同样保留，旧记录不得覆盖。

#### `OptimizerProposal`

所有非代码类 `OptimizerLLM` 输出先解析为统一外壳：

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `proposal_id` | 唯一 ID | 一项不可变提案；同一调用返回多项时分别编号。 |
| `call_id` | ID | 产生该提案的 `LLMCallRecord`。 |
| `proposal_type` | 枚举 | 与发起调用的 `call_type` 一致；不一致时解析失败。 |
| `target_ids` | ID 列表 | 被解释、比较、修改或总结的来源、trace、候选、claim、scope、动作或策略对象。 |
| `payload` | 类型化对象 | 由下表规定的 call-specific 内容；缺少必填字段时不能进入核验。 |
| `evidence_anchors` | 锚点列表 | 每个 payload 关键字段引用的来源段落、代码符号、trace 事件、账本事件或 claim revision。 |
| `counterevidence` | 锚点列表 | 与提案相冲突或使其失效的已知证据；没有时为空列表而非省略。 |
| `uncertainties` | 未知项列表 | 无法从披露视图判断的前提、替代解释和所需观察。 |
| `expected_observations` | 谓词列表 | 提案正确时应出现、错误时不应出现的可执行观察；纯来源抽取允许为 `NOT_APPLICABLE`。 |
| `validation_status` | 枚举 | `PENDING/ACCEPTED/REJECTED/PARTIALLY_ACCEPTED`；由 `OptimizerHarness` 写入，`OptimizerLLM` 无权设置最终值。 |

`payload` 按 call type 使用以下 schema：

| call type | payload 必填字段 | 各字段精确定义 |
| --- | --- | --- |
| `SOURCE_CLAIM_EXTRACTION` | `{problem_signatures, target_capability, mechanism_unit, atomic_claims, preconditions, forbidden_conditions, generic_interface_requirements, expected_observations, reported_successes, limitations, dependencies, conflicts, relation_candidates}` | `problem_signatures` 是来源中可观测的目标问题模式；`target_capability` 是方法预期新增或恢复的可观测能力；`mechanism_unit` 是不可再拆而不破坏机制的步骤组；`atomic_claims` 是单一主语、条件和结论的声明；`preconditions` 是应用前必须成立的可检查谓词；`forbidden_conditions` 是成立即禁止接入的谓词；`generic_interface_requirements` 是与具体宿主路径无关的 hook、输入输出、状态、权限与异常要求；`expected_observations` 是机制正确运行时应在 trace 中出现的事件谓词；`reported_successes` 是保留原实验条件的来源结果；`limitations` 是来源明确报告或可直接推出的失败边界；`dependencies` 与 `conflicts` 是方法运行所需组件和不可共存条件；`relation_candidates` 是与其他声明可能存在的有类型关系及双方锚点。 |
| `TRACE_TO_METHOD_NEED` | `{competing_hypotheses, desired_capability, problem_description, known_constraints, forbidden_properties, acceptable_evidence, unresolved_questions, query_plan}` | `competing_hypotheses` 是互不强行合并的可反驳故障解释；`desired_capability` 是需要新增或恢复的可观测行为；`problem_description` 是失败对象、阶段、频率、严重度和最小事件链；`known_constraints` 是已确认接口、权限、环境和能力保留约束；`forbidden_properties` 是候选不得具有的行为；`acceptable_evidence` 是当前需求允许采用的来源类型、重复、配对与陈旧度门槛；`unresolved_questions` 是尚缺事实及取证动作；`query_plan` 是五类字段查询、优先级与停止条件。 |
| `SEMANTIC_BUNDLE_RERANK` | `{bundle_order, mechanism_matches, migration_gaps, complementarities, refutation_tests}` | `bundle_order` 是仅对输入 bundles 的全序或带并列偏序；`mechanism_matches` 是每个 bundle 与故障假设之间的逐步对应；`migration_gaps` 是目标 Harness 缺失的 hook、状态、接口或环境条件；`complementarities` 是 bundle 内方法相互补足的机制及依赖；`refutation_tests` 是能够推翻该匹配解释的可执行观察。 |
| `TRACE_CAUSAL_DIAGNOSIS` | `{earliest_divergence, causal_chain, candidate_root_cause, alternative_causes, discriminating_probes}` | `earliest_divergence` 是失败 trace 相对匹配成功 trace 的最早可观测偏离；`causal_chain` 是从该偏离到最终失败的有序事件、状态和代码位置链；`candidate_root_cause` 是链首可能的可干预原因；`alternative_causes` 是同样解释观察的竞争原因；`discriminating_probes` 是能区分这些原因的最小实验。 |
| `COUNTEREXAMPLE_GUIDED_REVISION` | `{counterexample_class, affected_claims, revision_kind, target_locations, preserved_mechanism, required_checks}` | `counterexample_class` 是硬约束、未激活、adapter、适用性、regime、回归或未知；`affected_claims` 是被反例削弱的声明 revision；`revision_kind` 是收紧、重绑、替换、相邻检索或自由分支；`target_locations` 是允许修改的代码或草图孔位；`preserved_mechanism` 是不得改变的来源机制步骤；`required_checks` 是修订后必须重跑的 gate 和反例。 |
| `GATE_FAILURE_REFLECTION` | `{failure_explanation, minimal_revision, unchanged_fields, expected_gate_change}` | `failure_explanation` 是逐项对应 gate 报告的语义错误解释；`minimal_revision` 是在原位置和硬约束内的最小代码/绑定变化；`unchanged_fields` 是必须保持的机制、接口和行为字段；`expected_gate_change` 是修订后应由 FAIL/UNRESOLVED 变为 PASS 的具体检查。 |
| `EVIDENCE_INTERPRETATION` | `{supported_hypotheses, opposed_hypotheses, unidentified_claims, alternative_explanations, next_observations}` | `supported_hypotheses` 和 `opposed_hypotheses` 分别列出被当前事件支持或削弱的 hypothesis ID 及锚点；`unidentified_claims` 是当前设计无法归因的主张；`alternative_explanations` 是仍与观察相容的解释；`next_observations` 是区分这些解释所需的事实，不包含最终决策。 |
| `COUNTEREXAMPLE_ATTRIBUTION` | `{attribution_hypotheses, distinguishing_evidence, affected_scope, revision_destination}` | `attribution_hypotheses` 是方法、adapter、激活、regime 或旁路干扰的候选归因；`distinguishing_evidence` 是各归因预期不同的事件或实验；`affected_scope` 是反例当前能够约束的最大条件范围；`revision_destination` 是返回检索、草图、adapter、自由分支或仅继续取证。 |
| `NEXT_ACTION_PROPOSAL` | `{action_kind, target_hypothesis, executable_parameters, expected_observation, stop_condition}` | `action_kind` 是允许动作枚举或新 probe；`target_hypothesis` 是动作要区分的 belief 分量；`executable_parameters` 是任务、候选、seed、变换和运行配置；`expected_observation` 是动作可能产生的判别事件；`stop_condition` 是结束该动作而不继续消耗评测的可检查条件。 |
| `SEARCH_BRANCH_REFLECTION` | `{stagnation_cause, missing_hypotheses, retrieval_need, free_branch_outline, discriminating_action}` | `stagnation_cause` 是候选同质、诊断错误、知识缺失、观测不足或约束过强；`missing_hypotheses` 是现有 belief 未表示的解释；`retrieval_need` 是需返回第一阶段的新能力/机制需求；`free_branch_outline` 是不依赖当前方法束的新局部方向；`discriminating_action` 是判断是否值得开启该分支的最小实验。 |
| `EVIDENCE_TO_CLAIM` | `{mechanism, preconditions, expected_effect, interface_contract, initial_scope, regime_id, support_event_ids, oppose_event_ids}` | `mechanism` 是实际激活或失败的控制机制；`preconditions` 是从事件中可核验的成立条件；`expected_effect` 是可观测方向和指标；`interface_contract` 是本次实现的宿主接口；`initial_scope` 从 exact run 开始；`regime_id` 指向有效环境区间或 `UNRESOLVED`；`support_event_ids/oppose_event_ids` 分别是原始支持与反对事件。 |
| `REGIME_DISCOVERY` | `{candidate_regime_predicate, differing_outcomes, confounders, holdout_validation_plan}` | `candidate_regime_predicate` 是只使用运行前或可审计环境字段的分界谓词；`differing_outcomes` 是谓词两侧的机制、收益或回归差异；`confounders` 是可能造成伪分界的任务、版本或选择因素；`holdout_validation_plan` 是未参与分界形成的训练案例和接受规则。 |
| `SCOPE_SEPARATOR_PROPOSAL` | `{separator_predicate, observable_fields, success_partition, failure_partition, falsification_cases}` | `separator_predicate` 是区分成功与反例的最小布尔谓词；`observable_fields` 是其实际读取字段及时间可用性；`success_partition/failure_partition` 是现有事件在谓词两侧的 ID 集；`falsification_cases` 是最可能击穿该分界的留出案例。 |
| `REUSABLE_LESSON_SYNTHESIS` | `{mechanism_summary, applicability, adapter_guidance, activation_events, counterexamples, code_entry_points}` | `mechanism_summary` 是不超出已提交 claim 的机制描述；`applicability` 是经验证 scope/regime；`adapter_guidance` 是成功与失败绑定规则；`activation_events` 是确认机制执行的事件谓词；`counterexamples` 是稳定失败边界；`code_entry_points` 是可追溯实现或补丁位置。 |
| `RETRIEVAL_FAILURE_REFLECTION` | `{failure_stage, causal_explanation, query_revision, weight_revision, rerank_revision, replay_plan}` | `failure_stage` 是 retrieved、disclosed、adopted、activated 或 affected-result 的首次中断处；`causal_explanation` 是带使用链锚点的原因；`query_revision` 是字段或分解修改；`weight_revision` 是检索分数参数提案；`rerank_revision` 是语义重排上下文或规则提案；`replay_plan` 是验证修订且不读取测试集的历史查询集合与接受条件。 |

`KNOWLEDGE_COMPLETION` 和 `FREE_EXPLORATION` 直接解析为 Candidate IR；`CLAIM_RELATION_PROPOSAL` 解析为下述 `RelationProposal`。`OptimizerProposal` 的 `ACCEPTED` 只表示通过该类提案的结构与锚点核验，不表示其语义已由实验确认。

#### `RelationProposal`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `proposal_id` | 唯一 ID | 一次待规则核验的语义关系提案。 |
| `call_id` | ID | 产生该提案的 `LLMCallRecord`。 |
| `left_claim_revision` | revision ID | 被比较的新声明或左侧声明。 |
| `right_claim_revision` | revision ID | 候选匹配的既有声明。 |
| `proposed_relation` | 枚举 | `SAME_CLAIM`、`REFINES`、`CONFLICTS`、`ALTERNATIVE_TO`、`SUPPORTED_BY` 或 `UNRESOLVED`；规则检查后再映射为事务动作。 |
| `field_evidence` | 字段到依据的映射 | 对 mechanism、preconditions、interface、scope、regime 和时间关系逐项给出的输入锚点；不得引用未披露内容。 |
| `uncertainties` | 列表 | 无法从输入视图判断的条件；空列表不代表规则已经接受提案。 |

#### `ExposureRecord`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `task_id` | ID | 被追踪的训练案例。 |
| `round_id` | 非负整数 | 该次使用发生的演化轮次。 |
| `split_role` | 枚举 | 该轮承担的 `TRACE/SELECT/ANCHOR` 角色。 |
| `disclosed_fields` | 字段集合 | `OptimizerLLM` 实际看到的任务输入、标签、trace、分数和评测反馈。 |
| `disclosed_to_call_ids` | 调用 ID 列表 | 实际接收该案例字段的全部 `LLMCallRecord`；只记录已发起调用，不记录尚未执行的计划。 |
| `affected_candidate_ids` | 候选 ID 列表 | 直接或间接使用这些调用输出生成、修订或选择动作的候选及其后代。 |
| `independence_status` | 枚举 | 对每个候选取 `INDEPENDENT/EXPOSED/NOT_APPLICABLE`；一旦披露结果影响候选修订，该案例对该候选及后代永久为 `EXPOSED`。 |
| `harness_versions` | 版本 ID 列表 | 在该案例上运行过的父代与候选版本。 |
| `evidence_ids` | ID 列表 | 该次使用产生的 `EvidenceEvent`；可由此审计是否仍具独立性。 |

#### `ExecutionTrace`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `task_id` | ID | benchmark 任务实例的稳定标识。 |
| `split_role` | 枚举 | 本次运行中任务所处角色，只取 `TRACE/SELECT/ANCHOR/FINAL_TEST`。 |
| `harness_version` | 版本 ID | 产生该 trace 的父代或候选 Harness 精确版本。 |
| `model_and_tool_versions` | 版本映射 | 模型、provider、推理配置、工具、容器及协议版本。 |
| `seed` | 整数或种子对象 | 控制模型、环境和评测随机性的完整种子；不可用时写明不可控来源。 |
| `ordered_events` | 有序事件列表 | 模型可见上下文与输出、工具调用与结果、记忆读写、控制转移、重试、回退、异常及终止事件；每项含顺序号和时间。 |
| `final_output` | 原始输出定位 | 执行 agent 的最终答案、补丁、状态或终止结果及其不可变存储位置。 |
| `metric_vector` | 命名数值映射 | 官方任务指标及预注册的回归、时延、token、稳定性指标；不预先压成总分。 |
| `failure_signature` | 谓词或 `NOT_APPLICABLE` | 由评测结果和事件链共同确定的目标失败模式；成功运行显式写 `NOT_APPLICABLE`。 |
| `replay_artifacts` | 定位集合 | 在许可范围内重放任务所需的输入、状态快照、工具响应记录和环境定位；不可重放项逐项标记。 |

#### `SourcePacket`

| 字段 | 类型与必填性 | 精确定义 |
| --- | --- | --- |
| `paper_version` | 对象，必填 | 论文 ID、标题、作者、固定版本、发布日期、原始 URL、本地 PDF 和解析文本路径。 |
| `official_code_version` | 对象，必填 | 官方仓库 URL、分支、固定 revision、获取日期、本地范围和许可证状态；没有官方代码时值为 `UNAVAILABLE` 并说明检索过程。 |
| `exact_source_anchors` | 锚点列表，必填 | 每条机制或限制对应的论文页码、章节、图表、代码文件、符号或行区间；锚点必须能被另一人重新定位。 |
| `configs_and_examples` | 记录列表，必填 | 官方配置、命令、数据入口、依赖、示例输入输出和运行前提；缺失项逐项写 `UNKNOWN`。 |
| `tests_and_reported_results` | 记录列表，必填 | 官方测试入口、数据划分、指标、对照、消融、数值、方差、失败条件，以及本地是否复核。 |

#### `EvidenceBoundMethod`

| 字段 | 类型与必填性 | 生产与消费 | 精确定义 |
| --- | --- | --- | --- |
| `method_id` | 字符串，必填 | 编译器产生；检索器、草图编译器消费 | 方法机制的稳定 ID；同一机制的新解释使用 revision，不另造同义 ID。 |
| `source_anchors` | 锚点列表，必填 | 来源对齐产生；审计器消费 | 支撑该方法全部声明的最小来源集合；每个声明至少绑定一个锚点。 |
| `problem_signatures` | 特征谓词列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、锚点核验；召回器消费 | 方法面向的可观测问题模式，例如连续工具失败、上下文溢出或验证缺失；不是自然语言主题标签。 |
| `target_capability` | 能力 ID 列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、观测性核验；需求匹配消费 | 预期新增或恢复的能力，必须能由 trace 或任务指标观测。 |
| `preconditions` | 布尔谓词列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、来源/代码核验；硬过滤器消费 | 应用方法前必须成立的条件；任一值为 `FALSE` 时禁止直接实例化，`UNKNOWN` 时要求先取证。 |
| `forbidden_conditions` | 布尔谓词列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、风险规则核验；硬过滤器消费 | 一旦成立便排除方法的条件，例如无权限写状态或工具不支持幂等重试。 |
| `ordered_mechanism` | 有序步骤列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、论文/代码顺序核验；草图编译器消费 | 从触发、状态读取、干预、观测到回退的完整顺序；步骤不得只写目标而缺少动作。 |
| `generic_interface_requirements` | 接口契约列表，必填 | 代码分析产生；绑定器消费 | 所需 hook、输入输出类型、状态读写、异常语义、权限和资源；不得绑定目标 Harness 的具体路径。 |
| `expected_observations` | 观测谓词列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、可执行性核验；激活 gate 消费 | 机制正确接入后 trace 中必须出现或改变的事件、字段和方向。 |
| `reported_successes` | 条件化结果列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、表格/配置锚点核验；先验估计消费 | 在原任务、模型、配置和评测协议下报告的收益；必须保留适用条件。 |
| `counterexamples_and_limitations` | 条件化反例列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议并由来源/本地实验核验；过滤和 scope 更新消费 | 已知失败、退化、无效或未覆盖情形；没有记录时写 `UNKNOWN`，不得写空列表表示不存在。 |
| `dependencies` | 方法 ID 与接口条件列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、依赖分析核验；闭包检索消费 | 方法运行前必须存在的组件、能力或状态。硬依赖和可替代依赖分开。 |
| `conflicts` | 冲突规则列表，必填 | `SOURCE_CLAIM_EXTRACTION` 提议、effect 规则核验；组合器消费 | 与其他方法的状态写冲突、顺序冲突、资源冲突和语义冲突，以及可否通过排序或 adapter 消解。 |
| `evidence_grade` | 枚举对象，必填 | 证据评估产生；排序器消费 | 分别记录机制描述、代码一致性、原结果、本地复核和目标迁移的等级；不得压成单一字母等级。 |
| `extraction_call_ids` | 调用 ID 列表，必填 | `SOURCE_CLAIM_EXTRACTION` 产生；审计器消费 | 产生或修订该方法语义字段的全部 `LLMCallRecord`；纯人工来源字段使用空列表并记录人工复核事件。 |
| `field_validation_status` | 字段到状态的映射，必填 | `OptimizerHarness` 写入；目录冻结器消费 | 每个语义字段取 `ANCHORED/EXECUTION_VERIFIED/UNKNOWN/REJECTED`；只有前两类能作为硬事实，`UNKNOWN` 只能参与待验证召回。 |

#### `MethodCatalogSnapshot`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `catalog_revision` | 版本 ID | 一次离线组织的不可变版本；任一来源、解析器、组织规则或索引配置改变都产生新版本。 |
| `source_packet_ids` | ID 列表 | 本目录纳入的全部 `SourcePacket`；顺序和版本固定。 |
| `method_revisions` | `EvidenceBoundMethod` revision 列表 | 离线编译出的全部方法对象及其版本。 |
| `claim_graph` | 有类型图 | 方法声明之间的依赖、冲突、替代、细化、支持和反证边。 |
| `field_indexes` | 索引映射 | 问题、机制、条件、观测、限制、证据和代码字段的稀疏/稠密索引。 |
| `organization_protocol` | 版本化配置 | 来源对齐与切分规则、`SOURCE_CLAIM_EXTRACTION` 提示模板 revision、输出 schema、parser revision、锚点核验器、关系核验器及索引构建配置；任一项变化都产生新的 `catalog_revision`。 |
| `llm_call_ids` | 调用 ID 列表 | 本目录离线组织期间全部 `SOURCE_CLAIM_EXTRACTION` 调用；包括解析或核验失败记录。 |
| `frozen_at` | 时间戳 | 目录冻结时间；本次 benchmark 演化期间不可更新。 |

#### `MethodNeed`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `need_id` | 唯一 ID | 与父 Harness、轮次、trace batch 和 revision 绑定；反例修订产生新 ID，不覆盖旧需求。 |
| `source_call_id` | 调用 ID | 产生当前需求 revision 的 `TRACE_TO_METHOD_NEED` 调用。 |
| `competing_hypotheses` | 假设列表 | 对同一失败的多个可反驳解释；每项含 trace/代码锚点、相反证据、未知条件和判别观察。 |
| `desired_capability` | 能力谓词列表 | 当前 Harness 必须新增、恢复或增强的可观测能力。 |
| `problem_description` | 结构化诊断 | 包含失败对象、发生阶段、最小 trace 片段、频率、严重度和现有假设。 |
| `known_constraints` | 硬约束列表 | 已知不可违反的接口、权限、预算、模型、工具和能力保留要求。 |
| `forbidden_properties` | 排除谓词列表 | 候选不得具有的行为，例如泄露测试答案、扩大写权限或吞掉工具错误。 |
| `acceptable_evidence` | 证据门槛对象 | 允许用于召回和接受的证据来源、最低重复数、是否要求配对及最大陈旧度。 |
| `unresolved_questions` | 问题列表 | 当前决策仍依赖但尚未观测的事实；每项包含可执行的取证动作或 `UNOBSERVABLE`。 |
| `query_plan` | 子查询计划 | 问题、机制、条件、证据和反例五类查询及其字段、预算和停止条件；只指导召回，不覆盖硬过滤。 |

#### `MethodSketch`

| 组成或孔位 | 类型 | 精确定义 |
| --- | --- | --- |
| `FixedMechanism` | 不可修改的控制骨架 | 来自 `ordered_mechanism` 的必要步骤、顺序和状态变化；实例化不得删除。 |
| `hook` | 枚举孔位 | 允许接入的生命周期事件，例如 `before_tool`、`after_tool`、`on_error`；必须来自宿主可用 hook 集。 |
| `location` | 代码位置孔位 | 文件、符号、基本块或配置路径；绑定后必须能由静态工具重新定位。 |
| `predicate` | 纯函数孔位 | 决定机制是否触发的布尔函数；列明输入字段、未知值行为和副作用为零。 |
| `adapter` | 适配器孔位 | 在宿主接口与通用方法接口之间转换数据和异常，不得改变方法语义。 |
| `parameter` | 参数孔位 | 阈值、上限、模型或策略选择；给出类型、范围、默认来源和调参数据边界。 |
| `ordering` | 偏序孔位 | 与现有中间件、工具调用、验证和回退步骤的先后关系；必须无环。 |
| `fallback` | 恢复孔位 | 机制失败、超时或不确定时执行的恢复路径，至少能回到父版本行为。 |
| `HardConstraints` | 布尔谓词集合 | 权限、接口、数据隔离和能力保留约束；静态或动态 gate 失败立即拒绝。 |
| `ExpectedTraceEvents` | 事件谓词集合 | 机制激活和效果的可观测定义；候选若无法产生这些字段，不进入效果评测。 |

#### `CandidateIR` 与 `CandidateVersion`

`KNOWLEDGE_COMPLETION` 与 `FREE_EXPLORATION` 的原始输出先被固定 parser 转成同一种 `CandidateIR`。该对象仍是待检查提案；只有经过确定性 gate 并冻结后才成为 `CandidateVersion`。

| `CandidateIR` 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `ir_id` | 唯一 ID | 一次成功解析得到的不可变中间表示；解析失败不创建 ID。 |
| `source_channel` | 枚举 | `KNOWLEDGE` 或 `FREE`；只用于审计与消融，不作为阶段三的优先级特征。 |
| `parent_id` | Harness 版本 ID | 补丁必须应用到的冻结父版本；与实际父版本不一致时 gate 失败。 |
| `normalized_patch` | 规范化编辑列表 | 按文件、符号、AST/配置位置记录增删改及其前后值；不得只保存自然语言说明。 |
| `method_claims` | claim revision ID 列表 | 知识通道显式采用的来源机制与长期声明；自由通道没有来源声明时为空列表，不能伪造映射。 |
| `free_branch` | `FreeBranch` 或 `NOT_APPLICABLE` | 自由通道的原始提案、输入视图、调用与编译结果；知识通道写 `NOT_APPLICABLE`。 |
| `sketch_binding` | 孔位到实现的映射或 `NOT_APPLICABLE` | 对 `hook/location/predicate/adapter/parameter/ordering/fallback` 的实际绑定；自由候选没有草图时写 `NOT_APPLICABLE`。 |
| `diagnostic_call_ids` | 调用 ID 列表 | 该候选依赖的因果诊断、反例修订或 gate 反思调用；用于从补丁回溯语义依据。 |
| `expected_events` | 事件谓词列表 | 候选正确接入并激活时应出现的 trace 事件、字段、方向和观察窗口。 |
| `preserved_checks` | 检查 ID 列表 | 候选必须维持的旧能力、接口、安全、fallback 与数据隔离检查。 |
| `unresolved_conditions` | 未知项列表 | 候选尚未确认的前提、归因或适用范围；每项必须给出取证动作或 `UNOBSERVABLE`。 |
| `llm_call_ids` | 调用 ID 列表 | 直接产生或修订该 IR 的全部 `LLMCallRecord`；不能只保留最后一次调用。 |

`CandidateVersion` 在上述字段之外增加：

| 新增字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `candidate_id` | 唯一 ID | 通过 gate 后冻结的候选版本标识。 |
| `ir_id` | `CandidateIR` ID | 该冻结版本对应的规范化中间表示。 |
| `code_revision` | 不可变代码/配置版本 | 将 `normalized_patch` 应用于 `parent_id` 后得到的精确 revision。 |
| `hard_gate_status` | 检查到状态的映射 | 编译、接口、权限、hook、fallback、数据隔离和修改范围各自取 `PASS/FAIL/UNRESOLVED`；只有全部满足预注册接受规则时才能冻结并进入阶段三。 |
| `revision` | 正整数 | 同一候选谱系上的版本号；任何 LLM 反思或程序修订均递增并产生新 `candidate_id`。 |
| `frozen_at` | 时间戳 | 候选开始评测前的冻结时间；此后不得原地修改。 |

#### `CandidateState`：公式中的 `C_t`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `H_t` | 冻结 Harness 版本 | 第 `t` 轮父版本的代码、配置和依赖快照。 |
| `Z_t` | 故障假设分布 | 对本轮故障假设集合 $\Phi_t$ 中每个原因分配概率或粒子权重并保留证据；总和为 1。 |
| `L_t` | 定位候选集 | 可能需要修改的文件、符号或控制边及定位分数。 |
| `G_t` | 草图集合 | 已检索、编译且仍可满足硬约束的 `MethodSketch`。 |
| `P_t` | 候选补丁集合 | 知识约束候选和自由探索候选的冻结版本。 |
| `C_t^{hard}` | 硬反例集合 | 能证明候选违反接口、安全或逻辑不变量的最小反例。 |
| `C_t^{emp}` | 经验反例集合 | 在指定任务、种子和环境中复现退化或机制失活的最小案例。 |
| `Q_t` | 待解决问题队列 | 未知前提、冲突、观测缺口和下一步取证动作，按决策影响排序。 |

#### 长期证据对象

##### `EvidenceEvent`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `event_id` | 唯一 ID | 原始证据事件标识。 |
| `kind` | 枚举 | `SOURCE_REPORT`、`LOCAL_REPRODUCTION`、`TARGET_RUN`、`STATIC_CHECK`、`HUMAN_REVIEW` 或 `DERIVED`。 |
| `source_pointer` | URI/本地定位 | 指向不可变原始记录；派生事件同时指向全部父事件。 |
| `valid_from` | 时间/版本边界 | 事实开始适用的环境时间或版本。 |
| `valid_to` | 时间/版本边界或 `OPEN` | 事实停止适用的位置；未知结束写 `OPEN`。 |
| `learned_at` | 时间戳 | 系统首次记录该事件的时间。 |
| `task_descriptor` | 结构化对象 | 任务族、实例、输入特征、允许工具和数据 split。 |
| `harness_version` | 版本 ID | 产生证据的精确 Harness。 |
| `model_version` | 版本 ID | 模型、provider 和关键推理配置。 |
| `tool_version` | 版本映射 | 每个工具、容器和外部服务版本。 |
| `candidate_id` | ID 或 `NOT_APPLICABLE` | 与事件关联的候选。 |
| `method_ids` | ID 列表 | 该候选显式使用的方法，不包含仅被检索但未采用的方法。 |
| `trace_slice` | 事件区间 | 支撑判断的最小 trace 片段及完整 trace 指针。 |
| `metric_vector` | 命名数值映射 | 收益、旧能力、严重失败、时延、token 和稳定性等原始指标，不预先合成总分。 |
| `repetitions` | 正整数 | 同条件独立运行次数。 |
| `paired_run_id` | ID 或 `UNPAIRED` | 对应父版本同任务同环境运行；无配对时显式标记。 |
| `reproducibility_status` | 枚举 | `SINGLE_RUN`、`REPEATED`、`INDEPENDENTLY_REPRODUCED` 或 `FAILED_TO_REPRODUCE`。 |

##### `ClaimRevision`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `claim_id` | 稳定 ID | 同一原子主张跨版本不变。 |
| `revision` | 正整数 | 每次语义或 scope 改动递增。 |
| `mechanism` | 有序程序 | 可执行或可检查的机制步骤。 |
| `preconditions` | 谓词集合 | 主张成立前必须满足的条件。 |
| `expected_effect` | 条件化结果分布 | 指标变化方向、幅度分布和时间范围。 |
| `interface_contract` | 契约对象 | 输入、输出、状态、异常、权限和资源要求。 |
| `scope` | 五元组 | 见下方 scope 规范。 |
| `regime_id` | ID | 证据生成机制稳定的一段环境。 |
| `status` | 枚举 | `PROPOSED`、`ACTIVE`、`SUSPECT`、`SUPERSEDED` 或 `RETIRED`。 |
| `minimal_support_sets` | 事件 ID 集合列表 | 每个内层集合单独足以支持该主张；集合元素不可再删除。 |
| `oppose_ids` | 事件 ID 列表 | 反对、限制或击穿该主张的证据。 |
| `effect_posterior` | 分布 | 条件化收益的后验。 |
| `regression_posterior` | 分布 | 旧能力或安全退化的后验。 |
| `derived_from` | claim revision 列表 | 合并、分裂或修订的父主张。 |

`scope=(task_scope, harness_scope, model_scope, tool_scope, evidence_regime)`：`task_scope` 从实例到任务族或领域；`harness_scope` 从单版本到兼容架构族；`model_scope` 从精确版本到模型族；`tool_scope` 是工具及协议版本约束；`evidence_regime` 是数据、评测器和环境稳定区间。scope 扩大必须由新范围内的独立证据触发。

##### `UsageEvent`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `usage_id` | 唯一 ID | 一次方法使用链事件。 |
| `query_id` | ID | 触发检索的 `MethodNeed`。 |
| `claim_id` | ID | 被追踪的原子主张。 |
| `retrieved` | 布尔值 | 是否进入召回集。 |
| `disclosed` | 布尔值 | 是否在某次 `OptimizerLLM` 调用中披露该主张的机制、条件或证据；对应调用由实验级 `LLMCallLedger` 与 `ExposureRecord.disclosed_to_call_ids` 定位。 |
| `adopted` | 布尔值 | 是否进入候选修改。 |
| `activated` | 三值 | `TRUE/FALSE/UNKNOWN`，表示机制是否真实执行。 |
| `affected_result` | 三值 | `POSITIVE/NEGATIVE/UNRESOLVED`，必须来自消融或可归因证据。 |
| `candidate_id` | ID | 使用该主张的候选。 |
| `paired_run_id` | ID 或 `UNPAIRED` | 归因时使用的父子配对。 |

#### 长期状态 `M_t`

| 分量 | 完整名称 | 精确定义 |
| --- | --- | --- |
| `E_t` | Evidence ledger | 追加写的原始证据事件集合。 |
| `C_t` | Claim revisions | 当前及历史原子主张版本；与前文 `CandidateState` 的候选状态同名时必须写成 `M_t.C` 避免歧义。 |
| `J_t` | Relation graph | 主张之间的依赖、替代、冲突、支持和共享证据边。 |
| `U_t` | Usage ledger | 检索到结果影响的使用链。 |
| `R_t` | Regime history | 环境变化点、版本区间和拆分原因。 |
| `Pi_t` | Policy state | 声明写入、关系判定、scope 升降、归档、字段权重、过滤规则、重排器和校准器的版本化配置。 |
| `I_t` | Derived indexes | 可重建的稀疏、向量、图和代码索引；不是权威数据源。 |

### 公式逐项定义

#### 训练集轮次划分

$$
D_{dev}^{(t)}=D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}},
\qquad
D_t^{\mathrm{trace}}\cap D_t^{\mathrm{select}}=
D_t^{\mathrm{trace}}\cap D_t^{\mathrm{anchor}}=
D_t^{\mathrm{select}}\cap D_t^{\mathrm{anchor}}=\varnothing.
$$

$t$ 是 Harness 演化轮次；$D_t^{\mathrm{trace}}$ 产生当前父代的诊断 trace；$D_t^{\mathrm{select}}$ 提供未向当前候选生成器披露的相对收益证据；$D_t^{\mathrm{anchor}}$ 检查旧能力与严重失败是否回归；$D_{dev}^{(t)}$ 是阶段三可调度的两类评测任务之并集。两两不相交只约束同一轮，案例可以在后续轮次更换角色，但必须受 `ExposureRecord` 约束。

#### 候选演化状态

$$
C_t=(H_t,Z_t,L_t,G_t,P_t,C_t^{hard},C_t^{emp},Q_t).
$$

该公式把第 `t` 轮所有决策输入冻结为一个状态。$\Phi_t$ 是从 $D_t^{\mathrm{trace}}$ 的成功/失败对照中提出的有限故障原因集合；`H_t` 是父 Harness；`Z_t` 是定义在 $\Phi_t$ 上的故障假设分布；`L_t` 是代码定位集合；`G_t` 是可用草图；`P_t` 是冻结候选；`C_t^{hard}` 和 `C_t^{emp}` 分别是硬反例与经验反例；`Q_t` 是未解决问题队列。这里左侧 `C_t` 表示完整 CandidateState，右侧带上标的两个 `C` 表示反例集合；实现中分别命名为 `candidate_state`、`hard_counterexamples` 和 `empirical_counterexamples`，避免变量遮蔽。

#### 方法检索分数

$$
s(m)=\sum_f w_f s_f(m)+\lambda C_{condition}(m)+\eta C_{evidence}(m)-\mu U(m).
$$

| 符号 | 定义 |
| --- | --- |
| `m` | 一个 `EvidenceBoundMethod` 候选。 |
| `f` | 检索字段，例如问题签名、能力、接口、代码符号或反例。 |
| `s_f(m)` | 查询与方法在字段 `f` 上的归一化相似度，范围 `[0,1]`。 |
| `w_f` | 字段权重，非负且 `Σ_f w_f=1`；在开发集冻结。 |
| `C_condition(m)` | 已确认前提覆盖率，等于满足的必要前提权重除以全部必要前提权重；存在已知禁止条件时方法先被硬过滤。 |
| `C_evidence(m)` | 证据完整度，综合锚点、代码一致性、配对实验和反例覆盖，范围 `[0,1]`。 |
| `U(m)` | 关键未知项的加权比例，范围 `[0,1]`。 |
| `λ,η,μ` | 非负超参数，分别控制条件、证据和未知惩罚；使用独立检索开发集确定。 |

排序只在硬过滤后的候选中执行；同分时依次选择未知更少、依赖闭包更小、迁移成本更低的方法。

`SEMANTIC_BUNDLE_RERANK` 只对已经完成硬过滤与依赖闭包的方法束给出序位。程序分数和经核验的语义序位通过倒数秩融合：

$$
S_{final}(B)=\alpha\frac{1}{k+r_{prog}(B)}+
(1-\alpha)\frac{1}{k+r_{sem}(B)}.
$$

`B` 是一个依赖闭合的方法束；$r_{prog}(B)\in\{1,2,\ldots\}$ 是按程序检索分数得到的名次；$r_{sem}(B)$ 是 `OptimizerLLM` 提议且经机制锚点、迁移缺口和反驳测试字段核验后的语义名次；$k>0$ 是防止头部名次占比过大的平滑常数；$\alpha\in[0,1]$ 是程序排序权重，二者均在独立检索开发任务上冻结。语义提案解析或核验失败时令 $\alpha=1$；无论 $S_{final}$ 多高，都不能恢复硬过滤项、删除依赖或解除冲突。

#### 定位分数

$$
\operatorname{loc}(\ell)=w_1\,\text{slice-overlap}+w_2\,\text{failed/success contrast}+w_3\,\text{dependency proximity}+w_4\,\text{historical repair success}.
$$

`ℓ` 是代码位置；四个特征均缩放到 `[0,1]`。`slice-overlap` 是位置覆盖最小失败切片的比例；`failed/success contrast` 衡量该位置在失败 trace 中相对成功 trace 的差异；`dependency proximity` 是到故障事件的数据流/控制流距离的反向归一化；`historical repair success` 是相同位置族历史修复的带时间衰减成功率。`w_1...w_4≥0` 且和为 1。缺失特征不置零，而是在剩余已观测特征上重新归一化权重并标记不确定性。

#### 粒子权重更新

$$
w_l'\propto w_l P(e\mid \omega_l,a).
$$

`ω_l` 是第 `l` 个故障/方法作用域联合假设；`w_l` 是动作前权重；`a` 是已执行的演化或测评动作；`e` 是新证据；`P(e|ω_l,a)` 是由重复运行频率、冻结错误模型或预注册区间产生的观测似然；`w_l'` 是归一化后的新权重，满足 `Σ_l w_l'=1`。`EVIDENCE_INTERPRETATION` 和 `COUNTEREXAMPLE_ATTRIBUTION` 只决定证据可能对应哪些假设及哪些字段仍未知，`OptimizerLLM` 输出的概率、分数或措辞强度不得直接代入似然。若所有似然为零，触发 `unknown_model` 扩展，禁止直接均匀化掩盖模型失配。

#### Bayes 风险与证据价值

$$
\mathcal R(b)=\min_{d\in\{promote,reject,return,continue\}}\mathbb E_b[L(d,\theta)].
$$

`b` 是当前联合信念；`d` 是终止或续行动作；`θ` 是真实但未知的候选质量、退化、机制激活和适用范围；`L(d,θ)` 是采取 `d` 后的损失。`return` 表示返回候选生成或检索阶段。损失矩阵必须在实验前固定，严重退化损失高于多跑一次评测的成本。

$$
\operatorname{EVI}(a)=\mathcal R(b)-\mathbb E_{o\sim p(o\mid b,a)}\mathcal R(\operatorname{update}(b,a,o)).
$$

`a` 是待选取证动作；它可以来自程序枚举，也可以来自经 `COMPILE_VALID_ACTION_PROPOSALS` 核验的 `NEXT_ACTION_PROPOSAL`。`o` 是可能观测；`p(o|b,a)` 是预测观测分布；`update` 是执行 Bayes 或粒子更新后的信念；`EVI(a)` 是信息带来的期望风险下降。实际调度使用 `EVI(a)-cost(a)-risk(a)`，仅当其为正或硬门要求取证时执行；`OptimizerLLM` 提议动作的自然语言理由不进入该数值。

#### 保留探索概率的任务分布

$$
q_t(x)=(1-\varepsilon)\operatorname{softmax}(VOI_t(x)/\tau)+\varepsilon p_{target}(x),\qquad \varepsilon>0.
$$

`x` 是 $D_t^{\mathrm{select}}$ 中尚可调度的候选判定任务；`VOI_t(x)` 是在第 `t` 轮运行任务 `x` 对当前候选决策的预期价值；`τ>0` 是 softmax 温度；`p_target(x)` 是由冻结任务分层在本轮判定池上重新归一化的目标分布；`ε∈(0,1]` 是最低覆盖比例；`q_t` 是下一项收益判定任务的采样分布。anchor 与测试任务都不得出现在该收益分布或 `VOI` 估计中。

#### 长期记忆状态

$$
M_t=(E_t,C_t,J_t,U_t,R_t,\Pi_t,I_t).
$$

`M_t` 是第 `t` 次沉淀后的完整长期状态；`E_t` 是原始证据账本；`C_t` 是 ClaimRevision 集合，此处不再表示 CandidateState；`J_t` 是主张关系图；`U_t` 是使用账本；`R_t` 是 regime 历史；`Π_t` 是写入、关系、scope、归档与检索策略的联合版本化状态；`I_t` 是派生索引。实现中必须使用命名字段访问，禁止仅凭位置解包，以避免两个 `C_t` 的含义混淆。

#### 方法贡献消融

$$
d_m=\operatorname{metric}(H_{full})-\operatorname{metric}(H_{mask(m)}).
$$

`m` 是一个方法或机制；`H_full` 是完整候选；`H_mask(m)` 只屏蔽 `m` 且保持其余代码、配置、种子和任务一致；`metric` 是预先指定的单项指标；`d_m` 是方法边际贡献。多指标分别计算，不先合成。若屏蔽破坏接口，应使用等接口 no-op 或补偿适配器；无法构造有效 mask 时贡献为 `UNIDENTIFIED`。

### 阶段与轮次接口

| 阶段 | 必需输入 | 必需输出 | 不允许的隐式行为 |
| --- | --- | --- | --- |
| 训练集外层调度 | benchmark 训练集、当前父 Harness、当前长期状态、案例暴露历史 | 故障发现批次、候选判定面板、旧能力回放集合、下一轮状态或冻结决定 | 不得让当前候选读取判定面板的 trace 或标签；不得把已用于生成该候选的案例重新计作独立验证。 |
| loop 外离线组织 | `SourcePacket[]`、组织协议 | `SOURCE_CLAIM_EXTRACTION` 调用记录、经核验声明与冻结 `MethodCatalogSnapshot` | `OptimizerLLM` 只能从固定来源提出带锚点声明；不得把无锚点解释写入目录，不得在同一次 benchmark 演化中途加入来源或重建目录。 |
| 阶段一在线检索 | 冻结方法目录、当前 trace、`M_t` 的诊断证据视图 | `TRACE_TO_METHOD_NEED/SEMANTIC_BUNDLE_RERANK` 调用记录、`MethodNeed`、方法束、依赖闭包、冲突包和未决假设 | 语义重排不能恢复硬过滤项或删除依赖；不得把论文结果写成目标 Harness 效果。 |
| 阶段二候选综合 | 冻结 `H_t`、$D_t^{\mathrm{trace}}$ 的 `ExecutionTrace[]`、$\Phi_t/Z_t$、方法束、反例 | 诊断、修订、双通道与 gate 反思调用记录，冻结候选 $P_t$、草图绑定和 gate 结果 | 不得读取 $D_t^{\mathrm{select}}$；不得让 `OptimizerLLM` 原始输出绕过解析与共同硬约束；不得修改父版本。 |
| 阶段三规划测评 | `H_t`、$P_t$、信念、$D_{dev}^{(t)}$、案例暴露记录 | 证据解释、归因、动作与分支反思调用记录，决策、完整 ledger、新反例或返回请求 | `OptimizerLLM` 不拥有最终决定权；披露后用于修订的 select case 失去独立性；不得用测试集调度或用未激活机制归因效果。 |
| 阶段四在线积累 | 本轮全部评测与使用 ledger、旧 $M_t$ | claim、regime、关系、scope、复用经验与检索反思调用记录，新 `M_{t+1}` 和可查询索引 | 所有语义输出只是提案；不导入新论文、不覆盖原始事件、不因单次成功扩大 scope，不用当前 select 结果同轮追调检索器。 |
| stop 后正式测评 | 冻结 Harness、冻结模型/工具/评测协议、$D_{\mathrm{test}}$ | 与 baseline 可比的最终指标和只读审计 trace | 不运行 `OptimizerHarness`，不调用 `OptimizerLLM`；不更新 Harness、目录、检索策略或长期记忆。 |

### 辅助对象、枚举与边界语义

| 对象 | 完整定义 |
| --- | --- |
| `CandidateIR` / `CandidateVersion` | 字段与冻结边界见前文专表；两条生成通道必须先进入同一 IR，gate 通过后只允许创建新的不可变 version，禁止原地修补。 |
| `ActivationProbe` | `{probe_id,trigger,expected_event,observation_window,repetitions,pass_rule,missing_rule}`。 |
| `MetamorphicPair` | `{source_input,transform,expected_relation,paired_seeds,applicability}`；transform 不得改变目标语义。 |
| `PairedRun` | `{pair_id,parent_id,child_id,task,seed,environment,evaluator,parent_metrics,child_metrics}`。 |
| `TrainProtocol` | `{benchmark_revision,split_revision,task_strata,role_assignment_rule,reuse_policy,execution_config,optimizer_harness_revision,optimizer_llm_config,evaluator_revision,seeds,promotion_rule,stop_rule}`；在实验前冻结，约束训练角色分配、长期证据复用边界、两类模型与工具环境、晋级和 stop。 |
| `ExposureRecord` | `{task_id,round_id,split_role,disclosed_fields,disclosed_to_call_ids,affected_candidate_ids,independence_status,harness_versions,evidence_ids}`；记录案例何时以何种角色、通过哪些调用影响候选或决策。 |
| `DevPanel` | `{task_strata,weights,seeds,protocol_revision,selection_rule}`；由 $D_t^{\mathrm{select}}$ 与 $D_t^{\mathrm{anchor}}$ 构造，不含封存测试集和当前轮 $D_t^{\mathrm{trace}}$。正文中的 $D_{dev}^{(t)}$ 指第 $t$ 轮允许阶段三使用的完整任务池。 |
| `EvaluationLedger` | 追加写 `EvidenceEvent[]`，同时保存候选集、动作 propensity、失败运行和评测版本。 |
| `UsageLedger` | 追加写 `UsageEvent[]`，严格区分 `retrieved → disclosed → adopted → activated → affected-result`。 |
| `CrossTaskEvidenceView` | `{as_of,scope_ceiling,regime_filter,event_ids,claim_revisions,index_revision}`；仅为可重建投影。 |
| `FreeBranch` | `{generator_revision,llm_call_id,input_context,raw_proposal,normalized_patch,compiled_claims}`；`llm_call_id` 指向对应 `FREE_EXPLORATION` 调用，自由候选不绕过共同 gate。 |
| counterexample | `{violated_claim,precondition,minimal_input,transform,seeds,minimal_trace_slice,reproducibility}`；缺一项为 `contested`，不能收紧 scope。 |

gate 状态只取 `FAIL/PASS/UNRESOLVED`；候选决策只取 `Promote/Reject/Continue/Tie/Rollback/Stop`。关系只取 `REQUIRES/CONFLICTS/ALTERNATIVE_TO/REFINES/SUPPORTED_BY/REFUTED_BY`。事务动作 `duplicate/supersede/refine/split-condition/coexist-by-regime/merge-support` 必须保留原 claim revision。consolidation 状态中，`pending-review` 表示关系或策略判断仍需复核，`failed_consolidation` 表示派生快照未通过策略不变量或锚点重放；两者都只提交新原始事件，不提交 shadow 中的派生结构。`paper_only/code_only` 是来源对齐状态；`inert` 表示接入成功但机制未激活；`adapter_error/adapter_ok` 只判断适配器，不等价于任务效果。

### 公式参数与边界的完整定义

检索式中

$$
s_f(m)=\frac{\sum_{j\in f}a_j\,sim_j(q_j,m_j)}{\sum_{j:m_j,q_j\ observed}a_j},
$$

$sim_j\in[0,1]$ 由字段类型固定：谓词用满足率，集合用加权 Jaccard，代码符号用精确/规范化匹配，向量用截断余弦。$C_{condition}$ 是已确认必要前提的权重比例；存在任一 `FALSE` 前提或已知 forbidden condition 时先硬过滤。$C_{evidence}$ 是锚点、代码一致性、配对复现和反例覆盖的冻结加权和；$U$ 是决策关键 `UNKNOWN` 的权重比例。$w_f\ge0,\sum_fw_f=1$，$\lambda,\eta,\mu\ge0$；同分依次选择未知更少、依赖闭包更小、适配成本更低和 ID 更小者。

定位式中四个特征的权重 $w_{1:4}\ge0$ 且和为 1；缺失特征集合为 $M$ 时只在观测集合上按 $w_i/\sum_{j\notin M}w_j$ 重归一化。`dependency proximity` 使用 $1/(1+d)$，$d$ 是最短数据/控制依赖边数；无路径时该特征为 `UNKNOWN`，不是 0。

粒子更新的完整式为

$$
\tilde w_l=w_lP(e\mid\omega_l,a),\qquad
w_l'=\frac{\tilde w_l}{\sum_j\tilde w_j},\qquad
ESS=\frac{1}{\sum_l(w_l')^2}.
$$

$\omega_l$ 是故障、迁移、接入、激活与 scope 的联合粒子；$a$ 是已执行动作，$e$ 是版本化证据，似然只来自当前 observation-model revision。若归一化常数为 0，新增 `unknown_model` 粒子并重新计算；$ESS<\tau_{ESS}L$ 时按预注册核重采样，$L$ 为粒子数，$\tau_{ESS}\in(0,1)$。

Bayes 风险中的 $\theta$ 是真实候选质量、硬退化、激活和 scope；决策集 `{promote,reject,return,continue}` 的损失矩阵 $L(d,\theta)$ 在开发实验前冻结。`return` 分别返回检索、候选综合或反例构造，由缺失状态决定。EVI 的预测分布 $p(o\mid b,a)$ 必须含失败与 unknown 结果；实际选择量为

$$
NV(a)=EVI(a)-\lambda_c C(a)-\lambda_rR(a),
$$

$C,R\in[0,1]$，$\lambda_c,\lambda_r\ge0$。硬 gate 失败动作不进入 argmax；并列依次取风险低、可逆、成本低和 ID 小者。

任务分布中

$$
\operatorname{softmax}(VOI_t(x)/\tau)=
\frac{\exp(VOI_t(x)/\tau)}{\sum_{x'\in D_t^{\mathrm{select}}}\exp(VOI_t(x')/\tau)}.
$$

$x$ 和求和中的 $x'$ 都只属于本轮冻结的 $D_t^{\mathrm{select}}$；$\tau>0$；$\varepsilon\in(0,1]$；$p_{target}$ 是由 `TrainProtocol.task_strata` 在该集合上诱导并重新归一化的目标分布，因此任一 $p_{target}(x)>0$ 的任务至少有 $\varepsilon p_{target}(x)$ 的抽样概率。$VOI_t$ 不得由 anchor 或测试结果估计；anchor 的运行次序由回归风险单独决定。

消融式中的 `metric` 必须指定方向、范围、聚合和评测 revision；$H_{mask(m)}$ 与 $H_{full}$ 除 method $m$ 外完全配对。接口 no-op 仍改变机制时，$d_m$ 标为 `UNIDENTIFIED`。多个交互方法的单项 $d_m$ 不可相加；交互另建 bundle claim。

### 伪代码算子契约

| 算子组 | 输入 → 输出；失败与未知处理 |
| --- | --- |
| `OFFLINE_ORGANIZE` / `FREEZE_METHOD_CATALOG` | 固定来源与组织协议 → 经 LLM 提议、锚点核验、建图和索引的不可变 `MethodCatalogSnapshot`；只在 loop 外执行。 |
| `ALIGN_AND_SEGMENT` | 来源 → 与论文段落、代码符号、配置和测试绑定的最小来源单元；无法对齐标记 `paper_only/code_only`。 |
| `BUILD_SOURCE_CLAIM_REQUESTS` / `PARSE_SOURCE_CLAIM_PROPOSALS` | 来源单元 → `SOURCE_CLAIM_EXTRACTION` 最小视图 → `OptimizerProposal[]`；缺必填锚点时解析失败。 |
| `ANCHOR_SCHEMA_AND_RELATION_CHECK` | 声明提案、固定来源单元 → 经锚点、schema、revision 和关系规则核验的 claims；未确认字段为 `UNKNOWN/unverified_relation`。 |
| `BUILD_EVIDENCE_GRAPH_AND_INDEXES` | 经核验 claims → 关系图与可重建字段索引。 |
| `BUILD_METHOD_NEED` | 父 Harness、当前 trace、诊断证据视图和旧反例 → 经 `TRACE_TO_METHOD_NEED` 提议并核验的 `MethodNeed`；故障假设只从其 `competing_hypotheses` 字段读取。 |
| `BUILD_TRACE_NEED_VIEW` / `PARSE_METHOD_NEED_PROPOSAL` | 当前允许披露的 trace、代码和历史证据 → 最小诊断视图 → 竞争假设、需求与查询计划。 |
| `TRACE_ANCHOR_AND_CONSTRAINT_CHECK` | need 提案、诊断视图 → 逐项引用真实事件且满足权限的需求；无支持项保留为 hypothesis。 |
| `ONLINE_RETRIEVE` / `MERGE_RETRIEVAL_VIEWS` | 固定目录、`CrossTaskEvidenceView`、need、trace view → 合并只读检索视图 → 经语义重排的 bundles 与未决假设。 |
| `DECOMPOSE_NEED` / `FIELD_AWARE_HYBRID_RETRIEVE` | need → 字段子查询 → 高召回 seeds。 |
| `HARD_CONDITION_FILTER` | seeds、前提/禁止条件 → eligible/unknown/rejected；语义调用不能恢复 rejected。 |
| `DEPENDENCY_CLOSURE_AND_CONFLICT_PACK` | 图、seeds → 含完整硬依赖与冲突包的 bundles。 |
| `BUILD_SEMANTIC_BUNDLE_RERANK_REQUEST` / `PARSE_BUNDLE_RERANK_PROPOSAL` | bundles、need、trace view → `SEMANTIC_BUNDLE_RERANK` 最小视图 → 机制匹配、迁移缺口、反驳测试和排序提案。 |
| `FUSE_PROGRAM_SCORE_AND_VERIFIED_SEMANTIC_RANK` | 程序分数、经锚点核验的语义排序 → 最终 bundles；不得改变硬过滤和依赖闭包。 |
| `UNRESOLVED_ASSUMPTIONS` | bundles、need → 可执行取证问题；不可观测项显式标记。 |
| `SYNTHESIZE` | Harness、`ExecutionTrace[]`、假设、bundles、旧反例、作用域合格的历史补丁与本轮硬约束 → 经诊断、双通道生成、gate 与受控反思的冻结候选。 |
| `SELECT_DIAGNOSTIC_CASE` / `MATCHED_SUCCESS_TRACES` | 本轮 trace 与故障假设 → 一个待最小化失败案例及同任务族、环境和可比阶段的成功对照；没有可比项时返回 `UNKNOWN`。 |
| `MANIPULABLE_ATOMS` / `STOCHASTIC_DDMIN` | Harness、失败案例 → 可操纵原子 → 随机感知 1-minimal 切片。 |
| `LOCALIZE` | 最小切片、成功/失败 trace、Harness → 代码位置及结构证据。 |
| `BUILD_TRACE_CAUSAL_DIAGNOSIS_REQUEST` / `PARSE_CAUSAL_DIAGNOSES` | 最小切片、成功对照、位置与旧假设 → `TRACE_CAUSAL_DIAGNOSIS` 视图 → 竞争因果链。 |
| `VERIFY_CAUSAL_TRACE_ANCHORS_AND_DEPENDENCIES` | 因果链、trace、Harness → 事件、时间与依赖均可核验的诊断；失败链不进入 hypotheses。 |
| `BUILD_COUNTEREXAMPLE_REVISION_REQUEST` / `PARSE_COUNTEREXAMPLE_REVISIONS` | 已确认反例、诊断和父 Harness → `COUNTEREXAMPLE_GUIDED_REVISION` 视图 → 修订意图。 |
| `VERIFY_ALLOWED_REVISION_INTENTS` | 修订意图、反例 → 收紧、重绑、替换、相邻检索或自由分支中的合法最小动作。 |
| `ANTI_UNIFY_EDITS` / `COMPILE_TYPED_SKETCHES` | 历史补丁、方法代码、诊断和修订意图 → 公共结构 → 有类型草图。 |
| `BUILD_KNOWLEDGE_LLM_REQUESTS` | 父 Harness、草图、位置、最小切片、诊断、硬约束 → 每个草图的最小 `KNOWLEDGE_COMPLETION` 视图。 |
| `BUILD_FREE_LLM_REQUEST` | 父 Harness、位置、最小切片、诊断、硬约束 → `FREE_EXPLORATION` 视图；不披露本轮方法束、知识候选或其补丁。 |
| `CALL_OPTIMIZER_LLM` | 输入视图、call type、冻结 `OptimizerLLMConfig` → 原始输出与 `LLMCallRecord`；越权检查失败时不调用，重试另建 call ID。 |
| `PARSE_KNOWLEDGE_COMPLETIONS` / `PARSE_FREE_PROPOSALS` | `OptimizerLLM` 原始输出、固定 parser → Candidate IR 或解析失败；不得补写模型未输出语义。 |
| `NORMALIZE_TO_COMMON_IR` / `DEDUP_BY_BEHAVIOR_AND_PATCH` | 两类候选 → 共同 IR → 同父版本 canonical 候选。 |
| `DETERMINISTIC_FILTER` | Candidate IR → accepted/rejected 与逐项 gate 报告；权限和数据隔离失败不可修订。 |
| `ELIGIBLE_SEMANTIC_GATE_FAILURES` | rejected → 仅保留可能由局部语义绑定或实现修正的拒绝项。 |
| `BUILD_GATE_FAILURE_REFLECTION_REQUEST` / `PARSE_MINIMAL_GATE_REVISIONS` | 合格拒绝报告、原草图和硬约束 → `GATE_FAILURE_REFLECTION` 视图 → 一次最小修订提案。 |
| `APPLY_VERIFIED_MINIMAL_REVISIONS` / `FREEZE_NEW_VERSIONS` | 合法修订 → 新 Candidate IR → 重新完整 gate → 不可变 child revisions。 |
| `PLAN_AND_TEST` | 父版本、候选、假设、dev pool 与边界内规划先验 → 语义解释辅助但由规则决定的决策、ledger 与 belief。 |
| `EXTRACT_METHOD_SCOPES` / `RETRIEVE_PLANNING_PRIORS` | 冻结候选，或长期状态、候选、假设与复用边界 → 候选声明的适用 scope，或只含边界内历史证据的规划先验；缺失证据保留未知质量，不由 `OptimizerLLM` 补概率。 |
| `INIT_PARTICLES` | 假设、scope、先验证据 → 含 `unknown_model` 的归一化粒子。 |
| `RUN_NEXT_GATE` | 候选、gate 顺序 → contract/activation/bypass/MR 的下一真实事件。 |
| `BUILD_EVIDENCE_INTERPRETATION_REQUEST` / `PARSE_EVIDENCE_INTERPRETATION` | 新事件、候选和 belief → `EVIDENCE_INTERPRETATION` 视图 → 支持、反对、未知和替代解释。 |
| `VERIFY_INTERPRETATION_ANCHORS` / `UPDATE_WITH_OBSERVATION_MODEL` | 解释、事件 → 锚点合法的语义 observation → 使用校准似然而非 LLM 置信度更新 posterior。 |
| `MINIMIZE_AND_CONFIRM` / `CONFIRMED_COUNTEREXAMPLE` | 违规事件 → 最小反例；重复不足为 `contested`。 |
| `BUILD_COUNTEREXAMPLE_ATTRIBUTION_REQUEST` / `PARSE_COUNTEREXAMPLE_ATTRIBUTION` | 候选、反例、解释和 belief → `COUNTEREXAMPLE_ATTRIBUTION` 视图 → 竞争归因。 |
| `VERIFY_ATTRIBUTION_EVIDENCE` / `RETURN_TO_CANDIDATE_SYNTHESIS` | 归因、反例和事件 → 经证据核验的返回请求；未决归因保留多个分支。 |
| `ANYTIME_DECISION` | 候选、belief、ledger → promote/reject/tie/continue；只使用冻结规则和统计证据。 |
| `ENUMERATE_EVOLVE_AND_EVALUATE_ACTIONS` | belief → mutate、refine、probe、评测和回退的程序动作。 |
| `BUILD_NEXT_ACTION_PROPOSAL_REQUEST` / `PARSE_NEXT_ACTION_PROPOSALS` | belief、ledger、程序动作和 dev pool → `NEXT_ACTION_PROPOSAL` 视图 → 动作排序或新 probe。 |
| `COMPILE_VALID_ACTION_PROPOSALS` | 动作提案、belief、dev pool → 权限、数据角色、参数和停止条件完整的合法动作。 |
| `KEEP_ACTIONS_THAT_CAN_CHANGE_DECISION_OR_FORM_CEX` | 动作 → 会改变终局或形成反例者。 |
| `BUILD_SEARCH_BRANCH_REFLECTION_REQUEST` / `PARSE_SEARCH_BRANCH_REFLECTION` | 停滞状态、候选、belief 和 ledger → `SEARCH_BRANCH_REFLECTION` 视图 → 遗漏假设、检索需求或自由分支。 |
| `VERIFY_AND_COMPILE_BRANCH_RETURN` | 分支反思 → 返回阶段一/二的合法请求或无效；不能直接 stop。 |
| `FULL_DEV_PANEL` | 未决候选、`DevPanel` → 完整开发评测动作。 |
| `SAMPLED_POSTERIOR_ROLLOUT` / `EXECUTE_FIRST_ACTION` | 动作、深度、posterior → 计划 → 只执行首个真实动作。 |
| `CONSOLIDATE` | 长期状态、评测/使用账本 → LLM 知识提案经核验后的新状态，或只追加原始事件的 pending 状态。 |
| `NORMALIZE_EVENTS` / `APPEND_ONLY` / `COPY_ON_WRITE` | 原始 ledger → 规范事件 → 新证据账本 → 隔离 shadow。 |
| `BUILD_EVIDENCE_TO_CLAIM_REQUEST` / `PARSE_ATOMIC_CLAIM_PROPOSALS` | 新事件 → `EVIDENCE_TO_CLAIM` 视图 → 最小 claim proposals。 |
| `VERIFY_CLAIM_EVENT_ANCHORS_AND_IDENTIFIABILITY` | claim proposals、新事件 → 来源、数据角色和因果可识别性合格的 proposals。 |
| `BUILD_REGIME_DISCOVERY_REQUEST` / `PARSE_REGIME_PROPOSALS` | 新 claims、事件和 regime 历史 → `REGIME_DISCOVERY` 视图 → 条件分界与留出计划。 |
| `VALIDATE_REGIME_PREDICATES_AND_HOLDOUTS` / `APPLY_VERIFIED_REGIME_REVISIONS` | regime 提案 → 可观测且留出验证通过的 revisions；失败保留为未决假设。 |
| `FIND_BY_NORMALIZED_KEY_AND_OVERLAPPING_SCOPE` | claim、memory → 相同机制且 scope 重叠的候选。 |
| `BUILD_CLAIM_RELATION_REQUEST` / `PARSE_RELATION_PROPOSAL` | 新旧 claims 最小视图 → `CLAIM_RELATION_PROPOSAL` → `RelationProposal`。 |
| `RULE_CHECK` / `SELECT_TRANSACTIONAL_ACTION` / `APPLY` | 关系提案 → 经来源、条件、scope、regime 和时间核验的唯一 copy-on-write 动作。 |
| `PROPAGATE_WITHDRAWALS_TO_FIXED_POINT` | 关系图 → 依赖撤回闭包；循环边按 SCC 原子处理。 |
| `UPDATE_USAGE_STAGES` / `ACTIVATED_METHODS` | usage ledger → 阶段状态与已激活方法；未激活不归因效果。 |
| `HAS_MATCHED_MASK_ABLATION` / `PAIRED_DIFFERENCES` | 方法使用链 → 可识别性 bool 与配对差。 |
| `UPDATE_EFFECT_POSTERIOR` / `UPDATE_OBSERVATIONAL_ASSOCIATION_ONLY` | 可识别差值或非识别观察 → 效果 posterior 或仅相关记录。 |
| `CREATE_BUNDLE_CLAIMS_FOR_DETECTED_INTERACTIONS` | 交互证据 → bundle claims；不把交互信用强分给单方法。 |
| `BUILD_SCOPE_SEPARATOR_REQUEST` / `PARSE_SCOPE_SEPARATOR_PROPOSAL` | claim、成功/失败证据 → `SCOPE_SEPARATOR_PROPOSAL` 视图 → 最小可检查谓词候选。 |
| `VALIDATE_CHECKABLE_SEPARATOR` / `VALIDATE_SEPARATOR` | 分界提案 → 字段可观测、无未来信息且在留出 case 有效的谓词，或无效。 |
| `SPLIT_SCOPE` / `DEMOTE_TO_LARGEST_SUPPORTED_SUBSCOPE` | claim、合法谓词或反例 → `scope∧g/scope∧¬g` 或最大受支持子 scope。 |
| `IMMEDIATE_PARENT` / `PROMOTION_EVIDENCE_PASSES` / `STABILITY_PLASTICITY_PROBES_PASS` | 当前 scope → 上一级 → 证据门与稳定—可塑性门。 |
| `PROMOTE_ONE_LEVEL` | claim、相邻父 scope → 单边 scope 扩张 revision；禁止跨级。 |
| `BUILD_REUSABLE_LESSON_REQUEST` / `PARSE_REUSABLE_LESSONS` | 已通过证据门的 claims、usage 和事件 → `REUSABLE_LESSON_SYNTHESIS` 视图 → 可检索经验提案。 |
| `ATTACH_VERIFIED_LESSONS_TO_CLAIMS` | 经验提案、shadow → 每个字段均链接已提交 claim/证据的派生检索文档。 |
| `RETRIEVAL_USAGE_FAILURE_CHAINS` | usage ledger → retrieved/disclosed/adopted/activated/affected-result 中断链。 |
| `BUILD_RETRIEVAL_FAILURE_REFLECTION_REQUEST` / `PARSE_RETRIEVAL_POLICY_PROPOSALS` | 中断链、当前策略 → `RETRIEVAL_FAILURE_REFLECTION` 视图 → 查询、权重或重排修订提案。 |
| `QUEUE_POLICY_REVISIONS_FOR_OFFLINE_REPLAY` | 策略提案 → 待离线回放队列；当前轮不得直接启用。 |
| `POLICY_INVARIANTS_HOLD` / `REPLAY_NEW_AND_OLD_ANCHORS` | shadow → 策略检查与新旧锚点重放。 |
| `ATOMIC_COMMIT` | 合格 shadow → 新 $M_{t+1}$；失败只保留已追加原始证据。 |
| `RETRIEVE_DIAGNOSTIC_CONTEXT` / `RETRIEVE_VIEW` | 已提交长期状态与当前 trace 或 query → 受时间、scope、regime 和权限约束的只读证据视图。 |
| `EVOLVE_ON_BENCHMARK_TRAIN` | 初始 Harness、长期状态、冻结目录、训练集和 `TrainProtocol` → stop 后冻结的实验状态。 |
| `INIT_TRAIN_SCHEDULER` / `ASSIGN_TRAIN_ROLES` | 训练集、协议、暴露历史、当前状态 → 三个两两不相交的本轮任务集合；不得借用测试集。 |
| `RESOLVE_REUSE_BOUNDARY` | 冻结 `TrainProtocol.reuse_policy`、轮次 → 当前 `as_of` 与最大 `allowed_scope`；不读取本轮结果调整边界。 |
| `RUN_HARNESS` | 冻结 Harness、故障发现批次、执行协议 → 执行 agent 产生的 `ExecutionTrace[]`。 |
| `RETRIEVE_PATCH_HISTORY` | 长期状态、need、`as_of`、`allowed_scope` → 时间、scope、regime 与宿主兼容的历史补丁；原始 patch 保持版本定位。 |
| `COMPILE_ROUND_HARD_CONSTRAINTS` | 父 Harness、冻结协议、need、bundles → 权限、数据隔离、接口、机制保持、能力保留和修改范围的本轮不可绕过谓词集合。 |
| `REVISE_METHOD_NEED_WITH_COUNTEREXAMPLE` | 当前 need、trace、反例与诊断视图 → 通过 `TRACE_TO_METHOD_NEED` 形成且经锚点核验的新 revision。 |
| `TRACE_VIEW` | trace batch → 只含允许向当前 call type 披露字段的不可变视图。 |
| `LEDGER_FROM_TRACE_BATCH` | 父代 trace batch → 本轮评测账本初值；不得只保留失败运行。 |
| `RECORD_RETRIEVAL` / `RECORD_CANDIDATE_USAGE` | 检索结果或冻结候选 → 追加 `retrieved/disclosed/adopted` 使用事件。 |
| `INIT_LLM_CALL_LEDGER` / `UPDATE_EXPOSURE_FROM_LLM_CALLS` | 冻结协议 → 追加写调用账本；调用账本、候选谱系与当前 select pool → 更新实际披露字段、受影响候选谱系和案例独立性。 |
| `REFRESH_INDEPENDENT_SELECT_POOL` | 暴露历史、受影响候选、旧 select pool → 删除已影响修订的案例并补入未披露训练案例。 |
| `COMPLETE_USAGE_LEDGER` | 使用账本与完整评测账本 → 补齐 `activated/affected_result`；未披露、未采用和未激活分别记账。 |
| `ACCEPT_IF_PROMOTED` | 父代、冻结候选、决定 → `Promote` 时返回获胜候选，否则返回同一父代。 |
| `UPDATE_TRAIN_SCHEDULER` | 三类任务、决定、ledger → 新覆盖、暴露、未决故障和 anchor 状态。 |
| `TRAIN_SPLIT_FIXED_POINT` | 调度状态、新旧 Harness、新旧长期状态和 belief → 是否满足全部 stop 条件；缺失、pending 或未经反思的停滞一律为 `FALSE`。 |
| `FREEZE_FOR_FINAL_TEST` | 最终 Harness、长期状态、目录和训练协议 → 不再可写的测试包。 |
局部变量 `units/extraction_requests/extraction_calls/claim_proposals/claims/graph/field_indexes/catalog_snapshot` 依次表示来源单元、来源抽取请求及调用、未经核验的声明提案、经核验原子主张、关系图、字段索引和冻结目录。`diagnostic_view/need_call/need_proposal/need` 是需求形成所用最小证据视图、调用、原始提案和经核验 `MethodNeed`；`queries/indexes/seeds/bundles/rerank_request/rerank_call/rerank_proposal/unresolved` 是字段查询、联合索引、初召回、闭包方法束、语义重排请求及调用、排序提案和未决假设。

`trace_batch/failing_case/target_failure_signature/successful_traces/atoms/slice/locations` 是故障发现 trace、诊断案例、从该案例读取的失败谓词、成功对照、可操纵原子、最小切片和代码位置。`diagnosis_request/diagnosis_call/diagnosis_proposals/diagnoses` 是因果诊断请求、调用、原始因果链和经事件/依赖核验的诊断；`revision_request/revision_call/revision_intents` 是反例修订请求、调用和合法修订意图，没有旧反例时 `revision_intents` 为空集合。`historical_patches/hard_constraints` 是从复用边界内长期状态取回的兼容历史补丁，以及由父 Harness、冻结协议、need 和方法束共同编译出的本轮硬约束。`hierarchy/sketches/knowledge_candidates/free_candidates/accepted/rejected/semantic_rejections/revisions` 是编辑抽象、草图、两通道候选、gate 两类结果、允许反思的拒绝项和最小修订。

`method_scopes/prior_evidence/belief/interpretation/attribution/actions/action_proposals/reflection/return_request/plan/result` 分别是候选声明的适用范围、复用边界内且带证据质量的历史规划先验、当前 posterior、经核验证据解释、反例归因、合法动作集、LLM 动作提案、停滞反思、返回前序阶段的请求、短 rollout 计划和真实首动作结果。所有 `*_request/*_call/*_proposal` 分别表示 `OptimizerHarness` 构造的最小输入视图、一次 `LLMCallRecord` 和尚未成为事实的结构化提案。

`E1/proposals/shadow/verified_regimes/matches/relation/action` 是新证据账本、经事件锚点核验的 claims、写时复制状态、留出验证通过的 regime、候选匹配、规则核验关系和事务动作。`separator_proposal/g/lesson_proposals/failures/policy_proposals` 是 scope 分界提案、有效谓词、复用经验提案、检索使用中断链和待离线回放的策略提案。`scheduler/llm_call_ledger/trace_pool/select_pool/anchor_pool/train_protocol` 是训练调度状态、实验级 LLM 调用账本、三类任务池和冻结协议；`as_of/allowed_scope` 是该轮由 `reuse_policy` 固定的知识时间边界与最大复用范围；`diagnostic_evidence_view/evidence_view/confirmed_counterexamples` 是需求形成视图、按需跨任务视图和已确认反例；`round_eval_ledger/new_eval_ledger/round_usage_ledger/usage_ledger/decision/cex/H_next/M_next` 是本轮账本、增量账本、使用账本、终局决定、确认反例、下一父代和下一长期状态。

兼容名称固定如下：`RefineAdapter` 修改适配绑定但不改变来源机制；`TightenScope` 只执行 scope 收紧；`RetrieveNeighbor` 检索相邻 claim；`mechanism_on` 表示激活已确认；`observational_association` 是无可识别消融时保存的相关性对象。`promote / reject / return-counterexample / continue / tie` 是控制器返回枚举；`FAIL / PASS / UNRESOLVED` 是 gate 枚举；`REQUIRES / CONFLICTS / ALTERNATIVE_TO / REFINES / SUPPORTED_BY / REFUTED_BY` 是关系枚举。`mechanism + preconditions + interface + scope + regime` 构成 claim 的规范化键。`RETRIEVE_VIEW(M, query, as_of, scope_ceiling)` 是 `RETRIEVE_VIEW` 的完整调用签名。反例 schema 为 `{violated_claim, precondition, minimal_input, transform, seeds, minimal_trace_slice, reproducibility}`。

### 可执行不变量

1. 每个方法声明都能沿 `source_anchors → SourcePacket` 回到固定来源。
2. 每个候选都记录父版本、草图或自由来源、全部改动和未解决条件。
3. `activated=FALSE/UNKNOWN` 的候选不得更新方法效果后验。
4. scope 扩大需要新范围内至少一组配对、重复且可复核的证据。
5. 硬反例永远优先于平均分；违反硬约束的候选直接拒绝。
6. 所有派生索引都可从 `E_t/C_t/J_t/U_t/R_t` 重建。
7. 同一轮的 $D_t^{\mathrm{trace}}$、$D_t^{\mathrm{select}}$ 和 $D_t^{\mathrm{anchor}}$ 两两不相交，且每次使用都产生 `ExposureRecord`。
8. `MethodCatalogSnapshot` 在一次 benchmark 演化中不可改变；阶段四只能追加目标运行证据，不能导入新外部来源。
9. $D_{\mathrm{test}}$ 在 stop 前不可见，测试结果不得反向更新 Harness、检索策略或 $M_t$。
10. 任一 `OptimizerLLM` 输出在进入目录、候选、belief、动作集合或长期状态前，必须通过该 call type 的 parser、锚点、权限和规则核验；模型自述不构成证据。
11. `OptimizerLLM` 的概率、分数和语言置信度不得直接写入检索得分、观测似然、效果后验或晋级统计量。
12. 任一 select case 一旦通过 LLM 调用影响候选生成或修订，便对该候选及其后代永久失去独立选择资格，并由训练调度器补充未披露案例。
