from configs import agent_config as agentcfg
from src.agent.utils import funcs
from src.agent.rewriter import prompts as rewriter_prompts
import json
import re
def parse_ai_review(response_text: str) -> dict:
    try:
        # 1. 使用正则寻找第一个 { 开始，直到最后一个 } 结束的内容
        # re.DOTALL 让 . 可以匹配换行符，适应多行 JSON
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if not match:
            raise ValueError("No JSON object found in response.")
        json_str = match.group()
        # 2. 解析 JSON
        parsed_data = json.loads(json_str)
        # 3. 验证关键字段是否存在 (可选，视业务需求而定)
        required_keys = ["check", "suggestion"]
        if not all(key in parsed_data for key in required_keys):
            # 兼容性处理：如果模型漏了字段，赋予默认值
            parsed_data.setdefault("check", "Error: Missing 'check' field")
            parsed_data.setdefault("suggestion", "Error: Missing 'suggestion' field")
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"[Parse Error] JSON Decode failed: {e}")
        # 返回默认的空结构或抛出异常，取决于你的 Pipeline 设计
        return {
            "check": "Error: Invalid JSON format", 
            "suggestion": "Please ensure the output is valid JSON."
        }
    except Exception as e:
        print(f"[Parse Error] Unexpected error: {e}")
        return {
            "check": "Error: Parsing failed", 
            "suggestion": str(e)
        }
