import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# КЛЮЧИ
BOT_TOKEN = "7942858083:AAG1E_upeUZayYi33OfA6y9eGSyo3-dwJc4"
OPENAI_API_KEY = "sk-ijklmnopqrstuvwxijklmnopqrstuvwxijklmnop"
WEBHOOK_URL = "https://timon-sgzp.onrender.com/webhook"  # замени на свой адрес

openai.api_key = OPENAI_API_KEY

# Создание Telegram приложения
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши мне что-нибудь.")

# Ответ на любое сообщение
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
    await update.message.reply_text(reply)

# Регистрируем обработчики
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Установка webhook при запуске
async def set_webhook():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

# Запуск Telegram-бота в webhook-режиме
if __name__ == "__main__":
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),  # Используем порт из переменной среды
        webhook_url=WEBHOOK_URL,
        allowed_updates=Update.ALL_TYPES
    )
