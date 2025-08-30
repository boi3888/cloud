# bbs.py — Bot bán hàng (Việt hoá, icon rõ, nút chia đều 2 hàng)
from __future__ import annotations
import os, json, logging, datetime
from typing import Dict, Any, List

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
)
from dotenv import load_dotenv

from PRODUCT_MAP import PRODUCT_MAP
from bank import send_vietqr, save_payment_history
from gemini import chat_with_gemini, is_gemini_available

# ====== Cấu hình & Logging ======
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger("bbs")

load_dotenv()
BOT_TOKEN = os.getenv("BoiGPTbot")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

def _save(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _load(path, default):
    if not os.path.exists(path):
        _save(default, path)
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)

users: Dict[str, Any] = _load(USERS_FILE, {})
orders: Dict[str, Any] = _load(ORDERS_FILE, {})

# ====== Bàn phím chính (chia 2 cột) ======
def main_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🛒 Mua hàng", callback_data="buy_menu"),
         InlineKeyboardButton("💳 Nạp tiền", callback_data="topup")],
        [InlineKeyboardButton("🤖 Chat AI", callback_data="gemini_chat"),
         InlineKeyboardButton("🔎 Thông tin", callback_data="info")],
        [InlineKeyboardButton("📖 Hướng dẫn", callback_data="guide"),
         InlineKeyboardButton("☎️ Hỗ trợ", callback_data="support")],
        [InlineKeyboardButton("🏪 Kênh Shop", url="https://t.me/baoboishop")],
    ]
    return InlineKeyboardMarkup(rows)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🤖 <b>ß𝐚̉𝓞 ß𝐛̂́𝖎 𝗦𝗛𝗢𝗣</b>
✨ <i>Chào mừng bạn đến cửa hàng tiện lợi ngay trong Telegram!</i>

