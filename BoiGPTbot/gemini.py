# gemini.py — Tích hợp Gemini Pro 2.5 API
import os
import logging
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger("gemini")

# Cấu hình từ biến môi trường
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Khởi tạo Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')  # Gemini Pro 2.5
else:
    model = None
    logger.warning("GEMINI_API_KEY không được cấu hình")

async def chat_with_gemini(message: str, user_id: int) -> Optional[str]:
    """
    Gửi tin nhắn đến Gemini Pro 2.5 và nhận phản hồi
    """
    if not model:
        return "❌ Gemini API chưa được cấu hình. Vui lòng liên hệ admin."
    
    if not message.strip():
        return "❌ Vui lòng nhập tin nhắn hợp lệ."
    
    try:
        # Thêm context tiếng Việt
        prompt = f"""Bạn là trợ lý AI thông minh của ßåÒßßî 𝗦𝗛𝗢𝗣. Hãy trả lời bằng tiếng Việt một cách thân thiện và hữu ích.

Tin nhắn từ người dùng: {message}"""
        
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        else:
            return "❌ Không nhận được phản hồi từ Gemini. Vui lòng thử lại."
            
    except Exception as e:
        logger.error(f"Lỗi khi gọi Gemini API: {e}")
        return f"❌ Có lỗi xảy ra khi xử lý yêu cầu: {str(e)}"

def is_gemini_available() -> bool:
    """Kiểm tra xem Gemini có khả dụng không"""
    return model is not None