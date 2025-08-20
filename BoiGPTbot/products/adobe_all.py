"""
Sản phẩm: Adobe All Apps
"""
from typing import Dict, Any
KEY = "adobe"
def get_product() -> Dict[str, Any]:
    return {
        "key": KEY,
        "name": "Adobe All Apps",
        "benefit": (
            "🧰 Full bộ Adobe (PS/PR/AE/AI...)\n"
            "♻️ Cập nhật liên tục, dùng mượt"
        ),
        "plans": [
            {"label": "12 tháng", "months": 12, "price": 1339000},
        ],
        "ui": {"plans_prompt": "🧩 Chọn gói Adobe All Apps:"},
    }
