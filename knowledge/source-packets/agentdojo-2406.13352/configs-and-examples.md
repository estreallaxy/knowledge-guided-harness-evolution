# Configs and examples

##Environment and configuration entry

|document|use|
| --- | --- |
| `pyproject.toml` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `README.md` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `.devcontainer/Dockerfile` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `examples/README.md` |Dependencies, parameters, configuration, or minimal examples required by the core method.|

## Method access entrance

|document|Usage|
| --- | --- |
| `src/agentdojo/agent_pipeline/__init__.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/agent_pipeline.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/base_pipeline_element.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/basic_elements.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/errors.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/ground_truth_pipeline.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/pi_detector.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `src/agentdojo/agent_pipeline/planner.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|

## Local saving range

`official-code/` only preserves the paper method's core implementation, direct dependency interfaces, and the minimum configuration, examples, tests, and licenses. Large external datasets, copies of common frameworks, caches, and paper experiment outputs are not included.
