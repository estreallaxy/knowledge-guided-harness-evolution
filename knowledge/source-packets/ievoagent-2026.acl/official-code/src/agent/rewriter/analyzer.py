from src.agent.utils import funcs, reward
from configs import agent_config as agentcfg
from src.agent.rewriter import prompts as rewriter_prompts


class Analyzer:
    """Analyzer - Evaluates response quality and provides improvement suggestions"""
    
    def __init__(self, model=None, tokenizer=None, device="cuda"):
        """
        Initialize analyzer
        
        Args:
            model: Model for computing mutual information (optional)
            tokenizer: Corresponding tokenizer (optional)
            device: Computing device
        """
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
        # Error type to description mapping (consistent with utils/prompts.py)
        self.error_descriptions = {
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
        
        # Feedback type to description mapping (consistent with utils/prompts.py)
        self.feedback_descriptions = {
            "NEG_1": "Rephrasing - User repeats or rephrases concern, implying previous answer was unsatisfactory",
            "NEG_2": "Make Aware with Correction - User explicitly points out mistake and provides correction",
            "NEG_3": "Make Aware without Correction - User points out mistake but provides no additional information",
            "NEG_4": "Ask for Clarification - User asks for more details because response was unclear or ambiguous",
            "NEG_5": "Ignore and Continue - User ignores error and moves on to new topic",
            "POS": "Positive Feedback - User expresses gratitude, confirmation, or satisfaction",
            "NEU": "No Feedback/Neutral - User continues conversation normally without explicit sentiment",
            "STOP": "Conversation ends immediately after the Assistant's response"
        }
    
    def analyze(self, user_input: str, response: str, history: list = None, 
                next_user_input: str = None) -> dict:
        """
        Analyze response quality
        
        Args:
            user_input: Current user input
            response: AI's response
            history: Conversation history
            next_user_input: Next user input (for determining user feedback type)
            
        Returns:
            dict: Contains error type, feedback type, reward scores, and textual suggestions
        """
        if history is None:
            history = []
        
        # 1. Identify LLM response type (error type)
        error_type = funcs.parseLLMResponseType(
            history=history,
            user_input=user_input,
            llm_response=response
        )
        
        # 2. Identify user feedback type (if next input exists)
        ufb_type = "NEU"  # Default neutral
        if next_user_input:
            ufb_type = funcs.parseUserFeedbackType(
                history=history + [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response}
                ],
                llm_response=response,
                user_input=next_user_input
            )
        
        # 3. Calculate reward
        r_ufb, r_info = reward.compute_reward(
            input_text=user_input,
            response_text=response,
            ufb_type=ufb_type,
            error_type=error_type,
            device=self.device,
            model=self.model,
            tokenizer=self.tokenizer,
            history=history
        )
        
        # 4. Generate textual analysis report
        analysis_report = self._generate_analysis_report(
            error_type=error_type,
            ufb_type=ufb_type,
            r_ufb=r_ufb,
            r_info=r_info,
            user_input=user_input,
            response=response
        )
        
        # 5. Generate specific improvement suggestions
        suggestions = self._generate_suggestions(
            error_type=error_type,
            ufb_type=ufb_type,
            user_input=user_input,
            response=response,
            history=history
        )
        
        return {
            "error_type": error_type,
            "feedback_type": ufb_type,
            "reward_feedback": r_ufb,
            "reward_info": r_info,
            "analysis_report": analysis_report,
            "suggestions": suggestions,
            "overall_score": self._compute_overall_score(r_ufb, r_info)
        }
    
    def _generate_analysis_report(self, error_type: str, ufb_type: str, 
                                  r_ufb: float, r_info, 
                                  user_input: str, response: str) -> str:
        """Generate textual analysis report using LLM"""
        
        error_desc = self.error_descriptions.get(error_type, "Unknown error type")
        feedback_desc = self.feedback_descriptions.get(ufb_type, "Unknown feedback type")
        
        # Format reward info
        if isinstance(r_info, dict):
            info_details = f"""
            - Mutual Information Reward: {r_info.get('r_info', 0):.3f}
            - Semantic Similarity: {r_info.get('r_score', 0):.3f}
            - MI Score: {r_info.get('mi_score', 0):.3f}
            - Relevance Score: {r_info.get('relevance_score', 0):.3f}
            - Information Content Score: {r_info.get('info_content_score', 0):.3f}"""
        else:
            info_details = f"- Semantic Similarity: {r_info:.3f}"
        
        # Build prompt using template
        analysis_prompt = rewriter_prompts.analyzer_report_instruction.format(
            user_input=user_input,
            response=response,
            error_type=error_type,
            error_desc=error_desc,
            ufb_type=ufb_type,
            feedback_desc=feedback_desc,
            r_ufb=r_ufb,
            info_details=info_details
        )
        
        try:
            report = funcs.chatWithString(
                analysis_prompt, 
                rewriter_prompts.analyzer_report_system_prompt
            )
            return report
        except Exception as e:
            # Fallback to simple structured report
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} LLM analysis report generation failed: {e}")
            return self._generate_simple_report(error_type, ufb_type, r_ufb, r_info, error_desc, feedback_desc)
    
    def _generate_suggestions(self, error_type: str, ufb_type: str,
                             user_input: str, response: str, 
                             history: list) -> str:
        
        error_desc = self.error_descriptions.get(error_type, "Unknown error type")
        feedback_desc = self.feedback_descriptions.get(ufb_type, "Unknown feedback type")
        
        # Format conversation context
        context_str = ""
        if history:
            context_str = "\n**Recent Conversation History:**\n"
            for turn in history[-4:]:  # Last 2 turns
                role = turn.get("role", "unknown")
                content = turn.get("content", "")[:100]
                context_str += f"- {role.capitalize()}: {content}...\n"
        
        # Build prompt using template
        suggestions_prompt = rewriter_prompts.analyzer_suggestions_instruction.format(
            user_input=user_input,
            response=response,
            error_type=error_type,
            error_desc=error_desc,
            ufb_type=ufb_type,
            feedback_desc=feedback_desc,
            context_str=context_str
        )
        
        try:
            suggestions = funcs.chatWithString(
                suggestions_prompt,
                rewriter_prompts.analyzer_suggestions_system_prompt
            )
            return suggestions
        except Exception as e:
            # Fallback to rule-based suggestions
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} LLM suggestions generation failed: {e}")
            return self._generate_simple_suggestions(error_type, ufb_type)
    
    def _generate_simple_report(self, error_type: str, ufb_type: str, 
                               r_ufb: float, r_info, 
                               error_desc: str, feedback_desc: str) -> str:
        """Fallback: Generate simple structured report without LLM"""
        report = []
        report.append(f"## Response Quality Analysis")
        report.append(f"**Error Type**: {error_type} - {error_desc}")
        report.append(f"**User Feedback**: {ufb_type} - {feedback_desc}")
        report.append(f"\n**Feedback Reward**: {r_ufb:.3f}")
        
        if isinstance(r_info, dict):
            report.append(f"**Semantic Similarity**: {r_info.get('r_score', 0):.3f}")
        else:
            report.append(f"**Semantic Similarity**: {r_info:.3f}")
        
        return "\n".join(report)
    
    def _generate_simple_suggestions(self, error_type: str, ufb_type: str) -> str:
        """Fallback: Generate simple rule-based suggestions"""
        suggestions = []
        
        if error_type == "E1":
            suggestions.append("- Directly answer the specific question asked")
        elif error_type == "E2":
            suggestions.append("- Complete the requested action")
        elif error_type == "E3":
            suggestions.append("- Follow user preferences and expectations")
        elif error_type == "E4":
            suggestions.append("- Verify entities and slot values (time, location, quantity)")
        elif error_type == "E5":
            suggestions.append("- Ensure factual accuracy, avoid hallucination")
        elif error_type == "E6":
            suggestions.append("- Maintain topic coherence")
        elif error_type == "E7":
            suggestions.append("- Maintain context, avoid contradictions")
        elif error_type == "E8":
            suggestions.append("- Provide clear, specific answers")
        elif error_type == "E9":
            suggestions.append("- Use polite, respectful language")
        elif error_type == "E10":
            suggestions.append("- Provide information consistent with common sense")
        elif error_type == "E11":
            suggestions.append("- Check grammar and readability")
        else:
            suggestions.append("- Maintain current quality level")
        
        if ufb_type.startswith("NEG"):
            suggestions.append("- Address user's dissatisfaction")
        
        return "\n".join(suggestions)
    
    def _compute_overall_score(self, r_ufb: float, r_info) -> float:
        """
        Calculate overall score
        
        Args:
            r_ufb: Feedback reward (-1 to 1)
            r_info: Mutual information reward (0 to 1) or dict
            
        Returns:
            float: Overall score
        """
        # Weight configuration
        w_feedback = 0.6
        w_info = 0.4
        
        # Extract mutual information score
        if isinstance(r_info, dict):
            info_score = r_info.get('r_score', 0)  # Use semantic similarity
        else:
            info_score = r_info
        
        # Normalize feedback reward to [0, 1]
        normalized_ufb = (r_ufb + 1) / 2
        
        # Weighted sum
        overall = w_feedback * normalized_ufb + w_info * info_score
        
        return overall


if __name__ == "__main__":
    # Test code
    analyzer = Analyzer()
    
    # Test analysis
    user_input = "What is the capital of France?"
    response = "The capital of France is Paris."
    
    result = analyzer.analyze(
        user_input=user_input,
        response=response,
        history=[]
    )
    
    print("Analysis Result:")
    print(f"Error Type: {result['error_type']}")
    print(f"Feedback Type: {result['feedback_type']}")
    print(f"Overall Score: {result['overall_score']:.3f}")
    print(f"\nAnalysis Report:\n{result['analysis_report']}")
    print(f"\nSuggestions:\n{result['suggestions']}")

