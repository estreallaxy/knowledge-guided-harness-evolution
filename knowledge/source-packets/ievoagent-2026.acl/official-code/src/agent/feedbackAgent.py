# import os
# import sys
# from typing import List, Optional
# import uuid

# # LangChain 核心组件
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.tools import tool
# from langchain.agents import create_agent

# from langchain_core.messages import convert_to_messages

# import configs.agent_config as agentcfg
# import src.agent.utils.funcs as funcs
# from src.agent.memory.feedbackMatrix import FeedbackMatrixManager
# from src.agent.memory.dialogTraj import DialogTraj

# from src.agent.rewriter.refinement_agent import RefinementAgent


# # @tool
# # def search(query: str) -> str:
# #     """Use Tavily Search to answer questions about current events."""
# #     os.environ["TAVILY_API_KEY"] = agentcfg.TAVILY_API_KEY
# #     searcher = TavilySearch(max_results=2)
# #     search_results = searcher.invoke(query)
# #     return search_results

# # tools = [search]


# class LangChainAgent:
#     def __init__(self, 
#                  model_name: str, 
#                  local_api_base: Optional[str] = None, 
#                  api_key: Optional[str] = None,
#                  system_prompt: str = "You are helpful AI assistant.",
#                  tools = [],
#                  alpha = 0.2,
#                  base_path = agentcfg.MatrixBasePath,
#                  user_path = agentcfg.MatrixUserPath
#                  ):
#         """
#         初始化 Agent。
        
#         Args:
#             model_name: 模型名称 (例如 'gpt-3.5-turbo' 或本地模型的名称 'qwen2.5-7b')
#             local_api_base: 本地 API 地址 (例如 'http://localhost:8000/v1')。
#                             如果不填，默认连接官方 OpenAI API。
#             api_key: API Key。如果是本地模型，通常可以随便填一个字符串。
#             system_prompt: 系统提示词。
#         """
#         self.agentID = str(uuid.uuid4())
#         self.feedbackMatrixManager = FeedbackMatrixManager(base_path, user_path, alpha=alpha)
#         self.dialogTraj = DialogTraj(system_prompt=system_prompt)
#         self.system_prompt = system_prompt
#         self.original_system_prompt = system_prompt  # Keep original prompt for reference
#         # --- 核心逻辑：区分本地还是云端 ---
#         if local_api_base:
#             print(f"[Init] Connecting Local / Custom Model: {local_api_base} | Model: {model_name}")
#             self.llm = ChatOpenAI(
#                 model=model_name,
#                 openai_api_base=local_api_base, # 关键：指向本地地址
#                 openai_api_key=api_key or "EMPTY", # 本地通常不需要 Key，但参数不能为 None
#                 temperature= agentcfg.temperature,
#                 max_tokens = agentcfg.max_tokens
#             )
#         else:
#             print(f"[Init] Connecting Online API | Model: {model_name}")
#             self.llm = ChatOpenAI(
#                 model=model_name,
#                 openai_api_key=api_key,
#                 temperature=0,
#             )
        
#         self.agent_executor = create_agent(model=self.llm,tools=tools,system_prompt=system_prompt)
#         # 维护对话历史 (Memory)
#         self.memory: List[BaseMessage] = []

#     def reset_memory(self):
#         """清空历史"""
#         self.memory = []
#         self.dialogTraj.reset()
#     def after_get_user_instruction(self, user_input):
#         """1. 解析反馈类型"""
#         if len(self.memory) < 2:
#             return
#         print(self.memory)
#         user_feedback_type = funcs.parseUserFeedbackType(self.memory, self.memory[-1].content, user_input)
#         self.dialogTraj.turns[-1]["user_feedback"] = user_feedback_type
#         self.feedbackMatrixManager.update_user_feedback(self.dialogTraj.turns[-1]["llm_type"], user_feedback_type, count=1)

#     def after_get_user_instruction_messages(self, messages):
#         """1. 解析反馈类型"""
#         user_feedback_type = funcs.parseUserFeedbackType(messages[:-2], messages[-2]["content"], messages[-1]["content"])
#         return user_feedback_type


#     def after_response(self, user_input, llm_response):
#         """1. 解析回复类型"""
#         llm_type = funcs.parseLLMResponseType(self.memory, user_input, llm_response)
#         self.memory.append(HumanMessage(content=user_input))
#         self.memory.append(AIMessage(content=llm_response))
#         self.dialogTraj.add_turn( 
#                  user_input, 
#                  llm_response, 
#                  llm_type
#         )
    
