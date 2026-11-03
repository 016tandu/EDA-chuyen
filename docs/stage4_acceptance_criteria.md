# STAGE 4: ACCEPTANCE CRITERIA (TIÊU CHÍ NGHIỆM THU TỰ ĐỘNG)
> **Chặng 4: Interactive Web Demo & Dual-View Risk Control Dashboard**  
> Hệ thống phòng thủ gian lận thanh toán thời gian thực theo kiến trúc Fast-Fail 4 tầng kết hợp Mondrian Conformal Prediction.

---

### Bảng Tiêu Chí Nghiệm Thu (Acceptance Criteria Matrix)

| Mã AC | Tên tiêu chí | Điều kiện CẦN & ĐỦ để tự động kết luận PASS |
| :--- | :--- | :--- |
| **AC-1** | **Web UI Serving & Static Delivery** | Tuyến đường `/` và `/dashboard` của FastAPI phải phản hồi mã HTTP 200, trả về trang HTML hoàn chỉnh chứa đầy đủ các thành phần UI, không phụ thuộc vào Node.js build tools. |
| **AC-2** | **Real-Time Telemetry Endpoint** | Tuyến đường `/api/v1/telemetry/stats` phải phản hồi mã HTTP 200 và cấu trúc JSON chứa: tổng giao dịch, phân bổ tầng chặn (Layer 1, 2, 3, 4), tỷ lệ thoát sớm (Early Fast-Fail Rate), phân bổ quyết định (Approve, 2FA, Block), và ước tính chi phí tài chính tiết kiệm ($ USD). |
| **AC-3** | **Dual-View UI Components** | Giao diện HTML phải tích hợp đầy đủ 2 phân hệ:<br>1. *Checkout Simulator*: Bộ chọn kịch bản mẫu, form thẻ thanh toán, nút giả lập quẹt thẻ, modal OTP 2FA.<br>2. *Risk Control Tower*: Thẻ KPI đo lường, biểu đồ phân phối triage thời gian thực, bảng nhật ký kiểm toán giao dịch (Audit Stream). |
| **AC-4** | **Interactive 2FA Challenge Workflow** | API và giao diện phải hỗ trợ luồng giải quyết nghi vấn (Step-up 2FA): Khi giao dịch rơi vào vùng bất định (conformal uncertainty zone), hệ thống yêu cầu xác thực OTP và ghi nhận kết quả xác thực thành công. |
| **AC-5** | **Automated QA & Telemetry Verification** | Script kiểm thử tự động `scripts/run_stage4_verification.py` mô phỏng toàn bộ các kịch bản thực tế qua API, kiểm tra số liệu telemetry lũy kế, đo đạc độ trễ và xuất báo cáo tự động vào thư mục `test_script_log/`. |
