// ==============================================================================
// CHƯƠNG 1: GIỚI THIỆU & TỔNG QUAN ĐỀ TÀI
// ==============================================================================

= CHƯƠNG 1: GIỚI THIỆU & TỔNG QUAN ĐỀ TÀI

== 1.1. Bối cảnh nghiên cứu và Động lực thực tiễn
Sự phát triển vũ bão của thương mại điện tử (e-commerce) và các dịch vụ tài chính số (Fintech) đã thúc đẩy khối lượng giao dịch thanh toán không tiền mặt trên toàn cầu tăng trưởng theo cấp số nhân. Tuy nhiên, đi đôi với sự thuận tiện là sự gia tăng đột biến của các hành vi gian lận thanh toán trực tuyến (card-not-present fraud). Theo báo cáo thường niên của Ủy ban Thương mại Liên bang Hoa Kỳ (FTC) và tổ chức Nilson Report, thiệt hại tài chính do tội phạm gian lận thanh toán gây ra đã vượt ngưỡng 35 tỷ USD mỗi năm và tiếp tục diễn biến phức tạp với nhiều thủ đoạn tinh vi.

Trong các hệ thống thông tin ngân hàng truyền thống, việc phát hiện gian lận chủ yếu dựa trên các tập luật tĩnh (rule-based expert systems) như giới hạn số tiền tối đa, kiểm tra vị trí địa lý hoặc danh sách đen (blacklist). Khi mạng lưới gian lận biến chuyển sang các cuộc tấn công tự động hóa sử dụng botnet và danh tính tổng hợp (synthetic identity), hệ thống chuyên gia bộc lộ sự chậm chạp, đòi hỏi chi phí nhân sự duy trì khổng lồ và không thể thích ứng kịp thời với các biến thể gian lận mới.

Nhằm giải quyết bài toán trên, các mô hình học máy (Machine Learning - ML) hiện đại như Gradient Boosting (LightGBM, XGBoost) và Mạng nơ-ron sâu (Deep Neural Networks) đã được tích hợp rộng rãi vào các cổng thanh toán. Dẫu vậy, việc triển khai học máy trong môi trường công nghiệp thực tế đang đối mặt với hai rào cản cốt lõi:
+ *Sự thiếu vắng độ bảo đảm toán học về độ bất định (Uncertainty Quantification):* Hầu hết các bộ phân loại nhị phân truyền thống chỉ đưa ra xác suất điểm đơn lẻ $hat(p) in [0, 1]$. Đối với các giao dịch nằm trong vùng ranh giới quyết định (ví dụ $hat(p) approx 0.48$ hoặc $0.52$), mô hình không thể phản ánh mức độ tự tin toán học của dự đoán. Việc cưỡng ép đưa ra quyết định nhị phân cứng nhắc (Duyệt hoặc Chặn) thường dẫn đến hai thái cực sai lầm tai hại: hoặc bỏ lọt gian lận (False Negative) gây thất thoát hàng nghìn USD, hoặc chặn nhầm khách hàng trung thành (False Positive) làm suy giảm nghiêm trọng uy tín thương hiệu.
+ *Tính bất đối xứng về chi phí tài chính (Asymmetric Financial Cost):* Trong nghiệp vụ thanh toán, giá trị thiệt hại khi để lọt một giao dịch gian lận (mất toàn bộ giá trị giao dịch $"TransactionAmt"$ cộng phí phạt bồi hoàn chargeback) lớn hơn rất nhiều so với chi phí phát sinh khi gửi một thử thách xác thực hai yếu tố (Step-Up 2FA/OTP, xấp xỉ 0.05 USD). Các mô hình tối ưu theo hàm mất mát độ chính xác thuần túy (như Log-loss hay ROC-AUC) không thể tối ưu hóa trực tiếp dòng tiền thiệt hại thực tế của ngân hàng.

== 1.2. Mục tiêu nghiên cứu và Câu hỏi nghiên cứu (Research Questions)
Đề tài khóa luận tập trung nghiên cứu và hiện thực hóa một khung định chuẩn thích ứng dựa trên lý thuyết Dự đoán Conformal (Conformal Prediction) kết hợp ma trận chi phí bất đối xứng để xây dựng cơ chế phân loại rủi ro 3 ngã rẽ (3-Way Triage) trong hệ thống thông tin thanh toán phân tán.

