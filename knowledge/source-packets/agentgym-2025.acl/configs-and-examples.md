# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `agentenv-alfworld/pyproject.toml`
- `agentenv-babyai/pyproject.toml`
- `agentenv-lmrlgym/pyproject.toml`
- `agentenv-sciworld/pyproject.toml`
- `agentenv-searchqa/pyproject.toml`
- `agentenv-sqlgym/pyproject.toml`
- `agentenv-textcraft/pyproject.toml`
- `agentenv-tool/pyproject.toml`
- `agentenv-tool/requirements.txt`
- `agentenv-webarena/pyproject.toml`
- `agentenv-webshop/pyproject.toml`
- `agentenv/pyproject.toml`
- `agentenv-tool/Toolusage/requirements.txt`
- `agentenv-webarena/webarena/requirements.txt`
- `agentenv-webarena/webarena/setup.cfg`
- `agentenv-webarena/webarena/setup.py`
- `agentenv-webshop/webshop/requirements.txt`
- `agentenv-tool/Toolusage/toolusage/setup.cfg`
- `agentenv-tool/Toolusage/toolusage/setup.py`
- `agentenv-webshop/webshop/baseline_models/requirements.txt`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_eval_fail.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_eval_success.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_url_func_1.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/func_url_func_2.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_element_exact_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_exact_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/html_content_url_comb.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/string_match.json`
- `agentenv-webarena/webarena/tests/test_evaluation_harness/configs/url_exact_match.json`
- `agentenv-alfworld/configs/mappings_test.json`

## Upstream command excerpts

```text
### Trajectory Set: AgentTraj

The trajectory set AgentTraj-L is available on Hugging Face: [AgentGym/AgentTraj-L](https://huggingface.co/datasets/AgentGym/AgentTraj-L).

Here is an example:
```

```text
## 🛠 Usage & Quick Start

This project contains the `agentenv` python package and the integrated environments.

### Setup agentenv pacakage

#### from PyPI
```

```text
#### from Source
```

```text
Depending on which environments you want to use, `cd` into the corresponding `agentenv-*` folder and follow the `README.md` inside.

### Tutorials

- Evaluation: [01-evaluation](https://github.com/WooooDyy/AgentGym/blob/main/docs/tutorials/en/01-evaluation.md)
- Behavioral Cloning: [02-behavioral-cloning](https://github.com/WooooDyy/AgentGym/blob/main/docs/tutorials/en/02-behavioral-cloning.md)
- AgentEvol: [03-AgentEvol](https://github.com/WooooDyy/AgentGym/blob/main/docs/tutorials/en/03-AgentEvol.md)
- Env Visualization: [04-Env-Visualization](https://github.com/WooooDyy/AgentGym/blob/main/docs/tutorials/en/04-Env-Visualization.md)
- 2nd Development: [05-2nd-Development](https://github.com/WooooDyy/AgentGym/blob/main/docs/tutorials/en/05-2nd-Development.md)

### Examples

- See [AgentGym/agentenv/examples](https://github.com/WooooDyy/AgentGym/tree/main/agentenv/examples)

## Main Experimental Results

<div align=center><img src="./assets/main_results.png" width="90%" /></div>

## 📧 Contact

- zhxi22@m.fudan.edu.cn

## 🔖 Citation
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
