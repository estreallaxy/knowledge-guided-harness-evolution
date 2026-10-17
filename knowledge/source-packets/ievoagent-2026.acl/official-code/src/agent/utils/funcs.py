from src.agent.memory import dialogTraj, feedbackMatrix
from configs import agent_config as agentcfg
from src.agent.utils import prompts

from openai import OpenAI

# 配置客户端 - 使用 Rewriter API（避免 Gemini 欠费）
client = OpenAI(
    base_url=agentcfg.UTILS_LLM_URL,
    api_key=agentcfg.UTILS_LLM_APIKEY,
)
MODEL_NAME = agentcfg.UTILS_LLM_MODEL_NAME

client_rewriter = OpenAI(
    base_url=agentcfg.REWRITER_LLM_URL,
    api_key=agentcfg.REWRITER_LLM_API_KEY,
)
MODEL_NAME_REWRITER = agentcfg.REWRITER_LLM_MODEL_NAME

def chatWithMessages(messages: list,rewrite=False) -> str:
    """
    基于 Messages 列表进行对话 (支持多轮上下文、System Prompt)
    
    Args:
        messages: 列表，格式如 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
    """
    try:
        if not rewrite:
            # print(MODEL_NAME,agentcfg.UTILS_LLM_URL)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=agentcfg.u_temperature, 
                max_tokens=agentcfg.u_max_tokens,
            )
        else:
            # print(MODEL_NAME_REWRITER,agentcfg.REWRITER_LLM_URL)
            response = client_rewriter.chat.completions.create(
                model=MODEL_NAME_REWRITER,
                messages=messages,
                temperature=agentcfg.u_temperature, 
                max_tokens=agentcfg.u_max_tokens,
            )
        # print(response)
        if response.choices[0].message.content==None:
            raise Exception(f"{agentcfg.Colors.YELLOW}[DEBUG]{agentcfg.Colors.RESET} LLM returned None content, response: {response}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} In chat_with_messages: {e}")
        return ""

def chatWithString(prompt: str, system_prompt: str = "You are a helpful assistant.", rewrite = False) -> str:
    """
    基于普通 String 进行对话 (单轮问答)
    会自动帮你构造成 messages 格式
    """
    if system_prompt != "":

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    else:
        messages = [{"role": "user", "content":prompt}]
    # print(messages)
    if rewrite:
        return chatWithMessages(messages, rewrite=rewrite)
    return chatWithMessages(messages)
import json
import re
def parseJSONString(json_string: str) -> dict:
    """
    使用正则提取并解析 JSON 字符串，过滤前后解释性文字
    """
    if not json_string:
        return {}
        
    try:
        # 1. 尝试直接解析（性能最高）
        return json.loads(json_string)
    except json.JSONDecodeError:
        try:
            # 2. 如果直接解析失败，尝试提取第一个 { 和最后一个 } 之间的内容
            # [^]*? 是为了匹配包括换行符在内的所有内容
            match = re.search(r'(\{[\s\S]*\})', json_string)
            if match:
                clean_json = match.group(1)
                return json.loads(clean_json)
            else:
                # 针对极其特殊的情况，如果 LLM 没返回括号
                print(f"[ERROR] No JSON object found in: {json_string}")
                return {}
        except Exception as e:
            print(f"[ERROR] JSON Extraction/Decode Error: {e}")
            print(f"[ERROR] Raw Input Data: {json_string}")
            return {}


def parseLLMResponseType(history, user_input, llm_response):
    ORDER_LLM = ["NE", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11"]
    DEFAULT_LLM = "NE"  # 定义兜底默认值 (通常 NE 表示 Normal/Neutral)

    # print(f"[src.utils.funcs.parseLLMResponseType] Analyzing LLM response ({len(history)} turns)......")

    llm_type = DEFAULT_LLM  # 初始化为默认值
    res = None  # 初始化 res

    try:
        # 1. 调用 LLM
        # 注意：这里假设 prompts 中有对应的 instruction 和 sys 定义，且 instruction 需要三个参数
        res = chatWithString(
            prompts.parseLLMResponseType_prompt_instruction.format(
                history=history, 
                user_input=user_input, 
                ai_response=llm_response),
            prompts.parseLLMResponseType_prompt_sys
        )

        # 2. 尝试解析 JSON
        parsed_obj = parseJSONString(res)

        # 2.1 额外检查：确保解析出来的是字典
        if not isinstance(parsed_obj, dict):
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} JSON parse result is not a dict: {type(parsed_obj)}")
            llm_type = DEFAULT_LLM
        else:
            # 3. 获取字段 (假设 JSON key 为 "llm_response_type")
            llm_type = parsed_obj.get("llm_response_type", DEFAULT_LLM)

            # 4. 校验合法性：解析出来的 type 是否在允许列表中
            if llm_type not in ORDER_LLM:
                print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} Invalid LLM type detected: '{llm_type}'. Fallback to '{DEFAULT_LLM}'.")
                llm_type = DEFAULT_LLM

    except Exception as e:
        # 5. 捕获所有异常
        print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Failed to parse LLM response type. Error: {e}")
        print(f"{agentcfg.Colors.YELLOW}[DEBUG]{agentcfg.Colors.RESET} Raw response was: {res}")
        llm_type = DEFAULT_LLM

    # print(f"[src.utils.funcs.parseLLMResponseType] LLM Type: {llm_type}")
    return llm_type

