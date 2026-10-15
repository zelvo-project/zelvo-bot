import os
import json
import hmac
import hashlib
import time
import threading
import traceback

from urllib.parse import parse_qsl
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import psycopg2

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


def verify_telegram_init_data(init_data):
    if not TOKEN or not init_data:
        return None

    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed.pop("hash", None)

        if not received_hash:
            return None

        auth_date = int(parsed.get("auth_date", "0"))
        now = time.time()

        if auth_date <= 0 or now - auth_date > 86400 or auth_date > now + 60:
            return None

        data_check_string = "\n".join(
            f"{key}={value}" for key, value in sorted(parsed.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            TOKEN.encode(),
            hashlib.sha256,
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        user_data = json.loads(parsed.get("user", "{}"))
        telegram_id = user_data.get("id")

        return int(telegram_id) if telegram_id else None

    except (ValueError, TypeError, json.JSONDecodeError):
        return None


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg2.connect(DATABASE_URL)


def save_user(telegram_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (telegram_id)
                VALUES (%s)
                ON CONFLICT (telegram_id) DO NOTHING
                """,
                (telegram_id,),
            )


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id BIGINT PRIMARY KEY,
                    balance NUMERIC DEFAULT 0,
                    mining_speed NUMERIC DEFAULT 0,
                    referrals INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_mined_at TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS last_mined_at TIMESTAMP
                """
            )


class WebHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
    web_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "web"
    )
    super().__init__(*args, directory=web_dir, **kwargs)

def log_message(self, format, *args):
    print(format % args, flush=True)
    def send_json(self, status, data):
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response)

    def get_telegram_id(self, init_data):
        telegram_id = verify_telegram_init_data(init_data)
        if not telegram_id:
            raise PermissionError("بيانات تيليجرام غير صالحة. افتح التطبيق من البوت.")
        return telegram_id

    def do_POST(self):
        path = self.path.split("?")[0]

        if path not in ("/api/register", "/api/mine"):
            self.send_json(404, {"success": False, "message": "المسار غير موجود"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 10000:
                self.send_json(400, {"success": False, "message": "حجم الطلب غير صالح"})
                return

            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                self.send_json(400, {"success": False, "message": "صيغة الطلب غير صالحة"})
                return

            telegram_id = self.get_telegram_id(body.get("init_data", ""))

            if path == "/api/register":
                save_user(telegram_id)
                self.send_json(200, {"success": True})
                return

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (telegram_id)
                        VALUES (%s)
                        ON CONFLICT (telegram_id) DO NOTHING
                        """,
                        (telegram_id,),
                    )

                    cur.execute(
                        """
                        UPDATE users
                        SET balance = balance + %s,
                            last_mined_at = CURRENT_TIMESTAMP
                        WHERE telegram_id = %s
                          AND (
                              last_mined_at IS NULL
                              OR last_mined_at <=
                                 CURRENT_TIMESTAMP - (%s * INTERVAL '1 second')
                          )
                        RETURNING balance
                        """,
                        (MINE_REWARD, telegram_id, MINE_COOLDOWN_SECONDS),
                    )

                    row = cur.fetchone()

                    if row is None:
                        self.send_json(
                            429,
                            {
                                "success": False,
                                "message": "استنى 10 ثواني قبل التعدين مرة ثانية",
                            },
                        )
                        return

                    balance = float(row[0])

            self.send_json(
                200,
                {
                    "success": True,
                    "balance": balance,
                    "reward": MINE_REWARD,
                },
            )

        except PermissionError as error:
            self.send_json(401, {"success": False, "message": str(error)})

        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_json(400, {"success": False, "message": "البيانات المرسلة غير صالحة"})

        except Exception:
            traceback.print_exc()
            try:
                self.send_json(
                    500,
                    {"success": False, "message": "خطأ داخلي في السيرفر. راجع Render Logs."},
                )
            except Exception:
                pass

    def do_GET(self):
        if self.path.split("?")[0] != "/api/balance":
            super().do_GET()
            return

        try:
            init_data = self.headers.get("X-Telegram-Init-Data", "")
            telegram_id = self.get_telegram_id(init_data)

            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT balance FROM users WHERE telegram_id = %s",
                        (telegram_id,),
                    )
                    row = cur.fetchone()

            self.send_json(
                200,
                {"balance": float(row[0]) if row else 0},
            )

        except PermissionError as error:
            self.send_json(401, {"success": False, "message": str(error)})

        except Exception:
            traceback.print_exc()
            self.send_json(
                500,
                {"success": False, "message": "تعذّر تحميل الرصيد. راجع Render Logs."},
            )


def run_web_server():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), WebHandler)
    print(f"Web server running on port {PORT}", flush=True)
    server.serve_forever()


def main_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🚀 افتح Zelvo",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ],
            [
                InlineKeyboardButton("ℹ️ عن Zelvo", callback_data="info")
            ],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🍃 <b>أهلاً بك في Zelvo!</b>\n\n"
        "🚀 تطبيق المكافآت الخاص بك جاهز.\n\n"
        "اضغط على الزر بالأسفل لفتح تطبيق Zelvo."
    )
    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "info":
        text = (
            "🍃 <b>Zelvo</b>\n\n"
            "منصة مكافآت رقمية قيد التطوير.\n\n"
            "⚡ التعدين\n🎁 المكافآت\n👥 الإحالات\n"
            "📋 المهام\n🚀 الترقيات\n🏆 المتصدرين\n💸 السحب"
        )
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        )
        await query.edit_message_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    elif query.data == "back":
        await query.edit_message_text(
            "🍃 <b>أهلاً بك في Zelvo!</b>\n\n🚀 افتح التطبيق من الزر بالأسفل.",
            reply_markup=main_keyboard(),
            parse_mode="HTML",
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Telegram bot error: {context.error!r}", flush=True)


def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set.")
    if not WEBAPP_URL:
        raise ValueError("WEBAPP_URL is not set.")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set.")

    init_db()

    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)

    print("Zelvo Bot is running...", flush=True)
    app.run_polling()


if __name__ == "__main__":
    main()
