// ==============================================================================
// TEMPLATE KHÓA LUẬN TỐT NGHIỆP - QUY CHUẨN ĐẠI HỌC QUỐC GIA
// Phù hợp ngành Hệ thống Thông tin / Khoa học Máy tính
// Typst 0.14+ compatible
// ==============================================================================

#let dhqg-thesis(
  title-vi: "",
  title-en: "",
  author: "",
  student-id: "",
  advisor: "",
  faculty: "KHOA HỆ THỐNG THÔNG TIN",
  major: "HỆ THỐNG THÔNG TIN",
  city: "TP. HỒ CHÍ MINH",
  year: "2026",
  body
) = {
  // 1. Cấu hình trang tiêu chuẩn ĐHQG (A4, lề trái 3.0cm đóng gáy, lề phải 2.0cm)
  set document(title: title-vi, author: author)
  set page(
    paper: "a4",
    margin: (left: 3.0cm, right: 2.0cm, top: 2.5cm, bottom: 2.5cm),
    header: context {
      let page-num = counter(page).get().first()
      // Ẩn header ở các trang đầu
      if page-num > 3 [
        #set text(size: 9pt, fill: luma(100), font: "Times New Roman")
        #grid(
          columns: (1fr, auto),
          align(left)[*Khóa Luận Tốt Nghiệp:* Khung Định Chuẩn Bất Định Conformal],
          align(right)[*Ngành Hệ thống Thông tin*]
        )
        #line(length: 100%, stroke: 0.5pt + luma(180))
      ]
    },
    footer: context {
      let page-num = counter(page).get().first()
      if page-num > 1 [
        #set text(size: 10pt, fill: luma(80), font: "Times New Roman")
        #align(center)[#page-num]
      ]
    }
  )

  // 2. Kiểu chữ và khoảng cách dòng chuẩn học thuật
  set text(font: "Times New Roman", size: 12pt, lang: "vi")
  set par(justify: true, leading: 0.85em, first-line-indent: 1.27cm)

  // 3. Định dạng tiêu đề các cấp
  show heading.where(level: 1): it => block(width: 100%, breakable: false)[
    #set text(size: 16pt, weight: "bold", fill: rgb("#0f172a"))
    #v(1.2cm)
    #align(left)[#it.body]
    #v(0.6cm)
  ]

  show heading.where(level: 2): it => block(width: 100%, breakable: false)[
    #set text(size: 13.5pt, weight: "bold", fill: rgb("#1e293b"))
    #v(0.5cm)
    #align(left)[#it.body]
    #v(0.3cm)
  ]

  show heading.where(level: 3): it => block(width: 100%, breakable: false)[
    #set text(size: 12pt, weight: "bold", fill: rgb("#334155"))
    #v(0.3cm)
    #align(left)[#it.body]
    #v(0.2cm)
  ]

  // Tùy chỉnh bảng biểu (chống overflow, tự động ngắt dòng)
  show table: set table(
    stroke: 0.5pt + rgb("#cbd5e1"),
    fill: (col, row) => if row == 0 { rgb("#f1f5f9") } else { none },
    inset: 6.5pt
  )
  show table.cell: set text(size: 10pt)

  // ============================================================================
  // TRANG BÌA CHÍNH (MAIN COVER PAGE)
  // ============================================================================
  place(top + left, dx: -0.5cm, dy: -0.5cm)[
    #rect(
      width: 100% + 1.0cm,
      height: 100% + 1.0cm,
      stroke: 2.5pt + rgb("#1e3a8a"),
      inset: 4pt
    )[
      #rect(
        width: 100%,
        height: 100%,
        stroke: 0.8pt + rgb("#1e3a8a"),
        inset: 1.5cm
      )[
        #align(center)[
          #text(size: 12pt, weight: "bold")[ĐẠI HỌC QUỐC GIA TP. HỒ CHÍ MINH]\
          #text(size: 12pt, weight: "bold")[TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN]\
          #text(size: 11pt, weight: "bold")[#faculty]
          
          #v(0.8cm)

          // PLACEHOLDER LOGO TRƯỜNG Ở GIỮA
          #rect(
            width: 3.2cm,
            height: 3.2cm,
            stroke: (paint: rgb("#94a3b8"), thickness: 1pt, dash: "dashed"),
            fill: rgb("#f8fafc"),
            radius: 4pt
          )[
            #place(center + horizon)[
              #text(size: 8pt, fill: rgb("#64748b"))[
                *\[PLACEHOLDER LOGO\]*\
                #v(2pt)
                (Chèn logo.png\
                Đại học Quốc gia)
              ]
            ]
          ]

          #v(0.8cm)

          #text(size: 13pt, weight: "bold", fill: rgb("#1e3a8a"))[KHÓA LUẬN TỐT NGHIỆP CỬ NHÂN]\
          #text(size: 11pt, weight: "bold")[NGÀNH: #major]

          #v(1.0cm)

          #text(size: 15pt, weight: "bold", fill: rgb("#0f172a"))[#title-vi]\
          #v(0.3cm)
          #text(size: 11.5pt, style: "italic", fill: rgb("#334155"))[#title-en]

          #v(2.0cm)

          #align(left)[
            #grid(
              columns: (4.5cm, 1fr),
              row-gutter: 0.35cm,
              [*Sinh viên thực hiện:*], [#author],
              [*Mã số sinh viên:*], [#student-id],
              [*Giảng viên hướng dẫn:*], [#advisor]
            )
          ]

          #v(1.5cm)
          #text(size: 11pt, weight: "bold")[#city, #year]
        ]
      ]
    ]
  ]

  pagebreak()

  // ============================================================================
  // TRANG LỜI CAM ĐOAN
  // ============================================================================
  [
    #heading(level: 1, numbering: none)[LỜI CAM ĐOAN]
    Tôi xin cam đoan rằng công trình nghiên cứu *"#title-vi"* là kết quả học tập và nghiên cứu độc lập của riêng tôi dưới sự hướng dẫn khoa học của #advisor.

    Toàn bộ số liệu thực nghiệm được trích xuất và đo lường trực tiếp từ bộ dữ liệu công chuẩn quốc tế IEEE-CIS Fraud Detection Dataset. Các kết quả phân tích số liệu, mô hình toán học Mondrian Conformal Prediction và kiến trúc phân loại rủi ro 4 tầng Fast-Fail được xây dựng và kiểm chứng thực tế trong mã nguồn dự án. Các tài liệu tham khảo, lý thuyết kế thừa đều được trích dẫn nguồn gốc đầy đủ, minh bạch và trung thực theo đúng quy định liêm chính học thuật của Đại học Quốc gia.

    #v(1.5cm)
    #align(right)[
      #city, ngày 03 tháng 11 năm #year\
      *Sinh viên cam đoan*\
      #v(2.0cm)
      *#author*
    ]
  ]

  pagebreak()

  // ============================================================================
  // TRANG LỜI CẢM ƠN
  // ============================================================================
  [
    #heading(level: 1, numbering: none)[LỜI CẢM ƠN]
    Trước tiên, tôi xin bày tỏ lòng biết ơn sâu sắc nhất tới Thầy/Cô *#advisor*, người đã dành nhiều thời gian tận tâm định hướng nghiên cứu, chỉ bảo phương pháp luận khoa học và tạo mọi điều kiện thuận lợi nhất để tôi hoàn thành đề tài khóa luận này.

    Tôi xin chân thành cảm ơn toàn thể Quý Thầy Cô tại *#faculty* - Trường Đại học Công nghệ Thông tin, Đại học Quốc gia TP. Hồ Chí Minh đã truyền đạt những nền tảng tri thức chuyên môn quý báu về Khoa học Dữ liệu, Hệ thống Thông tin Phân tán và Quản trị Rủi ro trong suốt những năm tháng đại học.

    Cuối cùng, con xin gửi lời cảm ơn vô hạn đến Gia đình và Bạn bè đã luôn là điểm tựa tinh thần vững chắc, động viên và đồng hành cùng tôi trên con đường học tập và nghiên cứu khoa học.

    #v(1.5cm)
    #align(right)[
      *#author*
    ]
  ]

  pagebreak()

  // ============================================================================
  // TRANG TÓM TẮT ĐỀ TÀI (ABSTRACT - VN & EN)
  // ============================================================================
  [
    #heading(level: 1, numbering: none)[TÓM TẮT KHÓA LUẬN]
    Trong kỷ nguyên thanh toán số bùng nổ, gian lận thẻ trực tuyến (online card fraud) gây ra thiệt hại tài chính hàng tỷ USD mỗi năm cho các tổ chức ngân hàng. Các mô hình học máy truyền thống thường dự đoán theo xác suất điểm (point prediction) kèm một ngưỡng cắt nhị phân cứng nhắc (ví dụ $p >= 0.5$). Cách tiếp cận này bộc lộ hai nhược điểm nghiêm trọng trong thực tế: (1) Không thể định lượng được mức độ bất định toán học (uncertainty) đối với các giao dịch nằm gần biên quyết định; và (2) Bỏ qua tính chất bất đối xứng về chi phí tài chính (tổn thất khi bỏ lọt gian lận lớn hơn nhiều lần so với chi phí gửi mã OTP kiểm tra).

    Khóa luận này đề xuất một khung giải pháp toàn diện kết hợp giữa lý thuyết *Mondrian Split Conformal Prediction* và *Tối ưu hóa Chi phí Bất đối xứng (Cost-Sensitive Matrix)* để giải bài toán phân loại 3 ngã rẽ (3-Way Triage: Duyệt tự động, Thử thách OTP 2FA, và Chặn đứng). Hệ thống được hiện thực hóa theo kiến trúc phòng thủ 4 tầng Fast-Fail (Schema #sym.arrow.r Rule Engine #sym.arrow.r Idempotency Cache #sym.arrow.r Conformal ML) đáp ứng nghiêm ngặt cam kết thời gian thực ($p_99 < 40 "ms"$).

    Thực nghiệm trên 590,540 giao dịch thực tế từ bộ dữ liệu chuẩn IEEE-CIS Fraud Detection chứng minh rằng giải pháp đề xuất giúp giảm thiểu tổn thất tài chính thực tế từ 392,641.78 USD xuống còn 21,456.57 USD (*giảm 94.54%*), đạt tỷ lệ chặn gian lận *96.13%*, đồng thời đảm bảo độ phủ toán học nghiêm ngặt ở mức danh nghĩa 95% và độ trễ đuôi $p_99 = 27.57 "ms"$.

    #v(0.3cm)
    *Từ khóa:* Phân loại gian lận, Dự đoán Conformal, Mondrian Conformal Prediction, Tối ưu hóa chi phí, Kiến trúc Fast-Fail, Thời gian thực.

    #v(1.0cm)

    #heading(level: 1, numbering: none)[ABSTRACT]
    In the era of digital payments, online credit card fraud incurs billions of dollars in losses annually. Conventional machine learning fraud detection systems rely on point-probability estimates coupled with a rigid binary classification threshold (e.g., $p >= 0.5$). This standard approach exhibits two fundamental limitations: (1) Inability to mathematically quantify prediction uncertainty for borderline transactions; and (2) Disregard for asymmetric financial costs (the loss from missed fraud significantly outweighs the friction cost of a two-factor authentication challenge).

    This graduation thesis presents an *Adaptive Cost-Sensitive Conformal Calibration Framework* for real-time payment fraud triage. By incorporating *Mondrian Split Conformal Prediction*, the framework produces mathematically guaranteed prediction sets under a prescribed coverage level ($1 - alpha$). These prediction sets are subsequently mapped into an optimal 3-way triage mechanism (Automated Approve, Step-Up 2FA Challenge, and Immediate Block) via an empirical cost minimization matrix. The production system is engineered under Clean Architecture with a 4-layer Fast-Fail pipeline (Schema #sym.arrow.r Security Rules #sym.arrow.r Idempotency Cache #sym.arrow.r Conformal ML).

    Empirical benchmarks on 590,540 real-world transactions from the benchmark IEEE-CIS Fraud Detection dataset demonstrate that our proposed framework cuts financial losses from \$392,641.78 down to \$21,456.57 USD (*a 94.54% reduction*), intercepts *96.13%* of all fraudulent transactions, and sustains a $p_99$ tail latency of *27.57ms*, well within high-throughput industrial SLAs.

    #v(0.3cm)
    *Keywords:* Fraud Detection, Conformal Prediction, Mondrian Calibration, Cost-Sensitive Learning, Fast-Fail Architecture, Real-Time Inference.
  ]

  pagebreak()

  // ============================================================================
  // MỤC LỤC & DANH MỤC TỰ ĐỘNG
  // ============================================================================
  [
    #outline(title: "MỤC LỤC", depth: 3, indent: 1.5em)
    #pagebreak()
    #outline(title: "DANH MỤC HÌNH VẼ", target: figure.where(kind: image))
    #pagebreak()
    #outline(title: "DANH MỤC BẢNG BIỂU", target: figure.where(kind: table))
  ]

  pagebreak()

  // Thiết lập số trang kiểu 1, 2, 3 cho phần nội dung chính
  counter(page).update(1)

  // THÂN BÀI
  body
}
