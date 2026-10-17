import code
import copy
import io
import os
import re
import sys
from pathlib import Path

from utils.common import SandboxResponse
from utils.enumeration import *
from llm.openai_utils import MODEL_TYPE

from ablation_configs import NO_SHARED_STATE

class Sandbox:
    def __init__(self, init_toolpath: str, model_type: MODEL_TYPE=MODEL_TYPE.GPT_4o, is_copy=False) -> None:
        self.interpreter = code.InteractiveInterpreter()
        self.model_type = model_type
        self.code_history = []
        self.stdout = []
        self.stderr = []
        self.syspath = []
        self.init_toolpath = init_toolpath.strip("\\")
        self.office_type = None  # excel, word, powerpoint, unknown

        self.unified_mem = {
            "reasoning_traces": []
        }

        # construct init_tools
        config_path = os.path.join(self.init_toolpath, "configs.py")
        config_content = (
            "from llm.openai_utils import MODEL_TYPE\n"
            f"MODEL_SELECTION = MODEL_TYPE.{self.model_type.label()}\n"
        )
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
        except PermissionError:
            # Keep the existing runtime config when artifact tree is read-only.
            if not os.path.exists(config_path):
                raise
            self.stderr.append(
                f"Warning: cannot write runtime config to {config_path}; using existing configs.py."
            )

        if not is_copy:
            self.import_lib()

    def add_unified_mem(self, var_name: str, var_type: str, var_desc: str):

        if var_name == "reasoning_traces":
            self.unified_mem[var_name].append(var_desc)
        else:
            self.unified_mem[var_name] = {
               "type": var_type,
                "desc": var_desc
            }

    def _infer_office_type(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix in [".xlsx", ".xlsm", ".xlsb", ".xls"]:
            return "excel"
        elif suffix in [".docx", ".doc"]:
            return "word"
        elif suffix in [".pptx", ".ppt"]:
            return "powerpoint"
        else:
            return "unknown"

    def open_file(self, file_path: str, output_dir: str):
        if file_path != "" and os.path.exists(file_path):
            self.step(f'file_path = r"{file_path}"', dummy=False)
            self.add_unified_mem("file_path", "str", "The path of the file to be processed.")
            if self.office_type is None:
                self.office_type = self._infer_office_type(Path(file_path))
            if self.office_type == "excel":
                self.step(f'file_object = openpyxl.load_workbook(file_path)', dummy=False)
                self.add_unified_mem("file_object", "openpyxl.Workbook", "The Excel workbook object loaded from the file path.")
            elif self.office_type == "word":
                self.step(f'file_object = docx.Document(file_path)', dummy=False)
                self.add_unified_mem("file_object", "docx.Document", "The Word document object loaded from the file path.")
            elif self.office_type == "powerpoint":
                self.step(f'file_object = pptx.Presentation(file_path)', dummy=False)
                self.add_unified_mem("file_object", "pptx.Presentation", "The PowerPoint presentation object loaded from the file path.")
            else:
                self.add_unified_mem("file_object", "unknown", "The file type is unknown so has not been loaded. Please open the file accordingly.")

        # add output_dir
        self.step(f'output_dir = r"{output_dir}"', dummy=False)
        self.add_unified_mem("output_dir", "str", "The directory to save the output files.")

    def get_unified_mem_desc(self) -> str:
        if NO_SHARED_STATE:
            task_desc = ""
            for trace in self.unified_mem["reasoning_traces"]:
                if trace.startswith("Instruction:"):
                    task_desc += trace + "\n"
                elif trace.startswith("Context of the file:"):
                    task_desc += trace + "\n"
            return task_desc
    
        # REASONING_TOKEN_LIMIT = 3000
        desc = f"- Semantic info for your reasoning:\n"
        for i, trace in enumerate(self.unified_mem["reasoning_traces"]):
            # if len(trace) > REASONING_TOKEN_LIMIT:
            #     trace = trace[:REASONING_TOKEN_LIMIT] + "...[truncated]"
            desc += f"  {i+1}. {trace}\n"

        desc += "- The following are the shared variables:\n"
        for var_name, var_info in self.unified_mem.items():
            if var_name == "reasoning_traces":
                continue
            desc += f"  - {var_name} ({var_info['type']}): {var_info['desc']}\n"
        return desc

    def copy(self) -> 'Sandbox':
        new_sandbox = Sandbox(self.init_toolpath, model_type=self.model_type, is_copy=True)

        new_sandbox.code_history = copy.deepcopy(self.code_history)
        new_sandbox.stdout = copy.deepcopy(self.stdout)
        new_sandbox.stderr = copy.deepcopy(self.stderr)
        new_sandbox.syspath = copy.deepcopy(self.syspath)
        new_sandbox.unified_mem = copy.deepcopy(self.unified_mem)

        if self.code_history:
            new_sandbox.step("\n".join(self.code_history), dummy=True)
        
        return new_sandbox

    def add_sys_path(self, syspath: str, dummy=False):
        if syspath not in self.syspath:
            self.syspath.append(syspath)
            self.step(f"sys.path.append(r'{syspath}')", dummy=dummy)

    def get_code_context(self) -> str:
        if NO_SHARED_STATE:
            return ""
        code_context = "######### Code Context Start #########\n"
        for code_snippet in self.code_history:
            if code_snippet.startswith("sys.path.append(r"):
                continue
            code_context += code_snippet + "\n"
        code_context += "######### Code Context End #########\n"
        return code_context

    def import_tool(self, tool_path: str, module_name: str, tool_name: str, dummy=False):
        self.add_sys_path(tool_path, dummy=dummy)

        # module_path = tool_path.replace('\\', '.').replace('.py', '')
        code_snippet = f"from {module_name} import {tool_name}\n"
        tool_import_response = self.step(code_snippet, dummy=dummy)
        return tool_import_response

    def import_lib(self):
        core_imports = [
            "import sys",
            "import os",
            "import datetime",
            "import openpyxl",
            "import pandas as pd",
            "import matplotlib.pyplot as plt",
        ]

        for stmt in core_imports:
            import_resp = self.step(stmt, dummy=False)
            if import_resp.code != EXEC_CODE.SUCCESS:
                self.stderr.append(f"Core import failed: {stmt}. {import_resp.msg}")

        # Optional imports are best-effort to keep the artifact runnable
        # when only one office type is evaluated.
        for optional_stmt in ["import pptx", "import docx"]:
            import_resp = self.step(optional_stmt, dummy=False)
            if import_resp.code != EXEC_CODE.SUCCESS:
                self.stderr.append(f"Optional import failed: {optional_stmt}. {import_resp.msg}")

        self.add_sys_path(self.init_toolpath, dummy=False)

        code_snippet = []
        for init_tool in os.listdir(self.init_toolpath):
            if init_tool.endswith(".py") and not init_tool.startswith("__"):
                module_name = init_tool[:-3]
                code_snippet.append(f"from {module_name} import *")

        self.step("\n".join(code_snippet), dummy=False)

    def reset(self):
        self.interpreter = code.InteractiveInterpreter()

    def step(self, code_snippet: str, dummy=False) -> SandboxResponse:
        out_buffer = io.StringIO()
        err_buffer = io.StringIO()
        sys.stdout = out_buffer
        sys.stderr = err_buffer

        self.interpreter.runcode(code_snippet)

        output = out_buffer.getvalue() # because the tool uses try except to catch errors, so the error may appear in the output
        error = err_buffer.getvalue()

        def _clean_output(output: str) -> str:
            output = output.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            # remove empty characters
            cleaned_output = re.sub(r"\s+", " ", output.strip())
            return cleaned_output
        output = _clean_output(output)
        error = _clean_output(error)

        if not dummy:
            if error == "":
                # filter out the print() commands
                code_lines = code_snippet.splitlines()
                filtered_code = "\n".join(line for line in code_lines if not line.startswith("print("))
                self.code_history.append(filtered_code)
            self.stdout.append(output)
            self.stderr.append(error)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        if error != "":  # error caught
            self.backtrack()
            return SandboxResponse(EXEC_CODE.FAIL, error)

        # Set a limitation for the output length
        if len(output) > 5000:
            output = output[:5000] + "\n...[IMPORTANT: Output has been truncated and does not contain complete data. Please use comprehension tools that call the LLM to simplify the current output, and explicitly inform the LLM that the information is incomplete and further data is required before making any decisions.]..."

        return SandboxResponse(EXEC_CODE.SUCCESS, output)

    def shadow_step(self, code_snippet: str) -> SandboxResponse:
        out_buffer = io.StringIO()
        err_buffer = io.StringIO()
        sys.stdout = out_buffer
        sys.stderr = err_buffer

        self.interpreter.runcode(code_snippet)

        output = out_buffer.getvalue()
        error = err_buffer.getvalue()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        self.backtrack()
        if error != "":
            return SandboxResponse(EXEC_CODE.FAIL, error)
        else:
            return SandboxResponse(EXEC_CODE.SUCCESS, output)

    def save(self, save_dir: Path):
        if self.office_type == "excel":
            self.step(f'file_object.save(os.path.join(output_dir, "new_object.xlsx"))', dummy=False)
        elif self.office_type == "word":
            self.step(f'file_object.save(os.path.join(output_dir, "new_object.docx"))', dummy=False)
        elif self.office_type == "powerpoint":
            self.step(f'file_object.save(os.path.join(output_dir, "new_object.pptx"))', dummy=False)

        with open(save_dir / "code.py", "w", encoding="utf-8") as f:
            f.write("\n\n# ============\n".join(self.code_history))

        with open(save_dir / "outputs.txt", "w", encoding="utf-8") as f:
            f.write("\n\n# ============\n".join(self.stdout))

        with open(save_dir / "errors.txt", "w", encoding="utf-8") as f:
            f.write("\n\n# ============\n".join(self.stderr))

    def backtrack(self, progress: int=0):
        """
        Backtrack the code history to a specific progress.
        :param progress: The progress to backtrack to.
        """
        if progress > len(self.code_history) or progress < 0:
            progress = 0

        # Reset the interpreter
        self.reset()

        if progress != 0:
            self.code_history = self.code_history[:progress]
            self.stdout.append("Backtracked to step {}".format(progress))
            self.stderr.append("")

        self.step("\n".join(self.code_history), dummy=True)
