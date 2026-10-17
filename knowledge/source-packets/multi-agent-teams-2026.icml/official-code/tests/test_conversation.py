"""Basic tests for the teamwork core data types."""

from teamwork.conversation import Trajectory, Turn

def test_trajectory_append_and_last_turn():
    trajectory = Trajectory()
    assert trajectory.last_turn() is None

    first = Turn(speaker_id=1, content="kickoff")
    trajectory.append(first)

    assert trajectory.last_turn() is first
    assert trajectory.turns == [first]
    assert trajectory.as_dict() == {"turns": [first.as_dict()]}


def test_trajectory_extend_multiple_turns():
    trajectory = Trajectory()

    turns = (
        Turn(speaker_id=2, content="status update"),
        Turn(speaker_id=3, content="next steps"),
    )

    trajectory.extend(turns)

    assert trajectory.turns == list(turns)
    assert trajectory.last_turn() is turns[-1]
    assert trajectory.as_dict() == {"turns": [t.as_dict() for t in turns]}


def test_trajectory_from_dict():
    """Test creating Trajectory from dictionary representation."""
    data = {
        "turns": [
            {"speaker_id": 1, "content": "Hello"},
            {"speaker_id": 2, "content": "Hi there"},
            {"speaker_id": 1, "content": "How are you?"}
        ]
    }

    trajectory = Trajectory.from_dict(data)

    assert len(trajectory.turns) == 3
    assert trajectory.turns[0].speaker_id == 1
    assert trajectory.turns[0].content == "Hello"
    assert trajectory.turns[1].speaker_id == 2
    assert trajectory.turns[1].content == "Hi there"
    assert trajectory.turns[2].speaker_id == 1
    assert trajectory.turns[2].content == "How are you?"


def test_trajectory_from_dict_empty():
    """Test creating Trajectory from empty dictionary."""
    data = {"turns": []}
    trajectory = Trajectory.from_dict(data)
    assert len(trajectory.turns) == 0
    assert trajectory.last_turn() is None


def test_trajectory_from_dict_missing_turns():
    """Test creating Trajectory from dictionary without turns key."""
    data = {}
    trajectory = Trajectory.from_dict(data)
    assert len(trajectory.turns) == 0
    assert trajectory.last_turn() is None


def test_trajectory_roundtrip_dict():
    """Test that as_dict and from_dict are inverses."""
    original = Trajectory()
    original.append(Turn(speaker_id=1, content="First"))
    original.append(Turn(speaker_id=2, content="Second"))

    # Convert to dict and back
    dict_repr = original.as_dict()
    reconstructed = Trajectory.from_dict(dict_repr)

    # Should have same content
    assert len(reconstructed.turns) == len(original.turns)
    for orig_turn, recon_turn in zip(original.turns, reconstructed.turns):
        assert orig_turn.speaker_id == recon_turn.speaker_id
        assert orig_turn.content == recon_turn.content
