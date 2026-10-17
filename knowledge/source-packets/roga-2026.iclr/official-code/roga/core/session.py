import os
import re
from pathlib import Path
from typing import Optional

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd

from dataset.dataloader import OfficeProblem
from prompt.planner import PlannerPrompt
from llm.openai_utils import MODEL_TYPE
from utils.common import SandboxResponse, ColorWrapper
from utils.enumeration import *
from utils.exceptions import *
from utils.utils import parse_json_msg

from core.assistant import Planner
from core.sandbox import Sandbox

from tool.tool_box import ToolManager
from tool.tool_creator import ToolCreator

from ablation_configs import NO_TOOL_MANAGEMENT

class Session:
    def __init__(
        self,
        problem: OfficeProblem,
        output_dir: Path,
        model_type: MODEL_TYPE,
        sandbox: Sandbox,
        verbose: bool = False,
        max_step: int = 10,
        no_color_print: bool = False,
    ):
        self.problem = problem
        self.output_dir = output_dir
        self.model_type = model_type
        self.max_step = max_step
        self.verbose = verbose
        self.colorWrapper = ColorWrapper(enable_color=not no_color_print)

        # Construct sandbox
        self.sandbox = sandbox
        self.sandbox.add_unified_mem("reasoning_traces", None, f"Instruction: {self.problem.instruction}")
        self.sandbox.add_unified_mem("reasoning_traces", None, f"Context of the file: {self.problem.context}")
        self.sandbox.open_file(str(self.problem.file_path), str(self.output_dir))
        os.makedirs(output_dir, exist_ok=True)

        # construct agent
        self.tool_creator = ToolCreator(model_type=self.model_type, no_color_print=no_color_print)
        self.tool_manager = ToolManager(no_color_print=no_color_print)
        self.planner = Planner(
            sys_prompt=PlannerPrompt.SYSTEM_PROMPT,
            model_type=self.model_type,
        )

    def tool_execute(self, msg: str) -> Optional[SandboxResponse]:
        """
        Loop for tool execution based on the message from the planner.
        {
          "action": "toolexec",
            "params": {
                "tool_id": "F6RMTA",
                "tool_name": "get_excel_headers",
                "result_variable": "headers",
                "code_snippet": "headers = get_excel_headers()\n"
            }
        }
        """
        assert msg["action"] == "toolexec", "Action must be 'toolexec' for tool execution."
        tool_id = msg["params"]["tool_id"]
        tool_name = msg["params"]["tool_name"]
        result_variable = msg["params"]["result_variable"]
        code_snippet = msg["params"]["code_snippet"]
        for var in result_variable:
            code_snippet += f"\nprint({var})"

        tool_meta = self.tool_manager.get_tool(tool_id)
        if tool_meta is None:
            # raise ToolNotFoundError(f"Tool with ID {tool_id} not found in Tools.")
            return SandboxResponse(EXEC_CODE.FAIL, f"Tool with ID {tool_id} not found in Tools.")

        if not tool_id.startswith("PREDEFINE"):
            tool_import_response = self.sandbox.import_tool(
                tool_path=self.tool_manager.save_path,
                module_name=f"{tool_name}_{tool_id}",
                tool_name=tool_name
            )
            if tool_import_response.code != EXEC_CODE.SUCCESS:
                if self.verbose:
                    print(self.colorWrapper.RED + f"Failed to import tool {tool_name}: {tool_import_response.msg}")
                return SandboxResponse(EXEC_CODE.FAIL, tool_import_response.msg)
            else:
                if self.verbose:
                    print(self.colorWrapper.GREEN + f"Tool {tool_name} imported successfully.")
        
        # execute the tool
        tool_response = self.sandbox.step(
            code_snippet=code_snippet,
            dummy=False
        )
        if tool_response.code != EXEC_CODE.SUCCESS:
            if self.verbose:
                print(self.colorWrapper.RED + f"Tool execution failed: {tool_response.msg}")
            return SandboxResponse(EXEC_CODE.FAIL, tool_response.msg)
        else:
            if self.verbose:
                print(self.colorWrapper.GREEN + f"Tool executed result: {tool_response.msg}")

        return tool_response

    def run(self):
        if self.verbose:
            print(self.colorWrapper.YELLOW + f"System prompt:\n{self.planner.sys_prompt}\n")
        
        prompt = PlannerPrompt.USER_PROMPT.format(
            unified_mem=self.sandbox.get_unified_mem_desc(),
            code_context=self.sandbox.get_code_context(),
            available_tools=self.tool_manager.list_meta_tools(query=self.problem.instruction),
        )

        step = 0
        execution_feedback = ""
        step_response = None

        while step < self.max_step:
            if self.verbose:
                print(self.colorWrapper.RESET + f"========Round {step + 1}========\n")

            try:  # ask
                msg = self.planner.ask(prompt)
            except Exception as e:
                print(self.colorWrapper.RED + str(e))
                break

            msg = parse_json_msg(msg)
            if msg is None:
                print(self.colorWrapper.RED + "Failed to parse planner message.")
                break

            action = msg.get("action", None)
            step += 1
            if action == "toolgen":
                # check modify or generation
                prior_tool_id = msg.get("params", {}).get("prior_tool_id", "")
                if prior_tool_id != "" and (not NO_TOOL_MANAGEMENT): # modify
                    print(self.colorWrapper.YELLOW + f"Modifying existing tool with ID: {prior_tool_id}")
                    if prior_tool_id.startswith("PREDEFINE"):
                        prompt = PlannerPrompt.NEXT_STEP_FAIL.format(feedback=f"The predefined tool `{prior_tool_id}` is fully correct and must not be changed. If the task fails, the issue lies elsewhere in the reasoning or input—not in the tool itself.")
                        print(self.colorWrapper.RED + f"Predefined tool {prior_tool_id} is correct and cannot be modified.")
                        continue
                    prior_tool_meta = self.tool_manager.get_tool(prior_tool_id)
                    if prior_tool_meta is None:
                        prompt = PlannerPrompt.NEXT_STEP_FAIL.format(feedback=f"The tool with ID `{prior_tool_id}` to be modified is not found in the tool library. Please check the tool ID.")
                        print(self.colorWrapper.RED + f"Tool with ID {prior_tool_id} not found for modification.")
                        continue
                    step_response = self.tool_creator.create_tool(msg, self.sandbox, prior_tool_meta, execution_feedback)
                else:  # generation
                    step_response = self.tool_creator.create_tool(msg, self.sandbox) # Do not provide tid here
                
                # register the tool if success
                if step_response["status"] == "success":
                    tool_meta = step_response["generation"]
                    tid = self.tool_manager.register_gen_tool(tool_meta) # get the final tool id

                    step_response = {
                        "status": "success",
                        "msg": f"Tool created successfully and now available. The metadata of the new tool is:\n{self.tool_manager.get_tool_metastring(tid)}",
                    }
                    print(self.colorWrapper.GREEN + f"Tool '{tool_meta['name']}' ({tid}) created successfully.")
                    prompt = PlannerPrompt.GEN_STEP_SUCC.format(feedback=step_response)
                else: # failures
                    step_response = {
                        "status": "failure",
                        "msg": f"Tool creation failed: {step_response}. Thereby the tool has not been assigned tool_id.",
                    }
                    print(self.colorWrapper.RED + f"Tool creation failed: {step_response}")
                    prompt = PlannerPrompt.NEXT_STEP_FAIL.format(feedback=step_response)
            elif action == "toolexec":
                # step += 1
                step_response = self.tool_execute(msg)
                if step_response.code == EXEC_CODE.SUCCESS:
                    print(self.colorWrapper.GREEN + f"Step {step + 1} executed done.")
                    prompt = PlannerPrompt.EXEC_STEP_SUCC.format(feedback=f"Tool `{msg['params']['tool_id']}` executed by `{msg['params']['code_snippet']}`, getting results: {step_response.msg}")
                    execution_feedback = step_response.msg

                    for error_keyword in ["error", "traceback", "fail", "exception", "invalid", "aborted"]:
                        if re.search(error_keyword, step_response.msg, re.IGNORECASE):
                            # if self.verbose:
                            print(self.colorWrapper.RED + f"Error detected in step response. {step_response.msg}", end="")
                            self.tool_manager.tool_fault_record(msg["params"]["tool_id"])
                            break
                    else:
                        self.tool_manager.tool_success_record(msg["params"]["tool_id"])
                    
                    # add the execution result to unified memory
                    self.sandbox.add_unified_mem("reasoning_traces", None, f"Tool `{msg['params']['code_snippet']}` Execution Result: {step_response.msg}")
                else:
                    print(self.colorWrapper.RED + f"Tool execution failed: {step_response.msg}")
                    self.tool_manager.tool_fault_record(msg["params"]["tool_id"])
                    prompt = PlannerPrompt.NEXT_STEP_FAIL.format(feedback=f"Tool `{msg['params']['tool_id']}` executed by `{msg['params']['code_snippet']}` failed: {step_response.msg}")
                    execution_feedback = step_response.msg
            elif action == "codeexec":
                # step += 1
                result_variable = msg.get("params", {}).get("result_variable", [])
                code_snippet = msg.get("params", {}).get("code_snippet", "")
                for var in result_variable:
                    code_snippet += f"\nprint({var})"
                step_response = self.sandbox.step(code_snippet=code_snippet, dummy=False)
                if step_response.code == EXEC_CODE.SUCCESS:
                    print(self.colorWrapper.GREEN + f"Code execution done: {step_response.msg}")
                    prompt = PlannerPrompt.EXEC_STEP_SUCC.format(feedback=f"Code executed: `{code_snippet}`, getting results: {step_response.msg}")

                    # unified memory update
                    self.sandbox.add_unified_mem("reasoning_traces", None, f"Code `{code_snippet}` Execution Result: {step_response.msg}")
                else:
                    print(self.colorWrapper.RED + f"Code execution failed: {step_response.msg}")
                    prompt = PlannerPrompt.NEXT_STEP_FAIL.format(feedback=f"Code executed: `{code_snippet}` failed: {step_response.msg}")
            elif action == "done":
                print(self.colorWrapper.GREEN + "</DONE>FINISHED</DONE>")
                break

            tool_notification = self.tool_manager.update_tool_context()
            if tool_notification:
                prompt += f"\n{tool_notification}"
                print(self.colorWrapper.YELLOW + f"Updated Tool context for LLM: {tool_notification}")

            # add remarks for the overall tasks
            prompt += f"\n# Remarks:"
            prompt += f"\nCurrent code context: {self.sandbox.get_code_context()}"

        self.save() # save all the sessions

    def save(self):
        self.sandbox.save(self.output_dir)
        self.planner.save(self.output_dir)
        self.tool_manager.save()
        self.tool_creator.save(self.output_dir)
