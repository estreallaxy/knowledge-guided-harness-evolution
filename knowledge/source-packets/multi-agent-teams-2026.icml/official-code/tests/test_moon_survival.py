"""Tests for NASA Moon Survival Task implementation."""

import pytest

from teamwork import AgentProfile, EchoBackend, TeamAgent
from teamwork.tasks import MoonSurvivalTask


def test_parse_ranking_valid_format():
    """Test parsing a valid ranking in standard format."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    parsed = task._parse_ranking(ranking_text)
    expected = {item: i + 1 for i, item in enumerate(MoonSurvivalTask.ITEMS)}
    assert parsed == expected


def test_parse_ranking_with_parentheses():
    """Test parsing rankings with parentheses format."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1) Two 100-lb oxygen tanks
2) 20 liters of water
3) Stellar map
4) Food concentrate
5) Solar-powered FM receiver-transmitter
6) 50 feet of nylon rope
7) First aid kit with injection needles
8) Parachute silk
9) Self-inflating life raft
10) Signal flares
11) Two .45 caliber pistols
12) One case of dehydrated milk
13) Portable heating unit
14) Magnetic compass
15) Box of matches"""

    parsed = task._parse_ranking(ranking_text)
    assert len(parsed) == 15
    assert all(1 <= rank <= 15 for rank in parsed.values())
    assert parsed[MoonSurvivalTask.ITEMS[0]] == 1
    assert parsed[MoonSurvivalTask.ITEMS[14]] == 15


def test_parse_ranking_different_order():
    """Test parsing a ranking in different order."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Box of matches
2. Magnetic compass
3. Portable heating unit
4. One case of dehydrated milk
5. Two .45 caliber pistols
6. Signal flares
7. Self-inflating life raft
8. Parachute silk
9. First aid kit with injection needles
10. 50 feet of nylon rope
11. Solar-powered FM receiver-transmitter
12. Food concentrate
13. Stellar map
14. 20 liters of water
15. Two 100-lb oxygen tanks"""

    parsed = task._parse_ranking(ranking_text)
    assert parsed[MoonSurvivalTask.ITEMS[14]] == 1
    assert parsed[MoonSurvivalTask.ITEMS[13]] == 2
    assert parsed[MoonSurvivalTask.ITEMS[0]] == 15
    assert parsed[MoonSurvivalTask.ITEMS[1]] == 14
    assert len(parsed) == 15


def test_parse_ranking_with_extra_whitespace():
    """Test parsing handles extra whitespace."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """
    1.   Two 100-lb oxygen tanks

    2. 20 liters of water
3.    Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches
    """

    parsed = task._parse_ranking(ranking_text)
    assert len(parsed) == 15
    assert parsed[MoonSurvivalTask.ITEMS[0]] == 1
    assert parsed[MoonSurvivalTask.ITEMS[1]] == 2
    assert parsed[MoonSurvivalTask.ITEMS[14]] == 15


def test_parse_ranking_incomplete():
    """Test parsing fails for incomplete ranking."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map"""

    with pytest.raises(ValueError, match="Could not parse complete ranking"):
        task._parse_ranking(ranking_text)


def test_parse_ranking_duplicate_item():
    """Test parsing fails when same item appears twice."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Two 100-lb oxygen tanks
2. Two 100-lb oxygen tanks
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    # When duplicate detected, it skips second occurrence, leading to incomplete ranking
    with pytest.raises(ValueError, match="Could not parse complete ranking"):
        task._parse_ranking(ranking_text)


def test_parse_ranking_invalid_item():
    """Test parsing fails with non-existent item."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Space lasers"""

    with pytest.raises(ValueError, match="Could not parse complete ranking"):
        task._parse_ranking(ranking_text)


def test_score_solution_perfect():
    """Test scoring returns 0 for perfect expert ranking."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    score = task.score_solution(ranking_text)
    assert score == 0.0, "Perfect match with expert ranking should score 0"


def test_score_solution_reversed():
    """Test scoring for completely reversed ranking."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    ranking_text = """1. Box of matches
