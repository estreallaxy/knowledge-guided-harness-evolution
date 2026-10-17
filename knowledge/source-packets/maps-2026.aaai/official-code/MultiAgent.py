import base64
import json
from idlelib.window import add_windows_to_menu
from io import BytesIO
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.messages import ChatMessage, TextMessage, MultiModalMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
import requests
from autogen_core import Image as AGImage
from PIL import Image
from Prompt import *
from Config import *
from google import genai
from google.genai import types
from typing import Callable, Sequence
import openai
from openai import OpenAI
from pydantic import BaseModel

def image_to_base64(image: Image.Image, fmt='png') -> str:
    output_buffer = BytesIO()
    image.save(output_buffer, format=fmt)
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode('utf-8')
    return f'data:image/{fmt};base64,' + base64_str

class Process(BaseModel):
    Phase1: str
    Phase2: str
    Phase3: str
    Phase4: str

class Solution(BaseModel):
    process: Process
    final_answer: str

class Score(BaseModel):
    caption: int
    alignment: int
    knowledge: int
    solution: int

class Feedback(BaseModel):
    caption: str
    alignment: str
    knowledge: str
    solution: str

class Critic(BaseModel):
    score: Score
    need_feedback: bool
    worst_step: str
    feedback: Feedback

class ScoreWoImg(BaseModel):
    alignment: int
    knowledge: int
    solution: int

class FeedbackWoImg(BaseModel):
    alignment: str
    knowledge: str
    solution: str

class CriticWoImg(BaseModel):
    score: ScoreWoImg
    need_feedback: bool
    worst_step: str
    feedback: FeedbackWoImg

class UserProxyAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Responsible for receiving user input.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [MultiModalMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("UserProxyAgent is called")

        return Response(chat_message=messages)

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

class InterpreterAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Analyze the information in the image.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("InterpreterAgent is called")

        if len(messages[0]) == 2:
            if "Improve the description based on the following feedback:" in messages[0][0]:
                feedback = messages[0][0]
                img = messages[0][1]
                prompt = [prompt_interpreter + feedback, img]
            else:
                prompt = [messages[0][0], messages[0][1]]
        elif len(messages[0]) > 2:
            if "Improve the description based on the following feedback:" in messages[0][0]:
                feedback = messages[0][0]
                prompt = [prompt_interpreter_m + feedback]
            else:
                prompt = [prompt_interpreter_m]

            for i in range(1, len(messages[0])):
                prompt.append(messages[0][i])
        else:
            response = TextMessage(content = "No image input, Caption is None.", source=self.name)
            return Response(chat_message=response)

        try:
            if SWITCH == 1:
                response_text = await self.call_oaLMM(prompt)
            elif SWITCH == 0:
                response_text = await self.call_LMM(prompt)
            elif SWITCH == 2:
                response_text = await self.call_QWEN(prompt)

        except Exception as e:
            print(e)
        # print(response_text)
        response_message = TextMessage(content=response_text, source=self.name)
        return Response(chat_message=response_message)
    
    async def call_LMM(self, prompt):
        client = genai.Client(api_key = API_KEY_GOOGLE)
        response = client.models.generate_content(
            model=MODEL_GOOGLE,
            contents=prompt)

        return response.text

    async def call_oaLMM(self, prompt):
        openai.api_key = API_KEY
        content = [{
            "type": "text",
            "text": prompt[0],
        }]
        for i in range(1, len(prompt)):
            url = {
                "type": "image_url",
                "image_url": {
                    "url": image_to_base64(prompt[i], 'jpeg')},
            }
            content.append(url)
        completion = openai.chat.completions.create(
            model = MODEL_INTERPRETER,
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return completion.choices[0].message.content

    async def call_QWEN(self, prompt):
        client = OpenAI(
            base_url = BASE_URL_QWEN,
            api_key = API_KEY_QWEN
        )
        content = [{
            "type": "text",
            "text": prompt[0],
        }]
        for i in range(1, len(prompt)):
            url = {
                "type": "image_url",
                "image_url": {
                    "url": image_to_base64(prompt[i], 'jpeg')},
            }
            content.append(url)
        completion = client.chat.completions.create(
            model=MODEL_QWEN,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return completion.choices[0].message.content

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

class AlignerAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Make sure the caption is aligned with the corresponding context.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("AlignerAgent is called")

        prompt = prompt_aligner
        if "Improve the description based on the following feedback:" in messages[0]:
            feedback = messages[0]
            align_input = messages[1]
            prompt = prompt + align_input + feedback
        else:
            prompt = prompt + messages[0]

        if SWITCH == 1:
            response_text = await self.call_oaLLM(prompt)
        elif SWITCH == 0:
            response_text = await self.call_LLM(prompt)
        elif SWITCH == 2:
            response_text = await self.call_QWEN(prompt)
        # print(response_text)
        response_message = TextMessage(content=response_text, source=self.name)
        return Response(chat_message=response_message)

    async def call_LLM(self, prompt):
        client = genai.Client(api_key=API_KEY_GOOGLE)
        response = client.models.generate_content(
            model=MODEL_GOOGLE,
            contents=[prompt])

        return response.text

    async def call_oaLLM(self, prompt):
        openai.api_key = API_KEY
        completion = openai.chat.completions.create(
            model=MODEL_ALIGNER,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content

    async def call_QWEN(self, prompt):
        client = OpenAI(
            base_url=BASE_URL_QWEN,
            api_key=API_KEY_QWEN
        )
        completion = client.chat.completions.create(
            model=MODEL_QWEN,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

class ScholarAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Search for potentially useful physics knowledge.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("ScholarAgent is called")

        prompt = prompt_scholar
        if "Improve the description based on the following feedback:" in messages[0]:
            feedback = messages[0]
            search_input = messages[1]
            prompt = prompt + search_input + feedback
        else:
            prompt = prompt + messages[0]

        if SWITCH == 1:
            response_text = await self.call_oaLLM(prompt)
        elif SWITCH == 0:
            response_text = await self.call_LLM(prompt)
        elif SWITCH == 2:
            response_text = await self.call_QWEN(prompt)
        # print(response_text)
        response_message = TextMessage(content=response_text, source=self.name)

        return Response(chat_message=response_message)

    async def call_LLM(self, prompt):
        client = genai.Client(api_key=API_KEY_GOOGLE)
        response = client.models.generate_content(
            model=MODEL_GOOGLE,
            contents=[prompt])

        return response.text

    async def call_oaLLM(self, prompt):
        openai.api_key = API_KEY
        completion = openai.chat.completions.create(
            model=MODEL_SCHOLAR,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content

    async def call_QWEN(self, prompt):
        client = OpenAI(
            base_url=BASE_URL_QWEN,
            api_key=API_KEY_QWEN
        )
        completion = client.chat.completions.create(
            model=MODEL_QWEN,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return completion.choices[0].message.content
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

class SolverAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Solve the physics problem based on all the above content.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("SolverAgent is called")

        prompt = prompt_solver
        if "Improve the description based on the following feedback:" in messages[0]:
            feedback = messages[0]
            solution_input = messages[1]
            prompt = prompt + solution_input + feedback
        else:
            prompt = prompt + messages[0]

        if SWITCH == 1:
            response_text = await self.call_oaLLM(prompt)
        elif SWITCH == 0:
            response_text = await self.call_LLM(prompt)
        elif SWITCH == 2:
            response_text = await self.call_QWEN(prompt)
        # print(response_text)
        response_message = TextMessage(content=response_text, source=self.name)
        return Response(chat_message=response_message)
    
    async def call_LLM(self, prompt):
        client = genai.Client(api_key=API_KEY_GOOGLE)
        response = client.models.generate_content(
            model = MODEL_GOOGLE,
            contents = prompt,
            config={'response_mime_type' : "application/json"},
        )
        # print(response.text)
        return response.text

    async def call_oaLLM(self, prompt):
        openai.api_key = API_KEY
        completion = openai.beta.chat.completions.parse(
            model=MODEL_SCHOLAR,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format = Solution
        )
        return completion.choices[0].message.content

    async def call_QWEN(self, prompt):
        client = OpenAI(
            base_url=BASE_URL_QWEN,
            api_key=API_KEY_QWEN
        )
        completion = client.beta.chat.completions.parse(
            model=MODEL_QWEN,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format = Solution
        )
        return completion.choices[0].message.content
    
    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass

class CriticAgent(BaseChatAgent):
    def __init__(self, name: str):
        super().__init__(name, "Evaluate the quality of each step's output.")

    @property
    def produced_message_types(self) -> Sequence[type[ChatMessage]]:
        return [TextMessage]

    async def on_messages(self, messages: Sequence[ChatMessage], cancellation_token: CancellationToken) -> Response:
        print("CriticAgent is called")

        step_history = eval(messages[0])
        img = messages[1]
        ques = messages[2]
        if isinstance(img, Image.Image):
            img = [img]
        evaluation = await self._evaluate_steps(step_history, img, ques)

        return Response(chat_message=TextMessage(content=str(evaluation), source=self.name))

    async def _evaluate_steps(self, step_history: dict, image, question):
        if len(image) == 0:
            prompt = prompt_critic_woimg + f"""
            Question: {question}
            
            Steps to be evaluated:
            {json.dumps(step_history, indent=2, ensure_ascii=False)}
    
            Output JSON structured as:
            {{
                "scores": {{
                    "alignment": score,
                    "knowledge": score,
                    "solution": score,
                }},
                "need_feedback": boolean,
                "worst_step": "step_name",
                "feedback": {{
                    "alignment": "feedback_alignment",
                    "knowledge": "feedback_knowledge",
                    "solution": "feedback_solution",
                }}
            }}"""
        else:
            prompt = prompt_critic + f"""
            Question: {question}
            
            Steps to be evaluated:
            {json.dumps(step_history, indent=2, ensure_ascii=False)}
    
            Output JSON structured as:
            {{
                "scores": {{
                    "caption": score,
                    "alignment": score,
                    "knowledge": score,
                    "solution": score,
                }},
                "need_feedback": boolean,
                "worst_step": "step_name",
                "feedback": {{
                    "caption": "feedback_caption",
                    "alignment": "feedback_alignment",
                    "knowledge": "feedback_knowledge",
                    "solution": "feedback_solution",
                }}
            }}"""

        try:
            if SWITCH == 1:
                r = await self.call_oaLMM(prompt, image)
            elif SWITCH == 0:
                r = await self.call_LMM(prompt, image)
            elif SWITCH == 2:
                r = await self.call_QWEN(prompt, image)

            return r

        except Exception as e:
            print(f"Critic failed: {str(e)}")
            return {"need_feedback": False}

    async def call_LMM(self, prompt, image):
        client = genai.Client(api_key=API_KEY_GOOGLE)
        content = [prompt]
        for img in image:
            content.append(img)
        response = client.models.generate_content(
            model=MODEL_GOOGLE,
            contents=content,
            config={'response_mime_type': "application/json"},
        )
        # print(response.text)
        return json.loads(response.text)

    async def call_oaLMM(self, prompt, image):
        openai.api_key = API_KEY
        content = [{
            "type": "text",
            "text": prompt,
        }]
        for img in image:
            url = {
                "type": "image_url",
                "image_url": {
                    "url": image_to_base64(img, 'jpeg')},
            }
            content.append(url)
        if len(image) == 0:
            completion = openai.beta.chat.completions.parse(
                model=MODEL_CRITIC,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                response_format=CriticWoImg
            )
        else:
            completion = openai.beta.chat.completions.parse(
                model=MODEL_CRITIC,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                response_format=Critic
            )
        # print(completion.choices[0].message.content)
        return json.loads(completion.choices[0].message.content)


    async def call_QWEN(self, prompt, image):
        client = OpenAI(
            base_url=BASE_URL_QWEN,
            api_key=API_KEY_QWEN
        )
        content = [{
            "type": "text",
            "text": prompt,
        }]
        for img in image:
            url = {
                "type": "image_url",
                "image_url": {
                    "url": image_to_base64(img, 'jpeg')},
            }
            content.append(url)
        if len(image) == 0:
            completion = client.beta.chat.completions.parse(
                model=MODEL_QWEN,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                response_format=CriticWoImg
            )
        else:
            completion = client.beta.chat.completions.parse(
                model=MODEL_QWEN,
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                response_format=Critic
            )
        # print(completion.choices[0].message.content)
        return json.loads(completion.choices[0].message.content)


    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        pass