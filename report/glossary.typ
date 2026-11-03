// ==============================================================================
// BẢNG THUẬT NGỮ VÀ CHỮ VIẾT TẮT (GLOSSARY & ABBREVIATIONS)
// ==============================================================================

#heading(level: 1, numbering: none)[DANH MỤC THUẬT NGỮ VÀ CHỮ VIẾT TẮT]

Dưới đây là bảng giải thích chi tiết các thuật ngữ chuyên ngành và chữ viết tắt tiếng Anh được sử dụng xuyên suốt trong khóa luận:

#v(0.3cm)

#figure(
  table(
    columns: (1.3fr, 2.0fr, 3.5fr),
    align: (left + horizon, left + horizon, left + horizon),
    table.header(
      [*Chữ viết tắt / Thuật ngữ*],
      [*Thuật ngữ tiếng Việt*],
      [*Ý nghĩa & Giải thích chi tiết*]
    ),
    [CP (Conformal Prediction)], [Dự đoán Conformal], [Khung toán học phi tham số cung cấp tập dự đoán có bảo đảm xác suất độ phủ danh nghĩa $1 - alpha$ trong mẫu hữu hạn.],
    [Mondrian CP], [Định chuẩn Conformal nhóm (Mondrian)], [Kỹ thuật phân chia tập hiệu chuẩn theo từng lớp nhãn riêng biệt nhằm khắc phục hiện tượng mất cân bằng độ phủ giữa lớp thiểu số và lớp đa số.],
    [Nonconformity Score], [Điểm bất thường / không tương thích], [Đại lượng đo lường mức độ sai khác hoặc bất thường của một điểm dữ liệu mới so với phân phối dữ liệu đã quan sát trong quá khứ.],
    [3-Way Triage], [Định tuyến 3 ngã rẽ], [Quy trình phân loại rủi ro ra 3 hành động: Phê duyệt tự động (Approve), Yêu cầu xác thực 2 bước (Step-Up 2FA), và Từ chối/Chặn (Block).],
    [2FA (Two-Factor Auth)], [Xác thực hai yếu tố], [Phương thức bảo mật yêu cầu người dùng cung cấp hai bằng chứng xác thực (ví dụ mật khẩu thẻ kết hợp mã OTP gửi qua điện thoại).],
    [OOT (Out-of-Time)], [Tập kiểm thử ngoài khoảng thời gian], [Phương pháp chia dữ liệu kiểm thử theo trục thời gian tuyến tính để phản ánh chính xác tình trạng trôi dạt dữ liệu trong thực tế.],
    [EDA], [Khám phá & Phân tích dữ liệu], [Quy trình khảo sát, thống kê và trực quan hóa dữ liệu ban đầu nhằm phát hiện quy luật, dị biệt và định hướng kỹ nghệ đặc trưng.],
    [ROC-AUC], [Diện tích dưới đường cong ROC], [Thước đo khả năng phân tách giữa lớp gian lận và lớp hợp lệ trên mọi ngưỡng xác suất của mô hình học máy.],
    [PR-AUC], [Diện tích dưới đường cong Precision-Recall], [Chỉ số đánh giá độ chính xác và độ bao phủ, đặc biệt quan trọng trong bài toán mất cân bằng dữ liệu cực đoan.],
    [Fast-Fail], [Thất bại / Ngắt lỗi sớm], [Triết lý kiến trúc phần mềm cho phép kiểm tra và từ chối các yêu cầu vi phạm ở các tầng ngoài cùng nhằm tiết kiệm tài nguyên xử lý.],
    [Idempotency], [Tính bất biến / Tính lũy đẳng], [Đặc tính đảm bảo rằng một yêu cầu gửi lặp lại nhiều lần với cùng payload sẽ luôn trả về kết quả duy nhất mà không bị tính phí trùng.],
    [SLA (Service Level Agreement)], [Cam kết mức chất lượng dịch vụ], [Quy chuẩn kỹ thuật về hiệu năng hệ thống, đặc biệt là giới hạn trễ đuôi $p_99 < 40 "ms"$ trong giao dịch thẻ.],

    [Data Drift], [Trôi dạt phân phối dữ liệu], [Hiện tượng phân phối xác suất của hành vi khách hàng và thủ đoạn gian lận thay đổi liên tục theo thời gian thực.]
  ),
  caption: [Bảng danh mục thuật ngữ và chữ viết tắt chuyên ngành trong khóa luận],
) <tab:glossary>






