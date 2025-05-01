import os
import logging
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# 🔧 Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 Ключи
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# 🎯 Создаём Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# 🧠 Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start от {update.effective_user.id}")
    await update.message.reply_text("Привет! Напиши мне что-нибудь.")

# 💬 Обработчик сообщений
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

# 📥 Flask Webhook endpoint
@app.route('/webhook', methods=["POST"])
def webhook():
    logger.info("✅ Получен update от Telegram")
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "ok", 200

# ✅ Регистрируем обработчики
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# 🚀 Запускаем приложение
if __name__ == "__main__":
    # Устанавливаем webhook
    import asyncio
    asyncio.run(telegram_app.bot.set_webhook(WEBHOOK_URL))
    
    # Запускаем Flask + Telegram webhook
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )
