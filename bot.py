import os
import psycopg2
import json
import hmac
import hashlib
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))
WEBAPP_URL = os.environ.get("WEBAPP_URL")
DATABASE_URL = os.environ.get("DATABASE_URL")

MINE_REWARD = 1
MINE_COOLDOWN_SECONDS = 10

from urllib.parse import parse_qsl
import time


def verify_telegram_init_data(init_data):
    if not TOKEN or not init_data:
        return None

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", None)

        if not received_hash:
            return None

        auth_date = int(parsed.get("auth_date", "0"))

        if time.time() - auth_date > 86400 or auth_date > time.time() + 60:
            return None

        data_check_string = "\n".join(
            f"{key}={value}"
            for key, value in sorted(parsed.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            TOKEN.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        user_data = json.loads(parsed.get("user", "{}"))
        telegram_id = user_data.get("id")

        return int(telegram_id) if telegram_id else None

    except (ValueError, TypeError, json.JSONDecodeError):
        return None

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
def save_user(telegram_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users (telegram_id)
        VALUES (%s)
        ON CONFLICT (telegram_id) DO NOTHING
    """, (telegram_id,))

    conn.commit()
    cur.close()
    conn.close()
class WebHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="web", **kwargs)

    def log_message(self, format, *args):
        pass
 
    def do_POST(self):
        if self.path != "/api/register":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 10000:
                self.send_error(400)
                return

            body = json.loads(self.rfile.read(length))
            init_data = body.get("init_data", "")

            telegram_id = verify_telegram_init_data(init_data)

            if not telegram_id:
                self.send_error(401, "Invalid Telegram data")
                return

            save_user(telegram_id)

            response = json.dumps({
                "success": True
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        except Exception:
            self.send_error(400)

    
    def do_GET(self):
        if self.path.split("?")[0] == "/api/balance":
            try:
                init_data = self.headers.get(
                    "X-Telegram-Init-Data", ""
                )

                telegram_id = verify_telegram_init_data(init_data)

                if not telegram_id:
                    self.send_error(401, "Invalid Telegram data")
                    return

                conn = get_db_connection()
                cur = conn.cursor()

                cur.execute(
                    "SELECT balance FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )

                row = cur.fetchone()

                cur.close()
                conn.close()

                response = json.dumps({
                    "balance": float(row[0]) if row else 0
                }).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            except Exception:
                self.send_error(400)

            return

        super().do_GET()

def run_web_server():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), WebHandler)
    print(f"Web server running on port {PORT}")
    server.serve_forever()


def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "🚀 افتح Zelvo",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ عن Zelvo",
                callback_data="info"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🍃 <b>أهلاً بك في Zelvo!</b>\n\n"
        "🚀 تطبيق المكافآت الخاص بك جاهز.\n\n"
        "اضغط على الزر بالأسفل لفتح تطبيق Zelvo."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    if query.data == "info":

        text = (
            "🍃 <b>Zelvo</b>\n\n"
            "منصة مكافآت رقمية قيد التطوير.\n\n"
            "⚡ التعدين\n"
            "🎁 المكافآت\n"
            "👥 الإحالات\n"
            "📋 المهام\n"
            "🚀 الترقيات\n"
            "🏆 المتصدرين\n"
            "💸 السحب"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔙 رجوع",
                    callback_data="back"
                )
            ]
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif query.data == "back":

        text = (
            "🍃 <b>أهلاً بك في Zelvo!</b>\n\n"
            "🚀 افتح التطبيق من الزر بالأسفل."
        )

        await query.edit_message_text(
            text,
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id BIGINT PRIMARY KEY,
            balance NUMERIC DEFAULT 0,
            mining_speed NUMERIC DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
def main():
    init_db()
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    if not WEBAPP_URL:
        raise ValueError("WEBAPP_URL is not set.")

    threading.Thread(
        target=run_web_server,
        daemon=True
    ).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button)
    )

    print("Zelvo Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
