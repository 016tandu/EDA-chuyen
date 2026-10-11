# CỔNG THANH TOÁN PHÂN LOẠI RỦI RO GIAN LẬN CONFORMAL (FINTECH IS)
> **Tên đề tài khoa học:** *"An Adaptive Cost-Sensitive Conformal Calibration Framework for Real-Time Fraud Triage in Distributed Payment Information Systems"*  
> **Khóa luận Tốt nghiệp ngành Hệ thống Thông tin (HTTT)**  
> **Tiêu chuẩn vận hành & kiến trúc:** Tuân thủ chuẩn [AGENT_PLAYBOOK.md](./AGENT_PLAYBOOK.md).

---

## 📌 DANH MỤC TÀI LIỆU & TÀI NGUYÊN DỰ ÁN

1. 📖 **[AGENT_PLAYBOOK.md](./AGENT_PLAYBOOK.md):** Quy trình 7 bước (Life-Cycle), tiêu chuẩn Anti-"MID" và quy ước kỹ thuật.
2. 📚 **[docs/data_dictionary_ieee_cis.md](./docs/data_dictionary_ieee_cis.md):** **Từ điển dữ liệu đầy đủ**, giải mã tác giả Vesta & IEEE-CIS, giải thích các cột C1-C14, D1-D15, M1-M9, V1-V339 và kỹ nghệ định danh khách hàng Magic UID.
3. 📁 **[candidate_explanations/](./candidate_explanations/):** Thư mục hồ sơ giải thích chi tiết 2 ứng viên đề tài Khóa luận HTTT.
4. 📓 **[notebooks/01_ieee_cis_eda.ipynb](./notebooks/01_ieee_cis_eda.ipynb):** **File Jupyter Notebook EDA hoàn chỉnh**, đã thực thi trực tiếp trên toàn bộ 590.540 dòng dữ liệu kèm biểu đồ và bảng thống kê thực tế.
5. 📊 **[reports/figures/](./reports/figures/):** Thư mục lưu trữ biểu đồ phân phối nhãn, phân phối số tiền giao dịch và minh chứng Concept Drift theo tuần.
6. 📈 **[progress.md](./progress.md):** Bảng theo dõi tiến độ và lịch sử Git commit theo chuẩn Playbook.

---

## 🛠️ HƯỚNG DẪN MÔI TRƯỜNG & CHẠY DỰ ÁN (UV & VIRTUAL ENVIRONMENT)

Dự án được đóng gói và quản lý phụ thuộc hoàn toàn bằng **`uv`**:

```powershell
# 1. Kích hoạt môi trường ảo
.venv\Scripts\activate

# 2. Chạy tái sinh và thực thi Notebook EDA
uv run python scripts\generate_and_run_eda_notebook.py

# 3. Mở Jupyter Notebook để xem trực tiếp
uv run jupyter notebook notebooks/01_ieee_cis_eda.ipynb
```
