"""
Usecase: Payment Triage Service (4-Layer Fast-Fail Orchestrator)
Hiện thực hóa kiến trúc phòng thủ 4 tầng:
- Layer 1: Pydantic Schema Validation (bảo vệ ở cấp Entrypoint Router)
- Layer 2: Blocking Rule Engine (Blacklist, Velocity check) -> Ngắt lỗi trong < 5ms
- Layer 3: Idempotency SHA-256 Cache -> Trả kết quả cũ tức thì trong < 3ms
- Layer 4: Conformal ML Inference -> Phân loại 3 ngã rẽ với độ trễ đuôi p99 < 30ms
"""

import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
import lightgbm as lgb

from src.domain.cost_matrix import CostMatrix, TriageDecision
from src.domain.conformal import ConformalPredictionSet
from src.usecase.conformal_engine import ConformalEngine
from src.adapter.cache.idempotency_cache import IdempotencyCache
from src.adapter.rules.rule_engine import RuleEngine
from src.entrypoint.api.schemas import CheckoutRequest, TriageResponse


class BlockingRuleError(Exception):
    """Lỗi ngắt sớm tại Layer 2 (Rule Engine)."""
    def __init__(self, error_code: str, message: str, latency_ms: float):
        self.error_code = error_code
        self.message = message
        self.latency_ms = latency_ms
        super().__init__(message)


