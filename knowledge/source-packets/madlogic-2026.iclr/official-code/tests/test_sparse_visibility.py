from types import SimpleNamespace
import unittest

from agentverse.environments.rules.visibility.sparse import SparseVisibility


class SparseVisibilityTest(unittest.TestCase):
    def test_closed_gate_can_reopen_when_preference_recovers(self) -> None:
        visibility = SparseVisibility.model_construct(
            lambda_param=0.0,
            alpha=1.0,
            model=None,
        )
        environment = SimpleNamespace(
            cnt_turn=0,
            agents=[SimpleNamespace(name="agent_a"), SimpleNamespace(name="agent_b")],
            last_messages=[],
        )

        def update(round_number: int, confidence_a: float, confidence_b: float) -> None:
            environment.cnt_turn = round_number
            environment.last_messages = [
                SimpleNamespace(sender="agent_a", content=f"Confidence: {confidence_a}"),
                SimpleNamespace(sender="agent_b", content=f"Confidence: {confidence_b}"),
            ]
            visibility.update_visible_agents(environment)

        update(0, confidence_a=0.5, confidence_b=0.5)
        self.assertEqual(visibility.gates[0][0, 1], 1)

        update(1, confidence_a=0.2, confidence_b=0.8)
        self.assertEqual(visibility.gates[1][0, 1], 0)

        update(2, confidence_a=0.9, confidence_b=0.1)
        self.assertGreaterEqual(
            visibility.current_preferences[2][0, 1],
            visibility.historical_preferences[1][0, 1],
        )
        self.assertEqual(visibility.gates[2][0, 1], 1)


if __name__ == "__main__":
    unittest.main()
