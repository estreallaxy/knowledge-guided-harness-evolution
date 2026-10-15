# Exact source anchors

## Paper

| Mechanism or evidence | Exact location | Supported claim and boundary |
| --- | --- | --- |
| POMDP runtime and termination | §3.1, PDF p.4 | Defines observations, executable actions, state transitions, terminal DONE/FAIL actions and final-state reward. |
| Observation/action interfaces | §3.1.1–3.1.2 and Table 2, PDF p.4 | Combines screenshots, UIA/DOM/OCR/session state with pyautogui or typed Computer actions. |
| Executable final-state evaluation | §3.1.3 and Table 3, PDF pp.4–5 | Uses application/system getters and deterministic comparison functions. |
| Isolation and scalable scheduling | §3.3, PDF p.6 | Places a Windows 11 VM inside a Docker boundary and connects task scheduling, agent, evaluator and logs; cloud workers aggregate runs. |
| Baseline evidence | §4.2 and Table 4, PDF p.8 | Compares observation/grounding variants and shows the remaining human-agent gap. |

## Official code

The paths below refer to the retained snapshot of [https://github.com/microsoft/WindowsAgentArena](https://github.com/microsoft/WindowsAgentArena) at upstream revision `6d39ed88c545a0d40a7a02e39b928e278df7332b`.

| Mechanism or evidence | Snapshot path | Role |
| --- | --- | --- |
| Desktop environment | `src/win-arena-container/client/desktop_env/envs/desktop_env.py` | Implements reset, step, observation collection and evaluator invocation. |
| Action API | `src/win-arena-container/client/desktop_env/envs/actions.py` | Defines the executable computer action surface exposed to an agent. |
| Setup and VM controllers | `src/win-arena-container/client/desktop_env/controllers` | Applies initial state and communicates with the isolated VM. |
| Generic state evaluators | `src/win-arena-container/client/desktop_env/evaluators` | Retrieves application/system state and computes document, browser, settings and file metrics. |
| Trajectory capture and loop | `src/win-arena-container/client/trajectory_recorder.py; lib_run_single.py` | Records observations, actions, rewards and termination for each step. |

The snapshot deliberately omits benchmark answers, task-specific target state, credentials, generated traces, datasets, model weights and files that are unnecessary to inspect the selected mechanism.

## Additional retained implementation anchors

- `src/win-arena-container/client/lib_run_single.py`
- `src/win-arena-container/client/run.py`
- `src/win-arena-container/client/desktop_env/evaluators/__init__.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/calc.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/chrome.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/edge.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/file.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/fileexplorer.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/general.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/gimp.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/impress.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/info.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/microsoftpaint.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/misc.py`
- `src/win-arena-container/client/desktop_env/evaluators/getters/msedge.py`

## Symbol-level code anchors

- `src/win-arena-container/client/lib_run_single.py:18` — `run_single_example`
- `src/win-arena-container/client/run.py:36` — `setup_logging`
- `src/win-arena-container/client/desktop_env/evaluators/getters/calc.py:5` — `get_conference_city_in_order`
- `src/win-arena-container/client/desktop_env/evaluators/getters/chrome.py:43` — `get_info_from_website`
- `src/win-arena-container/client/desktop_env/evaluators/getters/edge.py:27` — `get_url_shortcuts_on_desktop`
- `src/win-arena-container/client/desktop_env/evaluators/getters/file.py:11` — `get_content_from_vm_file`
- `src/win-arena-container/client/desktop_env/evaluators/getters/fileexplorer.py:9` — `get_vm_folder_exists_in_documents`
- `src/win-arena-container/client/desktop_env/evaluators/getters/general.py:9` — `get_vm_command_line`
- `src/win-arena-container/client/desktop_env/evaluators/getters/gimp.py:8` — `get_gimp_config_file`
- `src/win-arena-container/client/desktop_env/evaluators/getters/impress.py:10` — `get_background_image_in_slide`
- `src/win-arena-container/client/desktop_env/evaluators/getters/info.py:5` — `get_vm_screen_size`
- `src/win-arena-container/client/desktop_env/evaluators/getters/microsoftpaint.py:14` — `find_red_circle`
