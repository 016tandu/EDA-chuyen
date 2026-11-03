// ==============================================================================
// CHƯƠNG 3: PHƯƠNG PHÁP LUẬN & KHUNG GIẢI PHÁP ĐỀ XUẤT
// ==============================================================================

= CHƯƠNG 3: PHƯƠNG PHÁP LUẬN & KHUNG GIẢI PHÁP ĐỀ XUẤT

== 3.1. Định nghĩa bài toán hình thức (Formal Problem Formulation)
Xét không gian đặc trưng của giao dịch thanh toán $cal(X) subset.eq RR^d$ và không gian nhãn nhị phân $cal(Y) = {0, 1}$, trong đó:
- $Y = 0$: Giao dịch hợp lệ (Legitimate transaction).
- $Y = 1$: Giao dịch gian lận (Fraudulent transaction).

Mỗi giao dịch thanh toán trực tuyến là một bộ dữ liệu $(X_i, Y_i, A_i)$ với $X_i in cal(X)$ là vector đặc trưng giao dịch (bao gồm số tiền, thời gian, thuộc tính thẻ, vị trí địa lý, lịch sử hành vi), $Y_i in cal(Y)$ là nhãn thực tế, và $A_i in RR^+$ là giá trị số tiền thanh toán ($"TransactionAmt"$).

Mục tiêu của nghiên cứu là xây dựng một hàm ánh xạ phân loại 3 ngã rẽ:
$ Psi : cal(X) arrow.r {"APPROVE", "STEP_UP_2FA", "BLOCK"} $
sao cho vừa bảo đảm độ phủ toán học theo lớp nhãn với mức tin cậy $1 - alpha$, vừa cực tiểu hóa tổng tổn thất tài chính thực tế khi vận hành trong môi trường sản xuất.

== 3.2. Hàm điểm bất thường (Nonconformity Score Function)
Giả sử ta đã huấn luyện một mô hình học máy cơ sở $hat(f) : cal(X) arrow.r [0, 1]$ trên tập dữ liệu huấn luyện $cal(D)_("train")$, với $hat(f)(x) = hat(p)(Y = 1 | X = x)$ là ước lượng xác suất gian lận của giao dịch $x$.

Để đo lường mức độ "bất thường" hoặc sai khác giữa một giao dịch $x$ và nhãn giả thuyết $y in {0, 1}$, ta định nghĩa hàm điểm bất thường $s(x, y)$ như sau:
$ s(x, y) = cases(
  1 - hat(p)(Y = 0 | X = x) = hat(f)(x) &"nếu " y = 0,
  1 - hat(p)(Y = 1 | X = x) = 1 - hat(f)(x) &"nếu " y = 1
) $

Ý nghĩa xác suất của hàm điểm bất thường:
- Khi giả định giao dịch là hợp lệ ($y = 0$): Nếu mô hình dự đoán xác suất gian lận cao ($hat(f)(x)$ lớn), điểm bất thường $s(x, 0)$ sẽ rất cao, báo hiệu sự mâu thuẫn lớn với giả thuyết hợp lệ.
- Khi giả định giao dịch là gian lận ($y = 1$): Nếu mô hình dự đoán xác suất gian lận thấp ($hat(f)(x)$ nhỏ), điểm bất thường $s(x, 1)$ sẽ rất cao, mâu thuẫn với giả thuyết gian lận.

== 3.3. Thuật toán Mondrian Split Conformal Prediction
Tập hiệu chuẩn độc lập $cal(D)_("calib")$ gồm $n$ giao dịch được phân hoạch thành hai tập con rời rạc theo nhãn thực tế:
$ cal(D)_("calib")^((0)) = {(x_i, y_i) in cal(D)_("calib") : y_i = 0}, quad n_0 = |cal(D)_("calib")^((0))| \
cal(D)_("calib")^((1)) = {(x_i, y_i) in cal(D)_("calib") : y_i = 1}, quad n_1 = |cal(D)_("calib")^((1))| $

Với mỗi mức ý nghĩa danh nghĩa $alpha in (0, 1)$ (trong nghiên cứu này chọn $alpha = 0.05$ tương ứng độ tin cậy $95\%$), ta tính toán giá trị phân vị hiệu chỉnh cấp $(1 - alpha)$ trên từng tập con:
$ hat(q)_0 = "Quantile"(frac(ceil((n_0 + 1)(1 - alpha)), n_0), {s(x_i, 0) : (x_i, y_i) in cal(D)_("calib")^((0))}) $
$ hat(q)_1 = "Quantile"(frac(ceil((n_1 + 1)(1 - alpha)), n_1), {s(x_i, 1) : (x_i, y_i) in cal(D)_("calib")^((1))}) $

Khi một giao dịch mới $x_(n+1)$ xuất hiện tại cổng thanh toán, tập dự đoán Conformal $C(x_(n+1)) subset.eq {0, 1}$ được xác định bởi:
$ C(x_(n+1)) = {y in {0, 1} : s(x_(n+1), y) <= hat(q)_y} $

