# ỨNG VIÊN 1: CỔNG THANH TOÁN THÔNG MINH & PHÂN LOẠI RỦI RO GIAN LẬN CONFORMAL NHẠY CẢM CHI PHÍ
> **Tên đề tài chuẩn học thuật (Scientific Title):**  
> *"An Adaptive Cost-Sensitive Conformal Calibration Framework for Real-Time Fraud Triage in Distributed Payment Information Systems"*  
> *(Khung hiệu chuẩn thích ứng Conformal nhạy cảm chi phí phục vụ phân loại rủi ro gian lận thời gian thực trong Hệ thống Thông tin Thanh toán)*  
>  
> **Lĩnh vực:** Hệ thống Thông tin Tài chính (FinTech & Payment Information Systems), An ninh Giao dịch & Học máy Ứng dụng.

---

## 1. Tóm tắt thuyết trình dễ hiểu (Synopsis / Presentation Pitch)

> *"Hãy tưởng tượng bạn đang quản lý một cổng thanh toán điện tử như VNPay hay Stripe xử lý hàng trăm nghìn giao dịch mỗi ngày. Vấn đề nan giải nhất của các hệ thống thanh toán hiện nay là: Nếu hệ thống quá lỏng lẻo, bạn bị tội phạm lừa đảo rút sạch tiền; nhưng nếu hệ thống quá gắt gao, người mua hàng chân chính bị từ chối oan ức, dẫn đến bực tức bỏ sang sàn khác. Các đồ án thông thường chỉ dừng lại ở việc gắn một mô hình AI đơn giản và đoán mò theo tỷ lệ 50/50.  
> Đề tài này giải quyết triệt để bài toán đó bằng cách: Xây dựng một cổng thanh toán tốc độ cao (phản hồi dưới 30 phần nghìn giây), kết hợp cơ chế toán học Conformal có bảo chứng độ tin cậy và bảng tính thiệt hại tiền bạc thực tế. Thay vì chỉ phán bừa 'Chặn' hoặc 'Cho qua', hệ thống tạo ra một vùng thứ ba: tự động yêu cầu xác thực OTP/Khuôn mặt đối với các giao dịch còn nghi ngờ. Mọi quyết định và mô phỏng đều bắt nguồn từ dữ liệu giao dịch thật được phân tích kỹ lưỡng, giúp doanh nghiệp vừa chặn đứng thất thoát tiền bạc, vừa giữ chân tối đa khách hàng."*

---

## 2. Bảng giải thích thuật ngữ "Bình dân học vụ" (Glossary without Buzzwords)

Bảng dưới đây giải thích toàn bộ các thuật ngữ kỹ thuật bằng ngôn ngữ đời thường, không dùng từ ngữ đao to búa lớn (buzzwords), đi kèm thuật ngữ gốc tiếng Anh:

