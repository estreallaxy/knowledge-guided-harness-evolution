# 开放式架构协同演化：完整详细版
# 基于拓扑结构的协同演化

## 一、完整 Method

现有 Harness 自动优化通常由通用 coding agent 根据任务 Trace、评测反馈和 Harness 代码提出修改。Trace 能揭示信息在哪个阶段丢失、工具链在哪里中断，以及恢复路径为何失效，却不能完整给出系统还缺少哪种组件、控制角色或调用结构。因此，结构候选仍主要来自 coding agent 在当前推理中调用到的内部知识，容易反复调整已有模块，而难以系统地发现新的架构机制。

为扩展结构候选空间，我们引入经过整理和核验的论文方法与工程经验，从中提取可迁移的控制机制、依赖关系和实现条件，同时保留自主探索，使系统能够提出外部材料尚未覆盖的新组件与新拓扑。Trace、外部方法和自主探索分别提供当前结构缺口、已有解决机制与开放式候选，共同支持 Harness 的架构改进。

另一方面，已有架构搜索即使允许修改工作流或模块组合，也往往需要在预先定义的组件词表、结构语言和编辑操作中搜索。组件能否接入并不只取决于输入和输出，状态所有权、副作用、执行顺序、生命周期、异常传播和补偿路径都会影响整体行为。组件内容与调用拓扑彼此依赖，分开优化容易产生局部合理却无法正确接入的结构；成功结构如果只作为完整补丁保存，也难以转化为后续任务可以继续组合和演化的架构原语。

为同时解决结构机制不足与架构搜索空间难以持续扩展的问题，我们将 Harness 表示为带有类型、状态和 effect 契约的可执行程序图，并让组件原语与调用拓扑协同演化。外部方法与自主方案被转化为带有接口、依赖、观测条件和恢复语义的结构候选，Trace 则用于定位当前 Harness 的结构断点。候选通过插入、拆分、替换和重连组件形成新的 Harness，运行产生的绑定反例、机制激活证据和任务反馈继续修正组件契约与拓扑关系，经过验证的结构再沉淀为可复用原语。由此，系统既能搜索更好的架构组合，也能让架构搜索所使用的组件与结构语言随演化持续生长。

### 结构组织与检索阶段：如何组织和检索外部方法

论文中的方法往往以算法描述、模块图或某个仓库中的实现出现，而目标 Harness 具有不同的对象模型、生命周期与工具接口。单纯按关键词检索只能发现主题接近的材料，无法判断两个实现是否具有相同的数据流和控制依赖；直接保存整段代码又会把命名、框架胶水和任务特定细节误当成可迁移结构。因此，外部方法需要被转换为独立于具体仓库的程序结构，检索才可能回答“当前缺少哪种可执行拓扑”。

本阶段将方法表示为带类型和 effect 的程序图：节点描述状态、操作、检查器和工具调用，边描述控制流、数据流、生命周期与异常恢复关系。频繁出现的图模式只作为结构候选，必须同时满足来源语义、接口约束和执行证据，才能成为组件原语。自然语言说明仍用于扩大语义召回，但最终兼容性由图结构、类型签名和副作用约束决定，从而避免用文本相似度替代程序可组合性。

本阶段包含两个时间位置不同的动作。**离线组织**发生在 benchmark 演化 loop 之前：把论文算法和官方实现编译为来源图，在多来源图中挖掘可复用 motif，为每个 motif 保存变量角色、开放端口、必要依赖、禁止绑定和验证记录，并冻结为目录快照。**在线检索**发生在每一轮 loop 内：先根据 $H_t$ 在 $D_t^{\mathrm{trace}}$ 上暴露的结构断点形成 `StructuralNeed`，再联合查询离线目录与当前组件谱系的可复用视图，完成语义召回、子图匹配、类型/effect 过滤和依赖闭包。输出保持抽象端口，不提前绑定目标 Harness 的具体对象。

本阶段把语义解释与结构事实分开处理。离线时，`OptimizerHarness` 先固定论文段落、代码符号、配置、测试和执行锚点，再通过 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT` 让 `OptimizerLLM` 提出算法步骤与代码子图的对应、节点语义角色、契约字段和可能的组件边界；程序随后逐项核验来源、类型、effect、控制依赖和执行证据。在线时，`TRACE_TO_STRUCTURAL_NEED` 让 `OptimizerLLM` 从父图与成功/失败 trace 中提出多个可反驳的结构断点解释和 transformation tree；程序完成多视图召回、硬过滤、反向依赖闭包与结构匹配后，`SEMANTIC_MOTIF_BUNDLE_RERANK` 再比较各方法束是否真正对应当前失败机制。任何 LLM 输出都只是带锚点的提案，不能恢复被硬过滤的 motif、删除硬依赖或把语义相似直接升级为图等价。

原始材料首先保存为不可变来源包：

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

`SourcePacket` 只承担来源保存和审计，不直接进入在线候选综合。全部来源在演化开始前被编译为固定 `StructureCatalogSnapshot`；若新增论文、改变代码 revision 或修改结构抽取规则，必须产生新的目录快照并作为新的实验条件重新开始。第一轮 `StructuralNeed` 来自 $H_0$ 在 $D_0^{\mathrm{trace}}$ 上的真实运行，后续轮次则来自 $H_t$ 的新 trace、上一轮未完成的结构义务和已确认绑定反例。

从来源中提取的最小可执行单位采用如下契约：

```text
ComponentContract = {
  component_id,
  semantic_role,
  typed_inputs,
  typed_outputs,
  preconditions,
  effects,
  trace_events,
  verifier,
  compensation,
  authority_and_resources,
  source_anchors,
  semantic_alignment_call_ids,
  field_validation_status
}
```

其中 `effects` 至少区分状态读写、外部调用、资源创建与释放、随机性和不可逆操作；`verifier` 描述执行后能够产生什么证据；`compensation` 描述失败后的恢复能力。只有输入输出类型而没有状态和 effect 的组件不能被视为可安全组合。

一个论文方法先保存为具体实现图，再从多个实现中产生结构模板：

```text
MethodGraphVariant = {
  nodes: ComponentContract[],
  data_edges,
  state_edges,
  order_edges,
  effect_conflicts,
  bounded_loop_regions,
  method_preconditions,
  expected_observations,
  execution_evidence,
  source_packet
}

GraphMotif = {
  motif_id,
  fixed_structure,
  typed_open_ports,
  required_effects,
  forbidden_compositions,
  concrete_variants,
  validated_rewrites,
  support_and_counterevidence
}
```

边统一使用“生产者或前置条件 $\rightarrow$ 消费者”的方向。重试和循环保存为带退出条件与上界的显式 region，不为迁就 DAG 表示而静默展开。

**算法 1：有证据约束的外部方法结构编译。**

1. **固定最小来源视图。** `OptimizerHarness` 将论文步骤、伪代码、官方代码符号、配置、测试和可重放执行对齐为不可变来源单元；尚未建立对应关系的材料仍保留原位置。
2. **提出语义图映射。** 对每个来源单元发起 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT`。`OptimizerLLM` 提出算法步骤到代码节点/边的候选映射、节点语义角色、输入输出、前置条件、effect、verifier、compensation、开放端口和组件边界，并逐字段引用来源锚点、相反证据与不确定项。
3. **编译并核验具体方法图。** 程序从代码控制流、数据流、状态读写和异常处理构造候选 `MethodGraphVariant`，再把语义映射叠加到图上；锚点不存在、类型/effect 不成立或执行路径不支持的字段分别变为 `paper_only`、`code_only`、`UNKNOWN` 或 `unverified_relation`，不能因描述合理而通过。
4. **执行契约核验。** 对能够运行的来源实现执行类型、schema、资源和测试检查；论文报告、代码静态事实、本地执行证据和 LLM 提案分开保存。没有执行证据的图仍可检索，但不能标为已验证组件。
5. **发现语法结构候选。** 在已编译图语料上使用 Stitch 式自顶向下搜索，从带孔模式开始扩展，利用匹配集、定义成本和潜在复用收益剪枝。输出的是候选模板，不是方法真理。
6. **受限地消除表面差异。** 只在高价值候选区域使用 babble 式 e-graph 与反统一。`OptimizerLLM` 提出的语义相同或相近只能帮助选择需要验证的候选对；等价重写必须来自类型/effect 规则、编译器规范或差分执行验证。
7. **保留模板与具体实现。** 抽象模板、每个具体 variant、抽象时使用的重写路径和未解决孔位同时保存。模板不能覆盖来源实现。
8. **生成检索投影。** 根据经核验契约、结构差异、来源和实际 trace 形成文本、端口/effect、局部结构、依赖与证据五类投影；投影只用于发现候选，不反向改写结构事实。
9. **冻结多视图索引。** 保存全部语义对齐调用及其拒绝结果；结构抽取、提示模板、parser、核验器或索引配置变化都产生新的目录 revision。

检索输入为：

```text
StructuralNeed = {
  need_id,
  source_call_id,
  competing_break_hypotheses,
  desired_capability,
  required_transformations,
  available_inputs_and_state,
  required_outputs_and_state,
  allowed_effects,
  forbidden_effects,
  authority_and_environment,
  unresolved_requirements,
  query_plan
}
```

`StructuralNeed` 不从任务说明直接臆测。静态任务与 Harness 信息只提供初始约束；所请求的能力变换、可用状态、缺失 effect 和未决条件必须由当前父 Harness 的训练 trace、程序图和上一轮结构证据共同确定。

**算法 2：目标分解、反向依赖闭包与结构匹配。**

1. `OptimizerHarness` 从当前父图、成功/失败 trace 对照、开放结构义务和已确认绑定反例构造 `TRACE_TO_STRUCTURAL_NEED` 最小视图；`OptimizerLLM` 提出多个结构断点假设、最早偏离路径、所需能力变换和可判别观察。程序核验其事件、节点、边、状态版本和权限引用，未被证据支持的解释保留为 hypothesis。
2. 将经核验需求拆成可验证的 transformation tree，每个叶节点声明输入、输出、状态条件和 verifier。分解结果必须覆盖原目标并保持必要顺序；LLM 的自然语言分解不能直接作为规格。
3. 对每个 transformation 使用文本、端口/effect 和结构索引产生种子。允许一个 motif 覆盖多个需求，也允许一个需求由多个 motif 合作完成，不使用固定一对一匹配。
4. 先执行硬过滤：禁止 effect、权限冲突、明确不满足的前置条件和不可解决的版本冲突直接排除；未知条件保留为未决孔位。
5. 从候选消费者沿 `data/state/order/effect` 硬依赖反向递归，直到所有前置条件由环境、已有组件或同一 bundle 中的生产者满足；资源所有权属于 state/端口契约，控制先后属于 order 边。
6. 对 `workflow/semantic/alternative` 等软关系执行反向加权扩展，只用于发现配套方法和备选结构，不能代替硬闭包。
7. 对每个闭合 bundle 执行带类型的近似子图匹配，并计算：

   $$
   S(B,N)=w_qC_{need}+w_tC_{type}+w_eC_{effect}
   +w_dC_{dependency}+w_vE_{validated}
   -w_uU_{unknown}-w_rR_{risk}-w_cC_{conflict}.
   $$

8. 对通过硬过滤与依赖闭包的 bundle 构造 `SEMANTIC_MOTIF_BUNDLE_RERANK` 视图。`OptimizerLLM` 逐束说明 motif 机制如何对应结构断点、需要哪些迁移绑定、束内组件如何互补及什么观察会反驳该匹配；程序只接受可回指当前 trace、父图和来源图的字段。
9. 通过倒数秩融合程序排序与经核验的语义排序，返回若干结构机制不同的 `RetrievedMotifBundle`，包含完整依赖、具体 variants、开放端口、来源证据和未决条件。本阶段到此停止，不生成当前 Harness 的 adapter。

```text
OFFLINE_COMPILE_STRUCTURE_CATALOG(source_packets, organization_protocol):
    units <- ALIGN_SOURCE_UNITS(source_packets)
    alignment_requests <- BUILD_SOURCE_GRAPH_ALIGNMENT_REQUESTS(units)
    alignment_calls <- CALL_OPTIMIZER_LLM(
                           alignment_requests,
                           call_type=SOURCE_GRAPH_SEMANTIC_ALIGNMENT)
    alignment_proposals <- PARSE_SOURCE_GRAPH_ALIGNMENTS(alignment_calls)
    alignments <- VERIFY_SOURCE_GRAPH_ALIGNMENTS(
                      alignment_proposals, units)
    variants <- COMPILE_METHOD_GRAPHS(source_packets, alignments)
    CHECK_COMPONENT_CONTRACTS(variants)
    syntax_candidates <- STITCH_STYLE_MINE(variants)
    motifs <- BOUNDED_EGRAPH_NORMALIZE_AND_ANTI_UNIFY(
        syntax_candidates, organization_protocol.validated_rewrites)
    indexes <- BUILD_TEXT_TYPE_EFFECT_STRUCTURE_INDEXES(motifs)
    return FREEZE_STRUCTURE_CATALOG(source_packets, variants,
                                    motifs, indexes)

BUILD_STRUCTURAL_NEED(parent, host_graph, trace_batch,
                      pending_structural_evidence):
    need_view <- BUILD_TRACE_TO_STRUCTURAL_NEED_VIEW(
                     parent, host_graph, trace_batch,
                     pending_structural_evidence)
    need_call <- CALL_OPTIMIZER_LLM(
                     need_view, call_type=TRACE_TO_STRUCTURAL_NEED)
    need_proposal <- PARSE_STRUCTURAL_NEED_PROPOSAL(need_call)
    return VERIFY_STRUCTURAL_NEED_GRAPH_AND_TRACE_ANCHORS(
               need_proposal, need_view)

ONLINE_RETRIEVE_MOTIFS(catalog_snapshot, reusable_view,
                       need, trace_graph_view):
    query_tree <- VALIDATED_TRANSFORMATION_DECOMPOSITION(need)
    indexes <- MERGE_STRUCTURE_RETRIEVAL_VIEWS(
                   catalog_snapshot.indexes, reusable_view)
    seeds <- MULTIVIEW_RETRIEVE(indexes, query_tree)
    seeds <- HARD_CONSTRAINT_FILTER(seeds, need)
    bundles <- REVERSE_HARD_DEPENDENCY_CLOSURE(seeds)
    bundles <- SOFT_REVERSE_EXPANSION(bundles)
    bundles <- TYPE_EFFECT_SUBGRAPH_RERANK(bundles, need)
    rerank_request <- BUILD_SEMANTIC_MOTIF_RERANK_REQUEST(
                          bundles, need, trace_graph_view)
    rerank_call <- CALL_OPTIMIZER_LLM(
                       rerank_request,
                       call_type=SEMANTIC_MOTIF_BUNDLE_RERANK)
    rerank_proposal <- PARSE_SEMANTIC_MOTIF_RERANK(rerank_call)
    return FUSE_VERIFIED_STRUCTURE_AND_SEMANTIC_RANKS(
               bundles, rerank_proposal)
```


### 结构候选生成阶段：如何结合 trace、知识与自主探索生成候选

结构原语描述的是通用控制或数据关系，而不是可以直接粘贴到目标仓库的补丁。当前 Harness 可能使用完全不同的状态对象、事件循环和工具封装，失败 trace 也可能只暴露整个程序图中的一个局部断点。若让模型基于自然语言说明重写整份 Harness，结构来源、实际变更和机制激活之间就无法对应，后续测评也不能判断究竟是哪条边带来了影响。

这里先把当前 Harness 与 trace 编译到和外部方法相同的图语言，再把故障定位为待替换、待扩展或待重新绑定的局部子图。知识候选从已验证 motif 出发，通过端口绑定和带孔程序补全完成适配；自由候选可以创造新节点与拓扑，但必须声明类型、effect、生命周期和观测点，并通过同样的图验证。两条路径共享表示后，系统既能利用外部结构，也能把自主发现的新结构纳入后续组件库。

算法为每个可疑子图生成若干 `StructuralSketch`。在此之前，`TRACE_GRAPH_DIAGNOSIS` 让 `OptimizerLLM` 比较成功/失败路径、状态版本和图切片，提出多个结构因果链及能区分它们的 probe；`OptimizerHarness` 只保留事件顺序、节点/边和数据依赖均可核验的诊断。随后程序利用类型约束、依赖闭包和反例约束枚举合法绑定，并构造知识补全与自由探索两类最小输入视图。`OptimizerLLM` 在知识通道中补全 motif 的局部实现，在自由通道中提出满足图文法的新节点或新边。CEGIS 返回新反例时，`COUNTEREXAMPLE_TO_GRAPH_REVISION` 让 `OptimizerLLM` 判断是端口误绑、前置结构缺失、节点语义错误、连线错误、控制条件错误还是补偿缺失，并提出最小修订意图；程序仍负责把意图编译成允许动作、重新检查并冻结新版本。

**trace 的来源。** 设 benchmark 官方训练集为 $D_{\mathrm{train}}$。第 $t$ 轮先固定父 Harness $H_t$、执行模型、工具与容器版本、评测器和种子，再在 $D_t^{\mathrm{trace}}$ 上实际运行。第一轮运行 $H_0$，以后运行上一轮确定的 $H_t$。每次运行都生成下文定义的不可变 `ExecutionTrace`。