👇 Chọn chức năng bên dưới:"""

    
    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_kb())
    else:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=main_kb())

# ====== Thông tin người dùng ======
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    uid = str(u.id)
    users.setdefault(uid, {"username": u.username, "balance": 0, "orders": []})
    users[uid].setdefault("username", u.username)
    users[uid].setdefault("balance", 0)
    users[uid].setdefault("orders", [])
    _save(users, USERS_FILE)

    user_orders = [orders[oid] for oid in users[uid]["orders"] if oid in orders]
    total_orders = len(user_orders)
    total_topup = sum(o.get("price", 0) for o in user_orders if o.get("status") == "Paid")

    text = (
        "👤 <b>Thông tin của bạn</b>\n\n"
        f"🧑 Tên: {u.first_name}\n"
        f"🔗 Username: @{u.username}\n"
        f"🆔 ID: <code>{u.id}</code>\n"
        f"💰 Số dư: <code>{users[uid]['balance']:,}</code>đ\n"
        f"🧾 Đơn đã tạo: <code>{total_orders}</code>\n"
        f"💳 Tổng đã nạp: <code>{total_topup:,}</code>đ"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ====== Menu mua hàng ======
async def show_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # chia 2 cột
    buttons = [InlineKeyboardButton(p["name"], callback_data=f"show_plans_{k}") for k, p in PRODUCT_MAP.items()]
    rows: List[List[InlineKeyboardButton]] = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton("🏠 Trang chủ", callback_data="home"),
                 InlineKeyboardButton("💳 Nạp tiền", callback_data="topup")])
    text = "🛍️ <b>Danh mục sản phẩm</b>\n\nChọn sản phẩm bạn muốn xem:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))

# ====== Hiển thị gói theo sản phẩm ======
async def show_product_plans(update: Update, context: ContextTypes.DEFAULT_TYPE, product_key: str):
    p = PRODUCT_MAP[product_key]
    prompt = p["ui"].get("plans_prompt", "🧩 Chọn gói thời gian:")
    text = f"<b>{p['name']}</b>\n{p['benefit']}\n\n{prompt}"
    plan_btns = [
        InlineKeyboardButton(f"{pl['label']} ({pl['price']:,}đ)", callback_data=f"buy_{product_key}_{pl['months']}")
        for pl in p["plans"]
    ]
    rows = [plan_btns[i:i+2] for i in range(0, len(plan_btns), 2)]  # 2 cột
    rows.append([InlineKeyboardButton("« Quay lại", callback_data="buy_menu"),
                 InlineKeyboardButton("🏠 Trang chủ", callback_data="home")])
    await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))

# ====== Callback tổng ======
async def buy_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    uid = str(update.effective_user.id)
    await query.answer()

    try:
        if data == "buy_menu":
            await show_buy_menu(update, context)

        elif data.startswith("show_plans_"):
            k = data.replace("show_plans_", "", 1)
            if k not in PRODUCT_MAP:
                await query.edit_message_text("❌ Sản phẩm không hợp lệ.", parse_mode="HTML")
                return
            await show_product_plans(update, context, k)

        elif data.startswith("buy_"):
            # buy_<key>_<months>
            try:
                _, k, months = data.split("_", 2)
            except ValueError:
                await query.edit_message_text("❌ Dữ liệu callback không hợp lệ.", parse_mode="HTML")
                return

            p = PRODUCT_MAP.get(k)
            if not p:
                await query.edit_message_text("❌ Sản phẩm không hợp lệ.", parse_mode="HTML")
                return

            plan = next((pl for pl in p["plans"] if str(pl["months"]) == str(months)), None)
            if not plan:
                await query.edit_message_text("❌ Gói không hợp lệ.", parse_mode="HTML")
                return

            ui = p["ui"]
            text = (
                f"🧾 Bạn chọn <b>{p['name']}</b> — <b>{plan['label']}</b>\n"
                f"💵 Giá: <code>{plan['price']:,}đ</code>\n\n"
                "➡️ Vui lòng xác nhận mua hoặc nạp tiền:"
            )
            rows = [
                [InlineKeyboardButton(ui.get("buy_now", "✅ Xác nhận mua"), callback_data=f"confirm_{k}_{plan['months']}"),
                 InlineKeyboardButton(ui.get("topup", "💳 Nạp tiền"), callback_data="topup")],
                [InlineKeyboardButton(ui.get("back", "« Quay lại"), callback_data=f"show_plans_{k}"),
                 InlineKeyboardButton(ui.get("home", "🏠 Trang chủ"), callback_data="home")]
            ]
            kb = InlineKeyboardMarkup(rows)
            try:
                await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=kb)
            except Exception as e:
                logger.warning("edit_message_text failed (%s); replying instead", e)
                await query.message.reply_text(text=text, parse_mode="HTML", reply_markup=kb)

        elif data in {"topup", "vnpay", "momo", "pay", "payment"}:
            add_info = f"{update.effective_user.id}"
            await send_vietqr(update, context, amount=0, add_info=add_info)

        elif data in {"back", "home"}:
            await start(update, context)

        elif data == "support":
            await query.edit_message_text(
                "☎️ <b>Hỗ trợ khách hàng</b>\n"
                "• Chat admin: @boibank6789\n"
                "• Hotline: +84 933 374 740",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]])
            )
        else:
            await query.answer("Không rõ yêu cầu, vui lòng thử lại.", show_alert=True)

    except Exception as e:
        logger.error("Lỗi callback: %s", e, exc_info=True)
        await query.answer("Đã có lỗi xảy ra, thử lại sau.", show_alert=True)

# ====== Lệnh /qr (tạo QR nhanh) ======
async def qr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = 0
    add_info = None
    if context.args:
        try:
            amount = int(context.args[0])
        except ValueError:
            amount = 0
        if len(context.args) >= 2:
            add_info = " ".join(context.args[1:])
    await send_vietqr(update, context, amount=amount, add_info=add_info)

# ====== Chat với Gemini ======
async def gemini_chat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /chat để bắt đầu chat với Gemini"""
    if not is_gemini_available():
        await update.message.reply_text(
            "❌ Tính năng Chat AI hiện chưa khả dụng. Vui lòng liên hệ admin.",
            parse_mode="HTML"
        )
        return
    
    if context.args:
        message = " ".join(context.args)
        await handle_gemini_message(update, context, message)
    else:
        text = ("🤖 <b>Chat với Gemini Pro 2.5</b>\n\n"
                "✨ Bạn có thể chat trực tiếp với AI bằng cách:\n"
                "• Sử dụng lệnh: <code>/chat tin nhắn của bạn</code>\n"
                "• Hoặc nhấn nút \"🤖 Chat AI\" và gửi tin nhắn bất kỳ\n\n"
                "💡 <b>Ví dụ:</b>\n"
                "<code>/chat Xin chào, bạn có thể giúp tôi viết email không?</code>")
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Bắt đầu chat", callback_data="start_gemini_chat")],
            [InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]
        ])
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def handle_gemini_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str = None):
    """Xử lý tin nhắn gửi đến Gemini"""
    if message is None:
        message = update.message.text
    
    user_id = update.effective_user.id
    
    # Hiển thị typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Gửi tin nhắn đến Gemini
    response = await chat_with_gemini(message, user_id)
    
    # Gửi phản hồi
    await update.message.reply_text(response, parse_mode="HTML")

