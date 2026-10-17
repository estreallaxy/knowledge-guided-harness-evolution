import asyncio
from string import Template

from agentverse.message import Message, StructuredPrompt
from . import agent_registry
from .base import BaseAgent


@agent_registry.register("llm_eval_multi")
class LLMEvalAgent(BaseAgent):
    question: str = ""
    context: str = ""
    options: str = ""
    final_prompt_to_use: str = ""
    normal_turn_instruction: str = ""
    error: str = ""

    def _fill_prompt_template(self, env_description="", env=None):
        is_final = env is None or env.cnt_turn == env.max_turns - 1
        instruction = self.final_prompt_to_use if is_final else self.normal_turn_instruction
        values = self.model_dump(exclude={"llm", "memory", "output_parser"})
        values.update(agent_name=self.name, env_description=env_description,
                      turn_specific_instruction=Template(instruction).safe_substitute(agent_name=self.name))
        prompt = Template(self.prompt_template).safe_substitute(values)
        system, separator, user = prompt.partition("${chat_history}")
        return StructuredPrompt(system_content=system.strip(), user_content=user.strip())

    def _parse(self, response, env=None):
        is_final = env is None or env.cnt_turn == env.max_turns - 1
        return self.output_parser.parse(response, is_final=is_final, agent_name=self.name)

    def _message(self, parsed):
        return Message(content=parsed.return_values["output"], sender=self.name,
                       receiver=self.get_receiver())

    def step(self, env_description=""):
        return asyncio.run(self.astep(env_description=env_description))

    async def astep(self, env=None, env_description=""):
        prompt = self._fill_prompt_template(env_description, env)
        response = None
        self.error = ""
        for attempt in range(self.max_retry):
            try:
                response = await self.llm.agenerate_response(prompt, self.memory.messages)
                parsed = self._parse(response, env)
                self.error = ""
                return self._message(parsed)
            except Exception as error:
                self.error = str(error)
                if attempt + 1 < self.max_retry:
                    await asyncio.sleep(min(2 ** attempt, 5))
        # Preserve the latest translation for the solver's explicit failure handling.
        return Message(content=response.content.strip() if response else "", sender=self.name,
                       receiver=self.get_receiver())

    def add_message_to_memory(self, messages):
        self.memory.add_message(messages)

    def reset(self):
        self.memory.reset()
        self.error = ""