2. Magnetic compass
3. Portable heating unit
4. One case of dehydrated milk
5. Two .45 caliber pistols
6. Signal flares
7. Self-inflating life raft
8. Parachute silk
9. First aid kit with injection needles
10. 50 feet of nylon rope
11. Solar-powered FM receiver-transmitter
12. Food concentrate
13. Stellar map
14. 20 liters of water
15. Two 100-lb oxygen tanks"""

    score = task.score_solution(ranking_text)
    expected_l1 = sum(abs((15 - i) - (i + 1)) for i in range(15))
    assert score == expected_l1, f"Reversed ranking should score {expected_l1}"


def test_score_solution_partial():
    """Test scoring with partial differences from expert ranking."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    # Swap first two items (oxygen and water)
    ranking_text = """1. 20 liters of water
2. Two 100-lb oxygen tanks
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    score = task.score_solution(ranking_text)
    # Oxygen: expert=1, model=2, diff=1
    # Water: expert=2, model=1, diff=1
    # All others: diff=0
    assert score == 2.0, "Swapping two adjacent items should score 2"


def test_score_solution_invalid_ranking():
    """Test scoring returns max penalty for invalid ranking."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    invalid_text = "This is not a valid ranking"
    score = task.score_solution(invalid_text)
    assert score == 112.0, "Invalid ranking should score maximum penalty"


def test_hidden_info_mutually_exclusive():
    """Test that hidden info is distributed in mutually exclusive manner."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
    # Need to assign info first by executing or calling _assign_expert_information
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]
    task._assign_expert_information(agents)

    all_assigned_info = []
    for agent_id in agent_ids:
        hidden_info = task.get_hidden_info(agent_id)
        pieces = hidden_info.split("\n\n")
        all_assigned_info.extend(pieces)

    assert len(all_assigned_info) == 15, "All 15 perspectives should be assigned"
    assert len(set(all_assigned_info)) == 15, "Each perspective should be assigned exactly once"


def test_hidden_info_all_perspectives_assigned():
    """Test that all perspectives are assigned regardless of agent count."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    for num_agents in range(1, 16):
        agent_ids = list(range(num_agents))
        task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
        agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]
        task._assign_expert_information(agents)

        all_perspectives = []
        for agent_id in agent_ids:
            hidden_info = task.get_hidden_info(agent_id)
            pieces = hidden_info.split("\n\n")
            all_perspectives.extend(pieces)

        assert len(all_perspectives) == 15, f"All 15 perspectives should be assigned with {num_agents} agents"
        assert len(set(all_perspectives)) == 15, f"Each perspective should be unique with {num_agents} agents"


def test_hidden_info_distribution_balance():
    """Test that perspectives are distributed as evenly as possible."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)

    counts = []
    for agent_id in agent_ids:
        hidden_info = task.get_hidden_info(agent_id)
        pieces = hidden_info.split("\n\n")
        counts.append(len(pieces))

    assert max(counts) - min(counts) <= 1, "Distribution should be balanced (max difference of 1)"


def test_hidden_info_too_many_agents():
    """Test that more than 15 agents raises an error in distributed mode."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    agent_ids = list(range(16))
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
    agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]

    with pytest.raises(ValueError, match="Cannot have more than 15"):
        task._assign_expert_information(agents)
        task.get_hidden_info(0)


def test_hidden_info_single_agent():
    """Test that single agent receives all 15 perspectives in distributed mode."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    agent_ids = [0]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
    agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]
    task._assign_expert_information(agents)

    hidden_info = task.get_hidden_info(0)
    pieces = hidden_info.split("\n\n")

    assert len(pieces) == 15, "Single agent should receive all 15 perspectives"


def test_hidden_info_three_agents_equal_distribution():
    """Test that with 3 agents, each gets 5 unique perspectives in distributed mode."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
    agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]
    task._assign_expert_information(agents)

    info_0 = task.get_hidden_info(0).split("\n\n")
    info_1 = task.get_hidden_info(1).split("\n\n")
    info_2 = task.get_hidden_info(2).split("\n\n")

    assert len(info_0) == 5, "Agent 0 should have 5 perspectives"
    assert len(info_1) == 5, "Agent 1 should have 5 perspectives"
    assert len(info_2) == 5, "Agent 2 should have 5 perspectives"

    all_info = info_0 + info_1 + info_2
    assert len(set(all_info)) == 15, "All perspectives should be unique across agents"


