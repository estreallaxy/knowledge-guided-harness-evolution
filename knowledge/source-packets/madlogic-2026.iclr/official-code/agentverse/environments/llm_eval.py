from . import env_registry
from .basic import BasicEnvironment


@env_registry.register("llm_eval")
class LLMEvalEnvironment(BasicEnvironment):
    """Concurrent translation and answer debate environment."""
