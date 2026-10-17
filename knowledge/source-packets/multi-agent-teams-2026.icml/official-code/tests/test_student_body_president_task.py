"""Tests for Student Body President task parsing and scoring."""

from teamwork.tasks.student_body_president_task import StudentBodyPresidentTask


def test_parse_ranking_basic():
    """Test that _parse_ranking correctly parses a basic ranking."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """MY RANKING:
1. Candidate A
2. Candidate B
3. Candidate C
4. Candidate D"""

    result = task._parse_ranking(ranking_text)

    assert result == {
        "Candidate A": 1,
        "Candidate B": 2,
        "Candidate C": 3,
        "Candidate D": 4,
    }


def test_parse_ranking_with_explanation():
    """Test that _parse_ranking handles rankings with explanations."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """I think Candidate A is the best because of their leadership experience.

MY RANKING:
1. Candidate A
2. Candidate B
3. Candidate C
4. Candidate D

This ranking reflects my assessment of their qualifications."""

    result = task._parse_ranking(ranking_text)

    assert result == {
        "Candidate A": 1,
        "Candidate B": 2,
        "Candidate C": 3,
        "Candidate D": 4,
    }


def test_parse_ranking_different_order():
    """Test that _parse_ranking handles rankings in different orders."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """MY RANKING:
1. Candidate D
2. Candidate A
3. Candidate C
4. Candidate B"""

    result = task._parse_ranking(ranking_text)

    assert result == {
        "Candidate A": 2,
        "Candidate B": 4,
        "Candidate C": 3,
        "Candidate D": 1,
    }


def test_parse_ranking_parentheses_format():
    """Test that _parse_ranking handles parentheses format."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """MY RANKING:
1) Candidate A
2) Candidate B
3) Candidate C
4) Candidate D"""

    result = task._parse_ranking(ranking_text)

    assert result == {
        "Candidate A": 1,
        "Candidate B": 2,
        "Candidate C": 3,
        "Candidate D": 4,
    }


def test_parse_ranking_incomplete():
    """Test that _parse_ranking raises ValueError for incomplete rankings."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """MY RANKING:
1. Candidate A
2. Candidate B
3. Candidate C"""

    try:
        task._parse_ranking(ranking_text)
        assert False, "Should have raised ValueError for incomplete ranking"
    except ValueError as e:
        assert "Could not parse complete ranking" in str(e)


def test_parse_ranking_duplicate():
    """Test that _parse_ranking raises ValueError for duplicate candidates."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    ranking_text = """MY RANKING:
1. Candidate A
2. Candidate B
3. Candidate A
4. Candidate D"""

    try:
        task._parse_ranking(ranking_text)
        assert False, "Should have raised ValueError for duplicate candidate"
    except ValueError as e:
        # The error could be either "appears multiple times" or "Could not parse complete ranking"
        # depending on which check happens first
        error_msg = str(e)
        assert "appears multiple times" in error_msg or "Could not parse complete ranking" in error_msg, \
            f"Expected error about duplicate or incomplete ranking, got: {error_msg}"


def test_score_solution_perfect_match():
    """Test that score_solution returns 0 for perfect match with ground truth."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Set ground truth: A=1, B=2, C=3, D=4
    task.GROUND_TRUTH_RANKING = [1, 2, 3, 4]

    solution = """FINAL TEAM RANKING:
1. Candidate A
2. Candidate B
3. Candidate C
4. Candidate D"""

    score = task.score_solution(solution)
    assert score == 0.0, f"Perfect match should score 0.0, got {score}"


def test_score_solution_one_swap():
    """Test that score_solution calculates L1 distance correctly for one swap."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Set ground truth: A=1, B=2, C=3, D=4
    task.GROUND_TRUTH_RANKING = [1, 2, 3, 4]

    # Agent ranking: A=1, B=3, C=2, D=4 (swapped B and C)
    solution = """FINAL TEAM RANKING:
1. Candidate A
2. Candidate C
3. Candidate B
4. Candidate D"""

    score = task.score_solution(solution)
    # A: |1 - 1| = 0
    # B: |3 - 2| = 1
    # C: |2 - 3| = 1
    # D: |4 - 4| = 0
    # Total = 2
    assert score == 2.0, f"One swap should score 2.0, got {score}"


def test_score_solution_complete_reversal():
    """Test that score_solution calculates L1 distance correctly for complete reversal."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Set ground truth: A=1, B=2, C=3, D=4
    task.GROUND_TRUTH_RANKING = [1, 2, 3, 4]

    # Agent ranking: D=1, C=2, B=3, A=4 (complete reversal)
    solution = """FINAL TEAM RANKING:
1. Candidate D
2. Candidate C
3. Candidate B
4. Candidate A"""

    score = task.score_solution(solution)
    # A: |4 - 1| = 3
    # B: |3 - 2| = 1
    # C: |2 - 3| = 1
    # D: |1 - 4| = 3
    # Total = 8
    assert score == 8.0, f"Complete reversal should score 8.0, got {score}"


