# Exact source anchors

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|Event flow structure: All interactive alignment to Action/Observation, Event stream record All history|§ 2.1, PDF p.3 (Fig.2 same page); § 1 p.2| "the event stream, which is a chronological collection of past actions and observations, including the agent's own actions and user interactions";Fig.2 "Event stream for tracking history of actions and observations". |
|Agent Cycle Abstract: step(state)action, implemented by the framework|§2.1 "Implement a New Age", PDF p.4 (Fig.3 same page)|"The core of the event action lies in the step play, which takes the current state as input and generales an application action." Note: The paper does not use the term "controller" and the controller only exists in code.|
|Runtime Sandbox: Quarantine Docker packaging for each mission, returning to observation through the REST API execution action inside the container| §2.2,PDF p.4–5;§F.1 p.20(Fig.4) |"For each task session, OpenHands spins up a securely identified contractor Sandbox, where all the actions from the event team are exported"; §F.1 "(6) the third components export results back as alternatives".|
|Agent commissioned: Agent DelegateAction Commission|§ 2.4, PDF p.5; evaluation supporting Tab.5 p.9| "a special action type AgentDelegateAction, which enables an agent to delegate a specific subtask to another agent… CodeActAgent… delegate web browsing tasks to the specialized BrowsingAgent". |
|Memory/History: history/incident stream, Fig.3| §2.1,PDF p.3–4(Fig.3) |State contains "accumulative post...metadata to track multi-agent development";`get_action_message`/`get_observation_message`Walk through state.history to construct LLM messages.|
|SWE-bench Outcome (26%)|§ 4.2 p.7 Text; Tab.4 p.8; Tab.3 p.7| "CodeActAgent v1.8, using claude-3.5-sonnet, achieves a competitive resolve rate of 26%";Tab.4 "SWE-Bench Lite…300 instances, w/o Hint":claude-3-5-sonnet@20240620 = 26.0($1.10),gpt-4o-2024-05-13 = 22.0($1.72). |
|Web/Miscellaneous Results (WebArena, GAIA, GPQA)| Tab.5 p.9;Tab.6 p.10;Tab.3 p.7 |WebArena (812 instances) BrowningAgent v1.0 claude-3-5-sonnet = 15.5 per cent, CodeAct v1.8 was commissioned = 15.3 per cent; MiniWoB+(125 envs)gpt-4o = 40.8 per cent; GAIA L1 (53 instances)gpt-4o = 32.1 per cent; GPQA diamond (198) claude = 52.0 per cent.|
|Event stream supports visualization| §D,PDF p.19;§F.1 p.20 |"This user directly confects with the events (§2.1) to control and visualize the treaties and runtime". Note: The paper does not contain the original term "replay/transparency/analysisof events cluster", closest to §D visualization + §F.1 observation backfill.|
|Limitations: Complex tasks and long document editing are still inadequate; workflow requires extensive manual design| §A,PDF p.17–18 | "Current agents still struggle with complex tasks";"Current agent suffers a lot when editing long files";"OpenHands's workflow still requires a substantial hand-crafted workload". |

# Official code

# Official code

(Excerpt`official-code/openhands/`prefix omitted from the subsequent path in the same section.

|Mechanism or evidence|File & Line Number|Role|
| --- | --- | --- |
| Event/Action/ObservationBase and subtypes| `official-code/openhands/events/event.py:36`(class Event),`events/action/action.py:22`,`events/observation/observation.py:7`;subcategories`events/action/commands.py:13`(CmdRunAction),`:43`(IPythonRunCellAction),`events/action/files.py:10/32/62`,`events/action/browse.py:29`;observation`events/observation/commands.py:93/168` |Harmonize the types of event model.|
|Event stream = sole storage: EventStream (EventStore), numbered by article and set aside| `events/stream.py:44`(class EventStream),`:158`(add event, distribution)`event._id`,`:183`Write file store,`:125`(subscribe);`events/event_store.py:42` docstring |All components read-and-written only event stream; lasting support for UI display and playback.|
|AgentController Loop: step drive, status machine, action flow, observation backfill| `controller/agent_controller.py:79`(class),`:296`(step),`:299`,`:759`(_step,stuck/budget/max_iterationsControl.`:873`(add_event(action)),`:428`,`:455` |Cycle and status core.|
|Runtme: Subscription Event Stream, Action| `runtime/base.py:89`(class Runtime),`:121`(Subscriptions),`:242`(on_event),`:278`(_handle_action),`:477`(run_action),`:310`(add_event(observation)) |Sandbox execution and observation backfill.|
|sandbox action evaluation API (REST service)| `runtime/action_execution_server.py:582`(FastAPI),`:639-640`(`@app.post('/execute_action')`),`:657`,`:764` |Corresponding paper §2.2/ § F rantime clit.|
|CodeActAgent and commission trigger| `agenthub/codeact_agent/codeact_agent.py:27`(class),`:97`(step);`agenthub/codeact_agent/function_calling.py:106-110`(delegate_to_browsing_agent → AgentDelegateAction(agent='BrowsingAgent')) |Default Universal Agent and Assign Tool (no snapshot agent.py).|
|Commission event and subcontroler| `events/action/agent.py:86`(AgentDelegateAction),`events/observation/delegate.py:8`(AgentDelegateObservation),`controller/agent_controller.py:655`(start delegate, future level+1, share media)|Multi-agent collaboration mechanism.|
|Dialogue memory and playback| `memory/conversation_memory.py:47`(class),`:54`(process_events),`:161`,`:302`;`controller/state/state.py:43`(class State),`:85`(history);`controller/replay.py:9`(ReplayManager),`:57`,`:74`,`:82` |Event flow LLM messages; trajectory playback.|

Line number is based on the`source-packet.json`fixed official code review.
