# Configs and examples

##Environment and configuration entry

|document|use|
| --- | --- |
| `README.md` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `data_prepare/process_example.py` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/README.md` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `data_prepare/1_goal/config.json` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `data_prepare/2_private_info/config.json` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/configs/judge_config.json` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/configs/prompt_template.json` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/commands/example/gpt4o.sh` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` |Dependencies, parameters, configuration, or minimal examples required by the core method.|
| `SENSE/commands/example/llama3_8b.sh` |Dependencies, parameters, configuration, or minimal examples required by the core method.|

## Method access entrance

|document|Usage|
| --- | --- |
| `SENSE/initialization.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/metric.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/run_eval.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/simulation.py` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/commands/example/gpt4o.sh` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/commands/example/heter_gpt4o_gpt35.sh` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/commands/example/llama3_8b.sh` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|
| `SENSE/configs/judge_config.json` |Method implementation or direct execution entry; complete the model, data and external services according to the official README.|

## Local saving range

`official-code/` only preserves the paper method's core implementation, direct dependency interfaces, and the minimum configuration, examples, tests, and licenses. Large external datasets, copies of common frameworks, caches, and paper experiment outputs are not included.
