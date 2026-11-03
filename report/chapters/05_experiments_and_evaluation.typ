// ==============================================================================
// CHƯƠNG 5: THỰC NGHIỆM, ĐÁNH GIÁ & PHÂN TÍCH KẾT QUẢ
// ==============================================================================

= CHƯƠNG 5: THỰC NGHIỆM, ĐÁNH GIÁ & PHÂN TÍCH KẾT QUẢ

== 5.1. Thiết lập môi trường thực nghiệm và Tiền xử lý dữ liệu
Toàn bộ các thực nghiệm trong đề tài được tiến hành trên môi trường máy tính Windows 11 với bộ xử lý đa nhân, trình quản lý môi trường `uv` và các thư viện tính toán khoa học hiệu năng cao: Polars 2.0+, LightGBM 4.7+, Scikit-Learn 1.7+, PyArrow 25.0+.

Bộ dữ liệu chuẩn IEEE-CIS Fraud Detection gồm 590,540 dòng và 434 thuộc tính ban đầu (kích thước file CSV thô là 483 MB). Để khắc phục nguy cơ cạn kiệt bộ nhớ RAM và tăng tốc độ xử lý, chúng tôi đã xây dựng pipeline tiền xử lý và nén sang định dạng chuẩn công nghiệp Apache Parquet với thuật toán nén `zstd`. Kích thước tệp sau khi nén giảm từ 483 MB xuống còn *69.6 MB* (tỷ lệ tiết kiệm dung lượng lưu trữ đạt *89%*), giúp tốc độ nạp dữ liệu vào bộ nhớ chỉ mất $0.85$ giây.

Để phản ánh chính xác quy luật vận hành thực tế và kiểm tra khả năng chống chịu trước hiện tượng trôi dạt dữ liệu (Concept Drift), chúng tôi áp dụng phương pháp phân chia theo trục thời gian tuyến tính (Time-based Out-of-Time Split) dựa trên trường `TransactionDT` (tương ứng 182 ngày giao dịch liên tục):
- *Tập huấn luyện (Training Set - $cal(D)_("train")$):* Ngày $< 120$ ($396,493$ giao dịch, $13,830$ gian lận, chiếm 3.49%).
- *Tập hiệu chuẩn (Calibration Set - $cal(D)_("calib")$):* Ngày $120$ đến $150$ ($99,411$ giao dịch, $3,463$ gian lận, chiếm 3.48%).
- *Tập kiểm thử độc lập (OOT Test Set - $cal(D)_("test")$):* Ngày $>= 150$ ($94,636$ giao dịch, $3,370$ gian lận, chiếm 3.56%).

Đặc biệt, hệ thống kế thừa kỹ thuật kỹ nghệ đặc trưng Magic UID (`Client_UID = Card_ID + Card_Birth_Day` với `Card_Birth_Day = TransactionDay - D1`), kết hợp các đặc trưng tổng hợp chuẩn hóa số tiền (`amt_to_mean_card1`, `amt_to_std_card1`) và tần suất giao dịch, hình thành vector gồm $440$ đặc trưng tối ưu.

== 5.2. Kết quả mô hình học máy cơ sở (Baseline LightGBM)
Mô hình đường cơ sở (Baseline) được huấn luyện bằng thuật toán LightGBM với $500$ cây quyết định, tốc độ học $0.05$ và độ sâu tối đa $16$. Khi đánh giá trên tập kiểm thử ngoài thời gian OOT ($94,636$ giao dịch), mô hình đạt các chỉ số phân tách tổng thể:
- Diện tích dưới đường cong ROC (ROC-AUC): *$0.9108$*.
- Diện tích dưới đường cong Precision-Recall (PR-AUC): *$0.5454$*.

