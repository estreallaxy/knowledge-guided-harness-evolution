# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `dev/requirements.txt`
- `tests/test_random_config_generation.py`
- `tests/test_task_from_config.py`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/dashboard_retrieval_value_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_minmax_task.json`
- `src/browsergym/workarena/data_files/task_configs/report_retrieval_value_task.json`
- `tests/test_task_setup.py`
- `src/browsergym/workarena/config.py`
- `src/browsergym/workarena/data_files/task_configs/all_menu.json`
- `src/browsergym/workarena/data_files/task_configs/impersonation_users.json`
- `src/browsergym/workarena/data_files/task_configs/order_apple_mac_book_pro15_task.json`
- `src/browsergym/workarena/data_files/task_configs/order_apple_watch_task.json`
- `src/browsergym/workarena/data_files/task_configs/order_development_laptop_pc_task.json`
- `src/browsergym/workarena/data_files/task_configs/order_ipad_mini_task.json`
- `src/browsergym/workarena/data_files/task_configs/order_ipad_pro_task.json`
- `src/browsergym/workarena/data_files/task_configs/order_loaner_laptop_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_asset_list_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_change_request_list_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_hardware_list_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_incident_list_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_service_catalog_item_list_task.json`
- `src/browsergym/workarena/data_files/task_configs/sort_user_list_task.json`
- `src/browsergym/workarena/tasks/scripts/generate_dashboard_configs.py`
- `src/browsergym/workarena/tasks/compositional/utils/infeasible_configs.py`

## Upstream command excerpts

```text
pip install browsergym-workarena
```

```text
playwright install
```

```text
import random

from browsergym.core.env import BrowserEnv
from browsergym.workarena import ATOMIC_TASKS
from time import sleep

random.shuffle(ATOMIC_TASKS)
for task in ATOMIC_TASKS:
    print("Task:", task)

    # Instantiate a new environment
    env = BrowserEnv(task_entrypoint=task,
                    headless=False)
    env.reset()

    # Cheat functions use Playwright to automatically solve the task
    env.chat.add_message(role="assistant", msg="On it. Please wait...")
    cheat_messages = []
    env.task.cheat(env.page, cheat_messages)

    # Send cheat messages to chat
    for cheat_msg in cheat_messages:
        env.chat.add_message(role=cheat_msg["role"], msg=cheat_msg["message"])

    # Post solution to chat
    env.chat.add_message(role="assistant", msg="I'm done!")

    # Validate the solution
    reward, stop, message, info = env.task.validate(env.page, cheat_messages)
    if reward == 1:
        env.chat.add_message(role="user", msg="Yes, that works. Thanks!")
    else:
        env.chat.add_message(role="user", msg=f"No, that doesn't work. {info.get('message', '')}")

    sleep(3)
    env.close()
```

```text
import random

from browsergym.core.env import BrowserEnv
from browsergym.workarena import get_all_tasks_agents
 
AGENT_L2_SAMPLED_SET = get_all_tasks_agents(filter="l2")
 
AGENT_L2_SAMPLED_TASKS, AGENT_L2_SEEDS = [sampled_set[0] for sampled_set in AGENT_L2_SAMPLED_SET], [
    sampled_set[1] for sampled_set in AGENT_L2_SAMPLED_SET
]
from time import sleep

for (task, seed) in zip(AGENT_L2_SAMPLED_TASKS, AGENT_L2_SEEDS):
    print("Task:", task)

    # Instantiate a new environment
    env = BrowserEnv(task_entrypoint=task,
                    headless=False)
    env.reset()

    # Cheat functions use Playwright to automatically solve the task
    env.chat.add_message(role="assistant", msg="On it. Please wait...")
    
    for i in range(len(env.task)):
        sleep(1)
        env.task.cheat(page=env.page, chat_messages=env.chat.messages, subtask_idx=i)
        sleep(1)
        reward, done, message, info = env.task.validate(page=env.page, chat_messages=env.chat.messages)
   
    if reward == 1:
        env.chat.add_message(role="user", msg="Yes, that works. Thanks!")
    else:
        env.chat.add_message(role="user", msg=f"No, that doesn't work. {info.get('message', '')}")

    sleep(3)
    env.close()
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
