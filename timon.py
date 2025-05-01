import os
import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters
)

# 🔧 Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 Ключи
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# 🧠 Создание Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# 📥 Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start от {update.effective_user.id}")
    await update.message.reply_text("Привет! Напиши мне что-нибудь.")

# 💬 Обработчик обычных сообщений
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Сообщение от {update.effective_user.id}: {user_message}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.exception("Ошибка при обращении к OpenAI")
        reply = "Произошла ошибка при обращении к OpenAI."
    await update.message.reply_text(reply)

# 🔗 Flask route для Telegram Webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, telegram_app.bot)
        await telegram_app.process_update(update)
        logger.info("✅ Обновление обработано")
    except Exception as e:
        logger.exception("Ошибка обработки webhook")
    return "ok", 200

# 📌 Регистрируем обработчики
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# 🚀 Запуск Flask и установка webhook
if __name__ == "__main__":
    import asyncio

    async def start():
        logger.info("Устанавливаю webhook...")
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        logger.info("Webhook установлен.")

    asyncio.run(start())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
