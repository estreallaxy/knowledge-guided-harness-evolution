"""Parameterized ReflexionAgent class shared across all CoT Direct scripts.

Also provides standalone utility functions ``parse_post_exec_update`` and
``fetch_relevant_memory_chunks`` for use outside the agent class.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Callable, Tuple

from loguru import logger
from aspec.llm import BaseLLM
from aspec.controller.utils import get_sentence_embedding
from experiments.lib.eval_utils import retry_with_backoff


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_post_exec_update(raw_text: str) -> Tuple[str, str]:
    """Extract ``(decision, updated_markdown)`` from model output.

    Supports both JSON and XML formats.  Returns ``("", "")`` on failure.
    """
    text = str(raw_text or "").strip()

    # Strip code fences
    if text.startswith("```"):
        nl = text.find("\n")
        if nl != -1:
            text = text[nl + 1 :]
    end_idx = text.rfind("```")
    if end_idx != -1:
        text = text[:end_idx]
    text = text.strip()

    # Try JSON first
    try:
        j = json.loads(text)
        if isinstance(j, dict):
            obj = j.get("memory_update", j)
            dec = str(obj.get("decision", "")).strip().lower()
            upd = obj.get("updated_markdown", "")
            if isinstance(upd, (dict, list)):
                upd = json.dumps(upd, ensure_ascii=False)
            else:
                upd = str(upd)
            dec = _normalize_decision(dec)
            upd = _strip_fences(upd)
            return dec, upd
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    # XML fallback
    m_dec = re.search(r"<decision>\s*([\s\S]*?)\s*</decision>", text, re.IGNORECASE)
    decision = m_dec.group(1).strip().lower() if m_dec else ""

    m_upd = re.search(
        r"<updated_markdown>\s*(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?\s*</updated_markdown>",
        text,
        re.IGNORECASE,
    )
    updated = m_upd.group(1).strip() if m_upd else ""

    return _normalize_decision(decision), _strip_fences(updated)


# ---------------------------------------------------------------------------
# Memory retrieval
# ---------------------------------------------------------------------------


def fetch_relevant_memory_chunks(
    memory_file: Path,
    query_text: str,
    *,
    top_k: int = 2,
    max_chunk_chars: int = 800,
    cosine_threshold: float = 0.4,
    max_total_chars: int = 1500,
    header_to_skip: str = "",
) -> str:
    """Semantic search over a specialist memory file.

    Returns a string of the top-k most relevant chunks joined by blank
    lines, or ``""`` if nothing passes the cosine threshold.
    """
    try:
        if not memory_file.exists():
            return ""
        text = memory_file.read_text(encoding="utf-8", errors="ignore").strip()
        if not text:
            return ""

        chunks = _parse_chunks(text)

        # Filter
        filtered = []
        skip = header_to_skip.lower().strip()
        for title, body in chunks:
            if skip and title.lower().strip() == skip:
                continue
            if not body.strip():
                continue
            filtered.append((title, body))

        if not filtered:
            return ""

        # Prefer structured entries
        structured = [
            (t, b) for t, b in filtered if "structured memory entry" in t.lower() or "problem pattern:" in b.lower()
        ]
        if structured:
            filtered = structured

        # Semantic ranking
        q_emb = get_sentence_embedding(str(query_text)[:1000])
        q_emb = q_emb / (q_emb.norm(p=2) + 1e-8)

        scored = []
        for title, body in filtered:
            chunk_text = f"{title}\n{body}"[:max_chunk_chars]
            c_emb = get_sentence_embedding(chunk_text)
            c_emb = c_emb / (c_emb.norm(p=2) + 1e-8)
            cos = float((q_emb * c_emb).sum().item())
            scored.append((cos, title, body))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored or scored[0][0] < cosine_threshold:
            return ""

        parts = [f"{t}\n{b}".strip() for _, t, b in scored[:top_k]]
        result = "\n\n".join(parts)
        if len(result) > max_total_chars:
            result = result[:max_total_chars] + "...[truncated]"
        return result
    except Exception as e:
        logger.warning(f"Failed to fetch relevant memory chunks from {memory_file}: {e}")
        return ""


# ---------------------------------------------------------------------------
# ReflexionAgent class
# ---------------------------------------------------------------------------


class ReflexionAgent:
    """A generic Reflexion agent with memory and self-reflection capabilities.

    Parameterized by ``dataset_name`` and ``domain_hint`` so the same class
    can be reused across MATH, GPQA, HumanEval, MMLU, and SciCode.
    """

    def __init__(
        self,
        llm: BaseLLM,
        memory_file: str = "reflexion_memory.txt",
        dataset_name: str = "default",
        domain_hint: str = "problems",
    ) -> None:
        self.llm = llm
        self.memory_file = Path(memory_file)
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.dataset_name = dataset_name
        self.domain_hint = domain_hint

        if not self.memory_file.exists():
            self.memory_file.write_text(f"# Reflexion Agent Memory - {dataset_name}\n\n", encoding="utf-8")

    def _parse_post_exec_update(self, raw_text: str) -> Tuple[str, str]:
        return parse_post_exec_update(raw_text)

    async def _fetch_relevant_memory_chunks(self, query_text: str, top_k: int = 2, max_chunk_chars: int = 800) -> str:
        return fetch_relevant_memory_chunks(
            self.memory_file,
            query_text,
            top_k=top_k,
            max_chunk_chars=max_chunk_chars,
            header_to_skip=f"# reflexion agent memory - {self.dataset_name}",
        )

    async def solve_with_reflection(
        self,
        problem: str,
        ground_truth: str = "",
        format_prompt_fn: Callable[[str, str], str] | None = None,
        score_fn: Callable[[str, str], Tuple[float, str]] | None = None,
        **kwargs: Any,
    ) -> Tuple[str, float]:
        """Solve a problem with memory-augmented reasoning and post-execution reflection.

        Parameters
        ----------
        problem : str
                The problem text (already formatted with choices if applicable).
        ground_truth : str
                Ground truth for scoring and reflection.
        format_prompt_fn : callable, optional
                If provided, called as ``format_prompt_fn(problem, memory_injection)``
                to build the solving prompt. Otherwise a generic prompt is used.
        score_fn : callable, optional
                If provided, called as ``score_fn(ground_truth, response)`` returning
                ``(score, predicted_answer)``. Used for reflection feedback.
        **kwargs
                Extra keyword arguments forwarded to ``_reflect_and_update_memory``.
        """
        memory_context = await self._fetch_relevant_memory_chunks(problem)

        memory_injection = ""
        if memory_context:
            print(f"Injecting memory context: {memory_context}")
            memory_injection = (
                f"\n\nRelevant memory from past similar problems:\n{memory_context}\n"
                "Use this memory to inform your approach.\n"
            )

        if format_prompt_fn is not None:
            solving_prompt = format_prompt_fn(problem, memory_injection)
        else:
            solving_prompt = (
                f"You are a helpful assistant with access to memory from past {self.domain_hint}. "
                f"Think step-by-step to solve the problem.\n"
                f"{memory_injection}\n"
                f"Problem:\n{problem}\n"
            )

        response = await retry_with_backoff(self.llm.aask, solving_prompt)

        score = 0.0
        predicted_answer = ""
        if score_fn is not None and ground_truth:
            score, predicted_answer = score_fn(ground_truth, response)
        elif ground_truth:
            score = 0.0
            predicted_answer = response

        if ground_truth:
            await self._reflect_and_update_memory(
                problem, response, ground_truth, score, predicted_answer=predicted_answer, **kwargs
            )

        return response, self.llm.cost_manager.total_cost

    async def _reflect_and_update_memory(
        self,
        problem: str,
        final_answer: str,
        ground_truth: str,
        score: float,
        predicted_answer: str = "",
        **kwargs: Any,
    ) -> None:
        """Perform post-execution reflection and update memory if needed."""
        reflection_prompt = f"""You are a helpful assistant with a memory system. After solving a problem, review your performance and decide if your memory should be updated.

