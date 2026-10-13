# Source Packets

All project-authored metadata, indexes, and explanatory documents under `source-packets/` must be written in English. Paper files and official-code snapshots retain their upstream language.

Each paper has a separate directory named `<short-title>-<arXiv-id-or-other-stable-identifier>`. Five members may add different paper directories in parallel. This directory stores source evidence only; Method-specific derived representations belong elsewhere.

Every source packet must contain:

```text
<paper-id>/
├── source-packet.json
├── paper/
│   ├── paper-vN.pdf
│   └── paper-vN.txt
├── official-code/
├── exact-source-anchors.md
├── configs-and-examples.md
└── tests-and-reported-results.md
```

| `SourcePacket` field | Required content |
| --- | --- |
| `paper_version` | Paper title, authors, version, publication date, source URL, and local PDF and text paths. |
| `official_code_version` | Official repository, pinned upstream revision, acquisition date, retained code scope, and license status. |
| `exact_source_anchors` | Exact paper pages, sections, figures, tables, and code locations supporting each mechanism, condition, and limitation. |
| `configs_and_examples` | Configurations, commands, data entry points, examples, and runtime prerequisites used by the paper or official repository. |
| `tests_and_reported_results` | Official test entry points, reported results, ablations, failure conditions, and local verification status. |

Follow these collection rules:

1. Keep primary sources separate from downstream Method artifacts. Do not impose a route-specific object structure on a source packet.
2. Pin paper and official-code versions. When a source changes, add a version record instead of overwriting the previous evidence.
3. Record paper claims, observed code behavior, and local execution results separately. Mark missing information as unknown.
4. Do not commit secrets, runtime caches, large external datasets, or answers leaked from hidden benchmark tests.
5. Before merging, the contributor resolves conflicts within the same paper directory. Different paper directories may be added in parallel.
6. Select `official-code/` files around the paper's method. Keep evaluators, scorers, tests, configurations, and examples when they are required by the mechanism. Exclude secrets, login state, and files that directly reveal hidden benchmark answers.
7. Include task instances, splits, or raw data only when they are part of the paper's method and materially aid understanding or reproduction. Describe their retained scope and purpose accurately in `snapshot_scope`; complete `benchmark_leakage_check` from the files actually retained.
8. Do not record locally computed MD5, SHA, or checksum values in source-packet documents. The official Git revision in `official_code_version.upstream_revision` is permitted.

## Included Sources

