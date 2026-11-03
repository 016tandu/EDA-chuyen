# STAGE 3: ACCEPTANCE CRITERIA (TIÊU CHÍ NGHIỆM THU ĐỘC LẬP)
> **Mục tiêu:** Xây dựng Cổng Dịch vụ Thanh toán (Payment Checkout API) theo chuẩn Clean Architecture với cơ chế phòng thủ 4 tầng (4-Layer Fast-Fail Defense-in-Depth).  
> **Quy tắc:** Hệ thống tự động kiểm chứng và chỉ kết luận hoàn thành Stage 3 khi 100% các tiêu chí dưới đây đều ĐẠT (PASS) mà không cần sự can thiệp thủ công của người dùng.

---

## 1. DANH SÁCH TIÊU CHÍ NGHIỆM THU (AC-1 ĐẾN AC-7)

| Mã tiêu chí | Tên tiêu chí | Điều kiện cần và đủ (Cần ĐẠT 100%) | Ngưỡng đo lường (Threshold) |
| :--- | :--- | :--- | :--- |
| **AC-1** | **Clean Architecture & Endpoints** | Cấu trúc phân tầng rõ rệt: `entrypoint/api`, `usecase/`, `adapter/`, `domain/`. Cung cấp đầy đủ 2 endpoints: `GET /api/v1/health` và `POST /api/v1/checkout/triage`. | HTTP 200 cho healthcheck & API sẵn sàng |
| **AC-2** | **Layer 1: Schema Fast-Fail** | Dữ liệu sai cú pháp (số tiền âm, thiếu mã thẻ, sai định dạng) bị chặn ngay tại Pydantic. | Trả về HTTP 422 trong thời gian $< 5\text{ms}$, KHÔNG đi tiếp vào Layer 2-4 |
| **AC-3** | **Layer 2: Rule Engine Fast-Fail** | Thẻ/IP nằm trong danh sách đen (Blacklist) hoặc vượt quá tần suất quẹt thẻ (Velocity > 5 lần/10s) bị từ chối lập tức. | Trả về HTTP 403/400 trong thời gian $< 5\text{ms}$, KHÔNG tiêu tốn tài nguyên gọi AI |
| **AC-4** | **Layer 3: Idempotency Cache** | Gửi cùng một giao dịch nhiều lần (chống double-charge) qua băm SHA-256. | Trả về HTTP 200 với kết quả cũ đã lưu, độ trễ $< 3\text{ms}$, cờ `cache_hit = true` |
| **AC-5** | **Layer 4: Conformal 3-Way Triage** | Giao dịch hợp lệ đi tới mô hình AI, phân loại chuẩn xác 3 ngã rẽ: `APPROVE`, `STEP_UP_2FA`, `BLOCK` kèm lý giải p-value. | Trả về đúng quyết định và xác suất rủi ro theo model đã hiệu chuẩn |
| **AC-6** | **Latency & Performance SLA** | Kiểm thử tải tự động 60 requests đa dạng (Hợp lệ, Rác, Blacklist, Trùng lặp, Nghi vấn). | Độ trễ đuôi $p_{99} < 40\text{ms}$, trung bình $< 25\text{ms}$ |
| **AC-7** | **Automated QA & Log Dumping** | Toàn bộ kịch bản kiểm thử được tự động thực thi bởi AI, kết quả xuất ra thư mục `test_script_log/`. | 100% test cases PASS (0 thất bại), có file log và summary JSON |