Inputs:
- Problem: {problem}
- Score: {score} (1.0 = correct, 0.0 = incorrect)
- Ground truth: {ground_truth}
- Your answer: {predicted_answer or final_answer}

Instructions:
1. Analyze your approach: What worked well? What went wrong?
2. Identify if there's a reusable insight or pattern that could help with future similar {self.domain_hint}
3. Update memory only if you can add an abstract, reusable insight
4. Focus on problem patterns, solution strategies, common pitfalls, and general rules

Output format (XML only):
<memory_update>
<decision>update|skip</decision>
<rationale><![CDATA[
Brief reasoning for your decision.
]]></rationale>
<updated_markdown><![CDATA[
If decision=update, provide a structured memory entry with these sections:
## Structured Memory Entry

**Problem Pattern:** [Describe the type/pattern of problem - keep general, <=150 chars]

**Solution Strategy:** [Describe the approach that works best - keep general, <=150 chars]

**Common Pitfalls:** [What mistakes to avoid - keep general, <=150 chars]

**Key Insight:** [The most important takeaway for future similar problems - keep general, <=150 chars]
]]></updated_markdown>
</memory_update>"""

        try:
            reflection_response = await retry_with_backoff(
                self.llm.aask, reflection_prompt, max_retries=3, base_delay=1.0
            )
            decision, updated_md = self._parse_post_exec_update(reflection_response)

            if decision == "update" and updated_md:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                memory_block = f"\n\n---\n*Added: {timestamp}*\n\n{updated_md.strip()}\n"

                with open(self.memory_file, "a", encoding="utf-8") as f:
                    f.write(memory_block)

                print("Memory updated with new insight")
            else:
                print(f"No memory update (decision: {decision})")

        except Exception as e:
            logger.error(f"Error during reflection: {e}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _normalize_decision(dec: str) -> str:
    if "update" in dec:
        return "update"
    if "skip" in dec:
        return "skip"
    return dec


def _strip_fences(text: str) -> str:
    text = re.sub(r"^\s*```[a-zA-Z]*\s*\n?", "", text.strip())
    text = re.sub(r"\n?\s*```\s*$", "", text)
    return text


def _parse_chunks(text: str) -> list[Tuple[str, str]]:
    lines = text.splitlines()
    chunks: list[Tuple[str, str]] = []
    cur_title: str | None = None
    cur_lines: list[str] = []
    for line in lines:
        if re.match(r"^#{1,6}\s+", line):
            if cur_title is not None:
                chunks.append((cur_title, "\n".join(cur_lines).strip()))
            cur_title = line.strip()
            cur_lines = []
        else:
            cur_lines.append(line)
    if cur_title is None:
        return [("# Memory", text.strip())]
    chunks.append((cur_title, "\n".join(cur_lines).strip()))
    return chunks
