"""
Entrypoint: FastAPI Application (Clean Architecture Entrypoint)
Cung cấp REST API cho cổng thanh toán với kiến trúc phòng thủ 4 tầng và Web Dashboard:
- GET  / hoặc /dashboard (Dual-View Risk Control Dashboard)
- POST /api/v1/checkout/triage
- POST /api/v1/checkout/verify-2fa
- GET  /api/v1/telemetry/stats
- POST /api/v1/telemetry/reset
- GET  /api/v1/health
"""

import os
import sys
import time
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.adapter.model_repository import ModelRepository
from src.usecase.conformal_engine import ConformalEngine
from src.domain.conformal import ConformalCalibrationConfig, CalibrationArtifacts
from src.domain.cost_matrix import CostMatrix
from src.usecase.triage_service import PaymentTriageService, BlockingRuleError
from src.entrypoint.api.schemas import (
    CheckoutRequest,
    TriageResponse,
    FastFailErrorResponse,
    HealthResponse,
    TelemetryStatsResponse,
    Verify2FARequest,
    Verify2FAResponse,
)

# Biến toàn cục giữ service
triage_service: Optional[PaymentTriageService] = None
start_time: float = time.time()
dashboard_html_content: str = ""


def _load_dashboard_html() -> str:
    template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "dashboard.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Payment Shield Dashboard (Template missing)</h1>"


