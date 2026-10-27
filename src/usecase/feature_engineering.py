"""
Module: Feature Engineering & Preprocessing Pipeline
Thực hiện:
1. Nạp dữ liệu giao dịch và định danh từ Parquet
2. Ghép dữ liệu & Tạo các đặc trưng Magic UID (Card_ID, Client_UID)
3. Tạo các đặc trưng chuỗi thời gian & tỷ lệ số tiền (TransactionAmt relative to group stats)
4. Phân chia tập dữ liệu theo trục thời gian (Time-based Split):
   - Train: 4 tháng đầu (Day 0 - 120)
   - Calibration (Dùng cho Conformal Prediction): Tháng thứ 5 (Day 120 - 150)
   - Test (Dùng kiểm thử Concept Drift & Out-of-time): Tháng thứ 6 (Day 150 - 182)
"""

import os
import polars as pl
import numpy as np
from typing import Tuple, List, Dict


def load_raw_parquet(data_dir: str) -> pl.DataFrame:
    """Nạp và nối bảng transaction + identity từ processed parquet."""
    tx_path = os.path.join(data_dir, "train_transaction.parquet")
    id_path = os.path.join(data_dir, "train_identity.parquet")

    df_tx = pl.read_parquet(tx_path)
    df_id = pl.read_parquet(id_path)

    # Nối bảng qua TransactionID (Left join)
    df = df_tx.join(df_id, on="TransactionID", how="left")
    return df


def engineer_magic_uid(df: pl.DataFrame) -> pl.DataFrame:
    """Tạo các định danh Card_ID và Client_UID theo công thức Magic UID."""
    df = df.with_columns([
        (pl.col("TransactionDT") / 86400.0).alias("Day"),
        ((pl.col("TransactionDT") % 86400) // 3600).cast(pl.Int32).alias("hour_of_day"),
        (((pl.col("TransactionDT") // 86400) % 7)).cast(pl.Int32).alias("day_of_week"),
    ])

    # Card_ID = card1_card2_card3_card4_card6_addr1
    card_id_expr = (
        pl.col("card1").cast(pl.String) + "_" +
        pl.col("card2").cast(pl.String).fill_null("0") + "_" +
        pl.col("card3").cast(pl.String).fill_null("0") + "_" +
        pl.col("card4").cast(pl.String).fill_null("na") + "_" +
        pl.col("card6").cast(pl.String).fill_null("na") + "_" +
        pl.col("addr1").cast(pl.String).fill_null("0")
    ).alias("Card_ID")

    df = df.with_columns(card_id_expr)

    # Card_Birth_Day = Day - D1
    birth_day_expr = (
        (pl.col("Day") - pl.col("D1").fill_null(0.0)).round(1).cast(pl.String)
    ).alias("Card_Birth_Day")

    df = df.with_columns(birth_day_expr)

    # Client_UID = Card_ID + Card_Birth_Day
    client_uid_expr = (
        pl.col("Card_ID") + "_" + pl.col("Card_Birth_Day")
    ).alias("Client_UID")

    df = df.with_columns(client_uid_expr)
    return df


def engineer_group_aggregations(df: pl.DataFrame) -> pl.DataFrame:
    """Tạo các đặc trưng thống kê nhóm và tần suất quẹt thẻ."""
    # 1. Tần suất giao dịch của Card_ID và Client_UID
    card_counts = df.group_by("Card_ID").agg(pl.len().alias("card_freq"))
    client_counts = df.group_by("Client_UID").agg(pl.len().alias("client_freq"))

    df = df.join(card_counts, on="Card_ID", how="left")
    df = df.join(client_counts, on="Client_UID", how="left")

    # 2. Thống kê số tiền giao dịch theo card1
    card1_amt_stats = df.group_by("card1").agg([
        pl.col("TransactionAmt").mean().alias("card1_amt_mean"),
        pl.col("TransactionAmt").std().alias("card1_amt_std"),
    ])
    df = df.join(card1_amt_stats, on="card1", how="left")

    # Tỷ lệ số tiền giao dịch so với trung bình của ngân hàng/dải thẻ (card1)
    df = df.with_columns([
        (pl.col("TransactionAmt") / (pl.col("card1_amt_mean") + 1e-5)).alias("amt_to_mean_card1"),
        ((pl.col("TransactionAmt") - pl.col("card1_amt_mean")) / (pl.col("card1_amt_std") + 1e-5)).alias("amt_to_std_card1"),
        (pl.col("TransactionAmt").log1p()).alias("log_TransactionAmt"),
    ])

    return df


def prepare_time_splits(
    df: pl.DataFrame,
    train_max_day: float = 120.0,
    calib_max_day: float = 150.0
) -> Tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """
    Phân tách theo trục thời gian (Time-based split):
    - Train: Day < 120 (4 tháng đầu, ~390.000 mẫu)
    - Calibration: 120 <= Day < 150 (tháng thứ 5, ~100.000 mẫu)
    - Test: Day >= 150 (tháng thứ 6, ~100.000 mẫu)
    """
    train_df = df.filter(pl.col("Day") < train_max_day)
    calib_df = df.filter((pl.col("Day") >= train_max_day) & (pl.col("Day") < calib_max_day))
    test_df = df.filter(pl.col("Day") >= calib_max_day)

    return train_df, calib_df, test_df
