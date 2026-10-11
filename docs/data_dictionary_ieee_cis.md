# TỪ ĐIỂN DỮ LIỆU & HƯỚNG DẪN GIẢI MÃ BỘ DỮ LIỆU IEEE-CIS FRAUD DETECTION
> **Tài liệu tham khảo kỹ thuật chính thức**  
> **Dự án:** Khóa luận Tốt nghiệp - Cổng thanh toán phân loại rủi ro Conformal (FinTech IS)  
> **Mã nguồn dữ liệu:** IEEE Computational Intelligence Society & Vesta Corporation  

---

## 1. NGUỒN GỐC, TÁC GIẢ VÀ CÔNG BỐ HỌC THUẬT

### 1.1. Tác giả & Đơn vị chủ trì
* **Đơn vị cung cấp dữ liệu:** **Tập đoàn Vesta (Vesta Corporation)** — Doanh nghiệp tiên phong hàng đầu thế giới trong lĩnh vực phòng chống gian lận thương mại điện tử và giải pháp thanh toán số (thành lập năm 1995, trụ sở tại Lake Oswego, Oregon, Hoa Kỳ).
* **Đơn vị đồng tổ chức khoa học:** **IEEE Computational Intelligence Society (IEEE-CIS)** — Hội Trí tuệ Tính toán thuộc Viện Các Kỹ sư Điện & Điện tử Toàn cầu (IEEE).

### 1.2. Thời gian công bố & Nguồn gốc dữ liệu
* **Thời gian công bố:** Tháng 07/2019 (Diễn ra từ 15/07/2019 đến 01/10/2019).
* **Bản chất dữ liệu:** Toàn bộ dữ liệu được trích xuất từ lưu lượng giao dịch thương mại điện tử thực tế trên hệ thống cổng thanh toán toàn cầu của Vesta trong khoảng thời gian 6 tháng (từ tháng 12/2017 đến tháng 05/2018).
* **Hiện trạng sử dụng:** Đến năm 2024–2026, đây vẫn là bộ dữ liệu chuẩn vàng (Gold Standard Benchmark) được sử dụng rộng rãi nhất trên thế giới để nghiên cứu phát hiện gian lận và được Amazon Science tích hợp làm bộ chuẩn đầu tiên trong thư viện **Fraud Dataset Benchmark (FDB)**.

