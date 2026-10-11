# Exact source anchors

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 事件流架构：所有交互统一为 Action/Observation，事件流记录 Agent 全部历史 | §2.1，PDF p.3（Fig.2 同页）；§1 p.2 | "the event stream, which is a chronological collection of past actions and observations, including the agent's own actions and user interactions"；Fig.2 "Event stream for tracking history of actions and observations"。 |
| Agent 循环抽象：step(state)→Action，由框架负责执行 | §2.1 "Implement a New Agent"，PDF p.4（Fig.3 同页） | "The core of the agent abstraction lies in the step function, which takes the current state as input and generates an appropriate action"。注意：论文未用 "controller" 一词，控制器仅存在于代码。 |
| Runtime 沙箱：每任务启动隔离 Docker 容器，经容器内 REST API 执行动作返回观察 | §2.2，PDF p.4–5；§F.1 p.20（Fig.4） | "For each task session, OpenHands spins up a securely isolated docker container sandbox, where all the actions from the event stream are executed"；三组件 bash/IPython/Chromium；§F.1 "(6) the client sends execution results back … as observations"。 |
| Agent 委托：AgentDelegateAction 委派子任务，CodeAct→BrowsingAgent | §2.4，PDF p.5；评测佐证 Tab.5 p.9 | "a special action type AgentDelegateAction, which enables an agent to delegate a specific subtask to another agent… CodeActAgent… delegate web browsing tasks to the specialized BrowsingAgent"。 |
| 记忆/历史：state 内 history/事件流，Fig.3 逐事件转消息 | §2.1，PDF p.3–4（Fig.3） | 状态含事件流与 "accumulative cost…metadata to track multi-agent delegation"；`get_action_message`/`get_observation_message` 遍历 state.history 构造 LLM 消息。 |
| SWE-bench 结果（26%） | §4.2 p.7 正文；Tab.4 p.8；Tab.3 p.7 | "CodeActAgent v1.8, using claude-3.5-sonnet, achieves a competitive resolve rate of 26%"；Tab.4 "SWE-Bench Lite…300 instances, w/o Hint"：claude-3-5-sonnet@20240620 = 26.0（$1.10）、gpt-4o-2024-05-13 = 22.0（$1.72）。 |
| Web/杂项结果（WebArena、GAIA、GPQA） | Tab.5 p.9；Tab.6 p.10；Tab.3 p.7 | WebArena（812 instances）BrowsingAgent v1.0 claude-3-5-sonnet = 15.5%、CodeAct v1.8 经委托 = 15.3%；MiniWoB++（125 envs）gpt-4o = 40.8%；GAIA L1（53 instances）gpt-4o = 32.1%；GPQA diamond（198）claude = 52.0%。 |
| 事件流支撑可视化 | §D，PDF p.19；§F.1 p.20 | "This user interface directly connects with the event streams (§2.1) to control and visualize the agents and runtime"。注意：论文无 "replay/transparency/analysis of event stream" 原词，最接近为 §D 可视化 + §F.1 观察回填。 |
| 限制：复杂任务与长文件编辑仍不足；工作流需大量手工设计 | §A，PDF p.17–18 | "Current agents still struggle with complex tasks"；"Current agent suffers a lot when editing long files"；"OpenHands's workflow still requires a substantial hand-crafted workload"。 |

## 官方代码

## 官方代码

（同节内后续路径省略 `official-code/openhands/` 前缀。）

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| Event/Action/Observation 基类及子类型 | `official-code/openhands/events/event.py:36`（class Event）、`events/action/action.py:22`、`events/observation/observation.py:7`；子类 `events/action/commands.py:13`（CmdRunAction）、`:43`（IPythonRunCellAction）、`events/action/files.py:10/32/62`、`events/action/browse.py:29`；观察 `events/observation/commands.py:93/168` | 统一事件模型的类型体系。 |
| 事件流=唯一存储：EventStream(EventStore)，逐条编号并落盘 JSON | `events/stream.py:44`（class EventStream）、`:158`（add_event，分配 `event._id`、`:183` 写 file_store）、`:125`（subscribe）；`events/event_store.py:42` docstring | 所有组件只读写事件流；持久化支撑 UI 展示与回放。 |
| AgentController 循环：step 驱动、状态机、动作入流、观察回填 | `controller/agent_controller.py:79`（class）、`:296`（step）、`:299`、`:759`（_step，stuck/budget/max_iterations 控制）、`:873`（add_event(action)）、`:428`、`:455` | 循环与状态机核心。 |
| Runtime：订阅事件流，Action→Observation | `runtime/base.py:89`（class Runtime）、`:121`（订阅）、`:242`（on_event）、`:278`（_handle_action）、`:477`（run_action）、`:310`（add_event(observation)） | 沙箱执行与观察回填。 |
| 沙箱内 action execution API（REST 服务） | `runtime/action_execution_server.py:582`（FastAPI）、`:639-640`（`@app.post('/execute_action')`）、`:657`、`:764` | 对应论文 §2.2/§F 的 runtime client。 |
| CodeActAgent 及委托触发 | `agenthub/codeact_agent/codeact_agent.py:27`（class）、`:97`（step）；`agenthub/codeact_agent/function_calling.py:106-110`（delegate_to_browsing_agent → AgentDelegateAction(agent='BrowsingAgent')） | 默认通用 agent 与委派工具（快照无 delegator_agent.py）。 |
| 委托事件与子控制器 | `events/action/agent.py:86`（AgentDelegateAction）、`events/observation/delegate.py:8`（AgentDelegateObservation）、`controller/agent_controller.py:655`（start_delegate，delegate_level+1、共享 metrics） | 多 agent 协作机制。 |
| 对话记忆与回放 | `memory/conversation_memory.py:47`（class）、`:54`（process_events）、`:161`、`:302`；`controller/state/state.py:43`（class State）、`:85`（history）；`controller/replay.py:9`（ReplayManager）、`:57`、`:74`、`:82` | 事件流→LLM 消息；轨迹回放。 |

行号以 `source-packet.json` 固定的官方代码 revision 为准。
