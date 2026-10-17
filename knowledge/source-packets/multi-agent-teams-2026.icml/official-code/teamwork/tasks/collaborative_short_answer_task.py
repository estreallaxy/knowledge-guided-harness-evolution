"""Base class for collaborative short-answer tasks.

This class contains generic logic for collaborative short-answer tasks, including
decision modes, debate facilitation, and GPT-5 autorating for answer evaluation.
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

import openai



class CollaborativeShortAnswerTask(Task):
    """Base class for collaborative short-answer tasks.

    Agents independently answer a short-answer question, then collaborate to find the
    correct answer. Answers are evaluated using GPT-5 autorating.

    Derived classes must implement:
    - get_task_description: Task-specific question description
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
        llm_fallback_model: str = "gpt-5-2025-08-07",
        llm_fallback_api_key: Optional[str] = None,
    ):
        """Initialize collaborative short-answer task.

        Args:
            agent_ids: List of unique agent IDs that will work on this task
            max_rounds: Maximum number of collaboration rounds (required)
            seed: Random seed for reproducibility (required)
            decision_mode: Decision strategy for team collaboration 
                           ("expert_not_mentioned", "explicit_expert_voting", "reveal_expert")
            most_capable_model_name: Model name to use as fallback expert in "reveal_expert" mode
            name: Optional human-readable name for the task
            use_llm_fallback: Whether to use LLM for equivalence checking (always True for short-answer)
            llm_fallback_model: Model name for LLM autorating (e.g., "gpt-5-2025-08-07")
            llm_fallback_api_key: OpenAI API key for LLM autorating (defaults to OPENAI_API_KEY env var)
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
        
        # Problem context for LLM autorating (set during execution)
        self._current_problem_context: Optional[str] = None
        
        # Cache for LLM equivalence checks (key: (problem_hash, pred, gold))
        self._llm_equiv_cache: Dict[Tuple[str, str, str], bool] = {}

        # Validate decision modes
        valid_decision_modes = ["expert_not_mentioned", "explicit_expert_voting", "reveal_expert"]
        if self.decision_mode not in valid_decision_modes:
            raise ValueError(f"decision_mode must be one of {valid_decision_modes}, got '{self.decision_mode}'")

    @abstractmethod
    def get_task_description(self, agent_id: int) -> str:
        """Return the task description (question) for a specific agent."""
        ...

    @abstractmethod
    def get_ground_truth(self) -> str:
        """Return the ground truth answer string."""
        ...
    
    def get_hidden_info(self, agent_id: int) -> str:
        """Return empty string as short-answer tasks typically don't have hidden info per agent."""
        return ""

    def _extract_answer(self, text: str) -> str:
        """Extract the answer from "My answer is X" format.
        
        Since we explicitly instruct agents to put their answer on one line with
        "My answer is X", we extract until the first newline. GPT-5 autorating
        will handle equivalence checking for variations (e.g., "Dr. Smith" vs "Dr Smith").
        
        Args:
            text: The text containing the answer
            
        Returns:
            Extracted answer string or empty string if not found
        """
        text = str(text).strip()
        
        # Look for "My answer is X" pattern (case-insensitive)
        # Extract everything after "My answer is" until newline or end of string
        pattern = r'my\s+answer\s+is\s*:?\s*(.+?)(?:\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            answer = match.group(1).strip()
            # Remove trailing punctuation (period, semicolon, colon)
            # GPT-5 autorating will handle equivalence for variations
            answer = answer.rstrip('.;:')
            if answer:
                return answer
        
        # Fallback: look for "answer is X" without "my"
        pattern_fallback = r'answer\s+is\s*:?\s*(.+?)(?:\n|$)'
        match = re.search(pattern_fallback, text, re.IGNORECASE | re.DOTALL)
        if match:
            answer = match.group(1).strip()
            answer = answer.rstrip('.;:')
            if answer:
                return answer
        
        # If no pattern found, return empty string
        return ""

    def _is_equiv(
        self, 
        predicted: str, 
        gold: str, 
        problem_context: Optional[str] = None
    ) -> bool:
        """Check if predicted answer is equivalent to ground truth using GPT-5 autorating.
        
        Args:
            predicted: The predicted answer string
            gold: The ground truth answer string
            problem_context: Optional problem statement for LLM autorating
        """
        # Step 1: Check exact match first (case-insensitive, whitespace-normalized)
        norm_pred = predicted.strip().lower()
        norm_gold = gold.strip().lower()
        
        if norm_pred == norm_gold:
            return True
        
        # Step 2: If exact match fails, use LLM autorating as fallback
        if self.use_llm_fallback and self.llm_fallback_api_key:
            try:
                return self._check_equiv_with_llm(predicted, gold, problem_context)
            except Exception:
                # If LLM check fails, return False
                pass
        
        return False

    def _check_equiv_with_llm(
        self, 
        predicted: str, 
        gold: str, 
        problem_context: Optional[str] = None
    ) -> bool:
        """Check equivalence using GPT-5 autorating.
        
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
            prompt = f"""Given the following question:

{problem_context}

Are these two answers equivalent? Consider them equivalent if they represent the same information, even if formatted differently.

Consider the following when evaluating equivalence:
- Numerical ranges: "10-15" is equivalent to "between 10 and 15" or "10 to 15"
- Name variations: "John Smith" is equivalent to "Smith, John" or "J. Smith"
- Date formats: "2020-01-01" is equivalent to "January 1, 2020" or "1/1/2020"
- Synonyms: "car" is equivalent to "automobile"
- Approximate values: "about 10" is equivalent to "approximately 10" or "~10"
- Units: "10 meters" is equivalent to "10m" or "ten meters"

Answer 1: {predicted}
Answer 2: {gold}

