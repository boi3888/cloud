"""
Sản phẩm: ChatGPT Plus
"""
from typing import Dict, Any
KEY = "chatgpt"
def get_product() -> Dict[str, Any]:
    return {
        "key": KEY,
        "name": "ChatGPT Plus",
        "benefit": (
            "🤖 Truy cập GPT-4/GPT-4o\n"
            "🚀 Ưu tiên giờ cao điểm\n"
            "🧠 Tạo GPTs, web browsing"
        ),
        "plans": [
            {"label": "1 tháng", "months": 1, "price": 120000},
        ],
        "ui": {"plans_prompt": "🧩 Chọn gói ChatGPT Plus:"},
    }
