# import numpy as np
# from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
# from configs import agent_config as agentcfg
# from src.agent.rewriter.generator import Generator
# from src.agent.rewriter.analyzer import Analyzer
# from src.agent.rewriter.prompt_rewriter import PromptRewriter
# from src.agent.utils import reward as reward_module

# # type_ufb_distribution = {'E1': {'NEG_1': 0.3370136134633937, 'NEG_2': 0.06635223496623432, 'NEG_3': 0.042341086933218995, 'NEG_4': 0.04094758280630292, 'NEG_5': 0.2991746167863651, 'NEU': 0.027870082538321364, 'POS': 0.0028942008789795263, 'STOP': 0.18340658162718404}, 'E10': {'NEG_1': 0.11240721102863202, 'NEG_2': 0.18663838812301167, 'NEG_3': 0.07741251325556733, 'NEG_4': 0.07953340402969247, 'NEG_5': 0.25556733828207845, 'NEU': 0.19830328738069988, 'POS': 0.018027571580063628, 'STOP': 0.07211028632025451}, 'E11': {'NEG_1': 0.15274949083503056, 'NEG_2': 0.04480651731160896, 'NEG_3': 0.04832438437326421, 'NEG_4': 0.06702462506943159, 'NEG_5': 0.34086280318459544, 'NEU': 0.08368820588779856, 'POS': 0.008331790409183484, 'STOP': 0.2542121829290872}, 'E2': {'NEG_1': 0.28337319514571707, 'NEG_2': 0.1266719815749845, 'NEG_3': 0.04260784834794933, 'NEG_4': 0.037824430861900966, 'NEG_5': 0.30658162813358136, 'NEU': 0.08220391531579413, 'POS': 0.008415271503233237, 'STOP': 0.1123217291168394}, 'E3': {'NEG_1': 0.3485918809456532, 'NEG_2': 0.22708863144014316, 'NEG_3': 0.04784779127813883, 'NEG_4': 0.06207026466986908, 'NEG_5': 0.1927098050296694, 'NEU': 0.06235283036639352, 'POS': 0.006310633889045869, 'STOP': 0.053028162381086937}, 'E4': {'NEG_1': 0.11879531511433351, 'NEG_2': 0.26380368098159507, 'NEG_3': 0.013943112102621304, 'NEG_4': 0.016174010039040714, 'NEG_5': 0.3067484662576687, 'NEU': 0.20580033463469047, 'POS': 0.011712214166201896, 'STOP': 0.0630228667038483}, 'E5': {'NEG_1': 0.0897084475454772, 'NEG_2': 0.16525458925159897, 'NEG_3': 0.04987955810283246, 'NEG_4': 0.05880887116870172, 'NEG_5': 0.3385663261068195, 'NEU': 0.21355594318464988, 'POS': 0.011421214386576959, 'STOP': 0.0728050502533433}, 'E6': {'NEG_1': 0.10714285714285714, 'NEG_2': 0.10576923076923077, 'NEG_3': 0.057692307692307696, 'NEG_4': 0.06318681318681318, 'NEG_5': 0.40934065934065933, 'NEU': 0.13598901098901098, 'POS': 0.019230769230769232, 'STOP': 0.10164835164835165}, 'E7': {'NEG_1': 0.1712373490042442, 'NEG_2': 0.15447818043312656, 'NEG_3': 0.06491457177059527, 'NEG_4': 0.04908042224398738, 'NEG_5': 0.31314615300903254, 'NEU': 0.1256937642833823, 'POS': 0.013820872782674937, 'STOP': 0.1076286864729568}, 'E8': {'NEG_1': 0.17861482381530985, 'NEG_2': 0.06520858647225597, 'NEG_3': 0.024301336573511544, 'NEG_4': 0.46496557310652087, 'NEG_5': 0.13082219522073715, 'NEU': 0.08140947752126367, 'POS': 0.0028351559335763467, 'STOP': 0.05184285135682463}, 'E9': {'NEG_1': 0.01990049751243781, 'NEG_2': 0.07462686567164178, 'NEG_3': 0.07960199004975124, 'NEG_4': 0.04228855721393035, 'NEG_5': 0.17164179104477612, 'NEU': 0.44029850746268656, 'POS': 0.07960199004975124, 'STOP': 0.09203980099502487}, 'NE': {'NEG_1': 0.04767492462155357, 'NEG_2': 0.009332939603991171, 'NEG_3': 0.0069550216033073264, 'NEG_4': 0.02704298902738491, 'NEG_5': 0.06844673774517422, 'NEU': 0.7398666500885891, 'POS': 0.03523359547418482, 'STOP': 0.06544714183581486}}

