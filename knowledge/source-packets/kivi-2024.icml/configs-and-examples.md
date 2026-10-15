# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- `pyproject.toml`
- `requirements.txt`
- `quant/setup.py`
- `config/dataset2prompt.json`
- `long_context_example.py`
- `config/dataset2maxlen.json`
- `config/model2maxlen.json`
- `config/model2path.json`
- `example.py`

## Upstream command excerpts

```text
conda create -n kivi python=3.10
conda activate kivi
pip install --upgrade pip  # enable PEP 660 support
pip install -e .
```

```text
cd quant && pip install -e .
```

```text
# LLaMA model with KIVI
import torch
import os
from models.llama_kivi import LlamaForCausalLM_KIVI
from transformers import LlamaConfig, AutoTokenizer
config = LlamaConfig.from_pretrained("meta-llama/Llama-2-7b-hf")

config.k_bits = K_BITS # current support 2/4 bit for KV Cache
config.v_bits = V_BITS # current support 2/4 bit for KV Cache
config.group_size = GROUP_SIZE
config.residual_length = RESIDUAL_LENGTH # the number of recent fp16 tokens
CACHE_DIR = PATH_TO_YOUR_SAVE_DIR

model = LlamaForCausalLM_KIVI.from_pretrained(
    pretrained_model_name_or_path='meta-llama/Llama-2-7b-hf',
    config=config,
    cache_dir=CACHE_DIR,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    device_map="auto",
)

tokenizer = AutoTokenizer.from_pretrained(
    'meta-llama/Llama-2-7b-hf', 
    use_fast=False, 
    trust_remote_code=True, 
    tokenizer_type='llama')

# Inference
# e.g., model.generate(...)
```

```text
python example.py
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
