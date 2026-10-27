"""
Adapter: Model Repository
Quản lý việc lưu trữ và nạp các artifact mô hình đã huấn luyện (model weights, metadata, feature names).
"""

import os
import json
import joblib
from typing import Any, Dict, List, Optional, Tuple


class ModelRepository:
    def __init__(self, base_dir: str = "models"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_model(
        self,
        model_name: str,
        model: Any,
        features: List[str],
        metrics: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        model_dir = os.path.join(self.base_dir, model_name)
        os.makedirs(model_dir, exist_ok=True)

        model_path = os.path.join(model_dir, "model.joblib")
        joblib.dump(model, model_path)

        meta = {
            "model_name": model_name,
            "features": features,
            "metrics": metrics,
            "metadata": metadata or {}
        }
        meta_path = os.path.join(model_dir, "metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        return model_dir

    def load_model(self, model_name: str) -> Tuple[Any, Dict[str, Any]]:
        model_dir = os.path.join(self.base_dir, model_name)
        model_path = os.path.join(model_dir, "model.joblib")
        meta_path = os.path.join(model_dir, "metadata.json")

        if not os.path.exists(model_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Khong tim thay mo hinh tai: {model_dir}")

        model = joblib.load(model_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        return model, meta
