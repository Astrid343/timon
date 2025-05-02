import os
import logging
import openai
from quart import Quart, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# === CONFIG ===
TELEGRAM_API_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"
WEBHOOK_URL = f"https://timon-sgzp.onrender.com/webhook/{TELEGRAM_API_TOKEN}"  # ← замени на свой домен (Render URL)

# === INIT ===
openai.api_key = OPENAI_API_KEY
app = Quart(__name__)
logging.basicConfig(level=logging.INFO)

# === Build bot ===
application = Application.builder().token(TELEGRAM_API_TOKEN).build()

# === Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I'll reply with GPT-3's response.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await update.message.reply_text("Error processing your request.")

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Initialize bot and set webhook ===
@app.before_serving
async def before_serving():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")

# === Webhook route ===
@app.route(f"/webhook/{TELEGRAM_API_TOKEN}", methods=["POST"])
async def webhook():
    payload = await request.get_json()
    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
    return "", 200

# === Run ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
