"""
Adapter: Telemetry Service
Thu thập và quản lý số liệu đo đạc thời gian thực (Real-time Telemetry):
- Phân bổ tầng xử lý (Layer 1, Layer 2, Layer 3, Layer 4)
- Tỷ lệ ngắt sớm (Early Fast-Fail Rate)
- Phân bổ quyết định (Approve, Step-Up 2FA, Block)
- Ước tính tổn thất gian lận đã ngăn chặn ($ USD)
- Lịch sử giao dịch trực tiếp (Live Audit Stream)
"""

import time
from typing import Dict, Any, List, Optional
import numpy as np


class TelemetryCollector:
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.start_time = time.time()
        self.total_transactions: int = 0
        self.layer_counts: Dict[str, int] = {
            "LAYER_1_SCHEMA": 0,
            "LAYER_2_RULE": 0,
            "LAYER_3_CACHE": 0,
            "LAYER_4_CONFORMAL_ML": 0,
        }
        self.decision_counts: Dict[str, int] = {
            "APPROVE": 0,
            "STEP_UP_2FA": 0,
            "BLOCK": 0,
            "FAST_FAIL_ERROR": 0,
        }
        self.latencies_ms: List[float] = []
        self.total_amount_usd: float = 0.0
        self.fraud_loss_prevented_usd: float = 0.0
        self.audit_stream: List[Dict[str, Any]] = []

    def record_transaction(
        self,
        transaction_id: str,
        amount: float,
        layer: str,
        decision: str,
        latency_ms: float,
        fraud_prob: Optional[float] = None,
        conformal_set: Optional[List[str]] = None,
        reason: Optional[str] = None
    ) -> None:
        """Ghi nhận một sự kiện giao dịch vào hệ thống telemetry."""
        self.total_transactions += 1
        self.total_amount_usd += amount
        self.latencies_ms.append(latency_ms)

        # Cập nhật số đếm tầng
        if layer in self.layer_counts:
            self.layer_counts[layer] += 1
        else:
            self.layer_counts[layer] = 1

        # Cập nhật số đếm quyết định
        if decision in self.decision_counts:
            self.decision_counts[decision] += 1
        else:
            self.decision_counts[decision] = 1

        # Ước tính tiền tổn thất ngăn chặn
        # Nếu bị Block ở Layer 2 hoặc Layer 4, hoặc bị chặn cú pháp ở Layer 1
        if decision in ["BLOCK", "FAST_FAIL_ERROR"] or (fraud_prob and fraud_prob >= 0.5):
            self.fraud_loss_prevented_usd += amount

        # Thêm vào live stream
        entry = {
            "id": transaction_id,
            "timestamp": time.strftime("%H:%M:%S", time.localtime()),
            "amount": round(amount, 2),
            "layer": layer,
            "decision": decision,
            "fraud_probability": round(fraud_prob, 4) if fraud_prob is not None else None,
            "conformal_set": conformal_set or [],
            "latency_ms": round(latency_ms, 2),
            "reason": reason or "Processed successfully"
        }
        self.audit_stream.insert(0, entry)
        if len(self.audit_stream) > self.max_history:
            self.audit_stream.pop()

    def get_summary_stats(self) -> Dict[str, Any]:
        """Tổng hợp chỉ số KPI phục vụ Risk Control Tower Dashboard."""
        early_fast_fail_count = (
            self.layer_counts["LAYER_1_SCHEMA"]
            + self.layer_counts["LAYER_2_RULE"]
            + self.layer_counts["LAYER_3_CACHE"]
        )
        early_exit_rate = (
            (early_fast_fail_count / self.total_transactions * 100.0)
            if self.total_transactions > 0
            else 0.0
        )

        p50 = float(np.percentile(self.latencies_ms, 50)) if self.latencies_ms else 0.0
        p90 = float(np.percentile(self.latencies_ms, 90)) if self.latencies_ms else 0.0
        p99 = float(np.percentile(self.latencies_ms, 99)) if self.latencies_ms else 0.0
        mean_latency = float(np.mean(self.latencies_ms)) if self.latencies_ms else 0.0

        return {
            "uptime_seconds": round(time.time() - self.start_time, 1),
            "total_transactions": self.total_transactions,
            "total_amount_usd": round(self.total_amount_usd, 2),
            "fraud_loss_prevented_usd": round(self.fraud_loss_prevented_usd, 2),
            "early_exit_count": early_fast_fail_count,
            "early_exit_rate_pct": round(early_exit_rate, 2),
            "layer_counts": dict(self.layer_counts),
            "decision_counts": dict(self.decision_counts),
            "latency_benchmarks": {
                "mean_ms": round(mean_latency, 2),
                "p50_ms": round(p50, 2),
                "p90_ms": round(p90, 2),
                "p99_ms": round(p99, 2),
            },
            "recent_audit_stream": self.audit_stream[:15]
        }

    def reset(self) -> None:
        """Đặt lại dữ liệu đo đạc."""
        self.__init__(max_history=self.max_history)
