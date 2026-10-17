from agentverse.answers import extract_answer
from agentverse.parser import OutputParser, OutputParserError, output_parser_registry
from agentverse.utils import AgentFinish


@output_parser_registry.register("final_debate")
class FinalDebateParser(OutputParser):
    def parse(self, output, is_final=False, agent_name=None):
        text = output.content.strip()
        values = {"output": text}
        if is_final:
            answer = extract_answer(text)
            if not answer:
                raise OutputParserError("Missing or invalid final answer")
            values["final_answer"] = answer
        return AgentFinish(values, text)
