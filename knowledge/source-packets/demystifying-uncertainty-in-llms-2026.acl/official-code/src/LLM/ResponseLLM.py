"""
Response LLM wrapper (Ray + vLLM).

- Configuration is provided via PolicyLLMConfig (loaded from external YAML).
- Ray actor holds the vLLM engine and runs on one or more GPUs.
- This wrapper only returns generated text; it does NOT compute logprobs.
"""

import ray


from src.utils.config_loader import LLMConfig


@ray.remote

class ResponseLLM:
    """
    Public wrapper for the response model.

    - Takes a PolicyLLMConfig (from external YAML).
    - Internally owns one Ray actor (_ResponseLLMWorker).
    - That actor occupies cfg.num_gpus GPUs, and vLLM uses cfg.tensor_parallel_size.
    - The main API is `generate(...)`, which returns generated text(s).
    """

    def __init__(self, cfg: LLMConfig):

        self.cfg = cfg
