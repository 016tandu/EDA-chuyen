"""
Script tự động tải bộ dữ liệu IEEE-CIS Fraud Detection từ public mirror Hugging Face.
Không yêu cầu tài khoản Kaggle, không cần kaggle.json hay API key.
"""

import os
import sys
import time
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

FILES = [
    {
        "name": "train_identity.csv",
        "url": "https://huggingface.co/datasets/aliceczr/ieee-fraud-detection/resolve/main/train_identity.csv",
        "expected_size_mb": 25.3,
    },
    {
        "name": "train_transaction.csv",
        "url": "https://huggingface.co/datasets/aliceczr/ieee-fraud-detection/resolve/main/train_transaction.csv",
        "expected_size_mb": 651.7,
    },
]


def download_file(url: str, dest_path: str):
    print(f"\n[DOWNLOAD] Bat dau tai tu: {url}")
    print(f"[DESTINATION] Luu vao: {dest_path}")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    
    with urllib.request.urlopen(req) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        total_size_mb = total_size / (1024 * 1024)
        
        # Kiem tra neu file da ton tai va du dung luong
        if os.path.exists(dest_path):
            existing_size = os.path.getsize(dest_path)
            if existing_size == total_size:
                print(f"[SKIP] File da ton tai va hoan chinh ({total_size_mb:.2f} MB): {dest_path}")
                return

        downloaded = 0
        chunk_size = 1024 * 1024  # 1MB per chunk
        start_time = time.time()
        last_print_time = start_time

        with open(dest_path, "wb") as f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                
                current_time = time.time()
                # Cap nhat tien trinh moi 1 giay
                if current_time - last_print_time >= 1.0 or downloaded == total_size:
                    elapsed = current_time - start_time
                    speed = (downloaded / (1024 * 1024)) / (elapsed if elapsed > 0 else 0.001)
                    percent = (downloaded / total_size) * 100 if total_size > 0 else 0
                    print(
                        f"\r -> Tien do: {percent:6.2f}% | "
                        f"{downloaded / (1024 * 1024):6.1f}/{total_size_mb:.1f} MB | "
                        f"Toc do: {speed:5.2f} MB/s | "
                        f"Thoi gian: {elapsed:.0f}s",
                        end="",
                        flush=True,
                    )
                    last_print_time = current_time

    print(f"\n[HOAN TAT] Da tai xong {os.path.basename(dest_path)}!")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"=== KHOI DONG PIPELINE TAI DU LIEU IEEE-CIS FRAUD DETECTION ===")
    print(f"Thu muc luu tru: {DATA_DIR}")

    target_files = FILES
    # Neu truyen tham so dong lenh de chon file cu the
    if len(sys.argv) > 1:
        chosen = sys.argv[1].lower()
        if chosen == "identity":
            target_files = [FILES[0]]
        elif chosen == "transaction":
            target_files = [FILES[1]]

    for item in target_files:
        dest = os.path.join(DATA_DIR, item["name"])
        download_file(item["url"], dest)

    print("\n=======================================================")
    print("[SUCCESS] Tat ca file da san sang phuc vu phan tich EDA!")
    print(f"Vi tri: {DATA_DIR}")


if __name__ == "__main__":
    main()
