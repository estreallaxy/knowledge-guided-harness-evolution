# Configs and examples

## Environment and configuration entry

|document|use|
| --- | --- |
| [pyproject.toml](official-code/pyproject.toml) |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| [README.md](official-code/README.md) |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| [.devcontainer/Dockerfile](official-code/.devcontainer/Dockerfile) |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| [examples/README.md](official-code/examples/README.md) |Dependencies, parameters, configuration, or minimal examples required by the core method.|

## Method access entrance

|document|Usage|
| --- | --- |
| [src/agentdojo/agent_pipeline/__init__.py](official-code/src/agentdojo/agent_pipeline/__init__.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/agent_pipeline.py](official-code/src/agentdojo/agent_pipeline/agent_pipeline.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/base_pipeline_element.py](official-code/src/agentdojo/agent_pipeline/base_pipeline_element.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/basic_elements.py](official-code/src/agentdojo/agent_pipeline/basic_elements.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/errors.py](official-code/src/agentdojo/agent_pipeline/errors.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/ground_truth_pipeline.py](official-code/src/agentdojo/agent_pipeline/ground_truth_pipeline.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/pi_detector.py](official-code/src/agentdojo/agent_pipeline/pi_detector.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| [src/agentdojo/agent_pipeline/planner.py](official-code/src/agentdojo/agent_pipeline/planner.py) |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|

## Local saving range

`official-code/` only preserves the paper method's core implementation, direct dependency interfaces, and the minimum configuration, examples, tests, and licenses. Large external datasets, copies of common frameworks, caches, and paper experiment outputs are not included.

Editorial clarification (2026-10-22): the listed files are retained source references, not a validated installation or runnable end-to-end entry. Historical page/title checks are preserved; no new conference, runtime, detector, benchmark or H0 verification was performed.