# # reward_matrix = {
# #     "POS": {"NE": 1.0, "E8": 0.5, "E7": 0.5, "E6": 0.5, "E4": 0.2, "E3": 0.2, "E1": 0.2, "E2": 0.2, "E11": 0.2, "E5": -0.2, "E9": -0.2, "E10": -0.2},
# #     "NEU": {"NE": 0.5, "E8": 0.2, "E7": 0.2, "E6": 0.2, "E4": -0.1, "E3": -0.1, "E1": -0.1, "E2": -0.1, "E11": -0.1, "E5": -0.3, "E9": -0.3, "E10": -0.3},
# #     "STOP": {"NE": 0.2, "E8": 0.1, "E7": 0.1, "E6": 0.1, "E4": -0.2, "E3": -0.2, "E1": -0.2, "E2": -0.2, "E11": -0.2, "E5": -0.4, "E9": -0.4, "E10": -0.4},
# #     "NEG_5": {"NE": 0.0, "E8": -0.1, "E7": -0.1, "E6": -0.1, "E4": -0.3, "E3": -0.3, "E1": -0.3, "E2": -0.3, "E11": -0.3, "E5": -0.4, "E9": -0.4, "E10": -0.4},
# #     "NEG_1": {"NE": -0.1, "E8": -0.3, "E7": -0.3, "E6": -0.3, "E4": -0.5, "E3": -0.5, "E1": -0.5, "E2": -0.5, "E11": -0.5, "E5": -0.6, "E9": -0.6, "E10": -0.6},
# #     "NEG_4": {"NE": -0.1, "E8": -0.4, "E7": -0.4, "E6": -0.4, "E4": -0.6, "E3": -0.6, "E1": -0.6, "E2": -0.6, "E11": -0.6, "E5": -0.7, "E9": -0.7, "E10": -0.7},
# #     "NEG_3": {"NE": -0.1, "E8": -0.6, "E7": -0.6, "E6": -0.6, "E4": -0.8, "E3": -0.8, "E1": -0.8, "E2": -0.8, "E11": -0.8, "E5": -0.8, "E9": -0.8, "E10": -0.8},
# #     "NEG_2": {"NE": -0.2, "E8": -0.7, "E7": -0.7, "E6": -0.7, "E4": -0.9, "E3": -0.9, "E1": -0.9, "E2": -0.9, "E11": -0.9, "E5": -0.9, "E9": -0.9, "E10": -0.9}
# # }


# reward_matrix = {'E1': -0.41530710687104727, 'E10': -0.5471898197242842, 'E11': -0.3553786335863729, 'E2': -0.43344848968021965, 'E3': -0.5275878308373363, 'E4': -0.4405465699944227, 'E5': -0.5145236315308581, 'E6': -0.16002747252747251, 'E7': -0.2065894003700076, 'E8': -0.28999594977723775, 'E9': -0.4258706467661692, 'NE': 0.40822246743961954}
# class RefinementAgent:
    
#     def __init__(self, 
#                  max_iterations: int = None,
#                  convergence_threshold: float = None,
#                  score_threshold: float = None,
#                  model=None,
#                  tokenizer=None,
#                  device="cuda",
#                  initial_system_prompt: str = None):
#         """
#         Initialize Refinement Agent (Aggressive Mode)
        
#         Args:
#             max_iterations: Maximum iterations (None uses aggressive mode default: 10)
#             convergence_threshold: Prompt convergence threshold (None uses aggressive mode default: 0.95)
#             score_threshold: Score threshold (None uses aggressive mode default: 0.85)
#             model: Model for computing mutual information
#             tokenizer: Corresponding tokenizer
#             device: Computing device
#             initial_system_prompt: Initial system prompt
#         """
#         self.max_iterations = max_iterations or agentcfg.REFINEMENT_MAX_ITERATIONS
#         self.convergence_threshold = convergence_threshold or agentcfg.REFINEMENT_CONVERGENCE_THRESHOLD
#         self.score_threshold = score_threshold or agentcfg.REFINEMENT_MIN_SCORE_THRESHOLD
        
#         self.model = model
#         self.tokenizer = tokenizer
#         self.device = device
        
#         # Initial system prompt
#         self.initial_system_prompt = initial_system_prompt or "You are a helpful assistant. Please provide accurate, relevant, and helpful responses to user queries."
        
#         # Initialize three core components
#         self.generator = Generator()
#         self.analyzer = Analyzer(model=model, tokenizer=tokenizer, device=device)
#         self.prompt_rewriter = PromptRewriter()
    
#     def generate_and_refine(self, history: list, initial_response: str,
#                            custom_prompt: str = None, verbose: bool = True, user_type = "NEU") -> dict:
#         """
#         Inference-time evolution: Improve response quality through iterative prompt refinement
        
#         Args:
#             history: Conversation history (last message MUST be current user input)
#             initial_response: Initial response from model (iteration 0, may have quality issues)
#             custom_prompt: Custom initial prompt (the prompt used for initial_response)
#             verbose: Whether to print detailed information
            
#         Returns:
#             dict: Contains final response, best prompt, iteration history, etc.
#         """
#         if not history:
#             raise ValueError("history cannot be empty. Last message should be user input.")
        
#         # Extract user input from history (last message must be user)
#         if history[-1].get("role") != "user":
#             raise ValueError("Last message in history must be from user.")
        
#         user_input = history[-1].get("content", "")
#         conversation_history = history[:-1]  # History before current question
        
#         # Use custom prompt or default prompt
#         current_prompt = custom_prompt or self.initial_system_prompt
        
#         if verbose:
#             print(f"{agentcfg.Colors.GREEN}[RefinementAgent]{agentcfg.Colors.RESET} Starting inference-time evolution...")
#             print(f"User input: {user_input}")
#             print(f"Initial prompt: {current_prompt[:100]}...")
#             print(f"Initial response (Iteration 0): {initial_response[:100]}...")
        
#         # Initialize history records
#         iteration_history = []
#         prompt_history = []
        
#         # Iteration 0: Evaluate initial response
#         current_response = initial_response
        
#         # Iterative refinement loop
#         for iteration in range(self.max_iterations):
#             if verbose:
#                 print(f"\n{agentcfg.Colors.YELLOW}[Iteration {iteration + 1}/{self.max_iterations}]{agentcfg.Colors.RESET}")
            
#             # Step 1: Evaluate current response (for iteration 1, this is initial_response)
#             if verbose:
#                 if iteration == 0:
#                     print(f"{agentcfg.Colors.GREEN}[Evaluate]{agentcfg.Colors.RESET} Evaluate initial response...")
#                 else:
#                     print(f"{agentcfg.Colors.GREEN}[Evaluate]{agentcfg.Colors.RESET} Evaluate response quality...")
            