第 $t$ 轮开始时，训练调度器将 benchmark 训练集冻结为三个互不重叠的主要角色。$D_t^{\mathrm{trace}}$ 运行当前父 Harness $H_t$，产生定位结构缺口所需的成功与失败 trace；$D_t^{\mathrm{select}}$ 在候选冻结前不进入 `OptimizerHarness` 构造的生成上下文，也不向 `OptimizerLLM` 披露，只用于比较候选与父代；$D_t^{\mathrm{anchor}}$ 回放已经确认的旧能力、关键接口和严重失败。本轮测评池为 $D_{dev}^{(t)}=D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}$。候选可以反复利用 $D_t^{\mathrm{trace}}$ 完成结构综合和绑定修复，却不能把这些运行重新计作独立收益证据。若本轮产生待抽象组件，调度器还预留没有参与该结构形成的 $D_t^{\mathrm{transfer}}$，只在第四阶段检查跨绑定复用。

```text
ExecutionTrace = {
  run_id,
  task_id,
  split_role,
  harness_version,
  model_tool_environment_versions,
  seed,
  ordered_component_events,
  state_and_artifact_versions,
  final_output,
  metric_vector,
  failure_signature,
  replay_artifacts
}
```

`ordered_component_events` 记录模型调用、工具调用、状态读写、组件入口与出口、guard 判定、循环迭代、异常、补偿、回退和终止，并关联到宿主程序图的节点与边；无法映射的事件明确标为 `unmapped`。成功 trace 与失败 trace 必须来自同一执行协议，前者用来排除普遍存在的结构，后者用来暴露断点。只有最终分数而没有事件与状态版本链的运行，不能用于图切片、端口绑定或机制激活判断。本轮的候选生成只能读取 $D_t^{\mathrm{trace}}$，不能读取测试集或 $D_t^{\mathrm{select}}$ 的结果。

当前 Harness 表示为：

$$
H_t=(V_t,E_t^{data},E_t^{state},E_t^{order},E_t^{effect},R_t^{loop},\Lambda_t),
$$

其中 $R_t^{loop}$ 是带上界、进展条件和退出条件的循环或重试 region，$\Lambda_t$ 是版本父边、innovation、结构编辑和 motif revision 组成的谱系元数据。组件状态不是简单布尔值，而是带版本的 artifact 与外部状态。

本阶段输入输出为：

```text
EvolutionInput = {
  frozen_parent_harness,
  trace_batch,
  structural_need,
  retrieved_motif_bundles,
  binding_counterexamples,
  preservation_requirements,
  hard_constraints
}

CandidateVersion = {
  candidate_id,
  ir_id,
  parent_id,
  candidate_graph,
  code_patch,
  motif_sources,
  structural_edits,
  port_bindings,
  expected_trace_contract,
  preservation_requirements,
  unresolved_assumptions,
  hard_gate_status,
  revision,
  frozen_at,
  llm_call_ids
}
```

**输入。** 冻结父代 $H_t$、从 $D_t^{\mathrm{trace}}$ 得到的 `ExecutionTrace[]`、由这些 trace 与宿主图形成的 `StructuralNeed`、在线检索返回的 motif bundles、前轮确认的绑定反例、旧能力保护谓词和硬约束。

**输出。** 一组不可原地修改的 `CandidateVersion`，以及仍未解决的 `StructuralObligation[]`。候选同时携带代码补丁和程序图差分；结构义务明确指出尚缺的端口、前置节点、effect、观测 probe、补偿边或终止条件，供拓扑控制器决定继续补全还是终止该分支。

**算法 3：trace 约束的类型化图综合。**

1. **编译宿主图。** 从当前代码提取控制、数据、状态、effect 和异常路径，并把 trace 事件对齐到具体节点、边与状态版本。无法对齐的事件保留为 `unmapped`。
2. **形成对比切片并提出结构诊断。** 比较成功和失败 trace，从失败事件沿数据、状态与控制前驱回溯，得到优先修改子图；再通过 `TRACE_GRAPH_DIAGNOSIS` 让 `OptimizerLLM` 提出最早结构偏离、传播链、候选根因、相反证据和判别 probe。程序检查所有事件与图锚点，切片和诊断只确定搜索顺序，不永久排除图外位置。
3. **建立乘积抽象域。** 根据查询涉及的类型、状态、effect 与 trace 条件建立有限抽象：

   $$
   A_0=A_{type}\times A_{state}\times A_{effect}\times A_{trace}.
   $$

   对多态类型使用 TYGAR 式抽象覆盖逐步细化；会话、事务和凭据等资源采用不可任意复制的 token。
4. **综合结构骨架。** 把抽象状态表示为 place，把组件或 motif 实例表示为 transition，在类型、资源、effect、权限和目标状态约束下搜索候选骨架。骨架只决定组件集合和粗粒度顺序。
5. **生成带孔程序。** 将开放端口、具体 artifact 绑定、状态版本、guard、verifier、timeout、重试、补偿与局部顺序保存为有类型的 holes。
6. **双通道补全。** `OptimizerHarness` 为知识通道构造包含检索 motif、合法端口绑定、父图局部切片和有类型孔位的请求，由 `OptimizerLLM` 补全适配代码；它另为自主探索通道构造不披露检索 motif 及知识候选的请求，由 `OptimizerLLM` 在同一图文法和硬约束下提出新节点或新边。两类输出都由 `OptimizerHarness` 解析为相同 Candidate IR，并交给同一 SMT/规则检查器补全确定性约束。
7. **执行有界 trace CEGIS。** 候选在当前反例集上通过后，validator 在允许的输入、状态、seed、schedule 与故障注入范围内寻找新的反例。确定性反例直接加入约束；随机失败只有在可重复并带统计证据时形成经验反例。
8. **解释反例并局部修复。** 对确认反例发起 `COUNTEREXAMPLE_TO_GRAPH_REVISION`。`OptimizerLLM` 必须在 `REBIND / INSERT_PREREQ / SUBSTITUTE / REWIRE / ADJUST_CONTROL / INSERT_COMPENSATION` 中选择或排序最小修订，指出目标节点/边、保持不变的机制和修订后应改变的 trace。`OptimizerHarness` 核验反例引用、权限和编辑边界后才执行；Getafix 式历史 rewrite 只负责提供或排序 proposal，修复后重新运行全部静态检查与反例回放。
9. **冻结候选。** 通过编译、类型/effect、权限、可达性、循环终止和父代接口检查后生成不可变候选版本。任何再次修复都产生新版本。

```text
SYNTHESIZE_TOPOLOGY_CANDIDATES(
    parent, trace_batch, need, bundles, binding_counterexamples,
    preservation_requirements, hard_constraints):
    host_graph <- COMPILE_TYPED_EFFECT_GRAPH(parent)
    slice <- CONTRAST_SUCCESS_FAILURE_TRACES(host_graph, trace_batch)
    diagnosis_request <- BUILD_TRACE_GRAPH_DIAGNOSIS_REQUEST(
                             parent, host_graph, slice, trace_batch, need)
    diagnosis_call <- CALL_OPTIMIZER_LLM(
                          diagnosis_request,
                          call_type=TRACE_GRAPH_DIAGNOSIS)
    diagnosis_proposals <- PARSE_TRACE_GRAPH_DIAGNOSES(diagnosis_call)
    diagnoses <- VERIFY_GRAPH_AND_TRACE_CAUSAL_CHAINS(
                     diagnosis_proposals, host_graph, trace_batch)
    abstract_domain <- INIT_PRODUCT_ABSTRACTION(slice, bundles)

    repeat:
        skeletons <- SEARCH_RESOURCE_EFFECT_SKELETONS(
            host_graph, bundles, abstract_domain, diagnoses)
        sketches <- CREATE_TYPED_HOLES(skeletons, diagnoses)
        knowledge_requests <- BUILD_KNOWLEDGE_TOPOLOGY_REQUESTS(
                                  parent, sketches, bundles, slice,
                                  preservation_requirements,
                                  hard_constraints)
        knowledge_calls <- CALL_OPTIMIZER_LLM(
                               knowledge_requests,
                               call_type=KNOWLEDGE_TOPOLOGY_COMPLETION)
        knowledge <- PARSE_KNOWLEDGE_TOPOLOGY_COMPLETIONS(
                         knowledge_calls)
        free_request <- BUILD_FREE_TOPOLOGY_REQUEST(
                            parent, sketches, slice, hard_constraints)
        free_call <- CALL_OPTIMIZER_LLM(
                         free_request,
                         call_type=FREE_TOPOLOGY_PROPOSAL)
        free <- PARSE_FREE_TOPOLOGY_PROPOSALS(free_call)
        candidates <- COMMON_STATIC_CHECK(knowledge union free)

        evidence, counterexamples <- BOUNDED_TRACE_VALIDATE(
                                         candidates, trace_batch,
                                         binding_counterexamples)
        revision_intents <- empty
        if counterexamples is not empty:
            revision_request <- BUILD_GRAPH_REVISION_REQUEST(
                                    candidates, counterexamples,
                                    diagnoses, sketches)
            revision_call <- CALL_OPTIMIZER_LLM(
                                 revision_request,
                                 call_type=COUNTEREXAMPLE_TO_GRAPH_REVISION)
            revision_proposals <- PARSE_GRAPH_REVISION_PROPOSALS(
                                      revision_call)
            revision_intents <- VERIFY_MINIMAL_GRAPH_REVISION_INTENTS(
                                    revision_proposals,
                                    counterexamples, parent)
        if counterexamples reveal spurious abstraction:
            abstract_domain <- REFINE_FROM_UNTYPEABILITY_OR_TRACE(counterexamples)
        candidates <- LOCAL_GRAPH_REPAIR(
                          candidates, counterexamples, revision_intents)
    until no decision-relevant refinement remains

    frozen <- FREEZE_VALID_CANDIDATE_VERSIONS(candidates, evidence)
    obligations <- EXTRACT_STRUCTURAL_OBLIGATIONS(frozen, counterexamples)
    return frozen, obligations
```


### 拓扑规划与测评阶段：如何规划、测评并控制多轮 Harness 演化

结构性改动常常需要多步才能形成闭合回路：增加记忆写入而没有读取策略、增加检查器而没有恢复边，都会在中间版本中表现不佳。若每一代只按当前总分选择，新拓扑会在完成前被淘汰；若对所有新结构提供长期保护，复杂但无效的分支持续占用评测资源。演化控制必须既允许结构逐步生长，又给这种保护设置可验证的期限和退出条件。

本阶段以谱系和结构里程碑管理候选。新分支只有在来源清楚、图合法、关键机制可观测且带来新的可达状态时，才获得有限的结构创新保护。保护期间的评测重点确认缺失边是否正在补齐、机制事件是否按预期出现；一旦达到闭合拓扑，候选必须回到统一的任务收益、回归和成本标准下竞争。这样，结构新颖性只换取完成验证的机会，不直接换取晋级资格。

控制器维护候选谱系、待完成的结构义务和各任务族证据，在 `mutate`、`refine-binding`、`add-probe`、`paired-evaluate`、`promote`、`retire` 与 `rollback` 之间滚动选择。动作价值由它能否解决当前结构义务或改变父子选择决定；接入反例返回结构生成阶段，缺失的通用原语则形成新的检索需求。最终晋级要求拓扑闭合、机制激活、相对父代有稳定收益且旧能力满足保护约束。

本阶段只使用训练集内预先冻结的 $D_t^{\mathrm{select}}$ 与 $D_t^{\mathrm{anchor}}$。前者负责提供候选生成过程未见过的父子收益证据，后者负责检查已确认能力和严重失败是否回归。候选与父代必须在相同 task、seed、模型、工具和环境下成对运行；两类执行都产生与候选生成阶段相同 schema 的 `ExecutionTrace` 并写入 `TopologyEvaluationLedger`，但其 `split_role` 保持可区分。$D_t^{\mathrm{trace}}$ 只允许用于结构诊断、绑定修复和机制 probe，不能再次作为候选相对父代的独立收益样本。

**输入。** 父代 $H_t$、冻结候选、每个候选的 `StructuralObligation[]`、$D_t^{\mathrm{select}}$、$D_t^{\mathrm{anchor}}$ 与当前 Harness 谱系 $L_t^H$。候选已经携带其引用的组件 revision，因此本阶段不直接修改 $L_t^M$。

**输出。** `Promote / Reject / Tie / ReturnBindingCounterexample / ReturnStructuralNeed / Continue` 之一、完整 `TopologyEvaluationLedger` 和更新后的本轮候选谱系。返回绑定反例或结构需求时仍停留在第 $t$ 轮；只有 `Promote / Reject / Tie` 才允许进入组件积累并结束本轮。

本阶段让 `OptimizerLLM` 参与“证据意味着什么”和“下一步应区分什么”，但不把最终晋级交给模型。`MUTANT_AND_PROBE_PROPOSAL` 根据候选机制与未决义务提出能够破坏关键结构的 mutant 和判别 probe；`TOPOLOGY_EVIDENCE_INTERPRETATION` 把 gate、mutant、父子配对和回归结果解释为对结构义务、绑定假设和机制激活的支持、反对或未知；`NEXT_LINEAGE_ACTION_PROPOSAL` 在合法动作上提出排序或新的局部动作；搜索停滞时，`STALLED_LINEAGE_REFLECTION` 检查遗漏原语、错误结构假设和替代拓扑。`OptimizerHarness` 核验所有图/trace 锚点、维护义务状态、执行真实动作，并依据冻结的收益、回归和结构门作出最终决定。若 select/anchor 证据经 LLM 解释后影响候选修订，相应 case 必须从该候选及后代的独立选择证据中移除并重新划分。

系统维护两个彼此独立的标识：`semantic_component_id` 表示组件的语义身份，`innovation_id` 只记录某次谱系中的结构变化。同一结构由不同祖先独立产生时可以具有不同谱系记录；谱系相同但结构已变化时也不能被视为语义相同。

每个候选 genome 包含节点、边、参数、启用状态、结构来源和创新记录。演化从“最小可运行、可验证、权限完整”的 Harness 开始，使用以下渐增算子：

| 算子 | 结构变化 | 初始保护条件 |
| --- | --- | --- |
| `SPLIT_EDGE` | 在已有边中插入 adapter、validator 或状态转换 | 插入前后接口与 effect 可检查 |
| `ADD_GUARDED_BRANCH` | 增加带 guard 的重试、fallback 或替代路径 | 默认不触发时保持父代行为 |
| `INSERT_MOTIF` | 插入依赖闭合的外部方法子图 | motif 契约与宿主端口可满足 |
| `SUBSTITUTE_NODE` | 替换接口兼容的组件 | effect、权限和补偿语义兼容 |
| `ADD_CHECK_OR_COMPENSATION` | 增加 verifier、回滚或清理节点 | 能观察或恢复目标 effect |
| `SPECIALIZE_CONTROL` | 修改 guard、参数或有界循环策略 | 不删除原有终止与安全约束 |

**算法 4：谱系感知的结构演化控制。**

1. **登记创新事件。** 每次结构编辑记录父代、算子、目标位置、前置条件以及新增和停用的节点/边。编号用于对齐祖先关系，不作为结构相似度或组件内容地址。
2. **划分结构物种。** 按共同创新、类型化子图编辑和参数差异计算结构距离：

   $$
   d(H_i,H_j)=c_1D_{innovation}+c_2D_{typed\ graph}+c_3D_{parameter}.
   $$

   阈值只用于形成局部竞争组，需要在 Harness 数据上校准；NEAT 的原始距离公式不能直接照搬。
3. **执行结构与机制 gate。** 检查编译、接口、effect、权限、状态版本、循环终止、异常恢复和父代能力 anchor；随后验证新增结构是否可触发并产生声明的中介 trace。每批结果由 `TOPOLOGY_EVIDENCE_INTERPRETATION` 提出其对义务和结构假设的含义，程序依据事件与图锚点更新状态，模型置信度不进入晋级统计。
4. **审计测评敏感性。** 程序枚举删除新增边、绕过 verifier、交换关键顺序或关闭 fallback 等基础 mutant；`MUTANT_AND_PROBE_PROPOSAL` 可以补充与候选语义相关的破坏方式及判别 probe。只有可执行、保持非目标条件且预期观察明确的提案才能运行。若当前 probe 无法区分原候选与破坏机制的 mutant，先补测评，不依据任务分数晋级。
5. **物种内成对比较。** 使用相同任务、seed、模型和环境比较候选与直接父代，分别记录目标收益、旧能力回归、随机方差和结构复杂度。
6. **有限保护新谱系。** 新物种只在机制已激活且没有确定性违规时获得继续验证或一次局部补全机会。保护期结束后仍无能力增益、诊断价值或后代潜力的谱系被归档。
7. **选择下一动作。** 程序先枚举 `mutate / refine-binding / add-probe / paired-evaluate / promote / retire / rollback`，再由 `NEXT_LINEAGE_ACTION_PROPOSAL` 基于未决义务、结构谱系和证据缺口提出排序或参数完整的新动作。`OptimizerHarness` 只保留可执行、数据角色合法且能改变当前决定的动作。接入反例返回结构候选生成阶段；缺失结构原语形成新的 `StructuralNeed` 返回结构组织与检索阶段。
8. **反思停滞分支。** 当合法动作为空、同类绑定反例反复出现或结构义务长期为 `UNKNOWN` 时，`STALLED_LINEAGE_REFLECTION` 提出遗漏原语、替代拓扑、需要收紧的假设或判别实验；经图锚点和可执行性核验后返回阶段一或二，模型不能直接宣布收敛。
9. **谨慎使用交叉。** mutation-only 作为默认和必须报告的基线。只有两个父代的共同创新可以对齐，且未匹配子图通过接口、依赖、权限和 effect 检查时才允许 crossover；交叉后重新执行图修复与完整 gate。
10. **晋级父代。** 只有机制证据完整、相对父代收益得到配对支持、关键旧能力未越界的候选才形成 $H_{t+1}$。结构新颖性、年龄和 LLM 建议只提供取证机会，不计入最终性能。

