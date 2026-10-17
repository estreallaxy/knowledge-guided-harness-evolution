import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import logging
import os
from typing import Dict, List

from tool.tool_searcher import ToolVectorSearcher
from utils.common import ColorWrapper

from ablation_configs import NO_TOOL_MANAGEMENT, NO_COMPREHENSION

class ToolManager:
    def __init__(
        self,
        save_path: str = "tool_box",
        max_faults: int = 3,
        no_color_print: bool = False
    ):
        self.tools = {}
        self.tool_contexts = []
        self.max_faults = max_faults
        self.colorWrapper = ColorWrapper(enable_color=not no_color_print)

        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)
        # add __init__.py to the save path
        init_file = os.path.join(save_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding="utf-8") as f:
                f.write("# Tool Box\n")

        # load predefined Tools
        if NO_COMPREHENSION:
            # no predefined tools
            self.init_tools = {}
        else:
            init_toolpath = os.path.join(os.path.dirname(__file__), "..", "init_tools", "init_tools.json")
            self.init_toolpath = init_toolpath
            if os.path.exists(init_toolpath):
                with open(init_toolpath, 'r', encoding="utf-8") as f:
                    self.init_tools = json.load(f)
                    self.tools.update(self.init_tools)
                    print(self.colorWrapper.GREEN + f"Loaded {len(self.init_tools)} predefined Tools from init_tools/init_tools.json")

        # load existing Tools if any
        if os.path.exists(os.path.join(self.save_path, "tools.json")):
            with open(os.path.join(self.save_path, "tools.json"), 'r', encoding="utf-8") as f:
                gen_tool = json.load(f)
                self.tools.update(gen_tool)
                print(self.colorWrapper.GREEN + f"Loaded {len(gen_tool)} Tools from {self.save_path}/tools.json")

        # FSM-inspired lifecycle labels for paper/code alignment:
        # - Generated: transient candidate inside ToolCreator before registration.
        # - Modifying: transient candidate during regeneration attempts.
        # - Active: registered reusable capability in self.tools.
        # - Deprecated: marked before removal after repeated failures.
        for tool in self.tools.values():
            tool.setdefault("lifecycle_state", "Active")

        # load Tool search engine
        self.search_engine = ToolVectorSearcher()
        # Following tools have been loaded in ToolVectorSearcher
        # # merge tools into search engine
        # for tid, tool in self.tools.items():
        #     self.search_engine.add_tool(tid, self.get_tool_metastring(tid))

    def update_tool_context(self, context: str=""):
        if NO_TOOL_MANAGEMENT:
            return ""

        # Update the change of Tool manager to LLMs
        if context != "":
            print(self.colorWrapper.RED + f"Update Tool context: {context}")
            context = "# PLEASE NOTE Tool TOOLS CHANGE: " + context
            self.tool_contexts.append(context)
            return ""
        else:
            if self.tool_contexts:
                context_str = str(self.tool_contexts)
                self.tool_contexts = []
                return context_str
            else:
                return ""

    def remove_tool(self, tool_id: str, inform_str: str=""):
        if NO_TOOL_MANAGEMENT:
            return ""
        
        """Remove a tool from the Tool manager."""
        if tool_id in self.tools:
            self.tools[tool_id]["lifecycle_state"] = "Deprecated"
            # inform LLMs about the removal
            if inform_str:
                self.update_tool_context(inform_str)
            # remove the python file
            python_file = os.path.join(self.save_path, f"{self.tools[tool_id]['name']}_{tool_id}.py")
            if os.path.exists(python_file):
                os.remove(python_file)
            # remove the meta data
            del self.tools[tool_id]

            # remove index
            self.search_engine.remove_tool(tool_id)
        else:
            print(self.colorWrapper.RED + f"Remove Failed: Tool ID {tool_id} not found.")

    def tool_fault_record(self, tool_id: str):
        """Record a fault for a tool."""
        if NO_TOOL_MANAGEMENT:
            return

        if tool_id not in self.tools:
            print(self.colorWrapper.RED + f"Tool ID {tool_id} not found.")
            return

        self.tools[tool_id]['faults'] = self.tools[tool_id].get('faults', 0) + 1
        self.tools[tool_id]['lifecycle_state'] = 'Modifying'
        if self.tools[tool_id]['faults'] >= self.max_faults: # remove tool from Tools
            print(self.colorWrapper.RED + f"Tool ID {tool_id} has exceeded max faults.")

            self.remove_tool(tool_id, inform_str="\n".join([
                f"Removed Tool for tool ID {tool_id} due to excessive faults.\nYou should consider ANOTHER approach to complete the task.",
                f"Tool metadata: {self.get_tool_metastring(tool_id)}"
            ]))
            return

        print(self.colorWrapper.YELLOW + f"Recorded fault for tool ID {tool_id}. Total faults: {self.tools[tool_id]['faults']}")

    def tool_success_record(self, tool_id: str):
        """Record a success for a tool, resetting its fault count."""
        if NO_TOOL_MANAGEMENT:
            return
        if tool_id not in self.tools:
            print(self.colorWrapper.RED + f"Tool ID {tool_id} not found.")
            return

        if 'faults' in self.tools[tool_id]:
            self.tools[tool_id]['faults'] = 0
            print(self.colorWrapper.GREEN + f"Reset faults for tool ID {tool_id}.")
        
        self.tools[tool_id]['lifecycle_state'] = 'Active'
        self.tools[tool_id]['successes'] = self.tools[tool_id].get('successes', 0) + 1
        print(self.colorWrapper.GREEN + f"Recorded success for tool ID {tool_id}. Total successes: {self.tools[tool_id]['successes']}")

    def save(self):
        """Save the Tools to a JSON file."""

        # remove predefined Tools
        self.tools = {k: v for k, v in self.tools.items() if v['source'] != 'predefined'}

        with open(os.path.join(self.save_path, "tools.json"), 'w', encoding="utf-8") as f:
            json.dump(self.tools, f, indent=2)

        self.search_engine.save()

        # print(self.colorWrapper.GREEN + f"Saved {len(self.tools)} Tools to {self.save_path}/tools.json")

    def random_tool_id(self):
        """Generate a random tool ID."""
        import random
        import string
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if new_id in self.tools:
            return self.random_tool_id()
        return new_id

    def add_tool(
        self,
        tid: str,
        name: str,
        description: str,
        args: list = [],
        returns: list = [],
        source: str = "dynamically-generated",
        requires: list = [],
        code: str = None,
        example_call: str = None,
    ):
        # get unique tid
        if tid == "":
            tid = self.random_tool_id()

        faults = self.tools.get(tid, {}).get("faults", 0)
        self.tools[tid] = {
            "tid": tid,
            "name": name,
            "description": description,
            "args": args,
            "returns": returns,
            "source": source,
            "requires": requires,
            "code": code,
            "example_call": example_call,
            "successes": 0, # recount of successful executions if modified
            "faults": faults, # only when successfully executed, faults can be reset to 0
            "lifecycle_state": "Active", # explicit FSM-aligned state for registered tools
        }
        print(f"   Agent Log: New Tool '{name}' ({source}) added. Description: {description}")

        # Add to vector search index
        self.search_engine.add_tool(tid, description=self.get_tool_metastring(tid))

        # save path
        with open(os.path.join(self.save_path, f"{name}_{tid}.py"), 'w', encoding="utf-8") as f:
            # write code 
            if code:
                f.write(f"# Tool: {name}\n# Description: {description}\n\n")
                if code.startswith("```python"):
                    code = code[9:]
                if code.endswith("```"):
                    code = code[:-3]
                f.write(code.strip() + "\n")

            else:
                f.write(f"# Tool: {name}\n# Description: {description}\n\n# No code provided.\n")

        return tid


    def register_gen_tool(self, metadata: dict):
        """Register an Tool with metadata dictionary format."""
        return self.add_tool(
            tid=metadata.get('tid', ""),
            name=metadata.get('name', "no_name"),
            description=metadata.get('description', 'No description'),
            args=metadata.get('args', None),
            returns=metadata.get('returns', None),
            source=metadata.get('source', 'dynamically-generated'),
            requires=metadata.get('requires', None),
            code=metadata.get('code', None),
            example_call=metadata.get('example_call', None),
        )

    def get_tool(self, tid: str):
        return self.tools.get(tid, None)
    
    def get_tool_success_rate(self, tid: str) -> float:
        if NO_TOOL_MANAGEMENT:
            return "N/A"
            
        tool = self.get_tool(tid)
        if tool is None:
            return 0
        successes = tool.get('successes', 0)
        faults = tool.get('faults', 0)
        total = successes + faults
        if total == 0:
            return 80.0  # default success rate
        return (successes / total) * 100

    def get_tool_metastring(self, tid: str):
        tool = self.get_tool(tid)
        if tool is None:
            return f"Tool with id {tid} not found."

        meta_str = f"- {tool['name']} (id: {tid})\n"
        meta_str += f"Description: {tool['description']}\n"
        meta_str += f"Arguments: {tool['args']}\n"
        meta_str += f"Returns: {tool['returns']}\n"
        # if tool.get('code'):
        #     meta_str += f"Code: {tool['code'][:200]}...\n"
        if "= call_llm(" in tool.get('code'):
            meta_str += f"Code: This tool uses LLM API.\n"

        return meta_str

    def list_meta_tools(self, query: str, top_k: int = 10) -> str:
        if (not self.tools) or NO_TOOL_MANAGEMENT:
            return "No tools available."

        tool_list = "Available Tools:\n"
        
        search_results = self.search_tools(query, top_k=top_k) # a list of dicts with keys: tool_id, description
        
        # add all predefined tools            
        searched_ids = [data['tool_id'] for data in search_results]
        for tid, tool in self.init_tools.items():
            if tid not in searched_ids:
                search_results.append({
                    'tool_id': tid,
                    'description': self.get_tool_metastring(tid),
                    'success_score': self.get_tool_success_rate(tid)
                })
                searched_ids.append(tid)
        # sort again by success rate
        search_results.sort(key=lambda x: x.get('success_score', 0), reverse=True)
        if search_results:
            for data in search_results:
                tool_list += f"{data['description']} (Success Rate: {data['success_score']:.2f}%)\n"

        if tool_list.strip() == "":
            return "No Tools found matching the query."

        return tool_list

    def search_tools(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search Tools using semantic similarity
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of matching Tools with scores
        """
        if NO_TOOL_MANAGEMENT:
            return []

        results = self.search_engine.search(query, top_k=top_k)

        # remove non-exsisting tools
        real_tids = []
        for tid, score in results:
            if tid not in self.tools:
                logging.warning(f"Tool ID {tid} found in search index but not in tools list. Removing from index.")
                self.search_engine.remove_tool(tid)
            else:
                real_tids.append(tid)

        return [
            {
                'tool_id': tid,
                "success_score": self.get_tool_success_rate(tid),
                'description': self.get_tool_metastring(tid)
            }
            for tid in real_tids
        ]
    
