"""Turn scheduling abstractions for multi-LLM conversations."""

import random
from abc import ABC, abstractmethod
from typing import Iterator, List


class TurnSchedule(ABC):
    """Abstract base class for infinite iterator that yields speaker lists for each round."""

    def __init__(self, agent_ids: List[int]):
        """Initialize with list of agent IDs this schedule will manage."""
        self.agent_ids = agent_ids.copy()

    def __iter__(self) -> Iterator[List[int]]:
        """Return self as the iterator."""
        return self

    @abstractmethod
    def __next__(self) -> List[int]:
        """Return the next list of speakers for this round."""
        ...


class BalancedTurnSchedule(TurnSchedule):
    """Round-robin scheduling where each agent speaks once per round."""

    def __init__(self, agent_ids: List[int], randomize_order: bool = False):
        super().__init__(agent_ids)
        if randomize_order:
            random.shuffle(self.agent_ids)

    def __next__(self) -> List[int]:
        """Always return the same ordered list of all agents."""
        return self.agent_ids.copy()


class RandomSubsetTurnSchedule(TurnSchedule):
    """Unbalanced scheduling where the same random subset speaks each round."""

    def __init__(self, agent_ids: List[int], num_speakers: int, allow_repeats: bool = False):
        super().__init__(agent_ids)
        self.allow_repeats = allow_repeats

        # Draw the subset once and reuse it
        if allow_repeats:
            self.speakers = random.choices(agent_ids, k=num_speakers)
        else:
            k = min(num_speakers, len(agent_ids))
            self.speakers = random.sample(agent_ids, k)

    def __next__(self) -> List[int]:
        """Always return the same random subset."""
        return self.speakers.copy()


class PerAgentTurnSchedule(TurnSchedule):
    """Future extension: agents propose their own turn schedules."""

    def __init__(self, agent_ids: List[int], proposer_id: int, proposed_speakers: List[int]):
        super().__init__(agent_ids)
        self.proposer_id = proposer_id
        # Only keep proposed speakers that are available
        self.speakers = ([speaker for speaker in proposed_speakers if speaker in agent_ids]
                        if all(speaker in agent_ids for speaker in proposed_speakers)
                        else [proposer_id] if proposer_id in agent_ids else [])

    def __next__(self) -> List[int]:
        """Always return the same proposed speakers."""
        return self.speakers.copy()