```text
PLAN_AND_TEST_TOPOLOGY_EVOLUTION(parent, candidates, obligations,
                                 select_pool, anchor_pool, lineage):
    REGISTER_INNOVATION_EVENTS(candidates, lineage)
    species <- STRUCTURAL_SPECIATION(candidates, lineage)
    ledger <- empty

    loop:
        for candidate with incomplete gates:
            probes <- ENUMERATE_PROGRAM_MUTANTS_AND_PROBES(
                          candidate, obligations[candidate])
            if SEMANTIC_MUTANT_GAP(
                   candidate, obligations[candidate], probes, ledger):
                mutant_request <- BUILD_MUTANT_AND_PROBE_REQUEST(
                                      candidate, obligations[candidate],
                                      probes, ledger)
                mutant_call <- CALL_OPTIMIZER_LLM(
                                   mutant_request,
                                   call_type=MUTANT_AND_PROBE_PROPOSAL)
                mutant_proposals <- PARSE_MUTANT_AND_PROBE_PROPOSALS(
                                        mutant_call)
                semantic_probes <- COMPILE_VALID_MUTANTS_AND_PROBES(
                                       candidate, mutant_proposals)
                probes <- probes union semantic_probes
            evidence <- RUN_STRUCTURE_MECHANISM_AND_MUTANT_CHECKS(
                            candidate, obligations[candidate], probes)
            APPEND(ledger, evidence)

            interpretation_request <- BUILD_TOPOLOGY_EVIDENCE_REQUEST(
                                          candidate, obligations[candidate],
                                          evidence, lineage)
            interpretation_call <- CALL_OPTIMIZER_LLM(
                                       interpretation_request,
                                       call_type=TOPOLOGY_EVIDENCE_INTERPRETATION)
            interpretation <- PARSE_TOPOLOGY_EVIDENCE_INTERPRETATION(
                                  interpretation_call)
            interpretation <- VERIFY_TOPOLOGY_EVIDENCE_ANCHORS(
                                  interpretation, evidence, candidate)
            UPDATE_STRUCTURAL_OBLIGATIONS(
                obligations[candidate], interpretation, evidence)
            if evidence contains binding_counterexample:
                attribution <- EXTRACT_VERIFIED_BINDING_ATTRIBUTION(
                                   interpretation, evidence)
                return RETURN_TO_TOPOLOGY_SYNTHESIS(
                           evidence, attribution), ledger

        decision <- PAIRED_PARENT_CHILD_DECISION(
                        parent, candidates, ledger)
        if decision is promote/reject/tie:
            return decision, ledger

        program_actions <- ENUMERATE_LEGAL_LINEAGE_ACTIONS(
                               species, obligations, ledger)
        action_request <- BUILD_NEXT_LINEAGE_ACTION_REQUEST(
                              species, obligations, ledger,
                              program_actions)
        action_call <- CALL_OPTIMIZER_LLM(
                           action_request,
                           call_type=NEXT_LINEAGE_ACTION_PROPOSAL)
        action_proposals <- PARSE_LINEAGE_ACTION_PROPOSALS(action_call)
        actions <- program_actions union COMPILE_VALID_LINEAGE_ACTIONS(
                                          action_proposals,
                                          obligations, ledger)
        action <- SELECT_DECISION_RELEVANT_LINEAGE_ACTION(actions, ledger)
        if action is NONE and decision-relevant uncertainty remains:
            reflection_request <- BUILD_STALLED_LINEAGE_REFLECTION_REQUEST(
                                      species, obligations, ledger)
            reflection_call <- CALL_OPTIMIZER_LLM(
                                   reflection_request,
                                   call_type=STALLED_LINEAGE_REFLECTION)
            reflection <- PARSE_STALLED_LINEAGE_REFLECTION(reflection_call)
            return_request <- VERIFY_AND_COMPILE_LINEAGE_RETURN(reflection)
            if return_request is valid:
                return return_request, ledger
            action <- COMPLETE_DEVELOPMENT_PANEL_ACTION(ledger)
        if action is NONE:
            return tie, ledger
        if action requires missing primitive:
            need <- BUILD_STRUCTURAL_NEED_FROM_ACTION(action, ledger)
            return RETURN_TO_MOTIF_RETRIEVAL(need), ledger
        if action is paired-evaluate:
            result <- PAIRED_PARENT_CHILD_RUNS(
                          parent, TARGETS(action),
                          select_pool, anchor_pool,
                          TASKS_AND_SEEDS(action))
        else:
            result <- EXECUTE(action)
        APPEND(ledger, result)
        result_interpretation_request <- BUILD_TOPOLOGY_EVIDENCE_REQUEST(
                                             TARGETS(action), obligations,
                                             result, lineage)
        result_interpretation_call <- CALL_OPTIMIZER_LLM(
                                          result_interpretation_request,
                                          call_type=TOPOLOGY_EVIDENCE_INTERPRETATION)
        result_interpretation <- PARSE_TOPOLOGY_EVIDENCE_INTERPRETATION(
                                     result_interpretation_call)
        result_interpretation <- VERIFY_TOPOLOGY_EVIDENCE_ANCHORS(
                                     result_interpretation, result,
                                     TARGETS(action))
        UPDATE_RELEVANT_STRUCTURAL_OBLIGATIONS(
            obligations, result_interpretation, result)
        # 下一次循环依据真实结果重新决策和规划
```


### 组件积累与复用阶段：如何持续积累并跨任务复用

一个成功补丁通常混合了通用程序结构、目标仓库的适配层和偶然实现细节。直接保存完整 patch 会产生大量近重复组件，换一个框架便无法复用；只保存文字总结又会丢失端口、依赖和控制流，下一次仍需从头实现。组件积累必须从真实执行谱系中识别可以独立成立的结构，同时保留它与具体适配器之间的边界。

这里把复用对象设为版本化组件谱系，而不是孤立代码片段。候选结构先根据图同构和语义角色聚类，再提取最小公共 motif；目标 Harness 特定的绑定被保留为 adapter revision，通用节点与边形成 component revision。压缩率只用于发现候选，能否进入活动库还取决于跨任务回放、机制消融、迁移工作量和回归风险，避免“常见”被误认为“有效”。

每轮从已验证谱系中收集图差分和运行证据，执行结构去重、接口归一化、反例合并和版本分叉。新组件需要在至少一个不同任务或 Harness 绑定上复现预期机制，并通过移除该组件的对照确认贡献；随后更新结构索引和文本索引。新任务检索时返回组件、可用 adapter、已知冲突和迁移成本，使历史结果以可执行结构而不是模糊经验进入下一轮。

本阶段由 `OptimizerLLM` 提出需要语义判断的组件边界和谱系关系，由 `OptimizerHarness` 用结构与执行证据决定能否提交。`SEMANTIC_COMPONENT_ABSTRACTION` 比较多个成功/失败图差分，提出哪些节点和边属于可复用机制、哪些应变成开放端口或保留为宿主 adapter；`COMPONENT_RELATION_PROPOSAL` 比较新 motif 与既有组件 revision，提出重复、细化、替代、冲突或组合关系；跨任务重放失败时，`FAILED_TRANSFER_ATTRIBUTION` 区分端口绑定、宿主 effect、adapter、regime 与抽象过宽；通过全部结构和证据门后，`COMPONENT_DOCUMENTATION` 才生成使用说明。程序负责图同构、类型/effect、跨任务重放、配对 mask、硬门、revision 提交和索引重建，任何语义提案都不能直接修改双谱系。

这一阶段位于 benchmark 训练 loop 内，在每轮得到终止决定后执行。它只沉淀本轮父代 trace、候选图、绑定反例、结构 gate、父子配对和 anchor 回放产生的证据，不在运行中接收或重新解析新论文。外部来源的增加只能在 loop 外产生新的 `StructureCatalogSnapshot`；在线积累得到的组件 revision 则写入 $L_{t+1}^{M}$，在下一轮 `StructuralNeed` 形成之后通过有条件的 `ReusableComponentView` 被检索。

**输入。** 本轮冻结的父代与候选图、`TopologyEvaluationLedger`、候选使用的 motif 与 adapter 记录、旧 Harness 谱系 $L_t^H$、旧组件谱系 $L_t^M$，以及尚未在该组件抽象中使用过的训练集 transfer cases。这里的 transfer cases 只能来自 $D_{\mathrm{train}}$ 或事先批准的外部训练环境，不能来自 benchmark 测试集。

**输出。** 原子提交的 $(L_{t+1}^{H},L_{t+1}^{M})$、可供下一轮按需查询的组件索引，以及未通过抽象门的 `FailedBindingRecord[]`。原始运行与图差分先只追加持久化；即使组件抽象、文档核验或索引重建失败，也不能丢失原始证据。

系统维护：

$$
L_t^{H}=\text{Harness 版本与结构谱系},\qquad
L_t^{M}=\text{可复用方法组件谱系}.
$$

被提升的组件保存为：

```text
ReusableGraphComponent = {
  component_revision,
  graph_motif,
  typed_open_ports,
  required_effects,
  applicability_conditions,
  concrete_variants,
  source_lineages,
  activation_evidence,
  paired_effect_evidence,
  regression_evidence,
  failed_bindings,
  validated_rewrites,
  abstraction_call_ids,
  relation_call_ids,
  transfer_attribution_call_ids,
  documentation,
  documentation_call_id
}
```

**算法 5：从成功谱系到可复用组件。**

1. **筛选结构语料。** 只有机制已激活、相对父代有配对证据、关键旧能力未回归且来源完整的候选进入抽象语料。失败结构也保存，但只作为反例和边界。
2. **提出并核验组件边界。** 对成功/失败图差分、具体绑定、激活 trace 和反例发起 `SEMANTIC_COMPONENT_ABSTRACTION`。`OptimizerLLM` 提出固定机制、开放端口、宿主 adapter、不可参数化常量和边界反例；程序检查每个节点/边能否回到来源谱系、是否保持类型/effect 与必要顺序。无法验证的部分保留在具体 variant，不进入公共 motif。
3. **两层发现并判定关系。** 先用 Stitch 式 top-down 搜索发现高复用语法结构；只对语法不同但行为证据接近的高价值区域运行受限 e-graph 与反统一。对新 motif 与既有组件候选发起 `COMPONENT_RELATION_PROPOSAL`，但重复、细化、替代、冲突或组合关系只有通过结构、scope、regime 和执行证据核验后才能写入谱系。
4. **多目标筛选。** 结构压缩只是一个信号，候选价值为：

   $$
   J(m)=\alpha G_{reuse}+\beta G_{execution}+\gamma G_{diagnosis}
   -\delta C_{definition}-\eta C_{migration}
   -\rho R_{instability}-\xi R_{semantic}.
   $$

   在计算该分数前，类型/effect 合法、来源任务回放和关键能力保持属于硬门槛。
5. **跨任务重放并归因失败。** 在所有来源 case、未用于抽象的同类任务以及至少一个跨项目任务上实例化 motif；分别报告结构可绑定率、机制激活率、任务收益、回归和修复次数。失败时通过 `FAILED_TRANSFER_ATTRIBUTION` 提出端口、effect、adapter、regime 或抽象边界解释，程序用重放事件与宿主图核验；证据不足时保存多个解释，不强行归因。
6. **验证公共结构贡献。** 在可行时 bypass 或 mask 公共子图，与完整候选做成对比较。无法消融时只记录关联证据，不能声称该 motif 导致收益。
7. **生成并核验文档。** `COMPONENT_DOCUMENTATION` 从已经通过门槛的契约、开放端口、来源差异、真实 trace 和失败绑定生成说明；检查名称能否区分相邻组件、示例是否可执行、限制是否完整。文档错误只修订说明，不静默改写程序结构。
8. **提交组件 revision。** 验证通过后原子写入 $L_t^M$，更新结构组织与检索阶段的结构和文本索引。旧 revision 与具体实现继续可追溯。
9. **根据反例分裂或回滚。** 后续失败先区分端口绑定错误、宿主 effect 缺失和抽象过宽。前两类形成 `failed_binding`；抽象过宽则缩小适用条件、分裂 motif 或回退到具体 variant。
10. **学习何时调用。** 循环执行 search–compress–learn-to-search：用实际检索、采用、激活和结果记录训练或更新检索器；冻结组件库与检索器后再做跨任务评测，避免边测边改。

```text
CONSOLIDATE_COMPONENT_LINEAGE(parent, candidates, decision,
                              harness_lineage, method_lineage,
                              ledger, eligible_transfer_cases):
    H_shadow <- APPEND_ROUND_LINEAGE_EVIDENCE(
                    harness_lineage, parent, candidates, decision, ledger)
    corpus <- SELECT_EVIDENCE_ELIGIBLE_STRUCTURES(H_shadow, ledger)
    abstraction_request <- BUILD_COMPONENT_ABSTRACTION_REQUEST(
                               corpus, ledger, method_lineage)
    abstraction_call <- CALL_OPTIMIZER_LLM(
                            abstraction_request,
                            call_type=SEMANTIC_COMPONENT_ABSTRACTION)
    abstraction_proposals <- PARSE_COMPONENT_ABSTRACTION_PROPOSALS(
                                 abstraction_call)
    parameterized <- VERIFY_AND_PARAMETERIZE_COMPONENT_BOUNDARIES(
                         corpus, abstraction_proposals)
    syntax_candidates <- STITCH_STYLE_MINE(parameterized)
    motifs <- BOUNDED_EGRAPH_NORMALIZE_AND_ANTI_UNIFY(syntax_candidates)

    for motif in MULTIOBJECTIVE_FILTER(motifs):
        relation_request <- BUILD_COMPONENT_RELATION_REQUEST(
                                motif, method_lineage)
        relation_call <- CALL_OPTIMIZER_LLM(
                             relation_request,
                             call_type=COMPONENT_RELATION_PROPOSAL)
        relation_proposal <- PARSE_COMPONENT_RELATION_PROPOSAL(
                                 relation_call)
        relation <- VERIFY_COMPONENT_RELATION(
                        relation_proposal, motif, method_lineage)
        replay <- CROSS_TASK_BIND_ACTIVATE_AND_REPLAY(
                      motif, eligible_transfer_cases)
        contribution <- PAIRED_MASK_WHEN_FEASIBLE(motif)
        if HARD_GATES_PASS(replay) and EVIDENCE_SUFFICIENT(contribution):
            doc_request <- BUILD_COMPONENT_DOCUMENTATION_REQUEST(
                               motif, replay, contribution)
            doc_call <- CALL_OPTIMIZER_LLM(
                            doc_request,
                            call_type=COMPONENT_DOCUMENTATION)
            docs <- PARSE_AND_VALIDATE_COMPONENT_DOCUMENTATION(
                        doc_call, motif, replay)
            if DOCUMENTATION_VALID(docs):
                method_lineage <- COMMIT_COMPONENT_REVISION(
                    method_lineage, motif, relation,
                    replay, contribution, docs)
            else:
                RECORD_DOCUMENTATION_REJECTION(motif, doc_call)
        else:
            failure_request <- BUILD_FAILED_TRANSFER_ATTRIBUTION_REQUEST(
                                   motif, replay, relation)
            failure_call <- CALL_OPTIMIZER_LLM(
                                failure_request,
                                call_type=FAILED_TRANSFER_ATTRIBUTION)
            failure_proposal <- PARSE_FAILED_TRANSFER_ATTRIBUTION(
                                    failure_call)
            failure <- VERIFY_TRANSFER_FAILURE_ATTRIBUTION(
                           failure_proposal, motif, replay)
            RECORD_FAILED_ABSTRACTION(motif, replay, failure)

    H_next_lineage, L_M_next <- ATOMIC_COMMIT_DUAL_LINEAGE(
                                    H_shadow, method_lineage)
    index <- REBUILD_RETRIEVAL_INDEX(L_M_next)
    return H_next_lineage, L_M_next, index
```


| 可以由设计保证 | 必须通过实验验证 |
| --- | --- |
| 方法图、具体实现、结构抽象和来源证据保持关联 | 结构检索是否提高候选成功率 |
| 类型、effect、权限和显式循环条件可以被确定性检查 | 渐增拓扑是否比自由代码搜索更有效 |
| innovation 记录与语义组件身份分开 | speciation 是否确实保护有价值结构 |
| 新组件经过来源任务回放后才进入组件谱系 | 跨任务抽象是否提升泛化并降低工作量 |
| 后续反例产生新 revision，不覆盖旧证据 | 学到的组件库是否长期优于手工库或无库基线 |

### 四阶段在多轮 Harness 演化中的完整流转

四个阶段共同完成训练集上的一次 Harness 版本更新。实验开始前只执行一次离线结构编译：`OptimizerLLM` 提出来源语义图映射，`OptimizerHarness` 核验并冻结 `StructureCatalogSnapshot`，同时封存 benchmark 测试集。在线 loop 从 $(H_0,L_0^H,L_0^M)$ 开始：$H_0$ 是未经本方法优化的初始 Harness，$L_0^H$ 只含该根版本，$L_0^M$ 可以包含其他训练任务已经验证的组件，但不包含当前 benchmark 测试证据。每轮先分配数据角色并运行父代；没有 $H_t$ 的新 trace，就不能直接复用上一轮需求生成候选。

