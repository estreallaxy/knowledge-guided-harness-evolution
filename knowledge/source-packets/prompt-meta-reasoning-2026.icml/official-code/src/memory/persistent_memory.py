"""
Memory module for MR.PEA agent
Handles persistent storage and retrieval of agent memory components
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MemoryState:
    """Data structure for agent memory state"""
    prompt_pool: Dict[int, str] = field(default_factory=dict)  # prompt_id -> prompt
    knowledge_memory: List[str] = field(default_factory=list)
    example_memory: List[str] = field(default_factory=list)
    ranking_scores: Dict[int, float] = field(default_factory=dict)  # prompt_id -> score
    feedback_memory: List[str] = field(default_factory=list)
    retrieved_information: List[Dict[str, Any]] = field(default_factory=list)  # Web search results

    # Metadata
    task_name: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class PersistentMemory:
    """Persistent memory manager for MR.PEA agent"""

    def __init__(self, memory_dir: str = "memory", task_name: str = "default"):
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.memory_dir = Path(f"{memory_dir}/{task_name}/{current_time}")
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.task_name = task_name

        self.knowledge_dir = self.memory_dir / "knowledge"
        self.examples_dir = self.memory_dir / "examples"
        self.prompts_dir = self.memory_dir / "prompts"
        self.feedback_dir = self.memory_dir / "feedback"

        for dir_path in [self.knowledge_dir, self.examples_dir, self.prompts_dir, self.feedback_dir]:
            dir_path.mkdir(exist_ok=True)

        self.state = MemoryState(task_name=task_name)
        self.memory_file = self.memory_dir / f"{task_name}_memory.json"

        self.load_memory()

    def save_memory(self):
        """Save complete memory state to file"""
        self.state.updated_at = datetime.now().isoformat()

        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.state), f, indent=2, ensure_ascii=False)

            self._save_knowledge_memory()

            logger.info(f"Memory saved to {self.memory_file}")

        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def load_memory(self):
        """Load memory state from file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.state = MemoryState(**data)

                self._load_knowledge_memory()

                logger.info(f"Memory loaded from {self.memory_file}")
            else:
                logger.info("No existing memory found, starting fresh")

        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            self.state = MemoryState(task_name=self.task_name)

    def _save_knowledge_memory(self):
        """Save knowledge memory to separate files"""
        for i, knowledge in enumerate(self.state.knowledge_memory):
            knowledge_file = self.knowledge_dir / f"{self.task_name}_knowledge_{i:03d}.txt"
            try:
                with open(knowledge_file, 'w', encoding='utf-8') as f:
                    if isinstance(knowledge, (dict, list)):
                        f.write(json.dumps(knowledge, indent=2, ensure_ascii=False))
                    else:
                        f.write(str(knowledge))
            except Exception as e:
                logger.error(f"Failed to save knowledge {i}: {e}")

    def _load_knowledge_memory(self):
        """Load knowledge memory from separate files"""
        knowledge_files = sorted(self.knowledge_dir.glob(f"{self.task_name}_knowledge_*.txt"))
        loaded_knowledge = []

        for knowledge_file in knowledge_files:
            try:
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge = f.read()
                    loaded_knowledge.append(knowledge)
            except Exception as e:
                logger.error(f"Failed to load knowledge from {knowledge_file}: {e}")

        if loaded_knowledge:
            self.state.knowledge_memory = loaded_knowledge

    def add_prompt(self, prompt: str, iteration: int = 0) -> int:
        """Add a prompt and return its ID (iteration number)"""
        prompt_id = iteration if iteration >= 0 else len(self.state.prompt_pool)
        self.state.prompt_pool[prompt_id] = prompt

        prompt_file = self.prompts_dir / f"{self.task_name}_prompt_{prompt_id:03d}.txt"
        try:
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
        except Exception as e:
            logger.error(f"Failed to save prompt {prompt_id}: {e}")

        self.save_memory()
        return prompt_id

    def add_knowledge(self, knowledge):
        """Add knowledge to memory"""
        self.state.knowledge_memory.append(knowledge)

        knowledge_id = len(self.state.knowledge_memory) - 1
        knowledge_file = self.knowledge_dir / f"{self.task_name}_knowledge_{knowledge_id:03d}.txt"
        try:
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                if isinstance(knowledge, (dict, list)):
                    f.write(json.dumps(knowledge, indent=2, ensure_ascii=False))
                else:
                    f.write(str(knowledge))
        except Exception as e:
            logger.error(f"Failed to save knowledge {knowledge_id}: {e}")

        self.save_memory()

    def add_examples(self, examples):
        """Add examples to memory and save each to a separate file"""

        self.state.example_memory.append(examples)

        example_id = len(self.state.example_memory) - 1
        example_file = self.examples_dir / f"{self.task_name}_example_{example_id:03d}.json"
        try:
            with open(example_file, 'w', encoding='utf-8') as f:
                if isinstance(examples, (dict, list)):
                    f.write(json.dumps(examples, indent=2, ensure_ascii=False))
                else:
                    f.write(str(examples))
        except Exception as e:
            logger.error(f"Failed to save example {example_id}: {e}")
        self.save_memory()

    def add_feedback(self, feedback: str):
        """Add feedback to memory"""
        self.state.feedback_memory.append(feedback)

        feedback_id = len(self.state.feedback_memory) - 1
        feedback_file = self.feedback_dir / f"{self.task_name}_feedback_{feedback_id:03d}.txt"
        try:
            with open(feedback_file, 'w', encoding='utf-8') as f:
                f.write(feedback)
        except Exception as e:
            logger.error(f"Failed to save feedback {feedback_id}: {e}")

        self.save_memory()

    def update_ranking_scores(self, scores: Dict[int, float]):
        """Update ranking scores"""
        self.state.ranking_scores = scores.copy()
        self.save_memory()
        logger.info(f"Ranking scores updated: {self.state.ranking_scores}")

    def get_prompt(self, prompt_id: int) -> Optional[str]:
        """Get prompt by ID"""
        return self.state.prompt_pool.get(prompt_id)

    def get_all_knowledge(self) -> str:
        """Get all knowledge as a single string"""
        return "\n\n".join(self.state.knowledge_memory)

    def get_latest_knowledge(self) -> str:
        """Get the most recently added knowledge"""
        return self.state.knowledge_memory[-1] if self.state.knowledge_memory else ""

    def get_all_examples(self) -> str:
        """Get all examples"""
        return self.state.example_memory

    def get_latest_example(self) -> str:
        """Get the most recently added example"""
        return self.state.example_memory[-1] if self.state.example_memory else ""

    def get_recent_examples(self, limit: int = 3) -> str:
        """Get the most recent N examples formatted for example generation"""
        if not self.state.example_memory:
            return "No recent examples available."

        num_examples = min(limit, len(self.state.example_memory))
        recent_examples = self.state.example_memory[-num_examples:]

        formatted_examples = []
        for i, example in enumerate(recent_examples, 1):
            if isinstance(example, (dict, list)):
                example_text = json.dumps(example, indent=2, ensure_ascii=False)
            else:
                example_text = str(example)
            formatted_examples.append(f"Example {i}:\n{example_text}")

        return "\n\n".join(formatted_examples)

    def get_latest_feedback(self) -> str:
        """Get the most recent feedback"""
        return self.state.feedback_memory[-1] if self.state.feedback_memory else ""

    def get_best_prompt_id(self) -> int:
        """Get the ID of the best-ranked prompt"""
        if not self.state.ranking_scores:
            return 0
        return max(self.state.ranking_scores.keys(),
                  key=lambda x: self.state.ranking_scores[x])

    def get_historical_prompts_with_scores(self, limit: int = 5) -> str:
        """Get top N historical prompts with their scores formatted for prompt refinement"""
        if not self.state.prompt_pool or not self.state.ranking_scores:
            return "No historical prompts available."

        sorted_prompts = sorted(
            self.state.ranking_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        num_prompts = min(limit, len(sorted_prompts))
        selected_prompts = sorted_prompts[:num_prompts]

        formatted_prompts = []
        for i, (prompt_id, score) in enumerate(selected_prompts, 1):
            prompt_text = self.state.prompt_pool.get(prompt_id, "Prompt not found")
            formatted_prompts.append(f"{i}. Prompt ID {prompt_id} (Score: {score:.3f}):\n{prompt_text}")

        return "\n\n".join(formatted_prompts)

    def add_retrieved_information(self, retrieved_info: List[Dict[str, Any]]):
        """Add retrieved information from web search to memory"""
        if not retrieved_info:
            return

        timestamped_info = []
        current_time = datetime.now().isoformat()

        for info in retrieved_info:
            info_copy = dict(info)
            info_copy['retrieved_at'] = current_time
            timestamped_info.append(info_copy)

        self.state.retrieved_information.extend(timestamped_info)
        logger.info(f"Added {len(retrieved_info)} retrieved information items to memory")

        self.save_memory()

    def get_retrieved_information(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent retrieved information"""
        return self.state.retrieved_information[-limit:]

    def get_retrieved_information_for_prompt_refinement(self, limit: int = 5) -> str:
        """Get retrieved information formatted for prompt refinement"""
        recent_info = self.get_retrieved_information(limit)

        if not recent_info:
            return "No retrieved information available."

        formatted_info = []
        for i, info in enumerate(recent_info, 1):
            query = info.get('query', 'Unknown query')
            information = info.get('information', 'No information')
            sources_count = info.get('sources_count', 0)

            formatted_section = f"=== Retrieved Knowledge {i} ===\n"
            formatted_section += f"Query: {query}\n"
            formatted_section += f"Sources: {sources_count} sources\n"
            formatted_section += f"Content:\n{self._format_retrieved_content(information)}"

            formatted_info.append(formatted_section)

        return "\n\n".join(formatted_info)

    def get_relevant_retrieved_information(self, task_keywords: List[str], limit: int = 3) -> str:
        """Get retrieved information relevant to specific task keywords"""
        all_info = self.state.retrieved_information

        if not all_info:
            return "No retrieved information available."

        scored_info = []
        for info in all_info:
            score = self._calculate_relevance_score(info, task_keywords)
            if score > 0:
                scored_info.append((score, info))

        scored_info.sort(key=lambda x: x[0], reverse=True)
        relevant_info = [info for score, info in scored_info[:limit]]

        if not relevant_info:
            return self.get_retrieved_information_for_prompt_refinement(limit)

        formatted_info = []
        for i, info in enumerate(relevant_info, 1):
            query = info.get('query', 'Unknown query')
            information = info.get('information', 'No information')
            sources_count = info.get('sources_count', 0)

            formatted_section = f"=== Relevant Knowledge {i} ===\n"
            formatted_section += f"Query: {query}\n"
            formatted_section += f"Sources: {sources_count} sources\n"
            formatted_section += f"Content:\n{self._format_retrieved_content(information)}"

            formatted_info.append(formatted_section)

        return "\n\n".join(formatted_info)

    def _calculate_relevance_score(self, info: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate relevance score for retrieved information based on keywords"""
        query = info.get('query', '').lower()
        information = info.get('information', '').lower()

        score = 0.0

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in query:
                score += 2.0
            if keyword_lower in information:
                score += 1.0

        return score

    def _format_retrieved_content(self, content: str, max_length: int = 1500) -> str:
        """Format retrieved content with intelligent truncation and structure preservation"""
        if not content:
            return "No information available"

        if len(content) <= max_length:
            return content

        lines = content.split('\n')
        formatted_lines = []
        current_length = 0

        for line in lines:
            if current_length + len(line) + 1 > max_length:
                if current_length < max_length * 0.5:
                    remaining_space = max_length - current_length - 20
                    if remaining_space > 50:
                        formatted_lines.append(line[:remaining_space] + "...")
                        break
                else:
                    formatted_lines.append("... [content truncated for length]")
                    break
            else:
                formatted_lines.append(line)
                current_length += len(line) + 1

        return '\n'.join(formatted_lines)

    def export_memory(self, export_path: str):
        """Export complete memory to a single file"""
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "memory_state": asdict(self.state),
            "export_timestamp": datetime.now().isoformat(),
            "task_name": self.task_name
        }

        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Memory exported to {export_file}")
        except Exception as e:
            logger.error(f"Failed to export memory: {e}")

    def clear_memory(self):
        """Clear all memory data"""
        self.state = MemoryState(task_name=self.task_name)

        for dir_path in [self.knowledge_dir, self.examples_dir, self.prompts_dir, self.feedback_dir]:
            for file_path in dir_path.glob(f"{self.task_name}_*"):
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.error(f"Failed to remove {file_path}: {e}")

        if self.memory_file.exists():
            try:
                self.memory_file.unlink()
            except Exception as e:
                logger.error(f"Failed to remove {self.memory_file}: {e}")

        logger.info("Memory cleared")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        return {
            "task_name": self.task_name,
            "prompts_count": len(self.state.prompt_pool),
            "knowledge_count": len(self.state.knowledge_memory),
            "examples_count": len(self.state.example_memory),
            "feedback_count": len(self.state.feedback_memory),
            "created_at": self.state.created_at,
            "updated_at": self.state.updated_at,
            "memory_file_size": self.memory_file.stat().st_size if self.memory_file.exists() else 0
        }