| Paper | Direction | Source packet |
| --- | --- | --- |
| How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings |Instructions and skills| [skill-usage-2604.04323](skill-usage-2604.04323/) |
| Inducing Programmatic Skills for Agentic Tasks |Instructions and skills| [agent-skill-induction-2504.06821](agent-skill-induction-2504.06821/) |
| ACON: Optimizing Context Compression for Long-horizon LLM Agents |Context management and compression| [acon-2510.00615](acon-2510.00615/) |
| AgentFold: Long-Horizon Web Agents with Proactive Context Management |Context management and compression| [agentfold-2510.24699](agentfold-2510.24699/) |
| FrugalGPT: How to Use Large Language Models While Reducing Cost and Improving Performance |Model selection and resource allocation| [frugalgpt-2305.05176](frugalgpt-2305.05176/) |
| RouteLLM: Learning to Route LLMs with Preference Data |Model selection and resource allocation| [routellm-2406.18665](routellm-2406.18665/) |
| ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities |Tools and environment interaction| [toolsandbox-2025.findings-naacl.65](toolsandbox-2025.findings-naacl.65/) |
| The Berkeley Function Calling Leaderboard (BFCL): From Tool Use to Agentic Evaluation of Large Language Models |Tools and environment interaction| [bfcl-2025.icml](bfcl-2025.icml/) |
| Why Do Multi-Agent LLM Systems Fail? |Fault tolerance and recovery| [mast-2025.neurips](mast-2025.neurips/) |
| AgentDiagnose: An Open Toolkit for Diagnosing LLM Agent Trajectories |Fault tolerance and recovery| [agentdiagnose-2025.emnlp-demos](agentdiagnose-2025.emnlp-demos/) |
| Open Grounded Planning: Challenges and Benchmark Construction |Execution loop and scheduling| [open-grounded-planning-2024.acl-long.272](open-grounded-planning-2024.acl-long.272/) |
| HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model |Execution loop and scheduling| [hiagent-2025.acl-long](hiagent-2025.acl-long/) |
| AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework |Sub-agent and multi-agent collaboration| [autogen-2308.08155](autogen-2308.08155/) |
| MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework |Sub-agent and multi-agent collaboration| [metagpt-2308.00352](metagpt-2308.00352/) |
| SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering |Runtime observation, traces, and integration interfaces| [swe-agent-2405.15793](swe-agent-2405.15793/) |
| OpenHands: An Open Platform for AI Software Developers as Generalist Agents |Runtime observation, traces, and integration interfaces| [openhands-2407.16741](openhands-2407.16741/) |
| AgentRewind |Session and environment state management| [agentrewind-2608.14380](agentrewind-2608.14380/) |
| AgentScope |Extension mechanisms and lifecycle hooks| [agentscope-2508.16279](agentscope-2508.16279/) |
| ExpeL |Long-term memory and experience reuse| [expel-2308.10144](expel-2308.10144/) |
| NORA |Extension mechanisms and lifecycle hooks| [nora-2605.02092](nora-2605.02092/) |
| ReasoningBank |Long-term memory and experience reuse| [reasoningbank-2509.25140](reasoningbank-2509.25140/) |
| StateFork |Session and environment state management| [statefork-2609.38648](statefork-2609.38648/) |


## Recent Top-Tier Papers with Official Code

