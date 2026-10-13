# Configs and examples

The following commands and paths are taken from`official-code/README.md`(revision`d63f9ae18959dc7215ff62899c94c5e8c56847ae`),
Not executed on this machine. Before execution, please confirm that the upstream README has not been updated, and abide by the "credentials only use local files and do not store them in the database".

## Running prerequisites

|project|Require|source|
| --- | --- | --- |
| Python | 3.11+ |Upstream README badge and Installation section|
|rely|`pip install -e .`(repository root`pyproject.toml`)|Upstream README|
|external environment| AppWorld (`git lfs` + `pip install -e .` + `appworld install --repo` + `appworld download data`) |Upstream README Quickstart|
|model credentials|OpenAI compatible key, write`configs/private_config.yaml`|Upstream README Configuration|
|Paper setting|**gpt-4.1 / gpt-4.1-mini** for agent and compressor; Qwen3/Phi-4 series small models for distillation|Paper table 1/2/13Table Notes|

## Upstream example commands (AppWorld + history compression)

```bash
git clone https://github.com/StonyBrookNLP/appworld && cd appworld
git lfs install && pip install -e . && appworld install --repo && appworld download data

git clone https://github.com/microsoft/acon.git && cd acon
mv /path/to/appworld/data /path/to/acon/experiments/appworld
pip install -e .
#Put openai_key in configs/private_config.yaml

cd experiments/appworld
python run_all.py \
  --split train \
  --model_name gpt-4.1-mini \
  --tag baseline \
  --co_config_path configs/context_opt/gpt-4.1-mini_history.yaml
# Result directory: experiments/appworld/outputs/gpt-4.1-mini_baseline/
```

Guide to optimization and distillation of the entrance:`experiments/appworld/run_ctxopt_pipeline.py`(`main`),
The prompt template is at`experiments/prompt_optimizer/`, and the entrances to OfficeBench and 8-objective QA are respectively there.
`experiments/`subdirectory (the OfficeBench task set was included with the snapshot).

## Configuration snippet

```yaml
# configs/private_config_dummy.yaml (as is upstream, only placeholder keys)
openai_key: <YOUR_OPENAI_KEY_HERE>
```

## Unconfirmed items (written as unknown)

- The exact seed, temperature, concurrency and retry settings of each upstream experiment are not given in the paper, and the code has not been checked one by one by this package.
- The correspondence between`experiments/appworld/configs/context_opt/*.yaml`and the rows of Table 1 of the paper: not compared one by one.
- Complete data entry for OfficeBench and 8-objective QA: included with the snapshot (`experiments/officebench/`,`experiments/smolagents/data/`).