| Thuật ngữ gốc tiếng Anh | Tên gọi tiếng Việt | Giải thích bản chất cực kỳ dễ hiểu |
| :--- | :--- | :--- |
| **Conformal Prediction** | Dự báo Conformal (Bảo chứng xác suất) | Thay vì đoán liều 1 đáp án (ví dụ: *"giao dịch này 80% là lừa đảo"*), phương pháp này đưa ra một **tập hợp các khả năng** kèm theo bảo đảm toán học: *"Tôi cam kết chắc chắn 99% trường hợp thật sẽ nằm trong tập này"*. Nếu hệ thống phân vân, nó trả về `{Hợp lệ, Gian lận}` $\rightarrow$ hệ thống biết mình chưa chắc chắn nên sẽ bắt xác thực thêm. |
| **Cost-Sensitive Learning / Asymmetric Cost Matrix** | Học nhạy cảm chi phí / Ma trận chi phí bất đối xứng | Trong kinh doanh, cái giá của 2 sai lầm là hoàn toàn khác nhau. Bỏ lọt 1 vụ lừa đảo ($FN$) làm công ty mất $500. Nhưng chặn nhầm 1 khách xịn ($FP$) công ty chỉ mất vài ngàn đồng tiền giải thích. Ma trận này dạy mô hình ưu tiên cứu tiền to, không đánh đồng mọi lỗi sai như nhau. |
| **Class Imbalance** | Mất cân bằng dữ liệu / Mất cân bằng nhãn | Tình trạng trong 100 giao dịch thì có tới 97 giao dịch của người tốt và chỉ có 2-3 giao dịch lừa đảo. Nếu một mô hình lười biếng đoán "ai cũng là người tốt", nó vẫn đúng 97% nhưng thực tế là vô dụng. Đề tài phải xử lý hiện tượng này. |
| **Concept Drift** | Trôi dạt khái niệm / Biến đổi hành vi theo thời gian | Thủ đoạn của tội phạm không bao giờ đứng yên. Tháng này chúng lừa bằng mã giảm giá, tháng sau chúng dùng mạng ảo (VPN), tháng tới chúng quẹt thẻ lúc 2h sáng. Dữ liệu cũ bị "lỗi thời" so với chiêu trò mới gọi là Concept Drift. |
| **p99 Tail Latency** | Độ trễ đuôi phân vị thứ 99 | Khi có 100 người quẹt thẻ, 99 người có tốc độ phản hồi nhanh hơn con số này. Trong thanh toán, chỉ cần 1 giao dịch bị treo 3 giây là khách hàng bấm hủy đơn. Chuẩn hệ thống phải đạt $p_{99} < 40\text{ms}$ (cực nhanh). |
| **Layered Fast-Fail Architecture** | Kiến trúc phòng thủ đa tầng "thất bại sớm" | Thay vì mọi giao dịch đều phải chờ máy học đắt đỏ tính toán, hệ thống chia thành 4 chốt gác: Chốt 1 kiểm tra định dạng rác ($1\text{ms}$), Chốt 2 chặn địa chỉ IP đen ($3\text{ms}$), Chốt 3 kiểm tra giao dịch trùng ($2\text{ms}$). Chỉ giao dịch nào vượt qua 3 chốt này mới được gửi tới mô hình AI. Giúp tiết kiệm 40% chi phí máy chủ. |
| **Idempotency** | Tính lũy đẳng (Chống quẹt thẻ trùng) | Khách hàng sốt ruột bấm nút "Thanh toán" 3 lần liên tiếp trong 1 giây. Tính năng này kiểm tra mã giao dịch duy nhất để đảm bảo tài khoản chỉ bị trừ tiền đúng 1 lần, 2 lần sau trả về kết quả cũ mà không cần tính toán lại. |
| **SHAP Values (Explainable AI)** | Giá trị giải thích nguyên nhân | "Hộp đen" AI đưa ra phán quyết, còn SHAP chỉ rõ lý do: *"Giao dịch này bị nghi ngờ vì IP từ nước ngoài (+35 điểm rủi ro), mua món hàng đắt bất thường (+40 điểm) và đổi thiết bị mới (+15 điểm)"*. Nhân viên kiểm soát nhìn vào là hiểu ngay. |

---

## 3. Tại sao thế giới thực lại cần đề tài này? (Why do we need this?)

* **Nỗi đau tài chính thực tế:** Theo báo cáo của Nilson Report, gian lận thanh toán toàn cầu gây thiệt hại hơn 35 tỷ USD mỗi năm. Các nền tảng E-commerce vừa và nhỏ liên tục bị tấn công bằng thẻ tín dụng đánh cắp (Carding attack).
* **Nỗi đau khách hàng (False Declines):** Thiệt hại từ việc **chặn nhầm khách hàng chân chính** còn lớn gấp nhiều lần gian lận. Khi người dùng bị khóa thẻ vô cớ tại bước thanh toán, hơn 40% sẽ lập tức từ bỏ giỏ hàng và không bao giờ quay lại mua sắm.
* **Hệ thống thanh toán chịu áp lực thời gian thực:** Cổng thanh toán chỉ có tối đa 100ms - 200ms để ra quyết định trước khi hệ thống ngân hàng bị timeout. Không thể dùng các mô hình cồng kềnh xử lý hàng giây.

---

## 4. Điểm đặc biệt của đề tài (Why is this special?)

