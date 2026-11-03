// ==============================================================================
// CHƯƠNG 4: THIẾT KẾ KIẾN TRÚC & HIỆN THỰC HỆ THỐNG
// ==============================================================================

= CHƯƠNG 4: THIẾT KẾ KIẾN TRÚC & HIỆN THỰC HỆ THỐNG

== 4.1. Kiến trúc tổng thể Clean Architecture
Để đảm bảo tính độc lập giữa nghiệp vụ cốt lõi và các công nghệ bên ngoài (frameworks, databases, web servers), hệ thống được xây dựng tuân thủ nghiêm ngặt nguyên lý *Clean Architecture* (Kiến trúc sạch) gồm 4 vòng tròn đồng tâm:

+ *Lớp Thực thể Doanh nghiệp (Domain Layer):* Chứa đựng các quy tắc nghiệp vụ bất biến, độc lập hoàn toàn với framework bên ngoài. Bao gồm ma trận chi phí (`CostMatrix`), các thực thể phân loại rủi ro (`TriageDecision`, `Transaction`) và cấu trúc tập dự đoán Conformal (`ConformalPredictionSet`).
+ *Lớp Trường hợp Sử dụng (Usecase Layer):* Điều phối luồng dữ liệu nghiệp vụ của hệ thống. Bao gồm dịch vụ định chuẩn Conformal (`ConformalEngine`), kỹ nghệ đặc trưng (`FeatureEngineeringPipeline`) và bộ điều phối thanh toán 4 tầng (`PaymentTriageService`).
+ *Lớp Tiếp hợp (Adapter Layer):* Chuyển đổi dữ liệu giữa định dạng nội bộ và các dịch vụ ngoại vi. Bao gồm kho lưu trữ mô hình (`ModelRepository`), bộ đệm bất biến lũy đẳng (`IdempotencyCache`), động cơ quy tắc an ninh (`RuleEngine`) và bộ thu thập viễn trắc (`TelemetryCollector`).
+ *Lớp Cổng vào (Entrypoint Layer):* Điểm tiếp nhận tương tác trực tiếp với người dùng và hệ thống ngân hàng. Bao gồm ứng dụng web FastAPI (`app.py`), bộ lọc kiểm tra cú pháp Pydantic (`schemas.py`) và giao diện điều khiển hai phân hệ (`dashboard.html`).

== 4.2. Đường ống phòng thủ 4 tầng Fast-Fail (Layered Defense Pipeline)
Trong các đợt cao điểm mua sắm (Flash Sale hoặc Black Friday), hệ thống thanh toán phải xử lý hàng chục nghìn yêu cầu mỗi giây. Nếu mọi yêu cầu đều được chuyển thẳng đến mô hình học máy 440 đặc trưng, hệ thống sẽ nhanh chóng rơi vào tình trạng quá tải (CPU saturation). Do đó, chúng tôi thiết kế đường ống phòng thủ 4 tầng theo nguyên lý *Thất bại nhanh (Fast-Fail)*:

#v(0.2cm)

#figure(
  table(
    columns: (1.2fr, 2.0fr, 2.5fr, 1.3fr),
    align: (center + horizon, left + horizon, left + horizon, center + horizon),
    table.header(
      [*Tầng phòng thủ*],
      [*Thành phần đảm nhiệm*],
      [*Nhiệm vụ kiểm tra nghiệp vụ*],
      [*Độ trễ trung bình*]
    ),
    [*Layer 1*], [Schema Validation (Pydantic)], [Kiểm tra kiểu dữ liệu, biên số tiền $0 < A <= 10^6$, mã danh mục.], [$< 2.0 "ms"$],
    [*Layer 2*], [Blocking Rule Engine], [Kiểm tra danh sách đen (Blacklist Card/IP) và tần suất (Velocity Limiter).], [$< 3.0 "ms"$],
    [*Layer 3*], [Idempotency Cache (SHA-256)], [Băm khóa SHA-256 nội dung giao dịch, tái sử dụng kết quả trong 300s.], [$< 2.0 "ms"$],
    [*Layer 4*], [Conformal ML Inference], [Suy luận mô hình LightGBM, định chuẩn Conformal và ánh xạ ma trận chi phí.], [$< 25.0 "ms"$]
  ),
  caption: [Bảng chi tiết thông số kỹ thuật 4 tầng phòng thủ Fast-Fail],
) <tab:fast_fail_layers>

#v(0.3cm)

