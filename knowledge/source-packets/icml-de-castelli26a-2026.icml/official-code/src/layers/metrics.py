import torch
from sklearn.metrics import roc_auc_score as sk_roc_auc_score, balanced_accuracy_score


class RMSE(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.mse = torch.nn.MSELoss()

    def forward(self, y_pred, y_true):
        return torch.sqrt(self.mse(y_pred, y_true))


class CrossEntropy(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.cross_entropy = torch.nn.CrossEntropyLoss()

    def forward(self, y_pred, y_true):
        targets = y_true.argmax(dim=1)
        return self.cross_entropy(y_pred, targets)


def _prepare_labels(y_pred, y_true, threshold=0.5):
    # handles logits or scores (no sigmoid)
    if y_pred.ndim > 1 and y_pred.size(-1) > 1:
        y_pred = torch.argmax(y_pred, dim=-1)
    else:
        y_pred = (torch.sigmoid(y_pred) > threshold).long()

    if y_true.ndim > 1 and y_true.size(-1) > 1:
        y_true = torch.argmax(y_true, dim=-1)

    return y_pred.int(), y_true.int()


def precision(y_pred, y_true, threshold=0.5):
    """
    computes precision for binary classification
    works with raw scores (no sigmoid)
    """
    y_pred, y_true = _prepare_labels(y_pred, y_true, threshold)
    tp = torch.sum((y_pred == 1) & (y_true == 1))
    fp = torch.sum((y_pred == 1) & (y_true == 0))
    return tp / (tp + fp) if (tp + fp).item() > 0 else torch.tensor(0.0)


def recall(y_pred, y_true, threshold=0.5):
    """
    computes recall for binary classification
    works with raw scores (no sigmoid)
    """
    y_pred, y_true = _prepare_labels(y_pred, y_true, threshold)
    tp = torch.sum((y_pred == 1) & (y_true == 1))
    fn = torch.sum((y_pred == 0) & (y_true == 1))
    return tp / (tp + fn) if (tp + fn).item() > 0 else torch.tensor(0.0)


def f1_score(y_pred, y_true, threshold=0.5):
    """
    computes f1 score for binary classification
    works with raw scores (no sigmoid)
    """
    p = precision(y_pred, y_true, threshold)
    r = recall(y_pred, y_true, threshold)
    return 2 * p * r / (p + r) if (p + r).item() > 0 else torch.tensor(0.0)


def accuracy(y_pred, y_true, threshold=0.5):
    """
    computes accuracy for binary classification
    works with raw scores (no sigmoid)
    """
    y_pred, y_true = _prepare_labels(y_pred, y_true, threshold)
    correct = torch.sum(y_pred == y_true)
    return correct.float() / y_true.numel()


def roc_auc_score(y_pred, y_true):
    """computes roc auc score for binary classification from raw logits or probabilities"""
    if y_true.ndim > 1 and y_true.size(-1) > 1:
        y_true = torch.argmax(y_true, dim=-1)

    if y_pred.ndim > 1 and y_pred.size(-1) > 1:
        y_pred = torch.softmax(y_pred, dim=-1)[:, 1]
    else:
        y_pred = torch.sigmoid(y_pred).view(-1)

    return torch.tensor(sk_roc_auc_score(y_true.cpu().numpy(), y_pred.cpu().numpy()))


def balanced_accuracy(y_pred, y_true, threshold=0.5):
    """
    computes balanced accuracy for binary classification
    works with raw scores (no sigmoid)
    """
    y_pred, y_true = _prepare_labels(y_pred, y_true, threshold)
    return torch.tensor(
        balanced_accuracy_score(y_true.cpu().numpy(), y_pred.cpu().numpy())
    )


def MAPE(y_pred, y_true):
    """
    computes Mean Absolute Percentage Error
    """
    epsilon = 1e-8  # to avoid division by zero
    ape = torch.abs((y_true - y_pred) / (y_true + epsilon))
    return torch.mean(ape) * 100
