# bank.py — Gửi QR VietQR (gọn & chặt)
import os, requests, base64, logging
from io import BytesIO
from telegram import InputFile, InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger("bank")

# ENV (giữ nguyên tên biến)
VIETQR_CLIENT_ID = os.getenv("VIETQR_CLIENT_ID", "").strip()
VIETQR_API_KEY   = os.getenv("VIETQR_API_KEY", "").strip()
ACCOUNT_NO       = os.getenv("ACCOUNT_NO", "").strip()
ACCOUNT_NAME     = os.getenv("ACCOUNT_NAME", "").strip()
ACQ_ID           = os.getenv("ACQ_ID", "970441").strip()
TEMPLATE         = (os.getenv("VIETQR_TEMPLATE", "") or "").strip()

def _reply_target(update):
    if getattr(update, 'callback_query', None) and getattr(update.callback_query, 'message', None):
        return update.callback_query.message
    if getattr(update, 'message', None):
        return update.message
    return None

async def send_vietqr(update, context, amount=0, add_info=None):
    user_id = update.effective_user.id
    if add_info is None:
        add_info = f"BOI{user_id}"

    url = "https://api.vietqr.io/v1/generate"
    headers = {
        "x-client-id": VIETQR_CLIENT_ID,
        "x-api-key": VIETQR_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "accountNo": ACCOUNT_NO,
        "accountName": ACCOUNT_NAME,
        "acqId": ACQ_ID,
        "amount": amount,
        "addInfo": add_info,
    }
    if TEMPLATE:
        payload["template"] = TEMPLATE

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    logger.info("VietQR status=%s", resp.status_code)

    target = _reply_target(update)

    if resp.status_code != 200:
        if target:
            await target.reply_text("❌ Lỗi kết nối VietQR API. Vui lòng thử lại sau.")
        return

    try:
        data = resp.json()
    except Exception:
        if target:
            await target.reply_text("❌ Lỗi dữ liệu VietQR. Vui lòng thử lại sau.")
        return

    # Nếu code != 0 → thử bỏ template (nếu có)
    if isinstance(data, dict) and int(data.get("code", 0)) != 0:
        desc = str(data.get("desc", ""))
        logger.warning("VietQR báo lỗi: %s", desc)
        if "template" in desc.lower() and "template" in payload:
            payload_retry = dict(payload); payload_retry.pop("template", None)
            resp2 = requests.post(url, headers=headers, json=payload_retry, timeout=15)
            try:
                data = resp2.json() if resp2.status_code == 200 else None
            except Exception:
                data = None
        else:
            if target:
                await target.reply_text(f"❌ VietQR API lỗi: {desc or 'Không xác định'}")
            return

    try:
        qr_data_url = data["data"]["qrDataURL"]
    except Exception as e:
        logger.error("Thiếu qrDataURL: %s", e)
        if target:
            await target.reply_text("❌ Không lấy được ảnh QR. Vui lòng thử lại sau.")
        return

    # Giải mã ảnh
    img_bytes = b""
    if qr_data_url.startswith("data:image/png;base64,"):
        b64 = qr_data_url.split(",", 1)[1]
        img_bytes = base64.b64decode(b64)

    bio = BytesIO(img_bytes); bio.name = "vietqr.png"; bio.seek(0)

    caption = (
        "💳 <b>Thông tin chuyển khoản</b>\n\n"
        f"👤 Chủ TK: <code>{ACCOUNT_NAME}</code>\n"
        f"🏛️ Ngân hàng (acq): <code>{ACQ_ID}</code>\n"
        f"🏦 Số TK: <code>{ACCOUNT_NO}</code>\n"
        f"📝 Nội dung: <code>{add_info}</code>\n\n"
        "🔍 Quét mã QR bên dưới để chuyển khoản nhanh!"
    )
    keyboard = [[InlineKeyboardButton("✅ Đã chuyển khoản", callback_data=f"confirm_payment_{add_info}")]]

    if target:
        await target.reply_photo(InputFile(bio), caption=caption, parse_mode="HTML",
                                 reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await context.bot.send_photo(update.effective_chat.id, InputFile(bio),
                                     caption=caption, parse_mode="HTML",
                                     reply_markup=InlineKeyboardMarkup(keyboard))

# Lưu lịch sử xác nhận
import json
from datetime import datetime
HISTORY_FILE = "payment_history.json"

def save_payment_history(user_id, add_info):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            history = json.load(open(HISTORY_FILE, "r", encoding="utf-8"))
        except Exception:
            history = []
    history.append({"user_id": user_id, "add_info": add_info, "time": datetime.now().isoformat()})
    json.dump(history, open(HISTORY_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
