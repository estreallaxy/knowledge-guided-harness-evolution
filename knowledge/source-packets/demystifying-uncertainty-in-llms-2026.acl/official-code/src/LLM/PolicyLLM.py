"""
Policy LLM wrapper (Ray + vLLM).

- All configuration is injected via PolicyLLMConfig (loaded from external YAML).
- The Ray actor requests cfg.num_gpus GPU resources.
- vLLM uses cfg.tensor_parallel_size for tensor parallelism.
"""

import ray

from src.utils.config_loader import LLMConfig



@ray.remote
class PolicyLLM:
    """
    High-level wrapper used by the rest of the codebase.
    - Holds a single Ray actor (_PolicyLLMWorker).
    - The actor uses cfg.num_gpus GPUs in total.
    - vLLM inside the actor uses cfg.tensor_parallel_size for TP.
    - Upper layers only call generate(...) and do not care about GPU details.
    """
    def __init__(self, cfg: LLMConfig):

        self.cfg = cfg
