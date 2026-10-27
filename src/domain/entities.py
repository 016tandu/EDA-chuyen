from dataclasses import dataclass
from typing import Optional, Dict, Any
from .cost_matrix import TriageDecision


@dataclass
class TransactionRecord:
    """Đại diện cho 1 giao dịch thanh toán trong hệ thống."""
    transaction_id: int
    transaction_dt: int
    transaction_amt: float
    product_cd: str
    card1: int
    card2: Optional[float] = None
    card3: Optional[float] = None
    card4: Optional[str] = None
    card5: Optional[float] = None
    card6: Optional[str] = None
    addr1: Optional[float] = None
    addr2: Optional[float] = None
    p_emaildomain: Optional[str] = None
    r_emaildomain: Optional[str] = None
    is_fraud: Optional[int] = None
    extra_features: Optional[Dict[str, Any]] = None


@dataclass
class TriageResult:
    """Kết quả phân loại và giải trình rủi ro của giao dịch."""
    transaction_id: int
    decision: TriageDecision
    fraud_probability: float
    conformal_set: list[str]
    estimated_cost: float
    latency_ms: float
    explanation: Optional[Dict[str, float]] = None