#             # Use reward calculation from utils
#             error_type = self.analyzer.analyze(user_input, current_response, conversation_history)['error_type']

#             feedback_type = user_type  # Default neutral (if no next user input)
            
#             # Call utils.reward to calculate reward
#             r_ufb, r_info = reward_module.compute_reward(
#                 input_text=user_input,
#                 response_text=current_response,
#                 ufb_type=feedback_type,
#                 error_type=error_type,
#                 device=self.device,
#                 model=self.model,
#                 tokenizer=self.tokenizer,
#                 history=conversation_history
#             )
            
#             # Calculate overall score
#             overall_score = self._compute_overall_score(r_ufb, r_info, error_type)
            
#             if verbose:
#                 print(f"Error type: {error_type}")
#                 print(f"Feedback reward: {r_ufb:.3f}")
#                 if isinstance(r_info, dict):
#                     print(f"Information reward: {r_info.get('r_score', 0):.3f}")
#                 else:
#                     print(f"Information reward: {r_info:.3f}")
#                 print(f"Overall score: {overall_score:.3f}")
            
#             # Record current iteration
#             current_iteration = {
#                 "iteration": iteration + 1,
#                 "prompt": current_prompt,
#                 "response": current_response,
#                 "error_type": error_type,
#                 "feedback_type": feedback_type,
#                 "reward_feedback": r_ufb,
#                 "reward_info": r_info,
#                 "score": overall_score
#             }
#             iteration_history.append(current_iteration)
            
#             # Step 3: Determine whether to continue refinement
#             should_continue, reason = self._should_continue_refinement(
#                 iteration=iteration,
#                 current_score=overall_score,
#                 error_type=error_type,
#                 iteration_history=iteration_history
#             )
            
#             if not should_continue:
#                 if verbose:
#                     print(f"\n{agentcfg.Colors.GREEN}[Terminate]{agentcfg.Colors.RESET} {reason}")
#                 break
            
#             # Step 4: Refine - Rewrite Prompt
#             if verbose:
#                 print(f"{agentcfg.Colors.GREEN}[Refine]{agentcfg.Colors.RESET} Rewrite Prompt...")
            
#             previous_prompt = current_prompt
            
#             # Call PromptRewriter to rewrite Prompt
#             current_prompt = self.prompt_rewriter.rewrite_prompt(
#                 user_input=user_input,
#                 current_response=current_response,
#                 current_prompt=current_prompt,
#                 error_type=error_type,
#                 feedback_type=feedback_type,
#                 reward_feedback=r_ufb,
#                 reward_info=r_info,
#                 history=conversation_history,
#                 prompt_history=prompt_history
#             )
            
#             # Update Prompt history
#             prompt_history.append({
#                 "version": iteration + 1,
#                 "prompt": previous_prompt,
#                 "score": overall_score,
#                 "error_type": error_type
#             })
            
#             if verbose:
#                 # print(f"New Prompt: {current_prompt[:150]}...")
#                 print(f"New Prompt: {current_prompt}")
            
#             # Step 5: Generate new response with optimized prompt
#             if verbose:
#                 print(f"{agentcfg.Colors.GREEN}[Generate]{agentcfg.Colors.RESET} Generate new response with optimized Prompt...")
            
#             # Generate response with new prompt
#             current_response = self.generator.generate(user_input, conversation_history, system_prompt=current_prompt)
            
#             if verbose:
#                 print(f"New response: {current_response[:150]}...")
            
#             # Step 6: Check Prompt convergence
#             prompt_similarity = self._compute_convergence_metric(
#                 previous_prompt,
#                 current_prompt
#             )
            
#             if verbose:
#                 print(f"Prompt similarity: {prompt_similarity:.3f}")
            
#             if prompt_similarity > self.convergence_threshold:
#                 if verbose:
#                     print(f"\n{agentcfg.Colors.GREEN}[Converged]{agentcfg.Colors.RESET} Prompt converged (similarity > {self.convergence_threshold})")
#                 break
        
#         # Select best version
#         best_version = self._select_best_version(iteration_history)
        
#         if verbose:
#             print(f"\n{agentcfg.Colors.GREEN}[Complete]{agentcfg.Colors.RESET} Select best version: Iteration {best_version['iteration']}")
#             print(f"Best score: {best_version['score']:.3f}")
#             print(f"Best Prompt: {best_version['prompt'][:100]}...")
#             print(f"Final response: {best_version['response'][:200]}...")
        
#         return {
#             "final_response": best_version['response'],
#             "final_prompt": best_version['prompt'],
#             "best_iteration": best_version['iteration'],
#             "best_score": best_version['score'],
#             "total_iterations": len(iteration_history),
#             "iteration_history": iteration_history,
#             "improvement": iteration_history[-1]['score'] - iteration_history[0]['score'] if len(iteration_history) > 1 else 0
#         }
    
#     def _should_continue_refinement(self, iteration: int, current_score: float,
#                                    error_type: str, iteration_history: list) -> tuple:
#         """
#         Determine whether to continue refining Prompt
        
#         Returns:
#             tuple: (should_continue: bool, reason: str)
#         """
#         # 1. Reached maximum iterations
#         if iteration >= self.max_iterations - 1:
#             return False, f"Reached maximum iterations ({self.max_iterations})"
        
#         # 2. Score is high enough and no error - stop
#         if current_score >= self.score_threshold and error_type == "NE":
#             return False, f"Score meets threshold ({current_score:.3f}) and no error"
        
