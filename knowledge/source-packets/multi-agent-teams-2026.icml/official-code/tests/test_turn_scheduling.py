"""Tests for turn scheduling iterators."""

import random
from teamwork.scheduling import BalancedTurnSchedule, RandomSubsetTurnSchedule, PerAgentTurnSchedule


def test_balanced_turn_schedule_consistent_order():
    """Test that BalancedTurnSchedule returns the same order each round."""
    agent_ids = [1, 2, 3, 4]
    schedule = BalancedTurnSchedule(agent_ids)

    # Get several rounds
    rounds = [next(schedule) for _ in range(5)]

    # All rounds should be identical
    for round_speakers in rounds:
        assert round_speakers == agent_ids

    # Verify it's a copy, not the same reference
    first_round = next(schedule)
    first_round.append(999)
    second_round = next(schedule)
    assert 999 not in second_round


def test_balanced_turn_schedule_randomized():
    """Test that randomized BalancedTurnSchedule maintains consistent order."""
    agent_ids = [1, 2, 3, 4]

    # Set seed for reproducible test
    random.seed(42)
    schedule = BalancedTurnSchedule(agent_ids, randomize_order=True)

    # Get several rounds
    rounds = [next(schedule) for _ in range(5)]

    # All rounds should be identical to each other
    first_round = rounds[0]
    for round_speakers in rounds[1:]:
        assert round_speakers == first_round

    # Should contain all agents
    assert set(first_round) == set(agent_ids)


def test_random_subset_turn_schedule_consistent():
    """Test that RandomSubsetTurnSchedule returns the same subset each round."""
    agent_ids = [1, 2, 3, 4, 5]

    # Set seed for reproducible test
    random.seed(42)
    schedule = RandomSubsetTurnSchedule(agent_ids, num_speakers=3)

    # Get several rounds
    rounds = [next(schedule) for _ in range(5)]

    # All rounds should be identical
    first_round = rounds[0]
    for round_speakers in rounds[1:]:
        assert round_speakers == first_round

    # Should have exactly 3 speakers
    assert len(first_round) == 3

    # All speakers should be from available agents
    assert all(speaker in agent_ids for speaker in first_round)


def test_random_subset_with_repeats():
    """Test RandomSubsetTurnSchedule with allow_repeats=True."""
    agent_ids = [1, 2]

    # Set seed for reproducible test
    random.seed(42)
    schedule = RandomSubsetTurnSchedule(agent_ids, num_speakers=5, allow_repeats=True)

    # Get several rounds
    rounds = [next(schedule) for _ in range(3)]

    # All rounds should be identical
    first_round = rounds[0]
    for round_speakers in rounds[1:]:
        assert round_speakers == first_round

    # Should have exactly 5 speakers (with repeats allowed)
    assert len(first_round) == 5

    # All speakers should be from available agents
    assert all(speaker in agent_ids for speaker in first_round)


def test_proposed_turn_schedule():
    """Test ProposedTurnSchedule with valid proposal."""
    agent_ids = [1, 2, 3, 4]
    proposer_id = 2
    proposed_speakers = [2, 4]

    schedule = PerAgentTurnSchedule(agent_ids, proposer_id, proposed_speakers)

    # Get several rounds
    rounds = [next(schedule) for _ in range(3)]

    # All rounds should be identical
    for round_speakers in rounds:
        assert round_speakers == proposed_speakers


def test_proposed_turn_schedule_fallback():
    """Test ProposedTurnSchedule fallback when proposal is invalid."""
    agent_ids = [1, 2, 3]
    proposer_id = 2
    proposed_speakers = [2, 4, 5]  # 4 and 5 are not available

    schedule = PerAgentTurnSchedule(agent_ids, proposer_id, proposed_speakers)

    # Should fallback to just the proposer
    rounds = [next(schedule) for _ in range(3)]

    for round_speakers in rounds:
        assert round_speakers == [proposer_id]


def test_turn_schedule_iterator_protocol():
    """Test that schedules properly implement iterator protocol."""
    agent_ids = [1, 2, 3]

    # Test that we can use iter() and next()
    schedule = BalancedTurnSchedule(agent_ids)
    iterator = iter(schedule)

    # Should be able to call next() multiple times
    first = next(iterator)
    second = next(iterator)

    assert first == agent_ids
    assert second == agent_ids

    # Should also work directly with next() on the schedule
    third = next(schedule)
    assert third == agent_ids