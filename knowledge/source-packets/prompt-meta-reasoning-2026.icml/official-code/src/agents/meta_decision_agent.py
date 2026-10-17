"""
Meta Decision agent for intelligent web search decision making
Only used when enable_web_search is true in config.
"""

import json
from typing import Dict, List
from .base_agent import BaseAgent


class MetaDecisionAgent(BaseAgent):
    """Agent responsible for making intelligent decisions about web search necessity"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.web_search_counter = None

    def set_web_search_counter(self, counter_ref):
        """Set reference to web search counter"""
        self.web_search_counter = counter_ref

    def execute(self, task_description: str, current_knowledge: str = "",
                iteration: int = 1, remaining_searches: int = 2) -> Dict:
        """
        Intelligently decide whether web search is needed and assess importance

        Args:
            task_description: Description of the task being performed
            current_knowledge: Current knowledge state (strategies, principles, etc.)
            iteration: Current iteration number
            remaining_searches: Number of web searches remaining

        Returns:
            Decision dictionary with search_needed, importance_score, rationale, etc.
        """
        self.log_info(f"Making intelligent web search decision for iteration {iteration}")

        user_message = self.format_user_message(
            task_description=task_description,
            current_knowledge=self._clean_knowledge_for_input(current_knowledge),
            iteration=iteration,
            remaining_searches=remaining_searches
        )

        response = self.call_llm(user_message)

        try:
            decision_result = json.loads(response.strip())

            decision_result = self._validate_and_enhance_decision(
                decision_result, iteration, remaining_searches
            )

            self.log_info(f"Meta decision: search_needed={decision_result.get('search_needed', False)}, "
                         f"importance={decision_result.get('importance_score', 0)}")

            return decision_result

        except json.JSONDecodeError as e:
            self.log_info(f"Failed to parse meta decision JSON: {e}")
            return {
                "search_needed": False,
                "importance_score": 0,
                "rationale": "Failed to parse decision, defaulting to no search",
                "confidence": 0.0
            }

    def _validate_and_enhance_decision(self, decision: Dict, iteration: int, remaining_searches: int) -> Dict:
        """Validate and enhance the meta decision with additional logic"""
        search_needed = decision.get('search_needed', False)
        importance_score = decision.get('importance_score', 0)
        confidence = decision.get('confidence', 0.5)

        effective_importance_threshold = 5
        effective_confidence_threshold = 0.6

        if self.web_search_counter and search_needed:
            last_search_iteration = self.web_search_counter.get('last_iteration', -1)
            iteration_gap = iteration - last_search_iteration if last_search_iteration >= 0 else float('inf')

            if iteration_gap <= 1:
                effective_importance_threshold = 7
                effective_confidence_threshold = 0.8
                self.log_info(f"Recent search detected: raising threshold due to gap of {iteration_gap}")

            elif iteration_gap >= 2:
                effective_importance_threshold = 4
                effective_confidence_threshold = 0.5
                self.log_info(f"Good iteration gap ({iteration_gap}): encouraging distributed search with lower threshold")

        if iteration <= 1 and search_needed:
            if confidence < 0.7:
                search_needed = False
                decision['rationale'] = f"{decision.get('rationale', '')} (Early iteration requires high confidence)".strip()

        if remaining_searches <= 0:
            search_needed = False
            decision['rationale'] = f"{decision.get('rationale', '')} (No web searches remaining)".strip()

        if search_needed and (importance_score < effective_importance_threshold or confidence < effective_confidence_threshold):
            search_needed = False
            threshold_msg = f"(Importance score <{effective_importance_threshold} or confidence <{effective_confidence_threshold})"
            if self.web_search_counter:
                last_search_iteration = self.web_search_counter.get('last_iteration', -1)
                iteration_gap = iteration - last_search_iteration if last_search_iteration >= 0 else float('inf')
                if iteration_gap <= 1:
                    threshold_msg += f" (Recent search in iteration {last_search_iteration})"
            decision['rationale'] = f"{decision.get('rationale', '')} {threshold_msg}".strip()

        decision.update({
            'search_needed': search_needed,
            'importance_score': max(0, min(10, importance_score)),
            'confidence': max(0.0, min(1.0, confidence)),
            'iteration': iteration,
            'remaining_searches': remaining_searches
        })

        return decision

    def _clean_knowledge_for_input(self, knowledge: str) -> str:
        """Clean knowledge for input to LLM"""
        if not knowledge:
            return "No existing knowledge"

        try:
            if isinstance(knowledge, str):
                knowledge_dict = json.loads(knowledge)
            else:
                knowledge_dict = knowledge

            cleaned = {
                'strategies': knowledge_dict.get('strategies', []),
                'principles': knowledge_dict.get('principles', []),
                'evaluation_criteria': knowledge_dict.get('evaluation_criteria', []),
                'gap_hypotheses': knowledge_dict.get('gap_hypotheses', [])
            }

            return json.dumps(cleaned, ensure_ascii=False)

        except (json.JSONDecodeError, TypeError):
            return str(knowledge)[:500]
