import os
import argparse
import json
import time
import re
import random
import base64
import requests
try:
    import anthropic
except ImportError:  # optional unless api_type == "claude"
    anthropic = None
try:
    from openai import OpenAI
except ImportError:  # optional unless using OpenAI client modes
    OpenAI = None
from typing import Dict, List, Tuple, Optional
import ast
try:
    from PIL import Image
except ImportError:  # optional unless image resizing is requested
    Image = None
from io import BytesIO

# Default prompt directory for the packaged repository. CLI entry points normally pass prompt_dir explicitly.
_current_file_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(_current_file_dir)))
PROMPT_DIR = os.path.join(_repo_root, "configs", "prompts")


class LLMEvaluator:
    def __init__(
            self,
            api_type: str = "openai",
            model: str = "gpt-4o-2024-11-20",
            base_url: str = None,
            api_key: Optional[str] = None,
            prompt_file: str = None,
            prompt_dir: str = None,
            temperature: float = 0.0,
            top_p: float = None,  # 添加top_p参数
            top_k: int = None,    # 添加top_k参数
            repetition_penalty: float = None,  # 添加repetition_penalty参数
            max_tokens: int = 4096,  # 添加max_tokens参数
            voting_type: Optional[str] = None,
            voting_num: int = 1,
            timeout: int = 900,  # 默认15分钟超时
    ):
        """Initialize LLM evaluator with specified API
        
        Args:
            api_type: Type of LLM API to use ('openai', 'claude', 'qwen', 'local')
            api_key: API key if required
            timeout: API request timeout in seconds (default: 900)
        """
        self.api_type = api_type
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p  # 保存top_p
        self.top_k = top_k  # 保存top_k
        self.repetition_penalty = repetition_penalty  # 保存repetition_penalty
        self.max_tokens = max_tokens  # 保存max_tokens
        self.voting_type = voting_type
        self.voting_num = voting_num
        self.timeout = timeout  # 保存timeout配置
        print(f"Initializing LLMEvaluator with {api_type}, timeout={timeout}s, temperature={temperature}, top_p={top_p}, top_k={top_k}, repetition_penalty={repetition_penalty}, max_tokens={max_tokens}")
        self._setup_client()

        # load prompt file
        prompt_dir = prompt_dir if prompt_dir is not None else PROMPT_DIR
        if prompt_file is not None:
            prompt_path = os.path.join(prompt_dir, prompt_file)
            with open(prompt_path, 'r') as f:
                self.prompt = json.load(f)

    def _setup_client(self):
        """Setup appropriate client based on API type"""
        try:
            if self.api_type == "openai":
                if OpenAI is None:
                    raise ImportError("openai is required for api_type='openai'. Please install openai.")
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                # print("OpenAI client initialized")
            elif self.api_type == "claude":
                self.client = anthropic.Anthropic(api_key=self.api_key)
                # print("Claude client initialized")
            elif self.api_type in ["3rd_openai", "3rd_openai_sn"]:
                self.client = None
                # print("3rd party OpenAI client initialized")
            elif "qwen" in self.api_type.lower():
                self.client = None
                # print("Qwen client initialized")
            elif self.api_type == "3rd_openai_glm":
                if OpenAI is None:
                    raise ImportError("openai is required for api_type='3rd_openai_glm'. Please install openai.")
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            else:
                print(f"Unsupported LLM type: {self.api_type}")
                raise NotImplementedError(f"Unsupported LLM type: {self.api_type}")
        except Exception as e:
            print(f"Failed to initialize client: {str(e)}")
            raise

    def _encode_image(self, image_bytes: bytes=None, image_path: str=None, img_scale=1.0) -> str:
        """Convert image to base64 string"""
        if image_bytes is not None:
            return base64.b64encode(image_bytes).decode("utf-8")
        elif image_path is not None:
            if img_scale == 1.0:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            else:
                if Image is None:
                    raise ImportError("pillow is required when img_scale != 1.0. Please install pillow.")
                with open(image_path, "rb") as image_file:
                    image = Image.open(image_file)

                    new_size = (int(image.width * img_scale), int(image.height * img_scale))
                    image = image.resize(new_size)

                    buffer = BytesIO()
                    image.save(buffer, format="PNG")
                    encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                return encoded_image
        else:
            raise NotImplementedError

    def _is_token_limit_error(self, error_message: str) -> bool:
        """检查是否是token长度超限错误"""
        error_indicators = [
            "longer than the maximum model length",
            "maximum model length",
            "token limit",
            "context length",
            "input too long"
        ]
        return any(indicator in error_message.lower() for indicator in error_indicators)

    def call_llm(self, prompt: str, n_samples: int = 1, max_tokens: int = 4096, temperature: float = 0.0, 
                 retry_times: int = 1, retry_delay: int = 1, timeout: int = 360, return_list: bool = False):
        """Call LLM API with prompt and optional images
        
        Args:
            prompt: Text prompt for the LLM
            retry_times: Number of retry attempts if API call fails
            retry_delay: Delay in seconds between retries
            
        Returns:
            str: LLM response text or special error codes
            
        Raises:
            Exception: If API call fails after all retries or unsupported LLM type
        """
        # print(f"Calling {self.api_type} API")
        for attempt in range(retry_times):
            try:
                print(f"Calling {self.api_type} API (attempt {attempt+1}/{retry_times})")
                if self.api_type in ["openai"]:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        n=n_samples,
                        extra_body={
                            # "ignore_eos": True,
                            # "skip_special_tokens": False,
                            "chat_template_kwargs": {"enable_thinking": False}
                        } if self.model == "MiniCPM-V-4_5" else {}
                    )
                    if return_list:
                        return [choice.message.content for choice in response.choices]
                    else:
                        assert n_samples == 1
                        return response.choices[0].message.content

                elif self.api_type in ["3rd_openai_glm"]:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=prompt,
                        max_tokens=max_tokens,
                        # temperature=temperature,
                        n=n_samples,
                    )
                    if return_list:
                        return [choice.message.content for choice in response.choices]
                    else:
                        assert n_samples == 1
                        return response.choices[0].message.content
                elif self.api_type == "claude":
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=prompt
                    )
                    return response.content
                    
                elif self.api_type == "3rd_openai" or "qwen" in self.api_type.lower():
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                    
                    # 构建请求body，使用实例配置的参数
                    request_body = {
                        "model": self.model,
                        "messages": prompt,
                        "max_tokens": self.max_tokens if self.max_tokens else max_tokens,
                        "temperature": temperature,
                        "n": n_samples,
                    }
                    
                    # 添加可选参数（仅当配置了时才添加）
                    if self.top_p is not None:
                        request_body["top_p"] = self.top_p
                    if self.top_k is not None:
                        request_body["top_k"] = self.top_k
                    if self.repetition_penalty is not None:
                        request_body["repetition_penalty"] = self.repetition_penalty
                    
                    response = requests.post(
                        os.path.join(self.base_url, "chat/completions"),
                        headers=headers,
                        json=request_body,
                        timeout=timeout,
                    )
                    if response.status_code != 200:
                        error_text = response.text
                        print(f"API request failed: {error_text}")
                        
                        # 检查是否是token长度超限错误
                        if self._is_token_limit_error(error_text):
                            print("Detected token limit error")
                            return "TOKEN_LIMIT_ERROR"
                        
                        if attempt < retry_times - 1:  # Don't sleep on the last attempt
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        return [] if return_list else ""

                    if return_list:
                        return [choice['message']['content'] for choice in response.json()['choices']]
                    else:
                        assert n_samples == 1
                        return response.json()['choices'][0]['message']['content']

                elif self.api_type == "3rd_openai_sn":
                    # 带 sec_info 的第三方 API（参考 llm_client.py 中的 chat_with_image 实现）
                    headers = {
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "sec_info": {
                            "username": getattr(self, 'username', 'xxxx'),
                            "userid": getattr(self, 'userid', 'xxx'),
                            "token": self.api_key
                        },
                        "model_type": "openai",
                        "model_name": self.model,
                        "messages": json.dumps(prompt) if isinstance(prompt, list) else prompt,
                    }
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=timeout,
                    )
                    if response.status_code != 200:
                        error_text = response.text
                        print(f"API request failed: {error_text}")
                        if self._is_token_limit_error(error_text):
                            print("Detected token limit error")
                            return "TOKEN_LIMIT_ERROR"
                        if attempt < retry_times - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                            continue
                        return [] if return_list else ""

                    try:
                        response_data = response.json()
                        if 'error_code' in response_data and response_data['error_code']:
                            print(f"API returned error: {response_data.get('message', 'Unknown error')}")
                            return [] if return_list else ""
                        # model_output 字段（嵌套 JSON 字符串）
                        if 'model_output' in response_data:
                            model_output_str = response_data['model_output']
                            model_output = json.loads(model_output_str) if isinstance(model_output_str, str) else model_output_str
                            if 'choices' in model_output:
                                if return_list:
                                    return [choice['message']['content'] for choice in model_output['choices']]
                                else:
                                    assert n_samples == 1
                                    return model_output['choices'][0]['message']['content']
                            else:
                                print(f"No 'choices' in model_output: {model_output.keys()}")
                                return [] if return_list else ""
                        # 标准 OpenAI 格式 fallback
                        elif 'choices' in response_data:
                            if return_list:
                                return [choice['message']['content'] for choice in response_data['choices']]
                            else:
                                assert n_samples == 1
                                return response_data['choices'][0]['message']['content']
                        else:
                            print(f"Unexpected response format. Keys: {response_data.keys()}")
                            return [] if return_list else ""
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Failed to parse response: {e}")
                        return [] if return_list else ""

                else:
                    print(f"Unsupported LLM type: {self.api_type}")
                    raise ValueError(f"Unsupported LLM type: {self.api_type}")
                    
            except Exception as e:
                error_str = str(e)
                print(f"Error calling {self.api_type} API (attempt {attempt+1}/{retry_times}): {error_str}")
                
                # 检查是否是token长度超限错误
                if self._is_token_limit_error(error_str):
                    print("Detected token limit error in exception")
                    return "TOKEN_LIMIT_ERROR"
                
                if attempt < retry_times - 1:  # Don't sleep on the last attempt
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed after {retry_times} attempts")
                    return "failed in response"

        return [] if return_list else ""

    def _evaluate_with_auto_scale(self, formatted_prompt, initial_img_scale=1.0, task_config=None, trajectory=None, action=None, eval_mode="zerogui"):
        """自动调整图片分辨率并重试评估"""
        current_scale = initial_img_scale
        min_scale = 0.7  # 最小缩放比例
        scale_step = 0.1  # 每次缩放步长
        
        while current_scale >= min_scale:
            print(f"Trying with img_scale: {current_scale}")
            
            # 如果不是第一次尝试，需要重新构建prompt
            if current_scale != initial_img_scale:
                if action is not None:
                    # 重新调用evaluate_task_step构建prompt
                    formatted_prompt = self._build_prompt_for_step(task_config, trajectory, action, eval_mode, current_scale)
                else:
                    # 重新调用evaluate_task构建prompt
                    formatted_prompt = self._build_prompt_for_task(task_config, trajectory, action, eval_mode, current_scale)
            
            # 调用LLM
            analysis = self.call_llm(formatted_prompt, temperature=self.temperature, timeout=self.timeout)
            
            # 检查是否是token长度超限错误
            if analysis == "TOKEN_LIMIT_ERROR":
                print(f"Token limit exceeded with scale {current_scale}, trying smaller scale...")
                current_scale -= scale_step
                current_scale = round(current_scale, 1)  # 避免浮点数精度问题
                continue
            else:
                # 成功获得结果
                if current_scale != initial_img_scale:
                    print(f"Successfully processed with reduced img_scale: {current_scale}\n================================")
                return analysis
        
        # 如果所有尝试都失败了
        print(f"Failed to process even with minimum img_scale: {min_scale}")
        return "failed in response - token limit exceeded even with minimum image scale"

    def _build_prompt_for_task(self, task_config, trajectory, action, eval_mode, img_scale):
        """为evaluate_task构建prompt"""
        instruction = task_config["instruction"]
        system_prompt = self.prompt["system_prompt"]
        user_prompt = self.prompt["user_prompt"]
        actions = trajectory["actions"]
        if action:
            action = int(action)
            action_code = actions[action-1]
        format_args = {'instruction': instruction}
        if "{step_index}" in user_prompt:
            format_args['step_index'] = action
        if "{action_code}" in user_prompt:
            format_args['action_code'] = action_code
        user_prompt = user_prompt.format(**format_args)
        screenshots = trajectory["screenshots"]
        screenshots_marker = trajectory["screenshots_marker"]
        actions = trajectory["actions"]

        # prepare messages based on LLM type
        if self.api_type in ["openai", "3rd_openai", "3rd_openai_glm"] or "qwen" in self.api_type.lower():
            messages = [{"role": "system", "content": system_prompt}]
            user_content = [{"type": "text", "text": user_prompt}]
            
            # Add screenshots
            for i, image_path in enumerate(screenshots):
                if "w_action" in eval_mode:
                    user_content.append({"type": "text", "text": actions[i]})
                    image_path = screenshots_marker[i]

                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{self._encode_image(image_path=image_path, img_scale=img_scale)}",
                        "detail": "high",
                    },
                })
            messages.append({"role": "user", "content": user_content})
            return messages
        elif self.api_type == "claude":
            content = [{"type": "text", "text": user_prompt}]
            for i, image_path in enumerate(screenshots):
                if "w_action" in eval_mode:
                    content.append({"type": "text", "text": actions[i]})
                    image_path = screenshots_marker[i]

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": self._encode_image(image_path=image_path, img_scale=img_scale)
                    }
                })
            return [{"role": "user", "content": content}]
        else:
            raise NotImplementedError(f"Unsupported LLM type: {self.api_type}")

    def _build_prompt_for_step(self, task_config, trajectory, action, eval_mode, img_scale):
        """为evaluate_task_step构建prompt"""
        instruction = task_config["instruction"]
        actions = trajectory["actions"]
        action = int(action)
        action_code = actions[action-1]
        system_prompt = self.prompt["system_prompt"]
        user_prompt = self.prompt["user_prompt"]
        user_prompt1 = user_prompt[0].format(instruction=instruction)
        user_prompt2 = user_prompt[1]
        user_prompt3 = user_prompt[2].format(step_index=action, action_code=action_code)
        screenshots = trajectory["screenshots"]
        screenshots_marker = trajectory["screenshots_marker"]
        assert len(screenshots) == len(actions)

        # prepare messages based on LLM type
        if self.api_type in ["openai", "3rd_openai", "3rd_openai_glm"] or "qwen" in self.api_type.lower():
            messages = [{"role": "system", "content": system_prompt}]
            user_content = [{"type": "text", "text": user_prompt1}]
            
            # Add screenshots
            if "fulltraj" in eval_mode:
                len_history = len(screenshots)
            else:
                len_history = action-1
            for i in range(len_history):
                image_path = screenshots[i]
                if "w_action" in eval_mode:
                    user_content.append({"type": "text", "text": actions[i]})
                    print(user_content[-1])
                    image_path = screenshots_marker[i]

                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{self._encode_image(image_path=image_path, img_scale=img_scale)}",
                        "detail": "high",
                    },
                })
                print(image_path)
            
            user_content.append({"type": "text", "text": user_prompt2})
            print(user_content[-1])
            image_path = screenshots_marker[action-2]
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{self._encode_image(image_path=image_path, img_scale=img_scale)}",
                    "detail": "high",
                },
            })
            print(image_path)
            image_path = screenshots[action-1]
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{self._encode_image(image_path=image_path, img_scale=img_scale)}",
                    "detail": "high",
                },
            })
            print(image_path)
            user_content.append({"type": "text", "text": user_prompt3})
            print(user_content[-1])
            messages.append({"role": "user", "content": user_content})
            return messages
        else:
            raise NotImplementedError(f"Unsupported LLM type: {self.api_type}")

    def evaluate_task(self, task_config: dict, trajectory: dict, action=None, eval_mode="zerogui", img_scale=1.0):
        """Evaluate task completion using screenshots and instruction
        
        Args:
            task_config: osworld task config
            trajectory: screenshots and other info
        
        Returns:
            Tuple of (reward, confidence) where:
                reward: 1.0 for success, 0.0 for failure
                confidence: Float between 0.0 and 1.0
        """
        try:
            # 构建初始prompt
            formatted_prompt = self._build_prompt_for_task(task_config, trajectory, action, eval_mode, img_scale)
            
            # 使用自动缩放重试机制
            analysis = self._evaluate_with_auto_scale(
                formatted_prompt, img_scale, task_config, trajectory, action, eval_mode
            )
            
            eval_outputs = {
                "llm_output": analysis,
            }
            return eval_outputs
            
        except Exception as e:
            print(f"Error in evaluate_task: {str(e)}")
            raise

    def evaluate_task_step(self, task_config: dict, trajectory: dict, action=None, eval_mode="zerogui", img_scale=1.0):
        """Evaluate task completion using screenshots and instruction
        
        Args:
            task_config: osworld task config
            trajectory: screenshots and other info
        
        Returns:
            Tuple of (reward, confidence) where:
                reward: 1.0 for success, 0.0 for failure
                confidence: Float between 0.0 and 1.0
        """
        try:
            # 构建初始prompt
            formatted_prompt = self._build_prompt_for_step(task_config, trajectory, action, eval_mode, img_scale)
            
            # 使用自动缩放重试机制
            analysis = self._evaluate_with_auto_scale(
                formatted_prompt, img_scale, task_config, trajectory, action, eval_mode
            )
            
            eval_outputs = {
                "llm_output": analysis,
            }
            return eval_outputs
            
        except Exception as e:
            print(f"Error in evaluate_task: {str(e)}")
            raise

if __name__ == '__main__':
    raise SystemExit(
        "LLMEvaluator is a library module. Use `python3 -m cuarewardbench.cli.eval_benchmark --help` "
        "or `python3 -m cuarewardbench.cli.eval_trajectory --help` for runnable entrypoints."
    )
