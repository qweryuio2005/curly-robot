import requests, difflib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = "7599894445:AAEuyMWjHE1J53jA2XCH3x2uKnwyso-dsq4"
FIREBASE = "https://gnrel-a39f1-default-rtdb.firebaseio.com"
OWNER_ID = 7438003241
states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    kb = [[InlineKeyboardButton("📚 تعليم", callback_data="teach")],
          [InlineKeyboardButton("🗑️ حذف رسالة", callback_data="delete_msg")],
          [InlineKeyboardButton("❌ حذف تعليم", callback_data="delete_learn")]]
    await update.message.reply_text("تحكم البوت:", reply_markup=InlineKeyboardMarkup(kb))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    if uid != OWNER_ID: return
    if query.data == "teach":
        states[uid] = "teaching"
        await query.edit_message_text("أرسل الأسئلة والأجوبة بهالشكل:\nسؤال: جواب\n.\nسؤال: جواب")
    elif query.data == "delete_msg":
        data = requests.get(f"{FIREBASE}/data.json").json() or {}
        kb = [[InlineKeyboardButton(q, callback_data=f"del_{q}")] for q in data]
        await query.edit_message_text("حدد الرسالة لحذفها:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith("del_"):
        q = query.data[4:]
        requests.delete(f"{FIREBASE}/data/{q}.json")
        await query.edit_message_text(f"تم حذف: {q}")
    elif query.data == "delete_learn":
        states[uid] = "confirm_delete"
        kb = [[InlineKeyboardButton("نعم", callback_data="confirm_yes")],
              [InlineKeyboardButton("لا", callback_data="confirm_no")]]
        await query.edit_message_text("هل تريد حذف كل التعليم؟", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data == "confirm_yes":
        requests.delete(f"{FIREBASE}/data.json")
        await query.edit_message_text("تم حذف كل التعليم.")
    elif query.data == "confirm_no":
        await query.edit_message_text("تم الإلغاء.")

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg, uid = update.message.text, update.effective_user.id
    if uid == OWNER_ID and states.get(uid) == "teaching":
        for block in msg.split("."):
            if ":" in block:
                q, a = [i.strip() for i in block.strip().split(":", 1)]
                path = f"{FIREBASE}/data/{q}.json"
                old = requests.get(path).json() or []
                if a not in old: old.append(a)
                requests.put(path, json=old)
        states[uid] = None
        await update.message.reply_text("تم الحفظ ✅")
        return
    data = requests.get(f"{FIREBASE}/data.json").json() or {}
    question = msg.strip()
    for saved_q in data:
        if difflib.SequenceMatcher(None, saved_q.lower(), question.lower()).ratio() > 0.6:
            import random
            return await update.message.reply_text(random.choice(data[saved_q]))
    await update.message.reply_text("ما أعرف الجواب بعد 😅")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.COMMAND, start))
print("Bot is running...")
app.run_polling()
