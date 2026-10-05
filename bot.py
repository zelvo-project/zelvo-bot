import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 10000))


# =========================
# Web Server
# =========================

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


# =========================
# Main Menu
# =========================

def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⛏️ التعدين", callback_data="mining"),
            InlineKeyboardButton("💰 رصيدي", callback_data="balance"),
        ],
        [
            InlineKeyboardButton("🎁 المكافأة اليومية", callback_data="daily"),
            InlineKeyboardButton("👥 الإحالات", callback_data="referrals"),
        ],
        [
            InlineKeyboardButton("🚀 ترقية السرعة", callback_data="upgrade"),
            InlineKeyboardButton("📋 المهام", callback_data="tasks"),
        ],
        [
            InlineKeyboardButton("🏆 المتصدرين", callback_data="leaderboard"),
            InlineKeyboardButton("💸 السحب", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton("ℹ️ معلومات Zelvo", callback_data="info"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# Start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🍃 <b>مرحباً بك في Zelvo!</b>\n\n"
        "🚀 نظام مكافآت يعتمد على السرعة والمهام والإحالات.\n\n"
        "━━━━━━━━━━━━━━\n"
        "💰 رصيدك: <b>0 ZELVO</b>\n"
        "⚡ سرعة التعدين: <b>0 ZELVO/ساعة</b>\n"
        "👥 الإحالات: <b>0</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        "👇 اختر من القائمة:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(),
        parse_mode="HTML",
    )


# =========================
# Buttons
# =========================

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    # -------------------------
    # Home
    # -------------------------

    if data == "home" or data == "back":

        text = (
            "🍃 <b>Zelvo</b>\n\n"
            "🚀 أهلاً في الصفحة الرئيسية\n\n"
            "💰 رصيدك: <b>0 ZELVO</b>\n"
            "⚡ سرعة التعدين: <b>0 ZELVO/ساعة</b>\n"
            "👥 الإحالات: <b>0</b>\n\n"
            "👇 اختر الخدمة:"
        )

        await query.edit_message_text(
            text,
            reply_markup=main_keyboard(),
            parse_mode="HTML",
        )
        return

    # -------------------------
    # Mining
    # -------------------------

    if data == "mining":

        text = (
            "⛏️ <b>التعدين</b>\n\n"
            "💰 الرصيد الحالي: <b>0 ZELVO</b>\n"
            "⚡ سرعة التعدين: <b>0 ZELVO/ساعة</b>\n\n"
            "🚧 نظام التعدين سيتم تفعيله في المرحلة القادمة.\n\n"
            "عند التفعيل سيتم احتساب المكافآت حسب سرعة حسابك."
        )

    # -------------------------
    # Balance
    # -------------------------

    elif data == "balance":

        text = (
            "💰 <b>رصيدك</b>\n\n"
            "🪙 ZELVO: <b>0</b>\n\n"
            "💵 قيمة السحب: <b>غير متاحة حالياً</b>\n\n"
            "🚧 نظام الرصيد والسحب قيد التطوير."
        )

    # -------------------------
    # Daily Reward
    # -------------------------

    elif data == "daily":

        text = (
            "🎁 <b>المكافأة اليومية</b>\n\n"
            "🎉 احصل على مكافأتك اليومية من Zelvo.\n\n"
            "💰 مكافأتك الحالية: <b>0 ZELVO</b>\n\n"
            "🚧 سيتم تفعيل نظام المكافآت اليومية قريباً."
        )

    # -------------------------
    # Referrals
    # -------------------------

    elif data == "referrals":

        text = (
            "👥 <b>الإحالات</b>\n\n"
            "شارك رابط Zelvo مع أصدقائك واحصل على مكافآت عند انضمامهم.\n\n"
            "👤 عدد الإحالات: <b>0</b>\n"
            "💰 أرباح الإحالات: <b>0 ZELVO</b>\n\n"
            "🚧 نظام الإحالات قيد التطوير."
        )

    # -------------------------
    # Upgrade
    # -------------------------

    elif data == "upgrade":

        text = (
            "🚀 <b>ترقية السرعة</b>\n\n"
            "⚡ السرعة الحالية: <b>0 ZELVO/ساعة</b>\n\n"
            "الترقيات ستسمح لك بزيادة سرعة جمع ZELVO.\n\n"
            "🚧 نظام الترقيات سيتم تفعيله لاحقاً."
        )

    # -------------------------
    # Tasks
    # -------------------------

    elif data == "tasks":

        text = (
            "📋 <b>المهام</b>\n\n"
            "أنجز المهام واحصل على مكافآت إضافية.\n\n"
            "🔹 المهام المتاحة: <b>0</b>\n"
            "💰 المكافآت: <b>0 ZELVO</b>\n\n"
            "🚧 سيتم إضافة المهام قريباً."
        )

    # -------------------------
    # Leaderboard
    # -------------------------

    elif data == "leaderboard":

        text = (
            "🏆 <b>المتصدرين</b>\n\n"
            "🥇 لا يوجد ترتيب حالياً.\n\n"
            "🚧 سيتم تفعيل قائمة المتصدرين مع بداية النظام."
        )

    # -------------------------
    # Withdraw
    # -------------------------

    elif data == "withdraw":

        text = (
            "💸 <b>السحب</b>\n\n"
            "رصيدك الحالي: <b>0 ZELVO</b>\n\n"
            "🚧 نظام السحب لم يتم تفعيله بعد.\n\n"
            "سيتم تحديد الحد الأدنى للسحب وطريقة التحويل لاحقاً."
        )

    # -------------------------
    # Info
    # -------------------------

    elif data == "info":

        text = (
            "ℹ️ <b>عن Zelvo</b>\n\n"
            "🍃 Zelvo هو مشروع مكافآت رقمي.\n\n"
            "⚡ سرعة\n"
            "🎁 مكافآت يومية\n"
            "📋 مهام\n"
            "👥 إحالات\n"
            "🏆 ترتيب\n"
            "💸 سحب\n\n"
            "🚧 المشروع ما زال في مرحلة التطوير."
        )

    # -------------------------
    # Start button
    # -------------------------

    elif data == "start":

        text = (
            "🎉 <b>أهلاً في Zelvo!</b>\n\n"
            "🚀 أنت الآن داخل المشروع.\n\n"
            "اختر إحدى الخدمات من القائمة:"
        )

    # -------------------------
    # Unknown
    # -------------------------

    else:

        text = "🍃 <b>Zelvo</b>\n\nحدث خطأ بسيط، حاول مرة أخرى."

    # -------------------------
    # Back Button
    # -------------------------

    keyboard = [
        [
            InlineKeyboardButton(
                "🔙 الرئيسية",
                callback_data="home"
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# =========================
# Main
# =========================

def main():

    if not TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

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


# =========================
# Run
# =========================

if __name__ == "__main__":
    main()