#     def after_response_messages(self, messages):
#         """1. 解析回复类型"""
#         llm_type = funcs.parseLLMResponseType(messages[:-2], messages[-2]["content"], messages[-1]["content"])
#         return llm_type

    
#     def chat(self, user_input: str) -> str:
#         """
#         进行多轮对话
#         """
#         # 1. 构建当前完整的 Prompt 结构： System + History + User Input
#         # 注意：LangChain 的 invoke 可以直接接受 Message 列表
        
#         # messages = [{"role": "system", "content": self.system_prompt}]
        
#         # # 加上之前的历史
#         # messages.extend(self.memory)
        
#         # # 加上当前用户输入
#         # messages.append({"role":"user", "content": user_input})

#         messages = [SystemMessage(content=self.system_prompt)]
        
#         # 加上之前的历史
#         messages.extend(self.memory)
        
#         # 加上当前用户输入
#         messages.append(HumanMessage(content=user_input))

#         try:
#             # 2. 调用 LLM
#             # print(messages)
#             self.after_get_user_instruction(user_input)
#             response_message = self.agent_executor.invoke({"messages":messages})
#             ai_content = response_message['messages'][-1].content

#             # 3. 更新记忆 (只有成功回复后才更新)
#             # self.memory.append(HumanMessage(content=user_input))
#             # self.memory.append(AIMessage(content=ai_content))
#             self.after_response(user_input, ai_content)

#             return ai_content

#         except Exception as e:
#             return f"Error invoking model: {e}"

#     # def chat_with_messages(self, messages: List[BaseMessage]) -> str:
#     #     """
#     #     进行多轮对话，直接传入消息列表
#     #     """
#     #     try:
#     #         # 2. 调用 LLM
            
#     #         self.after_get_user_instruction_messages(messages)
            
#     #         response_message = self.agent_executor.invoke({"messages": messages})
#     #         ai_content = response_message['messages'][-1].content
#     #         self.after_response_messages(messages)

#     #         return ai_content

#     #     except Exception as e:
#     #         return f"Error invoking model: {e}"
    

#     def chat_with_messages(self, messages: List[dict]) -> str:
#         """
#         接收 OpenAI 风格的消息列表，例如：
#         [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
#         """
#         try:
#             # 转换为 LangChain BaseMessage 列表
#             lc_messages = convert_to_messages(messages)
#             # 分析反馈（注意：parseUserFeedbackType 需要 BaseMessage 列表）
#             if len(messages) >= 2:
#                 user_type = self.after_get_user_instruction_messages(messages)
#                 print(f"[DEBUG] Parsed user feedback type: {user_type}")
#             else:
#                 user_type = "NEU"
#             # 调用 agent
#             response_message = self.agent_executor.invoke({"messages": lc_messages})
#             ########################################
#             # Rewrite
            
            
#             # Initialize RefinementAgent (only once, can be cached)
#             if not hasattr(self, '_refinement_agent'):
#                 self._refinement_agent = RefinementAgent()
            
#             # Get initial response from agent
#             initial_response = response_message['messages'][-1].content
            
#             # Use rewriter to refine the response
#             refine_result = self._refinement_agent.generate_and_refine(
#                 history=messages,
#                 initial_response=initial_response,
#                 custom_prompt=self.system_prompt,
#                 verbose=True,  # Set to True to see detailed logs
#                 user_type = user_type if len(messages) >= 2 else "NEU"
#             )
            
#             # Get the final refined response
#             ai_content = refine_result['final_response']
            
#             # Update system_prompt with the optimized version
#             optimized_prompt = refine_result['final_prompt']
#             if optimized_prompt and optimized_prompt != self.system_prompt:
#                 print(f"[Rewriter] New prompt: {optimized_prompt[:80]}...")
#                 self.system_prompt = optimized_prompt  # Update to use optimized prompt
#                 # Also update dialogTraj to use the new prompt
#                 self.dialogTraj.system_prompt = optimized_prompt
#             # 输出ai_content
#             ########################################
#             new_messages = messages + [{"role": "assistant", "content": ai_content}]
#             llm_type = self.after_response_messages(new_messages)
#             print(f"[DEBUG] Parsed LLM response type: {llm_type}")

#             return ai_content

#         except Exception as e:
#             return f"Error invoking model: {e}"
    
