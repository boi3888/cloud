"""
Sản phẩm: Telegram Premium
"""
from typing import Dict, Any
KEY = "telegram"
def get_product() -> Dict[str, Any]:
    return {
        "key": KEY,
        "name": "Telegram Premium",
        "benefit": (
            "⚡ Tốc độ tải nhanh hơn\n"
            "🧩 Sticker/Emoji Premium\n"
            "🚫 Không quảng cáo"
        ),
        "plans": [
            {"label": "3 tháng", "months": 3, "price": 339000},
            {"label": "6 tháng", "months": 6, "price": 539000},
            {"label": "12 tháng", "months": 12, "price": 839000},
        ],
        "ui": {"plans_prompt": "🧩 Chọn gói Telegram Premium:"},
    }
