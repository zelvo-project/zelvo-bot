import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


TOKEN = os.environ.get("BOT_TOKEN")


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


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()