#         # 3. Score is too low, needs improvement
#         if current_score < self.score_threshold:
#             return True, f"Score is low ({current_score:.3f}), need to improve Prompt"
        
#         # 4. Error exists, needs correction
#         if error_type != "NE":
#             return True, f"Error exists ({error_type}), need to improve Prompt"
        
#         # 5. Score is declining (may have made it worse), but still have chances
#         if len(iteration_history) > 1:
#             prev_score = iteration_history[-2]['score']
#             if current_score < prev_score - agentcfg.REFINEMENT_SCORE_DROP_TOLERANCE:
#                 return True, f"Score declined, try to improve Prompt to recover"
        
#         # Default: stop
#         return False, "Quality is good enough"
    
#     def _compute_convergence_metric(self, text1: str, text2: str) -> float:
#         """
#         Calculate Prompt convergence metric Δ = (Sim_sem + BLEU) / 2
        
#         Inspired by DRAFT: Compare the degree of change before and after Prompt rewriting
#         If Prompt barely changes, iteration has converged
        
#         Args:
#             text1: Prompt version 1
#             text2: Prompt version 2
            
#         Returns:
#             float: Convergence metric (0-1), closer to 1 means more similar
#         """
#         # 1. Calculate semantic similarity
#         try:
#             from src.agent.utils.rewardMutualInfo import local_embedder, _calculate_cosine_similarity_local
            
#             if local_embedder is not None:
#                 sem_sim = _calculate_cosine_similarity_local(text1, text2, local_embedder)
#             else:
#                 # Fallback: use simple word overlap
#                 sem_sim = self._simple_word_overlap(text1, text2)
#         except Exception as e:
#             print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} Semantic similarity calculation failed: {e}")
#             sem_sim = self._simple_word_overlap(text1, text2)
        
#         # 2. Calculate BLEU score
#         try:
#             reference = [text1.lower().split()]
#             candidate = text2.lower().split()
#             smoothie = SmoothingFunction().method4
#             bleu_score = sentence_bleu(reference, candidate, smoothing_function=smoothie)
#         except Exception as e:
#             print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} BLEU calculation failed: {e}")
#             bleu_score = 0.0
        
#         # 3. Combine: Δ = (Sim_sem + BLEU) / 2
#         delta = (sem_sim + bleu_score) / 2
#         return delta
    
#     def _simple_word_overlap(self, text1: str, text2: str) -> float:
#         """Simple word overlap similarity (fallback solution)"""
#         words1 = set(text1.lower().split())
#         words2 = set(text2.lower().split())
        
#         if not words1 or not words2:
#             return 0.0
        
#         intersection = words1 & words2
#         union = words1 | words2
        
#         return len(intersection) / len(union) if union else 0.0
    
#     def _compute_overall_score(self, r_ufb: float, r_info, llm_type = "NE") -> float:
#         # Read weights from config file
#         w_feedback = agentcfg.REFINEMENT_WEIGHT_FEEDBACK
#         w_info = agentcfg.REFINEMENT_WEIGHT_INFO
#         ufb_score = reward_matrix[llm_type]
#         # Extract mutual information score
#         if isinstance(r_info, dict):
#             info_score = r_info.get('r_score', 0)  # Use semantic similarity
#         else:
#             info_score = r_info
        
#         # Normalize feedback reward to [0, 1]
#         normalized_ufb = (ufb_score + 1) / 2
        
#         # Weighted sum
#         overall = w_feedback * normalized_ufb + w_info * info_score
        
#         return overall
    
#     def _select_best_version(self, iteration_history: list) -> dict:
#         """
#         Select the best version from iteration history (highest score Prompt and corresponding response)
        
#         Strategy: Prioritize the version with the highest score
#         """
#         if not iteration_history:
#             return None
        
#         # Sort by score
#         sorted_versions = sorted(iteration_history, key=lambda x: x['score'], reverse=True)
        
#         return sorted_versions[0]
    
#     def generate_simple(self, user_input: str, history: list = None) -> str:
#         """
#         Simple generation (without refinement)
        
#         Args:
#             user_input: User input
#             history: Conversation history
            
#         Returns:
#             str: Generated response
#         """
#         return self.generator.generate(user_input, history)


# if __name__ == "__main__":
#     # Test code
#     print("Initialize Refinement Agent...")
#     agent = RefinementAgent()
    
#     # Test case 1: Simple question with initial response
#     print("=" * 80)
#     print("Test Case 1: Simple Question with Initial Response")
#     print("=" * 80)
    
#     # Simulate: Model generated an initial response
#     history1 = [
#         {"role": "user", "content": "What is the capital of Australia?"}
#     ]
#     initial_response1 = "Sydney is the capital of Australia."  # Wrong answer!
    
#     result = agent.generate_and_refine(
#         history=history1,
#         initial_response=initial_response1,
#         custom_prompt="You are a helpful assistant.",
#         verbose=True
#     )
    
#     print(f"\nFinal Results:")
#     print(f"- Initial Response: {initial_response1}")
#     print(f"- Final Response: {result['final_response']}")
#     print(f"- Best Score: {result['best_score']:.3f}")
#     print(f"- Total Iterations: {result['total_iterations']}")
#     print(f"- Improvement: {result['improvement']:.3f}")
    
#     # Test case 2: Question with conversation history
#     print("\n" + "=" * 80)
#     print("Test Case 2: With Conversation History")
#     print("=" * 80)
    
#     history2 = [
#         {"role": "user", "content": "Tell me about Australia"},
#         {"role": "assistant", "content": "Australia is a country and continent in the Southern Hemisphere."},
#         {"role": "user", "content": "What is its capital?"}
#     ]
#     initial_response2 = "The capital is Sydney."  # Wrong again!
    
