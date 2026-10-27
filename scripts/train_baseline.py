"""
Script: Huấn luyện và Đánh giá Mô hình Cơ sở (Baseline Training Runner)
Thực thi:
1. Nạp và xử lý đặc trưng (Feature Engineering) từ dữ liệu Parquet
2. Phân chia tập dữ liệu Time-based Split (Train: Day < 120, Calib: 120-150, Test: >= 150)
3. Huấn luyện mô hình cơ sở LightGBM (chuẩn baseline $p > 0.5$)
4. Đánh giá toàn diện trên tập kiểm thử ngoài thời gian (Out-Of-Time Test Set)
5. Lưu trữ mô hình và số liệu thực nghiệm
"""

import os
import sys
import time
import json

# Dam bao import duoc src.*
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from src.usecase.feature_engineering import (
    load_raw_parquet,
    engineer_magic_uid,
    engineer_group_aggregations,
    prepare_time_splits,
)
from src.usecase.baseline_model import (
    get_feature_columns,
    prepare_lightgbm_data,
    train_baseline_lightgbm,
    evaluate_model,
)
from src.adapter.model_repository import ModelRepository
from src.domain.cost_matrix import CostMatrix


def main():
    print("=" * 70)
    print("🚀 BẮT ĐẦU QUY TRÌNH HUẤN LUYỆN MÔ HÌNH CƠ SỞ (BASELINE LIGHTGBM)")
    print("=" * 70)

    data_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    models_dir = os.path.join(PROJECT_ROOT, "models")
    reports_dir = os.path.join(PROJECT_ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Nạp và kỹ nghệ đặc trưng
    t0 = time.time()
    print("\n[BƯỚC 1/5] Nạp dữ liệu Parquet và ghép bảng (Left Join)...")
    df = load_raw_parquet(data_dir)
    print(f" -> Đã nạp {len(df):,} giao dịch, {len(df.columns)} cột.")

    print("\n[BƯỚC 2/5] Kỹ nghệ đặc trưng Magic UID & Nhóm thống kê...")
    df = engineer_magic_uid(df)
    df = engineer_group_aggregations(df)
    print(f" -> Hoàn tất kỹ nghệ đặc trưng ({time.time() - t0:.2f}s). Tổng số cột hiện tại: {len(df.columns)}")

    # 2. Phân chia Time-based split
    print("\n[BƯỚC 3/5] Phân tách tập dữ liệu theo trục thời gian (Time-based Split)...")
    train_df, calib_df, test_df = prepare_time_splits(df, train_max_day=120.0, calib_max_day=150.0)

    train_fraud_rate = (train_df["isFraud"].mean() * 100)
    calib_fraud_rate = (calib_df["isFraud"].mean() * 100)
    test_fraud_rate = (test_df["isFraud"].mean() * 100)

    print(f" -> Tập Huấn luyện (Train)     [Day 0 - 120]  : {len(train_df):,} mẫu | Gian lận: {train_fraud_rate:.2f}%")
    print(f" -> Tập Hiệu chuẩn (Calib)     [Day 120 - 150]: {len(calib_df):,} mẫu | Gian lận: {calib_fraud_rate:.2f}%")
    print(f" -> Tập Kiểm thử OOT (Test)    [Day 150 - 182]: {len(test_df):,} mẫu | Gian lận: {test_fraud_rate:.2f}%")

    # 3. Chuẩn bị dữ liệu huấn luyện
    feature_cols = get_feature_columns(df)
    print(f" -> Số lượng đặc trưng đưa vào mô hình: {len(feature_cols)} features.")

    print("\n[BƯỚC 4/5] Chuyển đổi dữ liệu và huấn luyện LightGBM...")
    train_data, val_data, cat_features = prepare_lightgbm_data(train_df, calib_df, feature_cols)

    t_train = time.time()
    model = train_baseline_lightgbm(
        train_data=train_data,
        val_data=val_data,
        categorical_features=cat_features,
        num_boost_round=400,
        early_stopping_rounds=30
    )
    print(f" -> Huấn luyện hoàn tất trong {time.time() - t_train:.2f} giây.")

    # 4. Đánh giá mô hình trên tập kiểm thử OOT
    print("\n[BƯỚC 5/5] Đánh giá toàn diện trên tập Kiểm thử ngoài thời gian (Out-Of-Time Test Set)...")
    cost_matrix = CostMatrix()
    metrics_05 = evaluate_model(model, test_df, feature_cols, cost_matrix=cost_matrix, threshold=0.5)

    print("\n" + "=" * 50)
    print("📊 KẾT QUẢ ĐÁNH GIÁ THỰC NGHIỆM MÔ HÌNH CƠ SỞ (BASELINE):")
    print("=" * 50)
    print(f" • ROC-AUC              : {metrics_05['roc_auc']:.4f}")
    print(f" • PR-AUC (Avg Precision): {metrics_05['pr_auc']:.4f}")
    print(f" • Brier Score          : {metrics_05['brier_score']:.4f}")
    print(f" • Ngưỡng quyết định    : {metrics_05['threshold']}")
    print(f" • Ma trận nhầm lẫn (CM):")
    print(f"    - True Negatives  (TN): {metrics_05['confusion_matrix']['TN']:,}")
    print(f"    - False Positives (FP): {metrics_05['confusion_matrix']['FP']:,} (Chặn nhầm khách tốt)")
    print(f"    - False Negatives (FN): {metrics_05['confusion_matrix']['FN']:,} (Bỏ lọt gian lận)")
    print(f"    - True Positives  (TP): {metrics_05['confusion_matrix']['TP']:,} (Bắt đúng kẻ gian)")
    print(f" • TỔNG THIỆT HẠI TÀI CHÍNH : ${metrics_05['total_financial_loss_usd']:,.2f} USD")
    print("=" * 50)

    # 5. Lưu trữ Model và Báo cáo
    repo = ModelRepository(base_dir=models_dir)
    save_dir = repo.save_model(
        model_name="baseline_lightgbm",
        model=model,
        features=feature_cols,
        metrics=metrics_05,
        metadata={
            "train_samples": len(train_df),
            "calib_samples": len(calib_df),
            "test_samples": len(test_df),
            "categorical_features": cat_features
        }
    )
    print(f"\n💾 Đã lưu trữ mô hình và metadata tại: {save_dir}")

    metrics_file = os.path.join(reports_dir, "metrics_baseline.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics_05, f, indent=2, ensure_ascii=False)
    print(f"📄 Báo cáo số liệu lưu tại: {metrics_file}")
    print("\n🎉 HOÀN THÀNH CHẶNG 1 THÀNH CÔNG 100%!")


if __name__ == "__main__":
    main()
