# Configurations and examples

## Runtime boundary

- Paper and repository versions are pinned in `source-packet.json`.
- Install dependencies from the retained upstream manifests.
- Supply model endpoints, credentials, datasets, and external services outside this packet. Never commit secrets.
- Use development or training splits for adaptation. Keep sealed benchmark test data outside retrieval and optimization state.

## Retained configuration and entry points

- No dedicated configuration filename was retained; use the upstream README and source entry points.

## Upstream command excerpts

```text
conda create -n homer python=3.10 -y
conda activate homer

conda install pytorch==2.3.1+cu118 torchvision==0.18.1+cu118 torchaudio==2.3.1+cu118 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install accelerate==0.32.1 matplotlib==3.9.1 sentencepiece==0.2.0 tqdm==4.66.4 transformers==4.42.4 protobuf==5.27.2
pip install flash-attn==2.6.1 --no-build-isolation
```

```text
from homer.modeling_llama import LlamaForCausalLM

# Setup arguments for HOMER
homer_args = {
    "max_chunk_len": 2048,
    "target_len": 2048,
    "layers_warmup": 12,
    "bias_path": "/path/to/bias_file.pt",
}

# Load model
model = LlamaForCausalLM.from_pretrained(
    meta-llama/Llama-2-7b-hf,
    device_map="auto",
    torch_dtype=torch.float16,
    attn_implementation="flash_attention_2",
    homer_args=homer_args,
)
```

```text
homer_prefix = model.create_homer_prefix(
    prefix_ids, context_ids, suffix_ids
)
output = model(input_ids, homer_prefix=homer_prefix)
```

```text
homer_prefix = model.create_homer_prefix(
    prefix_ids, context_ids, suffix_ids
)
output = model.generate(homer_prefix=homer_prefix)
```

These excerpts are preserved as upstream examples, not as a claim that the full system was rerun during packet ingestion.