# Biến toàn cục để theo dõi chat mode
chat_mode_users = set()

async def gemini_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý callback cho chat mode"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "start_gemini_chat":
        if not is_gemini_available():
            await query.edit_message_text(
                "❌ Tính năng Chat AI hiện chưa khả dụng. Vui lòng liên hệ admin.",
                parse_mode="HTML"
            )
            return
        
        user_id = update.effective_user.id
        chat_mode_users.add(user_id)
        
        text = ("🤖 <b>Chế độ Chat AI đã bật!</b>\n\n"
                "💬 Bây giờ bạn có thể gửi tin nhắn bất kỳ và tôi sẽ trả lời bằng Gemini Pro 2.5.\n\n"
                "⚠️ <i>Lưu ý: Tất cả tin nhắn tiếp theo sẽ được gửi đến AI cho đến khi bạn gõ /stop hoặc chọn menu khác.</i>")
        
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛑 Dừng chat AI", callback_data="stop_gemini_chat")],
            [InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]
        ])
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    
    elif query.data == "stop_gemini_chat":
        user_id = update.effective_user.id
        chat_mode_users.discard(user_id)
        await query.edit_message_text(
            "✅ Đã dừng chế độ Chat AI.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]])
        )

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn văn bản thường"""
    user_id = update.effective_user.id
    
    # Kiểm tra xem user có đang ở chat mode không
    if user_id in chat_mode_users:
        await handle_gemini_message(update, context)
    # Nếu không, có thể thêm logic khác ở đây

# ====== Lệnh /stop (dừng chat mode) ======
async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dừng chế độ chat AI"""
    user_id = update.effective_user.id
    if user_id in chat_mode_users:
        chat_mode_users.discard(user_id)
        await update.message.reply_text(
            "✅ Đã dừng chế độ Chat AI.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]])
        )
    else:
        await update.message.reply_text("ℹ️ Bạn hiện không trong chế độ Chat AI.", parse_mode="HTML")

# ====== Hướng dẫn ======
async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 <b>Hướng dẫn</b>\n\n"
        "1) 🛒 <b>Mua hàng</b> để xem & đặt gói.\n"
        "2) 💳 <b>Nạp tiền</b> để thanh toán nhanh qua VietQR.\n"
        "3) 🔎 <b>Thông tin</b> để xem số dư/đơn hàng.\n"
        "4) ☎️ <b>Hỗ trợ</b> khi cần trợ giúp."
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Trang chủ", callback_data="home")]])
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

# ====== Router các nút đơn ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "info":
        await info(update, context)
    elif q.data == "buy_menu":
        await show_buy_menu(update, context)
    elif q.data == "guide":
        await guide(update, context)
    elif q.data == "topup":
        await send_vietqr(update, context)
    elif q.data == "gemini_chat":
        await gemini_chat_callback(update, context)
    elif q.data in {"start_gemini_chat", "stop_gemini_chat"}:
        await gemini_chat_callback(update, context)
    elif q.data in {"home", "back"}:
        # Dừng chat mode khi về trang chủ
        user_id = update.effective_user.id
        chat_mode_users.discard(user_id)
        await start(update, context)
    # Các case khác đã được handle ở buy_menu_callback

# ====== Build App ======
async def _post_init(app):
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Đã xoá webhook, chạy polling.")
    except Exception as e:
        logger.warning("Không xoá được webhook: %s", e)

def build_app():
    if not BOT_TOKEN:
        raise RuntimeError("Thiếu BOT_TOKEN (env 'boi').")
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(_post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", guide))
    app.add_handler(CommandHandler("qr", qr_cmd))
    app.add_handler(CommandHandler("chat", gemini_chat_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(
        buy_menu_callback,
        pattern=r"^(show_plans_|buy_|confirm_|topup|buy_menu|back|home|pay|payment|vnpay|momo|support)"
    ))
    app.add_handler(CallbackQueryHandler(button_handler))  # fallback
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    return app

def main():
    app = build_app()
    logger.info("🚀 BBS Bot đang chạy (polling)…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