Đề tài giải quyết bài toán theo hướng **công nghệ kết hợp kinh tế học**:
1. **Không đoán mò:** Áp dụng phương pháp xác suất **Conformal Prediction**, biến việc dự báo của AI từ chỗ "phán hú họa một con số" thành "phân loại rủi ro có chứng minh toán học".
2. **Cơ chế 3 ngã rẽ thông minh (3-Way Triage):**
   * *Ngã 1 (An toàn tuyệt đối):* Cho qua ngay lập tức ($< 15\text{ms}$).
   * *Ngã 2 (Rủi ro cao rõ rệt):* Chặn thẳng và gắn cờ cảnh báo.
   * *Ngã 3 (Vùng bất định / Nghi ngờ):* Không chặn khách, mà tự động gửi mã OTP xác thực 2 bước (Step-Up 2FA). Đây là cứu cánh giúp doanh nghiệp giữ lại khách hàng mà vẫn an toàn.
3. **Phòng thủ đa tầng siêu nhanh:** 3 chốt chặn đầu tiên lọc sạch rác và tấn công thô sơ, bảo vệ chốt AI cuối cùng khỏi bị quá tải.

---

## 5. Tại sao phải làm cách này mà không làm theo cách thông thường? (Why not XYZ but this?)

| Cách thông thường của các đồ án sinh viên ("MID") | Hậu quả thực tế | Cách giải quyết đột phá của đề tài này |
| :--- | :--- | :--- |
| Dùng XGBoost / Random Forest mặc định, lấy ngưỡng xác suất $0.5$ ($>50\%$ là lừa đảo). | Thất bại thảm hại! Dữ liệu chỉ có 3% gian lận, nếu chọn ngưỡng 0.5 thì mô hình gần như bỏ lọt toàn bộ tội phạm tinh vi. | **Học nhạy cảm chi phí (Cost-Sensitive Matrix):** Tự động dò tìm ngưỡng tối ưu toán học sao cho tổng thiệt hại tiền bạc là nhỏ nhất. |
| Chỉ có 2 trạng thái nhị phân: Duyệt hoặc Chặn (Binary Accept/Reject). | Chặn nhầm khách VIP thì mất doanh thu; thả lọt kẻ gian thì đền tiền. | **Phân loại Conformal 3 trạng thái:** Đưa các ca khó phân định vào vùng "Step-up OTP", biến rủi ro thành cơ hội kiểm chứng. |
| Giao dịch nào cũng tống thẳng vào mô hình AI tính toán. | Máy chủ quá tải, nghẽn mạng lúc cao điểm săn sale (Black Friday), chi phí cloud đội lên cao. | **Kiến trúc phòng thủ đa tầng (Layered Fast-Fail):** Schema Validation $\rightarrow$ Rules $\rightarrow$ Cache $\rightarrow$ Model. Cắt giảm 40% chi phí gọi mô hình. |
| Viết code kiểu script lộn xộn trong 1 file Jupyter Notebook. | Không thể mang đi tích hợp vào hệ thống thật, hội đồng đánh giá thấp kỹ năng kỹ sư phần mềm. | **Clean Architecture (Hexagonal Architecture):** Tách bạch rõ ràng giữa Nghiệp vụ (`domain`), Điều phối (`usecase`), Cơ sở dữ liệu (`adapter`) và API (`entrypoint`). |

---

## 6. Đề tài đóng góp cho lĩnh vực nào? (Field Contribution)

1. **Hệ thống Thông tin Doanh nghiệp & Thương mại điện tử (IS & E-Commerce Systems):** Đưa ra một thiết kế kiến trúc chuẩn mực cho microservice quản lý rủi ro thanh toán có thể cắm trực tiếp vào hệ thống giỏ hàng của doanh nghiệp.
2. **Khoa học Dữ liệu Ứng dụng & Ra quyết định (Data Science & Decision Support):** Chứng minh tính khả thi của việc kết hợp hàm chi phí tài chính bất đối xứng với lý thuyết kiểm chứng Conformal trên dữ liệu lớn bị trôi dạt (Concept Drift).
3. **Kỹ thuật Phần mềm Phân tán (Distributed Systems Engineering):** Cung cấp giải pháp đáp ứng cam kết chất lượng dịch vụ (SLA) về độ trễ dưới 40ms với bộ đệm lũy đẳng (Idempotency Cache) và cơ chế ngắt sớm (Fast-Fail).

