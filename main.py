import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, CallbackQueryHandler

API_KEY = "7599894445:AAEuyMWjHE1J53jA2XCH3x2uKnwyso-dsq4"
OWNER_ID = 7438003241
FIREBASE_URL = "https://gnrel-a39f1-default-rtdb.firebaseio.com/"

user_states = {}
bot_responses = {}

logging.basicConfig(level=logging.INFO)

def save_to_firebase(user_id, question, answer):
    data = {"question": question, "answer": answer}
    requests.post(f"{FIREBASE_URL}/users/{user_id}/messages.json", json=data)

def get_responses(user_id):
    url = f"{FIREBASE_URL}/users/{user_id}/messages.json"
    res = requests.get(url)
    if res.ok and res.json():
        responses = {}
        for item in res.json().values():
            q = item["question"].strip().lower()
            a = item["answer"]
            if q in responses:
                responses[q].append(a)
            else:
                responses[q] = [a]
        return responses
    return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("👋 أهلاً، اضغط الزر لتعليم البوت", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🧠 تعليم", callback_data="teach")]]))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "teach":
        user_states[user_id] = "teaching"
        await query.edit_message_text("أرسل الأسئلة والأجوبة بهالشكل:\n\nسؤال: جواب\n.\nسؤال: جواب\n.\n\nلما تخلص أرسل 'حفظ'")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_states.get(user_id) == "teaching":
        if text.lower() in ["حفظ", "انهاء"]:
            user_states[user_id] = None
            await update.message.reply_text("✅ تم الحفظ.")
            return

        for pair in text.split("."):
            if ":" in pair:
                q, a = pair.split(":", 1)
                save_to_firebase(user_id, q.strip(), a.strip())
        return

    responses = get_responses(user_id)
    q = text.lower().strip()
    if q in responses:
        import random
        await update.message.reply_text(random.choice(responses[q]))

if __name__ == "__main__":
    app = ApplicationBuilder().token(API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