== 3.4. Bốn trạng thái tập Conformal và Cơ chế ánh xạ 3 ngã rẽ
Tập dự đoán $C(x)$ sinh ra bởi thuật toán có thể rơi vào đúng 4 trường hợp toán học đặc trưng:
+ *$C(x) = {0}$ (Chắc chắn hợp lệ):* Mô hình tự tin khẳng định giao dịch là an toàn với mức độ bảo đảm toán học $1 - alpha$.
+ *$C(x) = {0, 1}$ (Vùng bất định Conformal):* Dữ liệu rơi vào vùng chồng lấn xác suất. Cả hai giả thuyết hợp lệ và gian lận đều không thể bị bác bỏ tại mức tin cậy $95\%$. Đây chính là đối tượng lý tưởng để kích hoạt thử thách xác thực hai bước (Step-Up 2FA OTP).
+ *$C(x) = {1}$ (Chắc chắn gian lận):* Mô hình tự tin khẳng định hành vi gian lận rõ rệt với độ tin cậy $95\%$, cần chặn đứng giao dịch tức thì (Block).
+ *$C(x) = emptyset$ (Tập rỗng / Dị biệt dị thường):* Giao dịch sai khác hoàn toàn so với mọi quan sát trong quá khứ, cần chuyển sang luồng thẩm định an ninh đặc biệt.

== 3.5. Tối ưu hóa ma trận chi phí (Cost Matrix Grid Optimization)
Để chuyển đổi từ không gian xác suất và tập Conformal sang quy tắc quyết định tối ưu kinh tế, ta thiết lập ma trận chi phí tài chính thực tế $C(d, y, A)$ với quyết định $d in {"APPROVE", "STEP_UP_2FA", "BLOCK"}$, nhãn $y in {0, 1}$ và số tiền $A$:

#v(0.2cm)

#figure(
  table(
    columns: (1.8fr, 2.5fr, 2.5fr),
    align: (left + horizon, center + horizon, center + horizon),
    table.header(
      [*Quyết định của hệ thống ($d$)*],
      [*Giao dịch hợp lệ ($Y = 0$)*],
      [*Giao dịch gian lận ($Y = 1$)*]
    ),
    [*APPROVE (Duyệt)*], [$0$ USD], [$A + 15.00$ USD (Mất tiền + Phạt Chargeback)],
    [*STEP_UP_2FA (Thử thách OTP)*], [$0.05$ USD (Phí gửi SMS Gateway)], [$0.05$ USD (Chặn thành công gian lận)],
    [*BLOCK (Chặn tức thì)*], [$5.00$ USD (Chi phí mất thiện cảm khách VIP)], [$0$ USD (Chặn hoàn hảo)]
  ),
  caption: [Ma trận chi phí tài chính thực tế trong hệ thống thanh toán điện tử],
) <tab:cost_matrix>

#v(0.3cm)

Ta xác định hai ngưỡng quyết định $(tau_1, tau_2)$ thỏa mãn $0 < tau_1 <= tau_2 < 1$ sao cho:
$ "Quyết định"(x; tau_1, tau_2) = cases(
  "APPROVE" &"nếu " hat(f)(x) < tau_1,
  "STEP_UP_2FA" &"nếu " tau_1 <= hat(f)(x) < tau_2,
  "BLOCK" &"nếu " hat(f)(x) >= tau_2
) $

Bài toán tối ưu hóa chi phí được thiết lập trên toàn bộ tập hiệu chuẩn $cal(D)_("calib")$:
$ (tau_1^*, tau_2^*) = op("argmin")_(0 < tau_1 <= tau_2 < 1) sum_(i in cal(D)_("calib")) C("Quyết định"(x_i; tau_1, tau_2), y_i, A_i) $

Bằng thuật toán tìm kiếm lưới (Grid Search) hai chiều trên không gian tham số của tập hiệu chuẩn gồm 99,411 giao dịch, hệ thống đã xác định được cặp ngưỡng tối ưu toán học:
$ tau_1^* = 0.0050, quad tau_2^* = 0.9000 $

== 3.6. Giải thuật tổng thể Mondrian Cost-Sensitive Conformal Calibration
Dưới đây là mã giả thuật toán học (Pseudo-code) của toàn bộ quy trình:

#v(0.2cm)
#rect(width: 100%, stroke: 0.8pt + rgb("#94a3b8"), fill: rgb("#f8fafc"), inset: 10pt, radius: 4pt)[
#set text(size: 9.5pt, font: "Courier New")
*Thuật toán 1: Mondrian Conformal & Cost-Sensitive Calibration*
\--------------------------------------------------------------------------------
*Đầu vào:* Mô hình $hat(f)$, Tập hiệu chuẩn $cal(D)_("calib") = {(x_i, y_i, A_i)}_(i=1)^n$, Mức ý nghĩa $alpha = 0.05$.
*Đầu ra:* Phân vị hiệu chuẩn $(hat(q)_0, hat(q)_1)$, Ngưỡng chi phí tối ưu $(tau_1^*, tau_2^*)$.
1.  Khởi tạo $cal(D)_0 = emptyset, cal(D)_1 = emptyset$
2.  *For each* $(x_i, y_i) in cal(D)_("calib")$ *do:*
3.      $s_i = cases(hat(f)(x_i) "nếu " y_i = 0, 1 - hat(f)(x_i) "nếu " y_i = 1)$
4.      Thêm $s_i$ vào $cal(D)_(y_i)$
5.  *End For*
6.  $hat(q)_0 = "Quantile"(frac(ceil((|cal(D)_0| + 1)(1 - alpha)), |cal(D)_0|), cal(D)_0)$
7.  $hat(q)_1 = "Quantile"(frac(ceil((|cal(D)_1| + 1)(1 - alpha)), |cal(D)_1|), cal(D)_1)$
8.  $(tau_1^*, tau_2^*) = op("argmin")_(tau_1 <= tau_2) sum_(i=1)^n C("Triage"(hat(f)(x_i); tau_1, tau_2), y_i, A_i)$
9.  *Return* $(hat(q)_0, hat(q)_1, tau_1^*, tau_2^*)$
]






