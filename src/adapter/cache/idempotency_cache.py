"""
Adapter: Idempotency Cache (Layer 3)
Chống trừ tiền hai lần (Double-Spending) bằng băm SHA-256 và lưu đệm kết quả có thời hạn TTL.
"""

import time
import hashlib
import json
import threading
from typing import Optional, Dict, Any


class IdempotencyCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def compute_hash(self, payload: Dict[str, Any]) -> str:
        """Tạo khóa băm SHA-256 duy nhất từ payload giao dịch."""
        # Chuẩn hóa payload thành chuỗi JSON sắp xếp thứ tự khóa
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, hash_key: str) -> Optional[Dict[str, Any]]:
        """Lấy kết quả từ cache nếu còn trong thời hạn TTL."""
        with self._lock:
            entry = self._cache.get(hash_key)
            if not entry:
                return None

            now = time.time()
            if now - entry["timestamp"] > self.ttl_seconds:
                # Đã hết hạn TTL
                del self._cache[hash_key]
                return None

            return entry["data"]

    def set(self, hash_key: str, data: Dict[str, Any]) -> None:
        """Lưu kết quả phân loại vào cache kèm dấu thời gian."""
        with self._lock:
            self._cache[hash_key] = {
                "timestamp": time.time(),
                "data": data
            }

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
