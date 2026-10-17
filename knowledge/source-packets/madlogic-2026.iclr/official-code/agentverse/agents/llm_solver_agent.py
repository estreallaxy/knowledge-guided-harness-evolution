import asyncio
from dataclasses import dataclass
from string import Template

from agentverse.message import StructuredPrompt


@dataclass
class SolverResult:
    answer: str = ""
    reasoning: str = ""
    raw_output: str = ""
    success: bool = True
    error_message: str = ""


class LLMSolverAgent:
    def __init__(self, name, display_name, llm, output_parser, prompt_template,
                 role_description="", instruction="", max_retry=3):
        self.name = name
        self.display_name = display_name
        self.llm = llm
        self.output_parser = output_parser
        self.prompt_template = prompt_template
        self.role_description = role_description
        self.instruction = instruction
        self.max_retry = max_retry

    def _prompt(self, context, question, options):
        text = Template(self.prompt_template).safe_substitute(
            agent_name=self.name, role_description=self.role_description,
            context=context, question=question, options=options, instruction=self.instruction,
        )
        return StructuredPrompt(user_content=text)

    async def _request(self, prompt, parse=True):
        for attempt in range(self.max_retry):
            try:
                response = await self.llm.agenerate_response(prompt, [])
                return self.output_parser.parse(response) if parse else response
            except Exception:
                if attempt + 1 == self.max_retry:
                    raise
                await asyncio.sleep(min(2 ** attempt, 5))

    async def asolve(self, context, question, options):
        try:
            parsed = await self._request(self._prompt(context, question, options))
            values = parsed.return_values
            return SolverResult(answer=values["answer"], reasoning=values["reasoning"],
                                raw_output=values["output"])
        except Exception as error:
            return SolverResult(success=False, error_message=str(error))

    def solve(self, context, question, options):
        return asyncio.run(self.asolve(context, question, options))
