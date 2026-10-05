import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes


TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Zelvo Bot is running!")

    def log_message(self, format, *args):
        pass


def run_web_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 ابدأ", callback_data="start")],
        [InlineKeyboardButton("⛏️ التعدين", callback_data="mining")],
        [
            InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="daily"),
            InlineKeyboardButton("📋 المهام", callback_data="tasks"),
        ],
        [
            InlineKeyboardButton("👥 الإحالات", callback_data="referrals"),
            InlineKeyboardButton("🏆 الترتيب", callback_data="leaderboard"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🍃 ZELVO\n\n"
        "💰 الرصيد: 0 ZELVO\n"
        "⚡ سرعة التعدين: 0.426 ZELVO / ساعة\n\n"
        "🚀 أهلاً في النسخة التجريبية!",
        reply_markup=reply_markup,
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        text = (
            "🎉 أهلاً في Zelvo!\n\n"
            "🚀 أنت الآن داخل المشروع."
        )

    elif query.data == "mining":
        text = (
            "⛏️ التعدين\n\n"
            "💰 الرصيد: 0 ZELVO\n"
            "⚡ السرعة: 0.426 ZELVO / ساعة\n\n"
            "🚧 نظام التعدين قيد التجربة."
        )

    elif query.data == "daily":
        text = "🎁 المكافأة اليومية\n\n🚧 قيد التجربة."

    elif query.data == "tasks":
        text = "📋 المهام\n\n🚧 قريبًا."

    elif query.data == "referrals":
        text = "👥 الإحالات\n\n🚧 قريبًا."

    elif query.data == "leaderboard":
        text = "🏆 الترتيب\n\n🚧 قريبًا."

    else:
        text = "🍃 ZELVO"

    keyboard = [
        [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
