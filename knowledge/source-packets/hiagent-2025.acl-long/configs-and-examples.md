# Configs and examples

Line numbers are based on locally saved`official-code/`. The configuration can only be explained with the paper version, code review, AgentBoard environment and data; the values in the paper cannot be reproduced independently by a single YaML.

# Official Experiment Configuration

Upstream, four sets of HiAgent running configurations are placed in`eval_configs/hiagent/`, each set of YAML, containing`run`/`agent`/`llm`/`env`paragraphs. The four sets of`agent`are identical (`name: ContextEfficientAgent`, `memory_size: 100`, `need_goal: True`, `use_parser: True`) with the difference between `env.pddl.game_name`, `env_num_per_task` and `init_prompt_path`.

|Profile| `env.pddl.game_name` | `env_num_per_task` |Practically loaded prompt assets|Corresponding paper assignments|
| --- | --- | --- | --- | --- |
| `official-code/eval_configs/hiagent/blocksworld.yaml` | `[blockworld]` | 20 | `agentboard/prompts/VanillaAgent/pddl_vanilla_prompt.json` | Blocksworld（Table 1） |
| `official-code/eval_configs/hiagent/gripper.yaml` | `[gripper]` | 20 | `agentboard/prompts/ContextAgent/pddl.json` | Gripper（Table 1） |
| `official-code/eval_configs/hiagent/tyreworld.yaml` | `[tyreworld]` | 10（`problem_index: [2..9]`） | `agentboard/prompts/ContextAgent/pddl.json` | Tyreworld（Table 1–3、Table 4） |
| `official-code/eval_configs/hiagent/barman.yaml` | `[barman]` | 20 | `agentboard/prompts/ContextAgent/pddl_wretrieval.json` | Barman（Table 1） |

Each YAML also has a complete`env.jericho`section (20 Z-machine games, `ContextAgent/jericho.json`), so the Jericho experiment is started with the same YAML at `--tasks jericho` without a separate jericho profile.

Configure points and traps:

-`agent.name`is written in four YAMLs as `ContextEfficientAgent` (`blocksworld.yaml:11`), but only `ContextEfficientAgentV2` (`agentboard/agents/cme_final.py:21`) is included in the registration form. The actual effective value is derived from the command line`--agent`(`agentboard/eval_main.py:122-125`), which must be passed when running in an official script.
-`run.max_num_steps`is 30 (`blocksworld.yaml:2`) in YAML, but `eval_main.py:73` is unconditionally covered by command line values and official scripts are passed on 50.
-`agent.memory_size: 100`has nothing to do with the paper (the paper does not report the cross-reference), it is the upper limit of the window (`agentboard/agents/cme_final.py:222`).
- Whether or not to enable Observation Summarization is determined by the shell environment variable`EVALTASK`, rather than YAML: Take the "no summary" branch (`agentboard/agents/cme_final.py:115-120`) when the name contains`gripper`or`blocksworld`. This variable has to be changed when you digest or change jobs.
- `${PROJECT_PATH}` in `init_prompt_path` by `eval_main.py:45-51` YAML constructor, which must be exported in the environment.

# The official process entrance

|Steps|Entry|Annotations|
| --- | --- | --- |
|1. Building the environment| `official-code/setup.sh` |`pip install -r requirements.txt`, reload PDFL /Jericho/ALFWorld dependent; WebShop branch builds a search index (not included in this package). Require`conda create -n hiagent python=3.8.18`with available CUDA.|
|2. Taking NLTK data| `official-code/download_nltk.py` |Only`nltk.download('punkt')`and `punkt_tab`.|
|3... Keys|`agentboard/.env`(not included in this package)|Upstream README requests`PROJECT_PATH`and`OPENAI_API_KEY`; `eval_main.py:97` to`load_dotenv()`to read.|
|4. Run evaluation| `official-code/evaluate_model.sh` |For single file start script, see below.|
|5. Results|`{log_path}/all_results.txt`and sample records|Written by`SummaryLogger`/`TaskLogger`; these modules are not included in this package.|

Upstream README does not give a test command and there is no test package; the only "run example" is`evaluate_model.sh`.

# Duplicable commands

Original official script (`official-code/evaluate_model.sh:1-17`):

```bash
export PROJECT_PATH='[Project Path Here]'
export MODEL="gpt-4-turbo"
export STEP=50
export AGENT="ContextEfficientAgentV2"
export EVALTASK="blocksworld"

python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/blocksworld.yaml \
    --tasks pddl \
    --model gpt-4-turbo \
    --log_path ./logs/hiagent/analysis/"${AGENT}_${MODEL}_${STEP}" \
    --project_name none \
    --baseline_dir ./data/baseline_results \
    --max_num_steps 50 \
    --memory_size 100 \
    --agent ContextEfficientAgentV2
```

