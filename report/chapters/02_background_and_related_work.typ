// ==============================================================================
// CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & NGHIÊN CỨU LIÊN QUAN
// ==============================================================================

= CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & NGHIÊN CỨU LIÊN QUAN

== 2.1. Bài toán phát hiện gian lận trong hệ thống thanh toán phân tán
Hệ thống xử lý giao dịch tài chính phân tán (Distributed Payment Information Systems) hoạt động dưới những ràng buộc kỹ thuật vô cùng khắt khe về thông lượng và độ trễ. Một giao dịch thẻ trực tuyến (E-commerce Checkout) khi được kích hoạt phải đi qua chuỗi quy trình xác thực bao gồm: Cổng thanh toán (Payment Gateway), Hệ thống phát hiện rủi ro (Fraud Risk Engine), Mạng lưới chuyển mạch thẻ (Card Schemes như Visa/Mastercard) và Ngân hàng phát hành (Issuing Bank).

Trong quy trình này, toàn bộ thời gian cho phép dành cho phân hệ phân tích rủi ro thường không được vượt quá $50 "ms"$ đến $100 "ms"$ để tránh gây nghẽn hàng đợi hoặc làm gián đoạn trải nghiệm thanh toán của khách hàng. Đồng thời, dữ liệu giao dịch thẻ mang ba đặc thù kỹ thuật phức tạp:
+ *Tỷ lệ mất cân bằng dữ liệu cực đoan (Extreme Class Imbalance):* Trong hầu hết các hệ thống thực tế, tỷ lệ giao dịch gian lận chỉ chiếm từ $1\%$ đến $4\%$ tổng số giao dịch. Trong bộ dữ liệu chuẩn IEEE-CIS, tỷ lệ gian lận được ghi nhận là $3.50\%$ (20,663 giao dịch gian lận trên tổng số 590,540 giao dịch).
+ *Hiện tượng trôi dạt phân phối dữ liệu (Data Drift / Concept Drift):* Hành vi tiêu dùng của khách hàng hợp lệ biến đổi theo mùa vụ, ngày lễ và chu kỳ chi tiêu. Ngược lại, tội phạm mạng liên tục thay đổi địa chỉ IP, thay đổi thiết bị và hoán đổi dải số định danh ngân hàng (BIN) nhằm né tránh các thuật toán phát hiện.
+ *Hệ quả tài chính bất đối xứng:* Sai lầm loại II (False Negative - bỏ lọt kẻ gian) gây mất mát trực tiếp số tiền hàng hóa cùng phí phạt bồi hoàn từ ngân hàng quốc tế, trong khi sai lầm loại I (False Positive - từ chối nhầm khách VIP) làm tổn thương uy tín thương hiệu và mất doanh thu tiềm năng.

== 2.2. Các hướng tiếp cận học máy truyền thống và hạn chế
Trong thập kỷ qua, các mô hình học máy dạng cây tăng cường độ dốc (Gradient Boosting Decision Trees - GBDT) như XGBoost, LightGBM và CatBoost đã trở thành tiêu chuẩn vàng trong bài toán phát hiện gian lận dạng bảng (tabular fraud detection). Nhờ khả năng xử lý xuất sắc dữ liệu thưa, tương tác đặc trưng phi tuyến tính phức tạp và tốc độ suy luận nhanh, GBDT liên tục đạt thứ hạng cao tại các cuộc thi khoa học dữ liệu quốc tế.

Tuy nhiên, các mô hình GBDT truyền thống thường xuất ra giá trị xác suất điểm $hat(p)(x) = P(Y = 1 | X = x)$. Khi đưa vào vận hành thực tế, các kỹ sư thường áp dụng một quy tắc quyết định nhị phân cứng:
$ "Quyết định"(x) = cases(
  "BLOCK (Chặn)" &"nếu " hat(p)(x) >= tau,
  "APPROVE (Duyệt)" &"nếu " hat(p)(x) < tau
) $
với ngưỡng cắt cố định $tau$ (thường mặc định là $0.5$ hoặc tinh chỉnh thủ công theo trực giác kỹ sư rủi ro). Cách tiếp cận này bộc lộ những nhược điểm cố hữu:
- Không đo lường được mức độ chắc chắn toán học của dự đoán. Hai giao dịch có xác suất $hat(p) = 0.51$ và $hat(p) = 0.99$ đều bị đối xử giống nhau là "Chặn", mặc dù giao dịch đầu tiên có độ bất định cực kỳ lớn.
- Các kỹ thuật định lượng bất định truyền thống như Mạng nơ-ron Bayes (Bayesian Neural Networks), kỹ thuật Monte Carlo Dropout hay phương pháp Ensembles thường đòi hỏi tính toán suy luận lặp lại nhiều lần ($N >= 20$ lần), làm độ trễ suy luận vượt quá $300 "ms"$, hoàn toàn bất khả thi trong môi trường thanh toán trực tuyến thời gian thực.

== 2.3. Khung lý thuyết Dự đoán Conformal (Conformal Prediction)
Lý thuyết Dự đoán Conformal (Conformal Prediction - CP) do Vladimir Vovk và các cộng sự khởi xướng là một khung toán học thống kê phi tham số (distribution-free, non-parametric framework) cho phép chuyển đổi bất kỳ mô hình học máy điểm nào thành một bộ dự đoán tập hợp (set-valued predictor) có bảo đảm toán học vững chắc trong mẫu hữu hạn (finite-sample statistical guarantee).

Giả định duy nhất của Conformal Prediction là tính khả hoán (Exchangeability) của dữ liệu: tức là phân phối xác suất đồng thời của chuỗi dữ liệu không thay đổi khi hoán vị thứ tự các quan sát.

