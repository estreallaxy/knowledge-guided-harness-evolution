import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from openai import OpenAI


class OpenaiClient():
    def __init__(self, sys_msg, api_key=None, config_path=None):
        print("openai_init")
        # Priority: passed-in api_key > config file > environment variable.
        if api_key is None:
            # Try reading from the config file.
            if config_path is None:
                # If config_path is not provided, try get_config_path.
                try:
                    import sys
                    import os as os_module
                    # Try to import get_config_path.
                    sys.path.insert(0, os_module.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), '..'))
                    from agent_tools import get_config_path
                    config_path = get_config_path()
                except Exception as e:
                    print(f"Warning: Could not get config path: {e}")
                    config_path = None
            
            if config_path:
                try:
                    import json
                    import os as os_module
                    if os_module.path.exists(config_path):
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            api_key = config.get("OPENAI_API_KEY") or None
                            if api_key:
                                print(f"Using API key from config file: {config_path}")
                except Exception as e:
                    print(f"Warning: Could not read API key from config file {config_path}: {e}")
            
            # If the config file does not contain the key, fall back to the environment variable.
            if not api_key:
                import os
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    print("Using API key from environment variable OPENAI_API_KEY")
        
        if api_key is None:
            raise ValueError("OPENAI_API_KEY not found. Please set it in config file, environment variable, or pass it as parameter.")
        
        self.client = OpenAI(
            api_key=api_key,  
        )
        self.sys_msg = sys_msg

    def truncate_string_by_words(self, text, word_limit=4096):
        words = text.split()
        truncated_words = words[:word_limit]  # first 4096 words
        return " ".join(truncated_words)

    def generate(self, query, **kwargs):
        query = self.truncate_string_by_words(query)
        response = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.sys_msg,
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="gpt-4o",#"gpt-4o-mini",#gpt-4o-mini
            # max_completion_tokens=1024
            )
        return response.choices[0].message.content


class QwenClient():
    def __init__(self, sys_msg):
        print("transformers_init")
        self.model_name = "Qwen/Qwen2.5-Coder-32B-Instruct"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.sys_msg = sys_msg

    def generate(self, query, **kwargs):
        messages = [
            {"role": "system", "content": self.sys_msg},
            {"role": "user", "content": query}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=1024
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


class DSClient():
    def __init__(self, sys_msg):
        print("transformers_init")
        self.model_name = "deepseek-ai/deepseek-coder-6.7b-instruct"  # Use the DeepSeek model.

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,  # Use bfloat16 dtype.
            device_map="auto"  # Dispatch devices automatically.
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.sys_msg = sys_msg

    def generate(self, query, **kwargs):
        # Build the message format.
        messages = [
            {"role": "system", "content": self.sys_msg},
            {"role": "user", "content": query}
        ]
        
        # Build the chat-formatted text via tokenizer.
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        
        # Convert the text to model inputs.
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        # Generate output.
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=1024,
            **kwargs  # Allow passing extra kwargs through.
        )
        
        # Trim the input part from the generated ids.
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        
        # Decode and return the generated text.
        return self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


class LlamaClient:
    def __init__(self, sys_msg):
        print("transformers_init")
        self.model_name = "meta-llama/Llama-3.1-8B"  # Use the Llama model.

        # Load model and tokenizer.
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,  # Use bfloat16 dtype.
            device_map="auto"  # Dispatch devices automatically.
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.sys_msg = sys_msg  # System message.

    def generate(self, query, **kwargs):
        # Build the input messages.
        messages = [
            {"role": "system", "content": self.sys_msg},
            {"role": "user", "content": query}
        ]
        
        # Build chat-formatted text via tokenizer.
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        # Convert to the model's input format.
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        # Generate output.
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=1024,  # Cap the number of generated tokens.
            **kwargs  # Allow passing extra kwargs through.
        )
        
        # Decode the generated ids.
        generated_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        return generated_text

