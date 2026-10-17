import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os

from tool.tool_box import ToolManager
from utils.common import SandboxResponse, ColorWrapper
from utils.enumeration import EXEC_CODE
from core.assistant import Planner
from llm.openai_utils import MODEL_TYPE
from prompt.tool_generator import ToolGeneratorPrompt
from prompt.tool_validator import ToolValidatorPrompt
from core.sandbox import Sandbox
from utils.utils import parse_json_msg
from tool.tool_wrapper import ToolWrapper

from ablation_configs import NO_TOOL_VALIDATION

class ToolGenerator:
    def __init__(self, file_context, code_context, model_type: MODEL_TYPE=MODEL_TYPE.GPT_4o):
        self.generator = Planner(
            sys_prompt=ToolGeneratorPrompt.SYSTEM_PROMPT.replace("[file_context]", str(file_context)).replace("[code_context]", str(code_context)),
            model_type=model_type,
            name="ToolGenerator"
        )

    def chat(self, tool_description: str, feedback: dict) -> str:        
        """
        Generate a tool based on the description and arguments.
        Returns the generated tool code as a string.
        """
        user_prompt = ToolGeneratorPrompt.USER_PROMPT.format(
            tool_description=tool_description,
            feedback=feedback
        )
        response = self.generator.ask(prompt=user_prompt).strip()
        response = parse_json_msg(response)
        return response
    
    def save(self, save_dir: str):
        """
        Save the generator's state to a file.
        This can be extended to save more metadata if needed.
        """
        self.generator.save(save_dir)

class ToolValidator:
    def __init__(self, file_context: str, code_context: str, model_type: MODEL_TYPE=MODEL_TYPE.GPT_4o):
        self.validator = Planner(
            sys_prompt=ToolValidatorPrompt.SYSTEM_PROMPT.replace("[file_context]", str(file_context)).replace("[code_context]", str(code_context)),
            model_type=model_type,
            name="ToolValidator"
        )

    def chat(self, tool_description: str, tool_code: str, tool_call: str, execution_feedback: str) -> dict:
        """
        Validate the tool implementation based on the description and arguments.
        Returns a dictionary with assessment, reason, and examples.
        """
        user_prompt = ToolValidatorPrompt.USER_PROMPT.format(
            tool_description=tool_description,
            tool_code=tool_code,
            execution_command=tool_call,
            execution_feedback=execution_feedback
        )
        response = self.validator.ask(prompt=user_prompt).strip()
        response = parse_json_msg(response)

        return response

    def save(self, save_dir: str):
        """
        Save the validator's state to a file.
        This can be extended to save more metadata if needed.
        """
        self.validator.save(save_dir)

class ToolExecutor:
    def __init__(self, sandbox: Sandbox):

        # copy the sandbox
        self.sandbox = sandbox.copy()

        self.work_dir = "shadow_tool"
        os.makedirs(self.work_dir, exist_ok=True)

        # add a __init__.py
        with open(os.path.join(self.work_dir, "__init__.py"), 'w', encoding="utf-8") as f:
            f.write("\n\n")

    def add_tool(self, tool_name: str, tool_code: str):
        with open(os.path.join(self.work_dir, f"{tool_name}.py"), 'w', encoding="utf-8") as f:
            f.write(tool_code)
    
    def run_tool(self, tool_name: str, tool_code: str, tool_call: str) -> dict:
        self.add_tool(tool_name, tool_code)

        code_snippet = [
            f"sys.path.append(r'{self.work_dir}')",
            f"from {tool_name} import {tool_name}",
            f"{tool_call}"
        ]

        execute_response = self.sandbox.shadow_step("\n".join(code_snippet))
        return execute_response

class ToolCreator:
    def __init__(self, 
        model_type: MODEL_TYPE, 
        no_color_print: bool = False
        ):
        self.tool_generator = None
        self.tool_validator = None
        self.shadow_executor = None

        self.colorWrapper = ColorWrapper(enable_color=not no_color_print)

        self.model_type = model_type
        self.tool_wrapper = ToolWrapper(model_type=self.model_type)

    def save(self, save_dir: str):
        """
        Save the creator's state to a file.
        This can be extended to save more metadata if needed.
        """
        if self.tool_generator:
            self.tool_generator.save(save_dir)
        if self.tool_validator:
            self.tool_validator.save(save_dir)

    def create_tool(self, msg: dict, sandbox: Sandbox, prior_tool_meta: dict = None, execution_feedback: str = ""):
        assert msg.get("action", None) == "toolgen", "Action must be 'toolgen' for tool generation."

        file_context = sandbox.get_unified_mem_desc()
        code_context = sandbox.get_code_context()
        self.tool_generator = ToolGenerator(file_context=file_context, code_context=code_context, model_type=self.model_type)
        self.tool_validator = ToolValidator(file_context=file_context, code_context=code_context, model_type=self.model_type)
        self.shadow_executor = ToolExecutor(sandbox=sandbox)

        tool_description = msg.get("params", {}).get("tool_description", "")
        tool_args = msg.get("params", {}).get("tool_args", [])
        tool_description += f"\nTool Arguments: {tool_args}"
        prior_tool_id = ""

        validation_feedback = {}
        if prior_tool_meta:
            prior_tool_id = prior_tool_meta.get("tid", "")
            validation_feedback = {
                "assessment": "Code execution failed.",
                "prior_code": prior_tool_meta.get("code", ""),
                "prior_feedback": execution_feedback
            }
        
        generation_results = {}
        max_generation_steps = 3
        generation_step = 0
        while validation_feedback.get("assessment", None) != "success" and generation_step < max_generation_steps:
            generation_results = self.tool_generator.chat(tool_description=tool_description, feedback=validation_feedback)
            tool_description = generation_results.get("tool_description", tool_description)
            tool_name = generation_results.get("tool_name", "")
            tool_code = generation_results.get("tool_code", "").strip().strip("```python").strip("```")
            tool_call = generation_results.get("tool_call", "").strip().strip("```python").strip("```")

            if NO_TOOL_VALIDATION:
                validation_feedback = {
                    "assessment": "success",
                    "reason": "",
                    "examples": []
                }
                break

            execution_feedback = self.shadow_executor.run_tool(tool_name=tool_name, tool_code=tool_code, tool_call=tool_call)

            validation_feedback = self.tool_validator.chat(tool_description=tool_description, tool_code=tool_code, tool_call=tool_call, execution_feedback=str(execution_feedback))
            generation_step += 1

            if validation_feedback is None or validation_feedback == {}:
                validation_feedback = {
                    "assessment": "success",
                    "reason": "",
                    "examples": ""
                }

        if validation_feedback.get("assessment", None) != "success":
            print(self.colorWrapper.RED + f"Tool generation failed after {generation_step} steps.")
            return {
                "status": "failure",
                "generation": generation_results,
                "feedback": validation_feedback
            }

        # success, then wrap the tool
        tool_meta = self.tool_wrapper.create_tool_from_script(
            tool_description=generation_results.get("tool_description", ""),
            tool_args=generation_results.get("tool_args", []),
            tool_code=generation_results.get("tool_code", ""),
            tool_id=prior_tool_id
        )

        if tool_meta == {}:
            print(self.colorWrapper.RED + f"Tool wrapping failed.")
            return {
                "status": "failure",
                "generation": generation_results,
                "feedback": "Tool wrapping failed."
            }
        else:
            return {
                "status": "success",
                "generation": tool_meta,
                "feedback": "",
            }
