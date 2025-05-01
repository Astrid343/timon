import os
import logging
import openai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Настройки
BOT_TOKEN = os.getenv("BOT_TOKEN", "твой_токен")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://твой-домен.onrender.com/webhook")
PORT = int(os.environ.get("PORT", 10000))

openai.api_key = os.getenv("OPENAI_API_KEY", "твой_openai_ключ")

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хэндлер /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне что-нибудь.")

# Хэндлер для сообщений
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Ошибка: {e}"
        logger.error("OpenAI error: %s", e)
    await update.message.reply_text(reply)

# Основной запуск
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logger.info("Устанавливаю webhook на %s", WEBHOOK_URL)
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
