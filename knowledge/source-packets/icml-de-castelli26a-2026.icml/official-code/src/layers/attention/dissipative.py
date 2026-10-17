import torch


class AdaptiveDissipativity(torch.nn.Module):
    """Adaptive damping term ``Gamma = diag(sigmoid(d))``.

    Produces the diagonal damping matrix used by the LAMP dynamics. The diagonal
    ``d`` is learned and squashed by a sigmoid, initialized so that
    ``sigmoid(d) == gamma``.
    """

    def __init__(self, in_channels: int, gamma: float) -> None:
        """
        :param in_channels: Hidden-state size (diagonal length).
        :param gamma: Target / initial damping value.
        """
        super().__init__()

        self.diagonal = torch.nn.Parameter(torch.empty(in_channels), requires_grad=True)
        self.diagonal.data = torch.log(
            torch.full((in_channels,), gamma / (1 - gamma), dtype=torch.float32)
        )

    def forward(self) -> torch.Tensor:
        # Gamma = diag(activation(d)).
        return torch.diag(torch.sigmoid(self.diagonal))
