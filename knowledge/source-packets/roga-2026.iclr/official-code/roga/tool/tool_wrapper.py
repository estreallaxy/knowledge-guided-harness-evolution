import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from core.assistant import Planner, MODEL_TYPE
from prompt.tool_wrapper import ToolWrapperPrompt
from utils.utils import parse_json_msg

class ToolWrapper:
    """Wrapper for creating Tool functions from LLM-generated scripts with automatic package installation."""

    def __init__(
        self,
        model_type: MODEL_TYPE = MODEL_TYPE.GPT_4o
    ):
        self.generator = Planner(
            sys_prompt=ToolWrapperPrompt.SYSTEM_PROMPT,
            model_type=model_type,
            name="ToolWrapper"
        )

    def parse_script_metadata(self, tool_description: str, tool_args: list, tool_code: str) -> dict:
        """Extract metadata from the script using the LLM."""
        user_prompt = ToolWrapperPrompt.USER_PROMPT.format(tool_description=tool_description, tool_args=tool_args, tool_code=tool_code)
        response = self.generator.ask(prompt=user_prompt).strip()
        response = parse_json_msg(response)

        return response

    def create_tool_from_script(self, tool_description: str, tool_args: list, tool_code: str, tool_id: str="") -> tuple:
        """
        Create an Tool function from the generated info and code.
        """

        try:
            # Parse metadata from the script
            metadata = self.parse_script_metadata(tool_description, tool_args, tool_code)

            if tool_id != "":
                metadata["tid"] = tool_id
            else:
                metadata["tid"] = ""
            
            metadata["source"] = "dynamically-generated"

            # add the Tool to the tool box
            return metadata
            
        except Exception as e:
            print(f"Error creating Tool from script: {e}")
            return {}
        