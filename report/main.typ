// ==============================================================================
// KHÓA LUẬN TỐT NGHIỆP ĐẠI HỌC - BẢNG ĐIỀU PHỐI CHÍNH (MAIN ENTRYPOINT)
// ==============================================================================

#import "template.typ": dhqg-thesis

#show: dhqg-thesis.with(
  title-vi: "KHUNG ĐỊNH CHUẨN BẤT ĐỊNH CONFORMAL THÍCH ỨNG TỐI ƯU CHI PHÍ CHO HỆ THỐNG PHÂN LOẠI RỦI RO GIAN LẬN THANH TOÁN THỜI GIAN THỰC",
  title-en: "AN ADAPTIVE COST-SENSITIVE CONFORMAL CALIBRATION FRAMEWORK FOR REAL-TIME FRAUD TRIAGE IN DISTRIBUTED PAYMENT SYSTEMS",
  author: "VŨ HỒNG TÂN",
  student-id: "20520288",
  advisor: "TS. NGUYỄN VĂN A",
  faculty: "KHOA HỆ THỐNG THÔNG TIN",
  major: "HỆ THỐNG THÔNG TIN",
  city: "TP. HỒ CHÍ MINH",
  year: "2026",
)

// BẢNG THUẬT NGỮ VÀ CHỮ VIẾT TẮT
#include "glossary.typ"
#pagebreak()

// CHƯƠNG 1: GIỚI THIỆU & TỔNG QUAN
#include "chapters/01_introduction.typ"
#pagebreak()

// CHƯƠNG 2: CƠ SỞ LÝ THUYẾT & NGHIÊN CỨU LIÊN QUAN
#include "chapters/02_background_and_related_work.typ"
#pagebreak()

// CHƯƠNG 3: PHƯƠNG PHÁP LUẬN & KHUNG GIẢI PHÁP ĐỀ XUẤT
#include "chapters/03_methodology.typ"
#pagebreak()

// CHƯƠNG 4: THIẾT KẾ KIẾN TRÚC & HIỆN THỰC HỆ THỐNG
#include "chapters/04_architecture_and_implementation.typ"
#pagebreak()

// CHƯƠNG 5: THỰC NGHIỆM, ĐÁNH GIÁ & PHÂN TÍCH KẾT QUẢ
#include "chapters/05_experiments_and_evaluation.typ"
#pagebreak()

// CHƯƠNG 6: THẢO LUẬN, ĐÁNH GIÁ ĐỘ TIN CẬY & HẠN CHẾ
#include "chapters/06_discussion_and_limitations.typ"
#pagebreak()

// CHƯƠNG 7: KẾT LUẬN & HƯỚNG PHÁT TRIỂN
#include "chapters/07_conclusion.typ"
#pagebreak()

// TÀI LIỆU THAM KHẢO
#bibliography("references.bib", title: "TÀI LIỆU THAM KHẢO", style: "ieee")