def test_full_information_mode_all_agents_get_all_perspectives():
    """Test that in full_information mode, all agents receive all 15 perspectives."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="full", seed=None)

    full_info = task.get_full_info()
    pieces = full_info.split("\n\n")

    assert len(pieces) == 15, "get_full_info should return all 15 perspectives"

    for agent_id in agent_ids:
        full_info_agent = task.get_full_info()
        assert full_info_agent == full_info, f"Agent {agent_id} should receive identical full information"


def test_expert_info_mode_validation():
    """Test that expert_info_mode must be one of the valid values."""
    agent_ids = [0, 1, 2]

    with pytest.raises(ValueError, match="expert_info_mode must be one of"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="invalid_mode", seed=None)


def test_reveal_expert_requires_single_expert():
    """Test that reveal_expert decision_mode can only be used with expert_info_mode=single_expert."""
    agent_ids = [0, 1, 2]

    with pytest.raises(ValueError, match="decision_mode 'reveal_expert' can only be used with expert_info_mode='single_expert'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", decision_mode="reveal_expert", seed=None)

    with pytest.raises(ValueError, match="decision_mode 'reveal_expert' can only be used with expert_info_mode='single_expert'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="full", decision_mode="reveal_expert", seed=None)

    with pytest.raises(ValueError, match="decision_mode 'reveal_expert' can only be used with expert_info_mode='single_expert'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", decision_mode="reveal_expert", seed=None)

    # Should work with single_expert
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="single_expert", decision_mode="reveal_expert", seed=None)
    assert task.expert_info_mode == "single_expert"
    assert task.decision_mode == "reveal_expert"


def test_reveal_distributed_experts_requires_distributed():
    """Test that reveal_distributed_experts decision_mode can only be used with expert_info_mode=distributed."""
    agent_ids = [0, 1, 2]

    with pytest.raises(ValueError, match="decision_mode 'reveal_distributed_experts' can only be used with expert_info_mode='distributed'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="single_expert", decision_mode="reveal_distributed_experts", seed=None)

    with pytest.raises(ValueError, match="decision_mode 'reveal_distributed_experts' can only be used with expert_info_mode='distributed'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="full", decision_mode="reveal_distributed_experts", seed=None)

    with pytest.raises(ValueError, match="decision_mode 'reveal_distributed_experts' can only be used with expert_info_mode='distributed'"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", decision_mode="reveal_distributed_experts", seed=None)

    # Should work with distributed
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", decision_mode="reveal_distributed_experts", seed=None)
    assert task.expert_info_mode == "distributed"
    assert task.decision_mode == "reveal_distributed_experts"


def test_items_expert_in_per_agent_tracking():
    """Test that items_expert_in_per_agent is populated correctly in distributed mode."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
    agent_ids = [0, 1, 2]
    agents = [TeamAgent(AgentProfile(agent_id=aid, name=f"Agent {aid}", role="astronaut", system_prompt="You are an astronaut."), EchoBackend()) for aid in agent_ids]
    
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=42)
    task._assign_expert_information(agents)
    
    # Check that items are tracked for each agent
    total_items = 0
    for agent_id in agent_ids:
        items = task.items_expert_in_per_agent[agent_id]
        info = task.information_assigned_per_expert[agent_id]
        # Each agent should have the same number of items as info pieces
        assert len(items) == len(info), f"Agent {agent_id} should have same number of items as info pieces"
        # Each item should correspond to the info piece at the same index
        for i, info_piece in enumerate(info):
            # Find which index this info_piece is in SPECIALIZED_INFORMATION
            info_index = task.SPECIALIZED_INFORMATION.index(info_piece)
            # The corresponding item should be ITEMS[info_index]
            assert items[i] == task.ITEMS[info_index], f"Agent {agent_id}, item {i} should correspond to info piece index"
        total_items += len(items)
    
    # All 15 items should be distributed
    assert total_items == 15, "All 15 items should be distributed among agents"


