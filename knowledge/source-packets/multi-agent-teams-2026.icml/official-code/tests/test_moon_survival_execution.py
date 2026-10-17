"""Tests for Moon Survival task execution logic."""

from teamwork.agent import TeamAgent
from teamwork.backends import EchoBackend
from teamwork.tasks import MoonSurvivalTask
from teamwork.profiles import AgentProfile


def test_independent_rankings_isolated():
    """Test that independent phase uses isolated trajectories with no cross-contamination."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)

    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Astronaut",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    rankings = task._collect_individual_rankings(agents)

    # All agents produced rankings
    assert len(rankings) == 3, "Should have rankings from all 3 agents"
    for agent_id in agent_ids:
        assert agent_id in rankings, f"Agent {agent_id} should have a ranking"

    # Each agent's trajectory contains context + response (no cross-contamination)
    for agent in agents:
        assert len(agent.trajectory.turns) == 2, \
            f"Agent {agent.profile.agent_id} should have exactly 2 turns (context + response)"
        assert agent.trajectory.turns[0].speaker_id == -1, \
            f"Agent {agent.profile.agent_id} context turn should be a system message (speaker_id=-1)"
        assert agent.trajectory.turns[1].speaker_id == agent.profile.agent_id, \
            f"Agent {agent.profile.agent_id} response turn should have their speaker_id"


def test_collaboration_phase_shared_trajectory():
    """Test that collaboration phase shares trajectory across agents."""
    agent_ids = [0, 1]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)

    class TrackingBackend(EchoBackend):
        def __init__(self):
            super().__init__()
            self.all_calls = []

        def invoke(self, *, agent_profile, trajectory):
            self.all_calls.append({
                "agent_id": agent_profile.agent_id,
                "trajectory_length": len(trajectory.turns),
                "speaker_ids": [turn.speaker_id for turn in trajectory.turns],
                "is_collaboration": len(trajectory.turns) > 0
            })
            return super().invoke(
                agent_profile=agent_profile,
                trajectory=trajectory
            )

    backend = TrackingBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Astronaut",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    # First collect individual rankings
    individual_rankings = task._collect_individual_rankings(agents)

    # Then facilitate collaboration
    task._facilitate_collaboration(agents, individual_rankings)

    # Filter to collaboration calls only (trajectory length > 1 since agents have their own ranking)
    collab_calls = [c for c in backend.all_calls if c["trajectory_length"] > 1]

    assert len(collab_calls) >= 1, "Should have at least 1 collaboration turn"

    # First collaboration call - agent sees their own ranking + other agent's ranking + system messages
    first_call = collab_calls[0]
    assert first_call["trajectory_length"] >= 2, "Agent should see at least 2 rankings (own + others)"
    # Should see rankings from both agents plus system messages (speaker_id=-1)
    assert {0, 1}.issubset(set(first_call["speaker_ids"])), "Should see rankings from both agents"


def test_collaboration_trajectory_grows():
    """Test that collaboration trajectory grows as agents contribute."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=2, expert_info_mode="none", seed=None)

    class TrajectoryLengthTracker(EchoBackend):
        def __init__(self):
            super().__init__()
            self.trajectory_lengths_by_agent = {}  # Track per agent

        def invoke(self, *, agent_profile, trajectory):
            if len(trajectory.turns) > 0:  # Only during collaboration
                # Track all collaboration calls (including per-round collection) per agent
                # since they all append to the trajectory and should cause it to grow
                agent_id = agent_profile.agent_id
                if agent_id not in self.trajectory_lengths_by_agent:
                    self.trajectory_lengths_by_agent[agent_id] = []
                self.trajectory_lengths_by_agent[agent_id].append(len(trajectory.turns))
            return "FINAL TEAM RANKING:\n1. Item\n2. Item\n3. Item\n4. Item\n5. Item\n6. Item\n7. Item\n8. Item\n9. Item\n10. Item\n11. Item\n12. Item\n13. Item\n14. Item\n15. Item"

    backend = TrajectoryLengthTracker()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="ranker",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    individual_rankings = {i: f"Ranking {i}" for i in agent_ids}

    task._facilitate_collaboration(agents, individual_rankings)

    # Trajectory should grow monotonically for each agent
    for agent_id, lengths in backend.trajectory_lengths_by_agent.items():
        for i in range(1, len(lengths)):
            assert lengths[i] >= lengths[i-1], \
                f"Agent {agent_id}: Trajectory should grow or stay same size (got {lengths[i-1]} -> {lengths[i]})"


