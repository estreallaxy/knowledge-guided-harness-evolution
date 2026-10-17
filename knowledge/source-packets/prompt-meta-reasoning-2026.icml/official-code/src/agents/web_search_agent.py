"""
Web Search agent for performing web search using LinkUp API
"""

import json
from typing import Dict, List
from .base_agent import BaseAgent


class WebSearchAgent(BaseAgent):
    """Agent responsible for web search using LinkUp API"""

    def __init__(self, system_prompt: Dict, user_message: Dict, openai_client, linkup_client, config: Dict):
        super().__init__(system_prompt, user_message, openai_client, config)
        self.linkup_client = linkup_client
        if self.linkup_client:
            self.log_info("LinkUp client received")
        else:
            self.log_info("No LinkUp client provided — web search will be unavailable")

    def execute(self, task_description: str, gap_hypotheses: List[str],
                iteration: int = 0) -> Dict:
        """
        Perform web search based on gap hypotheses

        Args:
            task_description: Description of the task being performed
            gap_hypotheses: List of knowledge gaps that might need web search
            iteration: Current iteration number

        Returns:
            Dictionary with search results and sourced answers
        """
        self.log_info(f"Starting web search for iteration {iteration}")

        if not self.linkup_client:
            self.log_info("LinkUp client not available, returning empty results")
            return {
                "search_performed": False,
                "search_results": [],
                "error": "LinkUp client not available"
            }

        if not gap_hypotheses:
            self.log_info("No gap hypotheses provided, skipping web search")
            return {
                "search_performed": False,
                "search_results": [],
                "reason": "No knowledge gaps identified"
            }

        search_queries = self._generate_search_queries(task_description, gap_hypotheses)

        search_results = []
        for query in search_queries:
            try:
                self.log_info(f"Performing web search: {query}")

                response = self.linkup_client.search(
                    query=query,
                    depth="standard",
                    output_type="sourcedAnswer",
                    include_images=False,
                )

                if response and hasattr(response, 'answer') and response.answer:
                    search_results.append({
                        "query": query,
                        "answer": response.answer,
                    })
                    self.log_info(f"Successfully retrieved search result for: {query}")
                else:
                    self.log_info(f"No valid response for query: {query}")

            except Exception as e:
                self.log_info(f"Error performing search for '{query}': {e}")
                search_results.append({
                    "query": query,
                    "error": str(e),
                    "answer": None,
                    "sources": []
                })

        return {
            "search_performed": True,
            "search_results": search_results,
            "total_results": len([r for r in search_results if r.get('answer')])
        }

    def _generate_search_queries(self, task_description: str, gap_hypotheses: List[str]) -> List[str]:
        """Generate one most important search query based on gap hypotheses"""
        self.log_info("Generating the most important search query from gap hypotheses")

        user_message = self.format_user_message(
            task_description=task_description,
            gap_hypotheses=self._format_list_items(gap_hypotheses)
        )

        response = self.call_llm(user_message)

        try:
            queries_data = json.loads(response.strip())
            if isinstance(queries_data, dict) and 'query' in queries_data:
                query = queries_data['query']
                queries = [query] if query else []
            elif isinstance(queries_data, dict) and 'queries' in queries_data:
                queries_list = queries_data['queries']
                queries = [queries_list[0]] if queries_list else []
            elif isinstance(queries_data, str):
                queries = [queries_data.strip()]
            else:
                lines = [line.strip() for line in response.strip().split('\n')
                        if line.strip() and not line.strip().startswith('#')]
                queries = [lines[0]] if lines else []

            if queries:
                self.log_info(f"Generated most important search query: {queries[0]}")
            else:
                self.log_info("No valid search query generated")
            return queries

        except json.JSONDecodeError:
            lines = [line.strip() for line in response.strip().split('\n')
                    if line.strip() and not line.strip().startswith('#')]
            queries = [lines[0]] if lines else []
            if queries:
                self.log_info(f"Generated search query (fallback parsing): {queries[0]}")
            return queries
