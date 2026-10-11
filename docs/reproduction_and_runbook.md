# HƯỚNG DẪN TÁI LẬP MÔI TRƯỜNG & THỰC THI TOÀN BỘ HỆ THỐNG (RUNBOOK)
> **Dành cho:** Người dùng, Giảng viên hướng dẫn & Hội đồng bảo vệ Khóa luận  
> **Dự án:** Cổng thanh toán phân loại rủi ro Conformal (FinTech IS)  
> **Quy chuẩn kỹ thuật:** Tuân thủ chuẩn vận hành [AGENT_PLAYBOOK.md](../AGENT_PLAYBOOK.md)

---

## 1. TỔNG QUAN & YÊU CẦU TIỀN ĐỀ (PREREQUISITES)

Hệ thống được thiết kế theo tiêu chuẩn kỹ sư phần mềm hiện đại, đóng gói toàn bộ qua công cụ quản lý môi trường siêu tốc **`uv`** (thay thế cho `pip`, `conda`, `poetry` chậm chạp).

* **Hệ điều hành:** Windows 10/11 (PowerShell Core hoặc Windows PowerShell).
* **Python Runtime:** Python 3.10+ (được quản lý tự động bởi `uv`).
* **Công cụ cốt lõi:**
  * `uv`: Quản lý môi trường ảo và thư viện (`scoop install uv` hoặc cài đặt qua [astral.sh/uv](https://astral.sh/uv)).
  * `git`: Quản lý phiên bản mã nguồn (`scoop install git`).

---

## 2. QUY TRÌNH THỰC THI TỪNG BƯỚC TỪ ĐẦU (STEP-BY-STEP FROM SCRATCH)

Nếu bạn vừa clone repository này về một máy tính hoàn toàn mới, hãy thực hiện theo đúng 5 bước sau:

```mermaid
flowchart LR
    A["Bước 1: Khởi tạo môi trường uv"] --> B["Bước 2: Kéo dữ liệu tự động (Hugging Face)"]
    B --> C["Bước 3: Chuyển đổi nén Parquet"]
    C --> D["Bước 4: Chạy Notebook & Báo cáo EDA"]
    D --> E["Bước 5: Khởi động Cổng API & Web Demo"]
```

### Bước 1: Khởi tạo Môi trường Ảo & Tự Động Cài Đặt Thư Viện

Không cần gõ từng lệnh `pip install`, `uv` sẽ đọc trực tiếp từ `pyproject.toml` và `uv.lock` để cài đặt môi trường chính xác 100% trong vòng **10 giây**:

```powershell
# Di chuyển vào thư mục gốc của dự án
cd C:\Users\PC\Documents\Git\EDA-chuyen

# Tạo môi trường ảo .venv
uv venv .venv

# Kích hoạt môi trường ảo trên Windows PowerShell
.venv\Scripts\activate

# Cài đặt đồng bộ toàn bộ 53 thư viện phụ thuộc (Polars, Pandas, Matplotlib, Jupyter,...)
uv sync
```

---

### Bước 2: Tự Động Tải Bộ Dữ Liệu IEEE-CIS Fraud Detection

Không cần đăng ký tài khoản Kaggle hay tạo file `kaggle.json`. Hệ thống đã tích hợp sẵn pipeline tự động kéo dữ liệu từ public mirror chuẩn trên Hugging Face:

```powershell
# Chạy pipeline tự động tải dữ liệu gốc (train_identity.csv & train_transaction.csv)
uv run python scripts\download_ieee_data.py
```

* **Kết quả mong đợi:**
  * Dữ liệu được lưu vào: `data/raw/`
  * `train_identity.csv`: ~26.5 MB
  * `train_transaction.csv`: ~683.4 MB
  * Tốc độ tải: ~30 - 50 MB/s (toàn bộ quá trình chỉ mất 15-20 giây).

---

### Bước 3: Tái Sinh & Thực Thi Toàn Bộ Jupyter Notebook EDA

Để đảm bảo toàn bộ số liệu và đồ thị trong báo cáo là số liệu thật, chạy lệnh sinh tự động và thực thi toàn bộ notebook:

```powershell
# Chạy script thực thi tự động qua nbclient
uv run python scripts\generate_and_run_eda_notebook.py
```

* **Quy trình script tự động thực hiện:**
  1. Nạp 590.540 dòng giao dịch bằng Polars trong 3.9 giây.
  2. Đo đạc tỷ lệ mất cân bằng dữ liệu (3.5% gian lận).
  3. Phân tích phân phối số tiền giao dịch và vẽ biểu đồ mật độ KDE.
  4. Phân tích hiện tượng trôi dạt dữ liệu theo tuần (Concept Drift).
  5. Giải mã các trường bí ẩn C1-C14, D1-D15, M1-M9.
  6. Áp dụng công thức Magic UID, gom 590.540 giao dịch về 41.888 thẻ vật lý và 387.059 khách hàng.
  7. Chuyển đổi dữ liệu sang định dạng nén Apache Parquet (`data/processed/train_transaction.parquet`, giảm 89.3% dung lượng).
  8. Xuất toàn bộ biểu đồ vào thư mục `reports/figures/`.

---

### Bước 4: Mở Xem & Tương Tác Trực Tiếp Với Notebook

Bạn có thể mở giao diện Jupyter tương tác để duyệt từng cell và chạy thử các tham số mới:

```powershell
uv run jupyter notebook notebooks/01_ieee_cis_eda.ipynb
```

Hoặc mở trực tiếp file `notebooks/01_ieee_cis_eda.ipynb` trong IDE Cursor / VS Code (chọn Kernel là `.venv (Python 3.10)`).

---

## 3. CÁC QUY TẮC KỸ THUẬT & KINH NGHIỆM ĐÃ ĐƯỢC CHUẨN HÓA (CODING CONVENTIONS)

Trong quá trình triển khai thực tế, các bài học kinh nghiệm sau đã được ghi nhận và bắt buộc áp dụng cho toàn bộ các module tiếp theo:

### 3.1. Quy chuẩn Thư viện Polars (Polars 2.0+ Compatibility)
* **Tuyệt đối không dùng `pl.count()` không tham số:** Trong Polars 2.0+, để đếm số dòng khi gom nhóm (`group_by`), bắt buộc dùng `pl.len()`.
* **Quy chuẩn kiểu chuỗi:** Sử dụng `pl.String` thay vì `pl.Utf8`.
* **Suy luận kiểu dữ liệu an toàn:** Khi đọc các file CSV lớn có nhiều giá trị thiếu (`null`), luôn khai báo `infer_schema_length=10000` để tránh lỗi xung đột kiểu giữa các dòng đầu và các dòng sau.

### 3.2. Quy chuẩn Đường dẫn Động (Dynamic Path Resolution)
* Không bao giờ hardcode đường dẫn tương đối cứng như `../data/raw/` trong các notebook hay script, vì khi người dùng chạy từ thư mục gốc hoặc từ thư mục con `notebooks/` sẽ gây lỗi `FileNotFoundError`.
* **Mẫu chuẩn bắt buộc:**
  ```python
  import os
  PROJECT_ROOT = os.path.abspath(os.getcwd())
  if not os.path.exists(os.path.join(PROJECT_ROOT, "data", "raw")):
      PROJECT_ROOT = os.path.abspath(os.path.join(os.getcwd(), ".."))
  RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
  ```

### 3.3. Quy chuẩn Mã hóa Tiếng Việt trên Windows PowerShell
* Mặc định terminal Windows sử dụng bảng mã `cp1252` hoặc `cp936`, dễ gây lỗi `UnicodeEncodeError` khi in các chuỗi tiếng Việt có dấu.
* Khi viết script xuất console tiếng Việt hoặc ghi file text/json, luôn thiết lập UTF-8:
  ```python
  import sys
  if sys.platform == "win32":
      sys.stdout.reconfigure(encoding="utf-8")
  ```

### 3.4. Chiến lược Tối ưu hóa Bộ nhớ & Lưu trữ Parquet
* Các file CSV thô nặng $> 500\text{ MB}$ chỉ dùng một lần duy nhất tại bước tiền xử lý.
* Sau khi nạp, bắt buộc nén sang định dạng **Apache Parquet (`compression='zstd'`)**. Parquet giúp:
  * Giảm dung lượng đĩa từ 683 MB xuống còn ~70 MB (tiết kiệm 89%).
  * Giữ nguyên 100% định dạng kiểu dữ liệu (data types) mà không cần parse lại.
  * Tốc độ nạp vào bộ nhớ RAM cho các bước huấn luyện máy học sau này chỉ mất dưới 0.8 giây.