def parseUserFeedbackType(history, llm_response, user_input):
    ORDER_FB = ["NEU", "NEG_1", "NEG_2", "NEG_3", "NEG_4", "NEG_5", "POS", "STOP"]
    DEFAULT_FB = "NEU"  # 定义兜底默认值

    # print(f"[src.utils.funcs.parseUserFeedbackType] Sending history ({len(history)} turns)...")

    ufb_type = DEFAULT_FB  # 初始化为默认值
    res = None  # 初始化 res，防止报错时引用未定义变量
    # print("In parseUserFeedbackType")
    try:
        # 1. 调用 LLM
        res = chatWithString(
            prompts.parseUserFeedbackType_prompt_instruction.format(history=history,ai_response=llm_response, user_input=user_input),
            prompts.parseUserFeedbackType_prompt_sys
        )
        # print("LLM Response for User Feedback Type:", res)
        # 2. 尝试解析 JSON

        parsed_obj = parseJSONString(res)
        

        # 2.1 额外检查：确保解析出来的是字典
        if not isinstance(parsed_obj, dict):
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} JSON parse result is not a dict: {type(parsed_obj)}")
            ufb_type = DEFAULT_FB
        else:
            # 3. 获取字段
            ufb_type = parsed_obj.get("user_feedback_category", DEFAULT_FB)

            # 4. 校验合法性：解析出来的 type 是否在允许列表中
            if ufb_type not in ORDER_FB:
                print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} Invalid feedback type detected: '{ufb_type}'. Fallback to '{DEFAULT_FB}'.")
                ufb_type = DEFAULT_FB

    except Exception as e:
        # 5. 捕获所有异常（网络错误、JSON解析错误等）
        print(f"{agentcfg.Colors.RED}[ERROR]{agentcfg.Colors.RESET} Failed to parse user feedback. Error: {e}")
        print(f"{agentcfg.Colors.YELLOW}[DEBUG]{agentcfg.Colors.RESET} Raw response was: {res}")
        ufb_type = DEFAULT_FB

    # print(f"[src.utils.funcs.parseUserFeedbackType] User Feedback: {ufb_type}")
    return ufb_type

# if __name__ == "__main__":
#     history = [
#   {
#     "content": "hello",
#     "role": "user"
#   },
#   {
#     "content": "Hello there! How can I assist you today?",
#     "role": "assistant"
#   },
#   {
#     "content": "who are you",
#     "role": "user"
#   },
#   {
#     "content": "I am an AI language model created by OpenAI, designed to respond to text-based queries and assist with various tasks. How can I help you today?",
#     "role": "assistant"
#   },
#   {
#     "content": "whats your name",
#     "role": "user"
#   },
#   {
#     "content": "I am a language model created by OpenAI, and my programming does not include a human-like name. You can call me OpenAI if that helps.",
#     "role": "assistant"
#   },
#   {
#     "content": "are you chat gpt 3.5",
#     "role": "user"
#   },
#   {
#     "content": "As an OpenAI language model, I am part of the GPT (Generative Pretrained Transformer) family of models. However, I cannot say that I am specifically GPT 3.5, as there is currently no such version designation from OpenAI. I incorporate improvements and updates to the GPT architecture, which allows me to provide high-quality responses and perform a wide range of language tasks.",
#     "role": "assistant"
#   }
# ]
#     for i in range(len(history)//2):
#         parseLLMResponseType(history[:i*2], history[i*2]["content"],history[i*2+1]["content"])
        # parseUserFeedbackType(history[:i*2+1], history[i*2+1]["content"],history[i*2+2]["content"])