Khóa luận được dẫn dắt bởi ba câu hỏi nghiên cứu khoa học chính:
- *$"RQ"_1$ (Về tính bảo đảm toán học):* Làm thế nào để mở rộng khung lý thuyết Mondrian Split Conformal Prediction nhằm cung cấp các tập nhãn dự đoán có bảo đảm độ phủ toán học nghiêm ngặt ($1 - alpha$) đối với bài toán gian lận có độ mất cân bằng lớp cực đoan (imbalanced fraud data)?
- *$"RQ"_2$ (Về tính tối ưu chi phí tài chính):* Làm thế nào để thiết lập một ma trận chi phí bất đối xứng nhằm tối ưu hóa các ngưỡng quyết định 3 ngã rẽ (Duyệt tự động - Thử thách OTP 2FA - Chặn đứng), giúp cực tiểu hóa tổng tổn thất tài chính thực tế so với các mô hình ngưỡng nhị phân truyền thống?
- *$"RQ"_3$ (Về hiệu năng thời gian thực trong kiến trúc phần mềm):* Làm thế nào để thiết kế một kiến trúc phần mềm phòng thủ nhiều tầng (Fast-Fail Architecture) đạt cam kết chất lượng dịch vụ (SLA) với độ trễ đuôi $p_99 < 40 "ms"$ khi phục vụ hàng triệu giao dịch thời gian thực?

== 1.3. Đối tượng và Phạm vi nghiên cứu
- *Đối tượng nghiên cứu:* Các phương pháp định chuẩn bất định toán học phi tham số (Non-parametric Conformal Prediction), kỹ thuật hiệu chuẩn nhóm Mondrian (Mondrian Calibration), ma trận chi phí tối ưu trong học máy tài chính và kiến trúc phần mềm phân tán chịu tải cao (High-throughput Clean Architecture).
- *Dữ liệu thực nghiệm:* Bộ dữ liệu chuẩn quốc tế *IEEE-CIS Fraud Detection Benchmark* do tập đoàn thanh toán Vesta và Hiệp hội Trí tuệ Tính toán IEEE đồng bảo trợ, bao gồm 590,540 giao dịch thẻ tín dụng trực tuyến trong thế giới thực với 434 thuộc tính kỹ thuật.
- *Phạm vi kỹ thuật:* Khóa luận giới hạn phạm vi trong quy trình xử lý giao dịch thanh toán trực tuyến (Card-Not-Present Checkout), tập trung vào khâu phân luồng rủi ro trước khi ủy quyền giao dịch (Pre-authorization Triage Engine).

== 1.4. Đóng góp khoa học và Ý nghĩa thực tiễn của khóa luận
Khóa luận mang lại những đóng góp nổi bật về cả mặt học thuật lẫn kỹ thuật ứng dụng:
+ *Về mặt học thuật:* Đề xuất quy trình tích hợp giữa Mondrian Split Conformal Prediction và giải thuật tối ưu ma trận chi phí trên tập hiệu chuẩn (Calibration Set) độc lập theo trục thời gian (Time-based Out-of-Time). Chứng minh bằng toán học và thực nghiệm khả năng kiểm soát tỷ lệ lỗi cục bộ theo từng lớp nhãn.
+ *Về mặt thực tiễn định lượng:* Đạt mức giảm thiểu *94.54%* tổn thất tài chính thực tế trên 94,636 giao dịch kiểm thử ngoài thời gian (giảm từ 392,641.78 USD xuống còn 21,456.57 USD), chặn đứng *96.13%* số vụ gian lận so với mô hình baseline nhị phân thông thường.
+ *Về mặt kiến trúc kỹ thuật:* Hiện thực hóa hoàn chỉnh hệ sinh thái phần mềm theo chuẩn Clean Architecture gồm 4 tầng phòng thủ (Schema $->$ Rules $->$ Cache $->$ Conformal ML), đạt độ trễ $p_99 = 27.57 "ms"$, kèm bảng điều khiển trực quan hai phân hệ (Dual-View Dashboard) phục vụ giám sát rủi ro ngân hàng thời gian thực.

== 1.5. Cấu trúc tổng thể của Khóa luận
Nội dung khóa luận được tổ chức thành 7 chương mạch lạc:
- *Chương 1: Giới thiệu & Tổng quan đề tài* – Trình bày bối cảnh, động lực, câu hỏi nghiên cứu và đóng góp.
- *Chương 2: Cơ sở lý thuyết & Nghiên cứu liên quan* – Phân tích tổng quan lý thuyết dự đoán Conformal, học máy phân loại gian lận và ma trận chi phí.
- *Chương 3: Phương pháp luận & Khung giải pháp đề xuất* – Trình bày chi tiết toán học của Mondrian Conformal Prediction và cơ chế 3-way triage.
- *Chương 4: Thiết kế kiến trúc & Hiện thực hệ thống* – Mô tả kiến trúc 4 tầng Fast-Fail, kỹ thuật tối ưu tạo đặc trưng $1$-row dưới 2ms và API FastAPI.
- *Chương 5: Thực nghiệm, Đánh giá & Phân tích kết quả* – Báo cáo chi tiết các số liệu đo lường OOT, phân tích ablation study và kiểm định SLA.
- *Chương 6: Thảo luận, Đánh giá độ tin cậy & Hạn chế* – Thảo luận về các mối đe dọa giá trị nghiên cứu (Validity Threats) và đánh đổi kỹ thuật.
- *Chương 7: Kết luận & Hướng phát triển* – Trả lời tường minh các câu hỏi nghiên cứu và định hướng các nghiên cứu tiếp theo.






