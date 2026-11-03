"""
Entrypoint Schemas: Pydantic Data Models (Layer 1 Schema Validation)
Kiểm tra chặt chẽ định dạng, kiểu dữ liệu, ràng buộc biên trước khi vào các tầng bên dưới.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class CheckoutRequest(BaseModel):
    transaction_id: int = Field(..., description="Mã định danh giao dịch duy nhất")
    transaction_amt: float = Field(..., gt=0.0, le=1_000_000.0, description="Số tiền thanh toán phải lớn hơn 0 và không quá $1,000,000")
    product_cd: str = Field(..., min_length=1, max_length=5, description="Mã nhóm sản phẩm (W, C, R, H, S)")
    card1: int = Field(..., gt=0, le=999999, description="Mã dải thẻ / Ngân hàng phát hành (BIN)")
    card2: Optional[float] = Field(None, ge=0.0, le=999.0)
    card3: Optional[float] = Field(None, ge=0.0, le=999.0)
    card4: Optional[str] = Field(None, max_length=20)
    card6: Optional[str] = Field(None, max_length=20)
    addr1: Optional[float] = Field(None, ge=0.0, le=9999.0)
    addr2: Optional[float] = Field(None, ge=0.0, le=999.0)
    client_ip: Optional[str] = Field(None, max_length=45)
    device_info: Optional[str] = Field(None, max_length=100)
    p_emaildomain: Optional[str] = Field(None, max_length=50)
    c1: Optional[float] = Field(None, ge=0.0)
    c2: Optional[float] = Field(None, ge=0.0)
    d1: Optional[float] = Field(None, ge=0.0)
    extra_features: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("product_cd")
    @classmethod
    def validate_product_code(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in {"W", "C", "R", "H", "S"}:
            raise ValueError(f"Mã sản phẩm [{v}] không hợp lệ. Phải thuộc một trong các mã: W, C, R, H, S.")
        return clean


class TriageResponse(BaseModel):
    transaction_id: int
    decision: str  # "APPROVE", "STEP_UP_2FA", "BLOCK"
    fraud_probability: float
    conformal_set: List[str]
    estimated_cost_usd: float
    layer_reached: str
    cache_hit: bool
    latency_ms: float
    message: str
    reason_codes: List[str] = Field(default_factory=list)


class FastFailErrorResponse(BaseModel):
    error_code: str
    message: str
    layer: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    conformal_calibrated: bool
    cache_entries: int
    uptime_seconds: float


class Verify2FARequest(BaseModel):
    transaction_id: int = Field(..., description="Mã giao dịch cần xác thực OTP")
    otp_code: str = Field(..., min_length=4, max_length=10, description="Mã OTP do người dùng nhập")


class Verify2FAResponse(BaseModel):
    transaction_id: int
    verified: bool
    final_status: str  # "AUTHORIZED", "REJECTED"
    message: str
    latency_ms: float


class TelemetryStatsResponse(BaseModel):
    uptime_seconds: float
    total_transactions: int
    total_amount_usd: float
    fraud_loss_prevented_usd: float
    early_exit_count: int
    early_exit_rate_pct: float
    layer_counts: Dict[str, int]
    decision_counts: Dict[str, int]
    latency_benchmarks: Dict[str, float]
    recent_audit_stream: List[Dict[str, Any]]