def test_score_solution_example_from_user():
    """Test scoring with the example from user: agent ranking D, A, B, C vs ground truth D, A, C, B."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Ground truth order: D, A, C, B
    # So: A (items[0]) has rank 2, B (items[1]) has rank 4, C (items[2]) has rank 3, D (items[3]) has rank 1
    task.GROUND_TRUTH_RANKING = [2, 4, 3, 1]

    # Agent ranking: D, A, B, C
    solution = """FINAL TEAM RANKING:
1. Candidate D
2. Candidate A
3. Candidate B
4. Candidate C"""

    score = task.score_solution(solution)
    # A: |2 - 2| = 0
    # B: |3 - 4| = 1
    # C: |4 - 3| = 1
    # D: |1 - 1| = 0
    # Total = 2
    assert score == 2.0, f"Expected score 2.0, got {score}"


def test_expert_info_mode_none_no_unique_information():
    """Test that expert_info_mode='none' gives no unique information to agents."""
    from teamwork.agent import TeamAgent
    from teamwork.backends import EchoBackend
    from teamwork.profiles import AgentProfile

    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="none",
        seed=42,
    )

    # Create agents
    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Committee Member",
                system_prompt="You are a committee member."
            ),
            backend=backend
        )
        for agent_id in task.agent_ids
    ]

    # Call _assign_expert_information
    task._assign_expert_information(agents)

    # Verify that no agents receive unique information
    for agent_id in task.agent_ids:
        assigned_info = task.information_assigned_per_expert.get(agent_id, [])
        assert len(assigned_info) == 0, \
            f"Agent {agent_id} should have no unique information in 'none' mode, got {len(assigned_info)} pieces"



def test_specialized_information_includes_valence():
    """Test that specialized_information includes valence information."""
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Use the task's defined PER_AGENT_UNIQUE_INFORMATION
    specialized = task.specialized_information

    # Should include valence information
    assert any("valence: positive" in info for info in specialized), "Should include positive valence"
    assert any("valence: negative" in info for info in specialized), "Should include negative valence"
    assert any("valence: neutral" in info for info in specialized), "Should include neutral valence"

    # Should include candidate labels
    assert any("Candidate A:" in info for info in specialized), "Should include Candidate A label"
    assert any("Candidate B:" in info for info in specialized), "Should include Candidate B label"
    assert any("Candidate C:" in info for info in specialized), "Should include Candidate C label"
    assert any("Candidate D:" in info for info in specialized), "Should include Candidate D label"

    # Should include traits from the task definition
    assert any("Vision for campus" in info for info in specialized), "Should include Candidate A traits"
    assert any("Time management" in info for info in specialized), "Should include Candidate A or B or C traits"
    assert any("Creativity" in info for info in specialized), "Should include Candidate C traits"
    assert any("Reliability" in info for info in specialized), "Should include Candidate D traits"


def test_distributed_mode_one_candidate_per_agent():
    """Test that distributed mode guarantees each agent is an expert in exactly one candidate."""
    from teamwork.agent import TeamAgent
    from teamwork.backends import EchoBackend
    from teamwork.profiles import AgentProfile

    # Create task with distributed mode (uses PER_AGENT_UNIQUE_INFORMATION from task definition)
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Create agents
    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Committee Member",
                system_prompt="You are a committee member."
            ),
            backend=backend
        )
        for agent_id in task.agent_ids
    ]

    # Call _assign_expert_information
    task._assign_expert_information(agents)

    # Verify that each agent has information about exactly one candidate
    for agent_id in task.agent_ids:
        assigned_info = task.information_assigned_per_expert.get(agent_id, [])
        candidates = task.items_expert_in_per_agent.get(agent_id, [])
        
        # Each agent should have exactly one candidate
        assert len(candidates) == 1, f"Agent {agent_id} should be expert in exactly one candidate, got {candidates}"
        
        # Each agent should have all pieces for their candidate
        # Each candidate has 4 pieces in the task definition
        assert len(assigned_info) == 4, f"Agent {agent_id} should have 4 pieces of information (one candidate's worth), got {len(assigned_info)}"
        
        # Verify all pieces are about the same candidate
        candidate = candidates[0]
        # Get expected traits for this candidate from the task definition
        candidate_letter = candidate.replace("Candidate ", "")
        expected_traits = {
            "A": ["Vision for campus", "Time management", "Conflict resolution", "Work ethic"],
            "B": ["Communication skills", "Commitment to role", "Crisis handling", "Adaptability"],
            "C": ["Creativity", "Decision-making", "Networking", "Initiative"],
            "D": ["Reliability", "Fundraising ability", "Interpersonal skills", "Dedication"],
        }
        
        # Verify all assigned pieces contain traits for the correct candidate
        for info_string in assigned_info:
            found_trait = False
            for trait in expected_traits[candidate_letter]:
                if trait in info_string:
                    found_trait = True
                    break
            assert found_trait, \
                f"Agent {agent_id} (expert on {candidate}) should only have information about {candidate}, but found: {info_string}"

    # Verify that all 4 candidates are assigned (one per agent)
    all_candidates = set()
    for agent_id in task.agent_ids:
        candidates = task.items_expert_in_per_agent.get(agent_id, [])
        all_candidates.update(candidates)
    
    assert len(all_candidates) == 4, f"All 4 candidates should be assigned, got {all_candidates}"
    assert all_candidates == {"Candidate A", "Candidate B", "Candidate C", "Candidate D"}, \
        f"Should have all 4 candidates assigned, got {all_candidates}"


def test_full_info_mode_all_agents_see_all_information():
    """Test that full_info mode gives all unique information to all agents."""
    from teamwork.agent import TeamAgent
    from teamwork.backends import EchoBackend
    from teamwork.profiles import AgentProfile

    # Create task with full_info mode (uses PER_AGENT_UNIQUE_INFORMATION from task definition)
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="full",
        seed=42,
    )

    # Create agents
    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Committee Member",
                system_prompt="You are a committee member."
            ),
            backend=backend
        )
        for agent_id in task.agent_ids
    ]

    # Call _assign_expert_information
    task._assign_expert_information(agents)

    # Get all unique information pieces (should be 16 total: 4 candidates × 4 pieces each)
    # Format includes candidate label: "Candidate X: trait (valence: ...)"
    all_unique_pieces = []
    for pieces in task.PER_AGENT_UNIQUE_INFORMATION.values():
        for piece in pieces:
            piece_string = f"Candidate {piece.candidate}: {piece.trait} (valence: {piece.valence})"
            all_unique_pieces.append(piece_string)

    # Verify that all non-adversarial agents see all unique information
    for agent_id in task.agent_ids:
        assigned_info = task.information_assigned_per_expert.get(agent_id, [])
        
        # Each agent should have all 16 unique pieces
        assert len(assigned_info) == len(all_unique_pieces), \
            f"Agent {agent_id} should have all {len(all_unique_pieces)} unique pieces in full_info mode, got {len(assigned_info)}"
        
        # Verify they have all the pieces
        for piece_string in all_unique_pieces:
            assert piece_string in assigned_info, \
                f"Agent {agent_id} should have piece '{piece_string}' in full_info mode"

    # Verify all agents see the same information
    agent_0_info = set(task.information_assigned_per_expert[0])
    for agent_id in [1, 2, 3]:
        agent_info = set(task.information_assigned_per_expert[agent_id])
        assert agent_0_info == agent_info, \
            f"Agent {agent_id} should see the same information as Agent 0 in full_info mode"


def test_single_expert_mode_only_one_agent_sees_all_information():
    """Test that single_expert mode gives all unique information to only one agent."""
    from teamwork.agent import TeamAgent
    from teamwork.backends import EchoBackend
    from teamwork.profiles import AgentProfile

    # Create task with single_expert mode (uses PER_AGENT_UNIQUE_INFORMATION from task definition)
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="single_expert",
        seed=42,
    )

    # Create agents
    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Committee Member",
                system_prompt="You are a committee member."
            ),
            backend=backend
        )
        for agent_id in task.agent_ids
    ]

    # Call _assign_expert_information
    task._assign_expert_information(agents)

    # Get all unique information pieces (should be 16 total: 4 candidates × 4 pieces each)
    # Format includes candidate label: "Candidate X: trait (valence: ...)"
    all_unique_pieces = []
    for pieces in task.PER_AGENT_UNIQUE_INFORMATION.values():
        for piece in pieces:
            piece_string = f"Candidate {piece.candidate}: {piece.trait} (valence: {piece.valence})"
            all_unique_pieces.append(piece_string)

    # Find the expert agent
    expert_agent_id = task.designated_expert_agent_id
    assert expert_agent_id is not None, "Should have a designated expert agent"
    assert expert_agent_id in task.agent_ids, f"Expert agent {expert_agent_id} should be in agent_ids"

    # Verify expert agent has all unique information
    expert_info = task.information_assigned_per_expert.get(expert_agent_id, [])
    assert len(expert_info) == len(all_unique_pieces), \
        f"Expert agent {expert_agent_id} should have all {len(all_unique_pieces)} unique pieces, got {len(expert_info)}"
    
    for piece_string in all_unique_pieces:
        assert piece_string in expert_info, \
            f"Expert agent {expert_agent_id} should have piece '{piece_string}'"

    # Verify non-expert agents have no unique information
    for agent_id in task.agent_ids:
        if agent_id != expert_agent_id:
            non_expert_info = task.information_assigned_per_expert.get(agent_id, [])
            assert len(non_expert_info) == 0, \
                f"Non-expert agent {agent_id} should have no unique information in single_expert mode, got {len(non_expert_info)} pieces"


def test_distributed_mode_each_agent_sees_one_candidate_information():
    """Test that distributed mode gives each agent unique information for exactly one candidate."""
    from teamwork.agent import TeamAgent
    from teamwork.backends import EchoBackend
    from teamwork.profiles import AgentProfile

    # Create task with distributed mode (uses PER_AGENT_UNIQUE_INFORMATION from task definition)
    task = StudentBodyPresidentTask(
        agent_ids=[0, 1, 2, 3],
        max_rounds=1,
        expert_info_mode="distributed",
        seed=42,
    )

    # Create agents
    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Committee Member",
                system_prompt="You are a committee member."
            ),
            backend=backend
        )
        for agent_id in task.agent_ids
    ]

    # Call _assign_expert_information
    task._assign_expert_information(agents)

    # Expected: Each agent should have exactly 4 pieces (one candidate's worth)
    # Agent 0 → Candidate A (4 pieces)
    # Agent 1 → Candidate B (4 pieces)
    # Agent 2 → Candidate C (4 pieces)
    # Agent 3 → Candidate D (4 pieces)

    # Build expected pieces for each candidate from the task definition
    # Format includes candidate label: "Candidate X: trait (valence: ...)"
    expected_pieces_by_candidate = {}
    for candidate_letter in ["A", "B", "C", "D"]:
        pieces = []
        for agent_pieces in task.PER_AGENT_UNIQUE_INFORMATION.values():
            for piece in agent_pieces:
                if piece.candidate == candidate_letter:
                    pieces.append(f"Candidate {piece.candidate}: {piece.trait} (valence: {piece.valence})")
        expected_pieces_by_candidate[candidate_letter] = sorted(pieces)

    # Verify each agent has exactly 4 pieces for one candidate
    for agent_id in task.agent_ids:
        assigned_info = task.information_assigned_per_expert.get(agent_id, [])
        candidates = task.items_expert_in_per_agent.get(agent_id, [])
        
        # Each agent should have exactly one candidate
        assert len(candidates) == 1, \
            f"Agent {agent_id} should be expert in exactly one candidate in distributed mode, got {candidates}"
        
        # Each agent should have exactly 4 pieces
        assert len(assigned_info) == 4, \
            f"Agent {agent_id} should have exactly 4 pieces in distributed mode, got {len(assigned_info)}"
        
        # Verify all pieces are for the correct candidate
        candidate = candidates[0]
        candidate_letter = candidate.replace("Candidate ", "")
        expected_pieces = set(expected_pieces_by_candidate[candidate_letter])
        assigned_pieces = set(assigned_info)
        
        assert assigned_pieces == expected_pieces, \
            f"Agent {agent_id} (expert on {candidate}) should have pieces {expected_pieces}, got {assigned_pieces}"

    # Verify all 4 candidates are assigned (one per agent)
    all_candidates = set()
    for agent_id in task.agent_ids:
        candidates = task.items_expert_in_per_agent.get(agent_id, [])
        all_candidates.update(candidates)
    
    assert len(all_candidates) == 4, f"All 4 candidates should be assigned, got {all_candidates}"
    assert all_candidates == {"Candidate A", "Candidate B", "Candidate C", "Candidate D"}, \
        f"Should have all 4 candidates assigned, got {all_candidates}"

