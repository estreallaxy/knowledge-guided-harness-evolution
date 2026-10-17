"""Base class for collaborative math tasks.

This class contains generic logic for collaborative math tasks, including
decision modes, debate facilitation, and robust math answer evaluation.
"""

import os
import random
import re
from abc import abstractmethod
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from teamwork.agent import TeamAgent
from teamwork.conversation import Turn
from teamwork.tasks.task import Task, TaskResult

from sympy import simplify, parse_expr

import openai



class CollaborativeMathTask(Task):
    """Base class for collaborative math tasks.

    Agents independently solve a math problem, then collaborate to find the
    correct answer.

    Derived classes must implement:
    - get_task_description: Task-specific problem description
    - get_ground_truth: Method to return the canonical answer
    """

    def __init__(
        self,
        agent_ids: List[int],
        max_rounds: int,
        seed: int | None = None,
        decision_mode: str = "expert_not_mentioned",
        most_capable_model_name: Optional[str] = None,
        name: str | None = None,
        use_llm_fallback: bool = True,
        llm_fallback_model: str = "gpt-5",
        llm_fallback_api_key: Optional[str] = None,
    ):
        """Initialize collaborative math task.

        Args:
            agent_ids: List of unique agent IDs that will work on this task
            max_rounds: Maximum number of collaboration rounds (required)
            seed: Random seed for reproducibility (required)
            decision_mode: Decision strategy for team collaboration 
                           ("expert_not_mentioned", "explicit_expert_voting", "reveal_expert")
            most_capable_model_name: Model name to use as fallback expert in "reveal_expert" mode
            name: Optional human-readable name for the task
            use_llm_fallback: Whether to use LLM as final fallback for equivalence checking
            llm_fallback_model: Model name for LLM fallback (e.g., "gpt-4o", "gpt-5")
            llm_fallback_api_key: OpenAI API key for LLM fallback (defaults to OPENAI_API_KEY env var)
        """
        super().__init__(agent_ids, max_rounds, name)
        self.seed = seed
        self.decision_mode = decision_mode
        self.most_capable_model_name = most_capable_model_name
        self.use_llm_fallback = use_llm_fallback
        self.llm_fallback_model = llm_fallback_model
        self.llm_fallback_api_key = llm_fallback_api_key or os.getenv("OPENAI_API_KEY")
        
        # State tracking
        self.revealed_expert_agent_id: Optional[int] = None
        self.coordinator_agent_id: Optional[int] = None
        self.declared_best_agent_id: Optional[int] = None
        self.explicit_voting_votes: Dict[int, int | None] = {}
        
        # Problem context for LLM fallback (set during execution)
        self._current_problem_context: Optional[str] = None
        
        # Cache for LLM equivalence checks (key: (problem_hash, pred, gold))
        self._llm_equiv_cache: Dict[Tuple[str, str, str], bool] = {}

        # Validate decision modes
        valid_decision_modes = ["expert_not_mentioned", "explicit_expert_voting", "reveal_expert"]
        if self.decision_mode not in valid_decision_modes:
            raise ValueError(f"decision_mode must be one of {valid_decision_modes}, got '{self.decision_mode}'")

    @abstractmethod
    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (problem statement) for a specific agent."""
        ...

    @abstractmethod
    def get_ground_truth(self) -> str:
        """Return the ground truth answer string."""
        ...
    
    def get_hidden_info(self, agent_id: int) -> str:
        """Return empty string as math tasks typically don't have hidden info per agent."""
        return ""

    def _extract_answer(self, text: str) -> str:
        """Extract the answer from the text, prioritizing \\boxed{...}."""
        # Look for \boxed{...}
        boxed_matches = re.findall(r'\\boxed\{((?:[^{}]|{[^{}]*})*)\}', text)
        if boxed_matches:
            # Return the last boxed content
            return boxed_matches[-1]
        
        # Fallback: Look for the last number or expression
        text = text.strip()
        lines = text.split('\n')
        if not lines:
            return ""
            
        last_line = lines[-1].strip()
        
        # Look for common prefixes like "The answer is", "Answer:", "="
        # Regex to capture the part after the prefix
        # Matches: "The answer is 5", "Answer: 5", "x = 5", "is 5"
        match = re.search(r'(?:answer\s+is|answer:|result\s+is|=)\s*(.+)$', last_line, re.IGNORECASE)
        if match:
            last_line = match.group(1).strip()
            
        # Remove trailing period if present (e.g., "5.")
        if last_line.endswith('.'):
            last_line = last_line[:-1]
            
        return last_line

    def _is_equiv(
        self, 
        predicted: str, 
        gold: str, 
        problem_context: Optional[str] = None
    ) -> bool:
        """Check if predicted answer is equivalent to ground truth using SymPy.
        
        Args:
            predicted: The predicted answer string
            gold: The ground truth answer string
            problem_context: Optional problem statement for LLM fallback
        """
        
        # Preprocess: remove \boxed{} wrapper for both
        def preprocess_for_latex(s: str) -> str:
            """Preprocess string to remove \boxed{} wrapper."""
            s = str(s).strip()
            # Remove \boxed{...} wrapper if present
            match = re.search(r'\\boxed\{((?:[^{}]|{[^{}]*})*)\}', s)
            if match:
                s = match.group(1)
            return s
        
        # Manual normalization and parse_expr
        def normalize(s: str) -> str:
            s = str(s).strip()
            # Remove \boxed{...} wrapper if present
            match = re.search(r'\\?boxed\{((?:[^{}]|{[^{}]*})*)\}', s)
            if match:
                s = match.group(1)
            
            # Handle degrees: strip "degrees", "degree", "^\circ", "°", etc.
            # This handles cases like "72 degrees", "72^\circ", "72°", "72"
            # Do this BEFORE removing backslashes so we can match \circ
            s = re.sub(r'\s*degrees?\s*', ' ', s, flags=re.IGNORECASE)
            s = re.sub(r'\s*\^\{\s*\\?circ\s*\}\s*', ' ', s)  # LaTeX: ^{\circ} or ^{circ}
            s = re.sub(r'\s*\^\s*\\circ\s*', ' ', s)  # LaTeX: ^\circ (no braces, with backslash)
            s = re.sub(r'\s*\^\s*circ\s*', ' ', s)  # LaTeX: ^circ (no braces, no backslash)
            s = re.sub(r'\s*°\s*', ' ', s)  # Unicode degree symbol
            
            # Handle radians: strip "radians", "radian", "\text{radians}", etc.
            # This handles cases like "-\frac{\pi}{6} \text{radians}", "-\frac{\pi}{6} radians", "-\frac{\pi}{6}"
            # Do this BEFORE removing backslashes so we can match \text{radians}
            s = re.sub(r'\\text\s*\{\s*radians?\s*\}', ' ', s, flags=re.IGNORECASE)  # LaTeX: \text{radians} or \text{radian}
            s = re.sub(r'\s*radians?\s*', ' ', s, flags=re.IGNORECASE)  # Plain text: "radians" or "radian"
            
            # Strip all \text{...} commands (formatting-only, not semantically meaningful)
            # This handles cases like "55 \text{answer}" vs "55"
            s = re.sub(r'\\text\s*\{[^}]*\}', ' ', s)  # LaTeX: \text{anything}
            
            # Remove \left and \right (they're just LaTeX formatting, not semantic)
            s = s.replace(r'\left', '')
            s = s.replace(r'\right', '')
            s = s.replace('left', '')
            s = s.replace('right', '')
            
            # Common LaTeX standardizations
            s = s.replace(r'\dfrac', r'\frac')
            s = s.replace(r'\tfrac', r'\frac')
            s = s.replace(' ', '')
            
            # Convert \frac{a}{b} -> (a)/(b) BEFORE removing other backslashes
            # Handle nested fractions by repeatedly applying the conversion
            # Match either backslash or form feed (how \f is stored) followed by frac
            # Use a function to match balanced braces for nested fractions
            def replace_frac(match):
                num = match.group(1)
                den = match.group(2)
                return f'({num})/({den})'
            
            max_iterations = 10  # Prevent infinite loops
            for _ in range(max_iterations):
                # Match \frac{...}{...} with balanced braces
                # This regex matches from the innermost \frac first
                pattern = r'[\\\x0c]frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}'
                new_s = re.sub(pattern, replace_frac, s)
                if new_s == s:
                    break
                s = new_s
            
            # Convert common math symbols: \pi -> pi, etc.
            math_symbols = {
                r'\pi': 'pi',
                r'\alpha': 'alpha',
                r'\beta': 'beta',
                r'\gamma': 'gamma',
                r'\theta': 'theta',
                r'\lambda': 'lambda',
                r'\mu': 'mu',
                r'\sigma': 'sigma',
            }
            for latex_cmd, sympy_name in math_symbols.items():
                s = s.replace(latex_cmd, sympy_name)
            
            # Handle implicit multiplication: number followed by letter/symbol
            # e.g., "2pi" -> "2*pi", "3x" -> "3*x", but not "2.5pi" (already has decimal)
            s = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', s)
            
            # Now remove double backslashes (single backslashes for remaining commands)
            s = s.replace('\\\\', '')
            
            # Remove any remaining formatting commands
            known_formatting = ['boxed', 'left', 'right', 'dfrac', 'tfrac']
            for cmd in known_formatting:
                s = s.replace(f'\\{cmd}', '')
                s = s.replace(cmd, '')
            
            # Remove any remaining single backslashes (they're likely formatting commands)
            s = s.replace('\\', '')
            
            return s

        norm_pred = normalize(predicted)
        norm_gold = normalize(gold)

        # Exact match check
        if norm_pred == norm_gold:
            return True

        # Check if this looks like a tuple/coordinate pair
        # Tuples can't be parsed by parse_expr, so we need special handling
        is_tuple_pred = norm_pred.strip().startswith('(') and ',' in norm_pred
        is_tuple_gold = norm_gold.strip().startswith('(') and ',' in norm_gold
        
        if is_tuple_pred or is_tuple_gold:
            # For tuples, compare component-wise after normalization
            # Extract components from tuples like (a, b) or (a,b)
            def extract_tuple_components(s: str) -> list:
                s = s.strip()
                # Remove outer parentheses
                if s.startswith('(') and s.endswith(')'):
                    s = s[1:-1]
                # Split by comma and normalize each component
                components = [c.strip() for c in s.split(',')]
                return components
            
            try:
                comp_pred = extract_tuple_components(norm_pred)
                comp_gold = extract_tuple_components(norm_gold)
                
                if len(comp_pred) == len(comp_gold):
                    # Compare each component
                    all_match = True
                    for p, g in zip(comp_pred, comp_gold):
                        if not self._is_equiv(p, g):
                            all_match = False
                            break
                    if all_match:
                        return True
            except Exception:
                pass

        # Try SymPy parse_expr for algebraic expressions
        try:
            # Try converting to float if they are numbers
            try:
                float_pred = float(norm_pred)
                float_gold = float(norm_gold)
                if abs(float_pred - float_gold) < 1e-6:
                    return True
            except ValueError:
                pass

            # Clean up remaining latex tokens for parse_expr
            clean_pred = norm_pred.replace('^', '**')
            clean_gold = norm_gold.replace('^', '**')
            
            # Replace braces with parentheses
            clean_pred = clean_pred.replace('{', '(').replace('}', ')')
            clean_gold = clean_gold.replace('{', '(').replace('}', ')')
            
            # Handle implicit multiplication if not already handled in normalization
            # This is a fallback for cases that might have been missed
            clean_pred = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', clean_pred)
            clean_gold = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', clean_gold)
            
            # Remove any remaining LaTeX command backslashes and command names
            clean_pred = re.sub(r'\\[a-zA-Z]+\s*', '', clean_pred)
            clean_gold = re.sub(r'\\[a-zA-Z]+\s*', '', clean_gold)
            
            expr_pred = parse_expr(clean_pred)
            expr_gold = parse_expr(clean_gold)
            
            if simplify(expr_pred - expr_gold) == 0:
                return True
                
        except Exception:
            # Parsing failed
            pass

        # Final fallback: If both answers contain exactly one number, compare those numbers
        # This handles cases like "55 cm²" vs "55" or "72 degrees" vs "72"
        try:
            def extract_numbers(s: str) -> list:
                """Extract all numbers (integers and floats) from a string."""
                # Match integers and floats (including negative numbers)
                numbers = re.findall(r'-?\d+\.?\d*', s)
                return [float(n) for n in numbers]
            
            pred_numbers = extract_numbers(norm_pred)
            gold_numbers = extract_numbers(norm_gold)
            
            # If each has exactly one number, compare them
            if len(pred_numbers) == 1 and len(gold_numbers) == 1:
                if abs(pred_numbers[0] - gold_numbers[0]) < 1e-6:
                    return True
        except Exception:
            pass

        # Final fallback: Use LLM to check equivalence if enabled
        if self.use_llm_fallback and self.llm_fallback_api_key:
            try:
                return self._check_equiv_with_llm(predicted, gold, problem_context)
            except Exception:
                # If LLM check fails, log and return False
                # Don't print to avoid cluttering output - LLM failures are expected sometimes
                pass

        return False

    def _check_equiv_with_llm(
        self, 
        predicted: str, 
        gold: str, 
        problem_context: Optional[str] = None
    ) -> bool:
        """Check equivalence using LLM as final fallback.
        
        Args:
            predicted: The predicted answer string
            gold: The ground truth answer string
            problem_context: Optional problem statement for context
            
        Returns:
            True if LLM determines answers are equivalent, False otherwise
        """
        # Create cache key (use hash of problem context to keep key manageable)
        problem_hash = str(hash(problem_context)) if problem_context else "no_context"
        cache_key = (problem_hash, predicted, gold)
        
        # Check cache
        if cache_key in self._llm_equiv_cache:
            return self._llm_equiv_cache[cache_key]
        
        # Build prompt
        if problem_context:
            prompt = f"""Given the following math problem:

{problem_context}

Given the context of this problem, are these two answers mathematically equivalent? Do they represent the same mathematical value or expression, even if they use different notation or formatting?

Answer 1: {predicted}
Answer 2: {gold}

Consider them equal if they represent the same value/expression, regardless of notation differences (e.g., \\frac{{1}}{{2}} vs 1/2 vs 0.5, or \\left( 3, \\frac{{\\pi}}{{2}} \\right) vs (3, pi/2), or x \\in [-2,7] vs [-2, 7]).

First, explain your reasoning for why they are or are not equivalent. Then, on a new line, respond with only 'yes' or 'no'."""
        else:
            prompt = f"""Do these two mathematical answers represent the same value or expression, even if they use different notation or formatting?

Answer 1: {predicted}
Answer 2: {gold}

Consider them equal if they represent the same value/expression, regardless of notation differences (e.g., \\frac{{1}}{{2}} vs 1/2 vs 0.5, or \\left( 3, \\frac{{\\pi}}{{2}} \\right) vs (3, pi/2), or x \\in [-2,7] vs [-2, 7]).

First, explain your reasoning for why they are or are not equivalent. Then, on a new line, respond with only 'yes' or 'no'."""
        
        try:
            client = openai.OpenAI(api_key=self.llm_fallback_api_key)
            
            # Retry logic for empty/None responses
            max_retries = 3
            response_text = None
            response = None
            
            for attempt in range(max_retries):
                response = client.chat.completions.create(
                    model=self.llm_fallback_model,
                    messages=[
                        {"role": "system", "content": "You are a mathematical expert. Determine if two mathematical answers represent the same value or expression, even if they use different notation. Consider them equal if they are mathematically the same, regardless of formatting differences. First explain your reasoning, then provide 'yes' or 'no'."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=800  # Increased to allow for detailed reasoning
                )
                
                # Check if response is valid
                if response.choices and response.choices[0].message.content is not None:
                    response_text = response.choices[0].message.content.strip()
                    if response_text:
                        break
                
                # If we get here, response was empty/None, retry if we have attempts left
                if attempt < max_retries - 1:
                    continue
                else:
                    # Last attempt failed, use empty string
                    response_text = ""
            
            # Extract reasoning and yes/no answer
            # If response_text is empty after retries, default to 'no'
            if not response_text:
                reasoning = "(No reasoning available - empty response after retries)"
                answer = "no"
                is_equiv = False
            else:
                # Look for 'yes' or 'no' (case insensitive) - take the last occurrence
                reasoning = response_text
                answer = ""
                is_equiv = False
                
                # Try to find yes/no at the end
                response_lower = response_text.lower()
                if response_lower.endswith('yes') or response_lower.endswith('no'):
                    # Last word is yes/no
                    last_newline = response_text.rfind('\n')
                    if last_newline != -1:
                        reasoning = response_text[:last_newline].strip()
                        answer = response_text[last_newline:].strip().lower()
                    else:
                        # No newline, check if last word is yes/no
                        words = response_text.split()
                        if len(words) > 0:
                            last_word = words[-1].lower()
                            if last_word in ['yes', 'no']:
                                reasoning = ' '.join(words[:-1])
                                answer = last_word
                
                # If we didn't find yes/no cleanly, search for it anywhere
                if not answer:
                    if 'yes' in response_lower:
                        answer = 'yes'
                        # Try to extract reasoning before yes
                        yes_idx = response_lower.rfind('yes')
                        if yes_idx > 0:
                            reasoning = response_text[:yes_idx].strip()
                    elif 'no' in response_lower:
                        answer = 'no'
                        # Try to extract reasoning before no
                        no_idx = response_lower.rfind('no')
                        if no_idx > 0:
                            reasoning = response_text[:no_idx].strip()
                    else:
                        # Fallback: use entire response as reasoning, default to no
                        reasoning = response_text
                        answer = 'no'
                
                is_equiv = answer.startswith('yes')
                
                # Fallback: if reasoning ended up empty, use full response as reasoning
                if not reasoning:
                    reasoning = response_text
            
            # Debugging output
            problem_id = getattr(self, 'name', 'Unknown')
            print(f"\n{'='*80}")
            print("LLM Fallback Equivalence Check")
            print(f"{'='*80}")
            print(f"Problem ID: {problem_id}")
            print(f"Ground Truth: {gold}")
            print(f"Proposed Answer: {predicted}")
            if problem_context:
                print(f"Problem Statement:\n{problem_context}")
            else:
                print("Problem Statement: (not provided)")
            print(f"\nLLM Reasoning:\n{reasoning}")
            print(f"\nLLM Decision: {'EQUIVALENT (yes)' if is_equiv else 'NOT EQUIVALENT (no)'}")
            print(f"Full LLM Response:\n{response_text if response_text else '(Empty response after retries)'}")
            print(f"{'='*80}\n")
            
            # Cache result
            self._llm_equiv_cache[cache_key] = is_equiv
            
            return is_equiv
            
        except Exception as e:
            # Debugging output for errors
            problem_id = getattr(self, 'name', 'Unknown')
            print(f"\n{'='*80}")
            print("LLM Fallback Equivalence Check - ERROR")
            print(f"{'='*80}")
            print(f"Problem ID: {problem_id}")
            print(f"Ground Truth: {gold}")
            print(f"Proposed Answer: {predicted}")
            if problem_context:
                print(f"Problem Statement:\n{problem_context}")
            else:
                print("Problem Statement: (not provided)")
            print(f"Error: {e}")
            print(f"{'='*80}\n")
            # If API call fails, return False and don't cache
            return False

    def score_solution(self, solution: str, problem_context: Optional[str] = None) -> float:
        """Score the solution (1.0 for correct, 0.0 for incorrect).
        
        Args:
            solution: The solution string to score
            problem_context: Optional problem statement for LLM fallback
        """
        extracted_pred = self._extract_answer(solution)
        ground_truth = self.get_ground_truth()
        
        if self._is_equiv(extracted_pred, ground_truth, problem_context=problem_context):
            return 1.0
        return 0.0

    def _collect_individual_answers(self, agents: List[TeamAgent]) -> Dict[int, str]:
        """Collect independent answers from each agent."""
        answers = {}
        for agent in agents:
            task_desc = self.get_task_description(agent.profile.agent_id)
            prompt = f"{task_desc}\n\nPlease solve this problem independently. Show your reasoning step-by-step and put your final answer within \\boxed{{}}."
            
            # Add context to trajectory
            context_turn = Turn(speaker_id=-1, content=prompt)
            agent.trajectory.append(context_turn)
            
            turn = agent.act()
            answers[agent.profile.agent_id] = turn.content
            
        return answers

    def _extract_expert_vote(self, text: str) -> int | None:
        """Extract expert vote from text."""
        # Look for "I vote for Agent X" or "Agent X has the best reasoning"
        match = re.search(r'(?:vote|identify|best).*agent\s+(\d+)', text.lower())
        if match:
            return int(match.group(1))
        return None

    def _collect_expert_votes(self, agents: List[TeamAgent], individual_answers: Dict[int, str]) -> Dict[int, int | None]:
        """Collect explicit votes for the best expert."""
        votes = {}
        
        for agent in agents:
            agent_id = agent.profile.agent_id
            
            # Format answers for review
            answers_text = "\n\n".join(
                f"Agent {aid}:\n{individual_answers.get(aid, 'No answer provided')}"
                for aid in sorted(individual_answers.keys())
            )
            
            prompt = f"""Review the solutions provided by all agents:

{answers_text}

Based on the reasoning and accuracy, which agent provides the best solution?
Please independently vote for the best agent (it can be yourself or another agent).
Format: "I vote for Agent X because..."
"""
            prompt_turn = Turn(speaker_id=-1, content=prompt)
            agent.trajectory.append(prompt_turn)
            
            turn = agent.act()
            vote = self._extract_expert_vote(turn.content)
            votes[agent_id] = vote
            
        return votes

    def _facilitate_collaboration(self, agents: List[TeamAgent], individual_answers: Dict[int, str]) -> str:
        """Facilitate collaboration rounds and return final answer."""
        
        # 1. Share Individual Answers
        # In standard mode, agents just start discussing.
        # We can seed the discussion with everyone's initial thoughts if desired,
        # or just let them start. Let's explicitly share them to ground the debate.
        
        share_prompt = "Here are the initial independent solutions from all team members:\n\n"
        for aid, ans in individual_answers.items():
            share_prompt += f"--- Agent {aid} ---\n{ans}\n\n"
            
        share_turn = Turn(speaker_id=-1, content=share_prompt)
        for agent in agents:
            agent.trajectory.append(share_turn)

        # Add initial collaboration prompt
        collaboration_prompt = f"Collaborate with your team members to reach a final solution. You have {self.max_rounds} rounds to discuss."
        collaboration_turn = Turn(speaker_id=-1, content=collaboration_prompt)
        for agent in agents:
            agent.trajectory.append(collaboration_turn)

        # 2. Decision Mode Specific Logic
        if self.decision_mode == "reveal_expert":
            # Identify expert based on ground truth
            ground_truth = self.get_ground_truth()
            correct_agents = []
            
            for aid, ans in individual_answers.items():
                extracted = self._extract_answer(ans)
                if self._is_equiv(extracted, ground_truth, problem_context=self._current_problem_context):
                    correct_agents.append(aid)
            
            expert_id = None
            if correct_agents:
                # Pick one at random if multiple are correct
                rng = random.Random(self.seed)
                expert_id = rng.choice(correct_agents)
            else:
                # Fallback to most capable model
                if self.most_capable_model_name:
                    # Find agent with this model
                    capable_agents = []
                    for agent in agents:
                        # Check backend model name (handling potential variations)
                        model_name = agent.profile.metadata.get("backend_model", "")
                        if self.most_capable_model_name in model_name:
                            capable_agents.append(agent.profile.agent_id)
                    
                    if capable_agents:
                        rng = random.Random(self.seed)
                        expert_id = rng.choice(capable_agents)
                    else:
                        # No expert found
                        raise ValueError(f"No agent found with most_capable_model_name '{self.most_capable_model_name}' in reveal_expert mode")
                else:
                    # No expert found
                    raise ValueError("No agent was correct and no most_capable_model_name specified in reveal_expert mode")
            
            # Use unified message
            msg = f"After reviewing all agent's individual pre-discussion opinions, Agent {expert_id} has been deemed the relative expert on this topic."
            
            self.revealed_expert_agent_id = expert_id
            
            reveal_turn = Turn(speaker_id=-1, content=msg)
            for agent in agents:
                agent.trajectory.append(reveal_turn)

        elif self.decision_mode == "explicit_expert_voting":
            # Collect votes
            self.explicit_voting_votes = self._collect_expert_votes(agents, individual_answers)
            
            # Determine winner (simple majority)
            vote_counts = defaultdict(int)
            for vote in self.explicit_voting_votes.values():
                if vote is not None:
                    vote_counts[vote] += 1
            
            if vote_counts:
                # Sort by votes descending, then by ID for stability
                sorted_votes = sorted(vote_counts.items(), key=lambda x: (-x[1], x[0]))
                best_agent_id = sorted_votes[0][0]
                self.declared_best_agent_id = best_agent_id
                
                # Select coordinator (randomly)
                rng = random.Random(self.seed)
                self.coordinator_agent_id = rng.choice([a.profile.agent_id for a in agents])
                
                msg = f"Voting Results: Agent {best_agent_id} received the most votes ({vote_counts[best_agent_id]}). The team should treat their solution as the primary baseline."
            else:
                msg = "Voting Results: No clear consensus was reached."
                
            vote_turn = Turn(speaker_id=-1, content=msg)
            for agent in agents:
                agent.trajectory.append(vote_turn)

        # 3. Discussion Rounds
        for round_num in range(self.max_rounds):
            # Randomize speaking order
            round_agents = agents.copy()
            rng = random.Random(self.seed + round_num) if self.seed is not None else random
            rng.shuffle(round_agents)
            
            for agent in round_agents:
                agent_id = agent.profile.agent_id
                other_agent_ids = [aid for aid in self.agent_ids if aid != agent_id]
                other_agents_str = ", ".join(f"Agent {aid}" for aid in other_agent_ids)
                
                # Add agent identity reminder before they speak
                agent_identity_prefix = f"You are Agent {agent_id}. You are working with {len(self.agent_ids) - 1} other agents ({other_agents_str}).\n\n"
                prompt = agent_identity_prefix + f"Collaborate with your team members to reach a final solution. You have {self.max_rounds} rounds to discuss, and this is round {round_num + 1}."
                prompt_turn = Turn(speaker_id=-1, content=prompt)
                agent.trajectory.append(prompt_turn)
                
                turn = agent.act()
                
                # Share with others
                for other in agents:
                    if other.profile.agent_id != agent.profile.agent_id:
                        other.trajectory.append(turn)

        # 4. Final Answer Extraction
        # Ask a random agent for the final team answer
        rng = random.Random(self.seed + 100) if self.seed is not None else random
        final_agent = rng.choice(agents)
        
        final_agent_id = final_agent.profile.agent_id
        other_agent_ids = [aid for aid in self.agent_ids if aid != final_agent_id]
        other_agents_str = ", ".join(f"Agent {aid}" for aid in other_agent_ids)
        
        # Add agent identity reminder before final answer
        agent_identity_prefix = f"You are Agent {final_agent_id}. You are working with {len(self.agent_ids) - 1} other agents ({other_agents_str}).\n\n"
        final_prompt = agent_identity_prefix + "Discussion complete. Please provide the FINAL TEAM ANSWER. Explain your reasoning and YOU MUST put the final result in \\boxed{}."
        final_turn_prompt = Turn(speaker_id=-1, content=final_prompt)
        final_agent.trajectory.append(final_turn_prompt)
        
        final_turn = final_agent.act()
        
        return final_turn.content

    def execute(self, agents: List[TeamAgent]) -> TaskResult:
        """Execute the collaborative math task."""
        
        # Store problem context for LLM fallback
        # Get problem context from task description (use agent 0's description as representative)
        try:
            self._current_problem_context = self.get_task_description(agents[0].profile.agent_id if agents else 0)
        except Exception:
            self._current_problem_context = None
        
        # 1. Individual Phase
        individual_solutions = self._collect_individual_answers(agents)
        
        # Extract individual answers from solutions
        individual_answers = {}
        for aid, solution_text in individual_solutions.items():
            individual_answers[aid] = self._extract_answer(solution_text)
        
        # 2. Collaborative Phase
        final_team_solution = self._facilitate_collaboration(agents, individual_solutions)
        final_team_answer = self._extract_answer(final_team_solution)
        
        # 3. Scoring
        ground_truth = self.get_ground_truth()
        
        # Score individual answers
        individual_scores = {}
        individual_correctness = {}
        for aid, answer in individual_answers.items():
            score = self.score_solution(individual_solutions[aid], problem_context=self._current_problem_context)
            individual_scores[aid] = score
            individual_correctness[aid] = (score == 1.0)
            
        # Score team answer
        team_score = self.score_solution(final_team_solution, problem_context=self._current_problem_context)
        
        # Metadata
        metadata = {
            "ground_truth": ground_truth,
            "individual_solutions": individual_solutions,  # Full solution text
            "individual_answers": individual_answers,  # Extracted answers
            "individual_scores": individual_scores,
            "individual_correctness": individual_correctness,
            "team_solution": final_team_solution,  # Full solution text
            "team_answer": final_team_answer,  # Extracted answer
            "decision_mode": self.decision_mode,
            "declared_best_agent_id": self.declared_best_agent_id,
            "coordinator_agent_id": self.coordinator_agent_id,
            "revealed_expert_agent_id": self.revealed_expert_agent_id,
            "seed": self.seed
        }
        
        return TaskResult(
            solution=final_team_solution,
            score=team_score,
            metadata=metadata
        )