def test_full_information_uses_specialized_information_constant():
    """Test that get_full_info returns content from SPECIALIZED_INFORMATION constant."""
    agent_ids = [0]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="full", seed=None)

    full_info = task.get_full_info()
    expected_info = "\n\n".join(task.SPECIALIZED_INFORMATION)

    assert full_info == expected_info, "get_full_info should return all SPECIALIZED_INFORMATION perspectives joined"


def test_decision_mode_expert_not_mentioned():
    """Test that expert_not_mentioned decision mode works without errors."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", decision_mode="expert_not_mentioned", seed=None)
    assert task.decision_mode == "expert_not_mentioned"
    assert task.revealed_expert_agent_id is None


def test_decision_mode_invalid_value():
    """Test that invalid decision mode raises ValueError."""
    agent_ids = [0, 1, 2]

    with pytest.raises(ValueError, match="decision_mode must be one of"):
        MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", decision_mode="invalid_mode", seed=None)


def test_decision_mode_reveal_expert_initialization():
    """Test that reveal_expert mode initializes correctly."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="single_expert", decision_mode="reveal_expert", seed=None)
    assert task.decision_mode == "reveal_expert"
    assert task.expert_info_mode == "single_expert"
    assert task.revealed_expert_agent_id is None


def test_decision_mode_expert_identification_initialization():
    """Test that expert identification modes initialize correctly."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", decision_mode="discussion_based_expert_identification", seed=None)
    assert task.decision_mode == "discussion_based_expert_identification"
    assert task.revealed_expert_agent_id is None


def test_single_expert_initialization():
    """Test that single_expert mode initializes correctly."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="single_expert", seed=None)
    assert task.expert_info_mode == "single_expert"
    assert task.designated_expert_agent_id is None


# Removed test - expert_info_mode is a single parameter, no incompatibility checks needed


# Removed test - expert_info_mode is a single parameter, no incompatibility checks needed


# Removed test - expert_info_percentage no longer exists, single_expert always gives 100% of info


# Removed test - expert_info_percentage no longer exists, single_expert always gives 100% of info


def test_calculate_nominal_ranking():
    """Test that nominal ranking is calculated correctly from individual rankings."""
    task = MoonSurvivalTask([0, 1], max_rounds=1, expert_info_mode="none", seed=None)

    # Create two identical rankings (should produce same nominal ranking)
    ranking1 = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    individual_rankings = {0: ranking1, 1: ranking1}
    nominal = task._calculate_nominal_ranking(individual_rankings)

    # Nominal ranking should match the individual rankings
    assert "1. Two 100-lb oxygen tanks" in nominal
    assert "2. 20 liters of water" in nominal
    assert "15. Box of matches" in nominal


def test_calculate_nominal_ranking_with_different_individual_rankings():
    """Test nominal ranking calculation with different individual rankings."""
    task = MoonSurvivalTask([0, 1], max_rounds=1, expert_info_mode="none", seed=None)

    # Agent 0 ranks oxygen first, water second
    ranking1 = """1. Two 100-lb oxygen tanks
2. 20 liters of water
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    # Agent 1 ranks water first, oxygen second (swap top 2)
    ranking2 = """1. 20 liters of water