First, explain your reasoning for why they are or are not equivalent. Then, on a new line, respond with only 'yes' or 'no'."""
        else:
            prompt = f"""Are these two answers equivalent? Consider them equivalent if they represent the same information, even if formatted differently.

Consider the following when evaluating equivalence:
- Numerical ranges: "10-15" is equivalent to "between 10 and 15" or "10 to 15"
- Name variations: "John Smith" is equivalent to "Smith, John" or "J. Smith"
- Date formats: "2020-01-01" is equivalent to "January 1, 2020" or "1/1/2020"
- Synonyms: "car" is equivalent to "automobile"
- Approximate values: "about 10" is equivalent to "approximately 10" or "~10"
- Units: "10 meters" is equivalent to "10m" or "ten meters"

Answer 1: {predicted}
Answer 2: {gold}

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
                        {"role": "system", "content": "You are an expert at evaluating short-answer questions. Determine if two answers represent the same information, even if formatted differently. Consider numerical ranges, name variations, date formats, synonyms, and approximate values. First explain your reasoning very concisely, then provide 'yes' or 'no'."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=1000
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
                reasoning = response_text
                answer = ""
                is_equiv = False
                
                # Extract reasoning and yes/no answer
                response_lower = response_text.lower()
                
                # First, try to find standalone 'yes' or 'no' at the end (on its own line or as last word)
                # This handles cases like "reasoning\n\nyes" or "reasoning yes"
                last_newline = response_text.rfind('\n')
                if last_newline != -1:
                    last_line = response_text[last_newline:].strip().lower()
                    # Check if last line is just 'yes' or 'no'
                    if last_line == 'yes' or last_line == 'no':
                        reasoning = response_text[:last_newline].strip()
                        answer = last_line
                    else:
                        # Check if last line ends with 'yes' or 'no' as a word
                        words = last_line.split()
                        if len(words) > 0 and words[-1] in ['yes', 'no']:
                            reasoning = response_text[:last_newline].strip()
                            answer = words[-1]
                        else:
                            # Extract from the full response
                            reasoning = response_text[:last_newline].strip()
                            answer = ""
                else:
                    # No newline, check last word
                    words = response_text.split()
                    if len(words) > 0 and words[-1].lower() in ['yes', 'no']:
                        reasoning = ' '.join(words[:-1])
                        answer = words[-1].lower()
                    else:
                        reasoning = response_text
                        answer = ""
                
                # If we didn't find yes/no cleanly, search for it anywhere in the response
                if not answer:
                    # Look for 'yes' or 'no' as standalone words (not part of other words)
                    yes_match = re.search(r'\byes\b', response_lower)
                    no_match = re.search(r'\bno\b', response_lower)
                    
                    if yes_match and (not no_match or yes_match.end() > no_match.end()):
                        answer = 'yes'
                        yes_idx = yes_match.end()
                        reasoning = response_text[:yes_idx].strip()
                    elif no_match:
                        answer = 'no'
                        no_idx = no_match.end()
                        reasoning = response_text[:no_idx].strip()
                    else:
                        # Fallback: default to 'no' if we can't find either
                        reasoning = response_text
                        answer = 'no'
                
                # Determine equivalence: check if answer contains 'yes' (not just starts with it)
                is_equiv = 'yes' in answer.lower()
                
                # Fallback: if reasoning ended up empty, use full response as reasoning
                if not reasoning:
                    reasoning = response_text
            
            # Debugging output
            problem_id = getattr(self, 'name', 'Unknown')
            print(f"\n{'='*80}")
            print("GPT-5 Autorating Equivalence Check")
            print(f"{'='*80}")
            print(f"Problem ID: {problem_id}")
            print(f"Ground Truth: {gold}")
            print(f"Proposed Answer: {predicted}")
            if problem_context:
                print(f"Problem Statement:\n{problem_context}")
            else:
                print("Problem Statement: (not provided)")
            print(f"\nGPT-5 Reasoning:\n{reasoning}")
            print(f"\nGPT-5 Decision: {'EQUIVALENT (yes)' if is_equiv else 'NOT EQUIVALENT (no)'}")
            print(f"Full GPT-5 Response:\n{response_text if response_text else '(Empty response after retries)'}")
            print(f"{'='*80}\n")
            
            # Cache result
            self._llm_equiv_cache[cache_key] = is_equiv
            
            return is_equiv
            
        except Exception as e:
            # Debugging output for errors
            problem_id = getattr(self, 'name', 'Unknown')
            print(f"\n{'='*80}")
            print("GPT-5 Autorating Equivalence Check - ERROR")
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
            return False

    def score_solution(self, solution: str, problem_context: Optional[str] = None) -> float:
        """Score the solution (1.0 for correct, 0.0 for incorrect).
        
        Args:
            solution: The solution string to score
            problem_context: Optional problem statement for LLM autorating
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
            prompt = f"{task_desc}\n\nPlease answer this question independently. Show your reasoning step-by-step. On a new line, you MUST end your response with 'My answer is X' where X is your final answer."
            
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
            
            prompt = f"""Review the answers provided by all agents:

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
        share_prompt = "Here are the initial independent answers from all team members:\n\n"
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
        final_prompt = agent_identity_prefix + "Discussion complete. Please provide the FINAL TEAM ANSWER. State your reasoning and then, on a new line, end with EXACTLY the following format: My answer is X where X is your final answer."
        final_turn_prompt = Turn(speaker_id=-1, content=final_prompt)
        final_agent.trajectory.append(final_turn_prompt)
        
        final_turn = final_agent.act()
        
        return final_turn.content

    def execute(self, agents: List[TeamAgent]) -> TaskResult:
        """Execute the collaborative short-answer task."""
        
        # Store problem context for LLM autorating
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

