# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `setup.cfg`
- `setup.py`
- `mtraining/requirements.txt`
- `mtraining/setup.py`
- `scbench/requirements.txt`
- `TriangleMix/ruler/requirements.txt`
- `experiments/infinite_bench/requirements.txt`
- `experiments/ruler/requirements.txt`
- `examples/run_hf_streaming.py`
- `examples/run_hf_streaming.sh`
- `LeanK/eval/RULER/config_models.sh`
- `LeanK/eval/RULER/config_tasks.sh`
- `minference/dist_ops/test/run_ring_pytests.sh`
- `mtraining/model_configs/qwen2/modeling_qwen2.py`
- `.pre-commit-config.yaml`
- `LeanK/run_example.py`
- `examples/run_hf.py`
- `examples/run_vllm.py`
- `minference/minference_configuration.py`
- `LeanK/eval/RULER/run.sh`
- `scbench/run_scbench.py`
- `TriangleMix/ruler/config_models.sh`
- `TriangleMix/ruler/config_tasks.sh`
- `experiments/ruler/config_models.sh`
- `experiments/ruler/config_tasks.sh`
- `minference/configs/GLM_4_9B_1M_instruct_kv_out_v32_fit_o_best_pattern.json`
- `minference/configs/Llama_3.1_70B_Instruct_128k_kv_out_v32_fit_o_best_pattern_v2.json`
- `minference/configs/Llama_3.1_8B_Instruct_128k_kv_out_v32_fit_o_best_pattern.json`
- `minference/configs/Llama_3.1_8B_Instruct_128k_kv_out_v32_fit_o_best_pattern_v2.json`
- `minference/configs/Llama_3_70B_Instruct_262k_kv_out_v32_fit_o_best_pattern.json`

## Upstream command excerpts

```text
pip install minference
```

```text
from minference import MInferenceConfig
supported_attn_types = MInferenceConfig.get_available_attn_types()
supported_kv_types = MInferenceConfig.get_available_kv_types()
```

```text
from minference import get_support_models
get_support_models()
```

```text
> uv pip install "sglang[all]>=0.4.6.post4"
>
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
