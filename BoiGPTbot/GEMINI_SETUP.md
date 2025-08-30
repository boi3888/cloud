# Hướng dẫn tích hợp Gemini Pro 2.5

## Tổng quan
Dự án này đã được tích hợp với Google Gemini Pro 2.5 API để cung cấp khả năng chat AI thông minh cho người dùng Telegram bot.

## Các tính năng đã thêm

### 1. 🤖 Chat AI với Gemini Pro 2.5
- **Lệnh `/chat`**: Gửi tin nhắn trực tiếp đến AI
- **Chế độ chat tương tác**: Bật/tắt mode chat liên tục
- **Hỗ trợ tiếng Việt**: AI phản hồi bằng tiếng Việt
- **Giao diện thân thiện**: Tích hợp seamlessly với bot hiện tại

### 2. 🛒 Gemini Pro như một sản phẩm
- Người dùng có thể mua gói subscription Gemini Pro
- Các gói: 1 tháng (99.000đ), 3 tháng (249.000đ), 6 tháng (449.000đ), 1 năm (799.000đ)
- Tích hợp với hệ thống payment VietQR hiện có

## Cách sử dụng

### Người dùng cuối:
1. **Chat nhanh**: `/chat Xin chào AI!`
2. **Chat tương tác**: 
   - Nhấn nút "🤖 Chat AI" từ menu chính
   - Gửi tin nhắn bất kỳ và AI sẽ trả lời
   - Gõ `/stop` để dừng chat mode
3. **Mua subscription**: Chọn "🛒 Mua hàng" → "🤖 Gemini Pro 2.5"

### Admin setup:
1. **Lấy API Key**: Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Tạo API Key** cho Gemini
3. **Cấu hình** trong file .env:
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## Chi tiết kỹ thuật

### Files đã thêm/sửa đổi:
- `gemini.py` - Module tích hợp Gemini API
- `products/gemini_pro.py` - Cấu hình sản phẩm Gemini Pro
- `bbs.py` - Thêm handlers cho chat commands
- `PRODUCT_MAP.py` - Thêm Gemini Pro vào danh sách sản phẩm
- `requirements.txt` - Thêm `google-generativeai>=0.8.0`
- `.env.example` - Thêm GEMINI_API_KEY

### API Endpoints sử dụng:
- **Model**: `gemini-2.0-flash-exp` (Gemini Pro 2.5 experimental)
- **Context**: Mỗi tin nhắn được gửi với context tiếng Việt
- **Error handling**: Graceful fallback khi API không khả dụng

### Handlers mới:
- `CommandHandler("chat", gemini_chat_cmd)` - Lệnh /chat
- `CommandHandler("stop", stop_cmd)` - Lệnh /stop
- `MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message)` - Chat mode
- `CallbackQueryHandler` cho các nút chat AI

## Bảo mật
- API key được lưu trong biến môi trường
- Không log nội dung chat của người dùng
- Validation input trước khi gửi đến API
- Rate limiting tự nhiên qua Telegram

## Lưu ý quan trọng
1. **API Key**: Cần phải có Gemini API key hợp lệ để sử dụng
2. **Chi phí**: Google Gemini có thể tính phí, cần theo dõi usage
3. **Rate limits**: API có giới hạn requests, cần monitor
4. **Fallback**: Khi API lỗi, bot vẫn hoạt động bình thường với các tính năng khác

## Test đã thực hiện
✅ Import modules thành công
✅ Syntax check passed  
✅ Dependencies installed correctly
✅ Bot build successfully
✅ Product integration working
⚠️ Cần API key thật để test chat functionality