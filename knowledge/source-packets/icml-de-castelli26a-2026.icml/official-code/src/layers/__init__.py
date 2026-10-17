import torch

from src.layers.metrics import (
    RMSE,
    CrossEntropy,
    accuracy,
    f1_score,
    precision,
    recall,
    roc_auc_score,
    balanced_accuracy,
    MAPE,
)

SCORES = {
    "MAE": torch.nn.L1Loss(),
    "MSE": torch.nn.MSELoss(),
    "RMSE": RMSE(),
    "MAPE": MAPE,
    "CrossEntropy": CrossEntropy(),
    "BinaryClassificationLoss": torch.nn.BCEWithLogitsLoss(reduction="mean"),
    "Accuracy": accuracy,
    "F1": f1_score,
    "RocAuc": roc_auc_score,
    "BalancedAccuracy": balanced_accuracy,
    "Precision": precision,
    "Recall": recall,
}

DESCENDING_SCORES = [
    "MAE",
    "MSE",
    "RMSE",
    "CrossEntropy",
    "BinaryClassificationLoss",
]
ASCENDING_SCORES = [
    "Accuracy",
    "F1",
    "Precision",
    "Recall",
    "RocAuc",
    "BalancedAccuracy",
]
