"""
Sản phẩm: Canva Pro
"""
from typing import Dict, Any
KEY = "canva"
def get_product() -> Dict[str, Any]:
    return {
        "key": KEY,
        "name": "Canva Pro",
        "benefit": (
            "🖼️ Full template/element Pro\n"
            "🪄 Magic Resize, remove BG\n"
            "🚫 Không giới hạn, không watermark"
        ),
        "plans": [
            {"label": "1 tháng", "months": 1, "price": 30000},
            {"label": "3 tháng", "months": 3, "price": 80000},
            {"label": "12 tháng", "months": 12, "price": 300000},
        ],
        "ui": {"plans_prompt": "🧩 Chọn gói Canva Pro:"},
    }
