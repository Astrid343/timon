import os
import logging
import json
import httpx
import openai
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Ключи
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "import os
import logging
import json
import httpx
import openai
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Ключи
TELEGRAM_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"  # ← ВСТАВЬ СЮДА СВОЙ OpenAI ключ
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"  # ← ВСТАВЬ СЮДА СВОЙ URL на Render

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

# Инициализация Flask
app = Flask(name)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Telegram application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот.")

# Обработка текста через OpenAI
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=100,
            temperature=0.7,
        )
        reply = response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {e}")
        reply = "Ошибка при обращении к OpenAI."
    await update.message.reply_text(reply)

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Flask endpoint для webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return '', 200

# Установка webhook
def set_webhook():
    bot = Bot(TELEGRAM_TOKEN)
    response = httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        data={"url": WEBHOOK_URL}
    )
    if response.status_code == 200:
        logger.info("Вебхук установлен.")
    else:
        logger.error(f"Не удалось установить вебхук: {response.text}")

# Запуск Flask
if name == "main":
    set_webhook()
    app.run(host='0.0.0.0', port=10000)"  # ← ВСТАВЬ СЮДА СВОЙ OpenAI ключ
WEBHOOK_URL = "https://your-render-url.onrender.com/webhook"  # ← ВСТАВЬ СЮДА СВОЙ URL на Render

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Telegram application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот.")

# Обработка текста через OpenAI
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=100,
            temperature=0.7,
        )
        reply = response.choices[0].text.strip()
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {e}")
        reply = "Ошибка при обращении к OpenAI."
    await update.message.reply_text(reply)

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Flask endpoint для webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return '', 200

# Установка webhook
def set_webhook():
    bot = Bot(TELEGRAM_TOKEN)
    response = httpx.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        data={"url": WEBHOOK_URL}
    )
    if response.status_code == 200:
        logger.info("Вебхук установлен.")
    else:
        logger.error(f"Не удалось установить вебхук: {response.text}")

# Запуск Flask
if __name_ == "__main__":
    set_webhook()
    app.run(host='0.0.0.0', port=10000)
