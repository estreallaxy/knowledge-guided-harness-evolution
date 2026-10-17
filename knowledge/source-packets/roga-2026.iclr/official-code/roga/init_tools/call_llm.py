from init_tools.configs import MODEL_SELECTION

from pathlib import Path
import sys

# check if this path has been add
module_path = Path(__file__).resolve().parent.parent / "core"
if str(module_path) not in sys.path:
    sys.path.append(str(module_path))
from core.assistant import Planner

module_path = Path(__file__).resolve().parent.parent / "llm"
if str(module_path) not in sys.path:
    sys.path.append(str(module_path))

def call_llm(user_prompt: str, system_prompt: str = None, json_resp: bool = True) -> str:
    try:
        if system_prompt:
            planner = Planner(
                sys_prompt=system_prompt,
                model_type=MODEL_SELECTION,
                name="Tool calls"
            )
        else:
            planner = Planner(
                sys_prompt="You are a helpful assistant.",
                model_type=MODEL_SELECTION,
                name="Tool calls"
            )
        response = planner.ask(user_prompt, json_resp=json_resp).strip()
        return response
    except Exception as e:
        return f"LLM call failed: {str(e)}"