"""
Abstraction agent for knowledge update and strategy refinement
Supports optional web search integration (only active when web search agents are wired).
"""

import json
from typing import Dict, Optional, List
from .base_agent import BaseAgent


class AbstractionAgent(BaseAgent):
    """Agent responsible for abstracting knowledge and strategies from examples"""

    def __init__(self, system_prompt: Dict, user_message: Dict, openai_client, config: Dict):
        super().__init__(system_prompt, user_message, openai_client, config)
        self.web_search_agent = None
        self.meta_decision_agent = None
        self.web_search_counter = None
        self.memory = None

    def set_web_search_agent(self, web_search_agent):
        """Set the web search agent for this abstraction agent"""
        self.web_search_agent = web_search_agent

    def set_meta_decision_agent(self, meta_decision_agent):
        """Set the meta decision agent for intelligent web search decisions"""
        self.meta_decision_agent = meta_decision_agent

    def set_web_search_counter(self, counter_ref: Dict):
        """Set reference to web search counter from parent agent"""
        self.web_search_counter = counter_ref

    def set_memory(self, memory):
        """Set memory reference for accessing historical web search results"""
        self.memory = memory

    def execute(self, task_description: str, latest_knowledge: str = "",
                latest_example: str = "", iteration: int = 1) -> Dict:
        """
        Perform knowledge abstraction from examples and feedback, with optional web search

        Args:
            task_description: Description of the task to be performed
            latest_knowledge: Latest knowledge entry (can be empty for first round)
            latest_example: Latest example entry (can be empty)
            iteration: Current iteration number (1-based)

        Returns:
            Knowledge dictionary with strategies, principles, need_change flag, and optional search results
        """
        self.log_info(f"Starting knowledge abstraction for iteration {iteration}")

        user_message = self.format_user_message(
            task_description=task_description,
            sample_question=latest_example,
            latest_knowledge=self._clean_knowledge_for_input(latest_knowledge)
        )

        response = self.call_llm(user_message)

        try:
            abstraction_result = json.loads(response.strip())

            if not latest_knowledge and not abstraction_result.get('need_change', True):
                self.log_info("Overriding need_change=False because no existing knowledge provided")
                abstraction_result['need_change'] = True
                abstraction_result['change_rationale'] = "First iteration - generating initial knowledge"

            if not abstraction_result.get('need_change', True):
                self.log_info("LLM determined no changes needed, returning LLM response")
                return abstraction_result

            # Web search integration: only active when agents are wired (web mode)
            if iteration >= 2:
                if self.web_search_agent and self.meta_decision_agent:
                    remaining_searches = 0
                    if self.web_search_counter:
                        remaining_searches = self.web_search_counter['max'] - self.web_search_counter['count']

                    if remaining_searches > 0:
                        abstraction_result = self._intelligent_web_search_decision(
                            abstraction_result, task_description, iteration
                        )
                    else:
                        self.log_info("No web searches remaining, using historical web search knowledge")
                        abstraction_result = self._use_historical_web_knowledge(
                            abstraction_result, task_description
                        )
                else:
                    # No web search agents wired, try historical knowledge
                    abstraction_result = self._use_historical_web_knowledge(
                        abstraction_result, task_description
                    )

            self.log_info("Abstraction step completed successfully with changes")
            return abstraction_result

        except json.JSONDecodeError as e:
            self.log_info(f"Failed to parse abstraction JSON: {e}")
            return {"need_change": False}

    def _clean_knowledge_for_input(self, latest_knowledge: str) -> str:
        """Remove need_change and other output-only fields from knowledge before sending to LLM"""
        if not latest_knowledge:
            return latest_knowledge

        try:
            if isinstance(latest_knowledge, str):
                knowledge_dict = json.loads(latest_knowledge)
            else:
                knowledge_dict = latest_knowledge

            cleaned_dict = {k: v for k, v in knowledge_dict.items()
                          if k not in ['need_change', 'change_rationale']}

            return json.dumps(cleaned_dict, ensure_ascii=False)

        except (json.JSONDecodeError, TypeError):
            return latest_knowledge

    def _intelligent_web_search_decision(self, abstraction_result: Dict, task_description: str,
                                       iteration: int) -> Dict:
        """Use meta decision agent to intelligently decide whether web search is needed"""
        remaining_searches = 0
        if self.web_search_counter:
            remaining_searches = self.web_search_counter['max'] - self.web_search_counter['count']

        self.log_info("Consulting meta decision agent for web search recommendation")

        meta_decision = self.meta_decision_agent.execute(
            task_description=task_description,
            current_knowledge=json.dumps(abstraction_result, ensure_ascii=False),
            iteration=iteration,
            remaining_searches=remaining_searches
        )

        abstraction_result['meta_decision'] = meta_decision

        if not meta_decision.get('search_needed', False):
            self.log_info(f"Meta agent decided NO web search needed: {meta_decision.get('rationale', 'No rationale provided')}")
            abstraction_result['web_search_performed'] = False
            abstraction_result['web_search_skipped_reason'] = f"Meta agent decision: {meta_decision.get('rationale', 'Not recommended')}"
            return abstraction_result

        self.log_info(f"Meta agent recommends web search (importance: {meta_decision.get('importance_score', 'N/A')}, "
                     f"confidence: {meta_decision.get('confidence', 'N/A')})")

        search_gaps = meta_decision.get('knowledge_gaps', abstraction_result.get('gap_hypotheses', []))

        if search_gaps:
            abstraction_result = self._perform_web_search_with_gaps(
                abstraction_result, task_description, search_gaps, iteration
            )
        else:
            self.log_info("Meta agent recommended search but no specific gaps identified")
            abstraction_result['web_search_performed'] = False
            abstraction_result['web_search_skipped_reason'] = "No specific knowledge gaps identified for search"

        return abstraction_result

    def _perform_web_search_with_gaps(self, abstraction_result: Dict, task_description: str,
                                    knowledge_gaps: List[str], iteration: int) -> Dict:
        """Perform web search with specific knowledge gaps identified by meta decision agent"""
        if self.web_search_counter and self.web_search_counter['count'] >= self.web_search_counter['max']:
            self.log_info(f"Web search limit reached ({self.web_search_counter['count']}/{self.web_search_counter['max']}), skipping web search")
            abstraction_result['web_search_performed'] = False
            abstraction_result['web_search_skipped_reason'] = f"Search limit reached ({self.web_search_counter['count']}/{self.web_search_counter['max']})"
            return abstraction_result

        self.log_info(f"Performing web search for {len(knowledge_gaps)} knowledge gaps ({self.web_search_counter['count'] + 1}/{self.web_search_counter['max']})")

        search_results = self.web_search_agent.execute(
            task_description=task_description,
            gap_hypotheses=knowledge_gaps,
            iteration=iteration
        )

        if self.web_search_counter:
            self.web_search_counter['count'] += 1
            self.web_search_counter['last_iteration'] = iteration

        abstraction_result['web_search_performed'] = search_results.get('search_performed', False)
        abstraction_result['web_search_results'] = search_results.get('search_results', [])

        if search_results.get('total_results', 0) > 0:
            abstraction_result = self._integrate_search_results(abstraction_result, search_results)

        return abstraction_result

    def _integrate_search_results(self, abstraction_result: Dict, search_results: Dict) -> Dict:
        """Integrate web search results into the abstraction knowledge and re-analyze"""
        self.log_info("Integrating web search results into knowledge")

        retrieved_information = []
        for result in search_results.get('search_results', []):
            if result.get('answer'):
                retrieved_information.append({
                    'query': result['query'],
                    'information': result['answer'],
                    'sources_count': len(result.get('sources', []))
                })

        if retrieved_information:
            abstraction_result['retrieved_information'] = retrieved_information
            abstraction_result = self._refine_knowledge_with_search_results(
                abstraction_result, retrieved_information
            )
            self.log_info(f"Integrated and refined knowledge with {len(retrieved_information)} search results")

        return abstraction_result

    def _refine_knowledge_with_search_results(self, abstraction_result: Dict,
                                            retrieved_information: List[Dict]) -> Dict:
        """Refine the abstraction knowledge based on retrieved web search information"""
        self.log_info("Refining knowledge based on web search findings")

        search_summary = []
        for info in retrieved_information:
            query = info['query']
            information = info['information']
            sources_count = info['sources_count']
            formatted_info = f"=== Search Query: {query} ({sources_count} sources) ===\n{information}\n"
            search_summary.append(formatted_info)

        search_summary_text = "\n".join(search_summary)

        refined_user_message = f"""
            Task knowledge refinement using external web search findings:

            CURRENT KNOWLEDGE:
            - Strategies: {abstraction_result.get('strategies', [])}
            - Principles: {abstraction_result.get('principles', [])}
            - Evaluation Criteria: {abstraction_result.get('evaluation_criteria', [])}

            EXTERNAL KNOWLEDGE FROM WEB SEARCH:
            {search_summary_text}

            REFINEMENT INSTRUCTIONS:
            1. Extract specific techniques, patterns, and methods from the web search results
            2. Incorporate concrete examples into generalized, reusable strategies
            3. Update principles with insights from proven practices and industry standards
            4. Enhance evaluation criteria based on real-world quality indicators found in the search results
            5. Identify any additional knowledge gaps that could benefit from further research

            Focus on actionable insights that can be applied to similar tasks. Transform specific examples
            into general principles while preserving their practical value.

            Return the enhanced knowledge in the same JSON format.
            """

        try:
            refined_response = self.call_llm(refined_user_message)
            refined_knowledge = json.loads(refined_response.strip())

            if refined_knowledge.get('strategies'):
                abstraction_result['strategies'] = refined_knowledge['strategies']
            if refined_knowledge.get('principles'):
                abstraction_result['principles'] = refined_knowledge['principles']
            if refined_knowledge.get('evaluation_criteria'):
                abstraction_result['evaluation_criteria'] = refined_knowledge['evaluation_criteria']

            original_rationale = abstraction_result.get('change_rationale', '')
            abstraction_result['change_rationale'] = (
                f"{original_rationale}. Enhanced and refined with web search findings"
            ).strip('. ')

            self.log_info("Successfully refined knowledge with web search results")

        except (json.JSONDecodeError, Exception) as e:
            self.log_info(f"Failed to refine knowledge with search results: {e}, keeping original")
            original_rationale = abstraction_result.get('change_rationale', '')
            abstraction_result['change_rationale'] = (
                f"{original_rationale}. Integrated with web search findings"
            ).strip('. ')

        return abstraction_result

    def _use_historical_web_knowledge(self, abstraction_result: Dict, task_description: str) -> Dict:
        """Use historical web search knowledge when no new search quota available"""
        self.log_info("Using historical web search knowledge (no search quota available)")

        try:
            import re
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had'
            }
            words = re.findall(r'\b[a-zA-Z]+\b', task_description.lower())
            task_keywords = [word for word in words if len(word) > 2 and word not in stop_words][:5]

            if task_keywords:
                self.log_info(f"Task keywords for historical knowledge matching: {task_keywords}")
                abstraction_result = self._integrate_historical_knowledge(
                    abstraction_result, task_keywords
                )

        except Exception as e:
            self.log_info(f"Failed to use historical web knowledge: {e}")

        return abstraction_result

    def _integrate_historical_knowledge(self, abstraction_result: Dict, task_keywords: List[str]) -> Dict:
        """Integrate historical web search knowledge based on task relevance"""
        if not self.memory:
            self.log_info("No memory access available for historical knowledge")
            return abstraction_result

        self.log_info(f"Looking for historical knowledge relevant to keywords: {task_keywords}")

        try:
            historical_info = self.memory.get_relevant_retrieved_information(task_keywords, limit=2)

            if historical_info and historical_info.strip() != "No retrieved information available.":
                self.log_info("Found relevant historical web search knowledge, integrating...")

                historical_message = f"""
                    Task knowledge refinement using historical web search findings:

                    CURRENT KNOWLEDGE:
                    - Strategies: {abstraction_result.get('strategies', [])}
                    - Principles: {abstraction_result.get('principles', [])}
                    - Evaluation Criteria: {abstraction_result.get('evaluation_criteria', [])}

                    HISTORICAL WEB SEARCH KNOWLEDGE:
                    {historical_info}

                    REFINEMENT INSTRUCTIONS:
                    Since no new web search quota is available, leverage the historical external knowledge to refine current strategies and principles. Extract any relevant patterns, techniques, or insights that could enhance the current knowledge for this task.

                    Transform historical examples into updated, generalized knowledge while maintaining practical value.

                    Return enhanced knowledge in the same JSON format.
                    """

                refined_response = self.call_llm(historical_message)
                refined_knowledge = json.loads(refined_response.strip())

                if refined_knowledge.get('strategies'):
                    abstraction_result['strategies'] = refined_knowledge['strategies']
                if refined_knowledge.get('principles'):
                    abstraction_result['principles'] = refined_knowledge['principles']
                if refined_knowledge.get('evaluation_criteria'):
                    abstraction_result['evaluation_criteria'] = refined_knowledge['evaluation_criteria']

                original_rationale = abstraction_result.get('change_rationale', '')
                abstraction_result['change_rationale'] = (
                    f"{original_rationale}. Enhanced with historical web search knowledge"
                ).strip('. ')

                self.log_info("Successfully integrated historical web search knowledge")

            else:
                self.log_info("No relevant historical web search knowledge found")
                original_rationale = abstraction_result.get('change_rationale', '')
                abstraction_result['change_rationale'] = (
                    f"{original_rationale}. Checked for historical web search knowledge"
                ).strip('. ')

        except Exception as e:
            self.log_info(f"Failed to integrate historical knowledge: {e}")
            original_rationale = abstraction_result.get('change_rationale', '')
            abstraction_result['change_rationale'] = (
                f"{original_rationale}. Attempted historical knowledge integration"
            ).strip('. ')

        return abstraction_result
