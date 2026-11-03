"""
Unit & Integration Tests for Stage 3 (FastAPI 4-Layer Architecture)
Kiểm thử tự động theo chuẩn pytest:
- test_health_check (AC-1)
- test_layer1_schema_validation_fast_fail (AC-2)
- test_layer2_blocking_rule_blacklist_and_velocity (AC-3)
- test_layer3_idempotency_cache_replay (AC-4)
- test_layer4_conformal_inference_triage (AC-5)
- test_performance_sla_p99 (AC-6)
"""

import time
import pytest
import numpy as np
from fastapi.testclient import TestClient
from src.entrypoint.api.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert data["model_loaded"] is True
    assert data["conformal_calibrated"] is True


def test_layer1_schema_validation_fast_fail(client):
    # Payload sai: số tiền âm
    resp = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 1001,
        "transaction_amt": -10.0,
        "product_cd": "W",
        "card1": 13926
    })
    assert resp.status_code == 422
    assert resp.json()["layer"] == "LAYER_1_SCHEMA"

    # Payload sai: mã sản phẩm không hợp lệ
    resp2 = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 1002,
        "transaction_amt": 50.0,
        "product_cd": "XYZ",
        "card1": 13926
    })
    assert resp2.status_code == 422
    assert resp2.json()["layer"] == "LAYER_1_SCHEMA"


def test_layer2_blocking_rule_blacklist_and_velocity(client):
    # Test Blacklisted Card
    resp_card = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 2001,
        "transaction_amt": 100.0,
        "product_cd": "W",
        "card1": 9999,
        "card2": 999.0,
        "card3": 150.0,
        "card4": "visa",
        "card6": "credit",
        "addr1": 999.0
    })
    assert resp_card.status_code == 403
    assert resp_card.json()["layer"] == "LAYER_2_RULE"
    assert resp_card.json()["error_code"] == "RULE_CARD_BLACKLISTED"

    # Test Blacklisted IP
    resp_ip = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 2002,
        "transaction_amt": 100.0,
        "product_cd": "W",
        "card1": 13926,
        "client_ip": "185.220.101.5"
    })
    assert resp_ip.status_code == 403
    assert resp_ip.json()["layer"] == "LAYER_2_RULE"
    assert resp_ip.json()["error_code"] == "RULE_IP_BLACKLISTED"


def test_layer3_idempotency_cache_replay(client):
    client.post("/api/v1/cache/clear")
    payload = {
        "transaction_id": 3001,
        "transaction_amt": 55.0,
        "product_cd": "W",
        "card1": 8888,
        "card2": 150.0,
        "card3": 150.0,
        "card4": "visa",
        "card6": "debit"
    }

    # Lần 1: Chưa có trong cache
    resp1 = client.post("/api/v1/checkout/triage", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["cache_hit"] is False

    # Lần 2: Phải lấy từ Layer 3 Cache
    t0 = time.perf_counter()
    resp2 = client.post("/api/v1/checkout/triage", json=payload)
    elapsed = (time.perf_counter() - t0) * 1000.0

    assert resp2.status_code == 200
    assert resp2.json()["cache_hit"] is True
    assert resp2.json()["layer_reached"] == "LAYER_3_CACHE"
    assert elapsed < 10.0


def test_layer4_conformal_inference_triage(client):
    client.post("/api/v1/cache/clear")
    payload = {
        "transaction_id": 4001,
        "transaction_amt": 25.0,
        "product_cd": "W",
        "card1": 13926,
        "c1": 1.0,
        "d1": 10.0
    }
    resp = client.post("/api/v1/checkout/triage", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["decision"] in ["APPROVE", "STEP_UP_2FA", "BLOCK"]
    assert "conformal_set" in data
    assert 0.0 <= data["fraud_probability"] <= 1.0
    assert data["layer_reached"] == "LAYER_4_CONFORMAL_ML"
