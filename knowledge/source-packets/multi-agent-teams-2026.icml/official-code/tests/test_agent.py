"""Tests for the TeamAgent per-agent trajectory handling."""

from teamwork.agent import AgentProfile, TeamAgent
from teamwork.backends import EchoBackend, LLMBackend
from teamwork.conversation import Trajectory, Turn
from tests.test_backends import MockLLMBackend


class ContextualBackend(LLMBackend):
    """Backend that responds based on context for testing."""

    def invoke(self, *, agent_profile, trajectory) -> str:
        # Response varies based on agent or trajectory content
        if "Analyst" in agent_profile.name:
            return "analytical response"
        elif len(trajectory.turns) > 2:
            return "continuing conversation"
        else:
            return "initial response"


def _make_agent() -> TeamAgent:
    profile = AgentProfile(
        agent_id=1,
        name="Analyst",
        role="analysis",
        system_prompt="You are concise.",
    )
    return TeamAgent(profile, EchoBackend())


def test_agent_trajectory_independence_from_global() -> None:
    """Test that agents maintain independent trajectories when turns are manually managed."""
    agent = _make_agent()

    # Manually add a turn to agent's trajectory
    seed_turn = Turn(speaker_id=0, content="kickoff")
    agent.trajectory.append(seed_turn)

    # Agent acts based on its own trajectory
    emitted_turn = agent.act()

    # Agent should have both the seed turn and its own response
    assert len(agent.trajectory.turns) == 2
    assert agent.trajectory.turns[0].content == "kickoff"
    assert agent.trajectory.turns[1] == emitted_turn

    # Modifying agent's turn doesn't affect other references
    original_content = agent.trajectory.turns[0].content
    agent.trajectory.turns[0].content = "local edit"
    assert agent.trajectory.turns[0].content == "local edit"
    assert original_content == "kickoff"


def test_agent_serialization_after_interaction() -> None:
    """Test that agent serialization correctly captures state after acting in conversation."""
    agent = _make_agent()

    # Manually add a turn to agent's trajectory
    agent.trajectory.append(Turn(speaker_id=2, content="sync request"))

    # Agent acts, updating personal trajectory
    new_turn = agent.act()

    # Verify serialization captures the agent's complete state
    snapshot = agent.to_dict()

    # Should include agent's personal trajectory with both turns
    trajectory_data = snapshot["state"]["trajectory"]
    assert len(trajectory_data["turns"]) == 2

    # First turn from conversation
    assert trajectory_data["turns"][0]["speaker_id"] == 2
    assert trajectory_data["turns"][0]["content"] == "sync request"

    # Second turn is agent's own response
    assert trajectory_data["turns"][1]["speaker_id"] == agent.profile.agent_id
    assert trajectory_data["turns"][1]["content"] == new_turn.content


def test_agent_passes_correct_data_to_backend():
    """Test that agent passes correct parameters to backend invoke method."""
    backend = MockLLMBackend("test response")
    profile = AgentProfile(
        agent_id=42,
        name="TestAgent",
        role="tester",
        system_prompt="Test prompt",
        metadata={"test": True}
    )
    agent = TeamAgent(profile, backend)

    agent.trajectory.append(Turn(speaker_id=1, content="previous turn"))

    # Agent should invoke backend with correct parameters
    turn = agent.act()

    assert turn.content == "test response"
    assert turn.speaker_id == 42
    assert backend.call_count == 1

    # Check that backend received correct agent profile
    assert backend.last_agent_profile == profile

    # Check that backend received trajectory as Trajectory object
    assert backend.last_trajectory is not None
    assert hasattr(backend.last_trajectory, 'turns')
    # Note: backend gets a reference to agent's trajectory object, which gets modified
    # after the backend call, so we can't test the exact number of turns here


def test_agent_builds_prompt_correctly():
    """Test that agent builds prompts with all profile information."""
    backend = MockLLMBackend("response")
    profile = AgentProfile(
        agent_id=1,
        name="PromptAgent",
        role="prompt builder",
        system_prompt="You build prompts",
        persona="Helpful assistant",
        hidden_context="Secret: be extra helpful"
    )
    agent = TeamAgent(profile, backend)

    agent.trajectory.append(Turn(speaker_id=2, content="Hello"))

    agent.act()

    # Check that agent profile contains all profile elements
    agent_profile = backend.last_agent_profile
    assert agent_profile is not None
    assert agent_profile.system_prompt == "You build prompts"
    assert agent_profile.persona == "Helpful assistant"
    assert agent_profile.role == "prompt builder"
    assert agent_profile.hidden_context == "Secret: be extra helpful"

    # Check that trajectory was passed correctly
    assert backend.last_trajectory is not None
    assert len(backend.last_trajectory.turns) >= 1