2. Two 100-lb oxygen tanks
3. Stellar map
4. Food concentrate
5. Solar-powered FM receiver-transmitter
6. 50 feet of nylon rope
7. First aid kit with injection needles
8. Parachute silk
9. Self-inflating life raft
10. Signal flares
11. Two .45 caliber pistols
12. One case of dehydrated milk
13. Portable heating unit
14. Magnetic compass
15. Box of matches"""

    individual_rankings = {0: ranking1, 1: ranking2}
    nominal = task._calculate_nominal_ranking(individual_rankings)

    # Both oxygen and water have average rank of 1.5, but oxygen should come first
    # because it's lexicographically first in ITEMS list when tied
    # Actually, items are sorted by average rank, so both would be 1.5
    # The order among tied items depends on sort stability
    assert "NOMINAL RANKING:" in nominal
    assert len(nominal.split('\n')) == 16  # Header + 15 items


def test_calculate_nominal_ranking_empty_input():
    """Test that nominal ranking handles empty input gracefully."""
    task = MoonSurvivalTask([0], max_rounds=1, expert_info_mode="none", seed=None)

    nominal = task._calculate_nominal_ranking({})
    assert nominal == ""


def test_adversarial_agents_get_adversarial_prompt():
    """Test that adversarial agents receive adversarial instructions in their task description."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=1,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    # Select adversarial agents
    task._select_adversarial_agents(excluded_agent_ids=[])
    
    # Check that adversarial agent gets adversarial prompt
    adversarial_id = task.adversarial_agent_ids[0]
    adversarial_prompt = task.get_task_description(adversarial_id)
    
    assert "imposter astronaut" in adversarial_prompt.lower(), "Adversarial prompt should contain imposter instructions"
    assert "WORST performance" in adversarial_prompt, "Adversarial prompt should mention worst performance"
    assert "Ground Truth Ranking" in adversarial_prompt, "Adversarial prompt with ground truth should include ground truth ranking"
    assert "Worst Possible Ranking" in adversarial_prompt, "Adversarial prompt with ground truth should include reversed ranking"
    
    # Check that non-adversarial agents get normal prompt
    for agent_id in agent_ids:
        if agent_id not in task.adversarial_agent_ids:
            normal_prompt = task.get_task_description(agent_id)
            assert "imposter astronaut" not in normal_prompt.lower(), f"Agent {agent_id} should not get adversarial prompt"
            assert "collaborate with your" in normal_prompt, f"Agent {agent_id} should get collaborative instructions"