def test_hidden_info_passed_to_agents():
    """Test that hidden info is passed to agents during independent phase."""
    agent_ids = [0, 1]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)

    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="ranker",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    task._collect_individual_rankings(agents)

    # Each agent should have trajectory with task description
    assert len(agents) == 2, "Both agents should exist"
    assert len(agents[0].trajectory.turns) >= 1, "Agent 0 should have turns in trajectory"
    assert len(agents[1].trajectory.turns) >= 1, "Agent 1 should have turns in trajectory"

    # First turn contains the task description
    first_turn_0 = agents[0].trajectory.turns[0].content
    first_turn_1 = agents[1].trajectory.turns[0].content

    assert "NASA Moon Survival" in first_turn_0, "Task description should be in trajectory"
    assert "NASA Moon Survival" in first_turn_1, "Task description should be in trajectory"


def test_max_rounds_respected():
    """Test that collaboration respects max_rounds parameter."""
    agent_ids = [0, 1]

    for max_rounds in [1, 2, 3]:
        task = MoonSurvivalTask(agent_ids, max_rounds=max_rounds, expert_info_mode="none", seed=None)

        class RoundCounter(EchoBackend):
            def __init__(self):
                super().__init__()
                self.call_count = 0

            def invoke(self, *, agent_profile, trajectory):
                if len(trajectory.turns) > 0:  # Collaboration phase
                    self.call_count += 1
                return super().invoke(
                    agent_profile=agent_profile,
                    trajectory=trajectory
                )

        backend = RoundCounter()
        agents = [
            TeamAgent(
                profile=AgentProfile(
                    agent_id=agent_id,
                    name=f"Agent{agent_id}",
                    role="ranker",
                    system_prompt="Rank items"
                ),
                backend=backend
            )
            for agent_id in agent_ids
        ]

        individual_rankings = {i: f"Ranking {i}" for i in agent_ids}
        task._facilitate_collaboration(agents, individual_rankings)

        # Should make:
        # - max_rounds * num_agents calls for round discussions
        # - max_rounds * num_agents calls for per-round collection (one per agent per round)
        # - 1 call for final query
        # Total: 2 * max_rounds * num_agents + 1
        # Note: May make +1 additional call if parsing fails and retry is triggered
        expected_calls = 2 * max_rounds * len(agent_ids) + 1
        assert backend.call_count >= expected_calls, \
            f"Should make at least {expected_calls} collaboration calls for {max_rounds} rounds"
        assert backend.call_count <= expected_calls + 1, \
            f"Should make at most {expected_calls + 1} collaboration calls (including potential retry)"