| Paper | Venue | Covered directions | Source packet |
| --- | --- | --- | --- |
| LLM Agents Making Agent Tools | ACL 2025 | Instructions and skills; Tools and environment interaction; Execution loop and scheduling; Extension mechanisms and lifecycle hooks | [toolmaker-2502.11705](toolmaker-2502.11705/) |
| EASYTOOL: Enhancing LLM-based Agents with Concise Tool Instruction | NAACL 2025 | Instructions and skills; Tools and environment interaction; Context management and compression; Extension mechanisms and lifecycle hooks | [easytool-2401.06201](easytool-2401.06201/) |
| MAGIC: Generating Self-Correction Guideline for In-Context Text-to-SQL | AAAI 2025 | Instructions and skills; Long-term memory and experience reuse; Fault tolerance and recovery; Execution loop and scheduling; Planning and progress management | [magic-2406.12692](magic-2406.12692/) |
| G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems | NeurIPS 2025 | Instructions and skills; Context management and compression; Long-term memory and experience reuse; Execution loop and scheduling; Planning and progress management; Session and environment state management; Sub-agent and multi-agent collaboration; Extension mechanisms and lifecycle hooks; Runtime observation, traces, and integration interfaces | [g-memory-2506.07398](g-memory-2506.07398/) |
| INFERENCEDYNAMICS: Efficient Routing Across LLMs through Structured Capability and Knowledge Profiling | ACL 2026 | Instructions and skills; Model selection and resource allocation | [inference-dynamics-2505.16303](inference-dynamics-2505.16303/) |
| GuardAgent: Safeguard LLM Agents via Knowledge-Enabled Reasoning | ICML 2025 | Instructions and skills; Tools and environment interaction; Long-term memory and experience reuse; Fault tolerance and recovery; Planning and progress management; Permissions, approval, and runtime isolation | [guardagent-2406.09187](guardagent-2406.09187/) |
| AutoManual: Constructing Instruction Manuals by LLM Agents via Interactive Environmental Learning | NeurIPS 2024 | Instructions and skills | [automanual-2405.16247](automanual-2405.16247/) |
| PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization | ICLR 2024 | Instructions and skills | [promptagent-2310.16427](promptagent-2310.16427/) |
| Trace is the Next AutoDiff: Generative Optimization with Rich Feedback, Execution Traces, and LLMs | NeurIPS 2024 | Instructions and skills; Fault tolerance and recovery; Runtime observation, traces, and integration interfaces | [trace-2406.16218](trace-2406.16218/) |
| Automated Design of Agentic Systems | ICLR 2025 | Instructions and skills; Planning and progress management; Extension mechanisms and lifecycle hooks | [adas-2408.08435](adas-2408.08435/) |
| Benchmarking Failures in Tool-Augmented Language Models | NAACL 2025 | Tools and environment interaction; Fault tolerance and recovery; Permissions, approval, and runtime isolation; Runtime observation, traces, and integration interfaces; Verification, evaluation, and feedback | [fail-talms-2503.14227](fail-talms-2503.14227/) |
| GUI-Robust: A Comprehensive Dataset for Testing GUI Agent Robustness in Real-World Anomalies | KDD 2026 | Tools and environment interaction; Context management and compression; Fault tolerance and recovery; Session and environment state management; Permissions, approval, and runtime isolation; Runtime observation, traces, and integration interfaces | [gui-robust-2506.14477](gui-robust-2506.14477/) |
| DRIFT: Dynamic Rule-Based Defense with Injection Isolation for Securing LLM Agents | NeurIPS 2025 | Tools and environment interaction; Fault tolerance and recovery; Session and environment state management; Permissions, approval, and runtime isolation | [drift-2506.12104](drift-2506.12104/) |
| WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks | NeurIPS 2025 | Tools and environment interaction; Fault tolerance and recovery; Session and environment state management; Permissions, approval, and runtime isolation; Runtime observation, traces, and integration interfaces; Verification, evaluation, and feedback | [wasp-2504.18575](wasp-2504.18575/) |
| AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents | NeurIPS 2024 | Tools and environment interaction; Fault tolerance and recovery; Execution loop and scheduling; Session and environment state management; Permissions, approval, and runtime isolation; Extension mechanisms and lifecycle hooks; Runtime observation, traces, and integration interfaces; Verification, evaluation, and feedback | [agentdojo-2406.13352](agentdojo-2406.13352/) |
| AgentAuditor: Human-Level Safety and Security Evaluation for LLM Agents | NeurIPS 2025 | Tools and environment interaction; Long-term memory and experience reuse; Sub-agent and multi-agent collaboration; Permissions, approval, and runtime isolation; Runtime observation, traces, and integration interfaces; Verification, evaluation, and feedback | [agentauditor-2506.00641](agentauditor-2506.00641/) |
| ToolEmu: Identifying the Risks of LM Agents with an LM-Emulated Sandbox | ICLR 2024 | Tools and environment interaction; Fault tolerance and recovery; Permissions, approval, and runtime isolation | [toolemu-2309.15817](toolemu-2309.15817/) |
| DAC: A Dynamic Attention-aware Approach for Task-Agnostic Prompt Compression | ACL 2025 | Context management and compression | [dac-2507.11942](dac-2507.11942/) |
| SGLang: Efficient Execution of Structured Language Model Programs | NeurIPS 2024 | Context management and compression; Execution loop and scheduling; Model selection and resource allocation; Extension mechanisms and lifecycle hooks | [sglang-2312.07104](sglang-2312.07104/) |
| LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression | ACL 2024 | Context management and compression | [longllmlingua-2310.06839](longllmlingua-2310.06839/) |
| ReadAgent: A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts | ICML 2024 | Context management and compression | [readagent-2402.09727](readagent-2402.09727/) |
| A-MEM: Agentic Memory for LLM Agents | NeurIPS 2025 | Context management and compression; Long-term memory and experience reuse; Session and environment state management | [a-mem-2502.12110](a-mem-2502.12110/) |
| Reasoning Path Compression: Compressing Generation Trajectories for Efficient LLM Reasoning | NeurIPS 2025 | Context management and compression; Model selection and resource allocation | [reasoning-path-compression-2505.13866](reasoning-path-compression-2505.13866/) |
| Agent Workflow Memory | ICML 2025 | Execution loop and scheduling; Planning and progress management; Session and environment state management | [agent-workflow-memory-2409.07429](agent-workflow-memory-2409.07429/) |
| Interactive Debugging and Steering of Multi-Agent AI Systems | CHI 2025 | Long-term memory and experience reuse; Fault tolerance and recovery; Session and environment state management; Sub-agent and multi-agent collaboration; Extension mechanisms and lifecycle hooks; Runtime observation, traces, and integration interfaces | [agdebugger-2503.02068](agdebugger-2503.02068/) |
| Collab-Overcooked: Benchmarking and Evaluating Large Language Models as Collaborative Agents | EMNLP 2025 | Long-term memory and experience reuse; Sub-agent and multi-agent collaboration; Verification, evaluation, and feedback | [collab-overcooked-2502.20073](collab-overcooked-2502.20073/) |
| AgentSense: Benchmarking Social Intelligence of Language Agents through Interactive Scenarios | NAACL 2025 | Long-term memory and experience reuse; Sub-agent and multi-agent collaboration; Verification, evaluation, and feedback | [agentsense-2410.19346](agentsense-2410.19346/) |
| Thought-Augmented Planning for LLM-Powered Interactive Recommender Agent | KDD 2026 | Long-term memory and experience reuse; Planning and progress management | [taira-2506.23485](taira-2506.23485/) |
| OS-Harm: A Benchmark for Measuring Safety of Computer Use Agents | NeurIPS 2025 | Fault tolerance and recovery; Permissions, approval, and runtime isolation; Verification, evaluation, and feedback | [os-harm-2506.14866](os-harm-2506.14866/) |
| Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models | ICML 2024 | Fault tolerance and recovery; Planning and progress management | [lats-2310.04406](lats-2310.04406/) |
| MultiAgentBench : Evaluating the Collaboration and Competition of LLM agents | ACL 2025 | Execution loop and scheduling; Planning and progress management; Session and environment state management; Sub-agent and multi-agent collaboration; Extension mechanisms and lifecycle hooks; Runtime observation, traces, and integration interfaces; Verification, evaluation, and feedback | [multiagentbench-2503.01935](multiagentbench-2503.01935/) |
| Flow: A Modular Approach to Automated Agentic Workflow Generation | ICLR 2025 | Execution loop and scheduling; Planning and progress management; Sub-agent and multi-agent collaboration | [flow-2501.07834](flow-2501.07834/) |
| AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents | NeurIPS 2024 | Execution loop and scheduling | [agentboard-2401.13178](agentboard-2401.13178/) |
| Executable Code Actions Elicit Better LLM Agents | ICML 2024 | Execution loop and scheduling | [codeact-2402.01030](codeact-2402.01030/) |
| On the Limit of Language Models as Planning Formalizers | ACL 2025 | Planning and progress management | [llm-planning-formalizers-2412.09879](llm-planning-formalizers-2412.09879/) |
| Revealing the Barriers of Language Agents in Planning | NAACL 2025 | Planning and progress management | [agent-planning-barriers-2410.12409](agent-planning-barriers-2410.12409/) |
| Smoothie: Label Free Language Model Routing | NeurIPS 2024 | Model selection and resource allocation | [smoothie-2412.04692](smoothie-2412.04692/) |
| PORT: Efficient Training-Free Online Routing for High-Volume Multi-LLM Serving | NeurIPS 2025 | Model selection and resource allocation | [port-2509.02718](port-2509.02718/) |
| Archon: An Architecture Search Framework for Inference-Time Techniques | ICML 2025 | Model selection and resource allocation | [archon-2409.15254](archon-2409.15254/) |
| Bag of Tricks for Inference-time Computation of LLM Reasoning | NeurIPS 2025 | Model selection and resource allocation | [inference-time-computation-2502.07191](inference-time-computation-2502.07191/) |
| Mixture-of-Agents Enhances Large Language Model Capabilities | ICLR 2025 | Model selection and resource allocation; Sub-agent and multi-agent collaboration | [mixture-of-agents-2406.04692](mixture-of-agents-2406.04692/) |
| SpecEM: Training-Free LLM Ensembling via Iterative Drafting, Verification, and Online Feedback | NeurIPS 2025 | Model selection and resource allocation | [specem-2412.07380](specem-2412.07380/) |
| GPTSwarm: Language Agents as Optimizable Graphs | ICML 2024 | Model selection and resource allocation; Sub-agent and multi-agent collaboration; Extension mechanisms and lifecycle hooks | [gptswarm-2402.16823](gptswarm-2402.16823/) |
| OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments | NeurIPS 2024 | Session and environment state management | [osworld-2404.07972](osworld-2404.07972/) |
| AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents | ICLR 2025 | Session and environment state management | [androidworld-2405.14573](androidworld-2405.14573/) |
| Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key? | ACL 2024 | Sub-agent and multi-agent collaboration | [llm-discussion-2402.18272](llm-discussion-2402.18272/) |
| AgentDAM: Privacy Leakage Evaluation for Autonomous Web Agents | NeurIPS 2025 | Permissions, approval, and runtime isolation; Verification, evaluation, and feedback | [agentdam-2503.09780](agentdam-2503.09780/) |
| Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents | ICLR 2025 | Permissions, approval, and runtime isolation | [agent-security-bench-2410.02644](agent-security-bench-2410.02644/) |
| AI Control: Improving Safety Despite Intentional Subversion | ICML 2024 | Permissions, approval, and runtime isolation | [ai-control-2312.06942](ai-control-2312.06942/) |
| AFlow: Automating Agentic Workflow Generation | ICLR 2025 | Extension mechanisms and lifecycle hooks | [aflow-2410.10762](aflow-2410.10762/) |
| AgentSquare: Automatic LLM Agent Search in Modular Design Space | ICLR 2025 | Extension mechanisms and lifecycle hooks | [agentsquare-2410.06153](agentsquare-2410.06153/) |
| Agent-as-a-Judge: Evaluate Agents with Agents | ICML 2025 | Runtime observation, traces, and integration interfaces | [agent-as-a-judge-2410.10934](agent-as-a-judge-2410.10934/) |
| Agent-RewardBench: Towards a Unified Benchmark for Reward Modeling across Perception, Planning, and Safety in Real-World Multimodal Agents | ACL 2025 | Permissions, approval, and runtime isolation; Verification, evaluation, and feedback | [agent-rewardbench-2506.21252](agent-rewardbench-2506.21252/) |

