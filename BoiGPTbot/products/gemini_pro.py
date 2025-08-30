# products/gemini_pro.py
KEY = "gemini_pro"

def get_product():
    return {
        "name": "🤖 Gemini Pro 2.5",
        "benefit": """🚀 <b>Trí tuệ nhân tạo tiên tiến từ Google</b>

✨ <b>Tính năng nổi bật:</b>
• 💬 Chat thông minh với AI Gemini Pro 2.5
• 🧠 Xử lý ngôn ngữ tự nhiên cao cấp
• 📝 Hỗ trợ viết văn bản, dịch thuật
• 🔍 Phân tích và tư vấn chuyên sâu
• ⚡ Phản hồi nhanh chóng và chính xác

💎 <b>Ưu điểm vượt trội:</b>
• Giao diện tiếng Việt thân thiện
• Tích hợp ngay trong Telegram
• Không giới hạn số lượng câu hỏi
• Bảo mật thông tin tuyệt đối""",
        
        "plans": [
            {"months": 1, "label": "1 tháng", "price": 99000},
            {"months": 3, "label": "3 tháng", "price": 249000},
            {"months": 6, "label": "6 tháng", "price": 449000},
            {"months": 12, "label": "1 năm", "price": 799000},
        ],
        
        "ui": {
            "buy_now": "🤖 Mua Gemini Pro",
            "topup": "💳 Nạp tiền",
            "back": "« Quay lại",
            "home": "🏠 Trang chủ",
            "plans_prompt": "🤖 Chọn gói Gemini Pro 2.5:",
        }
    }