### 1.3. Trích dẫn học thuật & Liên kết chính thức
* **Kaggle Official Challenge:** [IEEE-CIS Fraud Detection Competition](https://www.kaggle.com/competitions/ieee-fraud-detection)
* **Hugging Face Public Mirror:** [aliceczr/ieee-fraud-detection](https://huggingface.co/datasets/aliceczr/ieee-fraud-detection)
* **Amazon Science Benchmark Repo:** [amazon-science/fraud-dataset-benchmark](https://github.com/amazon-science/fraud-dataset-benchmark)
* **Trích dẫn chuẩn IEEE/APA:**
  ```bibtex
  @misc{vesta_ieeecis_2019,
    author       = {Vesta Corporation and IEEE Computational Intelligence Society},
    title        = {IEEE-CIS Fraud Detection: Benchmarking Machine Learning Models on Real-world E-Commerce Fraud Data},
    year         = {2019},
    howpublished = {Kaggle Competition},
    url          = {https://www.kaggle.com/competitions/ieee-fraud-detection}
  }
  ```

---

## 2. TẠI SAO CÁC CỘT LẠI CÓ TÊN KỲ LẠ (C1-C14, D1-D15, M1-M9, V1-V339)?

Trong ngành tài chính và thẻ tín dụng, quy chuẩn bảo mật quốc tế **PCI-DSS** và luật bảo vệ dữ liệu **GDPR** nghiêm cấm các công ty thanh toán công khai dữ liệu cá nhân (PII) như họ tên khách, số thẻ đầy đủ hay địa chỉ chi tiết. Đồng thời, Vesta cần bảo vệ bí mật công nghệ phòng thủ độc quyền của họ. Do đó, các kỹ sư Vesta đã mã hóa các đặc trưng thành các nhóm chữ cái đại diện:

### 2.1. Cột C1 đến C14: "Counting Features" (Đặc trưng đếm số lượng)
* **Bản chất:** Là các trường số nguyên đo lường **tần suất và số lượng liên kết** trong một cửa sổ thời gian.
* **Ý nghĩa thực tế được giải mã:**
  * Thẻ này liên kết với bao nhiêu địa chỉ IP trong 30 ngày qua?
  * Thẻ này được dùng với bao nhiêu địa chỉ nhận hàng (Shipping Address) khác nhau?
  * Khách hàng đã thực hiện bao nhiêu giao dịch trong vòng 1 giờ, 24 giờ, 7 ngày qua?
  * Bao nhiêu thẻ tín dụng khác nhau đã từng được sử dụng từ cùng một thiết bị này?
* **Dấu hiệu gian lận:** Kẻ gian thường thử nhiều thẻ bị đánh cắp trên cùng 1 máy hoặc dùng 1 thẻ quẹt liên tục tại nhiều địa chỉ khác nhau $\rightarrow$ các chỉ số `C` tăng đột biến.

### 2.2. Cột D1 đến D15: "Timedeltas" (Khoảng cách thời gian)
* **Bản chất:** Là các số thực đo lường **khoảng thời gian (tính bằng số ngày)** giữa các sự kiện.
* **Ý nghĩa thực tế được giải mã:**
  * `D1`: Số ngày kể từ khi chiếc thẻ tín dụng này xuất hiện lần đầu tiên trong hệ thống Vesta.
  * `D2`: Số ngày kể từ giao dịch gần nhất trước đó của chiếc thẻ này.
  * `D3`: Số ngày kể từ khi thông tin người dùng (địa chỉ/email) được cập nhật lần cuối.
  * `D10`, `D15`: Khoảng thời gian gắn liền với tài khoản dịch vụ hoặc lịch sử thiết bị.
* **Dấu hiệu gian lận:** Thẻ mới tinh xuất hiện lần đầu (`D1 = 0`) nhưng lập tức quẹt số tiền cực lớn; hoặc khoảng cách giữa 2 giao dịch quá ngắn (`D2 = 0.001` ngày) ở 2 địa điểm cách xa nhau.

### 2.3. Cột M1 đến M9: "Match Features" (Độ trùng khớp thông tin)
* **Bản chất:** Là các biến phân loại nhị phân (gồm các giá trị: `T` - True, `F` - False, hoặc `Missing`).
* **Ý nghĩa thực tế được giải mã:**
  * Tên chủ thẻ có trùng khớp với tên người nhận hàng không?
  * Địa chỉ thanh toán trên hóa đơn (Billing Address) có trùng với địa chỉ giao hàng (Shipping Address) không?
  * Tên miền email (`P_emaildomain`) có khớp với ngân hàng phát hành thẻ không?
* **Dấu hiệu gian lận:** Kẻ trộm thẻ mua hàng online thường giao hàng về nhà riêng hoặc địa chỉ "ma", dẫn đến địa chỉ thanh toán và địa chỉ giao hàng không khớp nhau (`M = F`).

### 2.4. Cột V1 đến V339: "Vesta Engineered Rich Features" (Đặc trưng nội bộ của Vesta)
* **Bản chất:** 339 cột số thực là kết quả từ các mô hình học máy và hệ thống chấm điểm rủi ro có sẵn của Vesta trước khi cung cấp dữ liệu cho cuộc thi.
* **Nội dung bao gồm:**
  * Tỷ lệ số tiền giao dịch so với hạn mức trung bình của nhóm thẻ tương tự.
  * Số lần giao dịch bị từ chối trước đó do sai mã CVV hoặc sai ngày hết hạn thẻ.
  * Mức độ uy tín của dải mạng IP (IP reputation score).

---

## 3. TẠI SAO KHÔNG CÓ CỘT `userID`? LÀM SAO ĐỂ PHÂN BIỆT TỪNG KHÁCH HÀNG RIÊNG BIỆT?

Đây là câu hỏi xuất sắc nhất mà bất kỳ chuyên gia Hệ thống Thông tin nào cũng phải đối mặt:

### 3.1. Bản chất trong thế giới thực của Cổng thanh toán
Trong các cổng thanh toán quốc tế (như Vesta, Stripe, PayPal Guest Checkout), người mua hàng online **không bắt buộc phải tạo tài khoản đăng nhập**. Người dùng có thể mua hàng dưới dạng Khách vãng lai (Guest). Hơn nữa, kẻ gian lừa đảo sẽ liên tục đổi tên giả, đổi số điện thoại và đổi email giả mạo. Vì vậy: **Không thể tồn tại một cột `userID` duy nhất có sẵn!**

### 3.2. Bí quyết tạo "UID Ma thuật" (Magic Feature Engineering UID)
Để phân biệt từng khách hàng hoặc từng chiếc thẻ thực tế, các chuyên gia hàng đầu (dẫn đầu bởi Grandmaster Chris Deotte) đã phát minh ra kỹ thuật ghép khóa tổng hợp (Composite Key):

1. **Nhận diện Thẻ Tín Dụng Duy Nhất (`Card_ID`):**
   Một chiếc thẻ vật lý được định danh duy nhất bởi các trường:
   ```text
   Card_ID = card1 + card2 + card3 + card4 + card6 + addr1
   ```
   * `card1`: Mã định danh ngân hàng và dải phát hành (Bank Identification Number).
   * `card2`: Ngân hàng phát hành (Issuer Bank).
   * `card3`: Quốc gia phát hành.
   * `card4`: Tổ chức thẻ (Visa, Mastercard, Discover, Amex).
   * `card6`: Loại thẻ (Debit, Credit).
   * `addr1`: Mã bưu chính khu vực thanh toán của chủ thẻ.

2. **Dò Tìm "Ngày Sinh Của Thẻ" để phân biệt Chủ Thẻ (`Client_UID`):**
   * Trong tập dữ liệu, `TransactionDT` là thời gian giao dịch (tính bằng giây). Đổi ra ngày:
     $$\text{Day} = \frac{\text{TransactionDT}}{86400}$$
   * Cột `D1` biểu thị: *"Đã bao nhiêu ngày kể từ khi chiếc thẻ này thực hiện giao dịch đầu tiên"*.
   * Vì vậy, ngày chiếc thẻ này "ra đời" (Card Birth Day) là một hằng số bất biến:
     $$\text{Card\_Birth\_Day} = \text{Day} - \text{D1}$$
   * **Công thức tạo ID khách hàng duy nhất:**
     $$\mathbf{Client\_UID} = \mathbf{Card\_ID} + \mathbf{Card\_Birth\_Day}$$
   * **Hiệu quả:** Dù kẻ gian có đổi email hay đổi thiết bị, chỉ cần chiếc thẻ đó quẹt ở bất cứ đâu, hệ thống sẽ gom tất cả các giao dịch đó về cùng một `Client_UID` duy nhất để phát hiện hành vi rút tiền lặp lại!

---

## 4. BẢNG TỔNG HỢP KIỂU DỮ LIỆU & Ý NGHĨA TOÀN BỘ CÁC CỘT CỐT LÕI

| Tên nhóm cột | Số lượng cột | Kiểu dữ liệu | Ý nghĩa nghiệp vụ | Cách xử lý trong mô hình |
| :--- | :--- | :--- | :--- | :--- |
| **TransactionID** | 1 | Integer | Mã định danh duy nhất của mỗi giao dịch | Khóa chính (Primary Key), dùng nối bảng |
| **isFraud** | 1 | Binary (0, 1) | Nhãn mục tiêu: 1 là gian lận, 0 là hợp lệ | Biến phụ thuộc cần dự báo ($y$) |
| **TransactionDT** | 1 | Integer | Dấu thời gian (giây tính từ mốc ban đầu) | Dùng chia tập train/test theo trục thời gian |
| **TransactionAmt** | 1 | Float | Số tiền thanh toán (tính bằng USD) | Chuẩn hóa Log, tính tỷ lệ số tiền bất thường |
| **ProductCD** | 1 | Categorical | Mã nhóm sản phẩm (W, C, R, H, S) | One-hot encoding / Target encoding |
| **card1 - card6** | 6 | Mix (Int, Cat) | Thuộc tính thẻ tín dụng (loại thẻ, ngân hàng) | Tạo khóa nhận diện `Card_ID` |
| **addr1, addr2** | 2 | Float / Cat | Địa chỉ thanh toán (Mã bưu chính & Quốc gia) | Phân cụm địa lý, tính khoảng cách |
| **dist1, dist2** | 2 | Float | Khoảng cách địa lý (khoảng cách giao hàng/IP) | Phát hiện giao dịch xuyên biên giới |
| **P_/R_emaildomain**| 2 | Categorical | Tên miền email người mua & người nhận | Tách đuôi email (gmail.com, protonmail,...) |
| **C1 - C14** | 14 | Float / Int | Đếm tần suất quẹt thẻ/liên kết IP | Đặc trưng số, chuẩn hóa và tính độ biến thiên |
| **D1 - D15** | 15 | Float | Khoảng cách ngày giữa các sự kiện | Dò tìm "ngày sinh thẻ", phát hiện bất thường |
| **M1 - M9** | 9 | Categorical | So khớp trùng tên, trùng địa chỉ thanh toán | Mã hóa nhị phân (T/F $\rightarrow$ 1/0/Missing) |
| **V1 - V339** | 339 | Float | Điểm rủi ro và đặc trưng kỹ nghệ của Vesta | Giảm chiều (PCA) hoặc lọc tương quan cao |
| **id_01 - id_38** | 38 | Mix (Float, Cat)| Thông tin danh tính mạng, Proxy, Trình duyệt | Phát hiện IP giả mạo, thiết bị jailbreak |
| **DeviceType** | 1 | Categorical | Loại thiết bị: `mobile` hoặc `desktop` | Đánh giá mức độ rủi ro theo loại thiết bị |
| **DeviceInfo** | 1 | Categorical | Tên thiết bị (ví dụ: Windows, iOS, SM-G9650) | Trích xuất hệ điều hành và nhãn hiệu máy |

---

## 5. HƯỚNG DẪN CÁCH ĐỌC & TỐI ƯU HÓA BỘ DỮ LIỆU HIỆU QUẢ

1. **Bộ dữ liệu rất lớn:** File `train_transaction.csv` nặng ~683 MB và chứa gần 600.000 dòng $\times$ 394 cột. Nếu đọc bằng `pandas.read_csv()` thông thường sẽ tốn hơn 2.5 GB RAM.
2. **Giải pháp tối ưu hóa:**
   * Sử dụng thư viện **Polars** hoặc ép kiểu dữ liệu thông minh (`downcast`: `float64` $\rightarrow$ `float32`, `int64` $\rightarrow$ `int32/int16`).
   * Chuyển đổi dữ liệu sang định dạng **Apache Parquet**: giảm kích thước lưu trữ xuống chỉ còn ~90 MB và tăng tốc độ đọc lên gấp 10 lần.
   * Nối bảng `train_transaction` và `train_identity` thông qua khóa `TransactionID` bằng phép nối `left join`.