---

## 7. Độ tin cậy của bộ dữ liệu (Dataset Reliability)

Đề tài sử dụng bộ dữ liệu chuẩn vàng được cả giới học thuật và công nghiệp công nhận:
* **Tên bộ dữ liệu:** **IEEE-CIS Fraud Detection Benchmark** (hợp tác giữa tập đoàn công nghệ thanh toán Vesta Corporation và Viện Kỹ sư Điện & Điện tử IEEE).
* **Nguồn kiểm chứng:** Được lưu trữ chính thức trên Kaggle và được Amazon Science đưa vào khung chuẩn đánh giá toàn cầu **FDB (Fraud Dataset Benchmark)**.
* **Quy mô:** **590.540 giao dịch thực tế** kéo dài trong 6 tháng, bao gồm 431 đặc trưng phong phú:
  * Thông tin giao dịch: Số tiền (`TransactionAmt`), mã sản phẩm (`ProductCD`), loại thẻ (`card1-card6`), địa chỉ (`addr1-addr2`), khoảng cách (`dist1-dist2`).
  * Dấu vết kỹ thuật số: Trình duyệt, hệ điều hành (`DeviceInfo`), địa chỉ email nhà mạng (`P_emaildomain`, `R_emaildomain`).
  * Dữ liệu thời gian: Dấu thời gian thực (`TransactionDT`) thể hiện rõ các chu kỳ ngày/đêm và biến động theo tuần.
* **Tính chân thực:** Đây là dữ liệu giao dịch thẻ tín dụng thật từ các cổng thanh toán của Vesta, đã được ẩn danh hóa thông tin cá nhân (PII) theo tiêu chuẩn bảo mật ngân hàng, hoàn toàn không phải dữ liệu tự chế hay suy đoán ngẫu nhiên.

---

## 8. Phương pháp chứng minh đề tài hoạt động (Proof & Evaluation)

Để đảm bảo đạt điểm xuất sắc trước hội đồng, đề tài sử dụng phương pháp luận thực nghiệm nghiêm ngặt:

1. **Phương pháp chia tập dữ liệu theo thời gian (Time-Based Train/Test Split):**
   * Huấn luyện trên 4 tháng đầu và kiểm thử trên 2 tháng cuối để kiểm chứng khả năng chịu đựng của mô hình trước chiêu trò gian lận mới (không chia ngẫu nhiên kiểu Random Split vì sẽ làm rò rỉ dữ liệu tương lai).
2. **Chỉ số đo lường tài chính & kỹ thuật:**
   * *Độ chính xác kỹ thuật:* AUROC, AUPRC (chỉ số vàng cho dữ liệu mất cân bằng), Tỷ lệ lỗi cân bằng (Equal Error Rate - EER).
   * *Độ hiệu quả tài chính:* **Chỉ số Tiết kiệm Chi phí Tài chính (Financial Cost Savings Index - FCSI)** đo đếm trực tiếp bằng số tiền USD/VND tiết kiệm được so với ngưỡng mặc định.
   * *Hiệu năng hệ thống:* Đo đạc độ trễ phân vị $p_{50}, p_{90}, p_{99}$ bằng công cụ tải kiểm thử tự động.
3. **Nghiên cứu bóc tách từng phần (Ablation Study):**
   * So sánh hệ thống khi: (1) Đầy đủ 4 tầng vs. (2) Bỏ tầng Cache vs. (3) Bỏ tầng Rule Blocking vs. (4) Bỏ cơ chế Conformal để chứng minh bằng số liệu cụ thể công dụng của từng module.

---

## 9. Kịch bản trình diễn trước Hội đồng (Live Demo Walkthrough)