class PromptRewriter:
    """Prompt Rewriter - Rewrites system prompts based on analysis results"""
    
    def __init__(self):
        """Initialize Prompt Rewriter"""
        pass
    
    def rewrite_prompt(self, 
                      user_input: str,
                      current_response: str,
                      current_prompt: str,
                      error_type: str,
                      feedback_type: str,
                      reward_feedback: float,
                      reward_info: float,
                      history: list = None,
                      prompt_history: list = None) -> str:
        """
        Rewrite system prompt
        
        Args:
            user_input: User input
            current_response: Current generated response
            current_prompt: Current system prompt
            error_type: Error type (E1-E11, NE)
            feedback_type: Feedback type (NEG_1-5, POS, NEU, STOP)
            reward_feedback: Feedback reward score
            reward_info: Information reward score
            history: Conversation history
            prompt_history: Prompt iteration history
            
        Returns:
            str: Rewritten system prompt
        """
        if history is None:
            history = []
        if prompt_history is None:
            prompt_history = []
        
        # Build rewrite instruction
        rewrite_instruction = self._build_rewrite_instruction(
            user_input=user_input,
            current_response=current_response,
            current_prompt=current_prompt,
            error_type=error_type,
            feedback_type=feedback_type,
            reward_feedback=reward_feedback,
            reward_info=reward_info,
            history=history,
            prompt_history=prompt_history
        )

        # parse_check = funcs.chatWithString(
        #     prompt=self._bulid_self_check_instruction(
        #         user_input=user_input,
        #         current_response=current_response,
        #         history=history
        #     ),
        #     system_prompt=rewriter_prompts.prompt_self_check_instruction_sys
        # )
        # print(parse_check)
        # parsed_check = parse_ai_review(parse_check)
        # Call LLM to rewrite prompt
        new_prompt = funcs.chatWithString(
            prompt=rewrite_instruction,
            system_prompt=rewriter_prompts.prompt_rewriter_system_prompt
        )
        # system_with_check = new_prompt + "\n\nExtra Suggestions: \n" + parsed_check.get("suggestion","")
        # print("[DEBUG] Prompt Rewriter - Parsed Self-Check:", system_with_check)
        # return system_with_check.strip()
        return new_prompt.strip()
    def _bulid_self_check_instruction(self,user_input: str,current_response: str, history: list):
        """Build concise and clear self-check instruction"""
        history_str = ""
        if history:
            history_str = "**Recent History:**\n"
            for turn in history[-8:]:  # Last 3 turns
                role = turn.get("role", "unknown")
                content = turn.get("content", "")[:500]
                history_str += f"- {role.capitalize()}: {content}...\n"
            history_str += "\n"
        
        return rewriter_prompts.prompt_self_check_instruction_ins.format(
            history_str=history_str,
            user_input=user_input,
            current_response=current_response
        )
    def _build_rewrite_instruction(self,
                                   user_input: str,
                                   current_response: str,
                                   current_prompt: str,
                                   error_type: str,
                                   feedback_type: str,
                                   reward_feedback: float,
                                   reward_info: float,
                                   history: list,
                                   prompt_history: list) -> str:
        """Build concise and clear rewrite instruction"""
        
        error_desc = self._get_error_description(error_type)
        feedback_desc = self._get_feedback_description(feedback_type)
        
        # Format conversation history
        history_str = ""
        if history:
            history_str = "**Recent History:**\n"
            for turn in history[-8:]:  # Last 3 turns
                role = turn.get("role", "unknown")
                # content = turn.get("content", "")[:150]
                content = turn.get("content", "")[:500]
                history_str += f"- {role.capitalize()}: {content}...\n"
            history_str += "\n"
        
        # Format quality score
        quality_score = self._format_score(reward_feedback, reward_info)
        
        # Format key issues
        key_issues = self._summarize_key_issues(error_type, feedback_type, reward_feedback)
        
        # Format prompt history
        prompt_history_str = ""
        if prompt_history:
            prompt_history_str = "\n# Previous Attempts (Avoid Repeating)\n"
            for i, prev in enumerate(prompt_history[-3:]):
                version = prev.get("version", i+1)
                prompt = prev.get("prompt", "")
                score = prev.get("score", 0)
                error = prev.get("error_type", "Unknown")
                prompt_history_str += f"\n**Version {version}** (Score: {score:.2f}, Error: {error})\n"
                if len(prompt) > 200:
                    prompt_history_str += f"```\n{prompt[:200]}...\n```"
                else:
                    prompt_history_str += f"```\n{prompt}\n```"
        
        # Build instruction using template
        return rewriter_prompts.prompt_rewriter_instruction.format(
            current_prompt=current_prompt,
            history_str=history_str,
            user_input=user_input,
            current_response=current_response,
            error_type=error_type,
            error_desc=error_desc,
            feedback_type=feedback_type,
            feedback_desc=feedback_desc,
            quality_score=quality_score,
            key_issues=key_issues,
            prompt_history_str=prompt_history_str
        )
    
    def _get_error_description(self, error_type: str) -> str:
        error_descriptions = {
            "E1": "Ignore Question - Failed to answer the specific question or request asked",
            "E2": "Ignore Request - Ignored a requested action or constraint",
            "E3": "Ignore Expectation - Violated user preferences or expectations",
            "E4": "Attribute Error - Misunderstood entities or slot values (time, location, quantity)",
            "E5": "Factually Incorrect - Provided false, hallucinated, or inaccurate information",
            "E6": "Topic Deviation - Unnecessary topic shift or introduced irrelevant context",
            "E7": "Conversationality - Lost context, repetition, or self-contradiction",
            "E8": "Ambiguity - Vague, unclear response requiring user guessing",
            "E9": "Lack of Sociality - Rude, toxic, discriminatory, or lacking basic etiquette",
            "E10": "Lack of Common Sense - Information opposes the opinion of the majority",
            "E11": "Uninterpretable - Grammatically broken, garbled text, or nonsensical",
            "NE": "No Error - The response is correct, helpful, and contextually appropriate"
        }
        return error_descriptions.get(error_type, "Unknown error type")
    
    def _get_feedback_description(self, feedback_type: str) -> str:
        """Get feedback type description"""
        feedback_descriptions = {
            "NEG_1": "Rephrasing - User repeats or rephrases concern, implying previous answer was unsatisfactory",
            "NEG_2": "Make Aware with Correction - User explicitly points out mistake and provides correction",
            "NEG_3": "Make Aware without Correction - User points out mistake but provides no additional information",
            "NEG_4": "Ask for Clarification - User asks for more details because response was unclear or ambiguous",
            "NEG_5": "Ignore and Continue - User ignores error and moves on to new topic",
            "POS": "Positive Feedback - User expresses gratitude, confirmation, or satisfaction",
            "NEU": "No Feedback/Neutral - User continues conversation normally without explicit sentiment",
            "STOP": "Conversation ends immediately after the Assistant's response"
        }
        return feedback_descriptions.get(feedback_type, "Unknown feedback type")
    
    def _summarize_key_issues(self, error_type: str, feedback_type: str, reward_feedback: float) -> str:
        """Summarize key issues, let LLM determine how to improve"""
        issues = []
        
        # Error severity
        if reward_feedback < -0.5:
            issues.append("- **Critical Issue**: The response has serious quality problems that must be addressed")
        elif reward_feedback < 0:
            issues.append("- **Moderate Issue**: The response has noticeable problems that need improvement")
        else:
            issues.append("- **Minor Issue**: The response is acceptable but can be enhanced")
        
        # Primary error
        if error_type != "NE":
            issues.append(f"- **Primary Error**: {error_type} - {self._get_error_description(error_type)}")
        
        # User feedback signal
        if feedback_type.startswith("NEG"):
            issues.append(f"- **User Dissatisfaction**: {self._get_feedback_description(feedback_type)}")
        
        return "\n".join(issues) if issues else "- The response quality is good, minor refinements may help"
    
    def _format_score(self, reward_feedback: float, reward_info) -> str:
        """Format score display"""
        if isinstance(reward_info, dict):
            info_score = reward_info.get('r_score', 0)
            return f"Feedback={reward_feedback:.2f}, Information={info_score:.2f}"
        else:
            return f"Feedback={reward_feedback:.2f}, Information={reward_info:.2f}"


# if __name__ == "__main__":
#     # Test code
#     rewriter = PromptRewriter()
    
#     current_prompt = "You are a helpful assistant."
#     user_input = "What is the capital of Australia?"
#     current_response = "The capital of Australia is Sydney."
    
#     new_prompt = rewriter.rewrite_prompt(
#         user_input=user_input,
#         current_response=current_response,
#         current_prompt=current_prompt,
#         error_type="E5",  # Factual error
#         feedback_type="NEG_2",
#         reward_feedback=-0.7,
#         reward_info=0.6,
#         history=[]
#     )
    
#     print("Original Prompt:", current_prompt)
#     print("\nRewritten Prompt:", new_prompt)