- *Cơ chế Layer 1 (Schema Fast-Fail):* Ngăn chặn các yêu cầu có cú pháp sai lệch (ví dụ số tiền âm, thiếu mã ngành hàng) ngay tại tầng Router của FastAPI trước khi chạm vào bộ nhớ nghiệp vụ, phản hồi HTTP 422 trong chưa đầy $2 "ms"$.
- *Cơ chế Layer 2 (Rule Engine Fast-Fail):* Động cơ luật an ninh đánh giá ngay lập tức xem thẻ hay địa chỉ IP có nằm trong danh sách đen bị báo mất/khóa hay không. Đồng thời, thuật toán cửa sổ trượt (Sliding Window Velocity Limiter) phát hiện các hành vi quét thẻ tự động (brute-force) với tần suất vượt quá $2$ giao dịch trong $30$ giây, ngắt lỗi HTTP 403 tức thì.
- *Cơ chế Layer 3 (Idempotency Cache Fast-Fail):* Do độ trễ mạng Internet, người dùng thường có xu hướng bấm nút "Thanh toán" liên tiếp nhiều lần. Bộ đệm tính lũy đẳng băm toàn bộ payload thành chuỗi băm mật mã SHA-256. Nếu chuỗi băm đã tồn tại trong bộ nhớ đệm (TTL 300s), hệ thống trả về kết quả đã xử lý trước đó ngay lập tức mà không chạy lại mô hình học máy.
- *Cơ chế Layer 4 (Conformal ML Inference):* Chỉ các giao dịch hợp lệ, độc nhất và không vi phạm quy tắc an ninh cơ bản mới được chuyển tiếp vào tầng suy luận học máy Conformal để phân loại 3 ngã rẽ.

== 4.3. Kỹ thuật tối ưu hóa độ trễ suy luận 1-row (Single-Row Latency Engineering)
Trong quá trình thử nghiệm ban đầu, chúng tôi phát hiện một nút thắt cổ chai hiệu năng nghiêm trọng: Việc tái khởi tạo một đối tượng `pandas.DataFrame` gồm đầy đủ $440$ cột đặc trưng trong vòng lặp xử lý của từng yêu cầu mất tới xấp xỉ $80 "ms"$ (làm độ trễ $p_99$ vọt lên $94.72 "ms"$, vi phạm nghiêm trọng cam kết SLA $< 40 "ms"$).

Để giải quyết triệt để nút thắt này, chúng tôi đã tái cấu trúc tầng xử lý dữ liệu bằng kỹ thuật *Template Caching & In-place Injection*:
+ Khởi tạo một mẫu mảng tĩnh (`self._template`) sẵn trong bộ nhớ trong hàm khởi tạo của `PaymentTriageService`, trong đó toàn bộ $440$ cột đặc trưng được định kiểu sẵn bằng mảng `numpy.ndarray` kiểu `float32` hoặc `pandas.Categorical`.
+ Khi một yêu cầu mới được gửi đến, dịch vụ chỉ sao chép con trỏ tham chiếu của template, chèn trực tiếp các giá trị số từ `CheckoutRequest` vào các vị trí bộ nhớ tương ứng mà không thực hiện kiểm tra kiểu (type inference) lại từ đầu.
+ Nhờ giải pháp này, thời gian tạo hàng dữ liệu đặc trưng $1$-row giảm từ $80 "ms"$ xuống chỉ còn *$2.2 "ms"$*, giúp tổng thời gian suy luận tại tầng 4 đạt trung bình $22 "ms"$ và độ trễ $p_99$ toàn hệ thống duy trì ổn định ở mức *$27.57 "ms"$*.

== 4.4. Hiện thực giao diện điều khiển trực quan hai phân hệ (Dual-View Dashboard)
Nhằm hỗ trợ quá trình theo dõi và vận hành nghiệp vụ trực quan, hệ thống cung cấp giao diện web tương tác hai phân hệ:
- *Phân hệ 1: Cổng thanh toán mô phỏng (Customer Checkout Simulator):* Cung cấp các kịch bản kiểm thử mẫu (Khách hàng VIP, Giao dịch lớn bất định, Thẻ báo mất, Tấn công tần suất), hiển thị quy trình xử lý qua từng tầng, trực quan hóa tiến trình xác thực 2 bước (OTP Modal) và kết quả phân loại rủi ro.
- *Phân hệ 2: Tháp giám sát rủi ro ngân hàng (Risk Control Tower):* Kết nối trực tiếp với API viễn trắc `/api/v1/telemetry/stats` để vẽ biểu đồ phân phối triage 3 ngã rẽ theo thời gian thực (Chart.js), theo dõi tỷ lệ ngắt sớm (Early Fast-Fail Exit Rate), tổng chi phí tổn thất đã cứu vãn và bảng nhật ký kiểm toán giao dịch (Audit Stream).






