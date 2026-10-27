"""
Module: Baseline Model Training & Evaluation
Huấn luyện mô hình cơ sở LightGBM trên tập dữ liệu đã qua kỹ nghệ đặc trưng và đánh giá theo chuẩn khoa học:
- ROC-AUC
- PR-AUC (Average Precision)
- Ma trận chi phí tài chính thực tế (Financial Cost Impact)
"""

import numpy as np
import polars as pl
from typing import List, Dict, Any, Tuple
import lightgbm as lgb
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    brier_score_loss,
)
from src.domain.cost_matrix import CostMatrix, TriageDecision


def get_feature_columns(df: pl.DataFrame) -> List[str]:
    """Chọn lọc các cột đặc trưng số và danh mục phù hợp cho LightGBM."""
    exclude_cols = {
        "TransactionID",
        "isFraud",
        "TransactionDT",
        "Day",
        "Card_ID",
        "Client_UID",
        "Card_Birth_Day",
    }

    feature_cols = []
    for col, dtype in zip(df.columns, df.dtypes):
        if col in exclude_cols:
            continue
        # Giữ lại các cột số hoặc chuỗi để LightGBM xử lý
        if dtype in (
            pl.Float64, pl.Float32,
            pl.Int64, pl.Int32, pl.Int16, pl.Int8,
            pl.UInt64, pl.UInt32, pl.UInt16, pl.UInt8,
            pl.String
        ):
            feature_cols.append(col)

    return feature_cols


def prepare_lightgbm_data(
    train_df: pl.DataFrame,
    val_df: pl.DataFrame,
    feature_cols: List[str]
) -> Tuple[lgb.Dataset, lgb.Dataset, List[str]]:
    """Chuyển đổi dữ liệu Polars sang LightGBM Dataset với định danh biến Categorical."""
    cols_to_select = list(dict.fromkeys(feature_cols + ["isFraud"]))
    train_pdf = train_df.select(cols_to_select).to_pandas()
    val_pdf = val_df.select(cols_to_select).to_pandas()

    categorical_features = []
    for col in feature_cols:
        if train_pdf[col].dtype == "object":
            train_pdf[col] = train_pdf[col].astype("category")
            val_pdf[col] = val_pdf[col].astype("category")
            categorical_features.append(col)

    X_train = train_pdf[feature_cols]
    y_train = train_pdf["isFraud"]

    X_val = val_pdf[feature_cols]
    y_val = val_pdf["isFraud"]

    train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=categorical_features, free_raw_data=False)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data, categorical_feature=categorical_features, free_raw_data=False)

    return train_data, val_data, categorical_features


def train_baseline_lightgbm(
    train_data: lgb.Dataset,
    val_data: lgb.Dataset,
    categorical_features: List[str],
    scale_pos_weight: float = 1.0,
    num_boost_round: int = 500,
    early_stopping_rounds: int = 30
) -> lgb.Booster:
    """Huấn luyện mô hình LightGBM với early stopping."""
    params = {
        "objective": "binary",
        "metric": "auc",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 63,
        "max_depth": -1,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 1,
        "scale_pos_weight": scale_pos_weight,
        "verbose": -1,
        "n_jobs": -1,
        "seed": 42
    }

    callbacks = [
        lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=False),
        lgb.log_evaluation(period=100)
    ]

    model = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=[train_data, val_data],
        valid_names=["train", "valid"],
        callbacks=callbacks
    )

    return model


def evaluate_model(
    model: lgb.Booster,
    test_df: pl.DataFrame,
    feature_cols: List[str],
    cost_matrix: CostMatrix = CostMatrix(),
    threshold: float = 0.5
) -> Dict[str, Any]:
    """Đánh giá toàn diện mô hình: ROC-AUC, PR-AUC, Brier score và Tổng thiệt hại tài chính."""
    cols_to_select = list(dict.fromkeys(feature_cols + ["isFraud", "TransactionAmt"]))
    test_pdf = test_df.select(cols_to_select).to_pandas()
    for col in feature_cols:
        if test_pdf[col].dtype == "object":
            test_pdf[col] = test_pdf[col].astype("category")

    X_test = test_pdf[feature_cols]
    y_test = test_pdf["isFraud"].values
    amts = test_pdf["TransactionAmt"].values

    y_pred_proba = model.predict(X_test)
    y_pred = (y_pred_proba >= threshold).astype(int)

    roc_auc = float(roc_auc_score(y_test, y_pred_proba))
    pr_auc = float(average_precision_score(y_test, y_pred_proba))
    brier = float(brier_score_loss(y_test, y_pred_proba))

    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

    # Tính toán chi phí tài chính thực tế
    total_financial_loss = 0.0
    for pred, true_label, amt in zip(y_pred, y_test, amts):
        decision = TriageDecision.BLOCK if pred == 1 else TriageDecision.APPROVE
        total_financial_loss += cost_matrix.calculate_cost(decision, true_label, amt)

    return {
        "threshold": threshold,
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "confusion_matrix": {
            "TN": int(tn),
            "FP": int(fp),
            "FN": int(fn),
            "TP": int(tp)
        },
        "total_financial_loss_usd": round(total_financial_loss, 2),
        "total_transactions": len(y_test),
        "fraud_count": int(np.sum(y_test))
    }
