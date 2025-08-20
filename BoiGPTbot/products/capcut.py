"""
Sản phẩm: CapCut Pro — cập nhật theo tham chiếu gần nhất.
"""
from typing import Dict, Any

KEY = "capcut"

def get_product() -> Dict[str, Any]:
    return {
        "key": KEY,
        "name": "CapCut Pro",
        "benefit": (
            "✨ Không watermark khi xuất video\n"
            "🎛️ Công cụ chỉnh sửa nâng cao, thư viện tài nguyên Pro\n"
            "🚫 Không quảng cáo\n"
            "🛡️ Bảo hành theo gói, hỗ trợ nhanh"
        ),
        # Theo yêu cầu cập nhật gần nhất: 12 tháng = 399.000đ (1 thiết bị)
        "plans": [
            {"label": "12 tháng (1 thiết bị)", "months": 12, "price": 399000}
        ],
        "ui": {
            "plans_prompt": "🧩 Chọn gói CapCut Pro (khuyến nghị 1 năm):",
            "buy_now": "✅ Mua CapCut Pro 1 năm",
        },
    }
