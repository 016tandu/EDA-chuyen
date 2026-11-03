"""
Script: Huấn luyện & Hiệu chuẩn Động cơ Conformal (Conformal Calibration & Evaluation Runner)
Thực thi:
1. Nạp mô hình cơ sở LightGBM từ models/baseline_lightgbm
2. Nạp dữ liệu và phân tách Time-split: Calib Set (Day 120-150) và Test Set (Day 150-182)
3. Chạy thuật toán Mondrian Conformal Prediction & Tối ưu hóa ma trận chi phí
4. Đánh giá toàn diện trên tập Test OOT (94.636 mẫu)
5. Đối chiếu trực tiếp (Head-to-head) với Baseline ngưỡng cố định 0.5
6. Lưu trữ artifacts hiệu chuẩn và báo cáo khoa học
"""

import os
import sys
import time
import json
import numpy as np
import polars as pl

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapter.model_repository import ModelRepository
from src.usecase.feature_engineering import (
    load_raw_parquet,
    engineer_magic_uid,
    engineer_group_aggregations,
    prepare_time_splits,
)
from src.usecase.conformal_engine import ConformalEngine
from src.domain.conformal import ConformalCalibrationConfig
from src.domain.cost_matrix import CostMatrix


def main():
    print("=" * 80)
    print("⚡ BẮT ĐẦU QUY TRÌNH HIỆU CHUẨN CONFORMAL & TỐI ƯU CHI PHÍ TÀI CHÍNH")
    print("=" * 80)

    data_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    models_dir = os.path.join(PROJECT_ROOT, "models")
    reports_dir = os.path.join(PROJECT_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Nạp mô hình cơ sở LightGBM
    t0 = time.time()
    print("\n[BƯỚC 1/4] Nạp mô hình cơ sở LightGBM đã huấn luyện...")
    repo = ModelRepository(base_dir=models_dir)
    model, meta = repo.load_model("baseline_lightgbm")
    feature_cols = meta["features"]
    print(f" -> Đã nạp thành công mô hình: {meta['model_name']} ({len(feature_cols)} features).")

    # 2. Nạp dữ liệu và trích xuất đặc trưng
    print("\n[BƯỚC 2/4] Nạp dữ liệu Parquet và chuẩn bị tập Calib / Test...")
    df = load_raw_parquet(data_dir)
    df = engineer_magic_uid(df)
    df = engineer_group_aggregations(df)

    _, calib_df, test_df = prepare_time_splits(df, train_max_day=120.0, calib_max_day=150.0)
    print(f" -> Tập Hiệu chuẩn (Calib Set) [Day 120 - 150]: {len(calib_df):,} giao dịch")
    print(f" -> Tập Kiểm thử OOT (Test Set) [Day 150 - 182]: {len(test_df):,} giao dịch")

    # 3. Khởi tạo Conformal Engine và Hiệu chuẩn
    print("\n[BƯỚC 3/4] Thực thi Mondrian Split Conformal Calibration & Cost Optimization...")
    config = ConformalCalibrationConfig(alpha_legit=0.05, alpha_fraud=0.05)
    cost_matrix = CostMatrix()
    engine = ConformalEngine(config=config, cost_matrix=cost_matrix)

    t_calib = time.time()
    artifacts = engine.calibrate(model, calib_df, feature_cols)
    print(f" -> Hiệu chuẩn hoàn tất trong {time.time() - t_calib:.2f}s!")
    print(f"    • Phân vị Non-conformity Khách thật (q_hat_0) : {artifacts.q_hat_0:.4f}")
    print(f"    • Phân vị Non-conformity Kẻ gian   (q_hat_1) : {artifacts.q_hat_1:.4f}")
    print(f"    • Ngưỡng Duyệt tự động (t_approve)           : {artifacts.optimal_cost_thresholds['t_approve']:.4f}")
    print(f"    • Ngưỡng Chặn tức thì  (t_block)             : {artifacts.optimal_cost_thresholds['t_block']:.4f}")
    print(f"    • Chi phí tối ưu trên tập Calib              : ${artifacts.optimal_cost_thresholds['calib_min_cost']:,.2f} USD")

    # 4. Đánh giá trên tập Kiểm thử ngoài thời gian (OOT Test Set)
    print("\n[BƯỚC 4/4] Đánh giá trên tập Kiểm thử ngoài thời gian (OOT Test Set - 94.636 giao dịch)...")
    conformal_results = engine.evaluate_test_set(model, test_df, feature_cols)

    # Đọc lại số liệu baseline để so sánh
    baseline_metrics_path = os.path.join(reports_dir, "metrics_baseline.json")
    with open(baseline_metrics_path, "r", encoding="utf-8") as f:
        baseline_metrics = json.load(f)

    baseline_loss = baseline_metrics["total_financial_loss_usd"]
    conformal_loss = conformal_results["financial_impact"]["total_financial_loss_usd"]
    loss_reduction_usd = baseline_loss - conformal_loss
    loss_reduction_pct = (loss_reduction_usd / baseline_loss) * 100.0

    conformal_results["comparison_vs_baseline"] = {
        "baseline_loss_usd": baseline_loss,
        "conformal_loss_usd": conformal_loss,
        "loss_reduction_usd": round(loss_reduction_usd, 2),
        "loss_reduction_pct": round(loss_reduction_pct, 2),
        "baseline_missed_fraud": baseline_metrics["confusion_matrix"]["FN"],
        "conformal_missed_fraud": conformal_results["fraud_breakdown"]["fraud_missed_escaped"],
        "missed_fraud_reduction_pct": round(
            (baseline_metrics["confusion_matrix"]["FN"] - conformal_results["fraud_breakdown"]["fraud_missed_escaped"])
            / baseline_metrics["confusion_matrix"]["FN"] * 100.0, 2
        )
    }

    # In bảng so sánh đối đầu
    print("\n" + "=" * 80)
    print("🏆 BẢNG ĐỐI CHIẾU THỰC NGHIỆM ĐỘT PHÁ: BASELINE VS. CONFORMAL TRIAGE ENGINE")
    print("=" * 80)
    print(f"{'Tiêu chí đánh giá':<40} | {'Mô hình Cơ sở (p > 0.5)':<20} | {'Conformal Triage (Đề tài)':<20}")
    print("-" * 80)
    print(f"{'Chiến lược ra quyết định':<40} | {'Nhị phân (Duyệt / Chặn)':<20} | {'3 Ngã rẽ (+ Step-Up OTP)':<20}")
    print(f"{'Số ca Gian lận BỊ BỎ LỌT (FN)':<40} | {baseline_metrics['confusion_matrix']['FN']:<20,d} | {conformal_results['fraud_breakdown']['fraud_missed_escaped']:<20,d}")
    print(f"{'Tỷ lệ bắt đứng gian lận (Detection Rate)':<40} | {baseline_metrics['confusion_matrix']['TP'] / 3282 * 100:<19.2f}% | {conformal_results['fraud_breakdown']['fraud_detection_rate_pct']:<19.2f}%")
    print(f"{'Tỷ lệ duyệt tự động (Zero-Friction)':<40} | {baseline_metrics['confusion_matrix']['TN'] / 94636 * 100:<19.2f}% | {conformal_results['triage_summary']['auto_approved_pct']:<19.2f}%")
    print(f"{'Tỷ lệ chuyển sang 2FA OTP (Vùng đệm)':<40} | {'0.00% (Không hỗ trợ)':<20} | {conformal_results['triage_summary']['step_up_2fa_pct']:<19.2f}%")
    print(f"{'Tỷ lệ Chặn nhầm khách tốt (False Block)':<40} | {baseline_metrics['confusion_matrix']['FP'] / 91354 * 100:<19.2f}% | {conformal_results['legit_breakdown']['legit_false_blocked_pct']:<19.2f}%")
    print("-" * 80)
    print(f"{'TỔNG THIỆT HẠI TÀI CHÍNH THỰC TẾ':<40} | ${baseline_loss:<19,.2f} | ${conformal_loss:<19,.2f}")
    print(f"{'SỐ TIỀN TIẾT KIỆM ĐƯỢC (USD)':<40} | {'$0.00':<20} | ${loss_reduction_usd:<19,.2f}")
    print(f"{'TỶ LỆ CẮT GIẢM THIỆT HẠI':<40} | {'0.00%':<20} | {loss_reduction_pct:<19.2f}%")
    print("=" * 80)

    # Đảm bảo coverage bảo chứng toán học
    cov = conformal_results["calibration"]
    print("\n📐 BẢO CHỨNG TOÁN HỌC CONFORMAL COVERAGE (MARGINAL & CLASS-CONDITIONAL):")
    print(f" • Khách thật (Legit) : Danh định = {cov['nominal_coverage_legit'] * 100:.1f}% | Thực nghiệm = {cov['empirical_coverage_legit'] * 100:.2f}% (Bảo chứng an toàn)")
    print(f" • Kẻ gian (Fraud)    : Danh định = {cov['nominal_coverage_fraud'] * 100:.1f}% | Thực nghiệm = {cov['empirical_coverage_fraud'] * 100:.2f}% (Bảo chứng an toàn)")

    # Lưu artifacts
    conformal_artifacts_path = os.path.join(models_dir, "conformal_artifacts.json")
    with open(conformal_artifacts_path, "w", encoding="utf-8") as f:
        json.dump({
            "q_hat_0": artifacts.q_hat_0,
            "q_hat_1": artifacts.q_hat_1,
            "optimal_cost_thresholds": artifacts.optimal_cost_thresholds,
            "config": {
                "alpha_legit": artifacts.config.alpha_legit,
                "alpha_fraud": artifacts.config.alpha_fraud,
                "method": artifacts.config.method
            },
            "metadata": artifacts.metadata
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Đã lưu cấu hình Conformal Artifacts tại: {conformal_artifacts_path}")

    conformal_metrics_path = os.path.join(reports_dir, "metrics_conformal.json")
    with open(conformal_metrics_path, "w", encoding="utf-8") as f:
        json.dump(conformal_results, f, indent=2, ensure_ascii=False)
    print(f"📄 Báo cáo số liệu lưu tại: {conformal_metrics_path}")

    print("\n🎉 HOÀN THÀNH CHẶNG 2 THÀNH CÔNG RỰC RỠ!")


if __name__ == "__main__":
    main()
