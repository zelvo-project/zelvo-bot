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
        [InlineKeyboardButton("🚀 ابدأ", callback_data="start")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 أهلاً في Zelvo!\n\n"
        "🚀 أهلاً في أول نسخة تجريبية من المشروع.\n\n"
        "اضغط الزر للبدء:",
        reply_markup=reply_markup,
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start":
        await query.edit_message_text(
            "🎉 أهلاً في Zelvo!\n\n"
            "🚀 أنت الآن داخل المشروع.\n\n"
            "قريبًا رح نضيف المهام والمكافآت والسرعة."
        )


def main():
    threading.Thread(target=run_web_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()


if __name__ == "__main__":
    main()
