import abc
import json
import os
import time
from typing import Optional
import requests

from utils.enumeration import ROLE
from utils.exceptions import TokenLimitError
from utils.utils import num_tokens_from_messages
from llm.openai_utils import MODEL_TYPE, get_model_token_limit, get_model_max_tokens

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

class OpenAI:
    _req_cnt = 0
    _completion_tokens = 0
    _prompt_tokens = 0
    _total_tokens = 0
    _total_cost = 0.0

    # GPT-4.1 input $3.00 / 1M tokens, $0.75 / 1M tokens output $12.00 / 1M tokens
    _model_pricing = {
        MODEL_TYPE.GPT_41.value: {"prompt": 0.003, "completion": 0.012},
    }

    def __init__(self):
        self.url = "http://127.0.0.1:5000/chat/completions"

    def chat(self, model: str, messages: list, chat_configs: dict = {"temperature": 0.0}):
        chat_configs["messages"] = messages
        chat_configs["model"] = model
        response = requests.post(self.url, json=chat_configs)
        response = response.json()

        # statistics
        OpenAI._req_cnt += 1
        usage = response.get("usage", {})
        completion_tokens = usage.get("completion_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        OpenAI._completion_tokens += completion_tokens
        OpenAI._prompt_tokens += prompt_tokens
        OpenAI._total_tokens += total_tokens        
        cost = self._calculate_cost(model, prompt_tokens, completion_tokens)
        OpenAI._total_cost += cost

        return response
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        if model not in self._model_pricing:
            return 0.0
        
        pricing = self._model_pricing[model]
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
        return round(prompt_cost + completion_cost, 6)
    
    @classmethod
    def get_statistics(cls) -> dict:
        return {
            "req_cnt": cls._req_cnt,
            "completion_tokens": cls._completion_tokens,
            "prompt_tokens": cls._prompt_tokens,
            "total_tokens": cls._total_tokens,
            "total_cost": round(cls._total_cost, 6),
            "currency": "USD"
        }
    
    @classmethod
    def save(cls, save_dir: str):
        stats = cls.get_statistics()
        
        with open(os.path.join(save_dir, "api_cost_stats.json"), "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        


class Assistant(abc.ABC):
    def __init__(self, sys_prompt, model_type: MODEL_TYPE, name: str) -> None:
        super().__init__()
        self.sys_prompt = sys_prompt
        self.model_type = model_type
        self.msg_history = []
        self.verbose = True  # Set to False to disable verbose output
        self.name = name
        self.client = OpenAI()

    def get_history(self):
        return self.msg_history

    def ask(self, prompt: str, ask_configs: dict=None, json_resp=True) -> Optional[str]:
        self.msg_history.append({"role": ROLE.USER.value, "content": prompt})
        query = [{"role": ROLE.SYSTEM.value, "content": self.sys_prompt}]

        query.extend(self.msg_history)

        num_tokens = num_tokens_from_messages(query, self.model_type)
        token_limit = get_model_token_limit(self.model_type)
        if token_limit is None:
            raise NotImplementedError(f"Model type {self.model_type} is not supported.")
        if num_tokens >= token_limit:
            raise TokenLimitError(num_tokens, token_limit)
        
        if not ask_configs:
            ask_configs = {}
            if self.model_type in [MODEL_TYPE.GPT_O3, MODEL_TYPE.GPT_5]:
                ask_configs["max_completion_tokens"] = get_model_max_tokens(self.model_type)                
            else:
                ask_configs["temperature"] = 0.0
                ask_configs["max_tokens"] = get_model_max_tokens(self.model_type)
            # set response format to json

            if json_resp:
                ask_configs["response_format"] = {
                    "type": "json_object",
                }

        if self.verbose:
            print(f"{self.name} Prompt:\n{prompt}\n")
        
        response = self.client.chat(
            model=self.model_type.value,
            messages=query,  # type: ignore
            chat_configs=ask_configs
        )
        gpt_message = response.get("choices", [{}])[0].get("message", {})
        self.msg_history.append({"role": gpt_message.get("role", ROLE.ASSISTANT.value), "content": gpt_message.get("content", "")})

        if self.verbose:
            print(f"{self.name} Answer:\n{gpt_message.get('content', '')}\n")
        
        return gpt_message.get("content", "")

class Planner(Assistant):
    def __init__(self, sys_prompt, model_type: MODEL_TYPE = MODEL_TYPE.GPT_4o, name: str="Planner") -> None:
        super().__init__(sys_prompt, model_type, name)

    def save(self, save_dir: str):
        query = [{"role": ROLE.SYSTEM.value, "content": self.sys_prompt}]

        with open(os.path.join(save_dir, f"history_{self.name}.json"), "w", encoding="utf-8") as f:
            json.dump(query + self.msg_history, f, indent=2)

        # Save statistics
        OpenAI.save(save_dir)
