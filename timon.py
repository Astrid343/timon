import os
import openai
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# КЛЮЧИ
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"  # замени на свой адрес

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

telegram_app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получена команда /start от пользователя {update.message.from_user.id}")
    await update.message.reply_text("Привет! Напиши мне что-нибудь.")

# Ответ на любое сообщение
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Получено сообщение: {update.message.text}")  # Логирование
    user_message = update.message.text
    try:
        # Запрос к OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        print(f"Ответ от OpenAI: {reply}")  # Логирование ответа
    except Exception as e:
        reply = f"Ошибка: {e}"
        print(f"Ошибка при обращении к OpenAI: {e}")  # Логирование ошибки
    await update.message.reply_text(reply)

# Роут Flask, на который будет приходить Webhook
@app.route('/webhook', methods=["POST"])
def webhook():
    print("Получен запрос на /webhook")  # Логирование
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    print(f"Обработано обновление от {update.message.from_user.id}: {update.message.text}")  # Логирование
    telegram_app.update_queue.put(update)
    return "ok", 200

# Запуск Telegram-бота в webhook-режиме
async def set_webhook():
    print(f"Устанавливаем webhook на {WEBHOOK_URL}")
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

# Регистрируем обработчики
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Установка webhook при запуске
telegram_app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    webhook_url=WEBHOOK_URL,
    allowed_updates=Update.ALL_TYPES
)