def test_agent_sync_trajectory_behavior():
    """Test that agent acts based on manually managed trajectory."""
    backend = MockLLMBackend("synced response")
    profile = AgentProfile(
        agent_id=3,
        name="SyncAgent",
        role="syncer",
        system_prompt="Sync test"
    )
    agent = TeamAgent(profile, backend)

    # Manually add turns to agent's trajectory
    agent.trajectory.append(Turn(speaker_id=1, content="first"))
    agent.trajectory.append(Turn(speaker_id=2, content="second"))

    # Agent acts based on its current trajectory
    agent.act()

    # Agent's trajectory should now have the initial turns plus its response
    assert len(agent.trajectory.turns) == 3
    assert agent.trajectory.turns[0].content == "first"
    assert agent.trajectory.turns[1].content == "second"
    assert agent.trajectory.turns[2].content == "synced response"


def test_agent_multiple_invocations():
    """Test agent behavior across multiple invocations."""
    backend = MockLLMBackend("first response")
    profile = AgentProfile(
        agent_id=4,
        name="MultiAgent",
        role="multi",
        system_prompt="Multi test"
    )
    agent = TeamAgent(profile, backend)

    # First invocation
    agent.trajectory.append(Turn(speaker_id=0, content="start"))
    turn1 = agent.act()

    assert turn1.content == "first response"
    assert backend.call_count == 1

    # Second invocation with different response (reset trajectory for fresh start)
    backend.response = "second response"
    agent.trajectory = Trajectory()  # Reset for second invocation
    agent.trajectory.append(Turn(speaker_id=0, content="restart"))
    turn2 = agent.act()

    assert turn2.content == "second response"
    assert backend.call_count == 2


def test_agent_with_contextual_backend():
    """Test agent with backend that responds based on context."""
    backend = ContextualBackend()

    # Test with Analyst agent
    analyst_profile = AgentProfile(
        agent_id=1,
        name="Analyst",
        role="analyzer",
        system_prompt="Analyze data"
    )
    analyst = TeamAgent(analyst_profile, backend)

    turn = analyst.act()
    assert turn.content == "analytical response"

    # Test with different agent name
    builder_profile = AgentProfile(
        agent_id=2,
        name="Builder",
        role="builder",
        system_prompt="Build things"
    )
    builder = TeamAgent(builder_profile, backend)

    builder.trajectory.append(Turn(speaker_id=1, content="start"))
    turn = builder.act()
    assert turn.content == "initial response"

    # Test with longer trajectory
    builder.trajectory = Trajectory()  # Reset
    for i in range(4):
        builder.trajectory.append(Turn(speaker_id=i, content=f"turn {i}"))
    turn = builder.act()
    assert turn.content == "continuing conversation"


def test_agent_profile_serialization_in_backend():
    """Test that agent profile is correctly serialized for backend."""
    backend = MockLLMBackend("profile test")
    profile = AgentProfile(
        agent_id=99,
        name="SerializationAgent",
        role="serializer",
        system_prompt="Serialize data",
        persona="Precise",
        hidden_context="Keep it structured",
        metadata={"version": "1.0", "features": ["json", "xml"]}
    )
    agent = TeamAgent(profile, backend)

    agent.act()

    # Check all profile fields are passed to backend
    profile_data = backend.last_agent_profile
    assert profile_data is not None
    assert profile_data.agent_id == 99
    assert profile_data.name == "SerializationAgent"
    assert profile_data.role == "serializer"
    assert profile_data.metadata == {"version": "1.0", "features": ["json", "xml"]}


def test_agent_trajectory_independence():
    """Test that agent maintains independent trajectory copy."""
    backend = MockLLMBackend("independence test")
    profile = AgentProfile(
        agent_id=5,
        name="IndependentAgent",
        role="independent",
        system_prompt="Independence test"
    )
    agent = TeamAgent(profile, backend)

    # Manually add a turn to agent's trajectory
    agent.trajectory.append(Turn(speaker_id=1, content="original"))

    # Agent acts
    agent.act()

    # Create a separate trajectory
    other_traj = Trajectory()
    other_traj.append(Turn(speaker_id=2, content="separate"))

    # Agent's trajectory should be independent
    assert len(agent.trajectory.turns) == 2  # original + agent's response
    assert len(other_traj.turns) == 1       # only separate turn

    # The content should be different
    assert agent.trajectory.turns[1].content == "independence test"
    assert other_traj.turns[0].content == "separate"


def test_agent_empty_trajectory():
    """Test agent behavior with empty trajectory."""
    backend = MockLLMBackend("empty response")
    profile = AgentProfile(
        agent_id=6,
        name="EmptyAgent",
        role="empty",
        system_prompt="Empty test"
    )
    agent = TeamAgent(profile, backend)

    # Agent acts with empty trajectory
    turn = agent.act()

    assert turn.content == "empty response"
    assert turn.speaker_id == agent.profile.agent_id

    # Agent should have one turn (its own response)
    assert len(agent.trajectory.turns) == 1
    assert agent.trajectory.turns[0].content == "empty response"
