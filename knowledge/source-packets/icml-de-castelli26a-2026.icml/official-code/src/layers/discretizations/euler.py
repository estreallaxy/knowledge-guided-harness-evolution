import torch
import torch.nn.functional as F

from src.layers.discretizations.base_discretization import Discretization


class ForwardEuler(Discretization):
    """Explicit forward-Euler step: ``h <- h + epsilon * activation(conv)``."""

    def __init__(self, epsilon: float, activation: str = "tanh", **kwargs) -> None:
        super().__init__(**kwargs)
        self.epsilon = epsilon
        if activation == "identity":
            self.activation = torch.nn.Identity()
        else:
            try:
                self.activation = getattr(torch, activation)
            except AttributeError:
                self.activation = getattr(F, activation)

    def forward(self, h: torch.Tensor, conv: torch.Tensor) -> torch.Tensor:
        """Advance the state by one forward-Euler step.

        :param h: Current state.
        :param conv: Vector field evaluated at ``h``.
        :return: ``h + epsilon * activation(conv)``.
        """
        # Euler update with step size epsilon.
        return h + self.epsilon * self.activation(conv)
