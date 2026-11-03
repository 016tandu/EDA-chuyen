"""
Adapter: Blocking Rule Engine (Layer 2)
Kiểm tra các quy tắc nghiệp vụ chặn nhanh (Fast-Fail) trước khi tiêu tốn tài nguyên gọi mô hình AI:
- Danh sách đen Thẻ tín dụng bị báo mất (Card Blacklist)
- Danh sách đen Địa chỉ IP gian lận (IP Blacklist)
- Tần suất quẹt thẻ bất thường (Velocity Rate Limiter)
"""

import time
import threading
from typing import Tuple, Optional, Dict, List, Set


class RuleEngine:
    def __init__(
        self,
        velocity_window_seconds: float = 10.0,
        max_transactions_per_window: int = 5
    ):
        self.velocity_window_seconds = velocity_window_seconds
        self.max_transactions_per_window = max_transactions_per_window

        # Danh sách đen cố định (có thể đồng bộ từ CSDL / Redis)
        self._blacklisted_cards: Set[str] = {
            "9999_999.0_150.0_visa_credit_999.0",  # Thẻ trộm thử nghiệm
            "1111_0.0_150.0_mastercard_debit_0.0",
        }
        self._blacklisted_ips: Set[str] = {
            "192.168.1.99",
            "10.0.0.66",
            "185.220.101.5",  # Known Tor exit node
        }

        # Lưu lịch sử dấu thời gian giao dịch theo Card_ID: {Card_ID: [timestamp, ...]}
        self._velocity_history: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def add_blacklisted_card(self, card_id: str) -> None:
        self._blacklisted_cards.add(card_id)

    def add_blacklisted_ip(self, ip: str) -> None:
        self._blacklisted_ips.add(ip)

    def evaluate(
        self,
        card_id: str,
        client_ip: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Kiểm tra 3 quy tắc chặn cứng:
        Trả về (passed: bool, reason_code: str, error_message: str)
        """
        # 1. Kiểm tra danh sách đen Thẻ
        if card_id in self._blacklisted_cards:
            return False, "RULE_CARD_BLACKLISTED", f"Thẻ [{card_id}] nằm trong danh sách đen bị báo mất/khóa thẻ."

        # 2. Kiểm tra danh sách đen IP
        if client_ip and client_ip in self._blacklisted_ips:
            return False, "RULE_IP_BLACKLISTED", f"Địa chỉ IP [{client_ip}] bị liệt vào danh sách tấn công nguy hiểm."

        # 3. Kiểm tra tần suất quẹt thẻ (Velocity Check)
        now = time.time()
        with self._lock:
            timestamps = self._velocity_history.get(card_id, [])
            # Lọc bỏ các giao dịch nằm ngoài cửa sổ thời gian
            valid_timestamps = [t for t in timestamps if now - t <= self.velocity_window_seconds]
            
            if len(valid_timestamps) >= self.max_transactions_per_window:
                return (
                    False,
                    "RULE_VELOCITY_EXCEEDED",
                    f"Cảnh báo tấn công quét thẻ: Thẻ [{card_id}] đã gửi {len(valid_timestamps)} yêu cầu trong {self.velocity_window_seconds}s."
                )

            valid_timestamps.append(now)
            self._velocity_history[card_id] = valid_timestamps

        return True, None, None

    def reset(self) -> None:
        with self._lock:
            self._velocity_history.clear()
