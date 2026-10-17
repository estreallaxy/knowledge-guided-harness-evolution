from typing import Dict
from transformers import AutoConfig

# Assume a logger is configured in your application's scope
import logging
logger = logging.getLogger(__name__)

# Import the specific patching function from its module
from .streamingllm import patch_qwen3_with_streamingllm
from .rkv import patch_qwen3_with_rkv

def apply_kv_cache_patch(model_id: str, cache_impl_name: str, cache_config: Dict):
    """
    Dispatches to the correct patching function based on the cache_impl_name and model architecture.
    This function should be called *before* the model is loaded.
    """
    # Get the model's architecture name from its config before loading the full model
    config = AutoConfig.from_pretrained(model_id)
    model_arch = config.architectures[0]

    if cache_impl_name == "streamingllm":
        if model_arch == "Qwen3ForCausalLM":
            # Pass the config object to the patcher, not the model object
            patch_qwen3_with_streamingllm(config, cache_config)
        else:
            logger.warning(f"StreamingLLM patch not implemented for architecture: {model_arch}")
    
    elif cache_impl_name == "rkv":
        if model_arch == "Qwen3ForCausalLM":
            patch_qwen3_with_rkv(config, cache_config)
        else:
            logger.warning(f"R-KV patch not implemented for architecture: {model_arch}")
        
    elif cache_impl_name in ["quantized", "dynamic", "static", None]:
        # These are native implementations and require no patching.
        pass
    
    else:
        logger.warning(f"Unknown cache_implementation '{cache_impl_name}'. No patch will be applied.")
    
    return config