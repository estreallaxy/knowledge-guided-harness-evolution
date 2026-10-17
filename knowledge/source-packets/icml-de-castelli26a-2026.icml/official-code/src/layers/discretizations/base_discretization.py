import torch


class Discretization(torch.nn.Module):
    """Base class for ODE discretization schemes (e.g. forward Euler).

    Subclasses implement :meth:`forward`, advancing a state ``h`` by one step
    given the vector field ``conv`` evaluated at ``h``.
    """

    def __init__(self, *args, **kwargs):
        # Subclasses set ``self.epsilon`` (the step size) in their own __init__.
        super().__init__()
        self.epsilon = None

    def forward(self, h: torch.Tensor, conv: torch.Tensor) -> torch.Tensor:
        # Implemented by subclasses (e.g. ForwardEuler).
        raise NotImplementedError

    def reset_state(self) -> None:
        # No integration state to reset by default.
        pass
