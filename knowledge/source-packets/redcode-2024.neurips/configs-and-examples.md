# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `evaluation/RedCode_Gen/requirements.txt`
- `environment/OpenCodeInterpreter/demo/LICENSE`
- `environment/OpenCodeInterpreter/demo/README.md`
- `environment/OpenCodeInterpreter/demo/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/requirements.txt`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/pyproject.toml`
- `environment/OpenCodeInterpreter/evaluation/evalplus/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/setup.cfg`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tests/requirements.txt`
- `environment/OpenCodeInterpreter/evaluation/evalplus/evalplus/_experimental/evaluate_runtime.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/tools/tsr/run.py`
- `environment/OpenCodeInterpreter/evaluation/evalplus/.pre-commit-config.yaml`
- `evaluation/RedCode_Gen/config.py`
- `evaluation/RedCode_Exec/CA_evaluation/configs/container.py`
- `evaluation/RedCode_Exec/CA_evaluation/configs/evaluation.py`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/config_example/config.azure.example.json`
- `environment/OpenCodeInterpreter/data_collection/Local-Code-Interpreter/config_example/config.example.json`
- `evaluation/RedCode_Exec/main.py`
- `evaluation/RedCode_Gen/main.py`

## Upstream command excerpts

```text
git clone https://github.com/AI-secure/RedCode.git
```

```text
conda env create -f environment.yml
conda activate redcode
```

```text
./scripts/OCI_eval.sh
./scripts/RA_eval.sh
./scripts/CA_eval.sh
```

```text
@article{guo2024redcode,
  title={RedCode: Risky Code Execution and Generation Benchmark for Code Agents},
  author={Guo, Chengquan and Liu, Xun and Xie, Chulin and Zhou, Andy and Zeng, Yi and Lin, Zinan and Song, Dawn and Li, Bo},
  booktitle={Thirty-Eighth Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
  year={2024}
}
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