def test_agents_retain_independent_thinking_during_collaboration():
    """Test agents see: [own thinking] -> [all stating rankings] -> [collaboration]."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)

    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Astronaut",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    # Collect individual rankings
    individual_rankings = task._collect_individual_rankings(agents)

    # Each agent has their own independent thinking (context + response)
    for agent in agents:
        assert len(agent.trajectory.turns) == 2, "Agent should have context + response"
        assert agent.trajectory.turns[0].speaker_id == -1, "Context turn should be a system message"
        assert agent.trajectory.turns[1].speaker_id == agent.profile.agent_id

    # Start collaboration
    task._facilitate_collaboration(agents, individual_rankings)

    # After collaboration setup, verify trajectory structure for each agent
    for agent in agents:
        # Turn 0-1: Agent's own independent thinking (context + response)
        assert agent.trajectory.turns[0].speaker_id == -1, \
            f"Agent {agent.profile.agent_id}: Turn 0 should be a system message (context)"
        assert agent.trajectory.turns[1].speaker_id == agent.profile.agent_id, \
            f"Agent {agent.profile.agent_id}: Turn 1 should be their response"

        # Turns 2-4: All agents stating their rankings (shared context)
        stating_turns = agent.trajectory.turns[2:5]
        stating_speaker_ids = [turn.speaker_id for turn in stating_turns]
        assert sorted(stating_speaker_ids) == [0, 1, 2], \
            f"Agent {agent.profile.agent_id}: Turns 2-4 should be all agents stating rankings"

        # All agents see the SAME stating turns in the SAME order
        for turn_idx in range(2, 5):
            turn = agent.trajectory.turns[turn_idx]
            assert "My individual ranking:" in turn.content, \
                f"Agent {agent.profile.agent_id}: Turn {turn_idx} should be a stating turn"

    # Verify all agents see the same stating turns (same order, same content)
    agent0_stating = agents[0].trajectory.turns[2:5]
    agent1_stating = agents[1].trajectory.turns[2:5]
    agent2_stating = agents[2].trajectory.turns[2:5]

    for i in range(3):
        assert agent0_stating[i].speaker_id == agent1_stating[i].speaker_id == agent2_stating[i].speaker_id, \
            f"All agents should see same speaker at stating turn {i}"
        assert agent0_stating[i].content == agent1_stating[i].content == agent2_stating[i].content, \
            f"All agents should see same content at stating turn {i}"


def test_round_notifications():
    """Test that agents receive round numbers and final query after rounds complete."""
    agent_ids = [0, 1]
    task = MoonSurvivalTask(agent_ids, max_rounds=2, expert_info_mode="none", seed=None)

    class ContextTracker(EchoBackend):
        def __init__(self):
            super().__init__()
            self.contexts = []

        def invoke(self, *, agent_profile, trajectory):
            if len(trajectory.turns) > 0:  # Collaboration phase
                # Get the last turn which contains the current round's context
                last_turn = trajectory.turns[-1]
                self.contexts.append({
                    "agent_id": agent_profile.agent_id,
                    "context": last_turn.content
                })
            return super().invoke(
                agent_profile=agent_profile,
                trajectory=trajectory
            )

    backend = ContextTracker()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="ranker",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    individual_rankings = {i: f"Ranking {i}" for i in agent_ids}
    task._facilitate_collaboration(agents, individual_rankings)

    # Check that contexts include round information
    collab_contexts = [c["context"] for c in backend.contexts]

    # The order of contexts captured:
    # 0-1: Initial prompts for round 0 (both agents)
    # 2-3: Per-round collection after round 0 (says "completed Round 1 of 2")
    # 4-5: Round 1 discussion prompts (says "ROUND 2 of 2" for second round)
    # 6-7: Per-round collection after round 1 (says "completed Round 2 of 2")
    # 8: Final query (says "All 2 discussion rounds are now complete")
    
    # First 2 calls should be initial prompt (round 0) for both agents
    assert "You will have 2 rounds" in collab_contexts[0]
    assert "You will have 2 rounds" in collab_contexts[1]

    # Next 2 calls are per-round collection after round 0 (says "completed Round 1")
    assert "You have completed Round 1 of 2 rounds of discussion" in collab_contexts[2]
    assert "You have completed Round 1 of 2 rounds of discussion" in collab_contexts[3]

    # Next 2 calls should be round 2 discussion prompts for both agents
    assert "ROUND 2 of 2" in collab_contexts[4]
    assert "ROUND 2 of 2" in collab_contexts[5]

    # Next 2 calls are per-round collection after round 1 (says "completed Round 2")
    assert "You have completed Round 2 of 2 rounds of discussion" in collab_contexts[6]
    assert "You have completed Round 2 of 2 rounds of discussion" in collab_contexts[7]

    # Final call should be to the selected agent for final ranking (randomized, not always agent 0)
    assert "All 2 discussion rounds are now complete" in collab_contexts[8]
    assert "FINAL TEAM RANKING:" in collab_contexts[8]
    # The final submitter is randomized, so just check that it's one of the agents
    assert backend.contexts[8]["agent_id"] in agent_ids, f"Final submitter should be one of {agent_ids}, got {backend.contexts[8]['agent_id']}"


def test_collaboration_turns_shared_across_agents():
    """Test that during collaboration, all agents see each other's discussion turns."""
    agent_ids = [0, 1, 2]
    task = MoonSurvivalTask(agent_ids, max_rounds=2, expert_info_mode="none", seed=None)

    backend = EchoBackend()
    agents = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="Astronaut",
                system_prompt="Rank items"
            ),
            backend=backend
        )
        for agent_id in agent_ids
    ]

    # Collect individual rankings
    individual_rankings = task._collect_individual_rankings(agents)

    # Run collaboration
    task._facilitate_collaboration(agents, individual_rankings)

    # Find which agent submitted the final ranking (the one with the final prompt)
    final_submitter_id = None
    for agent in agents:
        for i, turn in enumerate(agent.trajectory.turns):
            if turn.speaker_id == -1 and "discussion rounds are now complete" in turn.content:
                if i + 1 < len(agent.trajectory.turns) and agent.trajectory.turns[i + 1].speaker_id == agent.profile.agent_id:
                    final_submitter_id = agent.profile.agent_id
                    break
        if final_submitter_id is not None:
            break
    
    assert final_submitter_id is not None, "Should find an agent that submitted the final ranking"
    
    # The final submitter will have 1-2 extra turns (final query + potential retry), others should have same length
    final_submitter = next(a for a in agents if a.profile.agent_id == final_submitter_id)
    other_agents = [a for a in agents if a.profile.agent_id != final_submitter_id]
    
    assert len(other_agents) == 2, f"Should have exactly 2 non-queried agents, got {len(other_agents)}"
    
    final_submitter_extra_turns = len(final_submitter.trajectory.turns) - len(other_agents[0].trajectory.turns)
    assert final_submitter_extra_turns >= 1 and final_submitter_extra_turns <= 2, \
        f"Final submitter (agent {final_submitter_id}) should have 1-2 extra turns (final query + potential retry)"
    
    # Non-queried agents should have the same trajectory length
    other_0_length = len(other_agents[0].trajectory.turns)
    other_1_length = len(other_agents[1].trajectory.turns)
    assert other_0_length == other_1_length, \
        f"Non-queried agents should have same trajectory length (agent {other_agents[0].profile.agent_id}: {other_0_length}, agent {other_agents[1].profile.agent_id}: {other_1_length})"

    # Turns 0-1 are independent thinking (context + response) - unique to each agent
    assert agents[0].trajectory.turns[0].speaker_id == -1, "Context turn should be a system message"
    assert agents[0].trajectory.turns[1].speaker_id == 0
    assert agents[1].trajectory.turns[0].speaker_id == -1, "Context turn should be a system message"
    assert agents[1].trajectory.turns[1].speaker_id == 1
    assert agents[2].trajectory.turns[0].speaker_id == -1, "Context turn should be a system message"
    assert agents[2].trajectory.turns[1].speaker_id == 2

    # Check that agents see each other's responses (excluding system prompts, agent_id = -1)
    # Each agent has their own per-round collection prompt that differs with "You are Agent X",
    # so we only check non-system prompts are the same across agents.
    # Also skip the first 2 turns (initial task description + individual response) which are unique per agent.

    def get_non_system_turns(trajectory):
        """Get non-system turns (speaker_id != -1) that should be shared across agents.
        
        Excludes per-round collection responses which echo back the full prompt and aren't shared.
        """
        non_system = []
        for i, t in enumerate(trajectory.turns):
            # Skip first 2 turns (initial task + individual response)
            if i < 2:
                continue
            # Only include non-system turns (agent responses)
            if t.speaker_id != -1:
                # Exclude per-round collection responses - they contain the full task description
                # Per-round responses are individual and echo back the prompt, so they're not shared
                if "NASA Moon Survival Exercise" in t.content and "You are Agent" in t.content:
                    # This is a per-round collection response that echoes the prompt - skip it
                    continue
                non_system.append(t)
        return non_system

    # Get non-system turns for all agents
    non_system_final_submitter = get_non_system_turns(final_submitter.trajectory)
    non_system_other_0 = get_non_system_turns(other_agents[0].trajectory)
    non_system_other_1 = get_non_system_turns(other_agents[1].trajectory)

    # Final submitter will have extra final response, others should match
    assert len(non_system_final_submitter) >= len(non_system_other_0), \
        f"Final submitter (agent {final_submitter_id}) should have at least as many non-system turns"
    assert len(non_system_other_0) == len(non_system_other_1), \
        f"Non-queried agents (agent {other_agents[0].profile.agent_id} and agent {other_agents[1].profile.agent_id}) should have same non-system turn count"

    # Check that non-system turns match across agents (up to the point where non-queried agents stop)
    # All agents should see the same agent responses up until the final query
    for turn_idx in range(len(non_system_other_0)):
        turn_final_submitter = non_system_final_submitter[turn_idx]
        turn_other_0 = non_system_other_0[turn_idx]
        turn_other_1 = non_system_other_1[turn_idx]

        assert turn_final_submitter.speaker_id == turn_other_0.speaker_id == turn_other_1.speaker_id, \
            f"Non-system turn {turn_idx}: All agents should see same speaker (got {turn_final_submitter.speaker_id}, {turn_other_0.speaker_id}, {turn_other_1.speaker_id})"
        assert turn_final_submitter.content == turn_other_0.content == turn_other_1.content, \
            f"Non-system turn {turn_idx}: All agents should see same content"

    # The final turn should only be in the final submitter's trajectory
    final_turn = final_submitter.trajectory.turns[-1]
    assert final_turn.speaker_id == final_submitter_id, f"Final query should be from agent {final_submitter_id}"
    assert "FINAL TEAM RANKING:" in final_turn.content, "Final turn should contain final ranking"