def _init_triage_service() -> PaymentTriageService:
    models_dir = os.path.join(PROJECT_ROOT, "models")
    repo = ModelRepository(base_dir=models_dir)
    model, meta = repo.load_model("baseline_lightgbm")

    conformal_art_path = os.path.join(models_dir, "conformal_artifacts.json")
    with open(conformal_art_path, "r", encoding="utf-8") as f:
        art_data = json.load(f)

    config = ConformalCalibrationConfig(**art_data["config"])
    conformal_engine = ConformalEngine(config=config)
    conformal_engine.artifacts = CalibrationArtifacts(
        q_hat_0=art_data["q_hat_0"],
        q_hat_1=art_data["q_hat_1"],
        config=config,
        optimal_cost_thresholds=art_data["optimal_cost_thresholds"],
        metadata=art_data.get("metadata", {})
    )

    return PaymentTriageService(
        model=model,
        conformal_engine=conformal_engine,
        feature_cols=meta["features"],
        categorical_features=meta.get("metadata", {}).get("categorical_features", []),
        cost_matrix=CostMatrix()
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo mô hình, động cơ Conformal và tài nguyên Web UI khi khởi động API."""
    global triage_service, dashboard_html_content
    dashboard_html_content = _load_dashboard_html()
    triage_service = _init_triage_service()
    yield


app = FastAPI(
    title="Payment Fraud Triage Engine API",
    description="Cổng API phân loại rủi ro gian lận thời gian thực với kiến trúc phòng thủ 4 tầng và Conformal Prediction",
    version="1.0.0",
    lifespan=lifespan
)


# --------------------------------------------------------------------------
# LAYER 1: SCHEMA VALIDATION ERROR HANDLER (Fast-Fail < 5ms)
# --------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    global triage_service
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = f"Lỗi cú pháp tại [{'.'.join(str(loc) for loc in first_error.get('loc', []))}]: {first_error.get('msg', 'Không hợp lệ')}"

    # Ghi nhận sự kiện vào Telemetry
    if triage_service and triage_service.telemetry:
        triage_service.telemetry.record_transaction(
            transaction_id="SYNTAX_ERR",
            amount=100.0,
            layer="LAYER_1_SCHEMA",
            decision="FAST_FAIL_ERROR",
            latency_ms=1.5,
            reason=msg
        )

    response_body = FastFailErrorResponse(
        error_code="SCHEMA_VALIDATION_ERROR",
        message=msg,
        layer="LAYER_1_SCHEMA",
        latency_ms=1.5
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_body.model_dump()
    )


# --------------------------------------------------------------------------
# LAYER 2: BLOCKING RULE ERROR HANDLER (Fast-Fail < 5ms)
# --------------------------------------------------------------------------
@app.exception_handler(BlockingRuleError)
async def blocking_rule_exception_handler(request: Request, exc: BlockingRuleError):
    global triage_service
    # Ghi nhận sự kiện vào Telemetry
    if triage_service and triage_service.telemetry:
        triage_service.telemetry.record_transaction(
            transaction_id="RULE_BLOCK",
            amount=500.0,
            layer="LAYER_2_RULE",
            decision="BLOCK",
            latency_ms=exc.latency_ms,
            reason=exc.message
        )

    response_body = FastFailErrorResponse(
        error_code=exc.error_code,
        message=exc.message,
        layer="LAYER_2_RULE",
        latency_ms=round(exc.latency_ms, 2)
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=response_body.model_dump()
    )


# --------------------------------------------------------------------------
# WEB DASHBOARD ENDPOINTS
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    """Phục vụ giao diện điều khiển Dual-View Dashboard hoàn chỉnh."""
    global dashboard_html_content
    if not dashboard_html_content:
        dashboard_html_content = _load_dashboard_html()
    return HTMLResponse(content=dashboard_html_content, status_code=200)


# --------------------------------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------------------------------
@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    global triage_service, start_time
    return HealthResponse(
        status="HEALTHY",
        model_loaded=(triage_service is not None),
        conformal_calibrated=(triage_service is not None and triage_service.conformal_engine.artifacts is not None),
        cache_entries=len(triage_service.cache._cache) if triage_service else 0,
        uptime_seconds=round(time.time() - start_time, 2)
    )


@app.post("/api/v1/checkout/triage", response_model=TriageResponse)
def triage_transaction(request: CheckoutRequest):
    global triage_service
    if not triage_service:
        triage_service = _init_triage_service()

    return triage_service.process_transaction(request)


@app.post("/api/v1/checkout/verify-2fa", response_model=Verify2FAResponse)
def verify_2fa(request: Verify2FARequest):
    """Xác thực mã OTP 2FA cho giao dịch nghi vấn."""
    t_start = time.perf_counter()
    # Mã OTP hợp lệ giả lập: "123456"
    is_valid = (request.otp_code.strip() == "123456")
    elapsed_ms = (time.perf_counter() - t_start) * 1000.0


    if is_valid:
        return Verify2FAResponse(
            transaction_id=request.transaction_id,
            verified=True,
            final_status="AUTHORIZED",
            message=f"Xác thực OTP thành công cho giao dịch #{request.transaction_id}. Thanh toán đã được phê duyệt an toàn.",
            latency_ms=round(elapsed_ms, 2)
        )
    else:
        return Verify2FAResponse(
            transaction_id=request.transaction_id,
            verified=False,
            final_status="REJECTED",
            message=f"Mã OTP không chính xác. Giao dịch #{request.transaction_id} tiếp tục bị khóa bảo vệ.",
            latency_ms=round(elapsed_ms, 2)
        )


@app.get("/api/v1/telemetry/stats", response_model=TelemetryStatsResponse)
def get_telemetry_stats():
    """Lấy dữ liệu telemetry thống kê thời gian thực phục vụ Dashboard."""
    global triage_service
    if not triage_service:
        triage_service = _init_triage_service()
    return triage_service.telemetry.get_summary_stats()


@app.post("/api/v1/telemetry/reset")
def reset_telemetry():
    """Đặt lại dữ liệu telemetry."""
    global triage_service
    if triage_service and triage_service.telemetry:
        triage_service.telemetry.reset()
    return {"message": "Telemetry stats reset successfully."}


@app.post("/api/v1/cache/clear")
def clear_cache():
    global triage_service
    if triage_service:
        triage_service.cache.clear()
        triage_service.rule_engine.reset()
    return {"message": "Cache and rule engine history cleared successfully."}
