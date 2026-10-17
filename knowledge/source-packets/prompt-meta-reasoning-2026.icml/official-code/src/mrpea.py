import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Union

from .memory import PersistentMemory
from datetime import datetime
from .agents import (
    AbstractionAgent,
    ExampleGenerationAgent,
    PromptRefinementAgent,
    EvaluationAgent,
)

# Set up logging
logger = logging.getLogger(__name__)


class MRPEAAgent:
    """Main agent that optimizes prompts using memory and multiple specialized agents"""

    def __init__(self,
                 config: Dict[str, Any],
                 system_prompts: Dict[str, Any],
                 user_message: Dict[str, Any],
                 openai_client,
                 linkup_client=None):

        # Store core components
        self.config = config
        self.system_prompts = system_prompts
        self.user_message = user_message
        self.openai_client = openai_client
        self.linkup_client = linkup_client

        # Get task settings
        task_config = config.get('task', {})
        self.task_name = task_config.get('task_name', 'default')

        # Get optimization settings
        optimization_config = config.get('optimization', {})
        self.max_iterations = optimization_config.get('max_iterations', 10)
        self.win_threshold = optimization_config.get('win_threshold', 3)
        self.current_best_id = optimization_config.get('current_best_id', 0)

        # Get ranking settings
        ranking_config = optimization_config.get('ranking', {})
        self.iteration_bonus = ranking_config.get('iteration_bonus', 0.1)
        self.decay_factor = ranking_config.get('decay_factor', 0.9)
        self.base_score = ranking_config.get('base_score', 1.0)

        # Get system and output settings
        system_config = config.get('system', {})
        output_config = config.get('output', {})

        self.memory_dir = system_config.get('memory_dir', 'data/memory')
        self.results_dir = output_config.get('results_dir', 'results/')
        self.export_memory = output_config.get('export_memory', True)

        # Web search settings
        web_search_config = config.get('web_search', {})
        self.enable_web_search = web_search_config.get('enabled', False)
        self.web_search_count = 0
        self.max_web_searches = web_search_config.get('max_searches', 2)
        self.historical_prompt_limit = optimization_config.get('historical_prompt_limit', 3)
        self.last_search_iteration = -1

        self.consecutive_wins = 0

        # Set up persistent memory
        self.memory = PersistentMemory(memory_dir=self.memory_dir, task_name=self.task_name)

        # Set up all agents
        self._initialize_agents()

        logger.info(f"MR.PEA Agent started for task: {self.task_name}")
        if self.enable_web_search:
            logger.info(f"Web search enabled with limit: {self.max_web_searches} searches maximum")
        else:
            logger.info("Web search disabled")

    def _initialize_agents(self):
        """Set up all the specialized agents with their specific prompts and config"""
        agents_config = self.config.get('agents', {})

        self.abstraction_agent = AbstractionAgent(
            system_prompt=self.system_prompts.get('abstraction', {}),
            user_message=self.user_message.get('abstraction', {}),
            openai_client=self.openai_client,
            config=agents_config.get('meta_reasoning', {})
        )

        self.example_generation_agent = ExampleGenerationAgent(
            system_prompt=self.system_prompts.get('example_generation', {}),
            user_message=self.user_message.get('example_generation', {}),
            openai_client=self.openai_client,
            config=agents_config.get('meta_reasoning', {})
        )

        self.prompt_refinement_agent = PromptRefinementAgent(
            system_prompt=self.system_prompts.get('prompt_refinement', {}),
            user_message=self.user_message.get('prompt_refinement', {}),
            openai_client=self.openai_client,
            config=agents_config.get('prompt_refinement', {})
        )

        self.evaluation_agent = EvaluationAgent(
            system_prompt=self.system_prompts.get('evaluation', {}),
            user_message=self.user_message.get('evaluation', {}),
            openai_client=self.openai_client,
            config=agents_config.get('evaluation', {})
        )

        # Conditionally initialize web search agents
        if self.enable_web_search:
            from .agents import WebSearchAgent, MetaDecisionAgent

            self.web_search_agent = WebSearchAgent(
                system_prompt=self.system_prompts.get('web_search', {}),
                user_message=self.user_message.get('web_search', {}),
                openai_client=self.openai_client,
                linkup_client=self.linkup_client,
                config=agents_config.get('web_search', {})
            )

            self.meta_decision_agent = MetaDecisionAgent(
                system_prompt=self.system_prompts.get('meta_decision', {}),
                user_message=self.user_message.get('meta_decision', {}),
                openai_client=self.openai_client,
                config=agents_config.get('meta_decision', {})
            )

            # Wire agents together for web search pipeline
            self.abstraction_agent.set_web_search_agent(self.web_search_agent)
            self.abstraction_agent.set_meta_decision_agent(self.meta_decision_agent)
            self.abstraction_agent.set_memory(self.memory)

            self.web_search_counter_ref = {'count': 0, 'max': self.max_web_searches, 'last_iteration': -1}
            self.abstraction_agent.set_web_search_counter(self.web_search_counter_ref)
            self.meta_decision_agent.set_web_search_counter(self.web_search_counter_ref)
        else:
            self.web_search_agent = None
            self.meta_decision_agent = None

        logger.info("All specialized agents set up successfully")

    def update_knowledge(self, task_description: str,
                        latest_knowledge: str = "", latest_example: str = "", iteration: int = 1) -> Dict:
        """Use abstraction agent to update knowledge"""
        logger.info(f"Starting knowledge update through abstraction for iteration {iteration}")

        knowledge = self.abstraction_agent.execute(
            task_description=task_description,
            latest_knowledge=latest_knowledge,
            latest_example=latest_example,
            iteration=iteration
        )

        # If web search was performed, store the retrieved information in memory
        if self.enable_web_search and knowledge.get('web_search_performed') and knowledge.get('retrieved_information'):
            self.memory.add_retrieved_information(knowledge['retrieved_information'])

        return knowledge

    def generate_examples(self, task_description: str, latest_knowledge: str = "",
                          recent_examples: str = "") -> List[Dict]:
        """Use example generation agent to create new examples"""
        logger.info("Starting example generation")

        retrieved_information = ""
        if self.enable_web_search:
            task_keywords = self._extract_task_keywords(task_description)
            if task_keywords:
                retrieved_information = self.memory.get_relevant_retrieved_information(
                    task_keywords=task_keywords, limit=2
                )
            else:
                retrieved_information = self.memory.get_retrieved_information_for_prompt_refinement(limit=2)

        examples = self.example_generation_agent.execute(
            task_description=task_description,
            latest_knowledge=latest_knowledge,
            recent_examples=recent_examples,
            retrieved_information=retrieved_information
        )

        return examples

    def _knowledge_actually_changed(self, new_knowledge: Dict) -> bool:
        """Check if the new knowledge is actually different from what we already have"""
        if not new_knowledge:
            return False

        if not new_knowledge.get('need_change', True):
            return False

        latest_knowledge = self.memory.get_latest_knowledge()
        if not latest_knowledge:
            return True

        if isinstance(latest_knowledge, dict) and isinstance(new_knowledge, dict):
            old_strategies = set(latest_knowledge.get('strategies', []))
            new_strategies = set(new_knowledge.get('strategies', []))
            old_principles = set(latest_knowledge.get('principles', []))
            new_principles = set(new_knowledge.get('principles', []))

            strategies_changed = old_strategies != new_strategies
            principles_changed = old_principles != new_principles

            return strategies_changed or principles_changed

        return True

    def refine_prompt(self, current_best: str, task_description: str ="", latest_knowledge: str = "",
                     latest_example: str = "", latest_feedback: str = "") -> str:
        """Improve the current best prompt using knowledge and feedback"""
        historical_prompts_with_scores = self.memory.get_historical_prompts_with_scores(limit=self.historical_prompt_limit)

        retrieved_information = ""
        if self.enable_web_search:
            task_keywords = self._extract_task_keywords(task_description)
            if task_keywords:
                retrieved_information = self.memory.get_relevant_retrieved_information(
                    task_keywords=task_keywords, limit=3
                )
            else:
                retrieved_information = self.memory.get_retrieved_information_for_prompt_refinement(limit=5)

        return self.prompt_refinement_agent.execute(
            current_best=current_best,
            task_description=task_description,
            latest_knowledge=latest_knowledge,
            latest_example=latest_example,
            latest_feedback=latest_feedback,
            historical_prompts_with_scores=historical_prompts_with_scores,
            retrieved_information=retrieved_information
        )

    def _extract_task_keywords(self, task_description: str) -> List[str]:
        """Extract relevant keywords from task description for information retrieval"""
        if not task_description:
            return []

        import re

        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        words = re.findall(r'\b[a-zA-Z]+\b', task_description.lower())
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]

        return list(set(keywords))[:10]

    def compare_prompts(self, prompt_1: str, prompt_2: str,
                        latest_example: Union[str, Dict] = "", latest_knowledge: str = "") -> Dict:
        """Compare two prompts by testing them and evaluating their outputs"""
        return self.evaluation_agent.execute(
            prompt_1=prompt_1,
            prompt_2=prompt_2,
            latest_example=latest_example,
            latest_knowledge=latest_knowledge
        )

    def _should_update_knowledge(self, in_sparse_update_mode: bool, iterations_since_last_update: int) -> bool:
        """Determine if knowledge should be updated in current iteration"""
        if not in_sparse_update_mode:
            return True
        else:
            return iterations_since_last_update >= 3

    def _handle_knowledge_update_mode(self, knowledge: Dict, in_sparse_update_mode: bool,
                                    iterations_since_last_update: int) -> tuple[bool, int]:
        """Handle knowledge update mode switching logic"""
        if isinstance(knowledge, dict):
            need_change = knowledge.get('need_change', True)
            logger.info(f"Knowledge need_change: {need_change}")

            if need_change:
                if in_sparse_update_mode:
                    in_sparse_update_mode = False
                    iterations_since_last_update = 0
                    logger.info("Received need_change: true, switching to continuous update mode")
            else:
                if not in_sparse_update_mode:
                    in_sparse_update_mode = True
                    logger.info("Received need_change: false, switching to sparse update mode (every 3 iterations)")
                else:
                    logger.info("Already in sparse update mode, need_change: false confirmed")
        else:
            logger.warning(f"Knowledge is not a dict or is None: {type(knowledge)}, value: {knowledge}")

        return in_sparse_update_mode, iterations_since_last_update

    def _update_prompt_rankings(self, winner: int, new_prompt_id: int, iteration: int) -> None:
        """Update prompt rankings based on evaluation results"""
        current_scores = self.memory.state.ranking_scores.copy()

        if winner == 2:  # New prompt wins
            current_scores[new_prompt_id] = self.base_score + iteration * self.iteration_bonus
            self.current_best_id = new_prompt_id
            self.consecutive_wins = 1
            logger.info(f"New prompt (ID: {new_prompt_id}) wins this round")
        else:  # Current best wins
            for pid in current_scores:
                current_scores[pid] *= self.decay_factor
            current_scores[self.current_best_id] += iteration * self.iteration_bonus
            current_scores[new_prompt_id] = self.base_score
            self.consecutive_wins += 1
            logger.info(f"Current best prompt (ID: {self.current_best_id}) wins this round")

        self.memory.update_ranking_scores(current_scores)

    def optimize_prompt(self, task_description: str, task_objective: str = "", sample_question: str = "") -> str:
        """Main optimization loop that improves prompts using memory and specialized agents"""
        logger.info(f"Starting MR.PEA prompt optimization for task: {self.task_name}")

        initial_prompt = task_description

        prompt_id = self.memory.add_prompt(initial_prompt, iteration=0)
        self.memory.add_examples([{"sample_question": sample_question}])

        ranking_scores = {prompt_id: self.base_score}
        self.memory.update_ranking_scores(ranking_scores)
        self.current_best_id = prompt_id

        logger.info(f"Initial prompt created (ID: {prompt_id}): {initial_prompt[:100]}...")

        in_sparse_update_mode = False
        iterations_since_last_update = 0

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"=============== Iteration {iteration}")

            should_update = self._should_update_knowledge(in_sparse_update_mode, iterations_since_last_update)

            logger.info(f"Update mode: {'dense' if not in_sparse_update_mode else 'sparse'}, "
                       f"iterations_since_last_update: {iterations_since_last_update}, "
                       f"should_update: {should_update}")

            if should_update:
                knowledge = self.update_knowledge(
                    task_description=task_description,
                    latest_knowledge=self.memory.get_latest_knowledge(),
                    latest_example=self.memory.get_latest_example(),
                    iteration=iteration
                )

                in_sparse_update_mode, iterations_since_last_update = self._handle_knowledge_update_mode(
                    knowledge, in_sparse_update_mode, iterations_since_last_update
                )

                if self._knowledge_actually_changed(knowledge):
                    self.memory.add_knowledge(knowledge)
                    logger.info("Knowledge updated with new insights")
                else:
                    logger.info("Knowledge remained unchanged")
            else:
                logger.info(f"Skipping knowledge update in iteration {iteration} for efficiency")

                if in_sparse_update_mode:
                    iterations_since_last_update += 1

            examples = self.generate_examples(
                task_description=task_description,
                latest_knowledge=self.memory.get_latest_knowledge(),
                recent_examples=self.memory.get_recent_examples(limit=3)
            )

            self.memory.add_examples(examples)

            current_best = self.memory.get_prompt(self.current_best_id)

            new_prompt = self.refine_prompt(
                current_best=current_best,
                task_description=task_description,
                latest_knowledge=self.memory.get_latest_knowledge(),
                latest_example=self.memory.get_latest_example(),
                latest_feedback=self.memory.get_latest_feedback()
            )

            new_prompt_id = self.memory.add_prompt(new_prompt, iteration=iteration)

            logger.info(f"Current best prompt (ID: {self.current_best_id}): {current_best[:100]}...")
            logger.info(f"Refined new prompt (ID: {new_prompt_id}): {new_prompt[:100]}...")

            evaluation_result = self.compare_prompts(
                prompt_1=current_best,
                prompt_2=new_prompt,
                latest_example=self.memory.get_latest_example(),
                latest_knowledge=self.memory.get_latest_knowledge()
            )

            winner = evaluation_result["winner"]
            feedback = "; ".join(evaluation_result["feedback"]) if evaluation_result["feedback"] else "No feedback"

            self._update_prompt_rankings(winner, new_prompt_id, iteration)

            self.memory.add_feedback(feedback)

            if self.consecutive_wins >= self.win_threshold:
                logger.info(f"Stopping: Current best won {self.win_threshold} times consecutively")
                break

        best_id = self.memory.get_best_prompt_id()
        best_prompt = self.memory.get_prompt(best_id)

        best_prompt = best_prompt + " " + task_objective

        logger.info(f"Optimization complete. Best prompt ID: {best_id}")

        return best_prompt

    def save_results(self, task_name: str = None, best_prompt: str = None, output_path: str = None):
        """Save optimization results to files"""
        if task_name is None:
            task_name = self.task_name
        if output_path is None:
            output_path = self.results_dir
        if best_prompt is None:
            best_id = self.memory.get_best_prompt_id()
            best_prompt = self.memory.get_prompt(best_id)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"{output_path}/{task_name}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)

        memory_stats = self.memory.get_memory_stats()

        results = {
            "task_name": task_name,
            "best_prompt": best_prompt,
            "best_prompt_id": self.memory.get_best_prompt_id(),
            "memory_stats": memory_stats,
            "optimization_history": {
                "prompts": self.memory.state.prompt_pool,
                "scores": self.memory.state.ranking_scores,
                "feedback": self.memory.state.feedback_memory,
                "knowledge_count": len(self.memory.state.knowledge_memory),
                "examples_count": len(self.memory.state.example_memory)
            }
        }

        with open(output_dir / f"{task_name}_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        if self.export_memory:
            self.memory.export_memory(output_dir / f"{task_name}_complete_memory.json")

        logger.info(f"Results saved to {output_dir}/{task_name}_results.json")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return self.memory.get_memory_stats()

    def clear_memory(self):
        """Clear all memory data"""
        self.memory.clear_memory()
        logger.info("Memory cleared")