第一阶段的离线组织不重复执行，在线检索则每轮执行。父代 trace 先被编译到程序图，`OptimizerLLM` 提出结构断点需求和 motif 语义比较，程序完成硬过滤与闭包。第二阶段通过结构诊断、知识补全、自由拓扑提案和反例修订形成冻结候选与结构义务。第三阶段由模型解释证据并提出判别 probe 与下一谱系动作，程序真实执行并决策：绑定反例返回第二阶段，缺少通用原语返回第一阶段的在线检索，结构尚未闭合则继续形成新 revision。所有返回都仍属于第 $t$ 轮，沿用同一父代和相同数据角色；凡 select case 经 LLM 披露后影响候选修订，立即失去对该候选及后代的独立判定资格。

只有第三阶段得到 `Promote`、`Reject` 或有充分证据的 `Tie`，第四阶段才将本轮原始证据写入 Harness 谱系并尝试抽象组件。`Promote` 令获胜候选成为 $H_{t+1}$；`Reject` 或 `Tie` 令 $H_{t+1}=H_t$。第四阶段提交 $L_{t+1}^H$ 与 $L_{t+1}^M$ 后，训练调度器更新每个案例已经承担的角色、结构缺口覆盖、旧能力 anchors 和待复核绑定反例。下一轮必须用 $H_{t+1}$ 在新分配的 $D_{t+1}^{\mathrm{trace}}$ 上重新运行，不能继承旧候选的收益统计。

```text
EVOLVE_TOPOLOGY_ON_BENCHMARK_TRAIN(
    H0, L_H0, L_M0, catalog_snapshot, D_train, train_protocol):

    scheduler <- INIT_TRAIN_SCHEDULER(D_train, train_protocol)
    llm_call_ledger <- INIT_LLM_CALL_LEDGER(train_protocol)
    H <- H0
    L_H <- L_H0
    L_M <- L_M0
    t <- 0

    loop:
        trace_pool, select_pool, anchor_pool, transfer_pool <-
            ASSIGN_TRAIN_ROLES(scheduler, H, L_H, L_M)

        trace_batch <- RUN_HARNESS(H, trace_pool, train_protocol)
        host_graph <- COMPILE_TYPED_EFFECT_GRAPH(H)
        need <- BUILD_STRUCTURAL_NEED(
                    H, host_graph, trace_batch,
                    PENDING_STRUCTURAL_EVIDENCE(L_H, L_M))
        reusable_view <- RETRIEVE_REUSABLE_COMPONENT_VIEW(
                             L_M, need, train_protocol)
        bundles <- ONLINE_RETRIEVE_MOTIFS(
                       catalog_snapshot, reusable_view, need,
                       TRACE_GRAPH_VIEW(host_graph, trace_batch))

        round_ledger <- LEDGER_FROM_TRACE_BATCH(trace_batch)
        binding_counterexamples <- CONFIRMED_BINDING_FAILURES(L_H, H)
        preservation_requirements <- BUILD_PRESERVATION_REQUIREMENTS(
                                         H, anchor_pool, L_H,
                                         train_protocol)
        hard_constraints <- COMPILE_TOPOLOGY_HARD_CONSTRAINTS(
                                H, need, bundles, train_protocol)

        repeat:
            candidates, obligations <- SYNTHESIZE_TOPOLOGY_CANDIDATES(
                H, trace_batch, need, bundles,
                binding_counterexamples,
                preservation_requirements, hard_constraints)

            decision, eval_ledger <- PLAN_AND_TEST_TOPOLOGY_EVOLUTION(
                H, candidates, obligations,
                select_pool, anchor_pool, L_H)
            APPEND(round_ledger, eval_ledger)
            UPDATE_EXPOSURE_FROM_LLM_CALLS(
                scheduler, llm_call_ledger, candidates,
                select_pool union anchor_pool)

            if decision is ReturnBindingCounterexample:
                cex <- CONFIRMED_BINDING_COUNTEREXAMPLE(eval_ledger)
                select_pool <- REFRESH_INDEPENDENT_SELECT_POOL(
                                   scheduler, candidates, select_pool)
                binding_counterexamples <-
                    binding_counterexamples union {cex}
                continue

            if decision is ReturnStructuralNeed:
                select_pool <- REFRESH_INDEPENDENT_SELECT_POOL(
                                   scheduler, candidates, select_pool)
                need <- REVISE_STRUCTURAL_NEED(need, eval_ledger)
                reusable_view <- RETRIEVE_REUSABLE_COMPONENT_VIEW(
                                     L_M, need, train_protocol)
                bundles <- ONLINE_RETRIEVE_MOTIFS(
                               catalog_snapshot, reusable_view, need,
                               TRACE_GRAPH_VIEW(host_graph, trace_batch))
                hard_constraints <- COMPILE_TOPOLOGY_HARD_CONSTRAINTS(
                                        H, need, bundles, train_protocol)
                continue
        until decision is Promote, Reject, or Tie

        L_H_next, L_M_next, component_index <-
            CONSOLIDATE_COMPONENT_LINEAGE(
                H, candidates, decision, L_H, L_M,
                round_ledger, transfer_pool)
        UPDATE_EXPOSURE_FROM_LLM_CALLS(
            scheduler, llm_call_ledger,
            COMPONENT_REVISIONS_CREATED(L_M, L_M_next),
            transfer_pool)
        H_next <- ACCEPT_IF_PROMOTED(H, candidates, decision)

        UPDATE_TRAIN_SCHEDULER(
            scheduler, trace_pool, select_pool, anchor_pool,
            transfer_pool, decision, round_ledger,
            L_H_next, L_M_next)

        if TOPOLOGY_TRAIN_FIXED_POINT(
               scheduler, H, H_next, L_H, L_H_next,
               L_M, L_M_next, round_ledger):
            break

        H <- H_next
        L_H <- L_H_next
        L_M <- L_M_next
        t <- t + 1

    return FREEZE_TOPOLOGY_SYSTEM_FOR_FINAL_TEST(
               H_next, L_H_next, L_M_next,
               catalog_snapshot, train_protocol)
```

`TOPOLOGY_TRAIN_FIXED_POINT` 只在训练调度器完成一个覆盖全部预定任务族和关键结构缺口的轮换后检查。stop 必须同时满足：本轮换没有候选达到 `Promote`；不存在尚未闭合但仍有合法补全动作的 `StructuralObligation`；所有候选已经 `Reject` 或形成证据充分的 `Tie`；最近一次 `STALLED_LINEAGE_REFLECTION` 没有产生通过核验的新原语需求、替代拓扑、修订分支或判别 probe；没有新绑定反例、组件 revision、失败抽象或结构需求会改变下一轮检索与变异空间；也不存在仍可能改变父子选择的合法配对运行。外部服务失败、预算意外中断、证据缺失、索引提交失败或 `UNKNOWN` 义务都不是 stop。

stop 后冻结最终 Harness、两条谱系、目录快照、检索器、执行模型、工具环境、评测器和随机协议，随后才按照 benchmark 官方协议在 $D_{\mathrm{test}}$ 上运行。测试阶段不再运行 `OptimizerHarness` 或调用 `OptimizerLLM`，不产生新结构、不提交组件 revision，也不把测试 trace 反馈到训练调度器或任一检索索引；测试结果只用于最终报告和与 baseline 比较。

## 二、字段、公式与参数完整定义

### 类型与图约定

| 概念 | 规范 |
| --- | --- |
| 程序图 | 有向多重图；节点是组件实例，边按 `data/state/order/effect` 分层保存，同一对节点可以有多类边。 |
| 类型 | `typed_inputs/outputs` 使用名义类型、结构类型和可空性；`UNKNOWN` 不自动兼容任何具体类型。 |
| effect | 至少区分状态读、状态写、外部调用、权限使用、资源消耗、异常和补偿；effect 集合参与硬兼容检查。 |
| 图等价 | 只有在类型、effect、必要顺序、可观测 trace 和指定测试上等价时才允许归并；文本或 AST 相似不构成等价。 |
| 版本 | 每次结构变异产生冻结子图和新的 `innovation_id`；父图保持不变。 |
| 未知关系 | 无法证明的 rewrite、绑定或 effect 关系标为 `unverified_relation`，不能进入硬等价类。 |

### 数据字段规范

#### Benchmark 数据角色与轮次边界

| 符号 | 类型 | 精确定义 |
| --- | --- | --- |
| $D_{\mathrm{train}}$ | 固定任务集合 | benchmark 官方训练集；在线演化、组件抽象和调度器唯一允许访问的 benchmark 任务全集。若官方没有训练集，必须在实验前公开定义开发集，不能从测试集回填。 |
| $D_{\mathrm{test}}$ | 封闭任务集合 | 只在训练 loop stop 且所有系统状态冻结后运行；其输入、标签、trace 和结果不得进入检索、候选生成、谱系更新或 stop 判断。 |
| $D_t^{\mathrm{trace}}$ | 训练子集 | 第 $t$ 轮的故障发现集合，用当前父代 $H_t$ 运行并生成结构诊断 trace。 |
| $D_t^{\mathrm{select}}$ | 训练子集 | 候选冻结前不得进入 `OptimizerHarness` 构造的生成上下文，也不得向 `OptimizerLLM` 披露的父子判定集合，用于估计候选相对父代的新收益。 |
| $D_t^{\mathrm{anchor}}$ | 训练子集 | 旧能力、接口、安全与严重失败的回放集合，用于检测结构回归。 |
| $D_t^{\mathrm{transfer}}$ | 训练子集或批准的外部训练任务 | 没有参与待抽象 motif 形成的独立 transfer cases，用于验证组件能否在新绑定中激活；不得包含测试实例。 |
| $D_{dev}^{(t)}$ | 派生集合 | $D_t^{\mathrm{select}}\cup D_t^{\mathrm{anchor}}$；只供第三阶段的候选判断使用。 |

同一轮要求 $D_t^{\mathrm{trace}}$、$D_t^{\mathrm{select}}$ 和 $D_t^{\mathrm{anchor}}$ 两两不相交。$D_t^{\mathrm{transfer}}$ 可以与更早轮次的训练任务重叠，但不能包含产生当前待抽象结构的运行；每个任务的角色历史由 `ExposureRecord` 审计。

#### `TrainProtocol`

| 字段 | 精确定义 |
| --- | --- |
| `benchmark_revision` | benchmark 名称、任务 revision 和评测协议版本。 |
| `split_revision` | 训练/测试任务 ID 清单及其来源；冻结后不可移动任务。 |
| `task_strata` | 供轮换覆盖的任务族、能力族、长度、工具或环境分层。 |
| `role_assignment_rule` | 如何从训练集分配 trace、select、anchor、transfer 角色及冷却期。 |
| `reuse_policy` | 组件视图允许读取的 `as_of`、最大 scope、regime、陈旧度与跨任务证据门；实验中不可追随结果改写。 |
| `execution_config` | 执行模型、采样参数、上下文限制、工具、容器、网络、资源和超时。 |
| `optimizer_harness_revision` | 结构目录编译与检索、trace 图编译、补全请求构造、Candidate IR 解析、CEGIS、拓扑规划、谱系巩固和调用账本组件的联合代码与配置版本。 |
| `optimizer_llm_config` | `OptimizerLLMConfig`；固定 `OptimizerLLM` 在来源图对齐、结构需求解释、检索重排、trace 图诊断、拓扑生成与修订、测评解释与规划、组件抽象和文档生成中的模型与调用边界。 |
| `evaluator_revision` | grader、指标方向、失败编码、聚合和并列规则。 |
| `seeds` | 父子成对运行、机制 probe 与重复实验允许使用的固定种子集合。 |
| `promotion_rule` | `Promote/Reject/Tie` 的收益、回归、结构 gate 和证据充分性边界。 |
| `stop_rule` | 完整训练轮换、未决结构义务、检索空间变化和可执行实验共同决定的固定点规则。 |

#### `OptimizationAgent`

本方法中的 `OptimizationAgent` 定义为：

$$
\text{OptimizationAgent}=\text{OptimizerLLM}+\text{OptimizerHarness}.
$$

公式中的加号表示二者共同组成一个可运行系统，不表示数值相加。`OptimizerLLM` 是贯穿来源结构理解、trace 图诊断、motif 语义比较、拓扑设计、证据解释、谱系动作规划和组件抽象的认知核心；`OptimizerHarness` 是把外部方法与目标 Harness 编译为程序图、构造最小权限视图、解析并约束提案、执行类型/effect 分析、CEGIS 和拓扑测评、维护调用账本、双谱系与数据隔离的外部程序。`OptimizerLLM` 负责提出难以规则化的结构语义，`OptimizerHarness` 负责证明其结构合法并用真实运行决定是否采用。

`OptimizerHarness` 在本方法中由以下组件构成：

| 组件 | 本方法中的职责 | 是否调用 `OptimizerLLM` |
| --- | --- | --- |
| `structure_catalog_compiler_and_retriever` | 固定来源锚点，核验语义图映射，编译来源图，挖掘并冻结 motif；形成 `StructuralNeed`，执行多视图召回、硬过滤、依赖闭包和排序融合。 | 发起 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT`、`TRACE_TO_STRUCTURAL_NEED`、`SEMANTIC_MOTIF_BUNDLE_RERANK`。 |
| `trace_graph_compiler_and_localizer` | 把父 Harness 与训练 trace 编译到类型/effect 图，形成对比切片、产品抽象域，核验结构因果链。 | 发起 `TRACE_GRAPH_DIAGNOSIS`。 |
| `topology_context_builder` | 从父图、局部切片、结构草图、合法绑定和披露策略构造知识通道与自由通道输入视图。 | 分别发起 `KNOWLEDGE_TOPOLOGY_COMPLETION` 和 `FREE_TOPOLOGY_PROPOSAL`。 |
| `candidate_parser_and_constraint_engine` | 将两类原始输出解析为共同 Candidate IR，执行类型、状态、effect、权限、顺序与有界循环检查。 | 否。 |
| `cegis_and_local_graph_repair` | 运行有界 trace CEGIS，确认绑定反例，把语义修订提案编译为六类最小动作并生成新 revision。 | 发起 `COUNTEREXAMPLE_TO_GRAPH_REVISION`。 |
| `lineage_planner_and_evaluator` | 管理结构物种、义务、mutant、父子配对与回归证据，核验证据解释和动作提案并依据冻结规则决策。 | 发起 `MUTANT_AND_PROBE_PROPOSAL`、`TOPOLOGY_EVIDENCE_INTERPRETATION`、`NEXT_LINEAGE_ACTION_PROPOSAL`、`STALLED_LINEAGE_REFLECTION`。 |
| `component_lineage_consolidator` | 核验可复用边界与组件关系，执行跨任务绑定、激活、mask 与硬门，归因失败并提交双谱系和索引。 | 发起 `SEMANTIC_COMPONENT_ABSTRACTION`、`COMPONENT_RELATION_PROPOSAL`、`FAILED_TRANSFER_ATTRIBUTION`、`COMPONENT_DOCUMENTATION`。 |
| `llm_call_ledger` | 追加保存全部调用的实际输入视图、原始输出、解析状态、验证状态和资源消耗。 | 不产生调用，只记录调用。 |

被优化的执行 agent 由当前执行模型与 $H_t$ 组成，负责在 benchmark 任务上产生 `ExecutionTrace`。`OptimizerHarness` 根据数据角色和程序图为每种 call type 构造允许披露的局部视图，`OptimizerLLM` 返回结构化提案，随后仍由 `OptimizerHarness` 解析、核验、执行和记录。即使 `OptimizerLLM` 与执行模型使用同一基础模型，也必须隔离会话、上下文、工具权限与调用账本。

#### `OptimizerLLMConfig`

| 字段 | 精确定义 |
| --- | --- |
| `provider_model_revision` | provider、模型名称、不可变 revision 或可审计快照。 |
| `call_types` | 只允许 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT`、`TRACE_TO_STRUCTURAL_NEED`、`SEMANTIC_MOTIF_BUNDLE_RERANK`、`TRACE_GRAPH_DIAGNOSIS`、`KNOWLEDGE_TOPOLOGY_COMPLETION`、`FREE_TOPOLOGY_PROPOSAL`、`COUNTEREXAMPLE_TO_GRAPH_REVISION`、`MUTANT_AND_PROBE_PROPOSAL`、`TOPOLOGY_EVIDENCE_INTERPRETATION`、`NEXT_LINEAGE_ACTION_PROPOSAL`、`STALLED_LINEAGE_REFLECTION`、`SEMANTIC_COMPONENT_ABSTRACTION`、`COMPONENT_RELATION_PROPOSAL`、`FAILED_TRANSFER_ATTRIBUTION`、`COMPONENT_DOCUMENTATION`。 |
| `decoding_by_call_type` | 每类调用的 temperature、top-p、最大输出、停止条件、推理强度、种子策略和候选数量。 |
| `prompt_template_revisions` | 每类请求的系统指令、输入序列化和输出 schema 版本。 |
| `context_policies` | 每类请求允许披露的图、trace、motif、代码和证据字段；未列字段默认禁止。 |
| `tool_policy` | 允许读取的父代码与局部分析工具；禁止读取 select/test 数据、直接修改父版本、写入谱系或绕过检查器。 |
| `retry_policy` | 超时、格式错误和工具失败的最大重试数及退避规则；每次重试创建新调用记录。 |
| `parser_revision` | 每种 call type 的固定解析器版本；解析器只能提取或拒绝字段，不能补写模型未输出的结构语义。 |

