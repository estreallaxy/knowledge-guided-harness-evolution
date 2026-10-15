# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `src/webapp/requirements.txt`
- `experiments/domain_agents/course_enroll/test_runtime.py`
- `experiments/domain_agents/course_enroll/config.yaml`
- `experiments/domain_agents/course_enroll/test_policy.py`
- `experiments/domain_agents/investment_agent/config.yaml`
- `experiments/domain_agents/investment_agent/test_policy.py`
- `src/worksheets/agent/config.py`
- `experiments/domain_agents/course_enroll/course_enroll.py`
- `experiments/domain_agents/course_enroll/course_enrollment.json`
- `experiments/domain_agents/investment_agent/investment_agent.py`
- `experiments/domain_agents/ticket_submission/services_general_info_chunked.json`
- `experiments/domain_agents/ticket_submission/ticket_submission.py`
- `experiments/domain_agents/yelpbot/yelpbot.py`
- `src/worksheets/core/runtime.py`
- `experiments/domain_agents/course_enroll/frontend/app_course_enroll.py`
- `experiments/domain_agents/course_enroll/frontend/app_course_enroll_gpt4.py`
- `experiments/domain_agents/investment_agent/frontend/app_investment_agent.py`
- `experiments/domain_agents/ticket_submission/frontend/app_service_now.py`
- `experiments/domain_agents/ticket_submission/frontend/app_service_now_gpt4.py`
- `experiments/domain_agents/yelpbot/frontend/app_restaurant.py`
- `experiments/domain_agents/yelpbot/frontend/app_restaurant_gpt4.py`
- `experiments/domain_agents/yelpbot/frontend/yelp_bot.json`
- `src/worksheets/config/settings.py`
- `src/worksheets/utils/logging_config.py`

## Upstream command excerpts

```text
git clone https://github.com/stanford-oval/genie-worksheets.git
cd worksheets
uv venv
source venv/bin/activate
uv sync
```

```text
from worksheets import Config
import os

# Define path to the prompts
current_dir = os.path.dirname(os.path.realpath(__file__))
prompt_dir = os.path.join(current_dir, "prompts")

# Load config from YAML file
config = Config.load_from_yaml(os.path.join(current_dir, "config.yaml"))
```

```text
from worksheets import Config, AzureModelConfig
import os

config = Config(
    semantic_parser=AzureModelConfig(
        model_name="azure/gpt-4o",
    ),
    response_generator=AzureModelConfig(
        model_name="azure/gpt-4o",
    ),
    knowledge_parser=AzureModelConfig(
        model_name="azure/gpt-4o",
    ),
    knowledge_base=AzureModelConfig(
        model_name="azure/gpt-4o",
    ),
    prompt_dir=prompt_dir,
)
```

```text
from worksheets.agent.config import agent_api
from worksheets.core.worksheet import get_genie_fields_from_ws
from uuid import uuid4

@agent_api("course_detail_to_individual_params", "Get course details")
def course_detail_to_individual_params(course_detail):
    if course_detail.value is None:
        return {}
    course_detail = course_detail.value
    course_detail = {}
    for field in get_genie_fields_from_ws(course_detail):
        course_detail[field.name] = field.value

    return course_detail

@agent_api("courses_to_take_oval", "Final API to enroll into a course")
def courses_to_take_oval(**kwargs):
    return {"success": True, "transaction_id": uuid4()}

@agent_api("is_course_full", "Check if a course is full")
def is_course_full(course_id, **kwargs):
    # Implementation here
    return False
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
