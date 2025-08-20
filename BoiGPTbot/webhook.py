# webhook.py — chạy webhook (tuỳ chọn)
import os, logging
from dotenv import load_dotenv
from bbs import build_app

load_dotenv()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
BASE_URL     = os.getenv("WEBHOOK_BASE")
PORT         = int(os.getenv("PORT", "8080"))

logging.basicConfig(level=logging.INFO)

def main():
    if not SECRET_TOKEN or not BASE_URL:
        raise RuntimeError("Thiếu env: SECRET_TOKEN hoặc WEBHOOK_BASE")
    app = build_app()
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        secret_token=SECRET_TOKEN,
        webhook_url=f"{BASE_URL}/webhook/{SECRET_TOKEN}",
    )

if __name__ == "__main__":
    main()
