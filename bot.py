import os
import psycopg2
import json
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
    def do_GET(self):
        if self.path.startswith("/api/balance"):
            try:
                from urllib.parse import urlparse, parse_qs

                query = parse_qs(urlparse(self.path).query)
                telegram_id = int(query["telegram_id"][0])

                conn = get_db_connection()
                cur = conn.cursor()

                cur.execute(
                    "SELECT balance FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )

                row = cur.fetchone()

                cur.close()
                conn.close()

                balance = row[0] if row else 0

                response = {
                    "balance": float(balance)
                }

                response_bytes = json.dumps(response).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_bytes)))
                self.end_headers()
                self.wfile.write(response_bytes)

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
