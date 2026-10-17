from agentverse.message import StructuredPrompt
from agentverse.parser import OutputParserError
from .llm_solver_agent import LLMSolverAgent, SolverResult


class PlanAndSolveAgent(LLMSolverAgent):
    def __init__(self, *args, extraction_trigger="Therefore, the answer is", **kwargs):
        super().__init__(*args, **kwargs)
        self.extraction_trigger = extraction_trigger

    async def asolve(self, context, question, options):
        reasoning = ""
        try:
            response = await self._request(self._prompt(context, question, options), parse=False)
            reasoning = response.content
            try:
                parsed = self.output_parser.parse(response)
                answer = parsed.return_values["answer"]
                raw = reasoning
            except OutputParserError:
                extraction = StructuredPrompt(user_content=(
                    f"Context: {context}\nQuestion: {question}\nOptions: {options}\n\n"
                    f"{reasoning}\n\n{self.extraction_trigger}"
                ))
                parsed = await self._request(extraction)
                answer = parsed.return_values["answer"]
                raw = reasoning + "\n\n" + parsed.return_values["output"]
            return SolverResult(answer=answer, reasoning=reasoning, raw_output=raw)
        except Exception as error:
            return SolverResult(reasoning=reasoning, success=False, error_message=str(error))