def test_expert_info_mode_distributed():
    """Test that expert_info_mode='distributed' provides hidden info to agents."""
    agent_ids = [0, 1]

    class ContextChecker(EchoBackend):
        def __init__(self):
            super().__init__()
            self.received_contexts = []

        def invoke(self, *, agent_profile, trajectory):
            # Get the first turn which contains the context
            if trajectory.turns:
                self.received_contexts.append(trajectory.turns[0].content)
            return super().invoke(
                agent_profile=agent_profile,
                trajectory=trajectory
            )

    # Test WITH distributed info
    task_with_distributed = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="distributed", seed=None)
    backend_with_distributed = ContextChecker()
    agents_with_distributed = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="ranker",
                system_prompt="Rank items"
            ),
            backend=backend_with_distributed
        )
        for agent_id in agent_ids
    ]

    task_with_distributed._collect_individual_rankings(agents_with_distributed)

    for ctx in backend_with_distributed.received_contexts:
        assert ctx is not None, "Should provide context"
        assert "You understand" in ctx, "Should contain hidden info perspective"
        assert "ONLY YOU KNOW" in ctx, "Should emphasize exclusivity of hidden info"

    # Test WITHOUT info (none mode)
    task_without_info = MoonSurvivalTask(agent_ids, max_rounds=1, expert_info_mode="none", seed=None)
    backend_without_info = ContextChecker()
    agents_without_info = [
        TeamAgent(
            profile=AgentProfile(
                agent_id=agent_id,
                name=f"Agent{agent_id}",
                role="ranker",
                system_prompt="Rank items"
            ),
            backend=backend_without_info
        )
        for agent_id in agent_ids
    ]

    task_without_info._collect_individual_rankings(agents_without_info)

    for ctx in backend_without_info.received_contexts:
        assert ctx is not None, "Should provide context"
        assert "You understand" not in ctx, "Should NOT contain hidden info perspective"
        assert "ONLY YOU KNOW" not in ctx, "Should NOT emphasize exclusivity"


def test_reveal_distributed_experts_message():
    """Test that reveal_distributed_experts mode reveals which items each agent is expert in."""
    from teamwork import AgentProfile, EchoBackend, TeamAgent
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
        expert_info_mode="distributed",
        decision_mode="reveal_distributed_experts",
        seed=42,
    )

    task.execute(agents)

    # Check that all agents received the revelation message
    for agent in agents:
        system_turns = [turn for turn in agent.trajectory.turns if turn.speaker_id == -1]
        system_text = " ".join(turn.content for turn in system_turns)
        
        # Should contain revelation about which agents have privileged information on which items
        assert "has privileged expert information on the following" in system_text, f"Agent {agent.profile.agent_id} should see expert item revelations"
        
        # Should mention all agents that have items (non-adversarial agents with info)
        for other_agent_id in agent_ids:
            if other_agent_id in task.items_expert_in_per_agent and task.items_expert_in_per_agent[other_agent_id]:
                assert f"Agent {other_agent_id}" in system_text, f"Agent {agent.profile.agent_id} should see revelation about Agent {other_agent_id}"