Cho một mức ý nghĩa danh nghĩa $alpha in (0, 1)$ (thường chọn $alpha = 0.05$, tương ứng với độ tin cậy $1 - alpha = 95\%$), với mỗi mẫu mới $x_(n+1)$, bộ dự đoán Conformal sẽ xuất ra một tập hợp các nhãn khả dĩ $C(x_(n+1)) subset.eq {0, 1}$ sao cho:
$ bb(P)(Y_(n+1) in C(X_(n+1))) >= 1 - alpha $

Trong kỹ thuật Split Conformal Prediction (còn gọi là Inductive Conformal Prediction - ICP), tập dữ liệu được tách thành hai phần độc lập: tập huấn luyện (Proper Training Set $cal(D)_("train")$) dùng để huấn luyện mô hình cơ sở, và tập hiệu chuẩn (Calibration Set $cal(D)_("calib")$ kích thước $n$) dùng để tính toán hàm điểm bất thường (Nonconformity Score function $s(x, y)$).

== 2.4. Hiệu chuẩn Conformal nhóm (Mondrian Conformal Prediction)
Mặc dù Split Conformal Prediction chuẩn cung cấp độ bảo đảm bao phủ biên (Marginal Coverage), phương pháp này bộc lộ khiếm khuyết lớn trong bài toán mất cân bằng dữ liệu: nó có thể đạt độ phủ tổng thể $95\%$ bằng cách bao phủ đúng $99\%$ lớp đa số (giao dịch hợp lệ) nhưng lại để độ phủ của lớp thiểu số (giao dịch gian lận) tụt xuống dưới $70\%$.

Để khắc phục hiện tượng "bất công toán học" này, khung lý thuyết *Mondrian Conformal Prediction* phân chia không gian hiệu chuẩn thành các nhóm phân vùng điều kiện nhãn (Mondrian Categories):
$ cal(D)_("calib")^((0)) = {(x_i, y_i) in cal(D)_("calib") : y_i = 0}, \
cal(D)_("calib")^((1)) = {(x_i, y_i) in cal(D)_("calib") : y_i = 1} $

Bằng cách tính toán riêng biệt các giá trị phân vị thực nghiệm $hat(q)_0$ và $hat(q)_1$ trên từng phân vùng nhãn, Mondrian Conformal Prediction bảo đảm tính hợp lệ có điều kiện theo từng lớp (Class-conditional Coverage Guarantee):
$ bb(P)(Y_(n+1) in C(X_(n+1)) | Y_(n+1) = k) >= 1 - alpha, quad forall k in {0, 1} $

== 2.5. Tối ưu hóa chi phí bất đối xứng (Cost-Sensitive Learning)
Học máy tối ưu chi phí (Cost-Sensitive Learning) nghiên cứu việc kết hợp ma trận tổn thất tài chính vào quá trình ra quyết định. Thay vì coi mọi sai số đều có giá trị ngang nhau, lý thuyết của Charles Elkan chỉ ra rằng quyết định tối ưu phải là quyết định cực tiểu hóa kỳ vọng tổn thất tài chính (Conditional Expected Loss).

Trong đề tài này, ma trận chi phí được thiết lập dựa trên chi phí kinh doanh thực tế của nghiệp vụ thanh toán điện tử:
- Chi phí chấp thuận đúng giao dịch hợp lệ: $C("Approve", Y=0) = 0$ USD.
- Chi phí gửi mã thử thách OTP 2FA: $C("2FA", Y=0) = C("2FA", Y=1) = c_("otp")$ (xấp xỉ $0.05$ USD chi phí SMS Gateway).
- Chi phí chặn nhầm khách hàng hợp lệ (Customer Friction Cost): $C("Block", Y=0) = c_("fric")$ (khoảng $5.00$ USD).
- Chi phí bỏ lọt gian lận (Fraud Loss & Chargeback Fee): $C("Approve", Y=1) = "TransactionAmt" + c_("chargeback")$.

== 2.6. Tổng hợp các nghiên cứu liên quan và Định vị đóng góp
Bảng sau đây tổng hợp và so sánh giải pháp của khóa luận với các công trình nghiên cứu tiêu biểu trong lĩnh vực:

#v(0.2cm)

#figure(
  table(
    columns: (1.8fr, 1.3fr, 1.4fr, 1.3fr, 1.2fr),
    align: (left + horizon, center + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      [*Công trình nghiên cứu*],
      [*Mô hình cơ sở*],
      [*Định lượng bất định*],
      [*Cơ chế 3-Way Triage*],
      [*Độ trễ thời gian thực*]
    ),
    [Dal Pozzolo et al. (2015)], [Random Forest], [Không (Point $hat(p)$)], [Không (2-way)], [Trung bình],
    [Lebichot et al. (2020)], [XGBoost / DNN], [Ensemble (Chậm)], [Không (2-way)], [Kém ($>200 "ms"$)],
    [Angelopoulos et al. (2021)], [Neural Net], [Split Conformal], [Không (Chỉ xuất tập)], [N/A (Offline)],
    [Guan & Tibshirani (2022)], [Gradient Boost], [Conformal Prediction], [Không (2-way)], [N/A (Lý thuyết)],
    [*Đề tài Khóa luận này*], [*LightGBM GBDT*], [*Mondrian CP ($95\%$)*], [*Có (Cost Matrix)*], [*Siêu tốc ($<30 "ms"$)*]
  ),
  caption: [Bảng so sánh tổng quan các công trình nghiên cứu liên quan và định vị đóng góp],
) <tab:related_work>






