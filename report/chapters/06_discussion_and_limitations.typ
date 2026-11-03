// ==============================================================================
// CHƯƠNG 6: THẢO LUẬN, ĐÁNH GIÁ ĐỘ TIN CẬY & HẠN CHẾ
// ==============================================================================

= CHƯƠNG 6: THẢO LUẬN, ĐÁNH GIÁ ĐỘ TIN CẬY & HẠN CHẾ

== 6.1. Đánh giá độ tin cậy khoa học (Threats to Validity)
Để bảo đảm tính nghiêm ngặt học thuật theo chuẩn nghiên cứu khoa học quốc tế, chúng tôi tiến hành phân tích ba khía cạnh đe dọa độ tin cậy của công trình:

+ *Độ tin cậy nội tại (Internal Validity):*
  - Nguy cơ rò rỉ dữ liệu (Data Leakage): Việc phân chia tập dữ liệu ngẫu nhiên (Random K-Fold Cross-Validation) thường dẫn đến rò rỉ thông tin tương lai về quá khứ do tính chất phụ thuộc thời gian của các giao dịch thẻ. Chúng tôi triệt tiêu nguy cơ này bằng cách áp dụng phân chia nghiêm ngặt theo trục thời gian (Time-based Split) với ba tập Train, Calib và OOT Test hoàn toàn cách biệt.
  - Tính ổn định của kỹ nghệ đặc trưng: Toàn bộ các đặc trưng thống kê lũy kế (`amt_to_mean_card1`, `card_freq`) đều chỉ được tính toán dựa trên dữ liệu lịch sử đã xuất hiện trước thời điểm giao dịch phát sinh.
+ *Độ tin cậy bên ngoài (External Validity):*
  - Bộ dữ liệu thực nghiệm IEEE-CIS đại diện cho các giao dịch thương mại điện tử qua thẻ trực tuyến (Card-Not-Present). Khi chuyển giao sang các môi trường thanh toán khác như quẹt thẻ vật lý tại điểm bán (Point-of-Sale - POS), thanh toán xuyên biên giới hoặc giao dịch ví điện tử P2P, phân phối thời gian và hành vi gian lận có thể có sự khác biệt. Do đó, ngân hàng tiếp nhận cần tái hiệu chuẩn (Re-calibrate) các phân vị $hat(q)_0, hat(q)_1$ trên dữ liệu nội bộ trước khi áp dụng.
+ *Độ tin cậy khái niệm (Construct Validity):*
  - Các tham số trong ma trận chi phí ($c_("otp") = 0.05$ USD, $c_("fric") = 5.00$ USD, $c_("chargeback") = 15.00$ USD) được xây dựng dựa trên thông lệ trung bình của các cổng thanh toán quốc tế (Stripe, Adyen). Tuy nhiên, đối với các thị trường có chi phí SMS OTP cao hoặc tỷ lệ hủy đơn hàng lớn khi gặp thử thách xác thực, ngân hàng hoàn toàn có thể điều chỉnh lại trọng số ma trận để phù hợp với chiến lược kinh doanh cụ thể.

== 6.2. Các đánh đổi kỹ thuật và nghiệp vụ (Trade-offs)
+ *Đánh đổi giữa Trải nghiệm người dùng (Friction) và An toàn tài chính (Security):*
  - Khung đề xuất đưa $55.13\%$ giao dịch vào vùng thử thách OTP (Step-Up 2FA). Đánh đổi này cho phép hệ thống chặn đứng tới $96.13\%$ các vụ gian lận (giảm $94.54\%$ thiệt hại tài chính), nhưng đồng thời yêu cầu một tỷ lệ đáng kể khách hàng thực hiện thêm một thao tác nhập mã OTP.
  - Trong thực tế, ngân hàng có thể điều chỉnh mức ý nghĩa $alpha$ theo khẩu vị rủi ro: giảm $alpha$ (ví dụ từ $0.05$ xuống $0.01$) làm tăng độ phủ mục tiêu và mở rộng tập dự đoán, thường khiến nhiều giao dịch cần OTP hơn; tăng $alpha$ (ví dụ từ $0.05$ lên $0.10$) có thể thu hẹp vùng cần OTP nhưng làm giảm độ phủ mục tiêu. Tỷ lệ OTP thực tế cần được đo lại sau mỗi lần hiệu chỉnh.
+ *Đánh đổi giữa Bộ nhớ trong (In-Memory) và Hệ thống phân tán (Distributed Cache):*
  - Việc hiện thực bộ đệm Idempotency Cache và Rule Engine ngay trong bộ nhớ ứng dụng (In-memory) giúp đạt tốc độ siêu tốc ($< 2.0 "ms"$). Tuy nhiên, khi mở rộng quy mô hệ thống ra nhiều nút cụm (Multi-node Cluster), bộ nhớ đệm cần được đồng bộ qua các giải pháp như Redis Sentinel hoặc Dragonfly để tránh hiện tượng phân mảnh trạng thái giữa các phiên bản.

== 6.3. Những hạn chế còn tồn đọng (Limitations)
Dù đạt được những kết quả thực nghiệm vượt trội, hệ thống vẫn còn một số hạn chế nhất định cần được hoàn thiện:
+ *Khả năng đối phó với gian lận ngày số không (Zero-Day Fraud Patterns):* Các thủ đoạn gian lận hoàn toàn mới chưa từng xuất hiện trong tập hiệu chuẩn có thể khiến hàm điểm bất thường $s(x, y)$ đánh giá sai lệch trong những giờ đầu tiên trước khi hệ thống được định chuẩn lại.
+ *Mạng lưới botnet phân tán xoay vòng IP (Residential Proxy Networks):* Các cuộc tấn công brute-force hiện đại sử dụng hàng nghìn địa chỉ IP dân cư xoay vòng có thể tạm thời vượt qua tầng kiểm tra tần suất đơn lẻ theo IP nếu không kết hợp với phân tích dấu vân tay thiết bị sâu (Device Fingerprinting).





