from . import agent_registry
from .llm_eval_multi_agent import LLMEvalAgent


@agent_registry.register("final_debate_multi")
class FinalDebateMultiAgent(LLMEvalAgent):
    predict: str = ""
    reasoning: str = ""
    final_answer: str = ""

    def _parse(self, response, env=None):
        parsed = super()._parse(response, env)
        self.final_answer = parsed.return_values.get("final_answer", "")
        return parsed

    def reset(self):
        super().reset()
        self.final_answer = ""