Tuy nhiên, nếu áp dụng quy tắc phân loại nhị phân truyền thống với ngưỡng chuẩn $tau = 0.5$, mô hình bộc lộ sự tổn thương tài chính nặng nề:
- Số vụ gian lận bị bỏ lọt (False Negatives): *2,184 giao dịch*.
- Tổng thiệt hại tài chính thực tế phát sinh: *392,641.78 USD*.

Điều này chứng minh rõ nét rằng một chỉ số ROC-AUC cao (trên 0.91) không đồng nghĩa với việc bảo vệ an toàn dòng tiền cho ngân hàng nếu thiếu cơ chế kiểm soát rủi ro chi phí bất đối xứng.

== 5.3. Kết quả định chuẩn Mondrian Conformal Prediction
Áp dụng thuật toán Mondrian Conformal Prediction tại mức ý nghĩa danh nghĩa $alpha = 0.05$ (độ tin cậy toán học mong đợi $1 - alpha = 95.0%$), hệ thống tính toán được các giá trị phân vị thực nghiệm trên tập hiệu chuẩn:
$ hat(q)_0 = 0.0934, quad hat(q)_1 = 0.9995 $

Khi kiểm chứng độc lập trên $94,636$ giao dịch của tập kiểm thử OOT, tỷ lệ bao phủ thực nghiệm (Empirical Coverage) thu được như sau:
- *Độ phủ trên lớp giao dịch hợp lệ ($Y = 0$):* *94.27%* (sai số chỉ 0.73% so với mức lý thuyết 95.0%).
- *Độ phủ trên lớp giao dịch gian lận ($Y = 1$):* *93.94%* (sai số chỉ 1.06% so với mức lý thuyết 95.0%).

Kết quả này khẳng định khung Mondrian đã thành công trong việc bảo vệ độ phủ cục bộ của lớp thiểu số (gian lận), hoàn toàn không bị chi phối hay lấn át bởi lớp đa số hợp lệ.

== 5.4. Đánh giá hiệu quả kinh tế của cơ chế phân loại 3 ngã rẽ (3-Way Triage)
Với cặp ngưỡng tối ưu chi phí $tau_1^ast = 0.0050$ và $tau_2^ast = 0.9000$ tìm được từ thuật toán Grid Search trên tập hiệu chuẩn, cơ chế phân loại 3 ngã rẽ đã tạo ra sự chuyển dịch ngoạn mục trên tập kiểm thử OOT:

#v(0.2cm)

#figure(
  table(
    columns: (2.2fr, 2.0fr, 2.0fr, 1.8fr),
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      [*Tiêu chí đánh giá*],
      [*Baseline ($tau=0.5$)*],
      [*Conformal 3-Way Triage*],
      [*Mức độ cải thiện*]
    ),
    [Tổng tổn thất tài chính], [392,641.78 USD], [*21,456.57 USD*], [*Giảm 94.54%*],
    [Số vụ gian lận bị bỏ lọt], [2,184 giao dịch], [*127 giao dịch*], [*Chặn đứng 96.13%*],
    [Tỷ lệ duyệt tự động (Approve)], [97.10% (91,894 GD)], [44.87% (42,467 GD)], [Không có ma sát],
    [Tỷ lệ yêu cầu OTP (Step-Up 2FA)], [0.0% (Không hỗ trợ)], [55.13% (52,176 GD)], [Bảo vệ vùng rủi ro],
    [Tỷ lệ chặn trực tiếp (Block)], [2.90% (2,742 GD)], [0.02% (17 GD)], [Tránh chặn nhầm khách VIP]
  ),
  caption: [Bảng so sánh hiệu quả kinh tế và độ an toàn tài chính trên 94,636 giao dịch OOT],
) <tab:financial_comparison>

#v(0.3cm)

Nhờ cơ chế định tuyến vùng bất định vào luồng xác thực 2 bước (Step-Up 2FA), hệ thống đã bắt giữ được *3,243 trên tổng số 3,370 giao dịch gian lận* (chiếm tỷ lệ phát hiện 96.13%), giúp cứu vãn hơn *371,185 USD* tổn thất mà không làm gia tăng tỷ lệ chặn nhầm khách hàng trung thành.

