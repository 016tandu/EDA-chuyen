"""
Test Suite: Stage 4 Web Dashboard & Telemetry Verification
Kiểm thử tự động các thành phần giao diện, telemetry stats và luồng 2FA verification.
"""

import pytest
from fastapi.testclient import TestClient
from src.entrypoint.api.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_dashboard_html_serving(client: TestClient):
    """AC-1 & AC-3: Kiểm tra giao diện HTML được phục vụ tại / và /dashboard."""
    for path in ["/", "/dashboard"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        html = res.text
        assert "Payment Shield Conformal Triage Engine" in html
        assert "CỔNG THANH TOÁN (CHECKOUT SIMULATOR)" in html
        assert "NHẬT KÝ KIỂM TOÁN GIAO DỊCH THỜI GIAN THỰC" in html
        assert "modal-2fa" in html
        assert "chart-triage" in html
        assert "chart-layers" in html


def test_verify_2fa_workflow(client: TestClient):
    """AC-4: Kiểm tra luồng xác thực OTP 2FA cho giao dịch nghi vấn."""
    # 1. Mã OTP hợp lệ
    res_valid = client.post("/api/v1/checkout/verify-2fa", json={
        "transaction_id": 999111,
        "otp_code": "123456"
    })
    assert res_valid.status_code == 200
    data_valid = res_valid.json()
    assert data_valid["verified"] is True
    assert data_valid["final_status"] == "AUTHORIZED"

    # 2. Mã OTP không hợp lệ
    res_invalid = client.post("/api/v1/checkout/verify-2fa", json={
        "transaction_id": 999111,
        "otp_code": "000"  # Ngắn hơn 4 ký tự -> Schema error hoặc 422
    })
    assert res_invalid.status_code == 422

    res_wrong = client.post("/api/v1/checkout/verify-2fa", json={
        "transaction_id": 999111,
        "otp_code": "99999"  # 5 ký tự hợp lệ về format nhưng không phải 6 số chuẩn
    })
    assert res_wrong.status_code == 200
    assert res_wrong.json()["verified"] is False
    assert res_wrong.json()["final_status"] == "REJECTED"


def test_telemetry_stats_and_accumulation(client: TestClient):
    """AC-2 & AC-5: Kiểm tra thu thập số liệu telemetry thời gian thực."""
    # Reset trước khi đo
    client.post("/api/v1/telemetry/reset")
    client.post("/api/v1/cache/clear")

    # 1. Gửi 1 giao dịch hợp lệ
    res1 = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 5001,
        "transaction_amt": 55.0,
        "product_cd": "W",
        "card1": 13926,
        "card4": "discover",
        "card6": "credit"
    })
    assert res1.status_code == 200

    # 2. Gửi 1 giao dịch vi phạm schema (Layer 1 Fast-Fail)
    res2 = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 5002,
        "transaction_amt": -10.0,  # Âm -> Fast-fail L1
        "product_cd": "W",
        "card1": 13926
    })
    assert res2.status_code == 422

    # 3. Gửi 1 giao dịch vi phạm thẻ blacklist (Layer 2 Fast-Fail)
    res3 = client.post("/api/v1/checkout/triage", json={
        "transaction_id": 5003,
        "transaction_amt": 800.0,
        "product_cd": "W",
        "card1": 9999,
        "card2": 999.0,
        "card3": 150.0,
        "card4": "visa",
        "card6": "credit",
        "addr1": 999.0
    })
    assert res3.status_code == 403

    # Kiểm tra telemetry
    stats_res = client.get("/api/v1/telemetry/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()

    assert stats["total_transactions"] >= 3
    assert stats["early_exit_count"] >= 2  # L1 + L2
    assert stats["early_exit_rate_pct"] > 0.0
    assert stats["layer_counts"]["LAYER_1_SCHEMA"] >= 1
    assert stats["layer_counts"]["LAYER_2_RULE"] >= 1
    assert len(stats["recent_audit_stream"]) >= 3
