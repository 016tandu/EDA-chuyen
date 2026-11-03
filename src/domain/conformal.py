"""
Domain Entity: Conformal Prediction & Calibration Structures
Định nghĩa các cấu trúc dữ liệu và hợp đồng cho cơ chế Conformal Prediction và Hiệu chuẩn chi phí.
"""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict, Any
from .cost_matrix import TriageDecision


@dataclass
class ConformalPredictionSet:
    """Đại diện cho tập dự báo Conformal C(x) kèm mức độ bao phủ danh định."""
    transaction_id: int
    labels: Set[int]  # ví dụ: {0}, {1}, hoặc {0, 1}
    p_value_legit: float
    p_value_fraud: float
    decision: TriageDecision
    fraud_probability: float

    @property
    def is_uncertain(self) -> bool:
        """Kiểm tra xem giao dịch có rơi vào vùng bất định hay không."""
        return len(self.labels) > 1 or len(self.labels) == 0

    @property
    def formatted_labels(self) -> List[str]:
        mapping = {0: "Legit", 1: "Fraud"}
        return [mapping[l] for l in sorted(self.labels)]


@dataclass
class ConformalCalibrationConfig:
    """Cấu hình tham số hiệu chuẩn Conformal."""
    alpha_legit: float = 0.05   # Mức ý nghĩa cho lớp 0 (khách thật): đảm bảo bao phủ 95% khách thật
    alpha_fraud: float = 0.05   # Mức ý nghĩa cho lớp 1 (kẻ gian): đảm bảo bao phủ 95% kẻ gian
    method: str = "mondrian"    # "standard" hoặc "mondrian" (hiệu chuẩn theo lớp)


@dataclass
class CalibrationArtifacts:
    """Lưu trữ các ngưỡng và phân vị đã hiệu chuẩn trên tập Calib Set."""
    q_hat_0: float  # Ngưỡng phân vị non-conformity cho lớp 0
    q_hat_1: float  # Ngưỡng phân vị non-conformity cho lớp 1
    config: ConformalCalibrationConfig
    optimal_cost_thresholds: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
