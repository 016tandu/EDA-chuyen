from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TriageDecision(str, Enum):
    APPROVE = "APPROVE"          # Duyệt tự động (rủi ro cực thấp)
    STEP_UP_2FA = "STEP_UP_2FA"  # Yêu cầu xác thực bổ sung OTP/Sinh trắc học (vùng bất định)
    BLOCK = "BLOCK"              # Từ chối giao dịch (rủi ro cao rõ rệt)


@dataclass(frozen=True)
class CostMatrix:
    """
    Ma trận chi phí tài chính thực tế cho hệ thống thanh toán:
    - Bỏ lọt gian lận (FN): Mất toàn bộ số tiền giao dịch (amt).
    - Chặn nhầm khách thật (FP): Mất uy tín và chi phí CSKH xử lý khiếu nại (mặc định $5.0).
    - Bắt đúng gian lận (TP): Chi phí xử lý hồ sơ gian lận ($1.0).
    - Duyệt đúng khách thật (TN): Chi phí bằng 0 ($0.0).
    - Can thiệp Step-up OTP trên kẻ gian: Chặn thành công sau OTP, mất phí viễn thông SMS ($0.5).
    - Can thiệp Step-up OTP trên khách thật: Khách nhập OTP thành công, mất phí viễn thông & gây ma sát nhỏ ($0.2).
    """
    cost_fp: float = 5.0
    cost_tp: float = 1.0
    cost_tn: float = 0.0
    cost_step_up_fraud: float = 0.5
    cost_step_up_legit: float = 0.2

    def calculate_cost(
        self,
        decision: TriageDecision,
        is_fraud: int,
        transaction_amt: float
    ) -> float:
        if is_fraud == 1:
            if decision == TriageDecision.APPROVE:
                # Thảm họa tài chính: Bỏ lọt gian lận
                return float(transaction_amt)
            elif decision == TriageDecision.BLOCK:
                # Chặn đúng gian lận
                return self.cost_tp
            else:  # STEP_UP_2FA
                # Chặn thành công qua lớp 2FA
                return self.cost_step_up_fraud
        else:
            if decision == TriageDecision.APPROVE:
                # Khách hàng giao dịch mượt mà
                return self.cost_tn
            elif decision == TriageDecision.BLOCK:
                # Chặn nhầm khách tốt
                return self.cost_fp
            else:  # STEP_UP_2FA
                # Khách tốt chịu ma sát nhẹ nhập OTP
                return self.cost_step_up_legit