In exchange for a different assignment, three changes are required at the same time, otherwise it is not the thesis set:

```bash
# Tyreworld (the environment used in Tables 1/2/3/4)
export EVALTASK="tyreworld"        # This task is outside the "gripper/blocksworld" allowlist, so summarization is enabled
python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/tyreworld.yaml \
    --tasks pddl --model gpt-4-turbo --agent ContextEfficientAgentV2 \
    --max_num_steps 30 --memory_size 100 \
    --log_path ./logs/hiagent/tyreworld --baseline_dir ./data/baseline_results

# Jericho (reuse the env.jericho section from any YAML file)
export EVALTASK="jericho"
python agentboard/eval_main.py \
    --cfg-path eval_configs/hiagent/blocksworld.yaml \
    --tasks jericho --model gpt-4-turbo --agent ContextEfficientAgentV2 \
    --max_num_steps 30 --memory_size 100 \
    --log_path ./logs/hiagent/jericho --baseline_dir ./data/baseline_results
```

The above-mentioned commands are read in the equivalent code,** not implemented in this repository** (AgentBoard environment and data are missing, see below).

# Pre-data and external dependence (not included in this package)

|Dependency|Upstream|Annotations|
| --- | --- | --- |
|AgentBoard PDF Environment| `agentboard/environment/pddl_env/` |Part of 26M`agentboard/environment/`, containing pddlgym and field definitions, has been removed.|
|WebShop Environment & Chromedriver| `agentboard/environment/WebShop/` |Including 16M binary, removed; the five tasks of HiAgent do not use it.|
|Other Organiser| `${PROJECT_PATH}/data/pddl/*.jsonl`、`data/jericho/test.jsonl` |To download separately, as described by AgentBoard, not included.|
|result| `${PROJECT_PATH}/data/baseline_results` |For wandb contrast, not included.|
|GPT-4 Access| `OPENAI_API_KEY` |Thesis uses`gpt-4-turbo`as a policy and summarizer.|

# Local Save Range

`official-code/`26 files, 248K, covering "minimal core of access and authentication":

|Included|Contents|
| --- | --- |
|Institutional realization| `agentboard/agents/cme_final.py`（ContextEfficientAgentV2）、`agentboard/agents/summarize.py`（TrajectorySummarizer） |
|Interface and assembly| `agentboard/agents/base_agent.py`、`agentboard/agents/__init__.py`、`agentboard/common/registry.py`、`agentboard/llm/openai_gpt.py`、`agentboard/llm/__init__.py` |
|Against baseline| `agentboard/agents/vanilla_agent.py`（STANDARD） |
|Driver Cycle| `agentboard/eval_main.py`、`agentboard/tasks/pddl.py`、`agentboard/tasks/base_task.py`、`agentboard/tasks/__init__.py` |
|Prompt assets| `agentboard/prompts/prompt_template.py`、`prompts/ContextAgent/{pddl.json,pddl_wretrieval.json,jericho.json}`、`prompts/VanillaAgent/pddl_vanilla_prompt.json` |
|Configure and Script|`eval_configs/hiagent/*.yaml`(4 sets), `evaluate_model.sh`, `setup.sh`, `requirements.txt`, `download_nltk.py`, `README.upstream.md`|

|Removed|Reason|
| --- | --- |
| `agentboard/environment/`（26M） |Environmental Realization and Binary; including WebShop, Chromedriver, pddlgym, alfworld, Browner env, Scienceworld, etc.|
| `assets/`（996K） |Thesis diagram with PDF (`main.png`, `main.pdf`, `hiagent exp.png`)|
|`agentboard/utils/`remainder|3.2M tool and environment-coding code consisting of 1.35M`gpt2/tokenizer.json`, 1.04M`vocab.json`, 264K xsx test forms|
| `agentboard/utils/logging/` |`logger.py`(32K,wandb/plotly visualization and aggregation of indicators), `agent_logger.py` (2.5K colour log); both are AgentBoard shared facilities, on which `eval_main.py` and `tasks/pddl.py` depend, so the drive cycle in this package cannot be reported directly|
|Other| `ours_agent.py`、`react_agent.py`、`custom_*.py` |
|Other tasks accomplished|`tasks/{webshop,webbrowse,alfworld,babyai,scienceworld,tool,neural}.py`and`tasks/legacy/`|
| `.ipynb_checkpoints`、`.DS_Store`、`run_dev.log`、`logs/` |Cache and editor products|

Note: As`agentboard/environment/`and `agentboard/utils/logging/` have been eliminated and `agentboard/tasks/__init__.py:10-11` in the snapshot quotes `pddl_structured`, `babyai_train`, which does not exist upstream, this package** cannot run in situ**; it is used for reading mechanisms, alignment interfaces and preparation for access, not an enforceable environment.
