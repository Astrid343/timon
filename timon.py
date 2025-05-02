import os
import logging
import openai
from quart import Quart, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Токены
TELEGRAM_API_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-5678ijklmnopabcd5678ijklmnopabcd5678ijkl"
WEBHOOK_PATH = f"/webhook/{TELEGRAM_API_TOKEN}"
WEBHOOK_URL = f"https://timon-sgzp.onrender.com{WEBHOOK_PATH}"

# Настройки
app = Quart(__name__)
openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

# Создание приложения Telegram один раз
application = Application.builder().token(TELEGRAM_API_TOKEN).build()

# Хендлеры
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a message and I will reply with GPT-3.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        await update.message.reply_text(response.choices[0].text.strip())
    except Exception as e:
        logging.error(f"OpenAI error: {e}")
        await update.message.reply_text("Sorry, I couldn't process your request.")

# Добавление хендлеров
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Хук для Telegram
@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    payload = await request.get_json()
    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
    return "", 200

# Запуск сервера + установка webhook
async def setup():
    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

# Запуск сервера
if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())  # установить webhook перед запуском сервера
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
