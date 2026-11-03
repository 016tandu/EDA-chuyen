# STAGE 5: ACCEPTANCE CRITERIA (TIÊU CHÍ NGHIỆM THU TỰ ĐỘNG)
> **Chặng 5: Báo Cáo Khóa Luận Tốt Nghiệp bằng Typst (Academic Research Thesis)**  
> Đề tài: *Khung Định Chuẩn Bất Định Conformal Thích Ứng Tối Ưu Chi Phí Cho Hệ Thống Phân Loại Rủi Ro Gian Lận Thanh Toán Thời Gian Thực*.

---

### Bảng Tiêu Chí Nghiệm Thu (Acceptance Criteria Matrix)

| Mã AC | Tên tiêu chí | Điều kiện CẦN & ĐỦ để tự động kết luận PASS |
| :--- | :--- | :--- |
| **AC-1** | **Cấu Trúc Bố Cục Chuẩn ĐHQG** | Toàn bộ tài liệu được tổ chức theo quy chuẩn Khóa luận tốt nghiệp của Đại học Quốc gia: Trang bìa chính, bìa phụ, khung viền chuẩn, placeholder logo trường nằm ở giữa, lời cam đoan, lời cảm ơn, tóm tắt tiếng Việt/Anh, bảng thuật ngữ, danh mục bảng biểu/hình vẽ, và mục lục tự động. |
| **AC-2** | **Cấu Trúc 7 Chương & Thuật Toán Toán Học** | Triển khai đầy đủ 7 chương học thuật theo chuẩn `AGENT_PLAYBOOK.md` (`01_introduction.typ` đến `07_conclusion.typ`). Tất cả công thức toán học về Nonconformity Score, Mondrian Split Conformal Prediction, Quantile Calibration, và Cost Matrix Optimization được render chuẩn xác bằng cú pháp Typst toán học. |
| **AC-3** | **Độ Toàn Vẹn Thuật Ngữ & Dữ Liệu Thực Nghiệm** | Có Bảng giải thích thuật ngữ chuyên ngành đầy đủ (Việt - Anh). Số liệu thực nghiệm khớp 100% với các kết quả đã đo đạc thực tế trên tập dữ liệu IEEE-CIS (590,540 giao dịch, giảm tổn thất 94.54% từ $392,641 xuống $21,456 USD, SLA $p_{99} = 27.57\text{ms}$). |
| **AC-4** | **Kiểm Soát Layout & Chống Tràn Bảng (No Overflow/Empty Pages)** | Tất cả các bảng biểu phải thiết lập kích thước cột tương đối (`1fr`, `%`), kích hoạt ngắt dòng tự động, căn lề nhất quán, tuyệt đối không bị tràn lề ngang trang (horizontal overflow) và không tạo trang trống do ngắt trang bất hợp lý. |
| **AC-5** | **Tự Động Biên Dịch PDF & Log Dumping** | Script kiểm thử tự động `scripts/run_stage5_verification.py` gọi trình biên dịch `typst compile`, kiểm tra mã thoát trả về 0, xác nhận file `report/thesis.pdf` được tạo thành công, kích thước tệp $> 50\text{ KB}$, và dump toàn bộ nhật ký kiểm tra vào thư mục `test_script_log/`. |