#     result = agent.generate_and_refine(
#         history=history2,
#         initial_response=initial_response2,
#         verbose=True
#     )
    
#     print(f"\nFinal Results:")
#     print(f"- Initial Response: {initial_response2}")
#     print(f"- Final Response: {result['final_response']}")
#     print(f"- Best Score: {result['best_score']:.3f}")
#     print(f"- Total Iterations: {result['total_iterations']}")
#     print(f"- Improvement: {result['improvement']:.3f}")






import numpy as np
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from configs import agent_config as agentcfg
from src.agent.rewriter.generator import Generator
from src.agent.rewriter.analyzer import Analyzer
from src.agent.rewriter.prompt_rewriter import PromptRewriter
from src.agent.utils import reward as reward_module

# type_ufb_distribution = {'E1': {'NEG_1': 0.3370136134633937, 'NEG_2': 0.06635223496623432, 'NEG_3': 0.042341086933218995, 'NEG_4': 0.04094758280630292, 'NEG_5': 0.2991746167863651, 'NEU': 0.027870082538321364, 'POS': 0.0028942008789795263, 'STOP': 0.18340658162718404}, 'E10': {'NEG_1': 0.11240721102863202, 'NEG_2': 0.18663838812301167, 'NEG_3': 0.07741251325556733, 'NEG_4': 0.07953340402969247, 'NEG_5': 0.25556733828207845, 'NEU': 0.19830328738069988, 'POS': 0.018027571580063628, 'STOP': 0.07211028632025451}, 'E11': {'NEG_1': 0.15274949083503056, 'NEG_2': 0.04480651731160896, 'NEG_3': 0.04832438437326421, 'NEG_4': 0.06702462506943159, 'NEG_5': 0.34086280318459544, 'NEU': 0.08368820588779856, 'POS': 0.008331790409183484, 'STOP': 0.2542121829290872}, 'E2': {'NEG_1': 0.28337319514571707, 'NEG_2': 0.1266719815749845, 'NEG_3': 0.04260784834794933, 'NEG_4': 0.037824430861900966, 'NEG_5': 0.30658162813358136, 'NEU': 0.08220391531579413, 'POS': 0.008415271503233237, 'STOP': 0.1123217291168394}, 'E3': {'NEG_1': 0.3485918809456532, 'NEG_2': 0.22708863144014316, 'NEG_3': 0.04784779127813883, 'NEG_4': 0.06207026466986908, 'NEG_5': 0.1927098050296694, 'NEU': 0.06235283036639352, 'POS': 0.006310633889045869, 'STOP': 0.053028162381086937}, 'E4': {'NEG_1': 0.11879531511433351, 'NEG_2': 0.26380368098159507, 'NEG_3': 0.013943112102621304, 'NEG_4': 0.016174010039040714, 'NEG_5': 0.3067484662576687, 'NEU': 0.20580033463469047, 'POS': 0.011712214166201896, 'STOP': 0.0630228667038483}, 'E5': {'NEG_1': 0.0897084475454772, 'NEG_2': 0.16525458925159897, 'NEG_3': 0.04987955810283246, 'NEG_4': 0.05880887116870172, 'NEG_5': 0.3385663261068195, 'NEU': 0.21355594318464988, 'POS': 0.011421214386576959, 'STOP': 0.0728050502533433}, 'E6': {'NEG_1': 0.10714285714285714, 'NEG_2': 0.10576923076923077, 'NEG_3': 0.057692307692307696, 'NEG_4': 0.06318681318681318, 'NEG_5': 0.40934065934065933, 'NEU': 0.13598901098901098, 'POS': 0.019230769230769232, 'STOP': 0.10164835164835165}, 'E7': {'NEG_1': 0.1712373490042442, 'NEG_2': 0.15447818043312656, 'NEG_3': 0.06491457177059527, 'NEG_4': 0.04908042224398738, 'NEG_5': 0.31314615300903254, 'NEU': 0.1256937642833823, 'POS': 0.013820872782674937, 'STOP': 0.1076286864729568}, 'E8': {'NEG_1': 0.17861482381530985, 'NEG_2': 0.06520858647225597, 'NEG_3': 0.024301336573511544, 'NEG_4': 0.46496557310652087, 'NEG_5': 0.13082219522073715, 'NEU': 0.08140947752126367, 'POS': 0.0028351559335763467, 'STOP': 0.05184285135682463}, 'E9': {'NEG_1': 0.01990049751243781, 'NEG_2': 0.07462686567164178, 'NEG_3': 0.07960199004975124, 'NEG_4': 0.04228855721393035, 'NEG_5': 0.17164179104477612, 'NEU': 0.44029850746268656, 'POS': 0.07960199004975124, 'STOP': 0.09203980099502487}, 'NE': {'NEG_1': 0.04767492462155357, 'NEG_2': 0.009332939603991171, 'NEG_3': 0.0069550216033073264, 'NEG_4': 0.02704298902738491, 'NEG_5': 0.06844673774517422, 'NEU': 0.7398666500885891, 'POS': 0.03523359547418482, 'STOP': 0.06544714183581486}}