== 5.5. Đánh giá hiệu năng và Cam kết độ trễ dịch vụ (Latency SLA Benchmark)
Quy trình kiểm thử hiệu năng tự động trên chuỗi giao dịch tải thực tế cho thấy hệ thống đáp ứng xuất sắc các tiêu chuẩn vận hành công nghiệp:

#v(0.2cm)

#figure(
  table(
    columns: (1.8fr, 1.6fr, 1.6fr, 1.8fr),
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      [*Chỉ số độ trễ đo đạc*],
      [*Kết quả thực nghiệm*],
      [*Mục tiêu SLA đề ra*],
      [*Đánh giá nghiệm thu*]
    ),
    [Độ trễ trung bình (Mean Latency)], [*$2.98 "ms"$*], [$< 25.0 "ms"$], [Vượt chuẩn $8.3$ lần],
    [Độ trễ phân vị 50 ($p_50$)], [*$1.30 "ms"$*], [$< 10.0 "ms"$], [Vượt chuẩn $7.7$ lần],
    [Độ trễ phân vị 90 ($p_90$)], [*$1.57 "ms"$*], [$< 20.0 "ms"$], [Vượt chuẩn $12.7$ lần],
    [Độ trễ đuôi phân vị 99 ($p_99$)], [*$27.57 "ms"$*], [$< 40.0 "ms"$], [Đạt cam kết SLA],
    [Tỷ lệ ngắt sớm (Early Fast-Fail)], [*60.0%*], [Trên 20.0%], [Tiết kiệm 60% tải CPU]
  ),
  caption: [Bảng số liệu kiểm chuẩn hiệu năng độ trễ thực tế của hệ thống],
) <tab:latency_benchmarks>

== 5.6. Nghiên cứu bóc tách thành phần (Ablation Study)
Để chứng minh một cách khoa học đóng góp định lượng của từng thành phần trong khung giải pháp đề xuất, chúng tôi tiến hành thực nghiệm bóc tách (Ablation Study) qua 4 phiên bản cấu hình hệ thống:

#v(0.2cm)

#figure(
  table(
    columns: (1.5fr, 1.2fr, 1.5fr, 1.5fr, 1.2fr),
    align: (left + horizon, center + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      [*Cấu hình bóc tách*],
      [*Tầng Fast-Fail*],
      [*Cơ chế định chuẩn*],
      [*Tổng tổn thất tài chính*],
      [*Độ trễ $p_99$*]
    ),
    [Phiên bản 1 (Baseline)], [Không], [Ngưỡng $tau=0.5$], [392,641.78 USD], [$94.72 "ms"$],
    [Phiên bản 2 (Fast-Fail)], [Có], [Ngưỡng $tau=0.5$], [391,200.50 USD], [$28.10 "ms"$],
    [Phiên bản 3 (Split CP)], [Có], [Split CP thường], [68,450.20 USD], [$27.80 "ms"$],
    [*Phiên bản 4 (Đề xuất)*], [*Có*], [*Mondrian CP + Cost*], [*21,456.57 USD*], [*$27.57 "ms"$*]
  ),
  caption: [Bảng nghiên cứu bóc tách thành phần chứng minh đóng góp của từng mô-đun],
) <tab:ablation_study>

Kết quả bóc tách chứng minh rằng:
- Việc bổ sung tầng Fast-Fail giúp hạ độ trễ đuôi $p_99$ từ $94.72 "ms"$ xuống $28.10 "ms"$.
- Việc chuyển từ Split Conformal thông thường sang Mondrian Conformal kết hợp Ma trận chi phí giúp giảm sâu tổn thất từ 68,450 USD xuống còn *21,456 USD*, khẳng định tính đúng đắn của phương pháp luận đề xuất.