Buổi bảo vệ sẽ diễn ra như một buổi giới thiệu sản phẩm công nghệ hoàn chỉnh với 2 màn hình song song:

```
+-------------------------------------------------------+-------------------------------------------------------+
|            MÀN HÌNH 1: CỔNG THANH TOÁN (CLIENT)       |            MÀN HÌNH 2: BẢNG GIÁM SÁT RỦI RO (ADMIN)   |
+-------------------------------------------------------+-------------------------------------------------------+
|  [Giả lập Khách mua hàng quẹt thẻ trên Web/Mobile]    |  [Telemetry Thời Gian Thực - Real-Time Dashboard]     |
|                                                       |                                                       |
|  * Giao dịch #1042: $45.00 -> Đạt [DUYỆT NGAY (8ms)]  |  - Tốc độ xử lý: 320 requests/sec                     |
|  * Giao dịch #1043: $890.00 từ IP lạ                  |  - Độ trễ p99: 24.3ms                                 |
|    -> Vùng bất định [YÊU CẦU MÃ OTP XÁC THỰC]         |  - Tỷ lệ duyệt tự động: 89.2%                         |
|  * Giao dịch #1044: Bị thẻ đánh cắp                   |  - Tỷ lệ chuyển sang 2FA OTP: 8.5%                    |
|    -> [CHẶN TỨC THÌ (18ms)]                           |  - Tỷ lệ chặn gian lận: 2.3%                          |
|                                                       |  - Biểu đồ SHAP: "Lý do chặn: IP Proxy + Số tiền lệch"|
+-------------------------------------------------------+-------------------------------------------------------+
```

1. **Khách hàng giả lập gửi thanh toán:** Nhấn nút quẹt thẻ với các tình huống khác nhau.
2. **Phản hồi tức thì:** Giao dịch an toàn được duyệt ngay trong nháy mắt. Giao dịch nghi vấn lập tức hiện popup bắt nhập mã OTP trên màn hình khách. Giao dịch gian lận bị từ chối kèm mã lỗi chi tiết.
3. **Bảng điều khiển Admin nhảy số trực tiếp:** Hội đồng nhìn thấy số liệu độ trễ, lưu lượng giao dịch và nguyên nhân giải thích vì sao giao dịch đó bị nghi ngờ.

---

## 10. Cơ chế mô phỏng: Dữ liệu thật từ EDA hay suy đoán? (Simulation Authenticity)

> **Khẳng định đanh thép:**  
> **CƠ CHẾ MÔ PHỎNG HOÀN TOÀN DỰA TRÊN QUY LUẬT DỮ LIỆU THỰC TẾ TRÍCH XUẤT TỪ QUÁ TRÌNH EDA (EXPLORATORY DATA ANALYSIS), TUYỆT ĐỐI KHÔNG PHẢI SUY ĐOÁN MÒ.**

Cụ thể, luồng dữ liệu giả lập được xây dựng bằng cách:
1. **Phân phối thời gian thực tế (Inter-arrival Time Distribution):** Phân tích nhịp độ giao dịch theo thời gian trong ngày từ tập IEEE-CIS (giờ cao điểm ban ngày có lưu lượng gấp 6 lần ban đêm) và mô phỏng luồng request theo phân phối Poisson khớp với thực tế.
2. **Hành vi gian lận trích xuất từ dữ liệu:**
   * Tỷ lệ gian lận trong luồng giả lập được neo đúng theo tỷ lệ thực tế $3,5\%$.
   * Các mẫu gian lận được trích từ chính các cụm dữ liệu vi phạm thật: số tiền giao dịch bất thường (outliers), địa chỉ email từ các tên miền lạ (`mail.com`, `protonmail`), hoặc sự thay đổi thông tin thiết bị (`DeviceInfo`) chỉ trong vài phút.
3. **Môi trường thử nghiệm chân thực:** Trình phát giao dịch (Transaction Replayer) đọc trực tiếp từ tập dữ liệu kiểm thử (Test set) chưa từng được huấn luyện để bắn request qua cổng API HTTP/JSON thật, đảm bảo đo đạc trung thực độ trễ mạng và hiệu năng CPU/RAM.
