"""
Entrypoint: FastAPI Application (Clean Architecture Entrypoint)
Cung cấp REST API cho cổng thanh toán với kiến trúc phòng thủ 4 tầng:
- POST /api/v1/checkout/triage
- GET /api/v1/health
"""

import os
import sys
import time
import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
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
)

# Biến toàn cục giữ service
triage_service: Optional[PaymentTriageService] = None
start_time: float = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo mô hình và động cơ Conformal khi khởi động API."""
    global triage_service
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

    triage_service = PaymentTriageService(
        model=model,
        conformal_engine=conformal_engine,
        feature_cols=meta["features"],
        categorical_features=meta.get("metadata", {}).get("categorical_features", []),
        cost_matrix=CostMatrix()
    )
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
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = f"Lỗi cú pháp tại [{'.'.join(str(loc) for loc in first_error.get('loc', []))}]: {first_error.get('msg', 'Không hợp lệ')}"

    response_body = FastFailErrorResponse(
        error_code="SCHEMA_VALIDATION_ERROR",
        message=msg,
        layer="LAYER_1_SCHEMA",
        latency_ms=1.5  # Phản hồi tức thì ở tầng schema
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
# ENDPOINTS
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
        # Khởi tạo dự phòng nếu chạy test độc lập ngoài lifespan
        models_dir = os.path.join(PROJECT_ROOT, "models")
        repo = ModelRepository(base_dir=models_dir)
        model, meta = repo.load_model("baseline_lightgbm")
        with open(os.path.join(models_dir, "conformal_artifacts.json"), "r", encoding="utf-8") as f:
            art_data = json.load(f)
        config = ConformalCalibrationConfig(**art_data["config"])
        conformal_engine = ConformalEngine(config=config)
        conformal_engine.artifacts = CalibrationArtifacts(
            q_hat_0=art_data["q_hat_0"],
            q_hat_1=art_data["q_hat_1"],
            config=config,
            optimal_cost_thresholds=art_data["optimal_cost_thresholds"]
        )
        triage_service = PaymentTriageService(
            model=model,
            conformal_engine=conformal_engine,
            feature_cols=meta["features"],
            categorical_features=meta.get("metadata", {}).get("categorical_features", [])
        )

    return triage_service.process_transaction(request)


@app.post("/api/v1/cache/clear")
def clear_cache():
    global triage_service
    if triage_service:
        triage_service.cache.clear()
        triage_service.rule_engine.reset()
    return {"message": "Cache and rule engine history cleared successfully."}