#     def get_history(self):
#         return self.memory

# # ================= 使用示例 =================

# def main():
#     tools = []
#     local_url = agentcfg.LLM_LOCAL_URL
#     model_name = agentcfg.LLM_MODEL_NAME
        
#     agent = LangChainAgent(
#         model_name="qwen2.5-7b", # 这里填你本地服务的模型名
#         local_api_base="http://localhost:8001/v1",
#         tools= tools,
#         api_key="EMPTY", # 本地可以随意,
#         alpha = 0
#     )

#     # # --- 场景 B: 官方 API ---
#     # api_key = os.getenv("OPENAI_API_KEY") # 或者直接填 "sk-..."
#     # if not api_key:
#     #     print("请设置 OPENAI_API_KEY")
#     #     return
        
#     # agent = LangChainAgent(
#     #     model_name="gpt-3.5-turbo",
#     #     local_api_base=None, # 设为 None 就是走官方
#     #     api_key=api_key
#     # )

#     # --- 开始对话循环 (代码完全一样) ---
#     print(f"\n=== {agent.llm.model_name} Agent Start ===")
#     messages = []
#     while True:
#         user_text = input("\nUser: ")
#         if user_text.lower() in ["quit", "exit"]:
#             break
#         messages.append({"role":"user", "content": user_text})
#         response = agent.chat_with_messages(messages)
#         messages.append({"role":"assistant", "content": response})
#         print(f"AI: {response}")
#     print(agent.feedbackMatrixManager.total_df)

# if __name__ == "__main__":
#     main()






import os
import sys
from typing import List, Optional
import uuid

# LangChain 核心组件
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_agent

from langchain_core.messages import convert_to_messages

import configs.agent_config as agentcfg
import src.agent.utils.funcs as funcs
from src.agent.memory.feedbackMatrix import FeedbackMatrixManager
from src.agent.memory.dialogTraj import DialogTraj

from src.agent.rewriter.refinement_agent import RefinementAgent
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# @tool
# def search(query: str) -> str:
#     """Use Tavily Search to answer questions about current events."""
#     os.environ["TAVILY_API_KEY"] = agentcfg.TAVILY_API_KEY
#     searcher = TavilySearch(max_results=2)
#     search_results = searcher.invoke(query)
#     return search_results

# tools = [search]

refinementAgentTokenizer = AutoTokenizer.from_pretrained("/data2/models/Qwen2.5-7B-Instruct")
refinementAgentModel = AutoModelForCausalLM.from_pretrained("/data2/models/Qwen2.5-7B-Instruct",device_map="auto")