# reward_matrix = {
#     "POS": {"NE": 1.0, "E8": 0.5, "E7": 0.5, "E6": 0.5, "E4": 0.2, "E3": 0.2, "E1": 0.2, "E2": 0.2, "E11": 0.2, "E5": -0.2, "E9": -0.2, "E10": -0.2},
#     "NEU": {"NE": 0.5, "E8": 0.2, "E7": 0.2, "E6": 0.2, "E4": -0.1, "E3": -0.1, "E1": -0.1, "E2": -0.1, "E11": -0.1, "E5": -0.3, "E9": -0.3, "E10": -0.3},
#     "STOP": {"NE": 0.2, "E8": 0.1, "E7": 0.1, "E6": 0.1, "E4": -0.2, "E3": -0.2, "E1": -0.2, "E2": -0.2, "E11": -0.2, "E5": -0.4, "E9": -0.4, "E10": -0.4},
#     "NEG_5": {"NE": 0.0, "E8": -0.1, "E7": -0.1, "E6": -0.1, "E4": -0.3, "E3": -0.3, "E1": -0.3, "E2": -0.3, "E11": -0.3, "E5": -0.4, "E9": -0.4, "E10": -0.4},
#     "NEG_1": {"NE": -0.1, "E8": -0.3, "E7": -0.3, "E6": -0.3, "E4": -0.5, "E3": -0.5, "E1": -0.5, "E2": -0.5, "E11": -0.5, "E5": -0.6, "E9": -0.6, "E10": -0.6},
#     "NEG_4": {"NE": -0.1, "E8": -0.4, "E7": -0.4, "E6": -0.4, "E4": -0.6, "E3": -0.6, "E1": -0.6, "E2": -0.6, "E11": -0.6, "E5": -0.7, "E9": -0.7, "E10": -0.7},
#     "NEG_3": {"NE": -0.1, "E8": -0.6, "E7": -0.6, "E6": -0.6, "E4": -0.8, "E3": -0.8, "E1": -0.8, "E2": -0.8, "E11": -0.8, "E5": -0.8, "E9": -0.8, "E10": -0.8},
#     "NEG_2": {"NE": -0.2, "E8": -0.7, "E7": -0.7, "E6": -0.7, "E4": -0.9, "E3": -0.9, "E1": -0.9, "E2": -0.9, "E11": -0.9, "E5": -0.9, "E9": -0.9, "E10": -0.9}
# }