#### `LLMCallRecord`

| 字段 | 精确定义 |
| --- | --- |
| `call_id` | 一次 `OptimizerLLM` 请求的唯一 ID；重试使用新 ID。 |
| `round_id` | 在线调用所属的外层 Harness 演化轮次；离线 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT` 使用 `OFFLINE:<catalog_revision>`。 |
| `call_type` | `OptimizerLLMConfig.call_types` 中的一种，决定输入披露、输出 schema 和核验器。 |
| `model_revision` | 实际响应请求的 `OptimizerLLM` revision。 |
| `prompt_template_revision` | 本次调用所用模板与输出 schema revision。 |
| `input_view_revision` | `OptimizerHarness` 构造的最小权限输入视图 revision。 |
| `disclosed_object_ids` | 实际披露的父图切片、草图、motif、trace 片段、反例或组件证据 ID。 |
| `forbidden_object_check` | `PASS/FAIL`；请求前检查 select/test、隐藏标签、未来 revision 和越权代码路径，`FAIL` 时不得发起调用。 |
| `tool_session_id` | 隔离工具会话 ID 或 `NONE`；记录实际读取、编辑、分析和测试权限。 |
| `seed` | 实际生成种子或 `UNCONTROLLED`。 |
| `raw_output_ref` | `OptimizerLLM` 原始输出的不可变存储位置。 |
| `parsed_output_ids` | 解析得到的 `OptimizerProposal`、Candidate IR、关系提案或文档草稿 ID；解析失败时为空。 |
| `validation_status` | `PENDING/PARSE_FAILED/ANCHOR_REJECTED/GATE_REJECTED/RULE_REJECTED/EVIDENCE_REJECTED/DOC_REJECTED/ACCEPTED_AS_PROPOSAL`；不等同于候选晋级或组件提交。 |
| `parent_call_id` | 格式修复或受控重试引用的前一调用；首次调用为 `NONE`。 |
| `usage` | 输入/输出 token、费用、时延和工具调用数，仅用于复现与成本统计。 |

`CALL_OPTIMIZER_LLM` 在请求开始前先创建 `call_id`，并把请求、响应、解析和核验状态原子追加到当前实验的 `LLMCallLedger`；因此成功、超时、解析失败和检查拒绝都不会从审计链中消失。全部 `LLMCallRecord` 按调用开始顺序保存。结构需求、候选、义务解释、谱系动作、组件 revision 和文档都通过 `call_id` 或 `llm_call_ids` 回指产生它们的调用；`OptimizerLLM` 的自述不作为结构或效果证据。

#### `OptimizerProposal`

除直接解析为 Candidate IR 的两类代码生成调用外，`OptimizerLLM` 输出先进入统一提案外壳：

| 字段 | 精确定义 |
| --- | --- |
| `proposal_id` | 一项不可变提案的唯一 ID；同一调用返回多项时分别编号。 |
| `call_id` | 产生该提案的 `LLMCallRecord`。 |
| `proposal_type` | 与调用的 `call_type` 一致；不一致时解析失败。 |
| `target_ids` | 被解释、比较、修改或抽象的来源单元、图、trace、候选、义务、动作或组件 revision。 |
| `payload` | 由下表规定的 call-specific 结构；缺少必填字段时不能进入核验。 |
| `evidence_anchors` | 每个关键字段引用的论文段落、代码符号、图节点/边、trace 事件、谱系事件或组件 revision。 |
| `counterevidence` | 与提案冲突或限制其适用性的锚点；没有时为空列表而非省略。 |
| `uncertainties` | 披露视图无法判断的前提、替代解释和所需观察。 |
| `expected_observations` | 提案正确或错误时应出现的可执行事件谓词；纯来源抽取允许为 `NOT_APPLICABLE`。 |
| `validation_status` | `PENDING/ACCEPTED/REJECTED/PARTIALLY_ACCEPTED`，只由 `OptimizerHarness` 写入。 |

| call type | `payload` 必填字段 | 字段含义 |
| --- | --- | --- |
| `SOURCE_GRAPH_SEMANTIC_ALIGNMENT` | `{algorithm_units, code_subgraphs, node_roles, contract_fields, boundary_candidates, relation_candidates}` | `algorithm_units` 是来源算法的不可再拆步骤；`code_subgraphs` 是候选实现节点/边；`node_roles` 是每个节点的单一语义职责；`contract_fields` 是输入、输出、前置条件、effect、verifier 与 compensation；`boundary_candidates` 是可能的固定结构与开放端口；`relation_candidates` 是步骤、代码、测试和其他组件之间的候选关系。 |
| `TRACE_TO_STRUCTURAL_NEED` | `{competing_break_hypotheses, earliest_divergences, desired_capability, required_transformations, available_state, required_state, effect_constraints, unresolved_requirements, query_plan}` | `competing_break_hypotheses` 是可反驳的结构故障解释；`earliest_divergences` 是失败相对成功路径的最早图/状态偏离；其余字段分别给出目标行为、保序变换、现有/所需端口状态、允许/禁止 effect、待取证条件和多视图查询计划。 |
| `SEMANTIC_MOTIF_BUNDLE_RERANK` | `{bundle_order, mechanism_matches, migration_gaps, complementarities, refutation_tests}` | 依次表示仅对输入 bundle 的序位、motif 到结构断点的逐步对应、目标宿主缺少的绑定、束内互补机制和能推翻匹配的可执行观察。 |
| `TRACE_GRAPH_DIAGNOSIS` | `{earliest_structural_divergence, causal_graph_path, candidate_root_break, alternative_breaks, discriminating_probes}` | 依次表示最早偏离节点/边、到最终失败的事件—状态—图路径、候选根断点、竞争解释和最小判别实验。 |
| `COUNTEREXAMPLE_TO_GRAPH_REVISION` | `{failure_class, affected_nodes_edges, repair_kind, target_locations, preserved_structure, expected_trace_change, required_rechecks}` | `repair_kind` 只取六类绑定修复；其余字段限定反例类别、目标子图、不可改变机制、修订后观察和必须重跑的检查。 |
| `MUTANT_AND_PROBE_PROPOSAL` | `{target_claim, mutant_edit, preserved_conditions, probe_input, expected_difference, stop_rule}` | 描述要击穿的结构声明、单一破坏编辑、必须保持条件、probe、原候选与 mutant 的预期差异和终止规则。 |
| `TOPOLOGY_EVIDENCE_INTERPRETATION` | `{supported_obligations, refuted_obligations, unknown_obligations, activation_assessment, alternative_explanations, next_observations}` | 将真实证据映射到义务与激活状态；未知项和替代解释不得省略，模型概率不进入晋级统计。 |
| `NEXT_LINEAGE_ACTION_PROPOSAL` | `{action_kind, target_obligation, executable_parameters, expected_observation, stop_condition}` | 描述合法谱系动作、所解决义务、完整执行参数、判别观察和停止条件。 |
| `STALLED_LINEAGE_REFLECTION` | `{stagnation_cause, missing_primitives, alternative_topology, assumption_revision, discriminating_action}` | 描述停滞原因、缺失原语需求、替代结构、需收紧假设和最小判别动作。 |
| `SEMANTIC_COMPONENT_ABSTRACTION` | `{fixed_mechanism, open_ports, host_adapters, nonparameterizable_parts, boundary_counterexamples}` | 分别描述可复用固定子图、参数化接口、宿主特定绑定、必须留在具体 variant 的部分和击穿抽象边界的反例。 |
| `COMPONENT_RELATION_PROPOSAL` | `{left_revision, right_revision, proposed_relation, field_evidence, scope_regime_conditions}` | 比较新旧组件并提出 `SAME/REFINES/ALTERNATIVE/CONFLICTS/COMPOSES/UNRESOLVED`，逐字段给出结构、契约、scope 与 regime 依据。 |
| `FAILED_TRANSFER_ATTRIBUTION` | `{attribution_hypotheses, distinguishing_evidence, affected_scope, remediation_destination}` | 在端口、宿主 effect、adapter、regime、抽象过宽和随机失败之间提出竞争归因，并指定继续取证、分裂组件、退回 variant 或修订 adapter。 |
| `COMPONENT_DOCUMENTATION` | `{distinctive_name, mechanism, interface, applicability, executable_examples, limitations, failed_bindings}` | 仅总结已提交证据允许的名称、机制、接口、适用条件、可执行示例、限制与失败绑定；不能创建新的结构主张。 |

`KNOWLEDGE_TOPOLOGY_COMPLETION` 与 `FREE_TOPOLOGY_PROPOSAL` 直接解析为共同 Candidate IR，所有其他 call type 均先解析为 `OptimizerProposal` 再进入对应核验器。

#### `ExposureRecord`

| 字段 | 精确定义 |
| --- | --- |
| `task_id` | 训练任务的稳定 ID。 |
| `round_id` | 该次暴露所属的外层演化轮次。 |
| `split_role` | `trace/select/anchor/transfer` 之一。 |
| `visible_to_generation_path_before_freeze` | 候选冻结前，该任务、标签或 trace 是否进入过 `OptimizerHarness` 构造的生成输入或向 `OptimizerLLM` 披露。 |
| `disclosed_fields` | 实际向 `OptimizerLLM` 披露的输入、标签、trace、指标、图切片和评测反馈字段。 |
| `disclosed_to_call_ids` | 接收上述字段的全部 `LLMCallRecord`；未实际发起的请求不记录。 |
| `affected_candidate_ids` | 直接或间接使用这些调用输出生成、修订拓扑或选择后续动作的候选及其后代。 |
| `affected_component_revision_ids` | 使用这些调用输出形成边界、关系、失败归因或文档的组件 revision；未通过提交门的抽象记录其失败记录 ID。 |
| `independence_status` | 对每个受影响候选或组件 revision 取 `INDEPENDENT/EXPOSED/NOT_APPLICABLE`；一旦披露结果影响候选修订或组件形成，对相应对象及后代永久为 `EXPOSED`。 |
| `harness_versions` | 在该角色下运行的父代或候选版本。 |
| `run_ids` | 对应 `ExecutionTrace.run_id` 列表。 |
| `evidence_uses` | `diagnosis/binding/gate/selection/regression/abstraction` 中实际承担的用途；一次运行不能同时被声明为生成证据和独立选择证据。 |

#### `ExecutionTrace`

| 字段 | 精确定义 |
| --- | --- |
| `run_id` | 一次不可变真实执行的唯一 ID。 |
| `task_id` | 输入任务 ID，必须能连接到 `ExposureRecord`。 |
| `split_role` | 本次运行在当前轮次中的数据角色。 |
| `harness_version` | 执行的冻结 Harness revision。 |
| `model_tool_environment_versions` | 模型、采样配置、工具 schema、容器、依赖和评测器版本。 |
| `seed` | 控制模型采样、环境随机性和调度随机性的实际种子；不支持的随机源标为 `UNCONTROLLED`。 |
| `ordered_component_events` | 按真实时间排序的组件、控制、工具和异常事件；每项含事件 ID、节点/边映射、输入输出指针、状态前后版本和父事件。 |
| `state_and_artifact_versions` | 被读取或写入的记忆、文件、缓存、会话、凭据和外部资源版本链。 |
| `final_output` | 执行 agent 最终可评分输出或终止状态。 |
| `metric_vector` | grader 返回的全部指标及方向，不预先压缩成单分数。 |
| `failure_signature` | 规范化失败阶段、异常/错误类别、未满足后置条件和最早可观测偏离；成功时为 `NONE`。 |
| `replay_artifacts` | 重放所需的输入、配置、环境指针和允许缓存的工具响应；不能重放时说明原因。 |

#### `StructureCatalogSnapshot`

| 字段 | 精确定义 |
| --- | --- |
| `catalog_revision` | 本次实验固定引用的目录 revision。 |
| `source_packet_ids` | 被离线编译的全部 `SourcePacket` ID。 |
| `method_graph_variants` | 从来源恢复的具体 `MethodGraphVariant`，不被 motif 抽象覆盖。 |
| `graph_motifs` | 通过结构挖掘和受限等价归并形成的 `GraphMotif` 集合。 |
| `validated_rewrite_rules` | 每条带适用条件、验证类型和证据指针的结构 rewrite。 |
| `indexes` | 由本快照重建的文本、类型、effect、结构和依赖索引。 |
| `compiler_config` | 来源对齐/图抽取规则、`SOURCE_GRAPH_SEMANTIC_ALIGNMENT` 提示与 parser revision、锚点/契约核验器、图规范化、挖掘界限和索引配置；改变任一项均产生新 revision。 |
| `semantic_alignment_call_ids` | 离线组织期间全部语义图对齐调用，包括解析或核验失败记录。 |
| `frozen_at` | 快照冻结时间；只用于审计，不参与排序。 |

#### `ReusableComponentView`

| 字段 | 精确定义 |
| --- | --- |
| `query_need_id` | 产生该视图的当前 `StructuralNeed` ID；不存在脱离查询的通用视图。 |
| `component_revisions` | 从 $L_t^M$ 中通过 scope、regime、类型、effect 和权限过滤的组件 revision。 |
| `known_adapters` | 与当前 Harness family 匹配的 adapter revision 及验证状态。 |
| `failed_bindings` | 与当前端口、宿主或环境相关的失败绑定和反例。 |
| `migration_evidence` | 历史绑定编辑、机制激活、修复次数、收益与回归证据。 |
| `as_of` | 查询允许看到的证据截止时间，防止读取未来 revision。 |
| `scope_ceiling` | 本次查询允许复用的最大任务、Harness、模型和工具范围。 |
| `regime_filter` | 允许进入视图的环境与证据 regime；不匹配项只可作为反例背景，不参与效果合并。 |

#### `SourcePacket`

| 字段 | 类型 | 定义 |
| --- | --- | --- |
| `source_packet_id` | 稳定 ID | 该固定论文—代码来源包的身份；内容或来源 revision 变化时创建新 ID，不覆盖旧包。 |
| `paper_version` | 固定版本对象 | 论文元数据、本地 PDF 与文本路径。 |
| `official_code_version` | 固定代码对象 | 仓库、revision、范围、获取日期和许可证。 |
| `exact_source_anchors` | 锚点列表 | 机制、图结构、类型和限制对应的论文及代码位置。 |
| `configs_and_examples` | 记录列表 | 官方配置、输入输出、依赖和运行条件。 |
| `tests_and_reported_results` | 记录列表 | 测试、指标、结果、消融、失败条件与复核状态。 |

#### `ComponentContract`

| 字段 | 类型与约束 | 精确定义 |
| --- | --- | --- |
| `component_id` | 稳定 ID，必填 | 一个语义组件的身份；实现变体另设实例 ID，不改变此 ID。 |
| `semantic_role` | 枚举/受控词表 | 组件在 Harness 中的职责，例如路由、记忆写入、工具验证、回退；一项只描述一个主职责。 |
| `typed_inputs` | 端口映射 | 输入端口名到类型、可空性、所有权和前置验证的映射。 |
| `typed_outputs` | 端口映射 | 输出端口名到类型、成功/失败分支和后置条件的映射。 |
| `preconditions` | 谓词列表 | 执行节点前必须成立的状态、权限和资源条件。 |
| `effects` | effect 列表 | 节点可能产生的状态读写、调用、异常、成本和控制转移；区分 must/may effect。 |
| `trace_events` | 事件契约 | 正常、失败和旁路时必须发出的事件名、字段、关联 ID 与顺序。 |
| `verifier` | 可执行检查 | 验证输出和 effect 是否满足契约的函数、测试或属性；返回 `PASS/FAIL/UNKNOWN`。 |
| `compensation` | 可执行动作或 `NOT_AVAILABLE` | 部分执行失败后恢复状态或回退父行为的操作，说明幂等性。 |
| `authority_and_resources` | 约束对象 | 所需权限、文件/网络边界、模型调用、token、时延和并发资源上限。 |
| `source_anchors` | 锚点列表 | 每个契约字段的证据来源。 |
| `semantic_alignment_call_ids` | 调用 ID 列表 | 提出或修订该契约语义字段的 `SOURCE_GRAPH_SEMANTIC_ALIGNMENT` 调用。 |
| `field_validation_status` | 字段到状态映射 | 每个语义字段取 `ANCHORED/STATICALLY_VERIFIED/EXECUTION_VERIFIED/UNKNOWN/REJECTED`；只有前三类可作为结构事实。 |

#### `MethodGraphVariant`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `nodes` | `ComponentContract[]` | 一个具体方法实现所需的组件节点；节点实例拥有唯一实例 ID。 |
| `data_edges` | 有向边列表 | `(producer.port, consumer.port, schema_mapping)`；必须类型兼容。 |
| `state_edges` | 有向边列表 | `(writer, state_key, reader, version_rule)`；明确读写集合和一致性要求。 |
| `order_edges` | 偏序边列表 | 必须发生在前的关系；闭包必须无环，循环只允许位于 `bounded_loop_regions`。 |
| `effect_conflicts` | 冲突列表 | 并发或顺序组合时产生的 effect 冲突、严重度和可用补偿。 |
| `bounded_loop_regions` | 循环对象列表 | 循环入口、出口、不变量、最大迭代/时间、进展条件和超时行为。 |
| `method_preconditions` | 谓词列表 | 整个方法图可接入的条件，区别于单节点前提。 |
| `expected_observations` | trace 谓词列表 | 接入后应观测到的路径、状态或输出变化。 |
| `execution_evidence` | 证据指针列表 | 原实现或本地运行中实际走过该图的记录。 |
| `source_packet` | 来源包 ID | 该变体对应的固定来源包。 |

#### `GraphMotif`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `motif_id` | 稳定 ID | 一组结构等价变体的身份。 |
| `fixed_structure` | 子图 | 所有合法变体必须保留的节点、边、控制关系和 effect。 |
| `typed_open_ports` | 开口端口列表 | 允许宿主或其他 motif 绑定的输入、输出和状态端口，含类型变量及约束。 |
| `required_effects` | effect 集合 | motif 完成语义必须产生的 effect。 |
| `forbidden_compositions` | 组合谓词 | 明确禁止的邻接组件、effect、顺序、循环或权限组合。 |
| `concrete_variants` | 变体 ID 列表 | 支撑抽象的具体方法图，至少保存一个可执行变体。 |
| `validated_rewrites` | rewrite 列表 | 已证明或实测保持契约的结构改写；每条含适用条件和验证证据。 |
| `support_and_counterevidence` | 证据对象 | 支持、失败绑定、反例和未解决边界。 |

#### `StructuralNeed`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `need_id` | 唯一 ID | 当前父 Harness、外层轮次和 revision 绑定的需求身份；反例修订产生新 revision。 |
| `source_call_id` | 调用 ID | 产生当前需求 revision 的 `TRACE_TO_STRUCTURAL_NEED` 调用。 |
| `competing_break_hypotheses` | 假设列表 | 对同一失败的多个可反驳结构解释；每项含图/trace 锚点、相反证据、未知条件和判别观察。 |
| `desired_capability` | 能力谓词 | 目标图应实现的可观测行为。 |
| `required_transformations` | 变换序列 | 输入状态到输出状态必须完成的语义变换，保留必要顺序。 |
| `available_inputs_and_state` | 端口/状态映射 | 宿主现有可读数据、类型、所有权和生命周期。 |
| `required_outputs_and_state` | 端口/状态映射 | 候选必须产生的数据、状态版本和错误分支。 |
| `allowed_effects` | effect 白名单 | 候选可以产生的副作用及上限。 |
| `forbidden_effects` | effect 黑名单 | 一旦出现即拒绝候选的副作用。 |
| `authority_and_environment` | 环境契约 | 可用权限、工具、模型、容器、网络和资源。 |
| `unresolved_requirements` | 未知列表 | 无法判断的接口或 effect；每项附取证方式。 |
| `query_plan` | 多视图查询计划 | 文本、端口/effect、结构、依赖与反例查询的字段、优先级和停止条件；不能覆盖硬过滤。 |

#### `EvolutionInput`

| 字段 | 定义 |
| --- | --- |
| `frozen_parent_harness` | 代码、配置、依赖和程序图均冻结的父版本。 |
| `trace_batch` | 仅来自当前 $D_t^{\mathrm{trace}}$ 的同协议成功与失败 `ExecutionTrace[]`，保留任务、种子、环境和图事件关联。 |
| `structural_need` | 由当前父图、trace 对照和已有结构证据产生的 `StructuralNeed`；不能由候选选择任务反向补写。 |
| `retrieved_motif_bundles` | 已做依赖闭包和冲突标注的 motif 束。 |
| `binding_counterexamples` | 已确认的端口、类型、effect、权限、状态版本或生命周期绑定反例。 |
| `preservation_requirements` | 旧能力、接口、安全和性能必须保持的谓词。 |
| `hard_constraints` | 任一违反便淘汰候选的限制。 |

#### `CandidateIR`

两条拓扑生成通道先解析为相同的待核验中间表示：

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `ir_id` | 唯一 ID | 一次成功解析得到的不可变 IR；解析失败不创建。 |
| `source_channel` | `KNOWLEDGE/FREE` | 只用于审计与消融，不参与阶段三候选优先级。 |
| `parent_id` | Harness 版本 ID | 图差分和补丁必须应用的冻结父版本。 |
| `candidate_graph_delta` | 节点/边编辑列表 | 新增、删除、替换、启停及 region 修改，逐项带父图定位。 |
| `code_patch` | 可重放补丁 | 实现图差分的精确代码与配置编辑。 |
| `motif_sources` | motif/revision 列表 | 知识通道采用的来源 motif；自由通道无对应来源时为空，不伪造映射。 |
| `structural_edits` | 编辑序列 | 每项属于允许的结构编辑枚举并声明前置条件、目标位置和预期 effect。 |
| `port_bindings` | 绑定映射 | 开放端口到宿主端口、adapter、类型代换、所有权和生命周期的映射。 |
| `expected_trace_contract` | 事件谓词 | 结构接入、激活、旁路和失败时应出现的路径、状态与事件。 |
| `preservation_requirements` | 谓词列表 | 必须保留的旧能力、接口、安全、补偿和终止行为。 |
| `unresolved_assumptions` | 未知列表 | 尚未确认的接口、effect、顺序、scope 或激活条件及其取证动作。 |
| `diagnostic_call_ids` | 调用 ID 列表 | 候选依赖的结构诊断与反例修订调用。 |
| `llm_call_ids` | 调用 ID 列表 | 直接生成或修订该 IR 的全部调用，不只保留最后一次。 |

#### `CandidateVersion`

| 字段 | 类型 | 精确定义 |
| --- | --- | --- |
| `candidate_id` | 唯一 ID | 冻结子版本身份。 |
| `ir_id` | `CandidateIR` ID | 该冻结版本对应的共同中间表示。 |
| `parent_id` | 版本 ID | 唯一直接父 Harness。多父 crossover 另在 lineage 边记录。 |
| `candidate_graph` | 程序图快照 | 应用结构编辑后的完整类型/effect 图。 |
| `code_patch` | 可重放补丁 | 从父版本到子版本的精确文件差异。 |
| `motif_sources` | motif/revision 列表 | 候选实例化或改写过的 motif。 |
| `structural_edits` | 编辑序列 | 每步为 `SUBSTITUTE_NODE`、`SPLIT_EDGE`、`INSERT_MOTIF`、`ADD_GUARDED_BRANCH` 或 `SPECIALIZE_CONTROL`，含前后图定位。 |
| `port_bindings` | 绑定映射 | 开口端口到宿主端口、adapter 和类型代换。 |
| `expected_trace_contract` | 事件谓词 | 结构正确接入时应出现的路径与事件。 |
| `preservation_requirements` | 谓词列表 | 该候选冻结时绑定的旧能力、接口、安全、补偿与终止保持条件。 |
| `unresolved_assumptions` | 未知列表 | 尚未验证但会影响候选有效性的假设；不得为空来表示已解决。 |
| `hard_gate_status` | 检查到状态映射 | 编译、类型、state/effect、权限、顺序、循环、补偿、数据隔离和父接口检查各自取 `PASS/FAIL/UNKNOWN`。 |
| `revision` | 正整数 | 同一候选谱系上的版本；任何 LLM 或程序修订都产生新 `candidate_id`。 |
| `frozen_at` | 时间戳 | 开始机制或收益评测前的冻结时间，之后不得原地修改。 |
| `llm_call_ids` | 调用 ID 列表 | 产生诊断、补全、自由拓扑或反例修订语义内容的全部调用；纯程序构造时为空。 |

#### `StructuralObligation`

| 字段 | 精确定义 |
| --- | --- |
| `obligation_id` | 与候选 revision 绑定的唯一 ID。 |
| `candidate_id` | 义务所属的冻结候选。 |
| `kind` | `OPEN_PORT/MISSING_PREREQUISITE/MISSING_EFFECT/MISSING_PROBE/MISSING_COMPENSATION/UNBOUNDED_LOOP/UNRESOLVED_ORDER` 之一。 |
| `target_subgraph` | 产生义务的节点、边、region 和源码位置。 |
| `satisfaction_predicate` | 判定义务完成的可执行类型、状态、effect、trace 或终止谓词。 |
| `allowed_actions` | 能处理该义务的最小结构编辑或 probe 集合。 |
| `review_boundary` | 触发重新审查结构保护的证据条件，例如规定的 probe 已完成或完整任务族轮换结束；它不是固定消耗额度，也不能单独使候选失败。 |
| `evidence_ids` | 支持义务已完成、被反驳或仍未知的 ledger 事件。 |
| `interpretation_call_ids` | 调用 ID 列表 | 对该义务状态产生语义解释的 `TOPOLOGY_EVIDENCE_INTERPRETATION` 调用；最终状态仍由程序依据事件写入。 |
| `status` | `OPEN/SATISFIED/REFUTED/UNKNOWN`。只有 `SATISFIED` 允许把对应结构视为闭合。 |

#### `TopologyEvaluationLedger`

| 字段 | 精确定义 |
| --- | --- |
| `round_id` | 当前外层演化轮次。 |
| `parent_id` | 本轮唯一父 Harness。 |
| `candidate_ids` | 本轮被评测的冻结候选 revisions。 |
| `exposure_records` | 每次运行的数据角色与可见性记录。 |
| `execution_trace_ids` | 父代、候选、probe、mutant 和 mask 运行的 trace 指针。 |
| `gate_events` | 编译、类型/effect、权限、循环、激活和 mutant sensitivity 的结果。 |
| `obligation_events` | 每项结构义务的创建、修订和终止证据。 |
| `paired_comparisons` | 相同任务、seed 和环境下父子或完整/mask 版本的指标向量差。 |
| `lineage_actions` | 实际执行的 mutate、refine、probe、evaluate、promote、retire 或 rollback，以及选择该动作时的 propensity；确定性选择记为 1，随机策略记录动作被选中的条件概率。 |
| `llm_call_ids` | 本轮证据解释、mutant/probe、下一动作与停滞反思调用；用于审计披露与决策来源。 |
| `decision` | 本轮当前决定及引用的证据集合；修订决定通过追加事件完成。 |

#### `FailedBindingRecord`

| 字段 | 精确定义 |
| --- | --- |
| `binding_id` | 失败绑定尝试的稳定 ID。 |
| `motif_revision` | 被实例化的 motif 或组件 revision。 |
| `host_context` | Harness family、版本、端口、状态、权限、工具和 environment regime。 |
| `failure_kind` | 类型不可统一、缺 effect、生命周期错误、权限不足、未激活、补偿失败或经验性任务失败。 |
| `minimal_counterexample` | 能重现失败的最小输入、状态、seed、schedule 与 trace 切片；无法最小时注明界限。 |
| `repair_attempts` | 已执行的六类绑定修复动作及结果。 |
| `evidence_ids` | 原始运行、静态检查和确认重复的指针。 |
| `scope` | 该失败能够约束的任务、Harness、模型、工具和版本范围；不能无条件推广。 |

#### `ReusableGraphComponent`

| 字段 | 精确定义 |
| --- | --- |
| `component_revision` | 组件 ID、递增 revision、父 revision 和提交时间。 |
| `graph_motif` | 被提交的规范化 motif。 |
| `typed_open_ports` | 对外接口与类型变量。 |
| `required_effects` | 激活组件时必须观测到的 effect。 |
| `applicability_conditions` | 可接入的 Harness、任务、模型、工具和 regime 条件。 |
| `concrete_variants` | 已验证具体实现及其绑定。 |
| `source_lineages` | 产生抽象的 Harness 谱系节点和 patch。 |
| `activation_evidence` | 证明机制实际执行的事件。 |
| `paired_effect_evidence` | 同任务、同环境父子配对的指标变化。 |
| `regression_evidence` | 旧能力、安全、成本和稳定性证据。 |
| `failed_bindings` | 无法类型化、激活或保持效果的绑定及原因。 |
| `validated_rewrites` | 可安全替换或简化该组件的规则。 |
| `documentation` | 经示例和接口检查的使用说明；文档不是证据源。 |
| `documentation_call_id` | 调用 ID 或 `NONE` | 产生当前文档草稿的 `COMPONENT_DOCUMENTATION` 调用；人工撰写且通过同一检查时为 `NONE`。 |
| `abstraction_call_ids` | 调用 ID 列表 | 提出当前固定机制、开放端口、adapter 边界和不可参数化部分的 `SEMANTIC_COMPONENT_ABSTRACTION` 调用。 |
| `relation_call_ids` | 调用 ID 列表 | 当前 revision 与相邻组件关系的 `COMPONENT_RELATION_PROPOSAL` 调用；关系须另有规则核验结果。 |
| `transfer_attribution_call_ids` | 调用 ID 列表 | 对失败跨任务绑定产生竞争归因的 `FAILED_TRANSFER_ATTRIBUTION` 调用。 |

### 图状态和公式

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

$t\in\{0,1,2,\ldots\}$ 是外层 Harness 演化轮次。三组集合都由 `TrainProtocol.role_assignment_rule` 在看到本轮候选之前冻结。它们不要求每轮覆盖全部训练集，但 `stop_rule` 要求在判断固定点前完成预定任务分层的完整轮换。$D_t^{\mathrm{transfer}}$ 不进入上面的两两不交约束，因为它可以复用更早训练轮次的任务；它必须对待验证组件的形成过程保持独立，并通过 `ExposureRecord` 检查。

#### motif 检索分数

$$
S(B,N)=w_qC_{need}+w_tC_{type}+w_eC_{effect}+w_dC_{dependency}+w_vE_{validated}-w_uU_{unknown}-w_rR_{risk}-w_cC_{conflict}.
$$

`B` 是完整 motif 束，`N` 是 `StructuralNeed`。`C_need` 为能力与变换覆盖率；`C_type` 为无需不安全 cast 的端口覆盖率；`C_effect` 为 required effect 覆盖且 forbidden effect 不出现的比例；`C_dependency` 为硬依赖闭包完整度；`E_validated` 为有执行和 rewrite 证据的结构比例；`U_unknown` 为关键未知条件比例；`R_risk` 为权限、资源和不可补偿 effect 风险；`C_conflict` 为束内未解决冲突比例。所有分量在 `[0,1]`；权重非负，正向权重和、惩罚权重和分别归一化。硬类型或禁止 effect 冲突在评分前淘汰。

程序结构分数与经核验的 `SEMANTIC_MOTIF_BUNDLE_RERANK` 序位通过倒数秩融合：

$$
S_{final}(B)=\alpha_r\frac{1}{k_r+r_{struct}(B)}+
(1-\alpha_r)\frac{1}{k_r+r_{sem}(B)}.
$$

$r_{struct}(B)\in\{1,2,\ldots\}$ 是按 $S(B,N)$ 得到的名次；$r_{sem}(B)$ 是 `OptimizerLLM` 提议且经机制、迁移缺口和反驳测试锚点核验后的语义名次；$k_r>0$ 是平滑常数；$\alpha_r\in[0,1]$ 是结构排序权重，两者在独立检索开发任务上冻结。语义提案解析或核验失败时令 $\alpha_r=1$。该式只能重排已通过硬过滤和依赖闭包的 bundle。

#### Harness 图状态

$$
H_t=(V_t,E_t^{data},E_t^{state},E_t^{order},E_t^{effect},R_t^{loop},\Lambda_t).
$$

`V_t` 是第 $t$ 轮父 Harness 的组件实例节点；$E_t^{data}$ 是数据端口边；$E_t^{state}$ 是状态版本读写边；$E_t^{order}$ 是跨组件偏序；$E_t^{effect}$ 是 effect 依赖与冲突边；$R_t^{loop}$ 是显式循环/重试 region 集；$\Lambda_t$ 是版本 ID、父节点、innovation、结构编辑和 motif revision 组成的谱系元数据。图状态必须能确定性地重新生成静态检查输入。$L_t^H$ 表示跨版本 Harness 谱系，不能与单个 $H_t$ 内的 $R_t^{loop}$ 或 $\Lambda_t$ 混用。

#### 产品抽象域

$$
A_0=A_{type}\times A_{state}\times A_{effect}\times A_{trace}.
$$

`A_type` 追踪可能类型和类型变量；`A_state` 追踪状态键存在性、版本和所有权；`A_effect` 追踪 may/must effect；`A_trace` 追踪必要事件是否可达。笛卡尔积中的一个抽象状态同时携带四类信息。出现伪候选时只细化造成伪解的分量；达到细化上限仍不能排除时返回 `UNKNOWN`。

#### 结构物种距离

$$
d(H_i,H_j)=c_1D_{innovation}+c_2D_{typed\ graph}+c_3D_{parameter}.
$$

`D_innovation` 是不匹配 innovation 的加权 Jaccard 距离；`D_typed graph` 是在类型和 effect 标签下的归一化图编辑距离；`D_parameter` 是共同节点参数的归一化距离。三项范围 `[0,1]`；`c_1,c_2,c_3≥0` 且和为 1。只有 `d≤τ_species` 才属于同一物种；阈值在开发任务冻结，不随候选分数动态改变。

#### 双谱系

$$
L_t^H=\text{Harness 版本与结构谱系},\qquad L_t^M=\text{可复用方法组件谱系}.
$$

`L_t^H` 的节点是完整 Harness 版本，边是结构变异或 crossover；`L_t^M` 的节点是 `ReusableGraphComponent` revision，边是抽象、特化、分裂、合并或废弃。Harness 节点必须指向使用的组件 revision；组件 revision 必须反向指向支撑它的 Harness 节点，保证双向追溯。

#### 组件提交目标

$$
J(m)=\alpha G_{reuse}+\beta G_{execution}+\gamma G_{diagnosis}-\delta C_{definition}-\eta C_{migration}-\rho R_{instability}-\xi R_{semantic}.
$$

`m` 是待提交 motif；`G_reuse` 是跨任务成功绑定覆盖；`G_execution` 是配对运行收益；`G_diagnosis` 是加入组件后定位或反例解释的增益；`C_definition` 是新增节点、端口和规则复杂度；`C_migration` 是目标 Harness 绑定成本；`R_instability` 是重复运行方差和复现失败风险；`R_semantic` 是抽象合并行为不等价风险。各项缩放到 `[0,1]`。`α...ξ` 非负。提交还需独立通过类型、effect、激活和回归硬门，`J` 不能覆盖硬门失败。

### 结构编辑语义

| 编辑 | 前置条件 | 结果 | 失败条件 |
| --- | --- | --- | --- |
| `SUBSTITUTE_NODE` | 新旧节点端口可绑定且 required effect 等价 | 替换单节点实现 | 类型、effect 或异常语义不兼容。 |
| `SPLIT_EDGE` | 原边可由中间节点保持数据/状态语义 | 在边上插入 adapter、verifier 或补偿器 | 中间节点改变所有权或破坏顺序。 |
| `INSERT_MOTIF` | motif 开口端口有完整绑定 | 插入完整机制子图 | 缺硬依赖或形成无界循环。 |
| `ADD_GUARDED_BRANCH` | predicate 可观测且纯函数 | 增加条件路径和明确汇合点 | 分支未覆盖 unknown 或无法恢复。 |
| `SPECIALIZE_CONTROL` | 存在明确 task/regime 条件 | 收紧触发条件或循环界 | 使用测试标签、未来信息或不稳定字段。 |

绑定失败分为 `REBIND`、`INSERT_PREREQ`、`SUBSTITUTE`、`REWIRE`、`ADJUST_CONTROL` 和 `INSERT_COMPENSATION` 六类修复动作；每次只执行一种最小修复并重新静态检查，避免同时变化导致反例无法定位。

### 四阶段接口

| 阶段 | 输入 | 输出 | 完成条件 |
| --- | --- | --- | --- |
| loop 外离线结构组织 | `SourcePacket[]`、编译配置 | 语义对齐调用记录和固定 `StructureCatalogSnapshot` | 每个语义字段有来源/代码/执行锚点或显式未知，具体图、motif、rewrite 和索引已冻结。 |
| loop 内结构检索 | 当前父图与 trace、目录快照、`ReusableComponentView` | 需求解释与语义重排调用记录、`StructuralNeed`、依赖闭合的 `RetrievedMotifBundle[]` | 硬不兼容项已排除，LLM 未恢复过滤项或删除依赖，未知项和开放端口保留。 |
| 结构候选生成 | `EvolutionInput` | 结构诊断、双通道和反例修订调用记录，冻结 `CandidateVersion[]`、`StructuralObligation[]` 和绑定反例 | 候选通过共同静态 gate，所有结构编辑可重放。 |
| 拓扑规划与测评 | 父子候选、结构义务、$D_t^{\mathrm{select}}$、$D_t^{\mathrm{anchor}}$、谱系 | mutant/probe、证据解释、动作与停滞反思调用记录，终止/返回决定和 `TopologyEvaluationLedger` | 最终决定只使用冻结规则与真实证据；影响修订的已披露 case 失去独立性。 |
| 组件积累与复用 | 本轮候选与决定、双谱系、ledger、独立 transfer cases | 抽象、关系、失败归因和文档调用记录，$(L_{t+1}^H,L_{t+1}^M)$、索引和失败绑定 | 原始证据已追加；语义输出只作提案，合法 revision 原子提交或明确失败。 |
| 外层训练 loop | $H_t$、两条谱系、训练调度器 | $H_{t+1}$ 与下一轮状态，或冻结系统 | 只有完整训练轮换达到固定点才 stop；测试集始终封闭。 |

### 辅助对象、枚举与数学约定

| 对象 | 完整定义 |
| --- | --- |
| `StructuralSketch` | `{sketch_id,fixed_nodes,fixed_edges,typed_holes,effect_holes,ordering_constraints,binding_domain,source_motifs}`。 |
| `RetrievedMotifBundle` | `{bundle_id,motifs,hard_dependency_closure,soft_dependencies,conflicts,open_ports,coverage,unknowns}`。 |
| `CandidateIR` / `CandidateVersion` | 字段与冻结边界见前文专表；知识与自由通道先进入共同 IR，全部 gate 通过后才能生成不可原地修改的 version。 |
| `ExposureRecord` | `{task_id,round_id,split_role,visible_to_generation_path_before_freeze,disclosed_fields,disclosed_to_call_ids,affected_candidate_ids,affected_component_revision_ids,independence_status,harness_versions,run_ids,evidence_uses}`。 |
| innovation | `{innovation_id,parent_ids,edit_type,affected_subgraph,created_at,evidence_status}`；同一历史创新跨后代保持 ID。 |
| edge | `{edge_id,source_port,target_port,edge_kind,type_or_state,effect,guard,revision}`；`edge_kind` 取 `data/state/order/effect`，资源所有权写入 `state` 边和端口契约，控制流先后写入 `order` 边。 |
| lineage edge | `workflow` 表示 Harness 演化，`semantic` 表示组件抽象/特化，`alternative` 表示同目标不同结构；三类不可混用。 |
| decision | `Promote/Reject/Tie/ReturnBindingCounterexample/ReturnStructuralNeed/Continue`；前三者结束本轮候选决策，两个 return 回到本轮前序阶段，`Continue` 留在规划器内。 |
| action | `mutate/refine-binding/add-probe/paired-evaluate/promote/retire/rollback`；规划器一次只执行一种真实动作，获得新证据后重规划。 |
| binding repair | `REBIND/INSERT_PREREQ/SUBSTITUTE/REWIRE/ADJUST_CONTROL/INSERT_COMPENSATION`；`ADD_CHECK_OR_COMPENSATION` 是无法细分时的上层请求，执行前必须落入后二者之一。 |
| alignment status | `paper_only/code_only/unmapped` 分别表示仅论文、仅代码、无法映射到统一图；均不等于失败证据。 |
| fixed point | 在完整训练轮换上无晋级、无可合法补全的开放义务、无会改变检索空间的新 revision/反例/需求、无能改变决定的合法实验；任一项为 `UNKNOWN` 时不成立。 |

所有图集合均以稳定 ID 去重；`UNKNOWN` 不兼容具体类型或 effect。所有距离和分数进入公式前归一到 `[0,1]`。空依赖闭包完整度定义为 1，空需求覆盖率定义为 `UNDEFINED` 并停止检索评分。

### 公式参数的可计算定义

motif 束得分的各项为

$$
C_{need}=\frac{\sum_i a_i\mathbf1[B\models req_i]}{\sum_i a_i},\quad
C_{type}=\frac{\sum_p b_p\mathbf1[bindable(p)]}{\sum_pb_p},
$$

$$
C_{effect}=\frac{\sum_e d_e\mathbf1[required_e\ covered]}{\sum_ed_e},\quad
C_{dependency}=\frac{\sum_h g_h\mathbf1[h\in closure(B)]}{\sum_hg_h},
$$

$E_{validated}$ 是具有执行或已验证 rewrite 证据的 motif 结构权重比例；$U_{unknown}$ 是关键未决绑定/依赖权重比例；$R_{risk}$ 是权限、资源、无补偿 effect 的冻结加权和；$C_{conflict}$ 是未解决冲突权重占全部潜在交互权重的比例。正向权重 $w_q+w_t+w_e+w_d+w_v=1$，惩罚权重 $w_u+w_r+w_c=1$；两组权重与总体正负缩放系数均在检索开发集冻结。并列依次选硬未知少、迁移编辑少、验证证据多和 bundle ID 小者。倒数秩融合中的 $r_{struct}$ 与 $r_{sem}$ 都从 1 开始且允许并列使用同一最小名次；$k_r>0$、$\alpha_r\in[0,1]$ 在检索开发任务上冻结，`OptimizerLLM` 的自然语言置信度不进入 $S_{final}$。

$H_t$ 中每个 $E_t^*$ 都是带类型多重边集合。$R_t^{loop}$ 的每个元素为 `{region_id,entry,exit,invariant,progress_measure,max_iterations,max_time,timeout_action}`；$\Lambda_t$ 为 `{version_id,parent_ids,innovation_ids,edit_log,motif_revisions}`。$E^{order}$ 在把每个 $R_t^{loop}$ 元素折叠成单节点后必须为 DAG；$E^{effect}$ 的冲突边只表达组合限制，不表示真实执行顺序。

产品域中每个分量都是有限格：$A_{type}$ 按允许类型集合的反向包含排序，$A_{state}$ 按键/版本/所有权信息精化，$A_{effect}$ 按 may 集缩小与 must 集扩大精化，$A_{trace}$ 按可达事件集合缩小精化。一次 refinement 只严格下降至少一个分量；最大细化次数 $K_{refine}\in\mathbb N^+$ 预先固定，超过后返回 `UNKNOWN`。

结构距离中

$$
D_{innovation}=1-\frac{\sum_{u\in I_i\cap I_j}\kappa_u}{\sum_{u\in I_i\cup I_j}\kappa_u},
$$

$I_i,I_j$ 是创新 ID 集，$\kappa_u>0$ 是编辑影响权重；并集为空时距离为 0。$D_{typed\ graph}$ 是最小合法节点/边插入删除替换成本除以两图最大自成本，非法类型映射成本为无穷；$D_{parameter}$ 是共同语义组件数值/类别参数距离的加权平均，无共同组件时为 1。$c_{1:3}\ge0$ 且和为 1，$\tau_{species}\in[0,1]$。

组件提交式的七项均在 `[0,1]`：$G_{reuse}$ 是独立任务/regime 成功绑定覆盖，$G_{execution}$ 是父子配对效应的保守下界，$G_{diagnosis}$ 是定位损失下降，$C_{definition}$ 是规范化节点/边/规则描述长度，$C_{migration}$ 是新宿主绑定与验证成本，$R_{instability}$ 是失败复现和方差，$R_{semantic}$ 是未被测试区分的抽象风险。$\alpha,\beta,\gamma,\delta,\eta,\rho,\xi\ge0$ 且和为 1；$J(m)>\epsilon_J$ 只是软门，类型、effect、激活和回归硬门仍须全部通过。

### 伪代码算子契约

| 算子组 | 输入 → 输出；失败与未知处理 |
| --- | --- |
| `OFFLINE_COMPILE_STRUCTURE_CATALOG` | 固定来源包与组织协议 → 经 LLM 语义对齐、程序图编译、契约核验、motif 挖掘和索引冻结的 `StructureCatalogSnapshot`。 |
| `ALIGN_SOURCE_UNITS` / `BUILD_SOURCE_GRAPH_ALIGNMENT_REQUESTS` | 来源包 → 论文步骤、代码、配置、测试和执行证据的最小来源单元 → `SOURCE_GRAPH_SEMANTIC_ALIGNMENT` 视图。 |
| `PARSE_SOURCE_GRAPH_ALIGNMENTS` / `VERIFY_SOURCE_GRAPH_ALIGNMENTS` | LLM 输出、来源单元 → 语义映射提案 → 锚点、类型、effect、控制和执行证据核验后的映射；失败字段保持未知。 |
| `COMPILE_METHOD_GRAPHS` | 来源与经核验语义映射 → `MethodGraphVariant[]`；未映射字段保留状态。 |
| `BUILD_TRACE_TO_STRUCTURAL_NEED_VIEW` / `PARSE_STRUCTURAL_NEED_PROPOSAL` | 父图、trace 与开放结构证据 → `TRACE_TO_STRUCTURAL_NEED` 最小视图 → 竞争断点假设和需求提案。 |
| `VERIFY_STRUCTURAL_NEED_GRAPH_AND_TRACE_ANCHORS` | 需求提案、输入视图 → 图节点/边、事件、状态版本和权限均可回溯的 `StructuralNeed`。 |
| `ONLINE_RETRIEVE_MOTIFS` | 固定目录、当前组件视图、当前 need 与 trace 图视图 → 硬约束合格且经语义重排的 motif bundles；不绑定宿主端口。 |
| `CHECK_COMPONENT_CONTRACTS` | variants → 逐节点契约结果；硬缺失阻止进入 motif 挖掘。 |
| `STITCH_STYLE_MINE` | 具体图 → 频繁/重复结构候选；仅产生候选抽象。 |
| `BOUNDED_EGRAPH_NORMALIZE_AND_ANTI_UNIFY` | 图候选、validated rewrites、界限 → 规范 motifs；未验证 rewrite 不入等价类。 |
| `BUILD_TEXT_TYPE_EFFECT_STRUCTURE_INDEXES` | motifs → 文本、类型、effect、结构索引；均可重建。 |
| `FREEZE_STRUCTURE_CATALOG` | 来源、具体图、motif、索引 → 只读目录快照；冻结失败不得进入在线 loop。 |
| `MERGE_STRUCTURE_RETRIEVAL_VIEWS` | 固定目录索引、按需组件视图 → 本次查询的逻辑联合视图；不改写任一权威来源。 |
| `VALIDATED_TRANSFORMATION_DECOMPOSITION` | StructuralNeed → 保序查询树；每个叶子可检查。 |
| `MULTIVIEW_RETRIEVE` / `HARD_CONSTRAINT_FILTER` | 索引、查询树 → seeds → 类型/effect/权限合格 seeds。 |
| `REVERSE_HARD_DEPENDENCY_CLOSURE` / `SOFT_REVERSE_EXPANSION` | seeds → 硬依赖闭包 → 标注可选依赖的 bundles。 |
| `TYPE_EFFECT_SUBGRAPH_RERANK` | bundles、need → $S(B,N)$ 确定排序。 |
| `BUILD_SEMANTIC_MOTIF_RERANK_REQUEST` / `PARSE_SEMANTIC_MOTIF_RERANK` | 硬过滤后的 bundles、need、trace 图 → `SEMANTIC_MOTIF_BUNDLE_RERANK` 视图 → 机制匹配、迁移缺口、互补关系、反驳测试和序位。 |
| `FUSE_VERIFIED_STRUCTURE_AND_SEMANTIC_RANKS` | 程序序位与经锚点核验的语义序位 → $S_{final}$ 排序；不得恢复过滤项、删依赖或解除冲突。 |
| `SYNTHESIZE_TOPOLOGY_CANDIDATES` | 父 Harness、当前 trace batch、need、bundles、绑定反例、能力保留要求和硬约束 → 冻结结构候选与结构义务。 |
| `COMPILE_TYPED_EFFECT_GRAPH` | Harness snapshot → $H_t$；无法定位的代码标为 `unmapped`。 |
| `CONTRAST_SUCCESS_FAILURE_TRACES` | host graph、配对 traces → 决策相关子图切片。 |
| `BUILD_TRACE_GRAPH_DIAGNOSIS_REQUEST` / `PARSE_TRACE_GRAPH_DIAGNOSES` | 父图、切片、成功/失败 trace、need → `TRACE_GRAPH_DIAGNOSIS` 视图 → 多条结构因果链。 |
| `VERIFY_GRAPH_AND_TRACE_CAUSAL_CHAINS` | 因果链、父图与 trace → 事件顺序、节点/边和数据/状态依赖均可核验的诊断。 |
| `INIT_PRODUCT_ABSTRACTION` | 切片、bundles → $A_0$ 与细化配置。 |
| `SEARCH_RESOURCE_EFFECT_SKELETONS` | host、bundles、抽象域 → 满足资源/effect 的骨架。 |
| `CREATE_TYPED_HOLES` | 骨架 → `StructuralSketch[]`。 |
| `BUILD_KNOWLEDGE_TOPOLOGY_REQUESTS` | 父 Harness、草图、motif bundles、局部切片、保留要求和硬约束 → 每个草图的最小 `KNOWLEDGE_TOPOLOGY_COMPLETION` 输入视图；只披露合法绑定、相关来源结构与待填孔位。 |
| `BUILD_FREE_TOPOLOGY_REQUEST` | 父 Harness、草图、局部切片、硬约束 → 一个 `FREE_TOPOLOGY_PROPOSAL` 输入视图；不披露本轮 motif bundles、知识补全或其补丁。 |
| `CALL_OPTIMIZER_LLM` | 输入视图、冻结 `OptimizerLLMConfig` → 原始输出与 `LLMCallRecord`；请求开始前创建 call ID，并将请求、响应、解析与核验状态原子追加到当前实验的 `LLMCallLedger`；越权检查失败时不调用，重试另建 call ID。 |
| `PARSE_KNOWLEDGE_TOPOLOGY_COMPLETIONS` / `PARSE_FREE_TOPOLOGY_PROPOSALS` | `OptimizerLLM` 原始输出、固定 parser → 共同 Candidate IR 或解析失败；不得补写未输出的语义节点、边或绑定。 |
| `COMMON_STATIC_CHECK` | 候选 → 类型、状态、顺序、权限和有界循环合格者。 |
| `BOUNDED_TRACE_VALIDATE` | 候选、trace 界限 → evidence 与 binding counterexamples。 |
| `BUILD_GRAPH_REVISION_REQUEST` / `PARSE_GRAPH_REVISION_PROPOSALS` | 候选、确认反例、诊断和草图 → `COUNTEREXAMPLE_TO_GRAPH_REVISION` 视图 → 六类修订意图。 |
| `VERIFY_MINIMAL_GRAPH_REVISION_INTENTS` | 修订提案、反例、父代 → 锚点、权限、最小编辑与机制保持合格的意图。 |
| `REFINE_FROM_UNTYPEABILITY_OR_TRACE` | 反例、当前产品域 → 严格更精细抽象域。 |
| `LOCAL_GRAPH_REPAIR` | 候选、反例 → 单一最小修复后的新 revisions。 |
| `FREEZE_VALID_CANDIDATE_VERSIONS` | 合格图、证据、父版本 → `CandidateVersion[]`。 |
| `EXTRACT_STRUCTURAL_OBLIGATIONS` | 冻结候选、验证反例 → 去重后的 `StructuralObligation[]`；无法判断的义务保持 `UNKNOWN`。 |
| `PLAN_AND_TEST_TOPOLOGY_EVOLUTION` | 父子候选、结构义务、select/anchor pools、lineage → LLM 解释和动作提案辅助、规则最终决定的结果与 `TopologyEvaluationLedger`。 |
| `REGISTER_INNOVATION_EVENTS` / `STRUCTURAL_SPECIATION` | candidates、lineage → 创新记录 → 按 $d$ 分物种。 |
| `ENUMERATE_PROGRAM_MUTANTS_AND_PROBES` / `SEMANTIC_MUTANT_GAP` | 候选与义务 → 按图编辑规则枚举的基础 mutant/probe；结合 ledger 判断这些测试能否区分仍未决的语义机制，不能时才返回 true。 |
| `BUILD_MUTANT_AND_PROBE_REQUEST` / `PARSE_MUTANT_AND_PROBE_PROPOSALS` | 候选、义务、已有基础 probes 与 ledger → `MUTANT_AND_PROBE_PROPOSAL` 视图 → 补充的单编辑 mutant 与判别 probe。 |
| `COMPILE_VALID_MUTANTS_AND_PROBES` | mutant/probe 提案、候选 → 可执行且保持非目标条件的测试对象；语义破坏不明确者拒绝。 |
| `RUN_STRUCTURE_MECHANISM_AND_MUTANT_CHECKS` | candidate、义务、合法 probes → 结构、激活和变异测试证据。 |
| `BUILD_TOPOLOGY_EVIDENCE_REQUEST` / `PARSE_TOPOLOGY_EVIDENCE_INTERPRETATION` | 候选、义务、真实证据、谱系 → `TOPOLOGY_EVIDENCE_INTERPRETATION` 视图 → 支持、反对、未知和替代解释。 |
| `VERIFY_TOPOLOGY_EVIDENCE_ANCHORS` / `UPDATE_STRUCTURAL_OBLIGATIONS` | 解释、证据、候选 → 锚点合法的语义观察 → 由程序规则更新的义务状态。 |
| `UPDATE_RELEVANT_STRUCTURAL_OBLIGATIONS` | 动作结果的经核验解释、结果、全部义务 → 只更新目标候选和受影响子图的义务 revisions。 |
| `PAIRED_PARENT_CHILD_RUNS` | 父代、候选、冻结 select/anchor pools → matched task/seed/environment traces 和指标差。 |
| `APPEND` | ledger、evidence → 追加 revision；错误通过 supersede 纠正。 |
| `RETURN_TO_TOPOLOGY_SYNTHESIS` | binding counterexample → 返回结构综合与抽象域 refinement。 |
| `PAIRED_PARENT_CHILD_DECISION` | 父子配对证据、硬门 → promote/reject/tie/continue。 |
| `ENUMERATE_LEGAL_LINEAGE_ACTIONS` | species、义务、ledger → 满足权限、数据角色和结构编辑语义的程序动作。 |
| `BUILD_NEXT_LINEAGE_ACTION_REQUEST` / `PARSE_LINEAGE_ACTION_PROPOSALS` | 物种、义务、ledger、程序动作 → `NEXT_LINEAGE_ACTION_PROPOSAL` 视图 → 动作排序或参数完整的新动作。 |
| `COMPILE_VALID_LINEAGE_ACTIONS` / `SELECT_DECISION_RELEVANT_LINEAGE_ACTION` | 动作提案、义务、ledger → 合法动作 → 能改变当前决定的唯一下一动作及 propensity。 |
| `BUILD_STALLED_LINEAGE_REFLECTION_REQUEST` / `PARSE_STALLED_LINEAGE_REFLECTION` | 停滞物种、义务和 ledger → `STALLED_LINEAGE_REFLECTION` 视图 → 新原语需求、替代拓扑、假设修订或 probe。 |
| `VERIFY_AND_COMPILE_LINEAGE_RETURN` | 停滞反思 → 返回阶段一/二的合法请求或无效；不能直接 stop。 |
| `COMPLETE_DEVELOPMENT_PANEL_ACTION` | 当前 ledger 与尚未决候选 → 运行剩余合法 select/anchor 面板的冻结动作；没有可运行项时返回 `NONE`。 |
| `BUILD_STRUCTURAL_NEED_FROM_ACTION` / `RETURN_TO_MOTIF_RETRIEVAL` | 缺失 primitive 的动作及其 ledger 证据 → 新 need → 返回 motif 检索。 |
| `EXECUTE` | 冻结 lineage action、隔离环境 → 原始证据；失败同样入账。 |
| `CONSOLIDATE_COMPONENT_LINEAGE` | 父代、候选、决定、双谱系、ledger、独立 transfer cases → 原子提交的新双谱系和索引。 |
| `APPEND_ROUND_LINEAGE_EVIDENCE` | Harness 谱系、本轮图与证据 → copy-on-write 影子谱系；不覆盖旧 revision。 |
| `SELECT_EVIDENCE_ELIGIBLE_STRUCTURES` | lineage、ledger → 通过激活、配对、回归门的结构语料。 |
| `BUILD_COMPONENT_ABSTRACTION_REQUEST` / `PARSE_COMPONENT_ABSTRACTION_PROPOSALS` | 结构语料、ledger、既有组件谱系 → `SEMANTIC_COMPONENT_ABSTRACTION` 视图 → 固定机制、开放端口、adapter 与边界反例提案。 |
| `VERIFY_AND_PARAMETERIZE_COMPONENT_BOUNDARIES` | 语料、抽象提案 → 来源、图、类型/effect 与执行证据合格的参数化图；未确认部分留在具体 variant。 |
| `MULTIOBJECTIVE_FILTER` | motifs → 非支配且过硬门的抽象候选。 |
| `CROSS_TASK_BIND_ACTIVATE_AND_REPLAY` | motif、独立宿主 → 绑定/激活/回放报告。 |
| `PAIRED_MASK_WHEN_FEASIBLE` | motif、宿主 → 配对 mask 贡献或 `UNIDENTIFIED`。 |
| `BUILD_COMPONENT_RELATION_REQUEST` / `PARSE_COMPONENT_RELATION_PROPOSAL` | 新 motif、组件谱系 → `COMPONENT_RELATION_PROPOSAL` 视图 → 重复、细化、替代、冲突、组合或未知关系。 |
| `VERIFY_COMPONENT_RELATION` | 关系提案、motif、组件谱系 → 结构、契约、scope、regime 和证据一致的关系或 `UNRESOLVED`。 |
| `BUILD_COMPONENT_DOCUMENTATION_REQUEST` | 已过结构与证据门的 motif、replay、贡献结果 → 最小 `COMPONENT_DOCUMENTATION` 输入视图；不得披露测试集或未提交的未来证据。 |
| `PARSE_AND_VALIDATE_COMPONENT_DOCUMENTATION` | `OptimizerLLM` 原始输出、motif、replay → 经接口、示例、限制和来源核验的文档，或 `DOC_REJECTED`；文档不作证据。 |
| `DOCUMENTATION_VALID` / `RECORD_DOCUMENTATION_REJECTION` | 文档检查结果 → 可提交布尔值；失败时保存调用、拒绝原因和待修订状态，不提交组件 revision。 |
| `BUILD_FAILED_TRANSFER_ATTRIBUTION_REQUEST` / `PARSE_FAILED_TRANSFER_ATTRIBUTION` | motif、失败 replay、已核验关系 → `FAILED_TRANSFER_ATTRIBUTION` 视图 → 竞争失败归因。 |
| `VERIFY_TRANSFER_FAILURE_ATTRIBUTION` | 归因提案、motif、replay → 端口、effect、adapter、regime、抽象边界或未知的带证据归因。 |
| `HARD_GATES_PASS` / `EVIDENCE_SUFFICIENT` | replay、contribution → 硬门 bool 与证据充分性 bool。 |
| `COMMIT_COMPONENT_REVISION` | lineage、motif、经核验关系、replay、贡献证据、文档 → 新 `ReusableGraphComponent` revision。 |
| `RECORD_FAILED_ABSTRACTION` | motif、失败 replay、经核验或未决归因 → 可检索失败绑定，不删除 motif 来源。 |
| `ATOMIC_COMMIT_DUAL_LINEAGE` | 通过不变量检查的 Harness/组件影子谱系 → 同一事务中的两个新 revision；任一侧失败则不发布派生 revision，但保留只追加原始事件。 |
| `REBUILD_RETRIEVAL_INDEX` | 权威 method lineage → 新派生索引。 |
| `EVOLVE_TOPOLOGY_ON_BENCHMARK_TRAIN` | 初始 Harness、双谱系、固定目录快照、训练集、协议 → stop 后冻结的 Harness 与结构系统。 |
| `INIT_TRAIN_SCHEDULER` / `ASSIGN_TRAIN_ROLES` | 训练集与协议 → 可审计的角色调度器 → 本轮四类任务池。 |
| `INIT_LLM_CALL_LEDGER` / `UPDATE_EXPOSURE_FROM_LLM_CALLS` | 冻结协议 → 追加写调用账本；调用账本、受影响的候选或组件 revisions 及相应任务池 → 披露字段、受影响后代与逐对象独立性状态。第三阶段处理 select/anchor，第四阶段处理 transfer。 |
| `COMPONENT_REVISIONS_CREATED` | 前后组件谱系 → 本轮新增或修订的组件 revision ID；未提交的失败抽象由其失败记录 ID 代替，以便保存 transfer 披露关系。 |
| `TRACE_GRAPH_VIEW` | 父图与 trace batch → 仅含当前 call type 允许披露的节点、边、事件和状态版本的不可变视图。 |
| `REFRESH_INDEPENDENT_SELECT_POOL` | 暴露历史、受影响候选和旧 select pool → 删除已影响候选修订的 case 并补入未披露训练 case。 |
| `RUN_HARNESS` | 冻结 Harness、任务池、协议 → `ExecutionTrace[]`；失败运行也必须产生终止事件。 |
| `BUILD_STRUCTURAL_NEED` / `REVISE_STRUCTURAL_NEED` | 当前父图、trace、历史结构证据或新反例 → 经 `TRACE_TO_STRUCTURAL_NEED` 提议并由图/trace 锚点核验的 `StructuralNeed` revision。 |
| `RETRIEVE_REUSABLE_COMPONENT_VIEW` | 组件谱系、need 与 `TrainProtocol.reuse_policy` → 同时满足提交时间边界、scope、regime、接口/effect 和证据等级限制的 `ReusableComponentView`；不合格 revision 不进入本轮查询视图。 |
| `LEDGER_FROM_TRACE_BATCH` | 父代 trace batch → 本轮 ledger 初始事件，并保留 `split_role=trace`。 |
| `CONFIRMED_BINDING_FAILURES` | Harness 谱系、当前父代 → 当前 scope 内已确认的 `FailedBindingRecord[]`。 |
| `BUILD_PRESERVATION_REQUIREMENTS` / `COMPILE_TOPOLOGY_HARD_CONSTRAINTS` | 父代、anchor pool、谱系、协议，或父代、need、bundles、协议 → 旧能力/接口保持谓词，或类型、effect、权限、数据隔离、终止和编辑范围硬约束。 |
| `CONFIRMED_BINDING_COUNTEREXAMPLE` | 本轮 ledger → 已达到复现门的最小绑定反例；证据不足时返回 `UNKNOWN` 并继续取证。 |
| `PENDING_STRUCTURAL_EVIDENCE` | 当前双谱系 → 与父 Harness scope 匹配的开放义务、失败绑定、未决抽象和上一轮返回项。 |
| `TARGETS` / `TASKS_AND_SEEDS` | 任一冻结动作 → 受影响候选/义务；对 `paired-evaluate` 另返回预先选择的任务与种子，执行后不得扩大范围。 |
| `ACCEPT_IF_PROMOTED` | 父代、冻结候选、决定 → 获胜候选或原父代；不得返回未冻结 revision。 |
| `UPDATE_TRAIN_SCHEDULER` | 本轮角色、决定、ledger、新双谱系 → 新 exposure 历史、覆盖状态、anchors 和未决项。 |
| `TOPOLOGY_TRAIN_FIXED_POINT` | 调度器、前后 Harness、前后双谱系、ledger → stop bool 或 `UNKNOWN`；只有完整轮换且最近停滞反思没有合法新分支时才可返回 true。 |
| `FREEZE_TOPOLOGY_SYSTEM_FOR_FINAL_TEST` | 最终 Harness、双谱系、目录和协议 → 不再可写的测试输入快照。 |

局部变量 `units/alignment_requests/alignment_calls/alignment_proposals/alignments/variants/syntax_candidates/motifs/indexes` 依次表示来源单元、图对齐请求及调用、未核验对齐提案、经核验映射、具体图变体、语法候选、规范 motif 和索引。`need_view/need_call/need_proposal/need/query_tree/seeds/bundles/rerank_request/rerank_call/rerank_proposal` 是需求解释视图、调用、原始提案、经核验需求、变换查询树、初召回、依赖闭合束和语义重排请求/调用/提案。

`host_graph/slice/diagnosis_request/diagnosis_call/diagnosis_proposals/diagnoses/abstract_domain/skeletons/sketches` 是宿主图、trace 对比切片、结构诊断请求及调用、未核验因果链、经图/trace 核验诊断、产品抽象域、结构骨架和带孔草图。`knowledge/free/candidates/evidence/counterexamples/revision_request/revision_call/revision_proposals/revision_intents/obligations` 是两条生成通道、共同候选、验证证据、绑定反例、反例修订请求及调用、原始修订、合法最小修订和结构义务；没有反例时 `revision_intents` 为空集合。

`species/ledger/probes/mutant_request/mutant_call/mutant_proposals/semantic_probes/interpretation_request/interpretation_call/interpretation/program_actions/action_request/action_call/action_proposals/actions/reflection_request/reflection_call/reflection/return_request/result` 依次表示结构物种、追加账本、程序枚举的基础 probes、语义 mutant/probe 请求及调用和提案、核验通过的语义 probes、证据解释请求及调用和经核验结果、程序动作、动作规划请求及调用和提案、合法动作集、停滞反思请求及调用和提案、返回前序阶段请求及真实执行结果。所有 `*_proposal` 在对应核验器通过前均不是结构事实或决策。

`corpus/abstraction_request/abstraction_call/abstraction_proposals/parameterized/relation_request/relation_call/relation_proposal/relation/replay/contribution/doc_request/doc_call/docs/failure_request/failure_call/failure_proposal/failure` 是可沉淀语料、组件抽象调用链、经核验参数化图、组件关系调用链及结果、跨任务重放、配对贡献、文档调用链、失败迁移归因调用链及经核验归因。`catalog/scheduler/llm_call_ledger/trace_pool/select_pool/anchor_pool/transfer_pool/trace_batch/reusable_view/preservation_requirements/hard_constraints` 是离线目录、训练调度器、实验级调用账本、四类训练角色、父代 trace、按需组件视图、能力保持谓词和本轮不可绕过约束。

兼容名称固定如下：`semantic_component_id` 等同于 `ComponentContract.component_id`；`workflow/semantic/alternative` 是三类 lineage edge 的并列简写；`REBIND / INSERT_PREREQ / SUBSTITUTE / REWIRE / ADJUST_CONTROL / INSERT_COMPENSATION` 是六类绑定修复动作；`mutate / refine-binding / add-probe / paired-evaluate / promote / retire / rollback` 是完整 lineage action 枚举。

### 不变量

1. `E_order` 闭包无环；循环必须显式位于有界区域。
2. 每个数据边两端类型兼容，每个状态写都有所有权和版本规则。
3. 所有结构候选先冻结再运行，运行过程不得自改代码。
4. 语法重复只产生 motif 候选，不直接产生可复用组件。
5. 新组件必须至少有一个可执行具体变体和一个失败绑定记录槽位。
6. 任一抽象被反例击穿时保留旧 revision，并创建分裂或回退 revision。
7. 同一运行不得同时作为生成当前候选的 trace 证据和该候选的独立选择证据。
8. 外部目录在一次 benchmark 演化中只读；新增论文或改变编译配置必须开启新的实验条件。
9. benchmark 测试集在 stop 前不可访问，测试 trace 永不回写 Harness 或组件谱系。
10. 本轮存在 `OPEN/UNKNOWN` 结构义务、未提交谱系或能改变决定的合法实验时，外层 loop 不得 stop。
11. 任一 `OptimizerLLM` 输出在进入目录、需求、Candidate IR、义务、动作集合或组件谱系前，必须通过该 call type 的 parser、图/trace 锚点、权限和规则核验。
12. `OptimizerLLM` 的概率、分数和语言置信度不得直接写入 motif 结构分数、gate、父子收益、组件提交目标或晋级统计量。
13. 任一 select case 一旦通过 LLM 调用影响候选生成或修订，便对该候选及后代失去独立选择资格，并由训练调度器补入未披露训练案例。