class PaymentTriageService:
    def __init__(
        self,
        model: lgb.Booster,
        conformal_engine: ConformalEngine,
        feature_cols: List[str],
        categorical_features: Optional[List[str]] = None,
        rule_engine: Optional[RuleEngine] = None,
        cache: Optional[IdempotencyCache] = None,
        cost_matrix: Optional[CostMatrix] = None
    ):
        self.model = model
        self.conformal_engine = conformal_engine
        self.feature_cols = feature_cols
        self.categorical_features = set(categorical_features or [])
        self.rule_engine = rule_engine or RuleEngine()
        self.cache = cache or IdempotencyCache(ttl_seconds=300)
        self.cost_matrix = cost_matrix or CostMatrix()

        # Tạo sẵn template dữ liệu chuẩn để tối ưu hóa tốc độ tạo row (< 2ms)
        self._template: Dict[str, Any] = {}
        for col in self.feature_cols:
            if col in self.categorical_features:
                self._template[col] = pd.Categorical([None])
            else:
                self._template[col] = np.array([np.nan], dtype=np.float32)

    def _build_card_id(self, req: CheckoutRequest) -> str:
        return f"{req.card1}_{req.card2 or 0.0}_{req.card3 or 0.0}_{req.card4 or 'na'}_{req.card6 or 'na'}_{req.addr1 or 0.0}"

    def _prepare_feature_row(self, req: CheckoutRequest, card_id: str) -> pd.DataFrame:
        """Tạo hàng dữ liệu 1-row với đầy đủ 440 đặc trưng siêu tốc (< 2ms)."""
        data_dict = dict(self._template)

        # 1. Các trường số
        data_dict["TransactionAmt"] = np.array([req.transaction_amt], dtype=np.float32)
        data_dict["log_TransactionAmt"] = np.array([np.log1p(req.transaction_amt)], dtype=np.float32)
        data_dict["amt_to_mean_card1"] = np.array([req.transaction_amt / 135.0], dtype=np.float32)
        data_dict["amt_to_std_card1"] = np.array([(req.transaction_amt - 135.0) / 230.0], dtype=np.float32)
        data_dict["card1"] = np.array([req.card1], dtype=np.float32)
        data_dict["card2"] = np.array([req.card2 if req.card2 is not None else np.nan], dtype=np.float32)
        data_dict["card3"] = np.array([req.card3 if req.card3 is not None else np.nan], dtype=np.float32)
        data_dict["addr1"] = np.array([req.addr1 if req.addr1 is not None else np.nan], dtype=np.float32)
        data_dict["addr2"] = np.array([req.addr2 if req.addr2 is not None else np.nan], dtype=np.float32)
        data_dict["C1"] = np.array([req.c1 if req.c1 is not None else 1.0], dtype=np.float32)
        data_dict["C2"] = np.array([req.c2 if req.c2 is not None else 1.0], dtype=np.float32)
        data_dict["D1"] = np.array([req.d1 if req.d1 is not None else 0.0], dtype=np.float32)
        data_dict["card_freq"] = np.array([1.0], dtype=np.float32)
        data_dict["client_freq"] = np.array([1.0], dtype=np.float32)
        data_dict["hour_of_day"] = np.array([12.0], dtype=np.float32)
        data_dict["day_of_week"] = np.array([3.0], dtype=np.float32)

        # 2. Các trường danh mục (Categorical)
        data_dict["ProductCD"] = pd.Categorical([req.product_cd])
        if req.card4:
            data_dict["card4"] = pd.Categorical([req.card4])
        if req.card6:
            data_dict["card6"] = pd.Categorical([req.card6])
        if req.p_emaildomain:
            data_dict["P_emaildomain"] = pd.Categorical([req.p_emaildomain])

        # 3. Gộp các đặc trưng bổ sung (nếu có)
        if req.extra_features:
            for k, v in req.extra_features.items():
                if k in data_dict:
                    if k in self.categorical_features:
                        data_dict[k] = pd.Categorical([v])
                    else:
                        data_dict[k] = np.array([v], dtype=np.float32)

        return pd.DataFrame(data_dict)

    def process_transaction(self, req: CheckoutRequest) -> TriageResponse:
        t_start = time.perf_counter()
        card_id = self._build_card_id(req)

        # -------------------------------------------------------------
        # LAYER 2: BLOCKING RULE ENGINE (Fast-Fail trong < 3ms)
        # -------------------------------------------------------------
        passed, rule_code, err_msg = self.rule_engine.evaluate(card_id, req.client_ip)
        if not passed:
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            raise BlockingRuleError(
                error_code=rule_code or "RULE_VIOLATION",
                message=err_msg or "Giao dịch vi phạm quy tắc an ninh nghiêm trọng.",
                latency_ms=elapsed_ms
            )

        # -------------------------------------------------------------
        # LAYER 3: IDEMPOTENCY CACHE (SHA-256 Fast Replay trong < 2ms)
        # -------------------------------------------------------------
        hash_key = self.cache.compute_hash(req.model_dump(mode="json"))
        cached_res = self.cache.get(hash_key)
        if cached_res:
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return TriageResponse(
                transaction_id=req.transaction_id,
                decision=cached_res["decision"],
                fraud_probability=cached_res["fraud_probability"],
                conformal_set=cached_res["conformal_set"],
                estimated_cost_usd=cached_res["estimated_cost_usd"],
                layer_reached="LAYER_3_CACHE",
                cache_hit=True,
                latency_ms=round(elapsed_ms, 2),
                message="[IDEMPOTENCY] Kết quả giao dịch đã được xử lý trước đó, tái sử dụng tức thì.",
                reason_codes=["IDEMPOTENT_REPLAY_SUCCESS"]
            )

        # -------------------------------------------------------------
        # LAYER 4: CONFORMAL AI INFERENCE (Độ trễ p99 < 30ms)
        # -------------------------------------------------------------
        X_row = self._prepare_feature_row(req, card_id)
        fraud_prob = float(self.model.predict(X_row)[0])

        # Phân loại 3 ngã rẽ Conformal
        triage_set = self.conformal_engine.predict_triage(fraud_prob, transaction_id=req.transaction_id)
        decision_enum = triage_set.decision

        # Tính toán chi phí ước tính
        estimated_cost = self.cost_matrix.calculate_cost(
            decision=decision_enum,
            is_fraud=1 if fraud_prob >= 0.5 else 0,
            transaction_amt=req.transaction_amt
        )

        reasons = []
        if decision_enum == TriageDecision.APPROVE:
            msg = "Giao dịch an toàn, duyệt tự động không độ trễ."
            reasons.append("CONFORMAL_PROVABLY_SAFE")
        elif decision_enum == TriageDecision.STEP_UP_2FA:
            msg = "Giao dịch rơi vào vùng bất định Conformal, kích hoạt xác thực 2 bước (OTP/Sinh trắc học)."
            reasons.append("CONFORMAL_UNCERTAINTY_TRIAGE")
            reasons.append("STEP_UP_2FA_REQUIRED")
        else:
            msg = "Phát hiện nguy cơ gian lận cao rõ rệt, từ chối thanh toán tức thì."
            reasons.append("CONFORMAL_HIGH_CONFIDENCE_FRAUD")
            reasons.append("TRANSACTION_BLOCKED")

        elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        response_data = {
            "transaction_id": req.transaction_id,
            "decision": decision_enum.value,
            "fraud_probability": round(fraud_prob, 4),
            "conformal_set": triage_set.formatted_labels,
            "estimated_cost_usd": round(estimated_cost, 2),
            "layer_reached": "LAYER_4_CONFORMAL_ML",
            "cache_hit": False,
            "latency_ms": round(elapsed_ms, 2),
            "message": msg,
            "reason_codes": reasons
        }

        # Lưu đệm Layer 3 cho các yêu cầu lặp lại
        self.cache.set(hash_key, response_data)

        return TriageResponse(**response_data)
