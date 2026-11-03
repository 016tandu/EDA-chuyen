"""
Usecase: Conformal Prediction & Cost-Sensitive Calibration Engine
Hiện thực hóa thuật toán:
1. Mondrian (Class-Conditional) Split Conformal Prediction
2. Tính toán phân vị Non-conformity Score trên tập Calib Set
3. Tối ưu hóa ngưỡng chi phí tài chính (Cost-Sensitive Optimization)
4. Phân loại 3 ngã rẽ: APPROVE, STEP_UP_2FA, BLOCK
"""

import numpy as np
import polars as pl
from typing import Tuple, Dict, Any, List, Optional
import lightgbm as lgb
from scipy.optimize import minimize_scalar

from src.domain.cost_matrix import CostMatrix, TriageDecision
from src.domain.conformal import (
    ConformalPredictionSet,
    ConformalCalibrationConfig,
    CalibrationArtifacts,
)


class ConformalEngine:
    def __init__(self, config: Optional[ConformalCalibrationConfig] = None, cost_matrix: Optional[CostMatrix] = None):
        self.config = config or ConformalCalibrationConfig()
        self.cost_matrix = cost_matrix or CostMatrix()
        self.artifacts: Optional[CalibrationArtifacts] = None

    def calibrate(
        self,
        model: lgb.Booster,
        calib_df: pl.DataFrame,
        feature_cols: List[str]
    ) -> CalibrationArtifacts:
        """
        Hiệu chuẩn trên tập Calib Set (Mondrian Conformal Prediction):
        - Lớp 0 (Khách thật): s_i = p_i (xác suất gian lận)
        - Lớp 1 (Kẻ gian): s_i = 1 - p_i (xác suất hợp lệ)
        """
        cols_to_select = list(dict.fromkeys(feature_cols + ["isFraud", "TransactionAmt"]))
        calib_pdf = calib_df.select(cols_to_select).to_pandas()

        for col in feature_cols:
            if calib_pdf[col].dtype == "object":
                calib_pdf[col] = calib_pdf[col].astype("category")

        X_calib = calib_pdf[feature_cols]
        y_calib = calib_pdf["isFraud"].values
        amts_calib = calib_pdf["TransactionAmt"].values

        # Dự báo xác suất p = P(isFraud = 1)
        p_calib = model.predict(X_calib)

        # 1. Tách điểm non-conformity theo từng lớp (Mondrian)
        scores_0 = p_calib[y_calib == 0]       # Non-conformity score của khách thật
        scores_1 = 1.0 - p_calib[y_calib == 1] # Non-conformity score của kẻ gian

        n_0 = len(scores_0)
        n_1 = len(scores_1)

        # 2. Tính phân vị chuẩn Conformal với hiệu chỉnh mẫu hữu hạn: ceil((n + 1)(1 - alpha)) / n
        q_level_0 = np.clip(np.ceil((n_0 + 1) * (1.0 - self.config.alpha_legit)) / n_0, 0.0, 1.0)
        q_level_1 = np.clip(np.ceil((n_1 + 1) * (1.0 - self.config.alpha_fraud)) / n_1, 0.0, 1.0)

        q_hat_0 = float(np.quantile(scores_0, q_level_0))
        q_hat_1 = float(np.quantile(scores_1, q_level_1))

        # 3. Tối ưu hóa ngưỡng chi phí (Cost-Sensitive Threshold Tuning)
        # Tìm ngưỡng (t_low, t_high) tối thiểu hóa ma trận chi phí thực tế trên tập Calib
        opt_t_low, opt_t_high, opt_cost = self._find_optimal_cost_thresholds(
            p_calib, y_calib, amts_calib, q_hat_0, q_hat_1
        )

        self.artifacts = CalibrationArtifacts(
            q_hat_0=q_hat_0,
            q_hat_1=q_hat_1,
            config=self.config,
            optimal_cost_thresholds={
                "t_approve": float(opt_t_low),
                "t_block": float(opt_t_high),
                "calib_min_cost": float(opt_cost),
            },
            metadata={
                "n_calib_total": len(y_calib),
                "n_calib_legit": int(n_0),
                "n_calib_fraud": int(n_1),
                "q_level_0": float(q_level_0),
                "q_level_1": float(q_level_1),
            }
        )
        return self.artifacts

    def _find_optimal_cost_thresholds(
        self,
        p_calib: np.ndarray,
        y_calib: np.ndarray,
        amts: np.ndarray,
        q_hat_0: float,
        q_hat_1: float
    ) -> Tuple[float, float, float]:
        """
        Quét lưới đa chiều để tìm cặp ngưỡng (t_low, t_high) tối ưu hóa chi phí tài chính:
        - p < t_low: Duyệt (APPROVE)
        - t_low <= p < t_high: Bắt xác thực OTP (STEP_UP_2FA)
        - p >= t_high: Chặn (BLOCK)
        """
        best_cost = float("inf")
        best_t_low = 1.0 - q_hat_1
        best_t_high = q_hat_0

        # Lưới ứng viên được neo theo các phân vị rủi ro
        candidate_lows = np.linspace(0.005, 0.15, 30)
        candidate_highs = np.linspace(0.30, 0.90, 30)

        for t_low in candidate_lows:
            for t_high in candidate_highs:
                if t_low >= t_high:
                    continue

                # Quyết định
                # APPROVE: p < t_low
                # BLOCK: p >= t_high
                # STEP_UP_2FA: t_low <= p < t_high
                cost = 0.0

                # Lớp gian lận (y=1)
                fraud_mask = (y_calib == 1)
                fraud_p = p_calib[fraud_mask]
                fraud_amts = amts[fraud_mask]

                # FN: p < t_low -> Mất toàn bộ số tiền
                fn_mask = (fraud_p < t_low)
                cost += np.sum(fraud_amts[fn_mask])

                # 2FA Fraud: t_low <= p < t_high -> Bắt được sau OTP, tốn phí SMS $0.5
                step_fraud_mask = (fraud_p >= t_low) & (fraud_p < t_high)
                cost += np.sum(step_fraud_mask) * self.cost_matrix.cost_step_up_fraud

                # TP: p >= t_high -> Chặn trực tiếp, tốn $1.0
                tp_mask = (fraud_p >= t_high)
                cost += np.sum(tp_mask) * self.cost_matrix.cost_tp

                # Lớp hợp lệ (y=0)
                legit_mask = (y_calib == 0)
                legit_p = p_calib[legit_mask]

                # FP: p >= t_high -> Chặn nhầm, tốn $5.0
                fp_mask = (legit_p >= t_high)
                cost += np.sum(fp_mask) * self.cost_matrix.cost_fp

                # 2FA Legit: t_low <= p < t_high -> Khách gõ OTP, tốn $0.2
                step_legit_mask = (legit_p >= t_low) & (legit_p < t_high)
                cost += np.sum(step_legit_mask) * self.cost_matrix.cost_step_up_legit

                if cost < best_cost:
                    best_cost = cost
                    best_t_low = t_low
                    best_t_high = t_high

        return best_t_low, best_t_high, best_cost

    def predict_triage(
        self,
        fraud_prob: float,
        transaction_id: int = 0
    ) -> ConformalPredictionSet:
        """
        Sinh tập dự báo Conformal và đưa ra quyết định phân loại rủi ro (3-Way Triage).
        """
        if self.artifacts is None:
            raise ValueError("Engine chua duoc hieu chuan. Vui long chay calibrate() truoc.")

        q_hat_0 = self.artifacts.q_hat_0
        q_hat_1 = self.artifacts.q_hat_1
        t_low = self.artifacts.optimal_cost_thresholds["t_approve"]
        t_high = self.artifacts.optimal_cost_thresholds["t_block"]

        # Tập nhãn Conformal
        labels = set()
        # Giả thuyết 0 (Hợp lệ): s = fraud_prob <= q_hat_0
        if fraud_prob <= q_hat_0:
            labels.add(0)
        # Giả thuyết 1 (Gian lận): s = 1 - fraud_prob <= q_hat_1
        if (1.0 - fraud_prob) <= q_hat_1:
            labels.add(1)

        # Tính p-values
        p_val_legit = max(0.0, 1.0 - fraud_prob / (q_hat_0 + 1e-7))
        p_val_fraud = max(0.0, 1.0 - (1.0 - fraud_prob) / (q_hat_1 + 1e-7))

        # Quyết định Triage kết hợp Conformal Set và Cost-Optimal Thresholds
        if fraud_prob < t_low:
            decision = TriageDecision.APPROVE
        elif fraud_prob >= t_high:
            decision = TriageDecision.BLOCK
        else:
            decision = TriageDecision.STEP_UP_2FA

        return ConformalPredictionSet(
            transaction_id=transaction_id,
            labels=labels,
            p_value_legit=float(p_val_legit),
            p_value_fraud=float(p_val_fraud),
            decision=decision,
            fraud_probability=float(fraud_prob)
        )

    def evaluate_test_set(
        self,
        model: lgb.Booster,
        test_df: pl.DataFrame,
        feature_cols: List[str]
    ) -> Dict[str, Any]:
        """
        Đánh giá thực nghiệm toàn diện trên tập kiểm thử ngoài thời gian (OOT Test Set):
        - Đo lường độ bao phủ thực nghiệm (Empirical Coverage) cho từng lớp
        - Tỷ lệ duyệt tự động (Auto-Approval Rate)
        - Tỷ lệ chuyển sang 2FA (Step-up Rate)
        - Tỷ lệ chặn gian lận (Block Rate)
        - Tổng thiệt hại tài chính theo ma trận chi phí
        """
        if self.artifacts is None:
            raise ValueError("Engine chua duoc hieu chuan.")

        cols_to_select = list(dict.fromkeys(feature_cols + ["TransactionID", "isFraud", "TransactionAmt"]))
        test_pdf = test_df.select(cols_to_select).to_pandas()

        for col in feature_cols:
            if test_pdf[col].dtype == "object":
                test_pdf[col] = test_pdf[col].astype("category")

        X_test = test_pdf[feature_cols]
        y_test = test_pdf["isFraud"].values
        amts_test = test_pdf["TransactionAmt"].values
        tx_ids = test_pdf["TransactionID"].values

        p_test = model.predict(X_test)

        n_total = len(y_test)
        n_fraud = int(np.sum(y_test == 1))
        n_legit = int(np.sum(y_test == 0))

        t_low = self.artifacts.optimal_cost_thresholds["t_approve"]
        t_high = self.artifacts.optimal_cost_thresholds["t_block"]
        q_hat_0 = self.artifacts.q_hat_0
        q_hat_1 = self.artifacts.q_hat_1

        # Đánh giá coverage
        # Lớp 0 có nằm trong C(x)? p <= q_hat_0
        covered_0 = (p_test[y_test == 0] <= q_hat_0)
        empirical_cov_0 = float(np.mean(covered_0))

        # Lớp 1 có nằm trong C(x)? 1 - p <= q_hat_1
        covered_1 = ((1.0 - p_test[y_test == 1]) <= q_hat_1)
        empirical_cov_1 = float(np.mean(covered_1))

        # Phân loại quyết định
        decisions = []
        total_cost = 0.0
        n_approve = 0
        n_step_up = 0
        n_block = 0

        # Thống kê chi tiết
        legit_approved = 0
        legit_stepped = 0
        legit_blocked = 0

        fraud_approved = 0  # FN (Bỏ lọt)
        fraud_stepped = 0   # Bắt qua 2FA
        fraud_blocked = 0   # Chặn trực tiếp (TP)

        for prob, true_y, amt in zip(p_test, y_test, amts_test):
            if prob < t_low:
                dec = TriageDecision.APPROVE
                n_approve += 1
                if true_y == 0:
                    legit_approved += 1
                else:
                    fraud_approved += 1
            elif prob >= t_high:
                dec = TriageDecision.BLOCK
                n_block += 1
                if true_y == 0:
                    legit_blocked += 1
                else:
                    fraud_blocked += 1
            else:
                dec = TriageDecision.STEP_UP_2FA
                n_step_up += 1
                if true_y == 0:
                    legit_stepped += 1
                else:
                    fraud_stepped += 1

            cost = self.cost_matrix.calculate_cost(dec, true_y, amt)
            total_cost += cost

        return {
            "calibration": {
                "q_hat_legit": round(q_hat_0, 4),
                "q_hat_fraud": round(q_hat_1, 4),
                "threshold_approve": round(t_low, 4),
                "threshold_block": round(t_high, 4),
                "nominal_coverage_legit": round(1.0 - self.config.alpha_legit, 4),
                "nominal_coverage_fraud": round(1.0 - self.config.alpha_fraud, 4),
                "empirical_coverage_legit": round(empirical_cov_0, 4),
                "empirical_coverage_fraud": round(empirical_cov_1, 4),
            },
            "triage_summary": {
                "total_transactions": n_total,
                "auto_approved": n_approve,
                "auto_approved_pct": round(n_approve / n_total * 100, 2),
                "step_up_2fa": n_step_up,
                "step_up_2fa_pct": round(n_step_up / n_total * 100, 2),
                "blocked": n_block,
                "blocked_pct": round(n_block / n_total * 100, 2),
            },
            "fraud_breakdown": {
                "total_fraud": n_fraud,
                "fraud_blocked_direct": fraud_blocked,
                "fraud_intercepted_2fa": fraud_stepped,
                "fraud_missed_escaped": fraud_approved,
                "fraud_detection_rate_pct": round((fraud_blocked + fraud_stepped) / n_fraud * 100, 2),
                "fraud_escaped_rate_pct": round(fraud_approved / n_fraud * 100, 2),
            },
            "legit_breakdown": {
                "total_legit": n_legit,
                "legit_frictionless_approved": legit_approved,
                "legit_frictionless_pct": round(legit_approved / n_legit * 100, 2),
                "legit_stepped_2fa": legit_stepped,
                "legit_stepped_pct": round(legit_stepped / n_legit * 100, 2),
                "legit_false_blocked": legit_blocked,
                "legit_false_blocked_pct": round(legit_blocked / n_legit * 100, 2),
            },
            "financial_impact": {
                "total_financial_loss_usd": round(total_cost, 2),
            }
        }
