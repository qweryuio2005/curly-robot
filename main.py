import re
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# إعدادات البوت
BOT_TOKEN = "8211834319:AAERPz5EZnfH5C96UzrDs09H9xIc69BexLU"
OWNER_ID = 7438003241

# قائمة نطاقات وروابط مشبوهة (تقدر توسعها)ry
SUSPICIOUS_DOMAINS = [
    "ngrok", "onion", "darkweb", "hack", "evil", "rat", "payload", "malware", "phishing"
]

# امتدادات الملفات المشبوهة
SUSPICIOUS_EXTENSIONS = [
    ".exe", ".apk", ".js", ".sh", ".py", ".bat", ".vbs", ".jar"
]

# دالة فحص الروابط
def is_suspicious_link(text):
    for domain in SUSPICIOUS_DOMAINS:
        if domain.lower() in text.lower():
            return True
    return False

# دالة فحص الملفات
def is_suspicious_file(file_name):
    return any(file_name.lower().endswith(ext) for ext in SUSPICIOUS_EXTENSIONS)

# زرار التحكم
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 تعليم", callback_data="teach")],
        [InlineKeyboardButton("🗑 حذف رد", callback_data="delete")],
        [InlineKeyboardButton("💣 تدمير البيانات", callback_data="destroy")]
    ]
    return InlineKeyboardMarkup(keyboard)

# بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("أهلاً بمالك البوت 🖤", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("أهلاً بك! 🤍")

# استقبال أي رسالة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text or ""
    file = update.message.document

    # فحص الروابط
    if text and is_suspicious_link(text):
        await context.bot.send_message(OWNER_ID, f"🚨 رابط مشبوه من {update.effective_user.mention_html()}:\n{text}", parse_mode="HTML")
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        return

    # فحص الملفات
    if file:
        if is_suspicious_file(file.file_name):
            await context.bot.send_message(OWNER_ID, f"🚨 ملف مشبوه من {update.effective_user.mention_html()}:\n{file.file_name}", parse_mode="HTML")
            await context.bot.ban_chat_member(update.effective_chat.id, user_id)
            return

    # إرسال أي رسالة أو ملف لك فقط
    if update.effective_user.id != OWNER_ID:
        await context.bot.send_message(OWNER_ID, f"📩 من {update.effective_user.mention_html()}:\n{text}", parse_mode="HTML")

# أزرار التحكم
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != OWNER_ID:
        return

    if query.data == "teach":
        await query.message.reply_text("📚 أرسل الأسئلة والأجوبة:\nسؤال: جواب\n.\nسؤال: جواب")
    elif query.data == "delete":
        await query.message.reply_text("🗑 أرسل السؤال اللي تريد تحذفه")
    elif query.data == "destroy":
        await query.message.reply_text("💣 تم مسح كل بيانات البوت (وهمية هنا)")

# تشغيل البوت
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    print("✅ البوت يعمل الآن...")
    app.run_polling()