class LangChainAgent:
    def __init__(self, 
                 model_name: str, 
                 local_api_base: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 system_prompt: str = "You are a helpful assistant.",
                 tools = [],
                 alpha = 0.0001,
                 base_path = agentcfg.MatrixBasePath,
                 user_path = agentcfg.MatrixUserPath
                 ):
        """
        初始化 Agent。
        
        Args:
            model_name: 模型名称 (例如 'gpt-3.5-turbo' 或本地模型的名称 'qwen2.5-7b')
            local_api_base: 本地 API 地址 (例如 'http://localhost:8000/v1')。
                            如果不填，默认连接官方 OpenAI API。
            api_key: API Key。如果是本地模型，通常可以随便填一个字符串。
            system_prompt: 系统提示词。
        """
        self.agentID = str(uuid.uuid4())
        self.feedbackMatrixManager = FeedbackMatrixManager(base_path, user_path, alpha=alpha)
        self.dialogTraj = DialogTraj(system_prompt=system_prompt)
        self.system_prompt = system_prompt
        self.original_system_prompt = system_prompt  # Keep original prompt for reference
        self.last_llm_type = "NE"
        # --- 核心逻辑：区分本地还是云端 ---
        if local_api_base:
            print(f"[Init] Connecting Local / Custom Model: {local_api_base} | Model: {model_name}")
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_base=local_api_base, # 关键：指向本地地址
                openai_api_key=api_key or "EMPTY", # 本地通常不需要 Key，但参数不能为 None
                temperature= agentcfg.temperature,
                max_tokens = agentcfg.max_tokens
            )
        else:
            print(f"[Init] Connecting Online API | Model: {model_name}")
            self.llm = ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                temperature=0.7,
            )
        
        self.agent_executor = create_agent(model=self.llm,tools=tools,system_prompt=system_prompt)
        # 维护对话历史 (Memory)
        self.memory: List[BaseMessage] = []

    def reset_memory(self):
        """清空历史"""
        self.memory = []
        self.dialogTraj.reset()
    def after_get_user_instruction(self, user_input):
        """1. 解析反馈类型"""
        if len(self.memory) < 2:
            return
        # print(self.memory)
        user_feedback_type = funcs.parseUserFeedbackType(self.memory, self.memory[-1].content, user_input)
        self.dialogTraj.turns[-1]["user_feedback"] = user_feedback_type
        self.feedbackMatrixManager.update_user_feedback(self.dialogTraj.turns[-1]["llm_type"], user_feedback_type, count=1)

    def after_get_user_instruction_messages(self, messages):
        """1. 解析反馈类型"""
        user_feedback_type = funcs.parseUserFeedbackType(messages[:-2], messages[-2]["content"], messages[-1]["content"])
        self.feedbackMatrixManager.update_user_feedback(self.last_llm_type, user_feedback_type, count=1)
        return user_feedback_type


    def after_response(self, user_input, llm_response):
        """1. 解析回复类型"""
        llm_type = funcs.parseLLMResponseType(self.memory, user_input, llm_response)
        self.memory.append(HumanMessage(content=user_input))
        self.memory.append(AIMessage(content=llm_response))
        self.dialogTraj.add_turn( 
                 user_input, 
                 llm_response, 
                 llm_type
        )
    
    def after_response_messages(self, messages):
        """1. 解析回复类型"""
        llm_type = funcs.parseLLMResponseType(messages[:-2], messages[-2]["content"], messages[-1]["content"])
        return llm_type

    
    def chat(self, user_input: str) -> str:
        """
        进行多轮对话
        """
        # 1. 构建当前完整的 Prompt 结构： System + History + User Input
        # 注意：LangChain 的 invoke 可以直接接受 Message 列表
        
        # messages = [{"role": "system", "content": self.system_prompt}]
        
        # # 加上之前的历史
        # messages.extend(self.memory)
        
        # # 加上当前用户输入
        # messages.append({"role":"user", "content": user_input})

        messages = [SystemMessage(content=self.system_prompt)]
        
        # 加上之前的历史
        messages.extend(self.memory)
        
        # 加上当前用户输入
        messages.append(HumanMessage(content=user_input))

        try:
            # 2. 调用 LLM
            # print(messages)
            self.after_get_user_instruction(user_input)
            response_message = self.agent_executor.invoke({"messages":messages})
            ai_content = response_message['messages'][-1].content

            # 3. 更新记忆 (只有成功回复后才更新)
            # self.memory.append(HumanMessage(content=user_input))
            # self.memory.append(AIMessage(content=ai_content))
            self.after_response(user_input, ai_content)

            return ai_content

        except Exception as e:
            return f"Error invoking model: {e}"

    # def chat_with_messages(self, messages: List[BaseMessage]) -> str:
    #     """
    #     进行多轮对话，直接传入消息列表
    #     """
    #     try:
    #         # 2. 调用 LLM
            
    #         self.after_get_user_instruction_messages(messages)
            
    #         response_message = self.agent_executor.invoke({"messages": messages})
    #         ai_content = response_message['messages'][-1].content
    #         self.after_response_messages(messages)

    #         return ai_content

    #     except Exception as e:
    #         return f"Error invoking model: {e}"
    

    def chat_with_messages(self, messages: List[dict]) -> str:
        """
        接收 OpenAI 风格的消息列表，例如：
        [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        try:
            # self.system_prompt = "You are helpful AI assistant."
            # 转换为 LangChain BaseMessage 列表
            
            # 分析反馈（注意：parseUserFeedbackType 需要 BaseMessage 列表）
            if len(messages) >= 2:
                user_type = self.after_get_user_instruction_messages(messages)
                print(f"[DEBUG] Parsed user feedback type: {user_type}")
            else:
                user_type = "NEU"
            # 调用 agent
            if len(messages)==1:
                self.system_prompt = "You are helpful AI assistant."
            if messages[0]["role"] != "system":
                messages = [{"role": "system", "content": self.system_prompt}] + messages
            lc_messages = convert_to_messages(messages)
            response_message = self.agent_executor.invoke({"messages": lc_messages})
            ########################################
            # Rewrite
            
            
            # Initialize RefinementAgent (only once, can be cached)
            if not hasattr(self, '_refinement_agent'):
                self._refinement_agent = RefinementAgent(model = refinementAgentModel,tokenizer=refinementAgentTokenizer, reward_matrix=self.feedbackMatrixManager.get_reward_matrix())
            
            # Get initial response from agent
            initial_response = response_message['messages'][-1].content
            
            # Use rewriter to refine the response
            refine_result = self._refinement_agent.generate_and_refine(
                history=messages,
                initial_response=initial_response,
                custom_prompt=self.system_prompt,
                verbose=False,  # Set to True to see detailed logs
                user_type = user_type if len(messages) >= 2 else "NEU"
            )
            
            # Get the final refined response
            ai_content = refine_result['final_response']
            
            # Update system_prompt with the optimized version
            optimized_prompt = refine_result['final_prompt']
            if optimized_prompt and optimized_prompt != self.system_prompt:
                print(f"[Rewriter] New prompt: {optimized_prompt[:80]}...")
                self.system_prompt = optimized_prompt  # Update to use optimized prompt
                # Also update dialogTraj to use the new prompt
                # self.dialogTraj.system_prompt = optimized_prompt
            # 输出ai_content
            ########################################
            new_messages = messages + [{"role": "assistant", "content": ai_content}]

            llm_type = self.after_response_messages(new_messages)
            self.last_llm_type = llm_type
            print(f"[DEBUG] Parsed LLM response type: {llm_type}")

            return ai_content

        except Exception as e:
            return f"Error invoking model: {e}"
    
    def chat_with_messages_info_only(self, messages: List[dict]) -> str:
        """
        仅使用信息奖励的回复逻辑，不分析 feedback signal 类型。
        """
        try:
            if len(messages) == 1:
                self.system_prompt = "You are helpful AI assistant."
            if messages[0]["role"] != "system":
                messages = [{"role": "system", "content": self.system_prompt}] + messages
            lc_messages = convert_to_messages(messages)
            response_message = self.agent_executor.invoke({"messages": lc_messages})

            # 创建 info-only 的 RefinementAgent
            if not hasattr(self, '_refinement_agent_info_only'):
                self._refinement_agent_info_only = RefinementAgent(
                    model=refinementAgentModel,
                    tokenizer=refinementAgentTokenizer,
                    reward_matrix=self.feedbackMatrixManager.get_reward_matrix(),
                    info_only=True  # ← 新增参数
                )

            initial_response = response_message['messages'][-1].content

            refine_result = self._refinement_agent_info_only.generate_and_refine(
                history=messages,
                initial_response=initial_response,
                custom_prompt=self.system_prompt,
                verbose=False,
                user_type="NEU"
            )

            ai_content = refine_result['final_response']
            optimized_prompt = refine_result['final_prompt']
            if optimized_prompt and optimized_prompt != self.system_prompt:
                self.system_prompt = optimized_prompt

            return ai_content
        except Exception as e:
            return f"Error invoking model: {e}"
    
    def get_history(self):
        return self.memory

# ================= 使用示例 =================

INFO_ONLY_MODE = True

def main():
    tools = []
    local_url = agentcfg.LLM_LOCAL_URL
    model_name = agentcfg.LLM_MODEL_NAME
        
    agent = LangChainAgent(
        model_name="qwen2.5-7b", # 这里填你本地服务的模型名
        local_api_base="http://localhost:8001/v1",
        tools= tools,
        api_key="EMPTY", # 本地可以随意,
        alpha = 0.001
    )

    # # --- 场景 B: 官方 API ---
    # api_key = os.getenv("OPENAI_API_KEY") # 或者直接填 "sk-..."
    # if not api_key:
    #     print("请设置 OPENAI_API_KEY")
    #     return
        
    # agent = LangChainAgent(
    #     model_name="gpt-3.5-turbo",
    #     local_api_base=None, # 设为 None 就是走官方
    #     api_key=api_key
    # )

    # --- 开始对话循环 (代码完全一样) ---
    print(f"\n=== {agent.llm.model_name} Agent Start ===")
    messages = []
    while True:
        user_text = input("\nUser: ")
        if user_text.lower() in ["quit", "exit"]:
            break
        messages.append({"role":"user", "content": user_text})
        response = agent.chat_with_messages_info_only(messages) if INFO_ONLY_MODE else agent.chat_with_messages(messages)
        messages.append({"role":"assistant", "content": response})
        print(f"AI: {response}")
    print(agent.feedbackMatrixManager.total_df)

if __name__ == "__main__":
    main()