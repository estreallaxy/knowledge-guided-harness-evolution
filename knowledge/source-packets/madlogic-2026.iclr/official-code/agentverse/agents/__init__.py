from agentverse.registry import Registry

agent_registry = Registry(name="AgentRegistry")

from .base import BaseAgent
from .llm_eval_multi_agent import LLMEvalAgent
from .final_debate_multi_agent import FinalDebateMultiAgent