default_reward_matrix = {'E1': -0.41530710687104727, 'E10': -0.5471898197242842, 'E11': -0.3553786335863729, 'E2': -0.43344848968021965, 'E3': -0.5275878308373363, 'E4': -0.4405465699944227, 'E5': -0.5145236315308581, 'E6': -0.16002747252747251, 'E7': -0.2065894003700076, 'E8': -0.28999594977723775, 'E9': -0.4258706467661692, 'NE': 0.40822246743961954}
class RefinementAgent:
    
    def __init__(self, 
                 max_iterations: int = None,
                 convergence_threshold: float = None,
                 score_threshold: float = None,
                 model=None,
                 tokenizer=None,
                 device="cuda",
                 initial_system_prompt: str = None,
                 reward_matrix = default_reward_matrix):
        """
        Initialize Refinement Agent (Aggressive Mode)
        
        Args:
            max_iterations: Maximum iterations (None uses aggressive mode default: 10)
            convergence_threshold: Prompt convergence threshold (None uses aggressive mode default: 0.95)
            score_threshold: Score threshold (None uses aggressive mode default: 0.85)
            model: Model for computing mutual information
            tokenizer: Corresponding tokenizer
            device: Computing device
            initial_system_prompt: Initial system prompt
        """
        self.max_iterations = max_iterations or agentcfg.REFINEMENT_MAX_ITERATIONS
        self.convergence_threshold = convergence_threshold or agentcfg.REFINEMENT_CONVERGENCE_THRESHOLD
        self.score_threshold = score_threshold or agentcfg.REFINEMENT_MIN_SCORE_THRESHOLD
        
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        
        # Initial system prompt
        self.initial_system_prompt = initial_system_prompt or "You are a helpful assistant. Please provide accurate, relevant, and helpful responses to user queries."
        
        # Initialize three core components
        self.generator = Generator()
        self.analyzer = Analyzer(model=model, tokenizer=tokenizer, device=device)
        self.prompt_rewriter = PromptRewriter()
        self.reward_matrix = reward_matrix
    
    def generate_and_refine(self, history: list, initial_response: str,
                           custom_prompt: str = None, verbose: bool = True, user_type = "NEU") -> dict:
        """
        Inference-time evolution: Improve response quality through iterative prompt refinement
        
        Args:
            history: Conversation history (last message MUST be current user input)
            initial_response: Initial response from model (iteration 0, may have quality issues)
            custom_prompt: Custom initial prompt (the prompt used for initial_response)
            verbose: Whether to print detailed information
            
        Returns:
            dict: Contains final response, best prompt, iteration history, etc.
        """
        if not history:
            raise ValueError("history cannot be empty. Last message should be user input.")
        
        # Extract user input from history (last message must be user)
        if history[-1].get("role") != "user":
            raise ValueError("Last message in history must be from user.")
        
        user_input = history[-1].get("content", "")
        conversation_history = history[:-1]  # History before current question
        
        # Use custom prompt or default prompt
        current_prompt = custom_prompt or self.initial_system_prompt
        
        if verbose:
            print(f"{agentcfg.Colors.GREEN}[RefinementAgent]{agentcfg.Colors.RESET} Starting inference-time evolution...")
            print(f"User input: {user_input}")
            print(f"Initial prompt: {current_prompt[:100]}...")
            print(f"Initial response (Iteration 0): {initial_response[:100]}...")
        
        # Initialize history records
        iteration_history = []
        prompt_history = []
        
        # Iteration 0: Evaluate initial response
        current_response = initial_response
        
        # Iterative refinement loop
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n{agentcfg.Colors.YELLOW}[Iteration {iteration + 1}/{self.max_iterations}]{agentcfg.Colors.RESET}")
            
            # Step 1: Evaluate current response (for iteration 1, this is initial_response)
            if verbose:
                if iteration == 0:
                    print(f"{agentcfg.Colors.GREEN}[Evaluate]{agentcfg.Colors.RESET} Evaluate initial response...")
                else:
                    print(f"{agentcfg.Colors.GREEN}[Evaluate]{agentcfg.Colors.RESET} Evaluate response quality...")
            
            # Use reward calculation from utils
            error_type = self.analyzer.analyze(user_input, current_response, conversation_history)['error_type']

            feedback_type = user_type  # Default neutral (if no next user input)
            
            # Call utils.reward to calculate reward
            r_ufb, r_info = reward_module.compute_reward(
                input_text=user_input,
                response_text=current_response,
                ufb_type=feedback_type,
                error_type=error_type,
                device=self.device,
                model=self.model,
                tokenizer=self.tokenizer,
                history=conversation_history
            )
            
            # Calculate overall score
            overall_score = self._compute_overall_score(r_ufb, r_info, error_type)
            
            if verbose:
                print(f"Error type: {error_type}")
                print(f"Feedback reward: {r_ufb:.3f}")
                if isinstance(r_info, dict):
                    print(f"Information reward: {r_info.get('r_score', 0):.3f}")
                else:
                    print(f"Information reward: {r_info:.3f}")
                print(f"Overall score: {overall_score:.3f}")
            
            # Record current iteration
            current_iteration = {
                "iteration": iteration + 1,
                "prompt": current_prompt,
                "response": current_response,
                "error_type": error_type,
                "feedback_type": feedback_type,
                "reward_feedback": r_ufb,
                "reward_info": r_info,
                "score": overall_score
            }
            iteration_history.append(current_iteration)
            
            # Step 3: Determine whether to continue refinement
            should_continue, reason = self._should_continue_refinement(
                iteration=iteration,
                current_score=overall_score,
                error_type=error_type,
                iteration_history=iteration_history
            )
            
            if not should_continue:
                if verbose:
                    print(f"\n{agentcfg.Colors.GREEN}[Terminate]{agentcfg.Colors.RESET} {reason}")
                break
            
            # Step 4: Refine - Rewrite Prompt
            if verbose:
                print(f"{agentcfg.Colors.GREEN}[Refine]{agentcfg.Colors.RESET} Rewrite Prompt...")
            
            previous_prompt = current_prompt
            
            # Call PromptRewriter to rewrite Prompt
            current_prompt = self.prompt_rewriter.rewrite_prompt(
                user_input=user_input,
                current_response=current_response,
                current_prompt=current_prompt,
                error_type=error_type,
                feedback_type=feedback_type,
                reward_feedback=r_ufb,
                reward_info=r_info,
                history=conversation_history,
                prompt_history=prompt_history
            )
            
            # Update Prompt history
            prompt_history.append({
                "version": iteration + 1,
                "prompt": previous_prompt,
                "score": overall_score,
                "error_type": error_type
            })
            
            if verbose:
                # print(f"New Prompt: {current_prompt[:150]}...")
                print(f"New Prompt: {current_prompt}")
            
            # Step 5: Generate new response with optimized prompt
            if verbose:
                print(f"{agentcfg.Colors.GREEN}[Generate]{agentcfg.Colors.RESET} Generate new response with optimized Prompt...")
            
            # Generate response with new prompt
            current_response = self.generator.generate(user_input, conversation_history, system_prompt=current_prompt)
            
            if verbose:
                print(f"New response: {current_response[:150]}...")
            
            # Step 6: Check Prompt convergence
            prompt_similarity = self._compute_convergence_metric(
                previous_prompt,
                current_prompt
            )
            
            if verbose:
                print(f"Prompt similarity: {prompt_similarity:.3f}")
            
            if prompt_similarity > self.convergence_threshold:
                if verbose:
                    print(f"\n{agentcfg.Colors.GREEN}[Converged]{agentcfg.Colors.RESET} Prompt converged (similarity > {self.convergence_threshold})")
                break
        
        # Select best version
        best_version = self._select_best_version(iteration_history)
        
        if verbose:
            print(f"\n{agentcfg.Colors.GREEN}[Complete]{agentcfg.Colors.RESET} Select best version: Iteration {best_version['iteration']}")
            print(f"Best score: {best_version['score']:.3f}")
            print(f"Best Prompt: {best_version['prompt'][:100]}...")
            print(f"Final response: {best_version['response'][:200]}...")
        
        return {
            "final_response": best_version['response'],
            "final_prompt": best_version['prompt'],
            "best_iteration": best_version['iteration'],
            "best_score": best_version['score'],
            "total_iterations": len(iteration_history),
            "iteration_history": iteration_history,
            "improvement": iteration_history[-1]['score'] - iteration_history[0]['score'] if len(iteration_history) > 1 else 0
        }
    
    def _should_continue_refinement(self, iteration: int, current_score: float,
                                   error_type: str, iteration_history: list) -> tuple:
        """
        Determine whether to continue refining Prompt
        
        Returns:
            tuple: (should_continue: bool, reason: str)
        """
        # 1. Reached maximum iterations
        if iteration >= self.max_iterations - 1:
            return False, f"Reached maximum iterations ({self.max_iterations})"
        
        # 2. Score is high enough and no error - stop
        if current_score >= self.score_threshold and error_type == "NE":
            return False, f"Score meets threshold ({current_score:.3f}) and no error"
        
        # 3. Score is too low, needs improvement
        if current_score < self.score_threshold:
            return True, f"Score is low ({current_score:.3f}), need to improve Prompt"
        
        # 4. Error exists, needs correction
        if error_type != "NE":
            return True, f"Error exists ({error_type}), need to improve Prompt"
        
        # 5. Score is declining (may have made it worse), but still have chances
        if len(iteration_history) > 1:
            prev_score = iteration_history[-2]['score']
            if current_score < prev_score - agentcfg.REFINEMENT_SCORE_DROP_TOLERANCE:
                return True, f"Score declined, try to improve Prompt to recover"
        
        # Default: stop
        return False, "Quality is good enough"
    
    def _compute_convergence_metric(self, text1: str, text2: str) -> float:
        """
        Calculate Prompt convergence metric Δ = (Sim_sem + BLEU) / 2
        
        Inspired by DRAFT: Compare the degree of change before and after Prompt rewriting
        If Prompt barely changes, iteration has converged
        
        Args:
            text1: Prompt version 1
            text2: Prompt version 2
            
        Returns:
            float: Convergence metric (0-1), closer to 1 means more similar
        """
        # 1. Calculate semantic similarity
        try:
            from src.agent.utils.rewardMutualInfo import local_embedder, _calculate_cosine_similarity_local
            
            if local_embedder is not None:
                sem_sim = _calculate_cosine_similarity_local(text1, text2, local_embedder)
            else:
                # Fallback: use simple word overlap
                sem_sim = self._simple_word_overlap(text1, text2)
        except Exception as e:
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} Semantic similarity calculation failed: {e}")
            sem_sim = self._simple_word_overlap(text1, text2)
        
        # 2. Calculate BLEU score
        try:
            reference = [text1.lower().split()]
            candidate = text2.lower().split()
            smoothie = SmoothingFunction().method4
            bleu_score = sentence_bleu(reference, candidate, smoothing_function=smoothie)
        except Exception as e:
            print(f"{agentcfg.Colors.YELLOW}[WARN]{agentcfg.Colors.RESET} BLEU calculation failed: {e}")
            bleu_score = 0.0
        
        # 3. Combine: Δ = (Sim_sem + BLEU) / 2
        delta = (sem_sim + bleu_score) / 2
        return delta
    
    def _simple_word_overlap(self, text1: str, text2: str) -> float:
        """Simple word overlap similarity (fallback solution)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _compute_overall_score(self, r_ufb: float, r_info, llm_type = "NE") -> float:
        # Read weights from config file
        w_feedback = agentcfg.REFINEMENT_WEIGHT_FEEDBACK
        w_info = agentcfg.REFINEMENT_WEIGHT_INFO
        ufb_score = self.reward_matrix[llm_type]
        # Extract mutual information score
        if isinstance(r_info, dict):
            info_score = r_info.get('r_score', 0)  # Use semantic similarity
        else:
            info_score = r_info
        
        # Normalize feedback reward to [0, 1]
        normalized_ufb = (ufb_score + 1) / 2
        
        # Weighted sum
        overall = w_feedback * normalized_ufb + w_info * info_score
        
        return overall
    
    def _select_best_version(self, iteration_history: list) -> dict:
        """
        Select the best version from iteration history (highest score Prompt and corresponding response)
        
        Strategy: Prioritize the version with the highest score
        """
        if not iteration_history:
            return None
        
        # Sort by score
        sorted_versions = sorted(iteration_history, key=lambda x: x['score'], reverse=True)
        
        return sorted_versions[0]
    
    def generate_simple(self, user_input: str, history: list = None) -> str:
        """
        Simple generation (without refinement)
        
        Args:
            user_input: User input
            history: Conversation history
            
        Returns:
            str: Generated response
        """
        return self.generator.generate(user_input, history)


if __name__ == "__main__":
    # Test code
    print("Initialize Refinement Agent...")
    agent = RefinementAgent()
    
    # Test case 1: Simple question with initial response
    print("=" * 80)
    print("Test Case 1: Simple Question with Initial Response")
    print("=" * 80)
    
    # Simulate: Model generated an initial response
    history1 = [
        {"role": "user", "content": "What is the capital of Australia?"}
    ]
    initial_response1 = "Sydney is the capital of Australia."  # Wrong answer!
    
    result = agent.generate_and_refine(
        history=history1,
        initial_response=initial_response1,
        custom_prompt="You are a helpful assistant.",
        verbose=True
    )
    
    print(f"\nFinal Results:")
    print(f"- Initial Response: {initial_response1}")
    print(f"- Final Response: {result['final_response']}")
    print(f"- Best Score: {result['best_score']:.3f}")
    print(f"- Total Iterations: {result['total_iterations']}")
    print(f"- Improvement: {result['improvement']:.3f}")
    
    # Test case 2: Question with conversation history
    print("\n" + "=" * 80)
    print("Test Case 2: With Conversation History")
    print("=" * 80)
    
    history2 = [
        {"role": "user", "content": "Tell me about Australia"},
        {"role": "assistant", "content": "Australia is a country and continent in the Southern Hemisphere."},
        {"role": "user", "content": "What is its capital?"}
    ]
    initial_response2 = "The capital is Sydney."  # Wrong again!
    
    result = agent.generate_and_refine(
        history=history2,
        initial_response=initial_response2,
        verbose=True
    )
    
    print(f"\nFinal Results:")
    print(f"- Initial Response: {initial_response2}")
    print(f"- Final Response: {result['final_response']}")
    print(f"- Best Score: {result['best_score']:.3f}")
    print(f"- Total Iterations: {result['total_iterations']}")
    print(f"- Improvement: {result['improvement']:.3f}")

