// ==============================================================================
// CHƯƠNG 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN
// ==============================================================================

= CHƯƠNG 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN

== 7.1. Trả lời tường minh các câu hỏi nghiên cứu
Dựa trên nền tảng lý thuyết vững chắc và toàn bộ chuỗi thực nghiệm định lượng trên 590,540 giao dịch thực tế, khóa luận xin đưa ra câu trả lời trực tiếp cho ba câu hỏi nghiên cứu khoa học đã đặt ra ở Chương 1:

+ *Trả lời $"RQ"_1$ (Về bảo đảm độ phủ toán học trong dữ liệu mất cân bằng):*
  - Khóa luận đã chứng minh rằng việc áp dụng kỹ thuật Mondrian Split Conformal Prediction cho phép phân hoạch không gian hiệu chuẩn theo từng lớp nhãn riêng biệt, qua đó tính toán độc lập các giá trị phân vị thực nghiệm $hat(q)_0 = 0.0934$ và $hat(q)_1 = 0.9995$.
  - Trên tập kiểm thử ngoài thời gian OOT gồm $94,636$ giao dịch, mô hình đạt độ phủ thực nghiệm $94.27\%$ trên lớp hợp lệ và $93.94\%$ trên lớp gian lận, thỏa mãn nghiêm ngặt bảo đảm toán học lý thuyết ($1 - alpha = 95.0\%$) mà không hề bị hiện tượng mất cân bằng dữ liệu làm suy giảm chất lượng.
+ *Trả lời $"RQ"_2$ (Về tối ưu hóa chi phí tài chính qua cơ chế 3 ngã rẽ):*
  - Bằng việc tích hợp ma trận chi phí bất đối xứng phản ánh đúng nghiệp vụ kinh doanh thẻ, thuật toán tìm kiếm lưới trên tập hiệu chuẩn đã xác định được cặp ngưỡng tối ưu toán học $(tau_1^* = 0.0050, tau_2^* = 0.9000)$.
  - So với cách tiếp cận nhị phân truyền thống ($tau = 0.5$), khung giải pháp đề xuất đã cắt giảm tổng thiệt hại tài chính từ $392,641.78$ USD xuống còn *$21,456.57$ USD* (đạt mức giảm *$94.54\%$*, tiết kiệm được *$371,185.21$ USD*), đồng thời chặn đứng *$96.13\%$* số vụ gian lận nhờ cơ chế định tuyến vùng bất định vào luồng thử thách xác thực 2 bước (Step-Up 2FA).
+ *Trả lời $"RQ"_3$ (Về kiến trúc phần mềm và hiệu năng thời gian thực):*
  - Khóa luận đã hiện thực hóa thành công kiến trúc phòng thủ 4 tầng Fast-Fail (Schema $->$ Rules $->$ Cache $->$ Conformal ML) tuân thủ triệt để nguyên lý Clean Architecture.
  - Kết hợp với kỹ thuật tối ưu hóa tạo hàng dữ liệu đặc trưng $1$-row dưới $2.2 "ms"$, toàn bộ hệ thống đạt độ trễ đuôi $p_99 = *27.57 "ms"*$ (vượt xa cam kết SLA $< 40 "ms"$), đồng thời tầng phòng thủ sớm đã ngắt lọc thành công *$60.0\%$* các yêu cầu vi phạm hoặc trùng lặp trước khi chạm vào mô hình học máy.

== 7.2. Tóm tắt các đóng góp chính của đề tài
Tựu trung lại, công trình khóa luận đã đóng góp cho chuyên ngành Hệ thống Thông tin các giá trị cốt lõi:
- *Đóng góp phương pháp luận:* Cầu nối vững chắc giữa lý thuyết xác suất thống kê hiện đại (Conformal Prediction) và bài toán kinh tế học máy ứng dụng (Cost-Sensitive Learning).
- *Đóng góp thực tiễn:* Một hệ thống phần mềm hoàn chỉnh từ đường ống dữ liệu (EDA, Parquet 89% nén), dịch vụ API FastAPI hiệu năng cao, cho tới bảng điều khiển viễn trắc rủi ro hai phân hệ (Dual-View Dashboard) sẵn sàng ứng dụng trong thực tế.
- *Tính minh bạch & Khả năng tái lập (Reproducibility):* Toàn bộ mã nguồn, dữ liệu hiệu chuẩn, kịch bản kiểm thử tự động và nhật ký thực nghiệm đều được tổ chức khoa học, phiên bản hóa chặt chẽ và lưu trữ minh bạch.

== 7.3. Định hướng nghiên cứu và Phát triển trong tương lai
Trong các giai đoạn tiếp theo, nghiên cứu có thể được mở rộng theo các hướng triển vọng:
+ *Định chuẩn Conformal động trực tuyến (Online Adaptive Conformal Prediction):* Ứng dụng kỹ thuật cửa sổ trượt (Rolling Calibration Window) để tự động cập nhật các phân vị $hat(q)_0, hat(q)_1$ theo từng giờ, giúp hệ thống thích ứng tức thì với các đợt bùng phát gian lận mới mà không cần huấn luyện lại toàn bộ mô hình.
+ *Thay thế mã OTP bằng Xác thực Sinh trắc học Không ma sát (FIDO2 / WebAuthn):* Tích hợp công nghệ khóa bảo mật Passkey sinh trắc học (vân tay, khuôn mặt FaceID) nhằm triệt tiêu hoàn toàn chi phí viễn thông SMS OTP ($c_("otp")$) và loại bỏ hoàn toàn ma sát trải nghiệm của khách hàng.
+ *Học máy trên đồ thị (Graph Neural Networks - GNN):* Mở rộng không gian đặc trưng bằng các liên kết đồ thị giao dịch để phát hiện các đường dây gian lận có tổ chức sử dụng nhiều thẻ và thiết bị liên kết với nhau.