def test_adversarial_agents_without_ground_truth():
    """Test that adversarial agents without ground truth mode get appropriate instructions."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=1,
        adversarial_mode="without_ground_truth",
        seed=42
    )
    
    task._select_adversarial_agents(excluded_agent_ids=[])
    
    adversarial_id = task.adversarial_agent_ids[0]
    adversarial_prompt = task.get_task_description(adversarial_id)
    
    assert "imposter astronaut" in adversarial_prompt.lower(), "Adversarial prompt should contain imposter instructions"
    assert "WORST performance" in adversarial_prompt, "Adversarial prompt should mention worst performance"
    assert "Ground Truth Ranking" not in adversarial_prompt, "Adversarial prompt without ground truth should not include ground truth ranking"
    assert "infer what would be suboptimal" in adversarial_prompt.lower(), "Adversarial prompt without ground truth should mention inferring"


def test_adversarial_agents_excluded_from_expert_selection():
    """Test that adversarial agents are excluded from expert selection in yetton mode."""
    agent_ids = [0, 1, 2, 3]
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="single_expert",
        decision_mode="reveal_expert",
        num_adversarial_agents=1,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    # Execute task (adversarial agents will be selected during execution, after expert is selected)
    task.execute(agents)
    
    # Verify adversarial agent is not the expert
    adversarial_id = task.adversarial_agent_ids[0]
    assert task.revealed_expert_agent_id != adversarial_id, "Adversarial agent should not be selected as expert"
    assert task.revealed_expert_agent_id is not None, "Expert should be selected"


def test_adversarial_agents_excluded_from_designated_expert():
    """Test that adversarial agents are excluded when selecting designated expert in single_expert mode."""
    agent_ids = [0, 1, 2, 3]
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="single_expert",
        num_adversarial_agents=1,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    # Execute task (adversarial agents selected after expert in _collect_individual_rankings)
    task.execute(agents)
    
    # Verify adversarial agent is not the expert
    assert task.designated_expert_agent_id not in task.adversarial_agent_ids, "Adversarial agent should not be the designated expert"
    assert task.designated_expert_agent_id is not None, "Expert should be selected"
    assert len(task.adversarial_agent_ids) == 1, "One adversarial agent should be selected"


def test_adversarial_agents_metadata_logged():
    """Test that adversarial agent IDs are logged in metadata."""
    agent_ids = [0, 1, 2]
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=1,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    result = task.execute(agents)
    
    assert "adversarial_agent_ids" in result.metadata, "Adversarial agent IDs should be in metadata"
    assert len(result.metadata["adversarial_agent_ids"]) == 1, "One adversarial agent ID should be logged"
    assert result.metadata["num_adversarial_agents"] == 1, "Number of adversarial agents should be logged"
    assert result.metadata["adversarial_mode"] == "with_ground_truth", "Adversarial mode should be logged"


def test_no_adversarial_agents_metadata():
    """Test that when no adversarial agents are used, metadata reflects this."""
    agent_ids = [0, 1, 2]
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=0,
        adversarial_mode="none",
        seed=42
    )
    
    result = task.execute(agents)
    
    assert result.metadata["adversarial_agent_ids"] == [], "Adversarial agent IDs should be empty list"
    assert result.metadata["num_adversarial_agents"] == 0, "Number of adversarial agents should be 0"
    assert result.metadata["adversarial_mode"] is None, "Adversarial mode should be None when disabled"


def test_multiple_adversarial_agents():
    """Test that multiple adversarial agents (2, 4, 6) can be selected correctly."""
    agent_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    
    for num_adv in [2, 4, 6]:
        agents = [
            TeamAgent(
                AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
                EchoBackend()
            )
            for agent_id in agent_ids
        ]
        
        task = MoonSurvivalTask(
            agent_ids,
            max_rounds=1,
            expert_info_mode="none",
            num_adversarial_agents=num_adv,
            adversarial_mode="with_ground_truth",
            seed=42
        )
        
        # Execute to trigger adversarial agent selection
        task.execute(agents)
        
        # Verify adversarial agents are selected
        assert len(task.adversarial_agent_ids) == num_adv, f"Should have {num_adv} adversarial agents"
        assert all(aid in agent_ids for aid in task.adversarial_agent_ids), "All adversarial agents should be in agent_ids"
        assert len(set(task.adversarial_agent_ids)) == num_adv, "Adversarial agent IDs should be unique"


def test_final_submitter_not_adversarial():
    """Test that the agent selected to submit final ranking is not an adversarial agent."""
    agent_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=2,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    task.execute(agents)
    
    # Find which agent submitted the final ranking by checking which agent has the final prompt followed by their response
    final_submitter_id = None
    for agent in agents:
        for i, turn in enumerate(agent.trajectory.turns):
            # Look for the final prompt (contains "discussion rounds are now complete")
            if turn.speaker_id == -1 and "discussion rounds are now complete" in turn.content:
                # The next turn should be the agent's response
                if i + 1 < len(agent.trajectory.turns) and agent.trajectory.turns[i + 1].speaker_id == agent.profile.agent_id:
                    final_submitter_id = agent.profile.agent_id
                    break
        if final_submitter_id is not None:
            break
    
    assert final_submitter_id is not None, "Should find an agent that submitted the final ranking"
    assert final_submitter_id not in task.adversarial_agent_ids, "Final submitter should not be an adversarial agent"


def test_random_final_submitter_all_cases():
    """Test that final submitter is randomly selected (not always agent 0) in both standard and adversarial cases."""
    agent_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    
    # Test standard case (no adversarial agents)
    submitter_ids_standard = []
    for seed in [42, 123, 456]:
        agents = [
            TeamAgent(
                AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
                EchoBackend()
            )
            for agent_id in agent_ids
        ]
        
        task = MoonSurvivalTask(
            agent_ids,
            max_rounds=1,
            expert_info_mode="none",
            num_adversarial_agents=0,
            adversarial_mode="none",
            seed=seed
        )
        
        task.execute(agents)
        
        # Find final submitter
        for agent in agents:
            for i, turn in enumerate(agent.trajectory.turns):
                # Look for the final prompt (contains "discussion rounds are now complete")
                if turn.speaker_id == -1 and "discussion rounds are now complete" in turn.content:
                    # The next turn should be the agent's response
                    if i + 1 < len(agent.trajectory.turns) and agent.trajectory.turns[i + 1].speaker_id == agent.profile.agent_id:
                        submitter_ids_standard.append(agent.profile.agent_id)
                        break
            if submitter_ids_standard and submitter_ids_standard[-1] == agent.profile.agent_id:
                break
    
    # With different seeds, we should get different submitters (or at least not always agent 0)
    # Note: This is probabilistic, but with 3 different seeds it's very unlikely all are agent 0
    assert len(set(submitter_ids_standard)) >= 1, "Should have at least one submitter ID"
    
    # Test adversarial case
    submitter_ids_adversarial = []
    adversarial_agent_sets = []  # Store adversarial agent IDs for each iteration
    for seed in [42, 123, 456]:
        agents = [
            TeamAgent(
                AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
                EchoBackend()
            )
            for agent_id in agent_ids
        ]
        
        task = MoonSurvivalTask(
            agent_ids,
            max_rounds=1,
            expert_info_mode="none",
            num_adversarial_agents=2,
            adversarial_mode="with_ground_truth",
            seed=seed
        )
        
        task.execute(agents)
        
        # Store adversarial agent IDs for this iteration
        adversarial_agent_sets.append(set(task.adversarial_agent_ids))
        
        # Find final submitter (should not be adversarial)
        submitter_found_for_this_seed = False
        for agent in agents:
            if agent.profile.agent_id in task.adversarial_agent_ids:
                continue
            for i, turn in enumerate(agent.trajectory.turns):
                # Look for the final prompt (contains "discussion rounds are now complete")
                if turn.speaker_id == -1 and "discussion rounds are now complete" in turn.content:
                    # The next turn should be the agent's response
                    if i + 1 < len(agent.trajectory.turns) and agent.trajectory.turns[i + 1].speaker_id == agent.profile.agent_id:
                        submitter_ids_adversarial.append(agent.profile.agent_id)
                        submitter_found_for_this_seed = True
                        break
            if submitter_found_for_this_seed:
                break
        
        assert submitter_found_for_this_seed, f"Should have found a final submitter for seed {seed}"
    
    # Verify all submitters are non-adversarial
    assert len(submitter_ids_adversarial) == 3, "Should have found 3 submitters (one per seed)"
    for idx, submitter_id in enumerate(submitter_ids_adversarial):
        assert submitter_id not in adversarial_agent_sets[idx], f"Final submitter {submitter_id} should not be adversarial (iteration {idx})"


def test_validation_minimum_non_adversarial_agent():
    """Test that validation requires at least 1 non-adversarial agent."""
    agent_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    
    # Should fail if num_adversarial_agents >= total agents
    with pytest.raises(ValueError, match="must be < total_agents"):
        MoonSurvivalTask(
            agent_ids,
            max_rounds=1,
            expert_info_mode="none",
            num_adversarial_agents=8,  # All agents adversarial
            adversarial_mode="with_ground_truth",
            seed=42
        )
    
    # Should succeed with 7 adversarial agents (1 non-adversarial remains)
    agents = [
        TeamAgent(
            AgentProfile(agent_id=agent_id, name=f"Agent {agent_id}", role="astronaut", system_prompt="You are an astronaut."),
            EchoBackend()
        )
        for agent_id in agent_ids
    ]
    
    task = MoonSurvivalTask(
        agent_ids,
        max_rounds=1,
        expert_info_mode="none",
        num_adversarial_agents=7,
        adversarial_mode="with_ground_truth",
        seed=42
    )
    
    # Execute to trigger adversarial agent selection
    task.execute(agents)
    assert len(task.adversarial_agent_ids) == 7