## Mechanism-level packet index

| Source | Extracted mechanism | Mechanism and boundaries | Claim-level evidence |
| --- | --- | --- | --- |
| ReasoningBank | Extracting and retrieving reasoning experience from success and failure | [Description](reasoningbank-2509.25140/mechanism-and-boundaries.md) | [Evidence map](reasoningbank-2509.25140/claim-evidence-map.json) |
| ExpeL | Rule maintenance and successful-example retrieval | [Description](expel-2308.10144/mechanism-and-boundaries.md) | [Evidence map](expel-2308.10144/claim-evidence-map.json) |
| AgentRewind | Aligned context and workspace recovery | [Description](agentrewind-2608.14380/mechanism-and-boundaries.md) | [Evidence map](agentrewind-2608.14380/claim-evidence-map.json) |
| StateFork | Separation of logical branching and physical state recovery | [Description](statefork-2609.38648/mechanism-and-boundaries.md) | [Evidence map](statefork-2609.38648/claim-evidence-map.json) |
| AgentScope | Lifecycle callback input/output contracts | [Description](agentscope-2508.16279/mechanism-and-boundaries.md) | [Evidence map](agentscope-2508.16279/claim-evidence-map.json) |
| NORA | Host events and structured session handoff | [Description](nora-2605.02092/mechanism-and-boundaries.md) | [Evidence map](nora-2605.02092/claim-evidence-map.json) |
