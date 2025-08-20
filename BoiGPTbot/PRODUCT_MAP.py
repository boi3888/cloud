"""
PRODUCT_MAP — tổng hợp sản phẩm từ các module trong thư mục `products/`.
Bạn có thể sửa UI chung ở UI_DEFAULTS hoặc override trong từng file sản phẩm.
"""
from typing import Dict, Any
from products import capcut, telegram_premium, canva, adobe_all, chatgpt_plus

UI_DEFAULTS = {
    "buy_now": "✅ Xác nhận mua",
    "topup": "💳 Nạp tiền",
    "back": "« Quay lại",
    "home": "🏠 Trang chủ",
    "plans_prompt": "🧩 Chọn gói thời gian:",
}

def with_ui_defaults(p: Dict[str, Any]) -> Dict[str, Any]:
    ui = dict(UI_DEFAULTS)
    ui.update(p.get("ui", {}))
    p = dict(p)
    p["ui"] = ui
    return p

PRODUCT_MAP: Dict[str, Any] = {
    capcut.KEY:           with_ui_defaults(capcut.get_product()),
    telegram_premium.KEY: with_ui_defaults(telegram_premium.get_product()),
    canva.KEY:            with_ui_defaults(canva.get_product()),
    adobe_all.KEY:        with_ui_defaults(adobe_all.get_product()),
    chatgpt_plus.KEY:     with_ui_defaults(chatgpt_plus.get_product()),
}
